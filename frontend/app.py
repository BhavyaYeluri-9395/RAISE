import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import os
import time

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="ZEST",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - With Visible Form Fields
# ============================================================================
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    .stApp {
        background: #f0f2f8;
        font-family: 'Inter', sans-serif;
    }
    
    /* ========== GRADIENT HEADER ========== */
    .gradient-header {
        background: linear-gradient(135deg, #6C5CE7 0%, #4E7FFF 50%, #3FD7E0 100%);
        padding: 2.5rem 3rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 20px 60px rgba(108, 92, 231, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .gradient-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
        font-family: 'Inter', sans-serif;
    }
    
    .gradient-header p {
        font-size: 1.1rem;
        opacity: 0.85;
        margin: 0.3rem 0 0 0;
        font-weight: 300;
    }
    
    .gradient-header .badge {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        padding: 0.2rem 1.2rem;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    
    /* ========== GLASS CARDS ========== */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 1.8rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.8);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.1);
    }
    
    .glass-card-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.3rem;
        font-family: 'Inter', sans-serif;
    }
    
    .glass-card-subtitle {
        font-size: 0.85rem;
        color: #6B7290;
        margin-bottom: 1rem;
    }
    
    /* ========== GRADIENT ACTION CARD ========== */
    .gradient-action {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.8rem;
        border-radius: 20px;
        color: white;
        box-shadow: 0 20px 60px rgba(245, 87, 108, 0.25);
        margin-bottom: 1.5rem;
    }
    
    .gradient-action h3 {
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0 0 0.2rem 0;
        font-family: 'Inter', sans-serif;
    }
    
    .gradient-action p {
        font-size: 0.85rem;
        opacity: 0.8;
        margin: 0 0 1.2rem 0;
    }
    
    /* ========== FIXED INPUTS - VISIBLE ========== */
    /* Text Input */
    .stTextInput input {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        font-family: 'Inter', sans-serif !important;
        background: white !important;
        color: #1a1a2e !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.95rem !important;
    }
    
    .stTextInput input:focus {
        border-color: #6C5CE7 !important;
        box-shadow: 0 0 0 4px rgba(108, 92, 231, 0.1) !important;
    }
    
    .stTextInput input::placeholder {
        color: #a0aec0 !important;
    }
    
    /* Text Area */
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        font-family: 'Inter', sans-serif !important;
        background: white !important;
        color: #1a1a2e !important;
        padding: 0.8rem 1rem !important;
        font-size: 0.95rem !important;
        min-height: 150px !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #6C5CE7 !important;
        box-shadow: 0 0 0 4px rgba(108, 92, 231, 0.1) !important;
    }
    
    .stTextArea textarea::placeholder {
        color: #a0aec0 !important;
    }
    
    /* ========== BUTTONS ========== */
    .stButton button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.7rem 1.5rem !important;
        border: none !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #6C5CE7 0%, #4E7FFF 100%) !important;
        color: white !important;
        box-shadow: 0 4px 16px rgba(108, 92, 231, 0.3) !important;
    }
    
    .stButton button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(108, 92, 231, 0.4) !important;
    }
    
    .stButton button[data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #4E7FFF 0%, #3FD7E0 100%) !important;
        color: white !important;
        box-shadow: 0 4px 16px rgba(78, 127, 255, 0.3) !important;
    }
    
    .stButton button[data-testid="baseButton-secondary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(78, 127, 255, 0.4) !important;
    }
    
    /* ========== FILE UPLOADER ========== */
    .stFileUploader {
        border: 2px dashed #cbd5e0 !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        background: rgba(255, 255, 255, 0.5) !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader:hover {
        border-color: #6C5CE7 !important;
        background: rgba(108, 92, 231, 0.04) !important;
    }
    
    .stFileUploader label {
        color: #1a1a2e !important;
        font-weight: 500 !important;
    }
    
    /* ========== TABS ========== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(255, 255, 255, 0.6);
        border-radius: 16px;
        padding: 0.3rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
        margin-bottom: 1.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 0.6rem 1.8rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        color: #6B7290;
        transition: all 0.3s ease;
        font-size: 0.9rem;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #6C5CE7 0%, #4E7FFF 100%);
        color: white;
        box-shadow: 0 4px 16px rgba(108, 92, 231, 0.25);
    }
    
    /* ========== SIDEBAR ========== */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(20px);
    }
    
    .sidebar-gradient {
        background: linear-gradient(135deg, #6C5CE7 0%, #4E7FFF 100%);
        padding: 1.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(108, 92, 231, 0.25);
    }
    
    .sidebar-gradient .label {
        font-size: 0.7rem;
        font-weight: 600;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .sidebar-gradient .value {
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 0.2rem;
    }
    
    /* ========== BADGES ========== */
    .badge-shortlisted {
        background: linear-gradient(135deg, #34D399, #22C55E);
        color: white;
        padding: 0.3rem 1.2rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .badge-not-shortlisted {
        background: linear-gradient(135deg, #FB7185, #F43F5E);
        color: white;
        padding: 0.3rem 1.2rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    
    /* ========== SKILL TAGS ========== */
    .skill-tag {
        display: inline-block;
        background: rgba(108, 92, 231, 0.1);
        color: #6C5CE7;
        padding: 0.25rem 1rem;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.15rem;
        border: 1px solid rgba(108, 92, 231, 0.15);
    }
    
    .missing-skill-tag {
        display: inline-block;
        background: rgba(244, 63, 94, 0.08);
        color: #F43F5E;
        padding: 0.25rem 1rem;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.15rem;
        border: 1px solid rgba(244, 63, 94, 0.15);
    }
    
    /* ========== METRIC ========== */
    .metric-box {
        background: rgba(255, 255, 255, 0.5);
        padding: 1rem 1.2rem;
        border-radius: 16px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.8);
        transition: all 0.3s ease;
    }
    
    .metric-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
    }
    
    .metric-box .number {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6C5CE7, #4E7FFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-box .label {
        font-size: 0.75rem;
        color: #6B7290;
        font-weight: 500;
        margin-top: 0.2rem;
    }
    
    /* ========== SCROLLBAR ========== */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: rgba(108, 92, 231, 0.05); border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #6C5CE7, #4E7FFF); border-radius: 10px; }
    
    /* ========== ANIMATIONS ========== */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in { animation: fadeInUp 0.5s ease-out; }
    
    /* ========== FIX: Make Streamlit form elements visible ========== */
    .stTextInput label, .stTextArea label {
        color: #1a1a2e !important;
        font-weight: 500 !important;
    }
    
    /* Fix for the upload text */
    .stFileUploader div {
        color: #1a1a2e !important;
    }
    
    /* Fix for slider */
    .stSlider label {
        color: #1a1a2e !important;
    }
    
    /* Fix for info/warning boxes */
    .stAlert {
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'analyses' not in st.session_state:
    st.session_state.analyses = []
if 'results' not in st.session_state:
    st.session_state.results = None

API_URL = "http://localhost:8000"

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="gradient-header fade-in">
    <div class="badge">AI-Powered Recruitment</div>
    <h1>ZEST</h1>
    <p>Zero-bias Evaluation and Smart Talent Finder</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    # Connection Status
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            st.markdown("""
            <div style="background: rgba(34, 197, 94, 0.08); padding: 0.8rem 1rem; border-radius: 12px; border: 1px solid rgba(34, 197, 94, 0.15); margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="width: 8px; height: 8px; background: #22C55E; border-radius: 50%; display: inline-block;"></span>
                    <span style="color: #1a1a2e; font-size: 0.85rem; font-weight: 500;">System Online</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: rgba(244, 63, 94, 0.08); padding: 0.8rem 1rem; border-radius: 12px; border: 1px solid rgba(244, 63, 94, 0.15); margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="width: 8px; height: 8px; background: #F43F5E; border-radius: 50%; display: inline-block;"></span>
                    <span style="color: #1a1a2e; font-size: 0.85rem; font-weight: 500;">Server Offline</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.markdown("""
        <div style="background: rgba(244, 63, 94, 0.08); padding: 0.8rem 1rem; border-radius: 12px; border: 1px solid rgba(244, 63, 94, 0.15); margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="width: 8px; height: 8px; background: #F43F5E; border-radius: 50%; display: inline-block;"></span>
                <span style="color: #1a1a2e; font-size: 0.85rem; font-weight: 500;">Server Offline</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.info("Start backend: `uvicorn app.main:app --reload`")
    
    # Match Weights
    st.markdown("""
    <div class="sidebar-gradient">
        <div class="label">Match Weights</div>
        <div style="margin-top: 0.8rem;">
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                <span>Skills</span>
                <span style="font-weight: 600;">50%</span>
            </div>
            <div style="width: 100%; height: 4px; background: rgba(255,255,255,0.2); border-radius: 4px; margin-top: 0.2rem;">
                <div style="width: 50%; height: 100%; background: white; border-radius: 4px;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-top: 0.5rem;">
                <span>Experience</span>
                <span style="font-weight: 600;">30%</span>
            </div>
            <div style="width: 100%; height: 4px; background: rgba(255,255,255,0.2); border-radius: 4px; margin-top: 0.2rem;">
                <div style="width: 30%; height: 100%; background: white; border-radius: 4px;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-top: 0.5rem;">
                <span>Education</span>
                <span style="font-weight: 600;">20%</span>
            </div>
            <div style="width: 100%; height: 4px; background: rgba(255,255,255,0.2); border-radius: 4px; margin-top: 0.2rem;">
                <div style="width: 20%; height: 100%; background: white; border-radius: 4px;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Threshold
    st.markdown("""
    <div style="background: rgba(255,255,255,0.5); backdrop-filter: blur(10px); padding: 1rem 1.5rem; border-radius: 16px; margin-bottom: 1rem; border: 1px solid rgba(255,255,255,0.6);">
        <div style="font-weight: 600; color: #1a1a2e; font-size: 0.85rem; margin-bottom: 0.3rem;">
            Shortlist Threshold
        </div>
    """, unsafe_allow_html=True)
    
    threshold = st.slider(
        "",
        min_value=0.0,
        max_value=1.0,
        value=0.70,
        step=0.05,
        key="threshold_slider",
        label_visibility="collapsed"
    )
    
    st.markdown(f"""
        <div style="text-align: center; font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #6C5CE7, #4E7FFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            {int(threshold * 100)}%
        </div>
        <div style="text-align: center; font-size: 0.7rem; color: #6B7290;">minimum match score</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# TABS
# ============================================================================
tab1, tab2, tab3 = st.tabs(["Upload & Analyze", "Results Dashboard", "History"])

# ============================================================================
# TAB 1: UPLOAD & ANALYZE
# ============================================================================
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="glass-card">
            <div class="glass-card-title">Job Description</div>
            <div class="glass-card-subtitle">Paste the job description or upload a file</div>
        """, unsafe_allow_html=True)
        
        col_title, col_company = st.columns(2)
        with col_title:
            job_title = st.text_input(
                "Job Title",
                placeholder="e.g. Senior Software Engineer",
                label_visibility="collapsed"
            )
        with col_company:
            company_name = st.text_input(
                "Company Name",
                placeholder="e.g. Google",
                label_visibility="collapsed"
            )
        
        job_description = st.text_area(
            "Job Description",
            height=180,
            placeholder="Paste the complete job description here...",
            label_visibility="collapsed"
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-card">
            <div class="glass-card-title">Resumes</div>
            <div class="glass-card-subtitle">Upload one or more resumes in PDF or TXT format</div>
        """, unsafe_allow_html=True)
        
        resume_files = st.file_uploader(
            "",
            type=['pdf', 'txt'],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        
        if resume_files:
            st.markdown(f"""
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.5rem;">
                <span style="background: rgba(108, 92, 231, 0.1); padding: 0.3rem 1rem; border-radius: 50px; font-size: 0.8rem; color: #6C5CE7; font-weight: 600;">
                    {len(resume_files)} file(s) uploaded
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            for f in resume_files:
                st.caption(f"• {f.name} ({round(f.size/1024, 1)} KB)")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="gradient-action">
            <h3>Actions</h3>
            <p>Analyze and shortlist candidates</p>
        """, unsafe_allow_html=True)
        
        if st.button("Analyze Single Resume", use_container_width=True, type="primary"):
            if not job_description:
                st.error("Please provide a job description")
            elif not resume_files:
                st.error("Please upload at least one resume")
            else:
                with st.spinner("Analyzing resume..."):
                    try:
                        file = resume_files[0]
                        files = {'file': (file.name, file.read(), file.type)}
                        data = {
                            'job_description': job_description,
                            'job_title': job_title or "Software Engineer",
                            'company_name': company_name or "Unknown"
                        }
                        
                        response = requests.post(
                            f"{API_URL}/analyze",
                            files=files,
                            data=data
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.results = result
                            st.success("Analysis complete")
                            st.balloons()
                        else:
                            st.error(f"Error: {response.text}")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
        
        if st.button("Shortlist Candidates", use_container_width=True, type="secondary"):
            if not job_description:
                st.error("Please provide a job description")
            elif not resume_files:
                st.error("Please upload at least one resume")
            else:
                with st.spinner("Analyzing all resumes..."):
                    try:
                        files = []
                        for file in resume_files:
                            files.append(
                                ('files', (file.name, file.read(), file.type))
                            )
                        
                        data = {
                            'job_description': job_description,
                            'job_title': job_title or "Software Engineer",
                            'company_name': company_name or "Unknown",
                            'threshold': threshold
                        }
                        
                        response = requests.post(
                            f"{API_URL}/shortlist",
                            files=files,
                            data=data
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.results = result
                            st.session_state.analyses = result.get('candidates', [])
                            st.success(f"Analyzed {result['total_candidates']} candidates")
                            st.balloons()
                        else:
                            st.error(f"Error: {response.text}")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
        
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# TAB 2: RESULTS DASHBOARD
# ============================================================================
with tab2:
    if hasattr(st.session_state, 'results') and st.session_state.results:
        result = st.session_state.results
        
        if 'analysis' in result:
            analysis = result['analysis']
            
            st.markdown("""
            <div class="glass-card fade-in">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                    <div>
                        <div class="glass-card-title" style="font-size: 1.3rem;">Analysis Results</div>
                        <div style="font-size: 0.9rem; color: #6B7290;">
                            Candidate: {candidate_name}
                        </div>
                    </div>
                    <div>
                        {badge}
                    </div>
                </div>
            """.format(
                candidate_name=analysis['resume_data'].get('candidate_name', 'Unknown Candidate'),
                badge='<span class="badge-shortlisted">Shortlisted</span>' if analysis['match_result']['is_shortlisted'] else '<span class="badge-not-shortlisted">Not Shortlisted</span>'
            ), unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="number">{analysis['match_result']['match_score']:.1f}%</div>
                    <div class="label">Overall Match</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="number">{analysis['match_result']['skill_match_score']:.1f}%</div>
                    <div class="label">Skills</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="number">{analysis['match_result']['experience_match_score']:.1f}%</div>
                    <div class="label">Experience</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="number">{analysis['match_result']['education_match_score']:.1f}%</div>
                    <div class="label">Education</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Gauge
            st.markdown("""
            <div class="glass-card">
                <div class="glass-card-title">Match Score Visualization</div>
            """, unsafe_allow_html=True)
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=analysis['match_result']['match_score'],
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [None, 100], 'tickcolor': "#6B7290"},
                    'bar': {'color': "#6C5CE7"},
                    'bgcolor': "rgba(0,0,0,0)",
                    'steps': [
                        {'range': [0, 40], 'color': "rgba(244, 63, 94, 0.08)"},
                        {'range': [40, 70], 'color': "rgba(237, 137, 54, 0.08)"},
                        {'range': [70, 100], 'color': "rgba(34, 197, 94, 0.08)"}
                    ],
                    'threshold': {
                        'line': {'color': "#F43F5E", 'width': 3},
                        'thickness': 0.75,
                        'value': 70
                    }
                }
            ))
            fig.update_layout(
                height=280,
                margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", color="#1a1a2e", size=14)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Skills
            st.markdown("""
            <div class="glass-card">
                <div class="glass-card-title">Skills Analysis</div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div style="font-weight: 600; color: #1a1a2e; font-size: 0.85rem; margin-bottom: 0.5rem;">
                    Matched Skills
                </div>
                """, unsafe_allow_html=True)
                for skill in analysis['match_result']['matched_skills'][:10]:
                    st.markdown(f'<span class="skill-tag">{skill}</span>', unsafe_allow_html=True)
                if not analysis['match_result']['matched_skills']:
                    st.caption("No matching skills found")
            
            with col2:
                st.markdown("""
                <div style="font-weight: 600; color: #1a1a2e; font-size: 0.85rem; margin-bottom: 0.5rem;">
                    Missing Skills
                </div>
                """, unsafe_allow_html=True)
                for skill in analysis['match_result']['missing_skills'][:10]:
                    st.markdown(f'<span class="missing-skill-tag">{skill}</span>', unsafe_allow_html=True)
                if not analysis['match_result']['missing_skills']:
                    st.caption("All required skills matched")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Justification
            if analysis['match_result'].get('justification'):
                st.markdown("""
                <div class="glass-card" style="border-left: 4px solid #6C5CE7;">
                    <div style="font-weight: 700; color: #1a1a2e; font-size: 0.95rem; margin-bottom: 0.5rem;">
                        Professional Justification
                    </div>
                    <div style="color: #4a5568; font-size: 0.9rem; line-height: 1.6;">
                        {justification}
                    </div>
                </div>
                """.format(justification=analysis['match_result']['justification']), unsafe_allow_html=True)
        
        elif 'candidates' in result:
            candidates = result['candidates']
            
            st.markdown(f"""
            <div class="glass-card fade-in">
                <div class="glass-card-title" style="font-size: 1.3rem;">Batch Analysis Results</div>
                <div style="color: #6B7290; font-size: 0.9rem;">{len(candidates)} candidates analyzed</div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            shortlisted_count = sum(1 for c in candidates if c['match_result']['is_shortlisted'])
            rate = (shortlisted_count/len(candidates)*100) if len(candidates) > 0 else 0
            
            with col1:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="number">{len(candidates)}</div>
                    <div class="label">Total Candidates</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="number">{shortlisted_count}</div>
                    <div class="label">Shortlisted</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="number">{rate:.1f}%</div>
                    <div class="label">Shortlist Rate</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Table
            st.markdown("""
            <div class="glass-card">
                <div class="glass-card-title">Candidate Rankings</div>
            """, unsafe_allow_html=True)
            
            df_data = []
            for idx, candidate in enumerate(candidates, 1):
                df_data.append({
                    'Rank': idx,
                    'Name': candidate['resume_data'].get('candidate_name', f'Candidate {idx}'),
                    'Match Score': candidate['match_result']['match_score'],
                    'Skills Match': candidate['match_result']['skill_match_score'],
                    'Experience Match': candidate['match_result']['experience_match_score'],
                    'Education Match': candidate['match_result']['education_match_score'],
                    'Status': '✓ Shortlisted' if candidate['match_result']['is_shortlisted'] else '✗ Not Shortlisted'
                })
            
            df = pd.DataFrame(df_data)
            
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Match Score": st.column_config.ProgressColumn(
                        "Match Score",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100,
                    ),
                    "Status": st.column_config.TextColumn("Status"),
                }
            )
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Chart
            st.markdown("""
            <div class="glass-card">
                <div class="glass-card-title">Score Comparison</div>
            """, unsafe_allow_html=True)
            
            fig = px.bar(
                df,
                x='Name',
                y='Match Score',
                color='Status',
                title='',
                color_discrete_map={'✓ Shortlisted': '#22C55E', '✗ Not Shortlisted': '#F43F5E'},
                text='Match Score'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", color="#1a1a2e"),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=350,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Shortlisted
            shortlisted = [c for c in candidates if c['match_result']['is_shortlisted']]
            if shortlisted:
                st.markdown("""
                <div class="glass-card" style="border-left: 4px solid #22C55E;">
                    <div style="font-weight: 700; color: #1a1a2e; font-size: 1rem; margin-bottom: 0.8rem;">
                        Shortlisted Candidates
                    </div>
                """, unsafe_allow_html=True)
                
                for idx, candidate in enumerate(shortlisted, 1):
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.4); border-radius: 12px; padding: 0.8rem 1.2rem; margin-bottom: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <div>
                                <span style="font-weight: 700; color: #1a1a2e;">#{idx}</span>
                                <span style="font-weight: 600; color: #1a1a2e; margin-left: 0.5rem;">
                                    {candidate['resume_data'].get('candidate_name', f'Candidate {idx}')}
                                </span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 1rem;">
                                <span style="font-weight: 700; color: #6C5CE7; font-size: 1.1rem;">
                                    {candidate['match_result']['match_score']:.1f}%
                                </span>
                                <span style="background: rgba(34, 197, 94, 0.15); color: #22C55E; padding: 0.1rem 0.8rem; border-radius: 50px; font-size: 0.7rem; font-weight: 600;">
                                    Shortlisted
                                </span>
                            </div>
                        </div>
                        <div style="font-size: 0.8rem; color: #6B7290; margin-top: 0.3rem;">
                            Skills: {', '.join(candidate['resume_data'].get('skills', [])[:3])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card fade-in" style="text-align: center; padding: 3rem;">
            <div style="font-size: 1.2rem; font-weight: 600; color: #1a1a2e; margin-bottom: 0.5rem;">
                No Results Yet
            </div>
            <div style="font-size: 0.9rem; color: #6B7290;">
                Upload a resume and job description to see analysis here
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# TAB 3: HISTORY
# ============================================================================
with tab3:
    st.markdown("""
    <div class="glass-card">
        <div class="glass-card-title">Analysis History</div>
        <div class="glass-card-subtitle">View past analyses and shortlisted candidates</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("History will appear here once you start analyzing resumes")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("""
<div style="text-align: center; padding: 2rem 0 0.5rem 0; color: #9AA1C0; font-size: 0.75rem; letter-spacing: 0.3px; border-top: 1px solid rgba(108, 92, 231, 0.08); margin-top: 2rem;">
    ZEST &bull; Built with Python, FastAPI &amp; Streamlit
</div>
""", unsafe_allow_html=True)