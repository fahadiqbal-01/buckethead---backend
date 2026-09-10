from app.database.db import pool


def create_space(user_id: str, folder_name: str, folder_color: str):
    clean_name = folder_name.strip()[:15]
    clean_color = folder_color.strip()[:7]

    if not clean_name:
        return {"error": "Folder name cannot be empty"}

    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, folder_name, folder_color 
                    FROM folder 
                    WHERE user_id = %s AND LOWER(folder_name) = LOWER(%s)
                    LIMIT 1;
                    """,
                    (user_id, clean_name),
                )
                existing = cur.fetchone()
                if existing:
                    return {
                        "error": "space_exists",
                        "details": f"A space named '{clean_name}' already exists",
                    }

                cur.execute(
                    """
                    INSERT INTO folder (user_id, folder_name, folder_color, post_id)
                    VALUES (%s, %s, %s, NULL)
                    RETURNING id, folder_name, folder_color;
                    """,
                    (user_id, clean_name, clean_color),
                )
                row = cur.fetchone()
                return {
                    "id": str(row[0]),
                    "user_id": str(user_id),
                    "folder_name": row[1],
                    "folder_color": row[2],
                    "post_ids": [],
                }
    except Exception as exc:
        return {"error": "db insert failed", "details": str(exc)}


def get_user_spaces(user_id: str):
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        folder_name, 
                        folder_color, 
                        ARRAY_REMOVE(ARRAY_AGG(post_id), NULL) AS post_ids
                    FROM folder
                    WHERE user_id = %s
                    GROUP BY folder_name, folder_color
                    ORDER BY folder_name ASC;
                    """,
                    (user_id,),
                )
                rows = cur.fetchall()
                spaces = []
                for row in rows:
                    raw_post_ids = row[2] or []
                    post_ids = [str(pid) for pid in raw_post_ids if pid is not None]
                    spaces.append({
                        "folder_name": row[0],
                        "folder_color": row[1],
                        "post_ids": post_ids,
                    })
                return spaces
    except Exception as exc:
        return {"error": "db query failed", "details": str(exc)}


def add_item_to_space(user_id: str, folder_name: str, post_id: str):
    clean_name = folder_name.strip()

    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT folder_color 
                    FROM folder 
                    WHERE user_id = %s AND LOWER(folder_name) = LOWER(%s)
                    LIMIT 1;
                    """,
                    (user_id, clean_name),
                )
                row = cur.fetchone()
                if not row:
                    return {"error": "not_found", "details": f"Space '{clean_name}' not found"}

                folder_color = row[0]

                cur.execute(
                    """
                    SELECT id 
                    FROM folder 
                    WHERE user_id = %s AND LOWER(folder_name) = LOWER(%s) AND post_id = %s
                    LIMIT 1;
                    """,
                    (user_id, clean_name, post_id),
                )
                existing = cur.fetchone()
                if existing:
                    return {
                        "success": True,
                        "message": "Item already in space",
                        "folder_name": clean_name,
                        "post_id": post_id,
                    }

                cur.execute(
                    """
                    INSERT INTO folder (user_id, folder_name, folder_color, post_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (user_id, clean_name, folder_color, post_id),
                )
                new_row = cur.fetchone()

                cur.execute(
                    """
                    DELETE FROM folder 
                    WHERE user_id = %s AND LOWER(folder_name) = LOWER(%s) AND post_id IS NULL;
                    """,
                    (user_id, clean_name),
                )

                return {
                    "success": True,
                    "id": str(new_row[0]),
                    "folder_name": clean_name,
                    "post_id": post_id,
                }
    except Exception as exc:
        return {"error": "db insert failed", "details": str(exc)}


def remove_item_from_space(user_id: str, folder_name: str, post_id: str):
    clean_name = folder_name.strip()

    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT folder_color 
                    FROM folder 
                    WHERE user_id = %s AND LOWER(folder_name) = LOWER(%s)
                    LIMIT 1;
                    """,
                    (user_id, clean_name),
                )
                color_row = cur.fetchone()
                if not color_row:
                    return {"error": "not_found", "details": f"Space '{clean_name}' not found"}
                folder_color = color_row[0]

                cur.execute(
                    """
                    DELETE FROM folder 
                    WHERE user_id = %s AND LOWER(folder_name) = LOWER(%s) AND post_id = %s
                    RETURNING id;
                    """,
                    (user_id, clean_name, post_id),
                )
                deleted_rows = cur.fetchall()

                cur.execute(
                    """
                    SELECT count(*) 
                    FROM folder 
                    WHERE user_id = %s AND LOWER(folder_name) = LOWER(%s);
                    """,
                    (user_id, clean_name),
                )
                count = cur.fetchone()[0]

                if count == 0:
                    cur.execute(
                        """
                        INSERT INTO folder (user_id, folder_name, folder_color, post_id)
                        VALUES (%s, %s, %s, NULL);
                        """,
                        (user_id, clean_name, folder_color),
                    )

                return {
                    "success": True,
                    "removed": len(deleted_rows) > 0,
                    "folder_name": clean_name,
                    "post_id": post_id,
                }
    except Exception as exc:
        return {"error": "db delete failed", "details": str(exc)}


def delete_space(user_id: str, folder_name: str):
    clean_name = folder_name.strip()

    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM folder 
                    WHERE user_id = %s AND LOWER(folder_name) = LOWER(%s)
                    RETURNING id;
                    """,
                    (user_id, clean_name),
                )
                deleted = cur.fetchall()
                if not deleted:
                    return {"error": "not_found", "details": f"Space '{clean_name}' not found"}
                return {"success": True, "folder_name": clean_name, "deleted_rows": len(deleted)}
    except Exception as exc:
        return {"error": "db delete failed", "details": str(exc)}
