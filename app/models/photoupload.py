from app.database.db import pool


def create_photo_post(user_id, photo_url, photo_name, photo_note):
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO imgpost (user_id, image_name, image_note, image_url)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (user_id, photo_name, photo_note, photo_url),
                )
                row = cur.fetchone()

                if row is None:
                    return {"error": "insert failed"}

                return {
                    "id": str(row[0]),
                    "user_id": str(user_id),
                    "image_name": photo_name,
                    "image_note": photo_note,
                    "image_url": photo_url,
                }
    except Exception as exc:
        return {"error": "db insert failed", "details": str(exc)}

