"""
Docintel AI Platform — Streamlit Frontend
==========================================
Minimal chat-first UI. Sidebar = file list. Main pane = chat.
"""

import streamlit as st
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="DocIntel AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Minimal Dark Theme CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* App background */
    .stApp {
        background: #0f1117;
        color: #e4e4e7;
    }

    /* Hide Streamlit chrome */
    #MainMenu, header, footer,
    [data-testid="stHeaderActionElements"],
    [data-testid="stHeader"],
    a.anchor-link,
    h1 a, h2 a, h3 a, h4 a { display: none !important; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #18181b !important;
        border-right: 1px solid #27272a !important;
    }

    section[data-testid="stSidebar"] .stMarkdown p {
        color: #a1a1aa;
        font-size: 0.82rem;
    }

    /* Sidebar file buttons */
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        text-align: left;
        background: transparent;
        border: none;
        border-radius: 6px;
        color: #d4d4d8;
        padding: 0.5rem 0.75rem;
        font-size: 0.85rem;
        font-weight: 400;
        cursor: pointer;
        transition: background 0.15s;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #27272a;
    }

    /* Active file highlight */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #27272a;
        color: #fafafa;
        font-weight: 500;
    }

    /* Chat message containers */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
        padding: 0.75rem 0;
    }

    /* Chat input */
    [data-testid="stChatInput"] textarea {
        background: #18181b !important;
        border: 1px solid #27272a !important;
        color: #e4e4e7 !important;
        border-radius: 8px;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 1px dashed #3f3f46;
        border-radius: 8px;
        padding: 0.5rem;
    }

    [data-testid="stFileUploader"] label {
        color: #a1a1aa !important;
        font-size: 0.82rem !important;
    }

    /* Divider */
    hr { border-color: #27272a !important; opacity: 0.5; }

    /* Spinner */
    .stSpinner > div { border-top-color: #a1a1aa !important; }

    /* Project title */
    .project-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #fafafa;
        padding: 0.25rem 0 0.5rem 0;
        letter-spacing: -0.02em;
    }

    /* Delete button (inline with filename) */
    .delete-btn button {
        background: transparent !important;
        color: #52525b !important;
        border: none !important;
        font-size: 0.72rem !important;
        padding: 0.1rem 0 !important;
        min-height: 0 !important;
        line-height: 1 !important;
    }
    .delete-btn button:hover {
        color: #ef4444 !important;
    }

    /* Status text */
    .status-text {
        color: #52525b;
        font-size: 0.75rem;
        padding: 0.25rem 0;
    }

    /* Empty state */
    .empty-state {
        color: #52525b;
        text-align: center;
        padding: 4rem 2rem;
        font-size: 0.9rem;
        line-height: 1.8;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------

if "documents" not in st.session_state:
    st.session_state.documents = []
if "active_doc_id" not in st.session_state:
    st.session_state.active_doc_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "docs_loaded" not in st.session_state:
    st.session_state.docs_loaded = False


# ---------------------------------------------------------------------------
# API Helpers
# ---------------------------------------------------------------------------

def fetch_documents():
    """Fetch document list from backend."""
    try:
        resp = requests.get(f"{API_URL}/documents/", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []


def upload_document(file):
    """Upload a file to the backend."""
    resp = requests.post(
        f"{API_URL}/documents/upload",
        files={"file": (file.name, file.getvalue(), file.type)},
        params={"use_parent_child": True},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def delete_document(doc_id):
    """Delete a document from the backend."""
    resp = requests.delete(f"{API_URL}/documents/{doc_id}", timeout=10)
    resp.raise_for_status()


def fetch_chat_history(doc_id):
    """Fetch chat history for a document."""
    try:
        resp = requests.get(f"{API_URL}/chat/{doc_id}", timeout=10)
        resp.raise_for_status()
        return [{"role": m["role"], "content": m["content"]} for m in resp.json()]
    except Exception:
        return []


def save_chat_message(doc_id, role, content):
    """Persist a chat message to the backend."""
    try:
        requests.post(
            f"{API_URL}/chat/{doc_id}",
            json={"role": role, "content": content},
            timeout=10,
        )
    except Exception:
        pass


def ask_question(query, doc_id):
    """Send a question to the QA endpoint."""
    resp = requests.post(
        f"{API_URL}/qa/",
        params={"query": query, "document_id": doc_id},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Load Documents (once per session, then on mutations)
# ---------------------------------------------------------------------------

def refresh_documents():
    st.session_state.documents = fetch_documents()
    st.session_state.docs_loaded = True


if not st.session_state.docs_loaded:
    refresh_documents()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown('<div class="project-title">DocIntel AI</div>', unsafe_allow_html=True)
    st.markdown("---")

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["pdf", "txt", "docx"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        # Prevent duplicate uploads on rerun
        upload_key = f"uploaded_{uploaded_file.name}_{uploaded_file.size}"
        if upload_key not in st.session_state:
            with st.spinner("Processing..."):
                try:
                    result = upload_document(uploaded_file)
                    st.session_state[upload_key] = True
                    refresh_documents()
                    # Auto-select the newly uploaded document
                    st.session_state.active_doc_id = result["document_id"]
                    st.session_state.chat_history = []
                    st.rerun()
                except Exception as e:
                    st.error(f"Upload failed: {e}")

    st.markdown("---")

    # Document list
    docs = st.session_state.documents

    if not docs:
        st.markdown('<p class="status-text">No documents yet</p>', unsafe_allow_html=True)
    else:
        for doc in docs:
            doc_id = doc["id"]
            filename = doc["filename"]
            is_active = doc_id == st.session_state.active_doc_id

            col1, col2 = st.columns([6, 1])

            with col1:
                btn_type = "primary" if is_active else "secondary"
                if st.button(
                    filename,
                    key=f"doc_{doc_id}",
                    type=btn_type,
                    use_container_width=True,
                ):
                    if st.session_state.active_doc_id != doc_id:
                        st.session_state.active_doc_id = doc_id
                        st.session_state.chat_history = fetch_chat_history(doc_id)
                        st.rerun()

            with col2:
                if st.button("🗑", key=f"del_{doc_id}"):
                    try:
                        delete_document(doc_id)
                        if st.session_state.active_doc_id == doc_id:
                            st.session_state.active_doc_id = None
                            st.session_state.chat_history = []
                        refresh_documents()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete failed: {e}")


# ---------------------------------------------------------------------------
# Main Pane — Chat Interface
# ---------------------------------------------------------------------------

active_id = st.session_state.active_doc_id

if active_id is None:
    # Empty state
    st.markdown(
        '<div class="empty-state">'
        "Upload a document or select one from the sidebar to start chatting."
        "</div>",
        unsafe_allow_html=True,
    )
else:
    # Find active document name
    active_name = None
    for d in st.session_state.documents:
        if d["id"] == active_id:
            active_name = d["filename"]
            break

    if active_name:
        st.markdown(f"**{active_name}**")
    else:
        st.markdown(f"**Document {active_id}**")

    # Render chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about this document"):
        # Phase 1: Show user message immediately
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        save_chat_message(active_id, "user", prompt)

        with st.chat_message("user"):
            st.markdown(prompt)

        # Phase 2: Show spinner, then answer
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = ask_question(prompt, active_id)
                    answer = result.get("answer", "No answer returned.")
                except Exception as e:
                    answer = f"Error: {e}"

            st.markdown(answer)

        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        save_chat_message(active_id, "assistant", answer)
