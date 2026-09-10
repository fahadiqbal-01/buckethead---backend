from app.models.posts import get_all_posts, delete_post


def fetch_all_user_posts(user_id):
    return get_all_posts(user_id)


def remove_user_post(user_id, post_type, post_id):
    return delete_post(user_id=user_id, post_type=post_type, post_id=post_id)
