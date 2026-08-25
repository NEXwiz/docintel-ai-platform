"""
Docintel AI Platform — Streamlit Frontend
==========================================
Ultra-fast, modern UI for RAG document intelligence.
"""

import streamlit as st
import requests
import time

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="DocIntel AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# High Performance & Premium UI CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    * { 
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important; 
    }

    /* Background & App Container */
    .stApp { 
        background: radial-gradient(circle at 50% 0%, #17192b 0%, #0c0e17 60%, #07090e 100%);
        color: #f0f3f8;
    }

    /* Hide Streamlit default headers, footers & anchor links */
    #MainMenu, header, footer, [data-testid="stHeaderActionElements"], a.anchor-link, [data-testid="stHeader"] { 
        display: none !important; 
        visibility: hidden !important; 
    }
    
    /* Disable anchor link icons on headers */
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
        display: none !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0d111a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4);
    }

    /* Prevent typing / text cursor inside selectbox inputs */
    div[data-baseweb="select"] input {
        cursor: pointer !important;
        user-select: none !important;
    }
    
    /* Custom Modern Glassmorphic Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.12) 0%, rgba(30, 41, 59, 0.4) 50%, rgba(15, 23, 42, 0.6) 100%);
        border: 1px solid rgba(139, 92, 246, 0.25);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.6rem 2rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    .hero-title {
        font-size: 1.65rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.02em;
        margin: 0;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 0.35rem;
        font-weight: 400;
    }

    /* Document Card Component */
    .doc-row {
        background: rgba(18, 24, 38, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.65rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .doc-row:hover {
        border-color: rgba(139, 92, 246, 0.5);
        background: rgba(28, 33, 52, 0.85);
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
    }
    .doc-title {
        font-weight: 600;
        color: #f1f5f9;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .doc-subtitle {
        color: #64748b;
        font-size: 0.78rem;
        margin-top: 0.25rem;
        font-weight: 500;
    }
    .format-pill {
        display: inline-block;
        background: rgba(139, 92, 246, 0.15);
        color: #c4b5fd;
        border: 1px solid rgba(139, 92, 246, 0.3);
        padding: 0.18rem 0.55rem;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    /* Stats Counter Card */
    .stat-box {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.25rem 1rem;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }
    .stat-number {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(135deg, #a78bfa 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.1;
    }
    .stat-label-text {
        font-size: 0.78rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.4rem;
    }

    /* Chat Messages */
    .chat-user-bubble {
        background: linear-gradient(135deg, #7c3aed 0%, #6366f1 100%);
        color: #ffffff;
        padding: 0.85rem 1.2rem;
        border-radius: 16px 16px 4px 16px;
        margin: 0.5rem 0 0.5rem auto;
        max-width: 80%;
        font-size: 0.92rem;
        font-weight: 500;
        box-shadow: 0 4px 14px rgba(124, 58, 237, 0.25);
    }
    .chat-bot-bubble {
        background: rgba(18, 24, 38, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #e2e8f0;
        padding: 0.95rem 1.25rem;
        border-radius: 16px 16px 16px 4px;
        margin: 0.5rem auto 0.5rem 0;
        max-width: 85%;
        font-size: 0.92rem;
        line-height: 1.6;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    .source-box {
        background: rgba(11, 15, 25, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 0.6rem 0.8rem;
        margin-top: 0.4rem;
        font-size: 0.8rem;
        color: #94a3b8;
        line-height: 1.45;
    }

    /* Upload Box */
    .success-alert-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(6, 78, 59, 0.3) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 14px;
        padding: 1.4rem;
        margin: 1.2rem 0;
    }
    .success-title {
        color: #34d399;
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
    }

    /* Empty state */
    .empty-container {
        text-align: center;
        padding: 3.5rem 1.5rem;
        color: #64748b;
    }
    .empty-icon {
        font-size: 2.8rem;
        margin-bottom: 0.75rem;
        opacity: 0.7;
    }

    /* Button Styling */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        transition: all 0.2s ease !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    .stButton > button:hover {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 12px rgba(139, 92, 246, 0.25) !important;
    }

    /* Streamlit Form Input Overrides */
    div[data-testid="stTextInput"] input {
        border-radius: 10px !important;
        background-color: rgba(18, 24, 38, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: #ffffff !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 1px #8b5cf6 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------

for key, default in {
    "page": "dashboard",
    "conversation": [],
    "selected_doc_id": None,
    "upload_result": None,
    "docs_cache": None,
    "last_fetch_time": 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ---------------------------------------------------------------------------
# API & Instant Cached Data Layer
# ---------------------------------------------------------------------------

def api_request(method, endpoint, **kwargs):
    url = f"{API_URL}{endpoint}"
    try:
        return requests.request(method, url, timeout=60, **kwargs)
    except requests.ConnectionError:
        st.error("Cannot connect to backend. Make sure the API server is running on port 8000.")
        return None
    except requests.Timeout:
        st.error("Request timed out.")
        return None


def fetch_documents(force_refresh=False):
    """
    Cached fetcher: provides instantaneous page loads.
    Re-fetches only if cache is empty, explicitly invalidated, or expired (>30s).
    """
    now = time.time()
    if (
        not force_refresh 
        and st.session_state.docs_cache is not None 
        and (now - st.session_state.last_fetch_time < 30)
    ):
        return st.session_state.docs_cache

    resp = api_request("GET", "/documents/")
    if resp and resp.status_code == 200:
        st.session_state.docs_cache = resp.json()
        st.session_state.last_fetch_time = now
        return st.session_state.docs_cache
    return st.session_state.docs_cache or []


def navigate(page, **kwargs):
    """Instant navigation helper."""
    st.session_state.page = page
    for k, v in kwargs.items():
        st.session_state[k] = v


# ---------------------------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------------------------

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding: 0.6rem 0.2rem 1rem;">
            <div style="display: flex; align-items: center; gap: 0.6rem;">
                <div style="background: linear-gradient(135deg, #7c3aed, #4f46e5); width: 36px; height: 36px; border-radius: 9px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.1rem; color: white; box-shadow: 0 4px 12px rgba(124, 58, 237, 0.4);">⚡</div>
                <div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #ffffff; letter-spacing: -0.01em;">DocIntel</div>
                    <div style="font-size: 0.72rem; color: #818cf8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em;">AI Platform</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        pages = [
            ("dashboard", "📂", "Documents"),
            ("upload", "📤", "Upload"),
            ("qa", "💬", "Query Docs"),
        ]
        
        for key, icon, label in pages:
            is_active = st.session_state.page == key
            btn_label = f"{'▶ ' if is_active else '   '}{icon}  {label}"
            if st.button(
                btn_label,
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                if st.session_state.page != key:
                    navigate(key)
                    st.rerun()


# ---------------------------------------------------------------------------
# Dashboard (Documents Page)
# ---------------------------------------------------------------------------

def render_dashboard():
    # Instant load from cache
    documents = fetch_documents(force_refresh=False)

    col_title, col_refresh = st.columns([5, 1])
    with col_title:
        st.markdown(f"""
        <div class="hero-banner">
            <div class="hero-title">Your Documents</div>
            <div class="hero-subtitle">{len(documents)} document{'s' if len(documents) != 1 else ''} indexed and ready for semantic intelligence</div>
        </div>
        """, unsafe_allow_html=True)
    with col_refresh:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh", use_container_width=True, help="Reload document index from database"):
            fetch_documents(force_refresh=True)
            st.rerun()

    if not documents:
        st.markdown("""
        <div class="empty-container">
            <div class="empty-icon">🗂️</div>
            <h3 style="color: #cbd5e1; font-weight: 600; margin-bottom: 0.4rem;">No documents found</h3>
            <p style="color: #64748b; font-size: 0.88rem; max-width: 380px; margin: 0 auto 1.5rem;">Upload your first document (PDF, DOCX, TXT, MD, HTML) to index and query.</p>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("📤 Upload Your First Document", use_container_width=True, type="primary"):
                navigate("upload")
                st.rerun()
        return

    # Document list items
    for doc in documents:
        created = doc.get("created_at", "")[:10] if doc.get("created_at") else "Recent"
        filename = doc["filename"]
        ext = filename.rsplit(".", 1)[-1].upper() if "." in filename else "FILE"

        col_info, col_query, col_del = st.columns([6, 1.2, 1])
        with col_info:
            st.markdown(f"""
            <div class="doc-row">
                <div>
                    <div class="doc-title">
                        <span>📄</span>
                        <span>{filename}</span>
                    </div>
                    <div class="doc-subtitle">ID #{doc['id']} &nbsp;•&nbsp; Uploaded {created}</div>
                </div>
                <span class="format-pill">{ext}</span>
            </div>
            """, unsafe_allow_html=True)
        with col_query:
            if st.button("💬 Query", key=f"q_{doc['id']}", use_container_width=True, help="Open query chat for this document"):
                navigate("qa", selected_doc_id=doc["id"], conversation=[])
                st.rerun()
        with col_del:
            if st.button("🗑️", key=f"d_{doc['id']}", use_container_width=True, help="Delete document from database and vector index"):
                api_request("DELETE", f"/documents/{doc['id']}")
                st.session_state.docs_cache = None
                fetch_documents(force_refresh=True)
                st.rerun()


# ---------------------------------------------------------------------------
# Upload Page
# ---------------------------------------------------------------------------

def render_upload():
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">Upload & Ingest Document</div>
        <div class="hero-subtitle">Parse, format-chunk, embed, and index files into Qdrant vector store</div>
    </div>
    """, unsafe_allow_html=True)

    # Show result from last upload
    if st.session_state.upload_result:
        data = st.session_state.upload_result
        st.markdown(f"""
        <div class="success-alert-card">
            <div class="success-title">✓ Ingestion & Indexing Successful</div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.8rem; margin-top: 0.8rem;">
                <div><span style="color: #64748b; font-size: 0.78rem;">Document ID:</span><br/><strong style="color: #f1f5f9;">#{data['document_id']}</strong></div>
                <div><span style="color: #64748b; font-size: 0.78rem;">Chunks Indexed:</span><br/><strong style="color: #f1f5f9;">{data['chunks_stored']} chunks</strong></div>
                <div><span style="color: #64748b; font-size: 0.78rem;">Chunk Size:</span><br/><strong style="color: #f1f5f9;">{data.get('chunk_size', 'auto')} tokens</strong></div>
                <div><span style="color: #64748b; font-size: 0.78rem;">Method:</span><br/><strong style="color: #f1f5f9;">{data.get('method', 'auto')}</strong></div>
                <div><span style="color: #64748b; font-size: 0.78rem;">Format Detected:</span><br/><strong style="color: #f1f5f9;">{data.get('format', 'N/A').upper()}</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("💬 Start Asking Questions", use_container_width=True, type="primary"):
                navigate("qa", selected_doc_id=data["document_id"], conversation=[], upload_result=None)
                st.rerun()
        with c2:
            if st.button("📤 Upload Another Document", use_container_width=True):
                st.session_state.upload_result = None
                st.rerun()
        return

    uploaded_file = st.file_uploader(
        "Select Document",
        type=["pdf", "docx", "txt", "md", "html"],
        help="Supported formats: PDF, Word (DOCX), Plain Text, Markdown, HTML"
    )

    col1, col2 = st.columns(2)
    with col1:
        chunk_options = {
            "⚡ Auto-Detect (Dynamic based on size)": 0,
            "100 tokens (High precision / Short answers)": 100,
            "200 tokens (Standard balance)": 200,
            "300 tokens (Rich context)": 300,
            "500 tokens (Large overview)": 500,
        }
        chunk_label = st.selectbox(
            "Chunking Granularity",
            options=list(chunk_options.keys()),
            index=0,
            help="Dynamic automatically selects optimal chunk size based on file length"
        )
        chunk_size = chunk_options[chunk_label]
        
    with col2:
        method_options = {
            "⚡ Auto (Format-Aware PDF/HTML/MD)": "auto",
            "🧩 Structural (Sentence & Section-Aware)": "structural",
            "🧠 Semantic (Embedding Similarity Split)": "semantic",
        }
        method_label = st.selectbox(
            "Chunking Strategy",
            options=list(method_options.keys()),
            index=0,
            help="Auto uses specialized parsers for PDF layouts, HTML tags, and Markdown hierarchies"
        )
        method = method_options[method_label]

    if uploaded_file:
        file_size_kb = uploaded_file.size / 1024
        st.markdown(f"""
        <div style="background: rgba(18, 24, 38, 0.8); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 10px; padding: 0.85rem 1.1rem; margin: 0.6rem 0; display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 0.6rem;">
                <span style="font-size: 1.2rem;">📎</span>
                <div>
                    <div style="color: #f1f5f9; font-weight: 600; font-size: 0.92rem;">{uploaded_file.name}</div>
                    <div style="color: #64748b; font-size: 0.75rem;">{file_size_kb:.1f} KB</div>
                </div>
            </div>
            <span class="format-pill">{uploaded_file.name.rsplit('.', 1)[-1].upper()}</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Upload & Process Document", use_container_width=True, type="primary"):
            with st.spinner("Extracting text, chunking, generating 3072-dim embeddings, and upserting vectors..."):
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type or "application/octet-stream"
                    )
                }
                resp = api_request(
                    "POST",
                    f"/documents/upload?chunk_size={chunk_size}&chunking_method={method}",
                    files=files
                )

                if resp and resp.status_code == 200:
                    result = resp.json()
                    result["chunk_size"] = chunk_size if chunk_size > 0 else "auto"
                    st.session_state.upload_result = result
                    st.session_state.docs_cache = None  # refresh cache
                    fetch_documents(force_refresh=True)
                    st.rerun()
                elif resp:
                    detail = resp.json().get("detail", "Upload failed")
                    st.error(f"❌ Ingestion Error: {detail}")


# ---------------------------------------------------------------------------
# Query Docs (Q&A Page)
# ---------------------------------------------------------------------------

def render_qa():
    documents = fetch_documents(force_refresh=False)

    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">Query Your Documents</div>
        <div class="hero-subtitle">Ask questions and retrieve semantic grounded answers with citations</div>
    </div>
    """, unsafe_allow_html=True)

    if not documents:
        st.markdown("""
        <div class="empty-container">
            <div class="empty-icon">📂</div>
            <h3 style="color: #cbd5e1; font-weight: 600;">No documents to query</h3>
            <p style="color: #64748b; font-size: 0.88rem;">Upload a document first to start querying.</p>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("📤 Go to Upload", use_container_width=True, type="primary"):
                navigate("upload")
                st.rerun()
        return

    # Document selection dropdown
    doc_map = {f"📄 {d['filename']} (ID: {d['id']})": d["id"] for d in documents}
    doc_names = list(doc_map.keys())

    default_idx = 0
    if st.session_state.selected_doc_id:
        for i, name in enumerate(doc_names):
            if doc_map[name] == st.session_state.selected_doc_id:
                default_idx = i
                break

    selected_label = st.selectbox(
        "Active Target Document",
        options=doc_names,
        index=default_idx,
        help="Select which indexed document to query against"
    )
    doc_id = doc_map[selected_label]
    
    # If selected document changed, update state
    if st.session_state.selected_doc_id != doc_id:
        st.session_state.selected_doc_id = doc_id
        st.session_state.conversation = []

    # Chat history display
    chat_box = st.container()
    with chat_box:
        if not st.session_state.conversation:
            clean_name = selected_label.split(" (ID:")[0]
            st.markdown(f"""
            <div class="empty-container" style="padding: 2.5rem 1rem;">
                <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">💬</div>
                <h4 style="color: #f1f5f9; font-weight: 600; margin: 0 0 0.3rem;">Ready to answer from {clean_name}</h4>
                <p style="color: #64748b; font-size: 0.85rem; margin: 0;">Type any question below to retrieve relevant chunks and generate accurate responses.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.conversation:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-bot-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
                    if msg.get("sources"):
                        with st.expander(f"📚 Grounded Citations ({len(msg['sources'])} retrieved chunks)"):
                            for i, src in enumerate(msg["sources"], 1):
                                preview = src[:450] + ("..." if len(src) > 450 else "")
                                st.markdown(f'<div class="source-box"><strong>[Chunk {i}]</strong><br/>{preview}</div>', unsafe_allow_html=True)

    # Chat Input Box
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    with st.form("qa_form", clear_on_submit=True):
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            query = st.text_input(
                "Question",
                placeholder="Ask anything about the document content...",
                label_visibility="collapsed"
            )
        with col_btn:
            submitted = st.form_submit_button("🔍 Search", use_container_width=True, type="primary")

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
                    "content": data.get("answer", "No answer could be synthesized."),
                    "sources": data.get("sources", [])
                })
            else:
                err = "Failed to query document."
                if resp:
                    try:
                        err = resp.json().get("detail", resp.text)
                    except Exception:
                        err = resp.text
                st.session_state.conversation.append({
                    "role": "assistant",
                    "content": f"⚠️ Error: {err}"
                })
            st.rerun()

    if st.session_state.conversation:
        c1, c2, c3 = st.columns([4, 1, 1])
        with c3:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.conversation = []
                st.rerun()


# ---------------------------------------------------------------------------
# Main Router
# ---------------------------------------------------------------------------

render_sidebar()
page = st.session_state.page
if page == "upload":
    render_upload()
elif page == "qa":
    render_qa()
else:
    render_dashboard()
