"""用户认证系统 - 数据访问层"""
import pymysql

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Liyizhang_10",
    "database": "app_auth",
    "charset": "utf8mb4",
}


def get_conn():
    """获取 MySQL 数据库连接"""
    return pymysql.connect(**DB_CONFIG)


def find_user(username: str) -> dict | None:
    """按用户名查询用户，返回用户记录字典；不存在则返回 None"""
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password, created_at, last_login "
            "FROM users WHERE username = %(username)s",
            {"username": username},
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return {
            "id": row[0],
            "username": row[1],
            "password": row[2],
            "created_at": row[3],
            "last_login": row[4],
        }
    finally:
        conn.close()


def insert_user(username: str, password_hash: str) -> None:
    """插入新用户，用户名重复时抛出 pymysql.IntegrityError"""
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%(username)s, %(password)s)",
            {"username": username, "password": password_hash},
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_last_login(username: str) -> None:
    """更新指定用户的最后登录时间为当前时间"""
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET last_login = NOW() WHERE username = %(username)s",
            {"username": username},
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()