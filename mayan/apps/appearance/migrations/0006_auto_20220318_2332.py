# Generated by Django 2.2.24 on 2022-03-18 16:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appearance', '0005_theme_logo_file'),
    ]

    operations = [
        migrations.RenameField(
            model_name='theme',
            old_name='logo_file',
            new_name='logo_asset',
        ),
    ]
