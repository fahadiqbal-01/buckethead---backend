from app.database.db import pool


def get_all_posts(user_id: str):
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        id, user_id, 'image' AS post_type, 
                        image_url, image_name, image_note, 
                        NULL AS link_name, NULL AS link_url, NULL AS link_desc, 
                        NULL AS color, NULL AS node_title, NULL AS note_text,
                        created_at
                    FROM imgpost
                    WHERE user_id = %s

                    UNION ALL

                    SELECT 
                        id, user_id, 'link' AS post_type, 
                        image_url, NULL AS image_name, NULL AS image_note, 
                        link_name, link_url, link_desc, 
                        NULL AS color, NULL AS node_title, NULL AS note_text,
                        created_at
                    FROM linkpost
                    WHERE user_id = %s

                    UNION ALL

                    SELECT 
                        id, user_id, 'note' AS post_type, 
                        NULL AS image_url, NULL AS image_name, NULL AS image_note, 
                        NULL AS link_name, NULL AS link_url, NULL AS link_desc, 
                        color, node_title, note_text,
                        created_at
                    FROM notespost
                    WHERE user_id = %s

                    ORDER BY created_at DESC;
                    """,
                    (user_id, user_id, user_id),
                )
                rows = cur.fetchall()

                posts = []
                for row in rows:
                    p_type = row[2]
                    posts.append({
                        "id": str(row[0]),
                        "user_id": str(row[1]),
                        "post_type": p_type,
                        "image_url": row[3] or "",
                        "image_name": row[4] or "",
                        "image_note": row[5] or "",
                        "link_name": row[6] or "",
                        "link_url": row[7] or "",
                        "link_desc": row[8] or "",
                        "color": row[9] if row[9] else ("white" if p_type == "note" else None),
                        "node_title": row[10] or "",
                        "note_text": row[11] or "",
                        "created_at": row[12].isoformat() if row[12] else None,
                    })
                return posts
    except Exception as exc:
        return {"error": "db query failed", "details": str(exc)}


def delete_post(user_id: str, post_type: str, post_id: str):
    """
    Securely deletes a post ensuring it belongs to the authenticated user.
    """
    table_map = {
        "image": "imgpost",
        "link": "linkpost",
        "note": "notespost",
    }
    table = table_map.get(post_type.lower())
    if not table:
        return {"error": "invalid post type"}

    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                # Use parameterized query with user_id verification for security
                cur.execute(
                    f"DELETE FROM {table} WHERE id = %s AND user_id = %s RETURNING id;",
                    (post_id, user_id),
                )
                row = cur.fetchone()
                if not row:
                    return {"error": "not_found", "details": "Post not found or unauthorized"}
                return {"success": True, "id": str(row[0]), "post_type": post_type}
    except Exception as exc:
        return {"error": "db delete failed", "details": str(exc)}
