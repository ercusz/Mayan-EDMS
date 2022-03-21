import bleach

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from mayan.apps.converter.models import Asset
from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.events.classes import EventManagerSave
from mayan.apps.events.decorators import method_event

from .events import event_theme_created, event_theme_edited


class Theme(ExtraDataModelMixin, models.Model):
    label = models.CharField(
        db_index=True, help_text=_('A short text describing the theme.'),
        max_length=128, unique=True, verbose_name=_('Label')
    )
    stylesheet = models.TextField(
        blank=True, help_text=_(
            'The CSS stylesheet to change the appearance of the different '
            'user interface elements.'
        ), verbose_name=_('Stylesheet (Advanced)')
    )
    default = models.BooleanField(
        default=False,
        help_text=_(
            'Set this theme to default theme.'
        ), verbose_name=_('Default Theme')
    )
    logo_asset = models.OneToOneField(
        on_delete=models.CASCADE, to=Asset, verbose_name=_('Logo file'),
        blank=True, null=True, related_name='logo_asset'
    )
    font_asset = models.OneToOneField(
        on_delete=models.CASCADE, to=Asset, verbose_name=_('Font file'),
        blank=True, null=True, related_name='font_asset'
    )
    header_bg = models.CharField(
        max_length=7, blank=True,
        help_text=_('The background color on header components.'),
        verbose_name=_('[Header] Background Color')
    )
    header_text = models.CharField(
        max_length=7, blank=True,
        help_text=_('The text color on header components.'),
        verbose_name=_('[Header] Text Color')
    )
    body_bg = models.CharField(
        max_length=7, blank=True,
        help_text=_('The background color on page body.'),
        verbose_name=_('[Body] Background Color')
    )
    body_text = models.CharField(
        max_length=7, blank=True,
        help_text=_('The text color on page body.'),
        verbose_name=_('[Body] Text Color')
    )
    body_link_hover = models.CharField(
        max_length=7, blank=True,
        help_text=_('(Hover action)The link color on page body.'),
        verbose_name=_('[Body] Link Text Color (Hover action)')
    )
    body_block = models.CharField(
        max_length=7, blank=True,
        help_text=_('The block color on page body.'),
        verbose_name=_('[Body] Block Background Color')
    )
    body_primary_btn = models.CharField(
        max_length=7, blank=True,
        help_text=_('The background color of primary button on page body.'),
        verbose_name=_('[Body] Primary Button Background Color')
    )
    lpanel_bg = models.CharField(
        max_length=7, blank=True,
        help_text=_('The background color on left panel components.'),
        verbose_name=_('[Left Panel] Background Color')
    )
    lpanel_collapse_btn_bg = models.CharField(
        max_length=7, blank=True,
        help_text=_('The background color of collapse button on left panel.'),
        verbose_name=_('[Left Panel] Collapse Button Background Color')
    )
    lpanel_collapse_btn_text = models.CharField(
        max_length=7, blank=True,
        help_text=_('The text color of collapse button on left panel.'),
        verbose_name=_('[Left Panel] Collapse Button Text Color')
    )
    lpanel_collapse_btn_bg_hover = models.CharField(
        max_length=7, blank=True,
        help_text=_('(Hover action)The background color of collapse button on left panel.'),
        verbose_name=_('[Left Panel] Collapse Button Background Color(Hover action)')
    )
    lpanel_collapse_btn_text_hover = models.CharField(
        max_length=7, blank=True,
        help_text=_('(Hover action)The text color of collapse button on left panel.'),
        verbose_name=_('[Left Panel] Collapse Button Text Color(Hover action)')
    )
    lpanel_collapsed_panel_bg = models.CharField(
        max_length=7, blank=True,
        help_text=_('(Active action)The background color of collapsed panel on left panel.'),
        verbose_name=_('[Left Panel] Collapsed Panel Background Color(Active action)')
    )
    lpanel_collapsed_btn_text = models.CharField(
        max_length=7, blank=True,
        help_text=_('(Active action)The text color of collapsed button on left panel.'),
        verbose_name=_('[Left Panel] Collapsed Button Text Color(Active action)')
    )
    lpanel_collapsed_btn_bg_hover = models.CharField(
        max_length=7, blank=True,
        help_text=_('(Active+Hover action)The background color of collapsed button on left panel.'),
        verbose_name=_('[Left Panel] Collapsed Button Background Color(Active+Hover action)')
    )
    rnav_bg_hover = models.CharField(
        max_length=7, blank=True,
        help_text=_('(Hover action)The background color of button on right navbar.'),
        verbose_name=_('[Right Navbar] Button Background Color(Hover action)')
    )
    rnav_text_hover = models.CharField(
        max_length=7, blank=True,
        help_text=_('(Hover action)The text color of button on right navbar.'),
        verbose_name=_('[Right Navbar] Button Text Color(Hover action)')
    )
    rnav_panelex_bg = models.CharField(
        max_length=7, blank=True,
        help_text=_('(Expanded Action)The background color of panel on right navbar menu list.'),
        verbose_name=_('[Right Navbar] Expanded Panel Background Color(Expanded action)')
    )
    rnav_panelex_text = models.CharField(
        max_length=7, blank=True,
        help_text=_('(Expanded Action)The text color of panel on right navbar menu list.'),
        verbose_name=_('[Right Navbar] Expanded Panel Text Color(Expanded action)')
    )
    rnav_ex_bg_hover = models.CharField(
        max_length=7, blank=True,
        help_text=_('(Expanded+Hover Action)The background color of panel on right navbar menu list when hover.'),
        verbose_name=_('[Right Navbar] Expanded Panel Background Color(Expanded+Hover action)')
    )
    rnav_ex_text_hover = models.CharField(
        max_length=7, blank=True,
        help_text=_('(Expanded+Hover Action)The text color of panel on right navbar menu list when hover.'),
        verbose_name=_('[Right Navbar] Expanded Panel Text Color(Expanded+Hover action)')
    )


    class Meta:
        ordering = ('label',)
        verbose_name = _('Theme')
        verbose_name_plural = _('Themes')

    def __str__(self):
        return force_text(s=self.label)

    def get_absolute_url(self):
        return reverse(
            viewname='appearance:theme_edit', kwargs={
                'theme_id': self.pk
            }
        )

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'event': event_theme_created,
            'target': 'self',
        },
        edited={
            'event': event_theme_edited,
            'target': 'self',
        }
    )
    def save(self, *args, **kwargs):
        self.stylesheet = bleach.clean(
            text=self.stylesheet, tags=('style',)
        )
        if self.default:
            Theme.objects.all().update(default=False)
        super().save(*args, **kwargs)


class UserThemeSetting(models.Model):
    user = models.OneToOneField(
        on_delete=models.CASCADE, related_name='theme_settings',
        to=settings.AUTH_USER_MODEL, verbose_name=_('User')
    )
    theme = models.ForeignKey(
        blank=True, null=True, on_delete=models.CASCADE,
        related_name='user_setting', to=Theme, verbose_name=_('Theme')
    )

    class Meta:
        verbose_name = _('User theme setting')
        verbose_name_plural = _('User theme settings')

    def __str__(self):
        return force_text(s=self.user)
