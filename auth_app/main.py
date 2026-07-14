# auth_app/main.py
"""用户认证系统 - Streamlit 入口与页面路由"""
import streamlit as st

from auth import login, register, logout, get_current_user

st.set_page_config(
    page_title="内部工具用户认证",
    page_icon="🔐",
    layout="centered",
)

# ====== 登录态守卫 ======
if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"]:
    # ====== 已登录：显示主功能页面 ======
    with st.sidebar:
        st.write(f"👤 当前登录：**{st.session_state['user']}**")
        st.divider()
        if st.button("🚪 登出", use_container_width=True):
            logout()
            st.rerun()

    st.title("🏠 主功能页面")
    st.success(f"欢迎，**{st.session_state['user']}**！")
    st.write("在此处添加业务功能内容。")

else:
    # ====== 未登录：显示登录 / 注册 Tab ======
    st.title("🔐 内部工具用户认证")

    tab_login, tab_register = st.tabs(["登录", "注册"])

    with tab_login:
        st.subheader("用户登录")
        login_username = st.text_input("用户名", key="login_username")
        login_password = st.text_input(
            "密码", type="password", key="login_password"
        )

        if st.button("登  录", type="primary", use_container_width=True):
            ok, msg = login(login_username, login_password)
            if ok:
                st.rerun()
            else:
                st.error(msg)

    with tab_register:
        st.subheader("用户注册")
        reg_username = st.text_input("用户名", key="reg_username")
        reg_password = st.text_input(
            "密码", type="password", key="reg_password",
            help="至少 6 位"
        )
        reg_confirm = st.text_input(
            "确认密码", type="password", key="reg_confirm",
        )

        if st.button("注  册", type="primary", use_container_width=True):
            if reg_password != reg_confirm:
                st.error("两次输入的密码不一致")
            else:
                ok, msg = register(reg_username, reg_password)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)