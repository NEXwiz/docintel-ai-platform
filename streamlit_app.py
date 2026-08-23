"""
Docintel AI Platform — Streamlit Frontend
==========================================
Pages: Dashboard, Upload, Query Docs
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
# CSS — minimal, dark, fast
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0a0e17; }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1520, #0a0e17);
        border-right: 1px solid #1a1f2e;
    }
    .hero {
        background: linear-gradient(135deg, #1a1035 0%, #0f1520 50%, #0a1628 100%);
        border: 1px solid #1a1f2e; border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem;
    }
    .hero h2 { color: #e6edf3; margin: 0; font-size: 1.6rem; }
    .hero p { color: #7d8590; margin: 0.5rem 0 0; }
    .doc-card {
        background: #12162180; border: 1px solid #1a1f2e; border-radius: 14px;
        padding: 1rem 1.2rem; margin-bottom: 0.5rem;
    }
    .doc-card:hover { border-color: #7c3aed; }
    .doc-name { font-weight: 600; color: #e6edf3; font-size: 0.95rem; }
    .doc-meta { color: #484f58; font-size: 0.75rem; margin-top: 0.15rem; }
    .doc-badge {
        background: #7c3aed20; color: #a78bfa; padding: 0.2rem 0.6rem;
        border-radius: 20px; font-size: 0.7rem; font-weight: 500; float: right;
    }
    .stat-card {
        background: #12162180; border: 1px solid #1a1f2e; border-radius: 14px;
        padding: 1.3rem; text-align: center;
    }
    .stat-value {
        font-size: 2rem; font-weight: 700;
        background: linear-gradient(135deg, #7c3aed, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .stat-label { font-size: 0.75rem; color: #484f58; margin-top: 0.3rem; }
    .user-msg {
        background: linear-gradient(135deg, #7c3aed, #6d28d9); color: white;
        padding: 0.8rem 1.1rem; border-radius: 14px 14px 4px 14px;
        margin: 0.4rem 0; max-width: 75%; margin-left: auto; font-size: 0.9rem;
    }
    .bot-msg {
        background: #121621; border: 1px solid #1a1f2e; color: #c9d1d9;
        padding: 0.8rem 1.1rem; border-radius: 14px 14px 14px 4px;
        margin: 0.4rem 0; max-width: 75%; font-size: 0.9rem; line-height: 1.5;
    }
    .source-chunk {
        background: #0f1520; border: 1px solid #1a1f2e; border-radius: 8px;
        padding: 0.5rem 0.7rem; margin: 0.3rem 0; font-size: 0.75rem;
        color: #7d8590; line-height: 1.4;
    }
    .upload-result {
        background: linear-gradient(135deg, #06291e, #0a0e17);
        border: 1px solid #1a4d2e; border-radius: 14px; padding: 1.5rem; margin: 1rem 0;
    }
    .upload-result h3 { color: #3fb950; margin: 0 0 0.8rem; }
    .upload-stat { color: #7d8590; font-size: 0.85rem; margin: 0.3rem 0; }
    .upload-stat strong { color: #e6edf3; }
    .empty-state { text-align: center; padding: 3rem 2rem; color: #484f58; }
    .empty-state .icon { font-size: 3rem; margin-bottom: 0.8rem; opacity: 0.5; }
    .empty-state h3 { color: #7d8590; font-weight: 500; }
    .empty-state p { color: #484f58; font-size: 0.85rem; }
    #MainMenu, header, footer { visibility: hidden; }
    .stButton > button {
        border: 1px solid #1a1f2e; color: #e6edf3; border-radius: 10px;
        font-weight: 500; transition: all 0.15s;
    }
    .stButton > button:hover { border-color: #7c3aed; background-color: #7c3aed15; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

for key, default in {
    "page": "dashboard",
    "conversation": [],
    "selected_doc_id": None,
    "upload_result": None,
    "docs_cache": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ---------------------------------------------------------------------------
# API + caching
# ---------------------------------------------------------------------------

def api_request(method, endpoint, **kwargs):
    url = f"{API_URL}{endpoint}"
    try:
        return requests.request(method, url, timeout=60, **kwargs)
    except requests.ConnectionError:
        st.error("Cannot connect to backend. Is the API running on port 8000?")
        return None
    except requests.Timeout:
        st.error("Request timed out.")
        return None


def fetch_documents(force_refresh=False):
    """Fetch docs with simple caching to avoid repeated API calls per rerun."""
    if not force_refresh and st.session_state.docs_cache is not None:
        return st.session_state.docs_cache
    resp = api_request("GET", "/documents/")
    if resp and resp.status_code == 200:
        st.session_state.docs_cache = resp.json()
        return st.session_state.docs_cache
    return []


def navigate(page, **kwargs):
    """Navigate without full rerun flash — just set state."""
    st.session_state.page = page
    for k, v in kwargs.items():
        st.session_state[k] = v


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding: 0.5rem 0 1rem;">
            <span style="font-size: 1.4rem;">🧠</span>
            <span style="font-size: 1.1rem; font-weight: 700; color: #e6edf3; margin-left: 0.4rem;">DocIntel</span>
            <span style="font-size: 0.7rem; color: #484f58; margin-left: 0.3rem;">AI</span>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        pages = [
            ("dashboard", "📄", "Documents"),
            ("upload", "⬆️", "Upload"),
            ("qa", "🔍", "Query Docs"),
        ]
        for key, icon, label in pages:
            marker = "▸ " if st.session_state.page == key else "  "
            if st.button(f"{marker}{icon} {label}", key=f"nav_{key}", use_container_width=True):
                navigate(key)
                st.rerun()


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

def render_dashboard():
    documents = fetch_documents(force_refresh=True)

    st.markdown(f"""
    <div class="hero">
        <h2>📄 Your Documents</h2>
        <p>{len(documents)} document{'s' if len(documents) != 1 else ''} indexed and ready to query</p>
    </div>
    """, unsafe_allow_html=True)

    if not documents:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">📂</div>
            <h3>No documents yet</h3>
            <p>Upload your first PDF, DOCX, or TXT file to get started</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⬆️ Upload Your First Document", use_container_width=True):
            navigate("upload")
            st.rerun()
        return

    for doc in documents:
        created = doc.get("created_at", "")[:10] if doc.get("created_at") else ""
        filename = doc["filename"]
        ext = filename.rsplit(".", 1)[-1].upper() if "." in filename else "FILE"

        col1, col2, col3 = st.columns([6, 1, 1])
        with col1:
            st.markdown(f"""
            <div class="doc-card">
                <span class="doc-badge">{ext}</span>
                <div class="doc-name">{filename}</div>
                <div class="doc-meta">Uploaded {created}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("🔍", key=f"q_{doc['id']}", help="Query"):
                navigate("qa", selected_doc_id=doc["id"], conversation=[])
                st.rerun()
        with col3:
            if st.button("🗑️", key=f"d_{doc['id']}", help="Delete"):
                api_request("DELETE", f"/documents/{doc['id']}")
                st.session_state.docs_cache = None
                st.rerun()


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

def render_upload():
    st.markdown("""
    <div class="hero">
        <h2>⬆️ Upload Document</h2>
        <p>Upload a file to index it for semantic search and Q&A</p>
    </div>
    """, unsafe_allow_html=True)

    # Show result from previous upload
    if st.session_state.upload_result:
        data = st.session_state.upload_result
        st.markdown(f"""
        <div class="upload-result">
            <h3>✅ Upload Complete</h3>
            <div class="upload-stat">Document ID: <strong>{data['document_id']}</strong></div>
            <div class="upload-stat">Chunks stored: <strong>{data['chunks_stored']}</strong></div>
            <div class="upload-stat">Chunk size: <strong>{data.get('chunk_size', 'auto')}</strong> tokens</div>
            <div class="upload-stat">Method: <strong>{data.get('method', 'auto')}</strong></div>
            <div class="upload-stat">Format: <strong>{data.get('format', 'N/A')}</strong></div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔍 Query This Document", use_container_width=True):
                navigate("qa", selected_doc_id=data["document_id"], conversation=[], upload_result=None, docs_cache=None)
                st.rerun()
        with c2:
            if st.button("⬆️ Upload Another", use_container_width=True):
                st.session_state.upload_result = None
                st.rerun()
        return

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "docx", "txt", "md", "html"],
        help="Supported: PDF, DOCX, TXT, Markdown, HTML"
    )

    col1, col2 = st.columns(2)
    with col1:
        chunk_options = {"Auto (recommended)": 0, "100 tokens": 100, "200 tokens": 200, "300 tokens": 300, "500 tokens": 500}
        chunk_label = st.selectbox(
            "Chunk size",
            options=list(chunk_options.keys()),
            index=0,
            help="Auto adjusts chunk size based on document length. Smaller = precise search, Larger = more context."
        )
        chunk_size = chunk_options[chunk_label]
    with col2:
        method = st.selectbox(
            "Chunking method",
            options=["auto", "structural", "semantic"],
            index=0,
            help="auto = format-aware, structural = sentence-based, semantic = similarity-based"
        )

    if uploaded_file:
        st.markdown(f"""
        <div style="background: #121621; border: 1px solid #1a1f2e; border-radius: 10px; padding: 0.8rem 1rem; margin: 0.5rem 0;">
            <span style="color: #a78bfa;">📎</span>
            <span style="color: #e6edf3; font-weight: 500;">{uploaded_file.name}</span>
            <span style="color: #484f58; font-size: 0.8rem; margin-left: 0.5rem;">{uploaded_file.size / 1024:.1f} KB</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📤 Upload & Process", use_container_width=True, type="primary"):
            with st.spinner("Extracting text, chunking, and generating embeddings..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "application/octet-stream")}
                resp = api_request(
                    "POST",
                    f"/documents/upload?chunk_size={chunk_size}&chunking_method={method}",
                    files=files
                )

                if resp and resp.status_code == 200:
                    result = resp.json()
                    result["chunk_size"] = chunk_size if chunk_size > 0 else "auto"
                    st.session_state.upload_result = result
                    st.session_state.docs_cache = None  # invalidate cache
                    st.rerun()
                elif resp:
                    detail = resp.json().get("detail", "Upload failed")
                    st.error(f"❌ {detail}" if isinstance(detail, str) else str(detail))


# ---------------------------------------------------------------------------
# Query Docs
# ---------------------------------------------------------------------------

def render_qa():
    st.markdown("""
    <div class="hero">
        <h2>🔍 Query Your Documents</h2>
        <p>Search and ask questions about your uploaded documents</p>
    </div>
    """, unsafe_allow_html=True)

    documents = fetch_documents()

    if not documents:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">📂</div>
            <h3>No documents to query</h3>
            <p>Upload a document first, then come back here</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⬆️ Go to Upload", use_container_width=True):
            navigate("upload")
            st.rerun()
        return

    # Document dropdown
    doc_map = {f"{d['filename']}": d["id"] for d in documents}
    doc_names = list(doc_map.keys())

    default_idx = 0
    if st.session_state.selected_doc_id:
        for i, name in enumerate(doc_names):
            if doc_map[name] == st.session_state.selected_doc_id:
                default_idx = i
                break

    selected = st.selectbox("Select document", doc_names, index=default_idx)
    doc_id = doc_map[selected]
    st.session_state.selected_doc_id = doc_id

    # Chat
    if not st.session_state.conversation:
        st.markdown(f"""
        <div class="empty-state" style="padding: 2rem;">
            <div class="icon">🔍</div>
            <h3>Ask about "{selected}"</h3>
            <p>Type a question below to search this document</p>
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
                            preview = src[:400] + ("..." if len(src) > 400 else "")
                            st.markdown(f'<div class="source-chunk"><strong>Chunk {i}:</strong> {preview}</div>', unsafe_allow_html=True)

    st.divider()
    with st.form("qa_form", clear_on_submit=True):
        query = st.text_input("Question", placeholder="e.g. What are the key findings?", label_visibility="collapsed")
        submitted = st.form_submit_button("🔍 Search & Answer", use_container_width=True)

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
                err = "Unknown error"
                if resp:
                    try:
                        err = resp.json().get("detail", resp.text)
                    except Exception:
                        err = resp.text
                st.session_state.conversation.append({
                    "role": "assistant",
                    "content": f"⚠️ {err}"
                })
            st.rerun()

    if st.session_state.conversation:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.conversation = []
            st.rerun()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

render_sidebar()
page = st.session_state.page
if page == "upload":
    render_upload()
elif page == "qa":
    render_qa()
else:
    render_dashboard()
