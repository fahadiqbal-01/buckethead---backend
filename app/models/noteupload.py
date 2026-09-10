from app.database.db import pool


def create_note_post(user_id: str, color: str, node_title: str, note_text: str):
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO notespost (user_id, color, node_title, note_text)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (user_id, color, node_title, note_text),
                )
                row = cur.fetchone()

                if row is None:
                    return {"error": "insert failed"}

                return {
                    "id": str(row[0]),
                    "user_id": str(user_id),
                    "color": color,
                    "node_title": node_title,
                    "note_text": note_text,
                }
    except Exception as exc:
        return {"error": "db insert failed", "details": str(exc)}


def get_note_posts(user_id: str):
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, user_id, color, node_title, note_text
                    FROM notespost
                    WHERE user_id = %s
                    ORDER BY id DESC
                    """,
                    (user_id,),
                )
                rows = cur.fetchall()

                notes = []
                for row in rows:
                    notes.append({
                        "id": str(row[0]),
                        "user_id": str(row[1]),
                        "color": row[2],
                        "node_title": row[3],
                        "note_text": row[4],
                    })
                return notes
    except Exception as exc:
        return {"error": "db query failed", "details": str(exc)}


def update_note_color(user_id: str, note_id: str, color: str):
    clean_color = color.strip()[:7]
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE notespost
                    SET color = %s
                    WHERE id = %s AND user_id = %s
                    RETURNING id, color;
                    """,
                    (clean_color, note_id, user_id),
                )
                row = cur.fetchone()
                if not row:
                    return {"error": "not_found", "details": "Note not found or unauthorized"}
                return {"success": True, "id": str(row[0]), "color": row[1]}
    except Exception as exc:
        return {"error": "db update failed", "details": str(exc)}
