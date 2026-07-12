import streamlit as st
import pymysql

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Liyizhang_10",
    "charset": "utf8mb4",
}
DB_NAME = "lording"
TABLE_NAME = "user"


def get_conn():
    return pymysql.connect(**DB_CONFIG, database=DB_NAME)


def get_all_usernames():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM `{TABLE_NAME}`")
        rows = cursor.fetchall()
        conn.close()
        return {row[0] for row in rows}
    except Exception:
        return set()


def insert_user(user: dict):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        f"""
        INSERT INTO `{TABLE_NAME}` (id, password)
        VALUES (%(id)s, %(password)s)
        """,
        user,
    )
    conn.commit()
    conn.close()


# ====== 注册页面 ======
st.title("用户注册")

username = st.text_input("用户名")
password = st.text_input("密码", type="password")
confirm_password = st.text_input("确认密码", type="password")

if st.button("注册"):
    # 校验
    if not username or not password:
        st.error("用户名和密码不能为空")
    elif password != confirm_password:
        st.error("两次输入的密码不一致")
    elif username in get_all_usernames():
        st.error("用户名已存在")
    else:
        insert_user({"id": username, "password": password})
        st.success("注册成功！")
