"""
Dashboard page for Security Compliance Advisor with PDF Report Generation
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os

from app.utils.pdf_generator import render_pdf_download_button

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
        
    # Add PDF report generation section
    st.markdown("---")
    st.markdown("## Generate Complete Risk Assessment Report")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Vendor name input
        vendor_name = st.text_input("Vendor Name", value="Acme Corporation")
        
        # Company name input
        company_name = st.text_input("Your Company Name", value="Your Company")
        
        # Generate PDF report button
        render_pdf_download_button(
            assessment=assessment, 
            vendor_name=vendor_name,
            company_name=company_name
        )
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-header">Risk Assessment Report</div>
            <p>Generate a comprehensive PDF risk assessment report that includes:</p>
            <ul>
                <li>Executive summary with key findings</li>
                <li>Detailed risk analysis with likelihood and impact assessments</li>
                <li>Framework compliance status</li>
                <li>Itemized security gaps and recommendations</li>
                <li>Documentation review and exceptions noted</li>
                <li>Risk matrix and scoring methodology</li>
            </ul>
            <p>This report follows industry standard risk assessment methodologies and is suitable for sharing with stakeholders and compliance teams.</p>
        </div>
        """, unsafe_allow_html=True)


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
            <div class="card-header">Risk Matrix</div>
            <p>Interactive risk matrix showing impact vs. likelihood:</p>
        </div>
        """, unsafe_allow_html=True)
        
        impact = ['Negligible(1)', 'Minor(2)', 'Major(3)', 'Severe(4)', 'Catastrophic(5)']
        likelihood = ['Rare(1)', 'Unlikely(2)', 'Possible(3)', 'Probable(4)', 'Certain(5)']
        
        risk_scores = [
            [1, 2, 3, 4, 5],   # Negligible impact
            [2, 4, 6, 8, 10],  # Minor impact
            [3, 6, 9, 12, 15], # Major impact
            [4, 8, 12, 16, 20], # Severe impact
            [5, 10, 15, 20, 25]  # Catastrophic impact
        ]
        
        # Create a heatmap
        fig = go.Figure(data=go.Heatmap(
            z=risk_scores,
            x=likelihood,
            y=impact,
            colorscale=[
                [0, 'green'],
                [0.3, 'yellow'],
                [0.6, 'orange'],
                [1, 'red']
            ],
            showscale=True,
            colorbar=dict(
                title="Risk Score",
                tickvals=[1, 7, 13, 19, 25],
                ticktext=["Low", "Medium-Low", "Medium", "High", "Critical"]
            ),
            text=risk_scores,
            texttemplate="%{text}",
            textfont={"size": 14},
        ))
        
        fig.update_layout(
               title="Risk Assessment Matrix",
    xaxis_title="Likelihood",
    yaxis_title="Impact",
    template="plotly_dark", 
    height=400,
    margin=dict(l=20, r=20, t=40, b=20),
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
            
            with st.expander(f"{title}"):
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 4px; margin-right: 10px;">
                        {priority} Priority
                    </div>
                    <div style="background-color: rgba(54, 135, 216, 0.2); color: #3687d8; padding: 3px 8px; border-radius: 4px;">
                        {category}
                    </div>
                </div>
                
                <p><b>Description:</b> {description}</p>
                """, unsafe_allow_html=True)
                
                # Display detailed actions if available
                if 'detailed_actions' in rec and rec['detailed_actions']:
                    st.markdown("<p><b>Detailed Actions:</b></p>", unsafe_allow_html=True)
                    for action in rec['detailed_actions']:
                        st.markdown(f"- {action}")
    else:
        # Sample recommendations for demo
        sample_recs = [
            {
                'priority': 'High',
                'category': 'Data Protection',
                'title': 'Implement Data Encryption at Rest',
                'description': 'Deploy encryption for all sensitive data stored in databases and file systems. Prioritize PII and financial data.',
                'detailed_actions': [
                    'Identify and classify sensitive data repositories',
                    'Select appropriate encryption standards (AES-256)',
                    'Implement key management procedures',
                    'Deploy database and file system encryption',
                    'Test recovery procedures with encrypted data'
                ]
            },
            {
                'priority': 'High',
                'category': 'Access Control',
                'title': 'Establish Privileged Access Management',
                'description': 'Implement a PAM solution to control, monitor, and audit privileged access to critical systems and sensitive data.',
                'detailed_actions': [
                    'Inventory all privileged accounts',
                    'Implement just-in-time privileged access',
                    'Deploy session recording for privileged activities',
                    'Establish approval workflows for privileged access',
                    'Conduct regular privileged access reviews'
                ]
            },
            {
                'priority': 'Medium',
                'category': 'Authentication',
                'title': 'Enable Multi-Factor Authentication',
                'description': 'Require MFA for all user accounts, especially those with administrative privileges or access to sensitive data.',
                'detailed_actions': [
                    'Select appropriate MFA methods (app-based, hardware tokens)',
                    'Implement MFA for administrative accounts first',
                    'Extend MFA to all user accounts',
                    'Develop bypass procedures for emergency access',
                    'Train users on MFA procedures'
                ]
            }
        ]
        
        for rec in sample_recs:
            priority = rec['priority']
            category = rec['category']
            title = rec['title']
            description = rec['description']
            detailed_actions = rec.get('detailed_actions', [])
            
            # Set color based on priority
            color = {
                'High': '#f44336',
                'Medium': '#ff9800',
                'Low': '#4caf50'
            }.get(priority, '#ff9800')
            
            with st.expander(f"{title}"):
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 4px; margin-right: 10px;">
                        {priority} Priority
                    </div>
                    <div style="background-color: rgba(54, 135, 216, 0.2); color: #3687d8; padding: 3px 8px; border-radius: 4px;">
                        {category}
                    </div>
                </div>
                
                <p><b>Description:</b> {description}</p>
                """, unsafe_allow_html=True)
                
                # Display detailed actions
                if detailed_actions:
                    st.markdown("<p><b>Detailed Actions:</b></p>", unsafe_allow_html=True)
                    for action in detailed_actions:
                        st.markdown(f"- {action}")
        
        st.markdown("""
        <div style="margin-top: 20px; text-align: center; color: #a0aec0; font-style: italic;">
            This is sample recommendation data. Upload a questionnaire for personalized recommendations.
        </div>
        """, unsafe_allow_html=True)


# QAD Analyzer Component for detailed questionnaire analysis
class QADAnalyzer:
    """
    Analyzes questionnaire responses (Questions, Answers, and Details)
    to identify risk factors and provide insights.
    """
    
    def __init__(self):
        """Initialize the QAD Analyzer"""
        # Define risk categories and critical control areas
        self.risk_categories = [
            "Access Control",
            "Authentication",
            "Data Protection",
            "Network Security",
            "Vulnerability Management",
            "Incident Response",
            "Business Continuity",
            "Encryption",
            "Third-Party Management",
            "Security Governance"
        ]
        
        # Define positive and negative response indicators
        self.positive_indicators = [
            "yes", "implemented", "complete", "compliant", "secure", 
            "encrypted", "monitored", "regularly", "always", "documented"
        ]
        
        self.negative_indicators = [
            "no", "not implemented", "partial", "in progress", "planned", 
            "sometimes", "rarely", "never", "none", "n/a"
        ]
        
        # Critical security controls that have higher risk impact
        self.critical_controls = [
            "multi-factor authentication",
            "encryption",
            "privileged access management",
            "vulnerability scanning",
            "patch management",
            "incident response plan",
            "data backup",
            "disaster recovery",
            "security monitoring"
        ]
    
    def analyze_questionnaire(self, questions_data):
        """
        Analyze questionnaire responses to identify risk factors
        
        Args:
            questions_data: List of question dictionaries from the questionnaire
            
        Returns:
            Analysis results including risk factors and category insights
        """
        results = {
            "total_questions": len(questions_data),
            "risk_factors": [],
            "category_insights": {},
            "critical_gaps": [],
            "strengths": [],
            "response_quality": {}
        }
        
        # Initialize category counters
        for category in self.risk_categories:
            results["category_insights"][category] = {
                "total": 0,
                "positive": 0,
                "negative": 0,
                "score": 0.0,
                "findings": []
            }
        
        # Analyze each question and answer
        for q_idx, question in enumerate(questions_data):
            q_text = question.get('question', '').lower()
            answer = question.get('answer', '').lower()
            
            # Skip questions without text or answers
            if not q_text or not answer:
                continue
            
            # Categorize the question
            category = self._determine_category(q_text)
            
            # Analyze the response for positive/negative indicators
            response_analysis = self._analyze_response(q_text, answer)
            is_positive = response_analysis["is_positive"]
            contradictions = response_analysis["contradictions"]
            confidence = response_analysis["confidence"]
            
            # Update category insights
            if category:
                results["category_insights"][category]["total"] += 1
                if is_positive:
                    results["category_insights"][category]["positive"] += 1
                else:
                    results["category_insights"][category]["negative"] += 1
                    
                    # Add to findings for negative responses
                    if confidence >= 0.6:  # Only include high confidence findings
                        finding = {
                            "question_id": q_idx,
                            "question_text": q_text,
                            "answer": answer,
                            "confidence": confidence,
                            "contradictions": contradictions,
                            "is_critical": self._is_critical_control(q_text)
                        }
                        results["category_insights"][category]["findings"].append(finding)
            
            # Check for critical control gaps
            if not is_positive and self._is_critical_control(q_text):
                results["critical_gaps"].append({
                    "question_id": q_idx,
                    "category": category,
                    "question_text": q_text,
                    "answer": answer,
                    "confidence": confidence
                })
            
            # Identify strengths
            if is_positive and confidence >= 0.8:
                results["strengths"].append({
                    "question_id": q_idx,
                    "category": category,
                    "question_text": q_text,
                    "answer": answer
                })
            
            # Identify risk factors from the response
            if not is_positive and confidence >= 0.7:
                risk_factor = {
                    "question_id": q_idx,
                    "category": category,
                    "question_text": q_text,
                    "answer": answer,
                    "is_critical": self._is_critical_control(q_text),
                    "impact": "High" if self._is_critical_control(q_text) else "Medium"
                }
                results["risk_factors"].append(risk_factor)
        
        # Calculate category scores
        for category, insights in results["category_insights"].items():
            if insights["total"] > 0:
                insights["score"] = (insights["positive"] / insights["total"]) * 100
            else:
                insights["score"] = 0
        
        # Analyze response quality
        results["response_quality"] = self._analyze_response_quality(questions_data)
        
        return results
    
    def _determine_category(self, question_text):
        """Determine the security category for a question"""
        # Simple keyword matching for categories
        category_keywords = {
            "Access Control": ["access control", "access management", "permission", "privilege", "authorization"],
            "Authentication": ["authentication", "password", "mfa", "multi-factor", "identity", "login"],
            "Data Protection": ["data protection", "privacy", "personal data", "data classification", "data loss"],
            "Network Security": ["network", "firewall", "intrusion", "perimeter", "segmentation", "dmz"],
            "Vulnerability Management": ["vulnerability", "patch", "update", "scan", "assessment", "penetration"],
            "Incident Response": ["incident", "breach", "response", "alert", "detect", "siem"],
            "Business Continuity": ["continuity", "disaster", "recovery", "backup", "resilience", "bcp", "drp"],
            "Encryption": ["encrypt", "cryptograph", "cipher", "key management", "tls", "ssl"],
            "Third-Party Management": ["vendor", "third party", "service provider", "supplier", "outsource"],
            "Security Governance": ["policy", "governance", "compliance", "standard", "procedure", "management"]
        }
        
        # Find the category with the most keyword matches
        best_category = None
        max_matches = 0
        
        for category, keywords in category_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in question_text)
            if matches > max_matches:
                max_matches = matches
                best_category = category
        
        return best_category if max_matches > 0 else "General"
    
    def _analyze_response(self, question_text, answer):
        """
        Analyze a question response to determine if it's positive or negative
        
        Returns:
            Dictionary with analysis results
        """
        # Count positive and negative indicators
        positive_count = sum(1 for ind in self.positive_indicators if ind in answer)
        negative_count = sum(1 for ind in self.negative_indicators if ind in answer)
        
        # Determine if the response is positive or negative
        is_positive = positive_count > negative_count
        
        # Check for contradictions (e.g., "yes, but...")
        contradictions = []
        if "yes" in answer and any(q in answer for q in ["but", "however", "although"]):
            contradictions.append("Qualified positive response")
            is_positive = positive_count > negative_count + 1  # Higher threshold for contradiction
        
        if "no" in answer and any(q in answer for q in ["but", "however", "although", "planned"]):
            contradictions.append("Qualified negative response")
            is_positive = positive_count > negative_count  # Standard threshold
        
        # Calculate confidence level
        if positive_count == 0 and negative_count == 0:
            # No clear indicators, medium confidence
            confidence = 0.5
        elif positive_count > 0 and negative_count > 0:
            # Mixed indicators, confidence based on ratio
            total = positive_count + negative_count
            confidence = max(positive_count, negative_count) / total
        else:
            # Clear indicators in one direction
            indicator_count = max(positive_count, negative_count)
            confidence = min(0.5 + (0.1 * indicator_count), 0.9)
        
        return {
            "is_positive": is_positive,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "contradictions": contradictions,
            "confidence": confidence
        }
    
    def _is_critical_control(self, question_text):
        """Determine if a question relates to a critical security control"""
        return any(control in question_text for control in self.critical_controls)
    
    def _analyze_response_quality(self, questions_data):
        """Analyze the overall quality of questionnaire responses"""
        total_questions = len(questions_data)
        answered_questions = sum(1 for q in questions_data if q.get('answer'))
        empty_answers = total_questions - answered_questions
        
        # Count short answers (less than 5 words)
        short_answers = sum(1 for q in questions_data if q.get('answer') and len(q.get('answer', '').split()) < 5)
        
        # Count detailed answers (more than 15 words)
        detailed_answers = sum(1 for q in questions_data if q.get('answer') and len(q.get('answer', '').split()) > 15)
        
        # Calculate response completion percentage
        completion_pct = (answered_questions / total_questions * 100) if total_questions > 0 else 0
        
        # Calculate detail level (0-100%)
        detail_level = (detailed_answers / answered_questions * 100) if answered_questions > 0 else 0
        
        return {
            "total_questions": total_questions,
            "answered_questions": answered_questions,
            "empty_answers": empty_answers,
            "short_answers": short_answers,
            "detailed_answers": detailed_answers,
            "completion_pct": completion_pct,
            "detail_level": detail_level
        }
    
    def render_qad_analysis(self, questions_data):
        """
        Render the QAD analysis results in Streamlit
        
        Args:
            questions_data: List of question dictionaries from the questionnaire
        """
        analysis = self.analyze_questionnaire(questions_data)
        
        st.subheader("Questionnaire Response Analysis")
        
        # Display response quality metrics
        quality = analysis["response_quality"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Response Completion", f"{quality['completion_pct']:.1f}%", 
                     delta=None if quality['completion_pct'] > 90 else f"{100-quality['completion_pct']:.1f}% incomplete")
        
        with col2:
            st.metric("Response Detail Level", f"{quality['detail_level']:.1f}%",
                     delta=None if quality['detail_level'] > 70 else f"{100-quality['detail_level']:.1f}% need more detail")
        
        with col3:
            detail_ratio = f"{quality['detailed_answers']}/{quality['answered_questions']}"
            st.metric("Detailed Responses", detail_ratio,
                     delta=None if quality['detail_level'] > 70 else "Need more detailed answers")
        
        # Display critical security gaps
        st.subheader("Critical Security Control Gaps")
        
        if analysis["critical_gaps"]:
            for gap in analysis["critical_gaps"]:
                with st.expander(f"Q: {gap['question_text'][:100]}..."):
                    st.markdown(f"**Category:** {gap['category']}")
                    st.markdown(f"**Question:** {gap['question_text']}")
                    st.markdown(f"**Response:** {gap['answer']}")
                    st.markdown(f"**Confidence:** {gap['confidence']:.0%}")
                    st.markdown(f"**Analysis:** This response indicates a gap in a critical security control.")
        else:
            st.info("No critical security control gaps identified.")
        
        # Display category insights
        st.subheader("Security Category Analysis")
        
        # Filter to categories with responses
        active_categories = {cat: data for cat, data in analysis["category_insights"].items() 
                           if data["total"] > 0}
        
        if active_categories:
            # Create data for horizontal bar chart
            categories = list(active_categories.keys())
            scores = [data["score"] for data in active_categories.values()]
            
            # Create colors based on scores
            colors = []
            for score in scores:
                if score >= 80:
                    colors.append('#4caf50')  # Green
                elif score >= 60:
                    colors.append('#ffb74d')  # Amber
                else:
                    colors.append('#f44336')  # Red
            
            # Create horizontal bar chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=categories,
                x=scores,
                orientation='h',
                marker_color=colors,
                text=[f"{s:.1f}%" for s in scores],
                textposition='auto'
            ))
            
            fig.update_layout(
                title="Security Category Scores",
                xaxis_title="Score (%)",
                xaxis=dict(range=[0, 100]),
                yaxis=dict(autorange="reversed"),
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                template="plotly_dark",
                paper_bgcolor='rgba(37, 50, 72, 0.0)',
                plot_bgcolor='rgba(37, 50, 72, 0.0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display findings for each category
            for category, data in active_categories.items():
                if data["findings"]:
                    with st.expander(f"{category} ({data['score']:.1f}%) - {len(data['findings'])} issues"):
                        for finding in data["findings"]:
                            st.markdown(f"**Question:** {finding['question_text']}")
                            st.markdown(f"**Response:** {finding['answer']}")
                            st.markdown(f"**Analysis:** {'Critical control gap' if finding['is_critical'] else 'Security gap'} " +
                                      f"(Confidence: {finding['confidence']:.0%})")
                            st.markdown("---")
        else:
            st.info("No category insights available. Please upload a questionnaire with valid responses.")