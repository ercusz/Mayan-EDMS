import bleach
import logging
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from mayan.apps.converter.models import Asset
from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.events.classes import EventManagerSave
from mayan.apps.events.decorators import method_event
from django.dispatch import receiver
from django.db.models.signals import post_save
from mayan.apps.acls.models import AccessControlList
from mayan.apps.permissions.models import Role, StoredPermission
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator

from .events import event_theme_created, event_theme_edited
logger = logging.getLogger(name=__name__)

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
    header_text_brand = models.CharField(
        max_length=26, blank=True,
        help_text=_('The heading text on header components.'),
        verbose_name=_('Heading Text')
    )
    header_text_brand_size = models.PositiveIntegerField(
        default=19, validators=[MinValueValidator(12), MaxValueValidator(36)],
        help_text=_('The font size of heading text on header components. \n only support size 12-36px'),
        verbose_name=_('Heading Text Font Size')
    )
    logo_asset = models.OneToOneField(
        on_delete=models.CASCADE, to=Asset, verbose_name=_('Logo file'),
        blank=True, null=True, related_name='logo_asset'
    )
    font_asset = models.OneToOneField(
        on_delete=models.CASCADE, to=Asset, verbose_name=_('Font file'),
        blank=True, null=True, related_name='font_asset'
    )
    font_header_asset = models.OneToOneField(
        on_delete=models.CASCADE, to=Asset, verbose_name=_('Header font file'),
        blank=True, null=True, related_name='font_header_asset'
    )
    header_bg = models.CharField(
        max_length=7, blank=True, default='#ffffff',
        help_text=_('The background color on header components.'),
        verbose_name=_('[Header] Background Color')
    )
    header_text = models.CharField(
        max_length=7, blank=True, default='#0F75BD',
        help_text=_('The text color on header components.'),
        verbose_name=_('[Header] Text Color')
    )
    body_bg = models.CharField(
        max_length=7, blank=True, default='#ffffff',
        help_text=_('The background color on page body.'),
        verbose_name=_('[Body] Background Color')
    )
    body_text = models.CharField(
        max_length=7, blank=True, default='#0a5286',
        help_text=_('The text color on page body.'),
        verbose_name=_('[Body] Text Color')
    )
    body_link_hover = models.CharField(
        max_length=7, blank=True, default='#0a5286',
        help_text=_('(Hover action)The link color on page body.'),
        verbose_name=_('[Body] Link Text Color (Hover action)')
    )
    body_block = models.CharField(
        max_length=7, blank=True, default='#ECF0F1',
        help_text=_('The block color on page body.'),
        verbose_name=_('[Body] Block Background Color')
    )
    body_primary_btn = models.CharField(
        max_length=7, blank=True, default='#0F75BD',
        help_text=_('The background color of primary button on page body.'),
        verbose_name=_('[Body] Primary Button Background Color')
    )
    lpanel_bg = models.CharField(
        max_length=7, blank=True, default='#ffffff',
        help_text=_('The background color on left panel components.'),
        verbose_name=_('[Left Panel] Background Color')
    )
    lpanel_collapse_btn_bg = models.CharField(
        max_length=7, blank=True, default='#ffffff',
        help_text=_('The background color of collapse button on left panel.'),
        verbose_name=_('[Left Panel] Collapse Button Background Color')
    )
    lpanel_collapse_btn_text = models.CharField(
        max_length=7, blank=True, default='#0F75BD',
        help_text=_('The text color of collapse button on left panel.'),
        verbose_name=_('[Left Panel] Collapse Button Text Color')
    )
    lpanel_collapse_btn_bg_hover = models.CharField(
        max_length=7, blank=True, default='#0F75BD',
        help_text=_('(Hover action)The background color of collapse button on left panel.'),
        verbose_name=_('[Left Panel] Collapse Button Background Color(Hover action)')
    )
    lpanel_collapse_btn_text_hover = models.CharField(
        max_length=7, blank=True, default='#ffffff',
        help_text=_('(Hover action)The text color of collapse button on left panel.'),
        verbose_name=_('[Left Panel] Collapse Button Text Color(Hover action)')
    )
    lpanel_collapsed_panel_bg = models.CharField(
        max_length=7, blank=True, default='#ffffff',
        help_text=_('(Active action)The background color of collapsed panel on left panel.'),
        verbose_name=_('[Left Panel] Collapsed Panel Background Color(Active action)')
    )
    lpanel_collapsed_btn_text = models.CharField(
        max_length=7, blank=True, default='#ffffff',
        help_text=_('(Active action)The text color of collapsed button on left panel.'),
        verbose_name=_('[Left Panel] Collapsed Button Text Color(Active action)')
    )
    lpanel_collapsed_btn_bg_hover = models.CharField(
        max_length=7, blank=True, default='#0F75BD',
        help_text=_('(Active+Hover action)The background color of collapsed button on left panel.'),
        verbose_name=_('[Left Panel] Collapsed Button Background Color(Active+Hover action)')
    )
    rnav_bg_hover = models.CharField(
        max_length=7, blank=True, default='#0F75BD',
        help_text=_('(Hover action)The background color of button on right navbar.'),
        verbose_name=_('[Right Navbar] Button Background Color(Hover action)')
    )
    rnav_text_hover = models.CharField(
        max_length=7, blank=True, default='#0F75BD',
        help_text=_('(Hover action)The text color of button on right navbar.'),
        verbose_name=_('[Right Navbar] Button Text Color(Hover action)')
    )
    rnav_panelex_bg = models.CharField(
        max_length=7, blank=True, default='#ffffff',
        help_text=_('(Expanded Action)The background color of panel on right navbar menu list.'),
        verbose_name=_('[Right Navbar] Expanded Panel Background Color(Expanded action)')
    )
    rnav_panelex_text = models.CharField(
        max_length=7, blank=True, default='#0F75BD',
        help_text=_('(Expanded Action)The text color of panel on right navbar menu list.'),
        verbose_name=_('[Right Navbar] Expanded Panel Text Color(Expanded action)')
    )
    rnav_ex_bg_hover = models.CharField(
        max_length=7, blank=True, default='#0F75BD',
        help_text=_('(Expanded+Hover Action)The background color of panel on right navbar menu list when hover.'),
        verbose_name=_('[Right Navbar] Expanded Panel Background Color(Expanded+Hover action)')
    )
    rnav_ex_text_hover = models.CharField(
        max_length=7, blank=True, default='#ffffff',
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

    def delete(self, *args, **kwargs):
        try:
            Asset.objects.get(label=self.label+'_logo').delete()
            Asset.objects.get(label=self.label+'_font').delete()
            Asset.objects.get(label=self.label+'_header_font').delete()
        except:
            logger.debug(
                'Asset logo and font label="%s" not found', self.label
            )
        return super().delete(*args, **kwargs)

@receiver(post_save, sender=Theme)
def set_asset_permissions(sender, instance, created, **kwargs):

    try:
        logo_acl = AccessControlList.objects.create(
            content_type=ContentType.objects
                .get(app_label='converter', model='asset'),
            content_object=Asset.objects.get(label=instance.label+'_logo'),
            role=Role.objects.get(label='Users')
        )

        font_acl = AccessControlList.objects.create(
            content_type=ContentType.objects
                .get(app_label='converter', model='asset'),
            content_object=Asset.objects.get(label=instance.label+'_font'),
            role=Role.objects.get(label='Users')
        )

        font_header_acl = AccessControlList.objects.create(
            content_type=ContentType.objects
                .get(app_label='converter', model='asset'),
            content_object=Asset.objects.get(label=instance.label+'_header_font'),
            role=Role.objects.get(label='Users')
        )

        stored_permission = StoredPermission.objects.get(
                    namespace='converter',
                    name='asset_view',
                )
        logo_acl.permissions.add(stored_permission)
        font_acl.permissions.add(stored_permission)
        font_header_acl.permissions.add(stored_permission)
    except:
        logger.debug(
                'ACLs for assets in theme="%s" was created', instance.label
            )

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
