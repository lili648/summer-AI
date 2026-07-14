# auth_app/auth.py
"""用户认证系统 - 业务逻辑层"""
import bcrypt
import pymysql
import streamlit as st

from database import find_user, insert_user, update_last_login


def hash_password(password: str) -> str:
    """对明文密码进行 bcrypt 哈希"""
    return bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """验证明文密码与 bcrypt 哈希是否匹配"""
    return bcrypt.checkpw(
        password.encode("utf-8"), password_hash.encode("utf-8")
    )


def register(username: str, password: str) -> tuple[bool, str]:
    """注册新用户，返回 (成功与否, 提示消息)"""
    # 校验非空
    if not username or not password:
        return False, "用户名和密码不能为空"
    # 校验密码长度
    if len(password) < 6:
        return False, "密码至少需要 6 位"
    # 校验用户名不重复
    if find_user(username) is not None:
        return False, "该用户名已被注册"
    # bcrypt 哈希并写入
    try:
        hashed = hash_password(password)
        insert_user(username, hashed)
        return True, "注册成功！请登录"
    except pymysql.IntegrityError:
        return False, "该用户名已被注册"
    except Exception:
        return False, "系统错误，请联系管理员"


def login(username: str, password: str) -> tuple[bool, str]:
    """验证用户登录，成功时写入 session，返回 (成功与否, 提示消息)"""
    # 校验非空
    if not username or not password:
        return False, "用户名和密码不能为空"
    # 查用户
    user = find_user(username)
    if user is None:
        return False, "用户名或密码错误"
    # 验证密码
    if not verify_password(password, user["password"]):
        return False, "用户名或密码错误"
    # 登录成功
    st.session_state["user"] = username
    try:
        update_last_login(username)
    except Exception:
        pass  # 更新登录时间失败不影响正常登录
    return True, "登录成功"


def logout() -> None:
    """清除登录会话"""
    st.session_state.pop("user", None)


def get_current_user() -> str | None:
    """获取当前登录用户名，未登录返回 None"""
    return st.session_state.get("user", None)