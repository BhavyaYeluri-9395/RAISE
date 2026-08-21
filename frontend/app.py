import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import os

# Page configuration
st.set_page_config(
    page_title="Smart Resume Screener",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .shortlisted {
        background: #d4edda;
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .not-shortlisted {
        background: #f8d7da;
        border: 2px solid #dc3545;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .skill-match {
        background: #cce5ff;
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        display: inline-block;
        margin: 0.2rem;
    }
    .missing-skill {
        background: #f8d7da;
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        display: inline-block;
        margin: 0.2rem;
    }
    </style>
""", unsafe_allow_html=True)

# API endpoint
API_URL = "http://localhost:8000"

# Title
st.markdown('<div class="main-header">🤖 Smart Resume Screener</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Intelligently parse resumes, extract skills, and match with job descriptions</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    
    # API connection check
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ Connected to API")
        else:
            st.error("❌ API connection failed")
    except:
        st.error("❌ API server not running! Start with: uvicorn app.main:app --reload")
    
    st.markdown("---")
    st.markdown("### 📊 Match Weights")
    st.info("""
    - **Skills**: 50%
    - **Experience**: 30%
    - **Education**: 20%
    """)
    
    st.markdown("---")
    st.markdown("### 🎯 Shortlist Threshold")
    threshold = st.slider(
        "Match score threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.70,
        step=0.05
    )

# Main content
tab1, tab2, tab3 = st.tabs(["📤 Upload & Analyze", "📊 Results Dashboard", "📚 History"])

# Tab 1: Upload
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 Job Description")
        
        col_title, col_company = st.columns(2)
        with col_title:
            job_title = st.text_input("Job Title", placeholder="e.g., Senior Software Engineer")
        with col_company:
            company_name = st.text_input("Company Name", placeholder="e.g., Google")
        
        job_description = st.text_area(
            "Paste the job description here",
            height=200,
            placeholder="Paste the complete job description here..."
        )
        
        st.markdown("---")
        st.markdown("### 📎 Upload Resumes")
        resume_files = st.file_uploader(
            "Upload one or more resumes (PDF/TXT)",
            type=['pdf', 'txt'],
            accept_multiple_files=True
        )
        
        if resume_files:
            st.info(f"📄 {len(resume_files)} resume(s) uploaded")
            for f in resume_files:
                st.caption(f"• {f.name} ({round(f.size/1024, 1)} KB)")
    
    with col2:
        st.markdown("### 🚀 Actions")
        
        if st.button("🔍 Analyze Single Resume", type="primary", use_container_width=True):
            if not job_description:
                st.error("❌ Please provide a job description")
            elif not resume_files:
                st.error("❌ Please upload at least one resume")
            else:
                with st.spinner("🔄 Analyzing resume..."):
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
                            st.success("✅ Analysis complete!")
                            st.balloons()
                        else:
                            st.error(f"❌ Error: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")
        
        if st.button("📊 Shortlist Candidates", type="primary", use_container_width=True):
            if not job_description:
                st.error("❌ Please provide a job description")
            elif not resume_files:
                st.error("❌ Please upload at least one resume")
            else:
                with st.spinner("🔄 Analyzing all resumes..."):
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
                            st.success(f"✅ Analyzed {result['total_candidates']} candidates!")
                            st.balloons()
                        else:
                            st.error(f"❌ Error: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")

# Tab 2: Results
with tab2:
    if hasattr(st.session_state, 'results') and st.session_state.results:
        result = st.session_state.results
        
        if 'analysis' in result:
            analysis = result['analysis']
            st.markdown(f"### 📊 Analysis Results")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Overall Match", f"{analysis['match_result']['match_score']:.1f}%")
            with col2:
                st.metric("Skills Match", f"{analysis['match_result']['skill_match_score']:.1f}%")
            with col3:
                st.metric("Experience Match", f"{analysis['match_result']['experience_match_score']:.1f}%")
            with col4:
                st.metric("Education Match", f"{analysis['match_result']['education_match_score']:.1f}%")
            
            # Gauge chart
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = analysis['match_result']['match_score'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Match Score"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 40], 'color': "lightgray"},
                        {'range': [40, 70], 'color': "gray"},
                        {'range': [70, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 70
                    }
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
            
        elif 'candidates' in result:
            candidates = result['candidates']
            st.markdown(f"### 📊 Batch Analysis Results - {len(candidates)} Candidates")
            
            df_data = []
            for idx, candidate in enumerate(candidates, 1):
                df_data.append({
                    'Rank': idx,
                    'Name': candidate['resume_data'].get('candidate_name', f'Candidate {idx}'),
                    'Match Score': candidate['match_result']['match_score'],
                    'Skills Match': candidate['match_result']['skill_match_score'],
                    'Experience Match': candidate['match_result']['experience_match_score'],
                    'Education Match': candidate['match_result']['education_match_score'],
                    'Shortlisted': '✅' if candidate['match_result']['is_shortlisted'] else '❌'
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Bar chart
            fig = px.bar(
                df,
                x='Name',
                y='Match Score',
                color='Shortlisted',
                title='Match Scores by Candidate',
                color_discrete_map={'✅': 'green', '❌': 'red'}
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("👈 Upload and analyze resumes to see results here")

# Tab 3: History
with tab3:
    st.markdown("### 📚 Analysis History")
    st.info("History will be available here once you analyze resumes")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        Made with ❤️ using Streamlit, FastAPI, and Gemini AI
    </div>
""", unsafe_allow_html=True)