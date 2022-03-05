from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Menu

from .icons import icon_workflow

menu_workflows = Menu(
    icon=icon_workflow,
    label=_('Workflows'),
    name='workflows'
)
