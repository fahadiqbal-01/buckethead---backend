from app.database.db import pool


def create_link_post(user_id: str, image_url: str, link_name: str, link_url: str, link_desc: str):
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO linkpost (user_id, image_url, link_name, link_url, link_desc)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (user_id, image_url, link_name, link_url, link_desc),
                )
                row = cur.fetchone()

                if row is None:
                    return {"error": "insert failed"}

                return {
                    "id": str(row[0]),
                    "user_id": str(user_id),
                    "image_url": image_url,
                    "link_name": link_name,
                    "link_url": link_url,
                    "link_desc": link_desc,
                }
    except Exception as exc:
        return {"error": "db insert failed", "details": str(exc)}


def get_link_posts(user_id: str):
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, user_id, image_url, link_name, link_url, link_desc
                    FROM linkpost
                    WHERE user_id = %s
                    ORDER BY id DESC
                    """,
                    (user_id,),
                )
                rows = cur.fetchall()

                links = []
                for row in rows:
                    links.append({
                        "id": str(row[0]),
                        "user_id": str(row[1]),
                        "image_url": row[2] or "",
                        "link_name": row[3],
                        "link_url": row[4],
                        "link_desc": row[5] or "",
                    })
                return links
    except Exception as exc:
        return {"error": "db query failed", "details": str(exc)}
