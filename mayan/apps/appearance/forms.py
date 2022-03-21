from django import forms

from mayan.apps.views.forms import DetailForm

from .models import Theme, UserThemeSetting

from mayan.apps.converter.models import Asset

from django.forms.widgets import TextInput


class ThemeForm(forms.ModelForm):
    
    logo_file = forms.ImageField(required=False)
    font_file = forms.FileField(required=False)

    class Meta:
        fields = (
            'default', 'label', 'logo_file', 'font_file',
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
        '''

        logo_asset, created = Asset.objects.get_or_create(label=logo_label, internal_name=logo_label)
        font_asset, created = Asset.objects.get_or_create(label=font_label, internal_name=font_label)
        
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
