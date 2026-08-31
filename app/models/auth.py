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
        
def remove_user(user_id):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""DELETE FROM users where id=%s RETURNING id""",
                        (user_id,))
            user=cur.fetchone()
            if user[0] is None:
                return None
            return{"id":"user deleted", "id":str(user[0])}
