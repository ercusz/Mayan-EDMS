from django.shortcuts import get_object_or_404

from mayan.apps.acls.models import AccessControlList
from mayan.apps.converter.api_view_mixins import APIImageViewMixin
from mayan.apps.documents.models.document_type_models import DocumentType
from mayan.apps.documents.permissions import permission_document_type_view
from mayan.apps.documents.serializers.document_type_serializers import DocumentTypeSerializer
from mayan.apps.rest_api.api_view_mixins import ExternalObjectAPIViewMixin
from mayan.apps.rest_api import generics

from ..models.workflow_models import Workflow
from ..permissions import (
    permission_workflow_template_create, permission_workflow_template_delete,
    permission_workflow_template_edit, permission_workflow_template_view
)
from ..serializers import (
    WorkflowTemplateDocumentTypeAddSerializer,
    WorkflowTemplateDocumentTypeRemoveSerializer, WorkflowTemplateSerializer,
    WorkflowTemplateStateActionSerializer, WorkflowTemplateStateSerializer,
    WorkflowTemplateTransitionSerializer, WorkflowTransitionFieldSerializer
)


class APIWorkflowTemplateDocumentTypeListView(
    ExternalObjectAPIViewMixin, generics.ListAPIView
):
    """
    get: Returns a list of all the document types attached to a workflow template.
    """
    external_object_class = Workflow
    external_object_pk_url_kwarg = 'workflow_template_id'
    mayan_external_object_permissions = {
        'GET': (permission_workflow_template_view,)
    }
    mayan_object_permissions = {
        'GET': (permission_document_type_view,),
    }
    serializer_class = DocumentTypeSerializer

    def get_queryset(self):
        """
        This view returns a list of document types that belong to a workflow template.
        """
        return self.external_object.document_types.all()


class APIWorkflowTemplateDocumentTypeAddView(generics.ObjectActionAPIView):
    """
    post: Add a document type to a workflow template.
    """
    lookup_url_kwarg = 'workflow_template_id'
    mayan_object_permissions = {
        'POST': (permission_workflow_template_edit,)
    }
    serializer_class = WorkflowTemplateDocumentTypeAddSerializer
    queryset = Workflow.objects.all()

    def object_action(self, request, serializer):
        document_type = serializer.validated_data['document_type_id']
        self.object._event_actor = self.request.user
        self.object.document_types_add(
            queryset=DocumentType.objects.filter(pk=document_type.id)
        )


class APIWorkflowTemplateDocumentTypeRemoveView(generics.ObjectActionAPIView):
    """
    post: Remove a document type from a workflow template.
    """
    lookup_url_kwarg = 'workflow_template_id'
    mayan_object_permissions = {
        'POST': (permission_workflow_template_edit,)
    }
    serializer_class = WorkflowTemplateDocumentTypeRemoveSerializer
    queryset = Workflow.objects.all()

    def object_action(self, request, serializer):
        document_type = serializer.validated_data['document_type_id']
        self.object._event_actor = self.request.user
        self.object.document_types_remove(
            queryset=DocumentType.objects.filter(pk=document_type.id)
        )


class APIWorkflowTemplateImageView(
    APIImageViewMixin, generics.RetrieveAPIView
):
    """
    get: Returns an image representation of the selected workflow template.
    """
    lookup_url_kwarg = 'workflow_template_id'
    mayan_object_permissions = {
        'GET': (permission_workflow_template_view,),
    }
    queryset = Workflow.objects.all()


class APIWorkflowTemplateListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all the workflow templates.
    post: Create a new workflow template.
    """
    mayan_object_permissions = {'GET': (permission_workflow_template_view,)}
    mayan_view_permissions = {'POST': (permission_workflow_template_create,)}
    ordering_fields = ('id', 'internal_name', 'label')
    queryset = Workflow.objects.all()
    serializer_class = WorkflowTemplateSerializer

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }


class APIWorkflowTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the selected workflow template.
    get: Return the details of the selected workflow template.
    patch: Edit the selected workflow template.
    put: Edit the selected workflow template.
    """
    lookup_url_kwarg = 'workflow_template_id'
    mayan_object_permissions = {
        'DELETE': (permission_workflow_template_delete,),
        'GET': (permission_workflow_template_view,),
        'PATCH': (permission_workflow_template_edit,),
        'PUT': (permission_workflow_template_edit,)
    }
    queryset = Workflow.objects.all()
    serializer_class = WorkflowTemplateSerializer

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }


# Workflow state views


class APIWorkflowTemplateStateListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all the workflow template states.
    post: Create a new workflow template state.
    """
    ordering_fields = ('start_datetime', 'end_datetime', 'completion', 'id', 'initial', 'label')
    serializer_class = WorkflowTemplateStateSerializer

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
            'workflow': self.get_workflow_template()
        }

    def get_queryset(self):
        return self.get_workflow_template().states.all()

    def get_workflow_template(self):
        if self.request.method == 'GET':
            permission_required = permission_workflow_template_view
        else:
            permission_required = permission_workflow_template_edit

        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_required, queryset=Workflow.objects.all(),
            user=self.request.user
        )

        return get_object_or_404(
            klass=queryset, pk=self.kwargs['workflow_template_id']
        )


class APIWorkflowTemplateStateView(
    ExternalObjectAPIViewMixin, generics.RetrieveUpdateDestroyAPIView
):
    """
    delete: Delete the selected workflow template state.
    get: Return the details of the selected workflow template state.
    patch: Edit the selected workflow template state.
    put: Edit the selected workflow template state.
    """
    external_object_class = Workflow
    external_object_pk_url_kwarg = 'workflow_template_id'
    mayan_external_object_permissions = {
        'DELETE': (permission_workflow_template_edit,),
        'GET': (permission_workflow_template_view,),
        'PATCH': (permission_workflow_template_edit,),
        'PUT': (permission_workflow_template_edit,),
    }
    lookup_url_kwarg = 'workflow_template_state_id'
    serializer_class = WorkflowTemplateStateSerializer

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }

    def get_queryset(self):
        return self.external_object.states.all()


class APIWorkflowTemplateStateActionListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all the workflow template state actions.
    post: Create a new workflow template state action.
    """
    ordering_fields = ('label', 'enabled', 'id')
    serializer_class = WorkflowTemplateStateActionSerializer

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
            'state': self.get_workflow_template_state()
        }

    def get_queryset(self):
        return self.get_workflow_template_state().actions.all()

    def get_workflow_template_state(self):
        if self.request.method == 'GET':
            permission_required = permission_workflow_template_view
        else:
            permission_required = permission_workflow_template_edit

        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_required,
            queryset=self.get_workflow_template().states.all(),
            user=self.request.user
        )

        return get_object_or_404(
            klass=queryset, pk=self.kwargs['workflow_template_state_id']
        )

    def get_workflow_template(self):
        return get_object_or_404(
            klass=Workflow.objects.all(),
            pk=self.kwargs['workflow_template_id']
        )


class APIWorkflowTemplateStateActionDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    """
    delete: Delete the selected workflow template state action.
    get: Return the details of the selected workflow template state action.
    patch: Edit the selected workflow template state action.
    put: Edit the selected workflow template state action.
    """
    mayan_object_permissions = {
        'DELETE': (permission_workflow_template_edit,),
        'GET': (permission_workflow_template_view,),
        'PATCH': (permission_workflow_template_edit,),
        'PUT': (permission_workflow_template_edit,),
    }
    lookup_url_kwarg = 'workflow_template_state_action_id'
    serializer_class = WorkflowTemplateStateActionSerializer

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }

    def get_queryset(self):
        return self.get_workflow_template_state().actions.all()

    def get_workflow_template_state(self):
        if self.request.method == 'GET':
            permission_required = permission_workflow_template_view
        else:
            permission_required = permission_workflow_template_edit

        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_required,
            queryset=self.get_workflow_template().states.all(),
            user=self.request.user
        )
        return get_object_or_404(
            klass=queryset, pk=self.kwargs['workflow_template_state_id']
        )

    def get_workflow_template(self):
        return get_object_or_404(
            klass=Workflow.objects.all(),
            pk=self.kwargs['workflow_template_id']
        )


# Workflow transition views


class APIWorkflowTemplateTransitionListView(
    ExternalObjectAPIViewMixin, generics.ListCreateAPIView
):
    """
    get: Returns a list of all the workflow template transitions.
    post: Create a new workflow template transition.
    """
    external_object_class = Workflow
    external_object_pk_url_kwarg = 'workflow_template_id'
    mayan_external_object_permissions = {
        'GET': (permission_workflow_template_view,),
        'POST': (permission_workflow_template_edit,),
    }
    ordering_fields = ('destination_state', 'id', 'label', 'origin_state')
    serializer_class = WorkflowTemplateTransitionSerializer

    def get_instance_extra_data(self):
        # This method is only called during POST, therefore filter only by
        # edit permission.
        return {
            '_event_actor': self.request.user,
            'workflow': self.external_object,
        }

    def get_queryset(self):
        return self.external_object.transitions.all()


class APIWorkflowTemplateTransitionView(
    ExternalObjectAPIViewMixin, generics.RetrieveUpdateDestroyAPIView
):
    """
    delete: Delete the selected workflow template transition.
    get: Return the details of the selected workflow template transition.
    patch: Edit the selected workflow template transition.
    put: Edit the selected workflow template transition.
    """
    external_object_class = Workflow
    external_object_pk_url_kwarg = 'workflow_template_id'
    mayan_external_object_permissions = {
        'DELETE': (permission_workflow_template_edit,),
        'GET': (permission_workflow_template_view,),
        'PATCH': (permission_workflow_template_edit,),
        'PUT': (permission_workflow_template_edit,),
    }
    lookup_url_kwarg = 'workflow_template_transition_id'
    serializer_class = WorkflowTemplateTransitionSerializer

    def get_instance_extra_data(self):
        # This method is only called during POST, therefore filter only by
        # edit permission.
        return {
            '_event_actor': self.request.user,
            'workflow': self.external_object,
        }

    def get_queryset(self):
        return self.external_object.transitions.all()


# Workflow template transition fields


class APIWorkflowTemplateTransitionFieldListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all the workflow template transition fields.
    post: Create a new workflow template transition field.
    """
    ordering_fields = ('id', 'label', 'name', 'required', 'widget_kwargs')
    serializer_class = WorkflowTransitionFieldSerializer

    def get_instance_extra_data(self):
        # This method is only called during POST, therefore filter only by
        # edit permission.
        return {
            '_event_actor': self.request.user,
            'transition': self.get_workflow_template_transition(),
        }

    def get_queryset(self):
        return self.get_workflow_template_transition().fields.all()

    def get_workflow_template(self):
        if self.request.method == 'GET':
            permission_required = permission_workflow_template_view
        else:
            permission_required = permission_workflow_template_edit

        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_required, queryset=Workflow.objects.all(),
            user=self.request.user
        )

        return get_object_or_404(
            klass=queryset, pk=self.kwargs['workflow_template_id']
        )

    def get_workflow_template_transition(self):
        return get_object_or_404(
            klass=self.get_workflow_template().transitions,
            pk=self.kwargs['workflow_template_transition_id']
        )


class APIWorkflowTemplateTransitionFieldDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the selected workflow template transition field.
    get: Return the details of the selected workflow template transition field.
    patch: Edit the selected workflow template transition field.
    put: Edit the selected workflow template transition field.
    """
    lookup_url_kwarg = 'workflow_template_transition_field_id'
    serializer_class = WorkflowTransitionFieldSerializer

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }

    def get_queryset(self):
        return self.get_workflow_template_transition().fields.all()

    def get_workflow_template(self):
        if self.request.method == 'GET':
            permission_required = permission_workflow_template_view
        else:
            permission_required = permission_workflow_template_edit

        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_required, queryset=Workflow.objects.all(),
            user=self.request.user
        )

        return get_object_or_404(
            klass=queryset, pk=self.kwargs['workflow_template_id']
        )

    def get_workflow_template_transition(self):
        return get_object_or_404(
            klass=self.get_workflow_template().transitions,
            pk=self.kwargs['workflow_template_transition_id']
        )
