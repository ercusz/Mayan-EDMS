import hashlib
import logging

from furl import furl
from graphviz import Digraph
from django.contrib.contenttypes.models import ContentType
from mayan.apps.acls.models import AccessControlList
from django.dispatch import receiver
from django.db.models.signals import post_save
from mayan.apps.permissions.models import Role, StoredPermission
from django.contrib.auth import get_user_model
from django.apps import apps
from django.core import serializers
from django.db import IntegrityError, models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from mayan.apps.acls.models import AccessControlList
from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.common.validators import validate_internal_name
from mayan.apps.documents.models import Document, DocumentType
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.events.classes import EventManagerSave
from mayan.apps.events.decorators import method_event
from mayan.apps.file_caching.models import CachePartitionFile
from mayan.apps.permissions.classes import Permission
from ..events import (
    event_workflow_template_created, event_workflow_template_edited
)
from ..literals import (
    STORAGE_NAME_WORKFLOW_CACHE, SYMBOL_MATH_CONDITIONAL,
    WORKFLOW_ACTION_ON_ENTRY
)
from ..managers import WorkflowManager

__all__ = ('Workflow', 'WorkflowRuntimeProxy')
logger = logging.getLogger(name=__name__)


class Workflow(ExtraDataModelMixin, models.Model):
    """
    Fields:
    * label - Identifier. A name/label to call the workflow
    """
    auto_launch = models.BooleanField(
        default=True, help_text=_(
            'Launch workflow when document is created.'
        ), verbose_name=_('Auto launch')
    )
    internal_name = models.CharField(
        db_index=True, help_text=_(
            'This value will be used by other apps to reference this '
            'workflow. Can only contain letters, numbers, and underscores.'
        ), max_length=255, unique=True, validators=[validate_internal_name],
        verbose_name=_('Internal name')
    )
    label = models.CharField(
        help_text=_('A short text to describe the workflow.'),
        max_length=255, unique=True, verbose_name=_('Label')
    )
    document_types = models.ManyToManyField(
        related_name='workflows', to=DocumentType, verbose_name=_(
            'Document types'
        )
    )
    start_datetime = models.DateTimeField(
        blank=True, null=True,
        help_text=_(
            'Date and time for this workflow is activated.' 
        ), verbose_name=_('Start Date Time')
    )
    end_datetime = models.DateTimeField(
        blank=True, null=True, 
        help_text=_(
            'Date and time for this workflow is deactivated.'
        ), verbose_name=_('End Date Time')
    )
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)

    objects = WorkflowManager()

    class Meta:
        ordering = ('label',)
        verbose_name = _('Workflow')
        verbose_name_plural = _('Workflows')

    def clean(self):
        super().clean()
        if self.start_datetime and self.end_datetime is not None:
            if not (self.start_datetime <= self.end_datetime):
                raise ValidationError(_('The start datetime should not be greater than the end datetime.'))

    def __str__(self):
        return self.label

    def get_absolute_url(self):
        return reverse(viewname='document_states:workflow_template_list')

    @cached_property
    def cache(self):
        Cache = apps.get_model(app_label='file_caching', model_name='Cache')
        return Cache.objects.get(
            defined_storage_name=STORAGE_NAME_WORKFLOW_CACHE
        )

    @cached_property
    def cache_partition(self):
        partition, created = self.cache.partitions.get_or_create(
            name='{}'.format(self.pk)
        )
        return partition

    def delete(self, *args, **kwargs):
        self.cache_partition.delete()
        try:
            DocumentType.objects.get(label=self.label).delete()
        except:
            logger.debug(
                'Documents Types label="%s" not found', self.label
            )
        return super().delete(*args, **kwargs)

    def document_types_add(self, queryset, _event_actor=None):
        for document_type in queryset.all():
            self.document_types.add(document_type)
            event_workflow_template_edited.commit(
                action_object=document_type,
                actor=_event_actor or self._event_actor,
                target=self
            )

    def document_types_remove(self, queryset, _event_actor=None):
        for document_type in queryset.all():
            self.document_types.remove(document_type)
            event_workflow_template_edited.commit(
                action_object=document_type,
                actor=_event_actor or self._event_actor,
                target=self
            )
            self.instances.filter(
                document__document_type_id=document_type.pk
            ).delete()

    def generate_image(
        self, maximum_layer_order=None, transformation_instance_list=None,
        user=None
    ):
        # `user` argument added for compatibility.
        cache_filename = '{}'.format(self.get_hash())

        try:
            self.cache_partition.get_file(filename=cache_filename)
        except CachePartitionFile.DoesNotExist:
            logger.debug(
                'workflow cache file "%s" not found', cache_filename
            )

            image = self.render()
            with self.cache_partition.create_file(filename=cache_filename) as file_object:
                file_object.write(image)
        else:
            logger.debug(
                'workflow cache file "%s" found', cache_filename
            )

        return cache_filename

    def get_api_image_url(self, *args, **kwargs):
        final_url = furl()
        final_url.args = kwargs
        final_url.path = reverse(
            viewname='rest_api:workflow-template-image',
            kwargs={'workflow_template_id': self.pk}
        )
        final_url.args['_hash'] = self.get_hash()

        return final_url.tostr()

    def get_document_types_not_in_workflow(self):
        return DocumentType.objects.exclude(pk__in=self.document_types.all())

    def get_hash(self):
        result = hashlib.sha256(
            serializers.serialize(format='json', queryset=(self,)).encode()
        )
        for state in self.states.all():
            result.update(state.get_hash().encode())

        for transition in self.transitions.all():
            result.update(transition.get_hash().encode())

        return result.hexdigest()

    def get_initial_state(self):
        try:
            return self.states.get(initial=True)
        except self.states.model.DoesNotExist:
            return None
    get_initial_state.short_description = _('Initial state')

    def launch_for(self, document):
        if document.document_type in self.document_types.all():
            try:
                logger.info(
                    'Launching workflow %s for document %s', self, document
                )
                workflow_instance = self.instances.create(document=document)
                initial_state = self.get_initial_state()
                if initial_state:
                    for action in initial_state.entry_actions.filter(enabled=True):
                        context = workflow_instance.get_context()
                        context.update(
                            {
                                'action': action
                            }
                        )
                        action.execute(
                            context=context,
                            workflow_instance=workflow_instance
                        )
            except IntegrityError:
                logger.info(
                    'Workflow %s already launched for document %s', self, document
                )
            else:
                logger.info(
                    'Workflow %s launched for document %s', self, document
                )
                return workflow_instance
        else:
            logger.error(
                'This workflow is not valid for the document type of the '
                'document.'
            )

    def render(self):
        diagram = Digraph(
            name='finite_state_machine', graph_attr={
                'rankdir': 'TB', 
                'fontname': 'TH Niramit AS',
            }, format='png',
        )

        action_cache = {}
        state_cache = {}
        transition_cache = []

        for state in self.states.all():
            state_cache['s{}'.format(state.pk)] = {
                'name': 's{}'.format(state.pk),
                'label': state.label,
                'initial': state.initial,
                'connections': {'origin': 0, 'destination': 0}
            }

            for action in state.actions.all():
                if action.has_condition():
                    action_label = '{} {}'.format(
                        SYMBOL_MATH_CONDITIONAL, action.label
                    )
                else:
                    action_label = action.label

                action_cache['a{}'.format(action.pk)] = {
                    'name': 'a{}'.format(action.pk),
                    'label': action_label,
                    'state': 's{}'.format(state.pk),
                    'when': action.when,
                }

        for transition in self.transitions.all():
            if transition.has_condition():
                transition_label = '{} {}'.format(
                    SYMBOL_MATH_CONDITIONAL, transition.label
                )
            else:
                transition_label = transition.label

            transition_cache.append(
                {
                    'tail_name': 's{}'.format(transition.origin_state.pk),
                    'head_name': 's{}'.format(transition.destination_state.pk),
                    'label': transition_label
                }
            )
            state_cache['s{}'.format(transition.origin_state.pk)]['connections']['origin'] = state_cache['s{}'.format(transition.origin_state.pk)]['connections']['origin'] + 1
            state_cache['s{}'.format(transition.destination_state.pk)]['connections']['destination'] += 1

        for key, value in state_cache.items():
            kwargs = {
                'name': value['name'],
                'label': value['label'],
                'shape': 'box' if value['connections']['origin'] == 0 or value['connections']['destination'] == 0 or value['initial'] else 'box',
                'style': 'filled' if value['initial'] else '',
                'fillcolor': '#9DD390',
                
            }
            diagram.node(**kwargs)

        for transition in transition_cache:
            diagram.edge(**transition)

        for key, value in action_cache.items():
            kwargs = {
                'name': value['name'],
                'label': value['label'],
                'shape': 'box',
            }
            diagram.node(**kwargs)
            diagram.edge(
                **{
                    'head_name': '{}'.format(value['name']),
                    'tail_name': '{}'.format(value['state']),
                    'label': 'On entry' if value['when'] == WORKFLOW_ACTION_ON_ENTRY else 'On exit',
                    'arrowhead': 'dot',
                    'dir': 'both',
                    'arrowtail': 'dot',
                    'style': 'dashed',
                }
            )

        return diagram.pipe()

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'event': event_workflow_template_created,
            'target': 'self',
        },
        edited={
            'event': event_workflow_template_edited,
            'target': 'self',
        }
    )
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


@receiver(post_save, sender=Workflow)
def make_acls(sender, instance, created, **kwargs):
    '''
        after X workflow created 
        create a new workflow's acls and set object = X workflow
    '''
    if created:
        acls = AccessControlList.objects.create(
            content_type=ContentType.objects
                .get(app_label='document_states', model='workflow'),
            content_object=instance,
            role=Role.objects.get(label=instance.created_by.username)
        )

        perms = [
            "workflow_create",
            "workflow_delte",
            "workflow_edit",
            "workflow_view",
            "workflow_transition",
            "workflow_tools"
        ]

        for perm in perms:
            stored_permission = StoredPermission.objects.get(
                        namespace="document_states",
                        name=perm,
                    )
            acls.permissions.add(stored_permission)

# after X workflow created 
# create a new acls and set object = X workflow
@receiver(post_save, sender=Workflow)
def make_doc_types(sender, instance, created, **kwargs):
    '''
        after X workflow created 
        create a new document types and set document type's workflow = X workflow
    '''
    if created:
        doc_types = DocumentType.objects.create(
            label=instance.label
        )
        instance.document_types.add(doc_types)
        instance.save()
        owner_acl = AccessControlList.objects.create(
            content_type=ContentType.objects
                .get(app_label='documents', model='documenttype'),
            content_object=doc_types,
            role=Role.objects.get(label=instance.created_by.username)
        )

        users_acl = AccessControlList.objects.create(
            content_type=ContentType.objects
                .get(app_label='documents', model='documenttype'),
            content_object=doc_types,
            role=Role.objects.get(label="Users")
        )

        

        users_perms = [
            {"namespace": "document_parsing", "name": "content_view"},
            {"namespace": "documents", "name": "document_file_view"},
            {"namespace": "documents", "name": "document_version_view"},
            {"namespace": "documents", "name": "document_view"},
        ]

        # add all permissions to owner acls
        for permission in Permission.all():
            owner_acl.permissions.add(permission.stored_permission)
        acl_set_permissions(users_acl, users_perms)

def acl_set_permissions(acl, perms):
    for perm in perms:
        stored_permission = StoredPermission.objects.get(
                    namespace=perm["namespace"],
                    name=perm["name"],
                )
        acl.permissions.add(stored_permission)


class WorkflowRuntimeProxy(Workflow):
    class Meta:
        proxy = True
        verbose_name = _('Workflow runtime proxy')
        verbose_name_plural = _('Workflow runtime proxies')

    def get_document_count(self, user):
        """
        Return the numeric count of documents executing this workflow.
        The count is filtered by access.
        """
        return AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=Document.valid.filter(workflows__workflow=self),
            user=user
        ).count()
