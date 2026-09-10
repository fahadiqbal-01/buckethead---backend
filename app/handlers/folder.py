from app.models.folder import (
    create_space,
    get_user_spaces,
    add_item_to_space,
    remove_item_from_space,
    delete_space,
)


def handle_create_space(user_id: str, folder_name: str, folder_color: str):
    return create_space(user_id=user_id, folder_name=folder_name, folder_color=folder_color)


def handle_get_user_spaces(user_id: str):
    return get_user_spaces(user_id=user_id)


def handle_add_item_to_space(user_id: str, folder_name: str, post_id: str):
    return add_item_to_space(user_id=user_id, folder_name=folder_name, post_id=post_id)


def handle_remove_item_from_space(user_id: str, folder_name: str, post_id: str):
    return remove_item_from_space(user_id=user_id, folder_name=folder_name, post_id=post_id)


def handle_delete_space(user_id: str, folder_name: str):
    return delete_space(user_id=user_id, folder_name=folder_name)
