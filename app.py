import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置页面标题
st.set_page_config(page_title="Trae Chatbot", page_icon="🤖")
st.title("🤖 Trae Chatbot (Python Edition)")

# 设置 OpenAI API Key
# 优先从环境变量获取，如果没有则在侧边栏输入
api_key = os.getenv("OPENAI_API_KEY")

with st.sidebar:
    st.markdown("## 配置")
    if not api_key:
        api_key = st.text_input("请输入 OpenAI API Key", type="password")
        if not api_key:
            st.warning("请输入 API Key 以开始对话")
    else:
        st.success("API Key 已配置")
    
    st.markdown("---")
    st.markdown("这个 App 是使用 Python + Streamlit 构建的。")

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示聊天历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 聊天输入框
if prompt := st.chat_input("说点什么..."):
    # 检查是否有 API Key
    if not api_key:
        st.error("请先在侧边栏设置 OpenAI API Key")
        st.stop()

    # 1. 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 调用 API 并显示回复
    client = OpenAI(api_key=api_key)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # 使用流式传输
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"发生错误: {e}")
            full_response = "抱歉，我遇到了一些问题。"

    # 3. 保存助手回复到历史
    st.session_state.messages.append({"role": "assistant", "content": full_response})
