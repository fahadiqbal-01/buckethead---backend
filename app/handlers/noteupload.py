from app.models.noteupload import create_note_post, get_note_posts, update_note_color


def note_upload(user_id, color, node_title, note_text):
    return create_note_post(
        user_id=user_id,
        color=color,
        node_title=node_title,
        note_text=note_text,
    )


def fetch_user_notes(user_id):
    return get_note_posts(user_id)


def change_note_color(user_id, note_id, color):
    return update_note_color(user_id=user_id, note_id=note_id, color=color)
