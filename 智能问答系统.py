import os
import sys
from openai import OpenAI
import streamlit as st

# Windows 控制台默认 GBK 编码，设成 UTF-8 避免 emoji 等字符崩掉
sys.stdout.reconfigure(encoding='utf-8')

# ====== 页面配置 ======
st.set_page_config(
    page_title="智能问答系统",
    page_icon="💬",
    layout="centered",
)

# ====== 侧边栏设置 ======
with st.sidebar:
    st.header("🔑 API 设置")
    api_key = os.environ.get("DEEPSEEK_API_KEY") or st.text_input(
        "DeepSeek API Key",
        type="password",
        placeholder="sk-...",
        help="优先使用环境变量 DEEPSEEK_API_KEY，未设置时可在此填入",
    )
    if not api_key:
        st.warning("⚠️ 请设置 DEEPSEEK_API_KEY 环境变量或在下方填入 API Key")
        st.stop()

    # ====== 初始化客户端 ======
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    st.divider()
    st.header("⚙️ 模型设置")
    model = st.selectbox(
        "模型",
        ["deepseek-chat", "deepseek-reasoner"],
        help="deepseek-chat: 通用对话 | deepseek-reasoner: 深度推理（会展示思考过程）",
    )
    enable_thinking = st.checkbox(
        "显示思考过程",
        value=True,
        help="仅 deepseek-reasoner 模型会输出思考过程",
    )
    system_prompt = st.text_area(
        "系统提示词",
        value="You are a helpful assistant",
        height=80,
    )
    st.divider()
    if st.button("🧹 清空对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ====== 会话状态：保存对话历史 ======
if "messages" not in st.session_state:
    st.session_state.messages = []

# ====== 标题 ======
st.title("💬 智能问答系统")
st.caption("基于 DeepSeek API 的多轮对话 · 支持流式输出")

# ====== 回放历史消息 ======
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("reasoning"):
            with st.expander("🧠 思考过程"):
                st.markdown(msg["reasoning"])
        st.markdown(msg["content"])

# ====== 聊天输入 ======
prompt = st.chat_input("请输入你的问题...")

if prompt:
    # 显示并保存用户消息
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 组装发送给 API 的消息（含 system + 历史）
    api_messages = [{"role": "system", "content": system_prompt}]
    api_messages += [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
    ]

    # 调用 DeepSeek API（流式）
    response = client.chat.completions.create(
        model=model,
        messages=api_messages,
        stream=True,
    )

    # 流式渲染回复
    with st.chat_message("assistant"):
        reasoning_text = ""
        answer_text = ""
        reasoning_box = st.empty()  # 思考过程容器
        answer_box = st.empty()     # 正文容器

        for chunk in response:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta

            # 思考过程
            if enable_thinking and getattr(delta, "reasoning_content", None):
                reasoning_text += delta.reasoning_content
                with reasoning_box.expander("🧠 思考过程", expanded=True):
                    st.markdown(reasoning_text)

            # 正文回答
            if delta.content:
                answer_text += delta.content
                answer_box.markdown(answer_text)

    # 收起思考过程
    if reasoning_text:
        with reasoning_box.expander("🧠 思考过程"):
            st.markdown(reasoning_text)

    # 保存助手回复到历史
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer_text,
        "reasoning": reasoning_text if enable_thinking else "",
    })
