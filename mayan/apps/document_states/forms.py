import json
from datetime import datetime
from django.utils.timezone import make_aware
from django import forms
from django.db.models import Model
from django.db.models.query import QuerySet
from django.forms.formsets import formset_factory
from django.forms import TextInput, MultiWidget, DateTimeField
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from mayan.apps.templating.fields import ModelTemplateField
from mayan.apps.views.forms import DynamicModelForm, FilteredSelectionForm

from .classes import WorkflowAction
from .fields import WorfklowImageField
from .models import (
    Workflow, WorkflowInstance, WorkflowState, WorkflowStateAction,
    WorkflowTransition
)

class MinimalSplitDateTimeMultiWidget(MultiWidget):

    def __init__(self, widgets=None, attrs=None):
        if widgets is None:
            if attrs is None:
                attrs = {}
            date_attrs = attrs.copy()
            time_attrs = attrs.copy()

            date_attrs['type'] = 'date'
            time_attrs['type'] = 'time'

            widgets = [
                TextInput(attrs=date_attrs),
                TextInput(attrs=time_attrs),
            ]
        super().__init__(widgets, attrs)

    # nabbing from https://docs.djangoproject.com/en/3.1/ref/forms/widgets/#django.forms.MultiWidget.decompress
    def decompress(self, value):
        if value:
            return [value.date(), value.strftime('%H:%M')]
        return [None, None]

    def value_from_datadict(self, data, files, name):
        date_str, time_str = super().value_from_datadict(data, files, name)
        # DateField expects a single string that it can parse into a date.

        if date_str == time_str == '':
            return None

        if time_str == '':
            time_str = '00:00'

        my_datetime = datetime.strptime(date_str + ' ' + time_str, "%Y-%m-%d %H:%M")
        # making timezone aware
        return make_aware(my_datetime)

class WorkflowActionSelectionForm(forms.Form):
    klass = forms.ChoiceField(
        choices=(), help_text=_('The action type for this action entry.'),
        label=_('Action'), widget=forms.Select(attrs={'class': 'select2'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['klass'].choices = WorkflowAction.get_choices()


class WorkflowForm(forms.ModelForm):

    use_required_attribute = False

    class Meta:
        fields = ('label', 'internal_name', 'auto_launch', 'start_datetime', 'end_datetime')
        model = Workflow
        widgets = {
            'start_datetime': MinimalSplitDateTimeMultiWidget(),
            'end_datetime': MinimalSplitDateTimeMultiWidget(),
        }

    def __init__(self, *args, **kwargs):
        super(WorkflowForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.error_messages = {'required': _('The field "%(field_name)s" is required.') % { 
                'field_name': field.label }}


class WorkflowMultipleSelectionForm(FilteredSelectionForm):
    class Meta:
        allow_multiple = True
        field_name = 'workflows'
        label = _('Workflows')
        required = False
        widget_attributes = {'class': 'select2'}


class WorkflowStateActionDynamicForm(DynamicModelForm):
    class Meta:
        fields = ('label', 'when', 'enabled', 'condition', 'action_data')
        model = WorkflowStateAction
        widgets = {'action_data': forms.widgets.HiddenInput}

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.action_path = kwargs.pop('action_path')
        super().__init__(*args, **kwargs)
        if self.instance.action_data:
            for key, value in json.loads(s=self.instance.action_data).items():
                self.fields[key].initial = value

        self.fields['condition'] = ModelTemplateField(
            initial_help_text=self.fields['condition'].help_text,
            label=self.fields['condition'].label, model=WorkflowInstance,
            model_variable='workflow_instance', required=False
        )

    def clean(self):
        data = super().clean()

        # Consolidate the dynamic fields into a single JSON field called
        # 'action_data'.
        action_data = {}

        for field_name, field_data in self.schema['fields'].items():
            action_data[field_name] = data.pop(
                field_name, field_data.get('default', None)
            )
            if isinstance(action_data[field_name], QuerySet):
                # Flatten the queryset to a list of ids
                action_data[field_name] = list(
                    action_data[field_name].values_list('id', flat=True)
                )
            elif isinstance(action_data[field_name], Model):
                # Store only the ID of a model instance
                action_data[field_name] = action_data[field_name].pk

        data['action_data'] = action_data
        data = import_string(dotted_path=self.action_path).clean(
            form_data=data, request=self.request
        )
        data['action_data'] = json.dumps(obj=action_data)

        return data

class WorkflowStateForm(forms.ModelForm):

    use_required_attribute = False

    class Meta:
        fields = ('initial', 'label', 'start_datetime', 'end_datetime')
        model = WorkflowState
        widgets = {
            'start_datetime': MinimalSplitDateTimeMultiWidget(),
            'end_datetime': MinimalSplitDateTimeMultiWidget(),
        }
    
    def __init__(self, *args, **kwargs):
        super(WorkflowStateForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.error_messages = {'required': _('The field "%(field_name)s" is required.') % { 
                'field_name': field.label }}



class WorkflowTransitionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        workflow = kwargs.pop('workflow')
        super().__init__(*args, **kwargs)
        self.fields[
            'origin_state'
        ].queryset = self.fields[
            'origin_state'
        ].queryset.filter(workflow=workflow)

        self.fields[
            'destination_state'
        ].queryset = self.fields[
            'destination_state'
        ].queryset.filter(workflow=workflow)

        self.fields['condition'] = ModelTemplateField(
            initial_help_text=self.fields['condition'].help_text,
            label=self.fields['condition'].label, model=WorkflowInstance,
            model_variable='workflow_instance', required=False
        )

    class Meta:
        fields = ('label', 'origin_state', 'destination_state', 'condition')
        model = WorkflowTransition


class WorkflowTransitionTriggerEventRelationshipForm(forms.Form):
    namespace = forms.CharField(
        label=_('Namespace'), required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    label = forms.CharField(
        label=_('Label'), required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    relationship = forms.ChoiceField(
        label=_('Enabled'),
        widget=forms.RadioSelect(), choices=(
            ('no', _('No')),
            ('yes', _('Yes')),
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['namespace'].initial = self.initial['event_type'].namespace
        self.fields['label'].initial = self.initial['event_type'].label

        relationship = self.initial['transition'].trigger_events.filter(
            event_type=self.initial['event_type'],
        )

        if relationship.exists():
            self.fields['relationship'].initial = 'yes'
        else:
            self.fields['relationship'].initial = 'no'

    def save(self):
        relationship = self.initial['transition'].trigger_events.filter(
            event_type=self.initial['event_type'],
        )

        if self.cleaned_data['relationship'] == 'no':
            relationship.delete()
        elif self.cleaned_data['relationship'] == 'yes':
            if not relationship.exists():
                self.initial['transition'].trigger_events.create(
                    event_type=self.initial['event_type'],
                )


WorkflowTransitionTriggerEventRelationshipFormSet = formset_factory(
    form=WorkflowTransitionTriggerEventRelationshipForm, extra=0
)


class WorkflowInstanceTransitionSelectForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        workflow_instance = kwargs.pop('workflow_instance')
        super().__init__(*args, **kwargs)
        self.fields[
            'transition'
        ].queryset = workflow_instance.get_transition_choices(_user=user)

    transition = forms.ModelChoiceField(
        help_text=_('Select a transition to execute in the next step.'),
        label=_('Transition'), queryset=WorkflowTransition.objects.none()
    )


class WorkflowPreviewForm(forms.Form):
    workflow = WorfklowImageField()

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        self.fields['workflow'].initial = instance
