from django import forms

from mayan.apps.views.forms import DetailForm

from .models import Theme, UserThemeSetting

from mayan.apps.converter.models import Asset


class ThemeForm(forms.ModelForm):
    
    logo_file = forms.ImageField(required=False)
    font_file = forms.FileField(required=False)

    class Meta:
        fields = ('label', 'stylesheet', 'default', 'logo_file', 'font_file',)
        model = Theme
        widgets = {
            'font_file': forms.FileInput(
                attrs={
                    'accept': '.eot, .ttf, .woff, .otf'
                }
            )
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        logo_label = obj.label + '_logo'
        font_label = obj.label + '_font'

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
