# Generated by Django 2.2.24 on 2022-03-05 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document_states', '0023_auto_20200930_0726'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflowstate',
            name='end_date',
            field=models.DateTimeField(blank=True, help_text='End date of this state.', null=True, verbose_name='EndDate'),
        ),
        migrations.AddField(
            model_name='workflowstate',
            name='start_date',
            field=models.DateTimeField(blank=True, help_text='Start date of this state.', null=True, verbose_name='StartDate'),
        ),
        migrations.AlterField(
            model_name='workflowstate',
            name='label',
            field=models.TextField(help_text='A short text to describe the workflow state.', verbose_name='Label'),
        ),
    ]
