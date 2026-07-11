import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ====== 页面配置 ======
st.set_page_config(
    page_title="Streamlit 演示",
    page_icon="🔥",
    layout="centered",
)

# ====== 侧边栏 ======
with st.sidebar:
    st.header("⚙️ 设置面板")
    theme_color = st.selectbox("主题色", ["蓝色", "绿色", "橙色", "红色"])
    show_chart = st.checkbox("显示图表", value=True)
    sample_size = st.slider("数据量", 10, 100, 30)
    st.divider()
    st.caption(f"当前时间：{datetime.now().strftime('%H:%M:%S')}")

# ====== 主标题 ======
st.title("🔥 Streamlit 快速上手")
st.caption("一个纯 Python 的 Web 应用框架，无需 HTML/CSS/JS。")

# ====== 基础输入 ======
st.subheader("📝 文本输入")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("你的名字？", placeholder="请输入...")
with col2:
    mood = st.selectbox("今天心情如何？", ["😊 很好", "😐 一般", "😢 不太好"])

if name:
    st.success(f"你好，**{name}**！祝你今天有个好心情～")

# ====== 数据表格 ======
st.subheader("📊 随机数据表")

np.random.seed(42)
df = pd.DataFrame({
    "编号": range(1, sample_size + 1),
    "分数": np.random.randint(50, 100, sample_size),
    "通过": np.random.choice(["✅ 是", "❌ 否"], sample_size, p=[0.7, 0.3]),
})
st.dataframe(df, width="stretch", hide_index=True)

# ====== 图表 ======
if show_chart:
    st.subheader("📈 分数分布")
    chart_df = pd.DataFrame(
        np.random.randn(20, 3),
        columns=["语文", "数学", "英语"],
    )
    st.line_chart(chart_df)

# ====== 指标卡片 ======
st.subheader("📌 统计概览")
m1, m2, m3 = st.columns(3)
m1.metric("平均分", f"{df['分数'].mean():.1f}", f"{df['分数'].mean() - 70:.1f}")
m2.metric("最高分", f"{df['分数'].max()}", "")
m3.metric("通过率", f"{(df['通过'] == '✅ 是').mean():.0%}", "")

# ====== 聊天组件 ======
st.subheader("💬 聊天消息（AI 应用常用）")
with st.chat_message("assistant"):
    st.write("你好！我是 Streamlit 助手，有什么可以帮你的吗？")
with st.chat_message("user"):
    st.write("用 Streamlit 写网页太方便了！")

prompt = st.chat_input("输入消息试试...")
if prompt:
    st.chat_message("user").write(prompt)
    st.chat_message("assistant").write("这是一个演示回复，你可以接入大模型 API 来实现真正的 AI 对话。")

# ====== 页脚 ======
st.divider()
st.caption(f"© 2026 Streamlit Demo | 运行于 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
