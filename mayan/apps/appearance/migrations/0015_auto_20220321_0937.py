# Generated by Django 2.2.24 on 2022-03-21 02:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appearance', '0014_auto_20220321_0914'),
    ]

    operations = [
        migrations.AddField(
            model_name='theme',
            name='body_bg',
            field=models.CharField(blank=True, help_text='The background color on page body.', max_length=7, verbose_name='[Body] Background Color'),
        ),
        migrations.AddField(
            model_name='theme',
            name='body_block',
            field=models.CharField(blank=True, help_text='The block color on page body.', max_length=7, verbose_name='[Body] Block Background Color'),
        ),
        migrations.AddField(
            model_name='theme',
            name='body_link_hover',
            field=models.CharField(blank=True, help_text='(Hover action)The link color on page body.', max_length=7, verbose_name='[Body] Link Text Color (Hover action)'),
        ),
        migrations.AddField(
            model_name='theme',
            name='body_primary_btn',
            field=models.CharField(blank=True, help_text='The background color of primary button on page body.', max_length=7, verbose_name='[Body] Primary Button Background Color'),
        ),
        migrations.AddField(
            model_name='theme',
            name='body_text',
            field=models.CharField(blank=True, help_text='The text color on page body.', max_length=7, verbose_name='[Body] Text Color'),
        ),
    ]
