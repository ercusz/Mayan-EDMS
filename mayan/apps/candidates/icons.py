from mayan.apps.appearance.classes import Icon

icon_user_setup = Icon(driver_name='fontawesome', symbol='user')

# Current user

icon_current_user_details = Icon(driver_name='fontawesome', symbol='user')
icon_current_user_edit = Icon(
    driver_name='fontawesome-dual', primary_symbol='user',
    secondary_symbol='pencil-alt'
)

# Group

icon_group = Icon(driver_name='fontawesome', symbol='users')
icon_group_create = Icon(
    driver_name='fontawesome-dual', primary_symbol='users',
    secondary_symbol='plus'
)
icon_group_delete_single = Icon(driver_name='fontawesome', symbol='times')
icon_group_edit = Icon(driver_name='fontawesome', symbol='pencil-alt')
icon_group_list = Icon(driver_name='fontawesome', symbol='users')
icon_group_delete_multiple = icon_group_delete_single
icon_group_user_list = Icon(driver_name='fontawesome', symbol='user')
icon_group_setup = Icon(driver_name='fontawesome', symbol='users')
icon_user_create = Icon(
    driver_name='fontawesome-dual', primary_symbol='user',
    secondary_symbol='plus'
)

# User

icon_user_delete_single = Icon(driver_name='fontawesome', symbol='times')
icon_user_edit = Icon(driver_name='fontawesome', symbol='pencil-alt')
icon_user_group_list = icon_group
icon_user_list = Icon(driver_name='fontawesome', symbol='user')
icon_user_delete_multiple = icon_user_delete_single
icon_user_multiple_set_password = Icon(driver_name='fontawesome', symbol='key')
icon_user_set_options = Icon(driver_name='fontawesome', symbol='cog')
