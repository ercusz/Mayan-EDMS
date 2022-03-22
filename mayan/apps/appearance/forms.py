from django import forms

from mayan.apps.views.forms import DetailForm

from .models import Theme, UserThemeSetting

from mayan.apps.converter.models import Asset

from django.forms.widgets import TextInput

from django.core.validators import FileExtensionValidator

from mayan.apps.acls.models import AccessControlList

from mayan.apps.permissions.models import Role, StoredPermission

from django.contrib.contenttypes.models import ContentType


class ThemeForm(forms.ModelForm):
    logo_file = forms.ImageField(required=False, validators=[FileExtensionValidator(['png','jpg','jpeg','webp'])])
    font_file = forms.FileField(required=False, validators=[FileExtensionValidator(['woff2','woff','ttf','otf'])])
    font_header_file = forms.FileField(required=False, validators=[FileExtensionValidator(['woff2','woff','ttf','otf'])])

    class Meta:
        fields = (
            'default', 'label', 'logo_file', 'font_file', 'font_header_file',
            'header_text_brand', 'header_text_brand_size',
            'header_bg', 'header_text', 'body_bg', 'body_text',
            'body_link_hover', 'body_block', 'body_primary_btn',
            'lpanel_bg', 'lpanel_collapse_btn_bg',
            'lpanel_collapse_btn_text', 'lpanel_collapse_btn_bg_hover',
            'lpanel_collapse_btn_text_hover', 'lpanel_collapsed_panel_bg',
            'lpanel_collapsed_btn_text', 'lpanel_collapsed_btn_bg_hover',
            'rnav_bg_hover', 'rnav_text_hover', 'rnav_panelex_bg', 'rnav_panelex_text',
            'rnav_ex_bg_hover', 'rnav_ex_text_hover', 'stylesheet',
        )
        model = Theme
        widgets = {
            'font_file': forms.FileInput(
                attrs={
                    'accept': '.woff2, .woff, .ttf, .otf'
                }
            ),
            'font_header_file': forms.FileInput(
                attrs={
                    'accept': '.woff2, .woff, .ttf, .otf'
                }
            ),
            'header_bg': TextInput(attrs={'type': 'color'}),
            'header_text': TextInput(attrs={'type': 'color'}),
            'body_bg': TextInput(attrs={'type': 'color'}),
            'body_text': TextInput(attrs={'type': 'color'}),
            'body_link_hover': TextInput(attrs={'type': 'color'}),
            'body_block': TextInput(attrs={'type': 'color'}),
            'body_primary_btn': TextInput(attrs={'type': 'color'}),
            'lpanel_bg': TextInput(attrs={'type': 'color'}),
            'lpanel_collapse_btn_bg': TextInput(attrs={'type': 'color'}),
            'lpanel_collapse_btn_text': TextInput(attrs={'type': 'color'}),
            'lpanel_collapse_btn_bg_hover': TextInput(attrs={'type': 'color'}),
            'lpanel_collapse_btn_text_hover': TextInput(attrs={'type': 'color'}),
            'lpanel_collapsed_panel_bg': TextInput(attrs={'type': 'color'}),
            'lpanel_collapsed_btn_text': TextInput(attrs={'type': 'color'}),
            'lpanel_collapsed_btn_bg_hover': TextInput(attrs={'type': 'color'}),
            'rnav_bg_hover': TextInput(attrs={'type': 'color'}),
            'rnav_text_hover': TextInput(attrs={'type': 'color'}),
            'rnav_panelex_bg': TextInput(attrs={'type': 'color'}),
            'rnav_panelex_text': TextInput(attrs={'type': 'color'}),
            'rnav_ex_bg_hover': TextInput(attrs={'type': 'color'}),
            'rnav_ex_text_hover': TextInput(attrs={'type': 'color'}),
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        logo_label = obj.label + '_logo'
        font_label = obj.label + '_font'
        font_header_label = obj.label + '_header_font'
        stylesheet = f'''
        :root {{
            /* header section */
            {'--cp_header_bg: ' + self.cleaned_data['header_bg'] + ';'
                if self.cleaned_data['header_bg'] is not None else ''}
            {'--cp_header_text: ' + self.cleaned_data['header_text'] + ';'
                if self.cleaned_data['header_text'] is not None else ''}
            
            /* body */
            {'--cp_body_bg: ' + self.cleaned_data['body_bg'] + ';'
                if self.cleaned_data['body_bg'] is not None else ''}
            {'--cp_body_text: ' + self.cleaned_data['body_text'] + ';'
                if self.cleaned_data['body_text'] is not None else ''}
            {'--cp_body_link_hover: ' + self.cleaned_data['body_link_hover'] + ';'
                if self.cleaned_data['body_link_hover'] is not None else ''}
            {'--cp_body_block: ' + self.cleaned_data['body_block'] + ';'
                if self.cleaned_data['body_block'] is not None else ''}
            {'--cp_body_primary_btn: ' + self.cleaned_data['body_primary_btn'] + ';'
                if self.cleaned_data['body_primary_btn'] is not None else ''}

            /* left panel section */
            /* left panel bg */
            {'--cp_lpanel_bg: ' + self.cleaned_data['lpanel_bg'] + ';'
                if self.cleaned_data['lpanel_bg'] is not None else ''}
            /* collapse btn */
            {'--cp_lpanel_collapse_btn_bg: ' + self.cleaned_data['lpanel_collapse_btn_bg'] + ';'
                if self.cleaned_data['lpanel_collapse_btn_bg'] is not None else ''}
            {'--cp_lpanel_collapse_btn_text: ' + self.cleaned_data['lpanel_collapse_btn_text'] + ';'
                if self.cleaned_data['lpanel_collapse_btn_text'] is not None else ''}
            {'--cp_lpanel_collapse_btn_bg_hover: ' + self.cleaned_data['lpanel_collapse_btn_bg_hover'] + ';'
                if self.cleaned_data['lpanel_collapse_btn_bg_hover'] is not None else ''}
            {'--cp_lpanel_collapse_btn_text_hover: ' + self.cleaned_data['lpanel_collapse_btn_text_hover'] + ';'
                if self.cleaned_data['lpanel_collapse_btn_text_hover'] is not None else ''}
            /* collapsed btn */
            {'--cp_lpanel_collapsed_panel_bg: ' + self.cleaned_data['lpanel_collapsed_panel_bg'] + ';'
                if self.cleaned_data['lpanel_collapsed_panel_bg'] is not None else ''}
            {'--cp_lpanel_collapsed_btn_text: ' + self.cleaned_data['lpanel_collapsed_btn_text'] + ';'
                if self.cleaned_data['lpanel_collapsed_btn_text'] is not None else ''}
            {'--cp_lpanel_collapsed_btn_bg_hover: ' + self.cleaned_data['lpanel_collapsed_btn_bg_hover'] + ';'
                if self.cleaned_data['lpanel_collapsed_btn_bg_hover'] is not None else ''}

            /* right navbar */
            {'--cp_rnav_bg_hover: ' + self.cleaned_data['rnav_bg_hover'] + ';'
                if self.cleaned_data['rnav_bg_hover'] is not None else ''}
            {'--cp_rnav_text_hover: ' + self.cleaned_data['rnav_text_hover'] + ';'
                if self.cleaned_data['rnav_text_hover'] is not None else ''}
            {'--cp_rnav_panelex_bg: ' + self.cleaned_data['rnav_panelex_bg'] + ';'
                if self.cleaned_data['rnav_panelex_bg'] is not None else ''}
            {'--cp_rnav_panelex_text: ' + self.cleaned_data['rnav_panelex_text'] + ';'
                if self.cleaned_data['rnav_panelex_text'] is not None else ''}
            {'--cp_rnav_ex_bg_hover: ' + self.cleaned_data['rnav_ex_bg_hover'] + ';'
                if self.cleaned_data['rnav_ex_bg_hover'] is not None else ''}
            {'--cp_rnav_ex_text_hover: ' + self.cleaned_data['rnav_ex_text_hover'] + ';'
                if self.cleaned_data['rnav_ex_text_hover'] is not None else ''}
        }}

        .navbar-brand {{
            {'font-size: ' + str(self.cleaned_data['header_text_brand_size']) + 'px !important;'}
        }}
        '''

        logo_asset, created = Asset.objects.get_or_create(label=logo_label, internal_name=logo_label)
        font_asset, created = Asset.objects.get_or_create(label=font_label, internal_name=font_label)
        font_header_asset, created = Asset.objects.get_or_create(label=font_header_label, internal_name=font_header_label)

        logo_file = self.cleaned_data['logo_file']
        if logo_file is not None:
            logo_asset.file = logo_file
            logo_asset.save()
            obj.logo_asset = logo_asset

        font_file = self.cleaned_data['font_file']
        if font_file is not None:
            font_asset.file = font_file
            font_asset.save()
            obj.font_asset = font_asset

        font_header_file = self.cleaned_data['font_header_file']
        if font_header_file is not None:
            font_header_asset.file = font_header_file
            font_header_asset.save()
            obj.font_header_asset = font_header_asset

        obj.stylesheet = stylesheet

        if commit:
            obj.save()

        return obj

class UserThemeSettingForm(forms.ModelForm):
    class Meta:
        fields = ('theme',)
        model = UserThemeSetting
        widgets = {
            'theme': forms.Select(
                attrs={
                    'class': 'select2'
                }
            ),
        }


class UserThemeSettingForm_view(DetailForm):
    class Meta:
        fields = ('theme',)
        model = UserThemeSetting
