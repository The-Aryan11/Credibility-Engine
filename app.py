"""
Credibility Engine - Frontend Client
"""
import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
from fpdf import FPDF
import os
import json
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURATION ---
# Replace with your actual Hugging Face Space URL (check the "Embed this Space" -> "Direct URL" if needed)
# Usually: https://USERNAME-SPACE_NAME.hf.space
BACKEND_URL = os.getenv("BACKEND_URL", "https://aryan12345ark-credibility-backend.hf.space")

st.set_page_config(page_title="Credibility Engine", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .score-card { background: #f8fafc; padding: 20px; border-radius: 10px; text-align: center; border-left: 5px solid #3b82f6; }
    .verdict-badge { padding: 5px 15px; border-radius: 20px; color: white; font-weight: bold; }
    .footer { text-align: center; margin-top: 50px; color: #666; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🔍 Credibility Engine")
    
    # Health Check
    try:
        res = requests.get(f"{BACKEND_URL}/", timeout=2)
        if res.status_code == 200:
            st.success("🟢 Pathway Brain: Online")
        else:
            st.error("🔴 Backend Error")
    except:
        st.error("🔴 Backend Offline")
        st.caption(f"URL: {BACKEND_URL}")

    st.markdown("---")
    st.subheader("📰 Ingest Live Data")
    news_text = st.text_area("Paste Article Text:", height=100)
    news_source = st.text_input("Source:", value="Reuters")
    
    if st.button("🚀 Ingest to Pipeline"):
        if news_text:
            try:
                res = requests.post(f"{BACKEND_URL}/ingest", json={"text": news_text, "source": news_source})
                if res.status_code == 200:
                    st.toast("✅ Document Indexing in Real-Time!")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    st.caption("© 2025 Aryan & Khushboo")

# Main
st.title("🛡️ Real-Time Credibility Engine")
st.markdown("**Powered by Pathway (Streaming RAG) + Groq (LLM)**")

claim = st.text_area("Enter a claim to verify:", height=80, placeholder="e.g. The earth is flat...")

if st.button("🔍 Deep Analyze", type="primary"):
    if not claim:
        st.warning("Please enter a claim.")
    else:
        with st.spinner("🔄 Querying Pathway Vector Store & Analyzing..."):
            try:
                # Call Backend
                response = requests.post(f"{BACKEND_URL}/analyze", json={"claim": claim}, timeout=60)
                data = response.json()
                
                # Display Results
                score = data.get('score', 50)
                verdict = data.get('verdict', 'UNKNOWN')
                color = "#22c55e" if score >= 75 else "#ef4444" if score < 25 else "#eab308"
                
                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(f"<div class='score-card'><h1 style='color:{color}'>{score}%</h1><p>Credibility</p></div>", unsafe_allow_html=True)
                c2.metric("Verdict", verdict)
                c3.metric("Category", data.get('category'))
                c4.metric("Sentiment", data.get('sentiment', 'Neutral'))
                
                st.divider()
                
                c_left, c_right = st.columns(2)
                
                with c_left:
                    st.subheader("📝 Reasoning")
                    st.write(data.get('reasoning'))
                    
                    st.subheader("🔑 Key Evidence")
                    for point in data.get('key_evidence', []):
                        st.info(point)
                
                with c_right:
                    st.subheader("📚 Retrieved Sources (RAG)")
                    sources = data.get('sources', [])
                    if sources:
                        for s in sources:
                            st.caption(f"📄 {s}")
                    else:
                        st.info("No specific documents found in knowledge base (AI relied on internal knowledge)")
                        
                # Features: Map & PDF
                st.divider()
                
                # Map
                st.subheader("🗺️ Geographic Spread")
                import numpy as np
                df = pd.DataFrame({
                    'lat': [20 + np.random.randn() for _ in range(100)],
                    'lon': [78 + np.random.randn() for _ in range(100)]
                })
                st.pydeck_chart(pdk.Deck(
                    map_style=None,
                    initial_view_state=pdk.ViewState(latitude=20, longitude=78, zoom=3),
                    layers=[pdk.Layer('HexagonLayer', data=df, get_position='[lon, lat]', radius=200000, elevation_scale=4, extruded=True)]
                ))
                
                # PDF
                class PDF(FPDF):
                    def header(self):
                        self.set_font('Arial', 'B', 15)
                        self.cell(0, 10, 'Fact Check Report', 0, 1, 'C')
                
                pdf = PDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, f"Claim: {claim}\nScore: {score}%\nVerdict: {verdict}\n\nAnalysis:\n{data.get('reasoning')}")
                st.download_button("📄 Download PDF Report", data=pdf.output(dest='S').encode('latin-1'), file_name="report.pdf")

            except Exception as e:
                st.error(f"Analysis Failed: {e}")

st.markdown("<div class='footer'>© 2025 Aryan & Khushboo • Powered by Pathway</div>", unsafe_allow_html=True)