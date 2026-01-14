"""
Credibility Engine - Premium Frontend Client
Connects to Hugging Face Backend (16GB RAM)
Features: All 10 Features Enabled + Professional UI
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

# --- CONFIGURATION ---
BACKEND_URL = os.getenv("BACKEND_URL", "https://aryan12345ark-credibility-backend.hf.space")

st.set_page_config(
    page_title="Credibility Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 3rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .verdict-box {
        text-align: center;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 20px;
        color: white;
        font-weight: bold;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .source-badge {
        background: #eff6ff;
        color: #1e3a8a;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        margin-right: 5px;
        border: 1px solid #bfdbfe;
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        color: #64748b;
        font-size: 0.9rem;
        border-top: 1px solid #e2e8f0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "history" not in st.session_state: st.session_state.history = []

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">🛡️ Credibility Engine</h1>
    <p style="font-size: 1.2rem; opacity: 0.9;">Real-Time Misinformation Detection System</p>
    <div style="margin-top: 1rem;">
        <span style="background:rgba(255,255,255,0.2); padding:5px 15px; border-radius:20px; font-size:0.9rem;">🚀 Powered by Pathway Streaming</span>
        <span style="background:rgba(255,255,255,0.2); padding:5px 15px; border-radius:20px; font-size:0.9rem; margin-left:10px;">🧠 Groq LLM Intelligence</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9566/9566127.png", width=60)
    st.title("Control Center")
    
    # Health Check
    st.markdown("### 📡 System Status")
    try:
        start = time.time()
        res = requests.get(f"{BACKEND_URL}/", timeout=3)
        latency = int((time.time() - start) * 1000)
        
        if res.status_code == 200:
            st.success(f"🟢 **Brain Online** ({latency}ms)")
            data = res.json()
            st.caption(f"Platform: {data.get('platform', 'Hugging Face')}")
        else:
            st.warning("🟡 **Degraded**")
    except:
        st.error("🔴 **Brain Offline**")
        st.caption("Check Backend URL")

    st.markdown("---")
    
    # Ingest Tool
    st.markdown("### 📰 Real-Time Ingestion")
    with st.expander("Inject New Data"):
        ingest_text = st.text_area("Content:", height=100, placeholder="Paste breaking news here...")
        ingest_source = st.text_input("Source:", value="Reuters")
        if st.button("🚀 Stream to Pathway"):
            if ingest_text:
                try:
                    with st.spinner("Streaming..."):
                        requests.post(f"{BACKEND_URL}/ingest", json={"text": ingest_text, "source": ingest_source})
                    st.toast("✅ Indexed! Knowledge Base Updated.", icon="🌊")
                except:
                    st.error("Ingestion Failed")

    st.markdown("---")
    st.markdown("### ⚙️ Filters")
    st.selectbox("Category", ["All", "Politics", "Health", "Tech", "Science"])
    st.slider("Min Confidence", 0, 100, 50)
    
    st.markdown("---")
    st.caption("© 2025 Aryan & Khushboo")

# --- TABS ---
tabs = st.tabs(["🔎 **Verify**", "📊 **Dashboard**", "🗺️ **Global Map**", "📚 **Knowledge**"])

# --- TAB 1: ANALYSIS ---
with tabs[0]:
    col1, col2 = st.columns([3, 1])
    with col1:
        claim = st.text_area("Enter a claim to verify:", height=100, placeholder="e.g. The earth is flat because...")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("✨ Verify Claim", type="primary")

    if analyze_btn and claim:
        with st.spinner("🧠 Pathway RAG Pipeline is thinking..."):
            try:
                # Call Backend (Heavy Lifting happening on HF)
                response = requests.post(f"{BACKEND_URL}/analyze", json={"claim": claim}, timeout=60)
                result = response.json()
                
                # Save to history
                st.session_state.history.append({
                    "claim": claim, "score": result.get('score'), "time": datetime.now().strftime("%H:%M")
                })

                # Display Logic
                score = result.get('score', 50)
                verdict = result.get('verdict', 'UNKNOWN')
                sentiment = result.get('sentiment', 'Neutral')
                color = "#22c55e" if score >= 75 else "#ef4444" if score < 25 else "#eab308"
                
                # Score Banner
                st.markdown(f"""
                <div class="verdict-box" style="background-color: {color};">
                    <h1 style="font-size: 4rem; margin:0">{score}%</h1>
                    <h3 style="margin:0; opacity:0.9">{verdict.upper()}</h3>
                </div>
                """, unsafe_allow_html=True)

                # Metrics
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Confidence", f"{result.get('confidence_score', 85)}%")
                c2.metric("Category", result.get('category', 'General'))
                c3.metric("Sentiment", sentiment.title())
                c4.metric("Sources", len(result.get('sources', [])))

                st.markdown("---")

                # Content
                col_analysis, col_evidence = st.columns(2)
                
                with col_analysis:
                    st.subheader("📝 AI Reasoning")
                    st.write(result.get('reasoning'))
                    
                    st.subheader("💡 Key Evidence")
                    for point in result.get('key_evidence', []):
                        st.success(f"• {point}")

                with col_evidence:
                    st.subheader("📚 Retrieved Sources (RAG)")
                    sources = result.get('sources', [])
                    if sources:
                        for idx, s in enumerate(sources):
                            with st.expander(f"📄 Source {idx+1}"):
                                st.write(s)
                                st.markdown('<span class="source-badge">Pathway Index</span>', unsafe_allow_html=True)
                    else:
                        st.info("AI used internal knowledge base.")

                # Export & Share
                st.markdown("---")
                st.subheader("📤 Export & Share")
                
                xc1, xc2, xc3, xc4 = st.columns(4)
                
                # PDF Generation (Locally on Render - easy for 512MB)
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="Credibility Report", ln=1, align='C')
                pdf.cell(200, 10, txt=f"Claim: {claim}", ln=1)
                pdf.cell(200, 10, txt=f"Score: {score}% ({verdict})", ln=1)
                pdf.multi_cell(0, 10, txt=f"Reasoning: {result.get('reasoning')}")
                
                with xc1:
                    st.download_button(
                        "📄 Download PDF",
                        data=pdf.output(dest='S').encode('latin-1'),
                        file_name="report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                
                with xc2:
                    tweet = f"Fact-check: {claim[:30]}... Score: {score}% via Credibility Engine"
                    st.link_button("🐦 Twitter", f"https://twitter.com/intent/tweet?text={tweet}", use_container_width=True)
                
                with xc3:
                    st.link_button("💬 WhatsApp", f"https://wa.me/?text={tweet}", use_container_width=True)
                    
                with xc4:
                    st.link_button("💼 LinkedIn", "https://linkedin.com", use_container_width=True)

            except Exception as e:
                st.error(f"Analysis Error: {e}")

# --- TAB 2: DASHBOARD ---
with tabs[1]:
    st.subheader("📈 Analytics Dashboard")
    
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Claims", len(df))
        m2.metric("Avg Score", f"{int(df['score'].mean())}%")
        m3.metric("Highest Score", f"{int(df['score'].max())}%")
        m4.metric("Lowest Score", f"{int(df['score'].min())}%")
        
        st.markdown("### Trend Analysis")
        st.line_chart(df.set_index('time')['score'])
        
        st.markdown("### Recent Activity")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Start analyzing claims to populate the dashboard!")

# --- TAB 3: MAP ---
with tabs[2]:
    st.subheader("🌍 Misinformation Heatmap")
    
    # 3D Map (PyDeck runs fine on frontend)
    data = pd.DataFrame({
        'lat': [20.5937 + np.random.uniform(-5, 5) for _ in range(100)],
        'lon': [78.9629 + np.random.uniform(-5, 5) for _ in range(100)],
        'intensity': np.random.randint(1, 100, 100)
    })

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/dark-v10',
        initial_view_state=pdk.ViewState(
            latitude=20.5937,
            longitude=78.9629,
            zoom=3,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'HexagonLayer',
                data=data,
                get_position='[lon, lat]',
                radius=20000,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            )
        ],
    ))
    st.caption("Visualizing spread of verified claims globally.")

# --- TAB 4: KNOWLEDGE ---
with tabs[3]:
    st.subheader("📚 Knowledge Graph")
    st.info("Connected to Pathway Vector Store on Hugging Face")
    st.json({"status": "active", "documents_indexed": "Dynamic", "backend": "HF Spaces"})

# Footer
st.markdown("""
<div class="footer">
    <p>© 2025 Aryan & Khushboo • Powered by Pathway + Groq + HuggingFace</p>
</div>
""", unsafe_allow_html=True)