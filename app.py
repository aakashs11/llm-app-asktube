import streamlit as st
from streamlit_chat import message
from asktube import process_video, run, get_video_details
import time

# Callback to handle sending messages
def send_message():
    if st.session_state.query_input:
        st.session_state.messages.append({"role": "user", "content": st.session_state.query_input})
        st.session_state.processing = True
        st.session_state.query_input = ""  # This will clear the input box

st.set_page_config(page_title="AskTube", page_icon="🎥", layout="wide")

# Custom CSS to improve font, styling, and responsiveness
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        background: url('https://www.toptal.com/designers/subtlepatterns/patterns/memphis-mini.png');
    }
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .stButton > button {
        font-size: 16px;
    }
    .chat-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        max-height: 400px;
        overflow-y: auto;
    }
    .input-container {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 10px;
    }
    .input-container .stTextInput {
        flex-grow: 1;
    }
    @media (max-width: 640px) {
        .input-container {
            flex-direction: column;
        }
        .input-container .stTextInput {
            width: 100%;
        }
    }
    .message-container {
        display: flex;
        align-items: flex-start;
        margin-bottom: 10px;
    }
    .message-content {
        margin-left: 10px;
    }
    .stApp {
        overflow: visible;
    }
    .fixed-header {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        background-color: white;
        z-index: 1000;
        padding-top: 10px;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "bot", "content": "Hi there! I'm ready to answer questions about your YouTube video. Just process a video and ask away!"}
    ]
if "video_processed" not in st.session_state:
    st.session_state.video_processed = False
if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = None
if "video_details" not in st.session_state:
    st.session_state.video_details = None
if "processing" not in st.session_state:
    st.session_state.processing = False

st.markdown('<div class="fixed-header">', unsafe_allow_html=True)
st.title("AskTube: Your YouTube Video Assistant 🎥🤖")
st.markdown('</div>', unsafe_allow_html=True)
if not st.session_state.video_processed:
    video_url = st.text_input("YouTube Video URL", placeholder="Paste your YouTube video URL here", label_visibility="collapsed")
    if st.button("Process Video", type="primary"):
        if video_url:
            with st.spinner("Processing video... This may take a moment."):
                chat_engine, error = process_video(video_url)
                video_details = get_video_details(video_url)
            if error:
                st.error(error)
            elif "error" in video_details:
                st.error(f"Error fetching video details: {video_details['error']}")
            else:
                st.session_state.chat_engine = chat_engine
                st.session_state.video_processed = True
                st.session_state.video_details = video_details
                st.session_state.messages.append({"role": "bot", "content": f"Great! I've processed the video '{video_details['title']}'. What would you like to know about it?"})
                st.success("Video processed successfully!")
                st.rerun()
        else:
            st.warning("Please enter a video URL.")
else:
    # Display video details
    if st.session_state.video_details:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(st.session_state.video_details["thumbnail_url"], use_column_width=True)
        with col2:
            st.subheader(st.session_state.video_details["title"])
    
    st.markdown("---")

    # Display chat messages
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for i, msg in enumerate(st.session_state.messages):
        message(
            msg["content"],
            is_user=msg["role"] == "user",
            key=f"msg_{i}"
        )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.text_input("Chat Input", placeholder="Type your question here", key="query_input", on_change=send_message, label_visibility="collapsed")
    st.button("Send", type="primary", on_click=send_message)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process the message and show typing indicator
    if st.session_state.processing:
        with st.spinner("Thinking..."):
            response = run(st.session_state.chat_engine, st.session_state.messages[-1]["content"])
            time.sleep(0.5)  # Add a small delay to make the typing indicator visible
        st.session_state.messages.append({"role": "bot", "content": response})
        st.session_state.processing = False
        st.rerun()

st.markdown("---")
st.markdown("Made with ☕ by Aakash")

# Restart button
if st.button("Start Over with New Video", type="secondary"):
    st.session_state.video_processed = False
    st.session_state.chat_engine = None
    st.session_state.messages = [
        {"role": "bot", "content": "Hi there! I'm ready to answer questions about your YouTube video. Just process a video and ask away!"}
    ]
    st.session_state.video_details = None
    st.session_state.processing = False
    st.rerun()