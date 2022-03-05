# Generated by Django 2.2.24 on 2022-03-05 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document_states', '0024_auto_20220305_1627'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workflowstate',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='workflowstate',
            name='start_date',
        ),
        migrations.AddField(
            model_name='workflowstate',
            name='end_datetime',
            field=models.DateTimeField(blank=True, help_text='Date and time for this state deactivated.', null=True, verbose_name='End Date'),
        ),
        migrations.AddField(
            model_name='workflowstate',
            name='start_datetime',
            field=models.DateTimeField(blank=True, help_text='Date and time for this state activated.', null=True, verbose_name='Start Date'),
        ),
    ]
