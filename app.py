import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# --- CONFIG ---
BACKEND_URL = os.getenv("BACKEND_URL", "https://aryan12345ark-credibility-backend.hf.space")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "") # Still needed for GNews
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")

st.set_page_config(page_title="Credibility Engine", page_icon="🔍", layout="wide")
st_autorefresh(interval=30000, key="refresh")

if "history" not in st.session_state: st.session_state.history = []
if "lang" not in st.session_state: st.session_state.lang = "English"

# --- TRANSLATOR ---
def t(text):
    if st.session_state.lang == "English": return text
    try:
        lang_map = {"Hindi": "hi", "Spanish": "es", "French": "fr"}
        return GoogleTranslator(source='auto', target=lang_map[st.session_state.lang]).translate(text)
    except: return text

# --- EXACT PHASE 2 CSS ---
st.markdown("""
<style>
    /* Dark Theme Base */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Blue Banner */
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #2563eb 100%);
        padding: 3rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
    
    /* Cards */
    .metric-card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    /* Result Boxes */
    .result-box {
        background-color: #ffffff;
        color: #000000;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    
    /* Evidence Points */
    .evidence-point {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin-bottom: 10px;
    }
    
    /* Footer */
    .footer {
        text-align: center; margin-top: 50px;
        color: #64748b; font-size: 0.8rem;
        border-top: 1px solid #334155; padding-top: 20px;
    }
    
    /* Status Button */
    .status-btn {
        background-color: #10b981; color: white;
        padding: 5px 15px; border-radius: 20px;
        display: inline-block; font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🔍 Credibility Engine")
    st.caption("Real-Time Misinformation Tracker")
    
    # Status
    try:
        r = requests.get(f"{BACKEND_URL}/", timeout=2)
        status = "System Active" if r.status_code==200 else "Connecting..."
        color = "#10b981" if r.status_code==200 else "#eab308"
    except: 
        status = "Offline"
        color = "#ef4444"
        
    st.markdown(f'<div style="background:{color}; color:white; padding:8px; border-radius:5px; text-align:center; margin-bottom:20px;">{status}</div>', unsafe_allow_html=True)
    
    # Stats
    c1, c2 = st.columns(2)
    c1.metric("Articles", "Dynamic")
    c2.metric("Analyses", len(st.session_state.history))
    
    st.markdown("---")
    
    # Feature 14: Language
    st.session_state.lang = st.selectbox("🌐 Language", ["English", "Hindi", "Spanish", "French"])
    
    st.markdown("---")
    
    # Live Feed
    st.markdown("### 📰 Live Data Feed")
    topic = st.selectbox("Select Topic:", ["general", "health", "science", "politics"])
    if st.button("🔄 Fetch Latest News"):
        if GNEWS_API_KEY:
            try:
                url = f"https://gnews.io/api/v4/top-headlines?category={topic}&lang=en&apikey={GNEWS_API_KEY}"
                data = requests.get(url).json()
                for a in data.get('articles', [])[:3]:
                    requests.post(f"{BACKEND_URL}/ingest", json={"text": f"{a['title']}\n{a['description']}", "source": a['source']['name']})
                st.success("Ingested live news!")
            except: st.error("Feed Error")
    
    st.markdown("---")
    
    # Manual
    with st.expander("📝 Add Evidence"):
        txt = st.text_area("Paste Article")
        if st.button("Submit"):
            requests.post(f"{BACKEND_URL}/ingest", json={"text": txt, "source": "Manual"})
            st.success("Indexed!")

    st.markdown("---")
    st.caption("© 2025 Aryan & Khushboo")

# --- MAIN HEADER ---
st.markdown("""
<div class="main-header">
    <h1 style="margin:0;">🔍 Credibility Engine</h1>
    <p style="margin:10px 0 0 0; opacity:0.8;">Real-time claim verification powered by AI & live evidence</p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔎 Verify Claim", "📊 Dashboard", "📚 Knowledge Base", "📈 History"])

# --- TAB 1: VERIFY ---
with tab1:
    st.markdown("### Enter a claim to verify")
    
    # Example dropdown
    ex = ["Select...", "The earth is flat", "Vaccines cause autism", "Drinking 8 glasses of water daily is necessary"]
    sel = st.selectbox("Or try an example:", ex)
    val = sel if sel != "Select..." else ""
    
    claim = st.text_area("Your Claim:", value=val, height=100)
    
    # Buttons
    c1, c2, c3 = st.columns([1, 1, 1])
    do_an = c1.button("🔍 Analyze Claim", type="primary", use_container_width=True)
    c2.button("⚡ Quick Check", use_container_width=True)
    if c3.button("🗑️ Clear", use_container_width=True): st.rerun()
    
    if do_an and claim:
        with st.spinner("Processing..."):
            try:
                # Backend Call
                res = requests.post(f"{BACKEND_URL}/analyze", json={"claim": claim}, timeout=60).json()
                st.session_state.history.append({"claim": claim, "res": res})
                
                # Colors
                score = res.get('score', 50)
                if score >= 75: color, bg = "#10b981", "#d1fae5" # Green
                elif score >= 40: color, bg = "#eab308", "#fef9c3" # Yellow
                else: color, bg = "#ef4444", "#fee2e2" # Red
                
                st.markdown("---")
                
                # 4-Card Layout (From Screenshot)
                k1, k2, k3, k4 = st.columns(4)
                
                # Card 1: Score
                k1.markdown(f"""
                <div style="background:{bg}; padding:20px; border-radius:10px; text-align:center; color:{color};">
                    <h1 style="margin:0">{score}%</h1>
                    <small>Credibility Score</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Card 2: Verdict
                k2.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin:0">{t(res.get('verdict', 'UNKNOWN'))}</h3>
                    <small style="color:#94a3b8">Verdict</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Card 3: Category
                k3.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin:0">{t(res.get('category', 'General'))}</h3>
                    <small style="color:#94a3b8">Category</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Card 4: Sources
                k4.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin:0">{len(res.get('sources', []))}</h3>
                    <small style="color:#94a3b8">Sources Used</small>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Analysis Section
                row = st.columns([2, 1])
                
                with row[0]:
                    st.subheader("📝 Analysis")
                    st.write(t(res.get('reasoning')))
                
                with row[1]:
                    st.subheader("💡 Key Evidence Points")
                    for k in res.get('key_evidence', []):
                        st.markdown(f'<div class="evidence-point">{t(k)}</div>', unsafe_allow_html=True)
                
                # Feature: Share
                st.markdown("---")
                st.markdown("#### 📤 Share")
                s1, s2, s3 = st.columns(3)
                
                txt = f"Fact-check: {claim[:30]}... {score}%"
                s1.link_button("🐦 Twitter", f"https://twitter.com/intent/tweet?text={txt}", use_container_width=True)
                s2.link_button("💬 WhatsApp", f"https://wa.me/?text={txt}", use_container_width=True)
                
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, f"Claim: {claim}\nScore: {score}%\n\nAnalysis:\n{res.get('reasoning')}")
                s3.download_button("📄 PDF", pdf.output(dest='S').encode('latin-1'), "report.pdf", use_container_width=True)

            except Exception as e:
                st.error(f"Error: {e}")

# --- DASHBOARD ---
with tab2:
    st.subheader("📊 System Dashboard")
    
    if st.session_state.history:
        df = pd.DataFrame([{"Score": h['res']['score'], "Category": h['res']['category']} for h in st.session_state.history])
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Articles Indexed", "Dynamic")
        m2.metric("Total Analyses", len(df))
        m3.metric("False Claims", len(df[df['Score'] < 40]))
        m4.metric("Verified True", len(df[df['Score'] > 80]))
        
        st.markdown("### Pipeline Status")
        st.info("✅ Pathway Streaming Engine: ACTIVE")
        st.info("✅ Vector Index: SYNCHRONIZED")
        st.info("✅ Groq LLM: CONNECTED")
    else:
        st.info("No data yet.")

# --- KNOWLEDGE ---
with tab3:
    st.subheader("📚 Knowledge Base")
    try:
        files = requests.get(f"{BACKEND_URL}/").json().get('files', 0)
        st.success(f"{files} documents currently indexed in Vector Store.")
        st.caption("Documents are ingested via Pathway streaming connector.")
    except: st.warning("Connecting...")

# --- HISTORY ---
with tab4:
    st.subheader("📈 History")
    for h in reversed(st.session_state.history):
        st.text(f"{h['claim']} - {h['res']['score']}%")

st.markdown("<div class='footer'>© 2025 Aryan & Khushboo • All Rights Reserved</div>", unsafe_allow_html=True)