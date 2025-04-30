"""
Dashboard page for Security Compliance Advisor
This page displays risk assessment results and recommendations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


def render_dashboard_page():
    """Render the dashboard page with risk assessment results"""
    # Check if assessment data exists
    if st.session_state.assessment is None:
        render_empty_dashboard()
        return

    # Display assessment results
    assessment = st.session_state.assessment
    recommendations = st.session_state.recommendations
    
    # Risk Summary Section
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <h3 class="card-header">Overall Risk Score</h3>
            <div class="dashboard-metric">68.5%</div>
            <p>Medium Risk Level</p>
            <div style="margin-top: 10px;">
                <div style="background-color: #FFB74D; height: 8px; width: 68.5%; border-radius: 4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <h3 class="card-header">Framework Compliance</h3>
            <div class="dashboard-metric">72.5%</div>
            <p>Average compliance across frameworks</p>
            <div style="margin-top: 10px;">
                <div style="background-color: #3687d8; height: 8px; width: 72.5%; border-radius: 4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="dashboard-card">
            <h3 class="card-header">Security Gaps</h3>
            <div class="dashboard-metric">11</div>
            <p>Critical security areas needing attention</p>
            <div style="margin-top: 10px; display: flex; justify-content: space-between;">
                <span>🔴 High: 4</span>
                <span>🟠 Medium: 5</span>
                <span>🟡 Low: 2</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Create tabs for different dashboard sections
    tab1, tab2, tab3 = st.tabs(["Risk Analysis", "Compliance", "Recommendations"])
    
    with tab1:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        render_risk_analysis()
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab2:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        render_compliance_section()
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab3:
        render_recommendations_section(recommendations)


def render_empty_dashboard():
    """Render the dashboard when no assessment data is available"""
    st.markdown("""
    <div class="card">
        <div class="card-header">No Assessment Data Available</div>
        <p>Please upload and analyze a security questionnaire to view risk assessment results.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="dashboard-card">
        <h3 class="card-header">Get Started</h3>
        <p>Follow these steps to generate your security assessment:</p>
        <ol>
            <li>Go to the <b>Assessment Questionnaire</b> page</li>
            <li>Upload a security questionnaire file or use a template</li>
            <li>Run the risk assessment</li>
            <li>Return to this dashboard to view results</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample visualization of what the dashboard will look like
    st.markdown("### Sample Dashboard Preview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-header">Risk Domain Analysis</div>
            <p><i>Sample data visualization (upload a questionnaire to see your actual data)</i></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample risk domain data
        domains = ["Access Control", "Data Protection", "Vulnerability Management", "Network Security", "Incident Response"]
        values = [62, 48, 75, 85, 70]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=domains,
            y=values,
            marker_color=['#FFB74D' if v < 70 else '#4CAF50' for v in values],
            text=values,
            textposition='auto',
        ))
        
        fig.update_layout(
            title="Security Domain Scores",
            xaxis_title="",
            yaxis_title="Score (%)",
            template="plotly_dark",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(37, 50, 72, 0.0)',
            plot_bgcolor='rgba(37, 50, 72, 0.0)',
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-header">Framework Compliance</div>
            <p><i>Sample data visualization (upload a questionnaire to see your actual data)</i></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample framework compliance data
        frameworks = ["ISO 27001", "NIST CSF", "GDPR", "HIPAA", "PCI DSS"]
        compliance = [78, 65, 82, 73, 90]
        
        fig = px.line_polar(
            r=compliance, 
            theta=frameworks, 
            line_close=True,
            range_r=[0, 100],
            color_discrete_sequence=["#3687d8"]
        )
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            template="plotly_dark",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(37, 50, 72, 0.0)',
            plot_bgcolor='rgba(37, 50, 72, 0.0)',
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_risk_analysis():
    """Render the risk analysis section of the dashboard"""
    # Domain Risk Chart
    st.subheader("Security Domain Risk Analysis")
    
    # Create domain risk data
    domains = ["Data Protection", "Access Control", "Vulnerability Management", "Network Security", "Authentication", "Encryption"]
    scores = [42, 55, 75, 65, 80, 58]
    thresholds = [50, 70, 90]  # Red, Yellow, Green thresholds
    
    # Assign colors based on thresholds
    colors = []
    for score in scores:
        if score < thresholds[0]:
            colors.append('#f44336')
        elif score < thresholds[1]:
            colors.append('#ff9800')
        else:
            colors.append('#4caf50')
    
    # Create horizontal bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=domains,
        x=scores,
        orientation='h',
        marker_color=colors,
        text=[f"{s}%" for s in scores],
        textposition='auto',
        hoverinfo='text',
        hovertext=[f"{d}: {s}% score" for d, s in zip(domains, scores)]
    ))
    
    fig.update_layout(
        xaxis_title="Score (%)",
        yaxis=dict(
            title="",
            autorange="reversed"
        ),
        template="plotly_dark",
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(range=[0, 100]),
        paper_bgcolor='rgba(37, 50, 72, 0.0)',
        plot_bgcolor='rgba(37, 50, 72, 0.0)',
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Risk Categories and Controls
    st.subheader("Top Risk Areas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-header">Data Protection</div>
            <div style="color: #f44336; font-size: 24px; font-weight: bold; margin: 10px 0;">42%</div>
            <p><b>Key Issues:</b></p>
            <ul>
                <li>No data encryption at rest</li>
                <li>Weak data classification policies</li>
                <li>Limited data loss prevention controls</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <div class="card-header">Access Control</div>
            <div style="color: #ff9800; font-size: 24px; font-weight: bold; margin: 10px 0;">55%</div>
            <p><b>Key Issues:</b></p>
            <ul>
                <li>Incomplete privileged access management</li>
                <li>No regular access review process</li>
                <li>Inconsistent least privilege implementation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-header">Risk Trend Analysis</div>
            <p>Risk score trend over the last 5 assessments:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample trend data
        dates = ["Jan 2025", "Feb 2025", "Mar 2025", "Apr 2025", "May 2025"]
        risk_scores = [78, 72, 68, 65, 68.5]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=risk_scores,
            mode='lines+markers',
            name='Risk Score',
            line=dict(color='#3687d8', width=4),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            xaxis_title="Assessment Date",
            yaxis_title="Risk Score",
            template="plotly_dark",
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis=dict(range=[40, 100]),
            paper_bgcolor='rgba(37, 50, 72, 0.0)',
            plot_bgcolor='rgba(37, 50, 72, 0.0)',
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_compliance_section():
    """Render the compliance section of the dashboard"""
    st.subheader("Framework Compliance")
    
    # Framework compliance radar chart
    frameworks = ["ISO 27001", "NIST CSF", "GDPR", "HIPAA", "PCI DSS", "CCPA", "CIS", "SOC 2"]
    compliance_scores = [73, 67, 83, 76, 92, 65, 70, 80]
    
    # Radar chart for framework compliance
    fig = px.line_polar(
        r=compliance_scores,
        theta=frameworks,
        line_close=True,
        range_r=[0, 100],
        color_discrete_sequence=["#3687d8"]
    )
    
    fig.update_traces(fill='toself', opacity=0.7)
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        template="plotly_dark",
        height=500,
        margin=dict(l=60, r=60, t=20, b=20),
        paper_bgcolor='rgba(37, 50, 72, 0.0)',
        plot_bgcolor='rgba(37, 50, 72, 0.0)',
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-header">Compliance Details</div>
            <p>Assessment against major security frameworks:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display compliance details for each framework
        for framework, score in zip(frameworks, compliance_scores):
            color = "#f44336" if score < 60 else "#ff9800" if score < 80 else "#4caf50"
            st.markdown(f"""
            <div style="margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 500;">{framework}</span>
                    <span style="color: {color}; font-weight: bold;">{score}%</span>
                </div>
                <div style="width: 100%; background-color: #1a2234; height: 6px; border-radius: 3px; margin-top: 5px;">
                    <div style="width: {score}%; background-color: {color}; height: 6px; border-radius: 3px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Control coverage by framework
    st.subheader("Control Coverage by Category")
    
    # Create control coverage data
    categories = ["Identity & Access Management", "Data Protection", "Network Security", 
                "Encryption", "Incident Response", "Business Continuity", "Third-Party Risk"]
    iso_coverage = [85, 65, 90, 70, 80, 60, 75]
    nist_coverage = [75, 60, 85, 65, 70, 55, 60]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories,
        y=iso_coverage,
        name='ISO 27001',
        marker_color='#3687d8',
        opacity=0.7
    ))
    
    fig.add_trace(go.Bar(
        x=categories,
        y=nist_coverage,
        name='NIST CSF',
        marker_color='#ffb74d',
        opacity=0.7
    ))
    
    fig.update_layout(
        xaxis_title="Control Categories",
        yaxis_title="Coverage (%)",
        barmode='group',
        template="plotly_dark",
        height=400,
        margin=dict(l=20, r=20, t=20, b=80),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        paper_bgcolor='rgba(37, 50, 72, 0.0)',
        plot_bgcolor='rgba(37, 50, 72, 0.0)',
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_recommendations_section(recommendations):
    """Render the recommendations section of the dashboard"""
    st.subheader("Security Recommendations")
    
    # If we have real recommendations, display them
    if recommendations and len(recommendations) > 0:
        for i, rec in enumerate(recommendations):
            priority = rec.get('priority', 'Medium')
            category = rec.get('category', 'General')
            title = rec.get('title', f'Recommendation {i+1}')
            description = rec.get('description', 'No description provided.')
            
            # Set color based on priority
            color = {
                'High': '#f44336',
                'Medium': '#ff9800',
                'Low': '#4caf50'
            }.get(priority, '#ff9800')
            
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 4px; margin-right: 10px;">
                        {priority}
                    </div>
                    <div style="background-color: rgba(54, 135, 216, 0.2); color: #3687d8; padding: 3px 8px; border-radius: 4px;">
                        {category}
                    </div>
                </div>
                <div class="card-header">{title}</div>
                <p>{description}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Sample recommendations for demo
        sample_recs = [
            {
                'priority': 'High',
                'category': 'Data Protection',
                'title': 'Implement Data Encryption at Rest',
                'description': 'Deploy encryption for all sensitive data stored in databases and file systems. Prioritize PII and financial data.'
            },
            {
                'priority': 'High',
                'category': 'Access Control',
                'title': 'Establish Privileged Access Management',
                'description': 'Implement a PAM solution to control, monitor, and audit privileged access to critical systems and sensitive data.'
            },
            {
                'priority': 'Medium',
                'category': 'Authentication',
                'title': 'Enable Multi-Factor Authentication',
                'description': 'Require MFA for all user accounts, especially those with administrative privileges or access to sensitive data.'
            },
            {
                'priority': 'Medium',
                'category': 'Network Security',
                'title': 'Implement Network Segmentation',
                'description': 'Segment networks to isolate critical systems and restrict lateral movement in case of a breach.'
            },
            {
                'priority': 'Low',
                'category': 'Policy & Procedures',
                'title': 'Update Security Policies',
                'description': 'Review and update security policies to align with current industry standards and regulatory requirements.'
            }
        ]
        
        for rec in sample_recs:
            priority = rec['priority']
            category = rec['category']
            title = rec['title']
            description = rec['description']
            
            # Set color based on priority
            color = {
                'High': '#f44336',
                'Medium': '#ff9800',
                'Low': '#4caf50'
            }.get(priority, '#ff9800')
            
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 4px; margin-right: 10px;">
                        {priority}
                    </div>
                    <div style="background-color: rgba(54, 135, 216, 0.2); color: #3687d8; padding: 3px 8px; border-radius: 4px;">
                        {category}
                    </div>
                </div>
                <div class="card-header">{title}</div>
                <p>{description}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="margin-top: 20px; text-align: center; color: #a0aec0; font-style: italic;">
            This is sample recommendation data. Upload a questionnaire for personalized recommendations.
        </div>
        """, unsafe_allow_html=True)