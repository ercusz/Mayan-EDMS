# Generated by Django 2.2.24 on 2022-03-18 15:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('converter', '0019_auto_20200819_0852'),
        ('appearance', '0004_theme_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='theme',
            name='logo_file',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='converter.Asset', verbose_name='Logo file'),
        ),
    ]
