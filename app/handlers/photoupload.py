from app.models.photoupload import create_photo_post


def photo_upload(user_id, photo_url, name, note):
    return create_photo_post(
        user_id=user_id,
        photo_url=photo_url,
        photo_name=name,
        photo_note=note,
    )