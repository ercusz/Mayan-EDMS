from django.apps import apps


def handler_initialize_new_user_options(sender, instance, **kwargs):
    CandidatesOptions = apps.get_model(
        app_label='candidates', model_name='CandidatesOptions'
    )

    if kwargs['created']:
        CandidatesOptions.objects.create(user=instance)
