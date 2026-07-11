import streamlit as st
import re
import hashlib
import pandas as pd
import pymysql
from datetime import datetime

# ====== 页面配置 ======
st.set_page_config(
    page_title="用户注册",
    page_icon="📝",
    layout="centered",
)

# ====== 数据库配置 ======
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Liyizhang_10",
    "charset": "utf8mb4",
}
DB_NAME = "user_register"
TABLE_NAME = "load_python"


# ====== 数据库工具函数 ======
def get_conn():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG, database=DB_NAME)


def hash_password(password: str) -> str:
    """SHA-256 哈希加密"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@st.cache_data(ttl=5)
def get_all_usernames():
    """获取所有已注册的用户名（缓存5秒）"""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(f"SELECT username FROM `{TABLE_NAME}`")
        rows = cursor.fetchall()
        conn.close()
        return {row[0] for row in rows}
    except Exception:
        return set()


def load_users():
    """从数据库加载所有注册用户"""
    conn = get_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(f"SELECT * FROM `{TABLE_NAME}` ORDER BY register_time DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def insert_user(user: dict):
    """插入一条用户记录"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO `{TABLE_NAME}` (username, password_hash, real_name, email, phone, gender, age_group, occupation, interests, register_time)
        VALUES (%(username)s, %(password_hash)s, %(real_name)s, %(email)s, %(phone)s, %(gender)s, %(age_group)s, %(occupation)s, %(interests)s, %(register_time)s)
    """, user)
    conn.commit()
    conn.close()


# ====== 标题 ======
st.title("📝 用户注册表")
st.caption("请填写以下信息完成注册")

# ====== 注册表单 ======
st.subheader("👤 基本信息")

col1, col2 = st.columns(2)
with col1:
    username = st.text_input("用户名 *", placeholder="4-20位字母或数字", key="reg_username")
with col2:
    real_name = st.text_input("真实姓名", placeholder="请输入真实姓名")

# ---- 用户名实时校验 ----
if username:
    if not re.match(r"^[a-zA-Z0-9_一-龥]{4,20}$", username):
        st.warning("⚠️ 用户名需为4-20位字母、数字或中文")
    else:
        existing_usernames = get_all_usernames()
        if username in existing_usernames:
            st.error(f"⚠️ 用户名 **{username}** 已被注册，请更换")
        else:
            st.success(f"✅ 用户名 **{username}** 可用")

col3, col4 = st.columns(2)
with col3:
    password = st.text_input("密码 *", type="password", placeholder="至少6位，含字母和数字", key="reg_password")
with col4:
    confirm_password = st.text_input("确认密码 *", type="password", placeholder="请再次输入密码", key="reg_confirm")

# ---- 密码实时校验 ----
if password:
    if len(password) < 6:
        st.warning("⚠️ 密码至少需要6位")
    elif not re.search(r"[a-zA-Z]", password) or not re.search(r"[0-9]", password):
        st.warning("⚠️ 密码需同时包含字母和数字")
if confirm_password and password != confirm_password:
    st.warning("⚠️ 两次输入的密码不一致")

col5, col6 = st.columns(2)
with col5:
    email = st.text_input("邮箱 *", placeholder="example@mail.com", key="reg_email")
with col6:
    phone = st.text_input("手机号", placeholder="11位手机号", key="reg_phone")

# ---- 邮箱/手机号实时校验 ----
if email and not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
    st.warning("⚠️ 邮箱格式不正确")
if phone and not re.match(r"^1[3-9]\d{9}$", phone):
    st.warning("⚠️ 手机号格式不正确")

st.subheader("📋 补充信息")

col7, col8 = st.columns(2)
with col7:
    gender = st.radio("性别", ["男", "女", "保密"], horizontal=True, key="reg_gender")
with col8:
    age_group = st.selectbox("年龄段", ["请选择", "18岁以下", "18-25岁", "26-35岁", "36-45岁", "46岁以上"], key="reg_age")

occupation = st.selectbox("职业", ["请选择", "学生", "工程师", "教师", "医生", "设计师", "销售", "其他"], key="reg_occ")

interests = st.multiselect(
    "兴趣爱好（可多选）",
    ["编程 💻", "阅读 📚", "运动 ⚽", "音乐 🎵", "旅行 ✈️", "摄影 📷", "游戏 🎮", "美食 🍔"],
    key="reg_interests",
)

agree = st.checkbox("我已阅读并同意《用户协议》和《隐私政策》*", key="reg_agree")

st.divider()

# 提交按钮
submitted = st.button("✅ 立即注册", type="primary", use_container_width=True)

# ====== 表单验证与处理 ======
if submitted:
    errors = []

    # 用户名验证
    if not username:
        errors.append("❌ 用户名不能为空")
    elif not re.match(r"^[a-zA-Z0-9_一-龥]{4,20}$", username):
        errors.append("❌ 用户名需为4-20位字母、数字或中文")
    elif username in get_all_usernames():
        errors.append(f"❌ 用户名 **{username}** 已被注册，请更换")

    # 密码验证
    if not password:
        errors.append("❌ 密码不能为空")
    elif len(password) < 6:
        errors.append("❌ 密码至少需要6位")
    elif not re.search(r"[a-zA-Z]", password) or not re.search(r"[0-9]", password):
        errors.append("❌ 密码需同时包含字母和数字")

    # 确认密码
    if password != confirm_password:
        errors.append("❌ 两次输入的密码不一致")

    # 邮箱验证
    if not email:
        errors.append("❌ 邮箱不能为空")
    elif not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        errors.append("❌ 邮箱格式不正确")

    # 手机号验证（可选）
    if phone and not re.match(r"^1[3-9]\d{9}$", phone):
        errors.append("❌ 手机号格式不正确")

    # 协议验证
    if not agree:
        errors.append("❌ 请阅读并同意用户协议")

    # 年龄段验证
    if age_group == "请选择":
        errors.append("❌ 请选择年龄段")

    if errors:
        for err in errors:
            st.error(err)
    else:
        try:
            user_info = {
                "username": username,
                "password_hash": hash_password(password),
                "real_name": real_name or "未填写",
                "email": email,
                "phone": phone or "未填写",
                "gender": gender,
                "age_group": age_group,
                "occupation": occupation,
                "interests": "、".join(interests) if interests else "未填写",
                "register_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            insert_user(user_info)
            get_all_usernames.clear()  # 清除缓存
            st.success(f"🎉 注册成功！欢迎你，**{username}**！")
            st.balloons()
        except Exception as e:
            st.error(f"❌ 数据库错误：{e}")

# ====== 已注册用户列表 ======
try:
    users = load_users()
    if users:
        st.divider()
        st.subheader(f"📋 已注册用户（{len(users)} 人）")

        df_users = pd.DataFrame(users)
        # 隐藏敏感列
        for col in ["id", "password_hash"]:
            if col in df_users.columns:
                df_users = df_users.drop(columns=[col])
        st.dataframe(df_users, width="stretch", hide_index=True)

        csv = df_users.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 导出为 CSV",
            data=csv,
            file_name=f"用户注册表_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
except Exception as e:
    st.error(f"❌ 读取数据失败：{e}")

# ====== 页脚 ======
st.divider()
st.caption(f"© 2026 用户注册系统 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
