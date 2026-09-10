from app.database.db import pool
from app.utils.bcrypt import verify_password
from psycopg import errors

def create_user(name, email, password):
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO users (name, email, password_hash) 
                    VALUES (%s, %s, %s) RETURNING id""",
                    (name, email, password)
                )
                user = cur.fetchone()

        if user is None:
            raise RuntimeError("Insert did not return a row")

        return {"id": str(user[0])}

    except errors.UniqueViolation:
        raise ValueError(f"User already exists")

    except Exception:
        raise

def validate_user(email, password):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT id, password_hash FROM users WHERE email=%s""",
                        (email,))
            user = cur.fetchone()
            if user is None:
                return {"err": "invalid credentials"}
            
            user_id, stored_hash = user
            if verify_password(password, stored_hash):
                return {"id": str(user_id)}
            else:
                return {"err": "invalid credentials"}

def update_user(user_id, name,email,Password_hash):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""UPDATE users SET name=%s, email=%s, password_hash=%s WHERE id=%s RETURNING id """,
                        (name, email,Password_hash, user_id))
            user=cur.fetchone()
            if user is None:
                return{"message":"user not found"}
            return{"id":str(user[0])}
        
def get_user_by_id(user_id: str):
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, email, image_url FROM users WHERE id = %s", (user_id,))
                row = cur.fetchone()
                if row is None:
                    return None
                return {
                    "id": str(row[0]),
                    "name": row[1] or "",
                    "email": row[2] or "",
                    "image_url": row[3] or "",
                }
    except Exception as exc:
        return {"error": "db query failed", "details": str(exc)}


def update_username(user_id: str, new_name: str):
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET name = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING id, name;",
                    (new_name, user_id),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                return {"id": str(row[0]), "name": row[1]}
    except Exception as exc:
        return {"error": "db update failed", "details": str(exc)}


def update_user_image(user_id: str, image_url: str):
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET image_url = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING id, image_url;",
                    (image_url, user_id),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                return {"id": str(row[0]), "image_url": row[1]}
    except Exception as exc:
        return {"error": "db update failed", "details": str(exc)}


