from app.models.linkupload import create_link_post, get_link_posts


def link_upload(user_id, image_url, link_name, link_url, link_desc):
    return create_link_post(
        user_id=user_id,
        image_url=image_url,
        link_name=link_name,
        link_url=link_url,
        link_desc=link_desc,
    )


def fetch_user_links(user_id):
    return get_link_posts(user_id)
