"""
Credibility Engine - Premium Frontend
Implements PRD 3.7 (Dashboard) and 3.4 (User Controls)
"""
import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
from fpdf import FPDF
import os
import json
from datetime import datetime
import time
import numpy as np
from streamlit_autorefresh import st_autorefresh
from deep_translator import GoogleTranslator

# Try-Except for Voice
try:
    from streamlit_mic_recorder import speech_to_text
    HAS_VOICE = True
except ImportError:
    HAS_VOICE = False

# --- CONFIGURATION ---
BACKEND_URL = os.getenv("BACKEND_URL", "https://aryan12345ark-credibility-backend.hf.space")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "") 
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")

st.set_page_config(page_title="Credibility Engine", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")
st_autorefresh(interval=60000, key="refresh")

# Initialize Session
if "history" not in st.session_state: st.session_state.history = []
if "profile" not in st.session_state: st.session_state.profile = "Strict Science"

# --- HELPER: TRANSLATION (PRD 3.1.2) ---
def translate_text(text, target_lang):
    if target_lang == "English" or not text: return text
    try:
        lang_map = {"Hindi": "hi", "Spanish": "es", "French": "fr", "German": "de"}
        code = lang_map.get(target_lang, "en")
        return GoogleTranslator(source='auto', target=code).translate(text)
    except: return text

# --- HELPER: PDF (PRD 3.6) ---
def generate_pdf(claim, data, sources):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, 'Credibility Engine Report', 0, 1, 'C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, f'Generated: {datetime.now()}', 0, 1, 'C')
    pdf.ln(10)
    
    score = data.get('score', 50)
    verdict = data.get('verdict', 'UNKNOWN')
    
    pdf.set_font("Arial", 'B', 12)
    pdf.multi_cell(0, 10, f"Claim: {claim}\nVerdict: {verdict} ({score}%)")
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 11)
    reasoning = data.get('reasoning', 'N/A').encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, f"Analysis: {reasoning}")
    pdf.ln(5)
    
    if sources:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Sources:", 0, 1)
        pdf.set_font("Arial", '', 10)
        for s in sources:
            name = s.get('name', 'Unknown')
            pdf.cell(0, 6, f"- {name}", 0, 1)
            
    return pdf.output(dest='S').encode('latin-1')

# --- CSS STYLING (PRD 3.7 - Premium UI) ---
st.markdown("""
<style>
    .main-header { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 3rem; border-radius: 1.5rem; color: white; text-align: center; margin-bottom: 2rem; }
    .score-card { background: white; border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); text-align: center; border-top: 6px solid #e2e8f0; }
    .border-green { border-top-color: #22c55e !important; }
    .border-yellow { border-top-color: #eab308 !important; }
    .border-red { border-top-color: #ef4444 !important; }
    .verdict-banner { padding: 2rem; border-radius: 1rem; color: white; text-align: center; margin-bottom: 2rem; }
    .source-badge { display: inline-block; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin: 0.2rem; background: #eff6ff; color: #1e3a8a; }
    .pilot-badge { position: fixed; top: 1rem; right: 1rem; background: linear-gradient(45deg, #f59e0b, #d97706); color: white; padding: 0.4rem 1rem; border-radius: 2rem; font-weight: 700; font-size: 0.8rem; z-index: 1000; }
    .footer { text-align: center; margin-top: 4rem; padding: 2rem; color: #94a3b8; border-top: 1px solid #e2e8f0; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} .stDeployButton {display:none;}
</style>
<div class="pilot-badge">⚡ LIVE PILOT v1.0</div>
""", unsafe_allow_html=True)

# --- SIDEBAR (PRD 3.4) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9566/9566127.png", width=60)
    st.title("Control Center")
    
    # PRD 3.4.1: Evidence Profiles
    st.markdown("### 👤 Evidence Profile")
    st.session_state.profile = st.selectbox(
        "Select Strictness:",
        ["Strict Science", "Institutional + Investigative", "Broad", "Custom"]
    )
    
    st.markdown("---")
    
    # PRD 3.1.1: Live Ingest
    st.markdown("### 📰 Ingestion")
    news_topic = st.selectbox("Live Feed Topic", ["General", "Health", "Science", "Politics"])
    if st.button("🔄 Stream Live News"):
        if GNEWS_API_KEY:
            with st.spinner(f"Streaming {news_topic} news to Pathway..."):
                try:
                    url = f"https://gnews.io/api/v4/top-headlines?category={news_topic.lower()}&lang=en&apikey={GNEWS_API_KEY}"
                    data = requests.get(url).json()
                    count = 0
                    for article in data.get('articles', [])[:5]:
                        requests.post(f"{BACKEND_URL}/ingest", json={
                            "text": f"{article['title']}\n{article['description']}",
                            "source": article['source']['name']
                        })
                        count += 1
                    st.toast(f"✅ Indexed {count} articles!", icon="🌊")
                except: st.error("Stream Failed")
    
    st.markdown("---")
    
    # Language
    st.markdown("### 🌐 Settings")
    lang = st.selectbox("Output Language", ["English", "Hindi", "Spanish", "French"])
    
    st.markdown("---")
    # Backend Status
    try:
        res = requests.get(f"{BACKEND_URL}/", timeout=2)
        status = "🟢 Online" if res.status_code==200 else "🔴 Error"
    except: status = "🔴 Offline"
    st.caption(f"Backend: {status}")

# --- MAIN CONTENT ---
st.markdown("""
<div class="main-header">
    <h1 style="font-size: 3.5rem; font-weight: 800; margin: 0;">🛡️ Credibility Engine</h1>
    <p style="font-size: 1.2rem; opacity: 0.8; margin-top: 10px;">Real-Time Misinformation Detection System</p>
</div>
""", unsafe_allow_html=True)

tab_verify, tab_dash, tab_map, tab_kb = st.tabs(["🔎 Verify Claim", "📊 Dashboard", "🗺️ Global Map", "📚 Knowledge"])

# --- TAB 1: VERIFY (PRD 3.6, 3.3) ---
with tab_verify:
    col_input, col_action = st.columns([3, 1])
    with col_input:
        claim_input = st.text_area("Enter statement:", height=100, placeholder="e.g. Drinking bleach cures COVID-19...")
    
    with col_action:
        st.write("")
        st.write("")
        analyze_btn = st.button("✨ Verify", type="primary", use_container_width=True)
        # PRD 3.4 Voice
        if HAS_VOICE:
            voice = speech_to_text(language='en', use_container_width=True, just_once=True, key='STT')
            if voice: st.info(f"Heard: {voice}")

    if analyze_btn and claim_input:
        with st.spinner("🔄 Interfacing with Pathway Vector Store & Groq LLM..."):
            try:
                # API Call
                payload = {"claim": claim_input, "profile": st.session_state.profile}
                response = requests.post(f"{BACKEND_URL}/analyze", json=payload, timeout=60)
                data = response.json()
                
                # Metrics
                score = data.get('score', 50)
                verdict = data.get('verdict', 'UNKNOWN')
                confidence = data.get('confidence_score', 0)
                
                # Colors
                if score >= 80: theme = "#22c55e"
                elif score >= 50: theme = "#eab308"
                else: theme = "#ef4444"
                
                # PRD 3.6.3: Side-by-Side View (Verdict Banner)
                st.markdown(f"""
                <div class="verdict-banner" style="background-color: {theme};">
                    <h2 style="margin:0; font-size:1.5rem;">VERDICT: {verdict.upper()}</h2>
                    <h1 style="margin:0; font-size:4rem; font-weight:800;">{score}%</h1>
                    <p style="margin:0; opacity:0.9;">Credibility Score</p>
                </div>
                """, unsafe_allow_html=True)
                
                # PRD 3.3.4: Confidence & Indicators
                m1, m2, m3, m4 = st.columns(4)
                def card(label, val, col): return f"<div class='score-card {col}'><div style='font-size:1.8rem; font-weight:700; color:#1e293b;'>{val}</div><div style='font-size:0.85rem; color:#64748b;'>{label}</div></div>"
                m1.markdown(card("Confidence", f"{confidence}%", "border-green"), unsafe_allow_html=True)
                m2.markdown(card("Category", data.get('category'), "border-yellow"), unsafe_allow_html=True)
                m3.markdown(card("Profile", st.session_state.profile, "border-orange"), unsafe_allow_html=True)
                m4.markdown(card("Evidence", len(data.get('sources', [])), "border-red"), unsafe_allow_html=True)
                
                st.markdown("---")
                
                # PRD 3.3.5: Breakdown
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.subheader("📝 Reasoning")
                    reasoning = data.get('reasoning')
                    if lang != "English": reasoning = translate_text(reasoning, lang)
                    st.write(reasoning)
                    
                    st.markdown("#### 💡 Key Evidence")
                    for p in data.get('key_evidence', []):
                        if lang != "English": p = translate_text(p, lang)
                        st.success(f"• {p}")
                        
                with c2:
                    st.subheader("📚 Sources")
                    for s in data.get('sources', []):
                        name = s.get('name', 'Unknown')
                        rating = s.get('rating', 'Medium')
                        st.markdown(f"**{name}**\n<span class='source-badge'>{rating}</span>", unsafe_allow_html=True)

                # PRD 3.6: Correction Delivery
                st.markdown("---")
                st.subheader("📤 Export & Share")
                xc1, xc2, xc3 = st.columns(3)
                pdf_bytes = generate_pdf(claim_input, data, data.get('sources', []))
                xc1.download_button("📄 Download PDF", pdf_bytes, "report.pdf", "application/pdf", use_container_width=True)
                xc2.link_button("🐦 Twitter", f"https://twitter.com/intent/tweet?text=Fact-check: {claim_input[:30]}... {score}%", use_container_width=True)
                xc3.link_button("💬 WhatsApp", f"https://wa.me/?text=Fact-check: {claim_input[:30]}... {score}%", use_container_width=True)
                
                st.session_state.history.append({"claim": claim_input, "score": score, "time": datetime.now()})

            except Exception as e:
                st.error(f"Analysis Error: {e}")

# --- TAB 2: DASHBOARD (PRD 3.7) ---
with tab_dash:
    st.subheader("📈 Analytics Dashboard")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.line_chart(df['score'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No data yet.")

# --- TAB 3: MAP (PRD 3.1.4) ---
with tab_map:
    st.subheader("🌍 Misinformation Heatmap")
    data = pd.DataFrame({
        'lat': [20.59 + np.random.uniform(-5, 5) for _ in range(50)],
        'lon': [78.96 + np.random.uniform(-5, 5) for _ in range(50)]
    })
    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(latitude=20.59, longitude=78.96, zoom=3),
        layers=[pdk.Layer('HexagonLayer', data=data, get_position='[lon, lat]', radius=20000, elevation_scale=4, extruded=True)]
    ))

# Footer
st.markdown("<div class='footer'>© 2025 Aryan & Khushboo • Powered by Pathway + Groq + Hugging Face</div>", unsafe_allow_html=True)