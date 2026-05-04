import streamlit as st
import requests

# Page configuration
st.set_page_config(
    page_title="Atul's Resume Q&A",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Enhanced CSS with Gradients and Colors
st.markdown("""
    <style>
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Main background */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Header styling */
    .header-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1.5rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .header-title h1 {
        margin: 0;
        font-size: 3rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Chat messages styling */
    .chat-message {
        padding: 1.5rem;
        border-radius: 1.2rem;
        margin-bottom: 1.2rem;
        display: flex;
        flex-direction: column;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        animation: slideIn 0.3s ease-in-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-left: 5px solid #4c51bf;
        margin-left: 2rem;
        border-radius: 1.2rem 1.2rem 0 1.2rem;
    }
    
    .user-message strong {
        color: #fff;
        font-size: 1.1rem;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-left: 5px solid #f5576c;
        margin-right: 2rem;
        border-radius: 1.2rem 1.2rem 1.2rem 0;
    }
    
    .assistant-message strong {
        color: #fff;
        font-size: 1.1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 0.8rem !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        background: white !important;
        border: 2px solid #667eea !important;
        border-radius: 0.8rem !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border: 2px solid #764ba2 !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Card styling for info boxes */
    .info-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    
    /* Section headers */
    .section-header {
        color: #667eea;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Success message */
    .success-badge {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        display: inline-block;
        font-weight: 600;
    }
    
    /* Error message */
    .error-badge {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        display: inline-block;
        font-weight: 600;
    }
    
    /* Question buttons container */
    .question-buttons {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 1rem;
        margin-top: 2rem;
        font-size: 0.9rem;
    }
    
    /* Spinner styling */
    .stSpinner {
        color: #667eea;
    }
    
    /* Markdown text */
    .markdown-text {
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 3px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 2rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# API endpoint
API_BASE_URL = "https://rag-chatbot-cr7n.onrender.com"

# Title with enhanced styling
st.markdown("""
    <div class="header-title">
        <h1>📄 Atul's Resume Q&A Chatbot</h1>
        <p style="font-size: 1.1rem; margin-top: 0.5rem; opacity: 0.95;">
            💡 Ask anything about skills, experience, projects & more!
        </p>
    </div>
""", unsafe_allow_html=True)

# Sidebar with enhanced styling
with st.sidebar:
    st.markdown("### 🎨 Chatbot Info")
    st.markdown("""
    <div class="info-card">
        <strong>✨ Features:</strong>
        <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
            <li>🛠️ Skills & expertise</li>
            <li>🏆 Certifications</li>
            <li>🎓 Education</li>
            <li>💼 Work experience</li>
            <li>📊 Projects & achievements</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚙️ API Status")
    api_status = st.empty()
    
    # Check API status
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=60)
        api_status.markdown("""
            <div class="success-badge">✅ API Connected</div>
        """, unsafe_allow_html=True)
    except:
        api_status.markdown("""
            <div class="error-badge">❌ API Not Connected</div>
        """, unsafe_allow_html=True)
        st.warning("⚠️ Make sure FastAPI is running on port 8000")
    
    st.divider()
    
    st.markdown("### 📚 Quick Links")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("[📖 API Docs](https://rag-chatbot-cr7n.onrender.com/docs)")
    with col2:
        st.markdown("[🚀 API Swagger](https://rag-chatbot-cr7n.onrender.com/redoc)")
    
    st.divider()
    
    st.markdown("### 💫 About")
    st.caption("Built with FastAPI + Streamlit powered by HuggingFace LLM")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history with enhanced styling
st.markdown('<p class="section-header">💬 Conversation History</p>', unsafe_allow_html=True)

if len(st.session_state.messages) == 0:
    st.info("👋 Start by asking a question using the buttons below or type your own!", icon="💭")
else:
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(
                    f"""
                    <div class="chat-message user-message">
                        <strong>👤 You:</strong><br>
                        <p style="margin: 0.5rem 0 0 0;">{message["content"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div class="chat-message assistant-message">
                        <strong>🤖 Assistant:</strong><br>
                        <p style="margin: 0.5rem 0 0 0;">{message["content"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# Input section with enhanced styling
st.markdown("---")
st.markdown('<p class="section-header">❓ Ask Atul a Question</p>', unsafe_allow_html=True)

# Predefined questions
st.markdown("### ⚡ Quick Questions")
st.markdown("*Click any button to get instant answers:*")
col1, col2 = st.columns(2)

quick_questions = [
    "What are Atul's main skills?",
    "What certifications does Atul have?",
    "What is Atul's educational background?",
    "Tell me about Atul's experience",
    "What projects has Atul worked on?",
    "What is Atul's expertise in Agentic AI?",
]

with col1:
    for i, question in enumerate(quick_questions[:3]):
        if st.button(f"✨ {question}", key=f"q_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": question})
            
            try:
                with st.spinner("🔄 Getting answer..."):
                    response = requests.post(
                        f"{API_BASE_URL}/chat",
                        json={"question": question},
                        timeout=30
                    )
                    if response.status_code == 200:
                        answer = response.json()["answer"]
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Connection Error: {str(e)}")

with col2:
    for i, question in enumerate(quick_questions[3:], start=3):
        if st.button(f"✨ {question}", key=f"q_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": question})
            
            try:
                with st.spinner("🔄 Getting answer..."):
                    response = requests.post(
                        f"{API_BASE_URL}/chat",
                        json={"question": question},
                        timeout=30
                    )
                    if response.status_code == 200:
                        answer = response.json()["answer"]
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Connection Error: {str(e)}")

# Custom question input with enhanced styling
st.markdown("---")
st.markdown("### 📝 Custom Question")
st.markdown("*Or ask your own question about Atul's profile:*")

col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.text_input(
        "Enter your question:",
        placeholder="💭 e.g., Tell me about Atul's experience?",
        label_visibility="collapsed"
    )

with col2:
    if st.button("🚀 Ask", use_container_width=True, key="ask_button"):
        if user_input.strip():
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            try:
                with st.spinner("🔄 Getting answer..."):
                    response = requests.post(
                        f"{API_BASE_URL}/chat",
                        json={"question": user_input},
                        timeout=30
                    )
                    if response.status_code == 200:
                        answer = response.json()["answer"]
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Connection Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a question first!")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    try:
        with st.spinner("🔄 Getting answer..."):
            response = requests.post(
                f"{API_BASE_URL}/chat",
                json={"question": user_input},
                timeout=30
            )
            if response.status_code == 200:
                answer = response.json()["answer"]
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
    except Exception as e:
        st.error(f"Failed to connect to API: {str(e)}")

# Action buttons
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.success("✅ Chat history cleared!")
        st.rerun()

with col2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

with col3:
    st.markdown("---")

# Footer with enhanced styling
st.markdown("""
    <div class="footer">
        <p style="margin: 0; font-size: 1rem; font-weight: 600;">
            💫 Powered by FastAPI & Streamlit
        </p>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
            🧠 Using HuggingFace LLM • 🔐 Secure & Private
        </p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; opacity: 0.8;">
            © 2026 Atul Resume Q&A
        </p>
    </div>
""", unsafe_allow_html=True)
