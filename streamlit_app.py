"""
Docintel AI Platform — Streamlit Frontend
==========================================
Lightweight Streamlit UI for RAG testing.
Pages: Dashboard, Upload, Q&A
Auth removed — uses default user_id=1 on backend.
"""

import streamlit as st
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="DocIntel AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #21262d;
    }
    .doc-card {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
        transition: border-color 0.2s;
    }
    .doc-card:hover { border-color: #8b5cf6; }
    .stat-card {
        background: linear-gradient(135deg, #1a1f2e, #161b22);
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    .stat-value { font-size: 2rem; font-weight: 700; color: #e6edf3; }
    .stat-label { font-size: 0.8rem; color: #8b949e; margin-top: 0.3rem; }
    .user-msg {
        background: linear-gradient(135deg, #7c3aed, #6d28d9);
        color: white;
        padding: 0.9rem 1.2rem;
        border-radius: 16px 16px 4px 16px;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
    }
    .bot-msg {
        background: #161b22;
        border: 1px solid #21262d;
        color: #e6edf3;
        padding: 0.9rem 1.2rem;
        border-radius: 16px 16px 16px 4px;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    .source-chunk {
        background: #1a1f2e;
        border: 1px solid #21262d;
        border-radius: 8px;
        padding: 0.6rem 0.8rem;
        margin: 0.3rem 0;
        font-size: 0.8rem;
        color: #8b949e;
    }
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    .stButton > button {
        border: 1px solid #7c3aed;
        color: white;
        border-radius: 8px;
    }
    .stButton > button:hover {
        border-color: #8b5cf6;
        background-color: #7c3aed20;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "selected_doc_id" not in st.session_state:
    st.session_state.selected_doc_id = None


# ---------------------------------------------------------------------------
# API helper (no auth needed)
# ---------------------------------------------------------------------------

def api_request(method, endpoint, **kwargs):
    """Make an API request to the backend."""
    url = f"{API_URL}{endpoint}"
    try:
        resp = requests.request(method, url, timeout=30, **kwargs)
        return resp
    except requests.ConnectionError:
        st.error("Cannot connect to backend. Is the API server running on port 8000?")
        return None
    except requests.Timeout:
        st.error("Request timed out.")
        return None


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def render_sidebar():
    with st.sidebar:
        st.markdown("### 🧠 DocIntel AI")
        st.divider()

        if st.button("📄 Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
        if st.button("⬆️ Upload", use_container_width=True):
            st.session_state.page = "upload"
            st.rerun()
        if st.button("💬 Ask AI", use_container_width=True):
            st.session_state.page = "qa"
            st.rerun()


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

def render_dashboard():
    st.markdown("## 📄 Dashboard")
    st.caption("Manage your uploaded documents")

    resp = api_request("GET", "/documents/")
    if not resp:
        return
    if resp.status_code != 200:
        st.error("Failed to load documents")
        return

    documents = resp.json()

    # Stats row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{len(documents)}</div>
            <div class="stat-label">Total Documents</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">AI Ready</div>
            <div class="stat-label">Gemini Powered</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">Q&A</div>
            <div class="stat-label">Ask Anything</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    if not documents:
        st.info("No documents yet. Upload your first document to get started!")
        if st.button("⬆️ Upload Your First Document"):
            st.session_state.page = "upload"
            st.rerun()
        return

    for doc in documents:
        col_info, col_actions = st.columns([4, 1])
        with col_info:
            created = doc.get("created_at", "")[:10] if doc.get("created_at") else ""
            st.markdown(f"""
            <div class="doc-card">
                <strong>{doc['filename']}</strong><br/>
                <span style="color: #8b949e; font-size: 0.8rem;">ID: {doc['id']} &nbsp; | &nbsp; {created}</span>
            </div>
            """, unsafe_allow_html=True)
        with col_actions:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("💬", key=f"ask_{doc['id']}", help="Ask questions"):
                    st.session_state.selected_doc_id = doc["id"]
                    st.session_state.page = "qa"
                    st.session_state.conversation = []
                    st.rerun()
            with c2:
                if st.button("🗑️", key=f"del_{doc['id']}", help="Delete"):
                    del_resp = api_request("DELETE", f"/documents/{doc['id']}")
                    if del_resp and del_resp.status_code == 200:
                        st.rerun()
                    else:
                        st.error("Failed to delete document")


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

def render_upload():
    st.markdown("## ⬆️ Upload Document")
    st.caption("Upload a PDF, DOCX, or TXT file to start asking questions")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "docx", "txt", "md", "html"],
        help="Supported: PDF, DOCX, TXT, MD, HTML"
    )

    col1, col2 = st.columns(2)
    with col1:
        chunk_size = st.selectbox(
            "Chunk size (tokens)",
            options=[100, 200, 300, 500],
            index=1,
            help="Smaller = more precise search. Larger = more context."
        )
    with col2:
        method = st.selectbox(
            "Chunking method",
            options=["auto", "structural", "semantic"],
            index=0,
            help="auto = format-aware, structural = sentence-based, semantic = similarity-based"
        )

    if uploaded_file:
        st.info(f"**{uploaded_file.name}** — {uploaded_file.size / 1024:.1f} KB")

        if st.button("📤 Upload & Process", use_container_width=True):
            with st.spinner("Extracting text, chunking, and generating embeddings..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "application/octet-stream")}
                resp = api_request(
                    "POST",
                    f"/documents/upload?chunk_size={chunk_size}&chunking_method={method}",
                    files=files
                )

                if resp and resp.status_code == 200:
                    data = resp.json()
                    st.success("Upload successful!")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Document ID", data["document_id"])
                    with c2:
                        st.metric("Chunks", data["chunks_stored"])
                    with c3:
                        st.metric("Format", data.get("format", "N/A"))

                    if st.button("💬 Ask Questions", use_container_width=True):
                        st.session_state.selected_doc_id = data["document_id"]
                        st.session_state.page = "qa"
                        st.session_state.conversation = []
                        st.rerun()
                elif resp:
                    detail = resp.json().get("detail", "Upload failed")
                    st.error(detail if isinstance(detail, str) else str(detail))


# ---------------------------------------------------------------------------
# Q&A
# ---------------------------------------------------------------------------

def render_qa():
    st.markdown("## 💬 Ask AI")
    st.caption("Ask questions about your documents")

    doc_id = st.number_input(
        "Document ID",
        min_value=1,
        value=st.session_state.selected_doc_id or 1,
        step=1,
        help="Enter the ID of the document to query"
    )
    st.session_state.selected_doc_id = doc_id

    chat_container = st.container()
    with chat_container:
        if not st.session_state.conversation:
            st.markdown(f"""
            <div style="text-align: center; padding: 3rem; color: #8b949e;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🧠</div>
                <h3 style="color: #e6edf3;">Ready to answer</h3>
                <p>Ask any question about Document #{doc_id}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.conversation:
                if msg["role"] == "user":
                    st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="bot-msg">{msg["content"]}</div>', unsafe_allow_html=True)
                    if msg.get("sources"):
                        with st.expander(f"📚 Sources ({len(msg['sources'])} chunks)"):
                            for i, src in enumerate(msg["sources"], 1):
                                st.markdown(f'<div class="source-chunk"><strong>Chunk {i}:</strong> {src[:300]}{"..." if len(src) > 300 else ""}</div>', unsafe_allow_html=True)

    st.divider()
    with st.form("qa_form", clear_on_submit=True):
        query = st.text_input("Ask a question", placeholder="What is this document about?", label_visibility="collapsed")
        submitted = st.form_submit_button("Send", use_container_width=True)

        if submitted and query.strip():
            st.session_state.conversation.append({"role": "user", "content": query.strip()})

            resp = api_request(
                "POST",
                f"/qa/?query={requests.utils.quote(query.strip())}&document_id={doc_id}"
            )

            if resp and resp.status_code == 200:
                data = resp.json()
                st.session_state.conversation.append({
                    "role": "assistant",
                    "content": data.get("answer", "No answer received"),
                    "sources": data.get("sources", [])
                })
            else:
                st.session_state.conversation.append({
                    "role": "assistant",
                    "content": "Sorry, I encountered an error. Please try again."
                })
            st.rerun()

    if st.session_state.conversation:
        if st.button("🗑️ Clear Conversation"):
            st.session_state.conversation = []
            st.rerun()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    render_sidebar()

    page = st.session_state.page
    if page == "dashboard":
        render_dashboard()
    elif page == "upload":
        render_upload()
    elif page == "qa":
        render_qa()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
