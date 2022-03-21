# Generated by Django 2.2.24 on 2022-03-21 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appearance', '0009_auto_20220321_0800'),
    ]

    operations = [
        migrations.AddField(
            model_name='theme',
            name='lpanel_collapse_btn_text',
            field=models.CharField(blank=True, help_text='The text color of collapse button on left panel.', max_length=7, verbose_name='[Left Panel] Collapse Button Text Color'),
        ),
        migrations.AlterField(
            model_name='theme',
            name='header_bg',
            field=models.CharField(blank=True, help_text='The background color on header components.', max_length=7, verbose_name='[Header] Background Color'),
        ),
        migrations.AlterField(
            model_name='theme',
            name='header_text',
            field=models.CharField(blank=True, help_text='The text color on header components.', max_length=7, verbose_name='[Header] Text Color'),
        ),
        migrations.AlterField(
            model_name='theme',
            name='lpanel_collapse_btn_bg',
            field=models.CharField(blank=True, help_text='The background color of collapse button on left panel.', max_length=7, verbose_name='[Left Panel] Collapse Button Background Color'),
        ),
    ]
