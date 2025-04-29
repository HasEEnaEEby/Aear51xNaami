import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import base64
from io import BytesIO

# Import our custom modules
# from compliance_knowledge_base import ComplianceKnowledgeBase
# from security_advisor_chatbot import SecurityAdvisorChatbot
# from risk_scoring_model import RiskScoringModel

class SecurityAdvisorUI:
    def __init__(self, chatbot=None, model=None, knowledge_base=None):
        """
        Initialize the Security Advisor UI
        
        Args:
            chatbot: SecurityAdvisorChatbot instance
            model: RiskScoringModel instance
            knowledge_base: ComplianceKnowledgeBase instance
        """
        self.chatbot = chatbot
        self.model = model
        self.knowledge_base = knowledge_base
        
        # Initialize session state variables
        if 'conversation' not in st.session_state:
            st.session_state.conversation = []
        
        if 'assessment' not in st.session_state:
            st.session_state.assessment = None
        
        if 'recommendations' not in st.session_state:
            st.session_state.recommendations = []
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'chat'
    
    def run(self):
        """Run the Streamlit app"""
        st.set_page_config(
            page_title="Security & Compliance Advisor",
            page_icon="🔒",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Apply custom CSS
        self._apply_custom_css()
        
        # Sidebar navigation
        self._render_sidebar()
        
        # Main content
        if st.session_state.current_page == 'chat':
            self._render_chat_page()
        elif st.session_state.current_page == 'dashboard':
            self._render_dashboard_page()
        elif st.session_state.current_page == 'questionnaire':
            self._render_questionnaire_page()
        elif st.session_state.current_page == 'frameworks':
            self._render_frameworks_page()
        elif st.session_state.current_page == 'settings':
            self._render_settings_page()
    
    def _apply_custom_css(self):
        """Apply custom CSS styling"""
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1E3A8A;
            margin-bottom: 1rem;
        }
        
        .sub-header {
            font-size: 1.8rem;
            font-weight: bold;
            color: #1E3A8A;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        
        .card {
            border-radius: 10px;
            padding: 1.5rem;
            background-color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }
        
        .risk-very-low {
            color: #059669;
            font-weight: bold;
        }
        
        .risk-low {
            color: #0284C7;
            font-weight: bold;
        }
        
        .risk-moderate {
            color: #D97706;
            font-weight: bold;
        }
        
        .risk-high {
            color: #DC2626;
            font-weight: bold;
        }
        
        .risk-critical {
            color: #7F1D1D;
            font-weight: bold;
        }
        
        .chat-message {
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 0.5rem;
            max-width: 80%;
        }
        
        .chat-message.user {
            background-color: #E0F2FE;
            margin-left: auto;
        }
        
        .chat-message.bot {
            background-color: #F3F4F6;
            margin-right: auto;
        }
        
        .recommendation-card {
            border-left: 4px solid #0284C7;
            padding: 1rem;
            background-color: #F0F9FF;
            margin-bottom: 0.5rem;
        }
        
        .recommendation-card.high-impact {
            border-left: 4px solid #DC2626;
        }
        
        .recommendation-card.medium-impact {
            border-left: 4px solid #D97706;
        }
        
        .recommendation-card.low-impact {
            border-left: 4px solid #059669;
        }
        
        .framework-card {
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 1rem;
            background-color: white;
            margin-bottom: 1rem;
            transition: all 0.2s;
        }
        
        .framework-card:hover {
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }
        
        .metric-card {
            text-align: center;
            padding: 1rem;
            border-radius: 8px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #6B7280;
        }
        
        /* Fix Streamlit UI elements */
        div.block-container {
            padding-top: 2rem;
        }
        
        div.stButton > button {
            width: 100%;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def _render_sidebar(self):
        """Render sidebar navigation"""
        with st.sidebar:
            st.image("https://via.placeholder.com/150x80?text=Security+Advisor", width=200)
            st.markdown("## Navigation")
            
            # Navigation buttons
            if st.button("💬 Chat", key="nav_chat"):
                st.session_state.current_page = 'chat'
                st.experimental_rerun()
            
            if st.button("📊 Risk Dashboard", key="nav_dashboard"):
                st.session_state.current_page = 'dashboard'
                st.experimental_rerun()
            
            if st.button("📋 Questionnaire", key="nav_questionnaire"):
                st.session_state.current_page = 'questionnaire'
                st.experimental_rerun()
            
            if st.button("📚 Frameworks", key="nav_frameworks"):
                st.session_state.current_page = 'frameworks'
                st.experimental_rerun()
            
            if st.button("⚙️ Settings", key="nav_settings"):
                st.session_state.current_page = 'settings'
                st.experimental_rerun()
            
            # Show assessment summary if available
            if st.session_state.assessment:
                st.markdown("---")
                st.markdown("### Current Assessment")
                
                risk_score = st.session_state.assessment.get('risk_score', 0)
                risk_level = st.session_state.assessment.get('risk_level', {}).get('name', 'Unknown')
                
                # Format risk level with color
                risk_class = risk_level.replace(' ', '-').lower()
                colored_risk = f'<span class="risk-{risk_class}">{risk_level.title()}</span>'
                
                st.markdown(f"Risk Score: **{risk_score:.1f}/100**", unsafe_allow_html=True)
                st.markdown(f"Risk Level: {colored_risk}", unsafe_allow_html=True)
                
                if st.button("View Full Report"):
                    st.session_state.current_page = 'dashboard'
                    st.experimental_rerun()
    
    def _render_chat_page(self):
        """Render chat interface page"""
        st.markdown('<h1 class="main-header">Security & Compliance Advisor</h1>', unsafe_allow_html=True)
        
        # Chat container
        chat_container = st.container()
        
        # Input container
        input_container = st.container()
        
        # Render chat messages
        with chat_container:
            for message in st.session_state.conversation:
                self._render_chat_message(message)
        
        # Input for new message
        with input_container:
            col1, col2 = st.columns([5, 1])
            
            with col1:
                user_input = st.text_input("Type your message...", key="chat_input")
            
            with col2:
                send_button = st.button("Send")
            
            # Process input when Send is clicked or Enter is pressed
            if send_button or (user_input and user_input != st.session_state.get('last_input', '')):
                if user_input:
                    # Save current input to avoid duplicate processing
                    st.session_state.last_input = user_input
                    
                    # Add user message to conversation
                    self._add_user_message(user_input)
                    
                    # Process with chatbot and add response
                    if self.chatbot:
                        response = self.chatbot.process_message(
                            user_input, 
                            user_id=st.session_state.get('user_id'),
                            organization_id=st.session_state.get('organization_id')
                        )
                        
                        self._add_bot_message(response['text'], response.get('data', {}))
                        
                        # Update assessment and recommendations if included in response
                        if 'risk_score' in response.get('data', {}):
                            st.session_state.assessment = response['data']
                        
                        if 'recommendations' in response.get('data', {}):
                            st.session_state.recommendations = response['data']['recommendations']
                    else:
                        # Dummy response if chatbot not available
                        self._add_bot_message("I'm just a demo right now. The real chatbot would process your message.")
                    
                    # Clear input
                    st.session_state.chat_input = ""
                    
                    # Rerun to update UI
                    st.experimental_rerun()
    
    def _render_chat_message(self, message):
        """
        Render a single chat message
        
        Args:
            message: Message dictionary with type, text, and optional data
        """
        message_type = message.get('type', 'bot')
        message_text = message.get('message', '')
        message_data = message.get('data', {})
        
        if message_type == 'user':
            st.markdown(f'<div class="chat-message user">{message_text}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message bot">{message_text}</div>', unsafe_allow_html=True)
            
            # Render any attached data visualizations
            if 'risk_score' in message_data:
                self._render_risk_score_card(message_data)
            
            if 'recommendations' in message_data and message_data['recommendations']:
                self._render_recommendations_preview(message_data['recommendations'][:3])
    
    def _render_risk_score_card(self, assessment_data):
        """
        Render risk score card
        
        Args:
            assessment_data: Assessment data dictionary
        """
        risk_score = assessment_data.get('risk_score', 0)
        risk_level = assessment_data.get('risk_level', {})
        risk_name = risk_level.get('name', 'Unknown')
        risk_color = risk_level.get('color', 'gray')
        
        # Format risk level with color
        risk_class = risk_name.replace(' ', '-').lower()
        
        st.markdown(f"""
        <div class="card">
            <h3>Security Risk Assessment</h3>
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div style="flex: 1; text-align: center;">
                    <div style="font-size: 3rem; font-weight: bold; color: #{risk_color};">{risk_score:.1f}</div>
                    <div style="font-size: 1.2rem;">out of 100</div>
                </div>
                <div style="flex: 2; padding-left: 1rem;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">Risk Level: <span class="risk-{risk_class}">{risk_name.title()}</span></div>
                    <div>{risk_level.get('description', '')}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_recommendations_preview(self, recommendations):
        """
        Render preview of recommendations
        
        Args:
            recommendations: List of recommendation dictionaries
        """
        if not recommendations:
            return
        
        st.markdown("<h4>Top Recommendations</h4>", unsafe_allow_html=True)
        
        for rec in recommendations:
            impact_class = "high-impact" if rec.get('impact') == "High" else (
                "medium-impact" if rec.get('impact') == "Medium" else "low-impact"
            )
            
            st.markdown(f"""
            <div class="recommendation-card {impact_class}">
                <div style="font-weight: bold;">{rec.get('title', 'Recommendation')}</div>
                <div style="margin-top: 0.5rem;">{rec.get('description', '')}</div>
                <div style="margin-top: 0.5rem; font-size: 0.8rem;">
                    <span style="margin-right: 1rem;">Impact: {rec.get('impact', 'Medium')}</span>
                    <span>Effort: {rec.get('effort', 'Medium')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_dashboard_page(self):
        """Render risk dashboard page"""
        st.markdown('<h1 class="main-header">Risk Assessment Dashboard</h1>', unsafe_allow_html=True)
        
        # Check if assessment is available
        if not st.session_state.assessment:
            st.warning("No risk assessment data available. Please complete the questionnaire or chat with the advisor to get a risk assessment.")
            
            if st.button("Go to Questionnaire"):
                st.session_state.current_page = 'questionnaire'
                st.experimental_rerun()
                
            return
        
        # Get assessment data
        assessment = st.session_state.assessment
        risk_score = assessment.get('risk_score', 0)
        risk_level = assessment.get('risk_level', {})
        explanation = assessment.get('explanation', {})
        recommendations = st.session_state.recommendations
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self._render_metric_card(
                "Risk Score", 
                f"{risk_score:.1f}", 
                "/100", 
                risk_level.get('color', '#6B7280')
            )
        
        with col2:
            risk_factors = len(explanation.get('top_factors', []))
            self._render_metric_card(
                "Risk Factors", 
                f"{risk_factors}", 
                "Identified", 
                "#1E40AF"
            )
        
        with col3:
            rec_count = len(recommendations)
            self._render_metric_card(
                "Recommendations", 
                f"{rec_count}", 
                "Actions", 
                "#059669"
            )
        
        with col4:
            # Calculate potential improvement
            potential_improvement = min(100, risk_score * 0.3)  # Simplified estimate
            self._render_metric_card(
                "Potential Improvement", 
                f"{potential_improvement:.1f}", 
                "Points", 
                "#D97706"
            )
        
        # Risk breakdown and recommendations
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown('<h2 class="sub-header">Risk Breakdown</h2>', unsafe_allow_html=True)
            
            # Risk factors chart
            if explanation.get('top_factors'):
                self._render_risk_factors_chart(explanation['top_factors'])
            
            # Risk categories chart
            categories = explanation.get('categories', {})
            if categories:
                self._render_risk_categories_chart(categories)
            
        with col2:
            st.markdown('<h2 class="sub-header">Prioritized Actions</h2>', unsafe_allow_html=True)
            
            if recommendations:
                self._render_recommendations_list(recommendations[:10])
            else:
                st.info("No recommendations available. Please chat with the advisor to get personalized recommendations.")
        
        # Compliance impact section
        st.markdown('<h2 class="sub-header">Compliance Impact</h2>', unsafe_allow_html=True)
        self._render_compliance_impact()
    
    def _render_metric_card(self, label, value, suffix, color):
        """
        Render a metric card
        
        Args:
            label: Metric label
            value: Metric value
            suffix: Text to show after value
            color: Color for the value
        """
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: {color};">{value}<span style="font-size: 1rem; color: #6B7280;">{suffix}</span></div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_risk_factors_chart(self, factors):
        """
        Render risk factors chart
        
        Args:
            factors: List of risk factors with impact values
        """
        # Prepare data
        factors = sorted(factors, key=lambda x: x['impact'])
        
        # Take top/bottom 5 factors
        display_factors = []
        
        # Add negative factors (ones that decrease risk)
        neg_factors = [f for f in factors if f['impact'] < 0]
        if neg_factors:
            display_factors.extend(neg_factors[:3])
        
        # Add positive factors (ones that increase risk)
        pos_factors = [f for f in factors if f['impact'] > 0]
        if pos_factors:
            display_factors.extend(pos_factors[-5:])
        
        # Create chart data
        labels = [f"{f['description'][:30]}..." if len(f['description']) > 30 else f['description'] for f in display_factors]
        values = [f['impact'] for f in display_factors]
        colors = ['#059669' if v < 0 else '#DC2626' for v in values]
        
        # Create Plotly horizontal bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=labels,
            x=values,
            orientation='h',
            marker_color=colors
        ))
        
        fig.update_layout(
            title="Top Risk Factors",
            xaxis_title="Impact on Risk Score",
            height=400,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_risk_categories_chart(self, categories):
        """
        Render risk categories chart
        
        Args:
            categories: Dictionary of risk categories with factors
        """
        # Calculate total impact by category
        category_impact = {}
        
        for category, factors in categories.items():
            total_impact = sum(f['impact'] for f in factors if f['impact'] > 0)
            if total_impact > 0:
                category_impact[category] = total_impact
        
        # Sort and prepare data
        sorted_categories = sorted(category_impact.items(), key=lambda x: x[1], reverse=True)
        
        # Take top 5 categories
        top_categories = sorted_categories[:5]
        
        labels = [c[0] for c in top_categories]
        values = [c[1] for c in top_categories]
        
        # Create Plotly pie chart
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.4,
            marker_colors=px.colors.qualitative.Set2
        )])
        
        fig.update_layout(
            title="Risk by Category",
            height=350,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_recommendations_list(self, recommendations):
        """
        Render recommendations list
        
        Args:
            recommendations: List of recommendation dictionaries
        """
        for i, rec in enumerate(recommendations):
            impact_class = "high-impact" if rec.get('impact') == "High" else (
                "medium-impact" if rec.get('impact') == "Medium" else "low-impact"
            )
            
            expander = st.expander(f"{i+1}. {rec.get('title', 'Recommendation')}")
            
            with expander:
                st.markdown(f"""
                <div class="recommendation-card {impact_class}" style="border-left-width: 8px;">
                    <div style="font-size: 1.1rem; font-weight: bold;">{rec.get('title', 'Recommendation')}</div>
                    <div style="margin-top: 0.8rem;">{rec.get('description', '')}</div>
                    <div style="margin-top: 1rem; display: flex; justify-content: space-between;">
                        <div>
                            <span style="font-weight: bold;">Impact:</span> {rec.get('impact', 'Medium')}
                        </div>
                        <div>
                            <span style="font-weight: bold;">Effort:</span> {rec.get('effort', 'Medium')}
                        </div>
                        <div>
                            <span style="font-weight: bold;">Category:</span> {rec.get('category', 'General')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    def _render_compliance_impact(self):
        """Render compliance impact section"""
        # Example compliance frameworks
        frameworks = ["ISO 27001", "NIST 800-53", "HIPAA", "GDPR", "PCI DSS"]
        
        # Example coverage percentages (would come from actual assessment)
        coverage = [65, 78, 42, 59, 71]
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Create horizontal bar chart for compliance coverage
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=coverage,
                y=frameworks,
                orientation='h',
                marker_color='#1E40AF',
                text=[f"{c}%" for c in coverage],
                textposition='auto'
            ))
            
            fig.update_layout(
                title="Compliance Coverage",
                xaxis_title="Coverage Percentage",
                xaxis=dict(
                    tickmode='array',
                    tickvals=[0, 25, 50, 75, 100],
                    range=[0, 100]
                ),
                height=300,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("""
            <div class="card">
                <h3>Compliance Gap Analysis</h3>
                <p>The chart shows your estimated compliance coverage based on your risk assessment. This is not a full compliance audit but provides an indication of how well your security controls align with major frameworks.</p>
                <p>For a detailed compliance assessment, consider using the chatbot to explore specific requirements.</p>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_questionnaire_page(self):
        """Render questionnaire page"""
        st.markdown('<h1 class="main-header">Security Assessment Questionnaire</h1>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <h3>Instructions</h3>
            <p>Complete this security questionnaire to receive a comprehensive risk assessment and tailored recommendations. Your responses will be used to evaluate your organization's security posture across multiple dimensions.</p>
            <p>Answer each question as accurately as possible. The more complete your responses, the more accurate your risk assessment will be.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create tabs for different questionnaire sections
        tabs = st.tabs([
            "General Information", 
            "Access Controls", 
            "Data Protection",
            "Network Security",
            "Incident Response",
            "Vendor Management"
        ])
        
        with tabs[0]:
            self._render_general_section()
        
        with tabs[1]:
            self._render_access_section()
        
        with tabs[2]:
            self._render_data_section()
        
        with tabs[3]:
            self._render_network_section()
        
        with tabs[4]:
            self._render_incident_section()
        
        with tabs[5]:
            self._render_vendor_section()
        
        # Submit button
        if st.button("Submit Questionnaire", type="primary"):
            self._process_questionnaire()
    
    def _render_general_section(self):
        """Render general information section of questionnaire"""
        st.markdown('<h2 class="sub-header">General Information</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Organization Name", key="org_name")
            st.text_input("Industry", key="industry")
            st.number_input("Number of Employees", min_value=1, key="employee_count")
        
        with col2:
            st.selectbox("Geographic Regions of Operation", 
                        ["North America", "Europe", "Asia-Pacific", "Latin America", "Global"],
                        key="regions")
            st.selectbox("Regulatory Frameworks Applicable", 
                        ["GDPR", "HIPAA", "PCI DSS", "SOX", "CCPA", "Multiple", "None"],
                        key="frameworks")
            st.selectbox("Security Team Size", 
                        ["No dedicated team", "1-5 people", "6-15 people", "16+ people"],
                        key="security_team_size")
    
    def _render_access_section(self):
        """Render access controls section of questionnaire"""
        st.markdown('<h2 class="sub-header">Access Controls</h2>', unsafe_allow_html=True)
        
        # MFA Question
        st.selectbox(
            "Do you enforce multi-factor authentication (MFA)?",
            ["Not implemented", "For privileged users only", "For all employees", "For all users including third parties"],
            key="mfa_status"
        )
        
        # Password Policy
        st.selectbox(
            "What is your password policy?",
            ["Basic (8+ characters)", "Medium (10+ chars, mixed case)", "Strong (12+ chars, mixed case, symbols, numbers)", "Very strong (14+ chars with complexity)"],
            key="password_policy"
        )
        
        # Privileged Access
        st.selectbox(
            "How do you manage privileged access?",
            ["No specific management", "Manual tracking", "PAM solution for some systems", "Comprehensive PAM with monitoring"],
            key="privileged_access"
        )
        
        # Access Reviews
        st.selectbox(
            "How often do you perform access reviews?",
            ["Never/ad hoc", "Annually", "Quarterly", "Monthly", "Continuous monitoring"],
            key="access_reviews"
        )
    
    def _render_data_section(self):
        """Render data protection section of questionnaire"""
        st.markdown('<h2 class="sub-header">Data Protection</h2>', unsafe_allow_html=True)
        
        # Data Classification
        st.selectbox(
            "Do you have a data classification policy?",
            ["No formal classification", "Basic classification exists but not enforced", "Classification implemented for sensitive data", "Comprehensive classification enforced for all data"],
            key="data_classification"
        )
        
        # Encryption
        st.selectbox(
            "How is encryption deployed in your environment?",
            ["Minimal/ad hoc encryption", "Encryption for some sensitive data", "Encryption for all sensitive data at rest and in transit", "End-to-end encryption for all data"],
            key="encryption_status"
        )
        
        # Data Loss Prevention
        st.selectbox(
            "Do you use Data Loss Prevention (DLP) solutions?",
            ["No DLP implementation", "Basic DLP for email only", "DLP for email and endpoints", "Comprehensive DLP across all channels"],
            key="dlp_status"
        )
        
        # Data Retention
        st.selectbox(
            "Do you have a data retention and disposal policy?",
            ["No formal policy", "Policy exists but not enforced", "Policy with manual enforcement", "Automated enforcement of retention policies"],
            key="data_retention"
        )
    
    def _render_network_section(self):
        """Render network security section of questionnaire"""
        st.markdown('<h2 class="sub-header">Network Security</h2>', unsafe_allow_html=True)
        
        # Network Segmentation
        st.selectbox(
            "How is your network segmented?",
            ["Minimal/no segmentation", "Basic segmentation (e.g., IT vs OT)", "Moderate segmentation by department/function", "Zero trust architecture/microsegmentation"],
            key="network_segmentation"
        )
        
        # Firewall Management
        st.selectbox(
            "How do you manage firewalls and access control lists?",
            ["Basic firewall configuration", "Regular but manual reviews", "Change management process with reviews", "Automated policy management and continuous monitoring"],
            key="firewall_management"
        )
        
        # Vulnerability Scanning
        st.selectbox(
            "How often do you perform vulnerability scanning?",
            ["Ad hoc or never", "Annually", "Quarterly", "Monthly", "Continuous/automated scanning"],
            key="vuln_scanning"
        )
        
        # Patch Management
        st.selectbox(
            "What is your patch management approach?",
            ["Ad hoc patching", "Regular but manual patching", "Scheduled patching with SLAs", "Automated patch management with verification"],
            key="patch_management"
        )
    
    def _render_incident_section(self):
        """Render incident response section of questionnaire"""
        st.markdown('<h2 class="sub-header">Incident Response</h2>', unsafe_allow_html=True)
        
        # Incident Response Plan
        st.selectbox(
            "Do you have an incident response plan?",
            ["No formal plan", "Basic plan but not tested", "Documented plan with annual testing", "Comprehensive plan with regular exercises"],
            key="ir_plan"
        )
        
        # Security Monitoring
        st.selectbox(
            "What security monitoring capabilities do you have?",
            ["Minimal/ad hoc monitoring", "Basic logging without 24/7 monitoring", "SIEM solution with business hours monitoring", "24/7 SOC with advanced analytics"],
            key="security_monitoring"
        )
        
        # Breach Response
        st.selectbox(
            "How quickly can you respond to security incidents?",
            ["No defined SLAs", "Within 24 hours for critical systems", "Within 8 hours for critical systems", "Within 1 hour with automated containment"],
            key="breach_response"
        )
        
        # Forensic Capabilities
        st.selectbox(
            "What forensic capabilities do you have?",
            ["No forensic capabilities", "Basic log review capabilities", "Some forensic tools and training", "Advanced forensics team and tools"],
            key="forensic_capabilities"
        )
    
    def _render_vendor_section(self):
        """Render vendor management section of questionnaire"""
        st.markdown('<h2 class="sub-header">Vendor Management</h2>', unsafe_allow_html=True)
        
        # Vendor Risk Assessment
        st.selectbox(
            "How do you assess vendor security?",
            ["No formal assessment", "Basic security questionnaire", "Detailed assessment for critical vendors", "Comprehensive assessments with ongoing monitoring"],
            key="vendor_assessment"
        )
        
        # Vendor Contracts
        st.selectbox(
            "Do your vendor contracts include security requirements?",
            ["Minimal security language", "Basic security requirements", "Detailed requirements with right-to-audit", "Comprehensive requirements with regular verification"],
            key="vendor_contracts"
        )
        
        # Third-Party Access
        st.selectbox(
            "How do you manage third-party access to your systems?",
            ["Same as employee access", "Some restrictions for third parties", "Limited access with additional controls", "Just-in-time access with comprehensive monitoring"],
            key="third_party_access"
        )
        
        # Vendor Incidents
        st.selectbox(
            "How do you handle vendor security incidents?",
            ["No specific process", "Basic notification requirements", "Formal process for critical vendors", "Comprehensive incident management with all vendors"],
            key="vendor_incidents"
        )
    
    def _process_questionnaire(self):
        """Process submitted questionnaire"""
        # Collect all answers from session state
        questionnaire_data = {}
        
        for key in st.session_state:
            if key.startswith("org_") or key in [
                "industry", "employee_count", "regions", "frameworks", "security_team_size",
                "mfa_status", "password_policy", "privileged_access", "access_reviews",
                "data_classification", "encryption_status", "dlp_status", "data_retention",
                "network_segmentation", "firewall_management", "vuln_scanning", "patch_management",
                "ir_plan", "security_monitoring", "breach_response", "forensic_capabilities",
                "vendor_assessment", "vendor_contracts", "third_party_access", "vendor_incidents"
            ]:
                questionnaire_data[key] = st.session_state[key]
        
        # Process with chatbot if available
        if self.chatbot:
            result = self.chatbot.start_assessment(questionnaire_data)
            st.success("Questionnaire submitted successfully. Your risk assessment is ready.")
            
            # Perform initial assessment
            response = self.chatbot.process_message("Assess my security risk based on the questionnaire")
            
            # Update assessment and recommendations
            if 'risk_score' in response.get('data', {}):
                st.session_state.assessment = response['data']
            
            if 'recommendations' in response.get('data', {}):
                st.session_state.recommendations = response['data']['recommendations']
            
            # Navigate to dashboard
            st.session_state.current_page = 'dashboard'
            st.experimental_rerun()
        else:
            # Demo mode - generate dummy assessment
            risk_score = np.random.randint(40, 80)
            risk_level = self._get_risk_level(risk_score)
            
            st.session_state.assessment = {
                'risk_score': risk_score,
                'risk_level': risk_level,
                'explanation': self._generate_dummy_explanation(),
                'timestamp': datetime.now().isoformat()
            }
            
            # Generate dummy recommendations
            st.session_state.recommendations = self._generate_dummy_recommendations()
            
            st.success("Questionnaire submitted successfully. Your risk assessment is ready.")
            
            # Navigate to dashboard
            st.session_state.current_page = 'dashboard'
            st.experimental_rerun()
    
    def _get_risk_level(self, score):
        """Convert score to risk level dictionary"""
        if score < 20:
            return {
                'name': 'very low risk',
                'description': 'Your security posture is excellent with minimal areas for improvement.',
                'color': 'green'
            }
        elif score < 40:
            return {
                'name': 'low risk',
                'description': 'Your security posture is good with a few minor areas for improvement.',
                'color': 'blue'
            }
        elif score < 60:
            return {
                'name': 'moderate risk',
                'description': 'Your security posture needs attention in several key areas.',
                'color': 'yellow'
            }
        elif score < 80:
            return {
                'name': 'high risk',
                'description': 'Your security posture has significant vulnerabilities that need immediate attention.',
                'color': 'orange'
            }
        else:
            return {
                'name': 'critical risk',
                'description': 'Your security posture has critical vulnerabilities requiring urgent remediation.',
                'color': 'red'
            }
    
    def _generate_dummy_explanation(self):
        """Generate dummy explanation data for demo purposes"""
        # Sample factors
        factors = [
            {
                'feature': 'mfa_status',
                'description': 'Multi-factor authentication not fully implemented',
                'impact': 8.2,
                'direction': 'negative'
            },
            {
                'feature': 'password_policy',
                'description': 'Weak password policy',
                'impact': 6.5,
                'direction': 'negative'
            },
            {
                'feature': 'patch_management',
                'description': 'Irregular patch management',
                'impact': 5.9,
                'direction': 'negative'
            },
            {
                'feature': 'security_monitoring',
                'description': 'Limited security monitoring',
                'impact': 4.3,
                'direction': 'negative'
            },
            {
                'feature': 'vendor_assessment',
                'description': 'Minimal vendor security assessment',
                'impact': 3.8,
                'direction': 'negative'
            },
            {
                'feature': 'ir_plan',
                'description': 'Basic incident response plan',
                'impact': 2.7,
                'direction': 'negative'
            },
            {
                'feature': 'encryption_status',
                'description': 'Good encryption practices',
                'impact': -3.2,
                'direction': 'positive'
            },
            {
                'feature': 'access_reviews',
                'description': 'Regular access reviews',
                'impact': -2.8,
                'direction': 'positive'
            }
        ]
        
        # Organize by category
        categories = {
            'Access Control': [f for f in factors if f['feature'] in ['mfa_status', 'password_policy', 'access_reviews']],
            'Data Protection': [f for f in factors if f['feature'] in ['encryption_status', 'dlp_status', 'data_retention']],
            'Network Security': [f for f in factors if f['feature'] in ['network_segmentation', 'firewall_management', 'vuln_scanning', 'patch_management']],
            'Incident Response': [f for f in factors if f['feature'] in ['ir_plan', 'security_monitoring', 'breach_response', 'forensic_capabilities']],
            'Vendor Management': [f for f in factors if f['feature'] in ['vendor_assessment', 'vendor_contracts', 'third_party_access', 'vendor_incidents']]
        }
        
        return {
            'top_factors': factors,
            'categories': categories
        }
    
    def _generate_dummy_recommendations(self):
        """Generate dummy recommendations for demo purposes"""
        recommendations = [
            {
                'title': 'Implement Multi-Factor Authentication',
                'description': 'Deploy MFA for all users, especially those with privileged access. This will significantly reduce the risk of unauthorized access due to compromised credentials.',
                'category': 'Access Control',
                'impact': 'High',
                'effort': 'Medium',
                'source': 'template'
            },
            {
                'title': 'Strengthen Password Policy',
                'description': 'Update your password policy to require longer passwords (14+ characters) with complexity requirements. Implement a password manager to help users maintain strong, unique passwords.',
                'category': 'Access Control',
                'impact': 'High',
                'effort': 'Low',
                'source': 'template'
            },
            {
                'title': 'Improve Patch Management',
                'description': 'Implement an automated patch management system with defined SLAs for critical, high, medium, and low vulnerabilities. Establish a verification process to ensure patches are applied successfully.',
                'category': 'Network Security',
                'impact': 'High',
                'effort': 'High',
                'source': 'template'
            },
            {
                'title': 'Enhance Security Monitoring',
                'description': 'Upgrade your security monitoring capabilities with a SIEM solution and 24/7 coverage. Implement automated alerting for critical security events and establish an escalation process.',
                'category': 'Incident Response',
                'impact': 'Medium',
                'effort': 'High',
                'source': 'template'
            },
            {
                'title': 'Formalize Vendor Risk Assessment',
                'description': 'Develop a comprehensive vendor risk assessment process that includes initial vetting, ongoing monitoring, and regular reassessment. Prioritize vendors based on data access and business criticality.',
                'category': 'Vendor Management',
                'impact': 'Medium',
                'effort': 'Medium',
                'source': 'template'
            },
            {
                'title': 'Test Incident Response Plan',
                'description': 'Conduct regular tabletop exercises and simulations of your incident response plan. Include scenarios specific to your industry and infrastructure. Document lessons learned and update the plan accordingly.',
                'category': 'Incident Response',
                'impact': 'Medium',
                'effort': 'Medium',
                'source': 'template'
            },
            {
                'title': 'Implement Data Loss Prevention',
                'description': 'Deploy a DLP solution to monitor and protect sensitive data across endpoints, networks, and cloud services. Start with high-risk channels like email and gradually expand coverage.',
                'category': 'Data Protection',
                'impact': 'Medium',
                'effort': 'High',
                'source': 'template'
            },
            {
                'title': 'Segment Network by Function',
                'description': 'Implement network segmentation based on security requirements and data sensitivity. Use firewalls, VLANs, and access controls to restrict lateral movement within the network.',
                'category': 'Network Security',
                'impact': 'High',
                'effort': 'High',
                'source': 'template'
            }
        ]
        
        return recommendations
    
    def _render_frameworks_page(self):
        """Render compliance frameworks page"""
        st.markdown('<h1 class="main-header">Compliance Frameworks</h1>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <h3>Understanding Compliance Frameworks</h3>
            <p>Compliance frameworks provide structured approaches to security, privacy, and risk management. They help organizations establish controls and processes to protect information assets and meet regulatory requirements.</p>
            <p>Explore the common frameworks below to better understand their scope, requirements, and how they might apply to your organization.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create columns for framework cards
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_framework_card(
                "ISO/IEC 27001",
                "International standard for information security management systems (ISMS). Provides a systematic approach to managing sensitive information.",
                ["Information Security Management", "Risk Assessment", "Security Policy", "Asset Management", "Access Control"],
                ["Financial Services", "Healthcare", "Technology", "Government"],
                "global"
            )
            
            self._render_framework_card(
                "NIST Cybersecurity Framework",
                "Voluntary framework consisting of standards, guidelines, and best practices to manage cybersecurity risk.",
                ["Identify", "Protect", "Detect", "Respond", "Recover"],
                ["Critical Infrastructure", "Government", "Financial Services", "Healthcare"],
                "us"
            )
            
            self._render_framework_card(
                "HIPAA",
                "Health Insurance Portability and Accountability Act sets standards for protecting sensitive patient health information.",
                ["Privacy Rule", "Security Rule", "Breach Notification Rule", "Patient Rights", "Administrative Safeguards"],
                ["Healthcare Providers", "Health Plans", "Healthcare Clearinghouses", "Business Associates"],
                "us"
            )
            
            self._render_framework_card(
                "PCI DSS",
                "Payment Card Industry Data Security Standard is a set of security standards for organizations that handle credit card information.",
                ["Secure Network", "Cardholder Data Protection", "Vulnerability Management", "Access Control", "Monitoring and Testing"],
                ["Retail", "E-commerce", "Financial Services", "Hospitality"],
                "global"
            )
        
        with col2:
            self._render_framework_card(
                "GDPR",
                "General Data Protection Regulation is a regulation on data protection and privacy in the European Union and the European Economic Area.",
                ["Lawful Processing", "Consent", "Data Subject Rights", "Privacy by Design", "Data Protection Officer"],
                ["Any organization handling EU citizen data", "Online Services", "Multinational Corporations"],
                "eu"
            )
            
            self._render_framework_card(
                "SOC 2",
                "Service Organization Control 2 is a framework for service organizations to demonstrate their controls relevant to security, availability, processing integrity, confidentiality, and privacy.",
                ["Security", "Availability", "Processing Integrity", "Confidentiality", "Privacy"],
                ["SaaS Providers", "Cloud Services", "Data Centers", "Managed Services"],
                "us"
            )
            
            self._render_framework_card(
                "CCPA/CPRA",
                "California Consumer Privacy Act/California Privacy Rights Act gives California residents certain rights regarding their personal information.",
                ["Right to Know", "Right to Delete", "Right to Opt-Out", "Right to Non-Discrimination", "Data Protection"],
                ["Any business serving California residents", "Online Services", "Retail", "Marketing"],
                "us-ca"
            )
            
            self._render_framework_card(
                "NIST 800-53",
                "Security and Privacy Controls for Federal Information Systems and Organizations provides a catalog of security and privacy controls.",
                ["Access Control", "Awareness and Training", "Audit and Accountability", "Configuration Management", "Incident Response"],
                ["Federal Agencies", "Government Contractors", "Critical Infrastructure"],
                "us"
            )
    
    def _render_framework_card(self, title, description, key_controls, industries, region):
        """
        Render a compliance framework card
        
        Args:
            title: Framework title
            description: Framework description
            key_controls: List of key control categories
            industries: List of applicable industries
            region: Region code (global, us, eu, etc.)
        """
        # Map region to emoji flag
        region_emoji = {
            "global": "🌎",
            "us": "🇺🇸",
            "eu": "🇪🇺",
            "uk": "🇬🇧",
            "us-ca": "🇺🇸 (CA)"
        }
        
        flag = region_emoji.get(region, "")
        
        st.markdown(f"""
        <div class="framework-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3>{title}</h3>
                <div>{flag}</div>
            </div>
            <p>{description}</p>
            <div style="margin-top: 1rem;">
                <div style="font-weight: bold;">Key Control Categories:</div>
                <ul style="margin-top: 0.5rem; padding-left: 1.5rem;">
        """, unsafe_allow_html=True)
        
        for control in key_controls:
            st.markdown(f"<li>{control}</li>", unsafe_allow_html=True)
        
        st.markdown("""
                </ul>
            </div>
            <div style="margin-top: 1rem;">
                <div style="font-weight: bold;">Commonly Applied In:</div>
                <div style="margin-top: 0.5rem;">
        """, unsafe_allow_html=True)
        
        for industry in industries:
            st.markdown(f"<span style='background-color: #E0F2FE; padding: 0.2rem 0.5rem; border-radius: 4px; margin-right: 0.5rem; font-size: 0.9rem;'>{industry}</span>", unsafe_allow_html=True)
        
        st.markdown("""
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_settings_page(self):
        """Render settings page"""
        st.markdown('<h1 class="main-header">Settings</h1>', unsafe_allow_html=True)
        
        # Create tabs for different settings sections
        tabs = st.tabs(["Profile", "Notification Preferences", "Data Management", "Integrations"])
        
        with tabs[0]:
            self._render_profile_settings()
        
        with tabs[1]:
            self._render_notification_settings()
        
        with tabs[2]:
            self._render_data_settings()
        
        with tabs[3]:
            self._render_integration_settings()
    
    def _render_profile_settings(self):
        """Render profile settings section"""
        st.markdown('<h2 class="sub-header">Profile Settings</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Organization Name", value=st.session_state.get("org_name", ""), key="settings_org_name")
            st.text_input("Your Name", value=st.session_state.get("user_name", ""), key="settings_user_name")
            st.text_input("Email Address", value=st.session_state.get("user_email", ""), key="settings_user_email")
        
        with col2:
            st.selectbox("Industry", 
                       ["Financial Services", "Healthcare", "Manufacturing", "Retail", "Technology", "Government", "Education", "Other"],
                       index=0 if not st.session_state.get("industry") else 0,
                       key="settings_industry")
            
            st.selectbox("Organization Size", 
                       ["1-50 employees", "51-250 employees", "251-1000 employees", "1001-5000 employees", "5001+ employees"],
                       key="settings_org_size")
            
            st.selectbox("Primary Compliance Framework", 
                       ["ISO 27001", "NIST CSF", "HIPAA", "GDPR", "PCI DSS", "SOC 2", "Other"],
                       key="settings_primary_framework")
        
        if st.button("Save Profile Settings"):
            # Save settings to session state
            st.session_state.org_name = st.session_state.settings_org_name
            st.session_state.user_name = st.session_state.settings_user_name
            st.session_state.user_email = st.session_state.settings_user_email
            st.session_state.industry = st.session_state.settings_industry
            st.session_state.org_size = st.session_state.settings_org_size
            st.session_state.primary_framework = st.session_state.settings_primary_framework
            
            st.success("Profile settings saved successfully!")
    
    def _render_notification_settings(self):
        """Render notification settings section"""
        st.markdown('<h2 class="sub-header">Notification Preferences</h2>', unsafe_allow_html=True)
        
        st.checkbox("Email notifications for assessment reports", value=True, key="notify_reports")
        st.checkbox("Email notifications for security recommendations", value=True, key="notify_recommendations")
        st.checkbox("Email notifications for framework updates", value=False, key="notify_frameworks")
        st.checkbox("Email notifications for risk score changes", value=True, key="notify_risk_changes")
        
        st.markdown("### Notification Frequency")
        st.radio("Assessment reminders", ["Never", "Monthly", "Quarterly", "Annually"], index=2, key="remind_frequency")
        
        if st.button("Save Notification Settings"):
            st.success("Notification preferences saved successfully!")
    
    def _render_data_settings(self):
        """Render data management settings section"""
        st.markdown('<h2 class="sub-header">Data Management</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <h3>Data Retention</h3>
            <p>Control how long your assessment data and chat history are retained.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.selectbox("Assessment Data Retention", 
                   ["3 months", "6 months", "1 year", "2 years", "Until manually deleted"],
                   index=2,
                   key="assessment_retention")
        
        st.selectbox("Chat History Retention", 
                   ["30 days", "90 days", "1 year", "Until manually deleted"],
                   index=1,
                   key="chat_retention")
        
        st.markdown("### Data Export")
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            st.button("Export Assessment Reports (CSV)")
        
        with export_col2:
            st.button("Export Chat History (JSON)")
        
        st.markdown("### Data Deletion")
        st.warning("The following actions cannot be undone.")
        
        delete_col1, delete_col2 = st.columns(2)
        
        with delete_col1:
            st.button("Clear Chat History")
        
        with delete_col2:
            st.button("Delete All Assessment Data")
    
    def _render_integration_settings(self):
        """Render integration settings section"""
        st.markdown('<h2 class="sub-header">Integrations</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <h3>Available Integrations</h3>
            <p>Connect the Security Advisor to your existing security tools and platforms to enhance risk assessment and automate data collection.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Security Tools Integrations
        st.markdown("### Security Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("Vulnerability Scanner Integration", key="vuln_scanner_integration")
            st.text_input("API Endpoint", placeholder="https://", key="vuln_scanner_api")
            st.text_input("API Key", type="password", key="vuln_scanner_key")
        
        with col2:
            st.checkbox("SIEM Integration", key="siem_integration")
            st.text_input("SIEM API Endpoint", placeholder="https://", key="siem_api")
            st.text_input("SIEM API Key", type="password", key="siem_key")
        
        # Compliance Platform Integrations
        st.markdown("### Compliance Platforms")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("GRC Platform Integration", key="grc_integration")
            st.selectbox("GRC Platform", ["MetricStream", "Archer", "ServiceNow", "Other"], key="grc_platform")
            st.text_input("GRC API Key", type="password", key="grc_key")
        
        with col2:
            st.checkbox("Audit Management Integration", key="audit_integration")
            st.selectbox("Audit Platform", ["AuditBoard", "Workiva", "MetricStream", "Other"], key="audit_platform")
            st.text_input("Audit API Key", type="password", key="audit_key")
        
        if st.button("Save Integration Settings"):
            st.success("Integration settings saved successfully!")
    
    def _add_user_message(self, message):
        """
        Add user message to conversation history
        
        Args:
            message: User message text
        """
        st.session_state.conversation.append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'type': 'user'
        })
    
    def _add_bot_message(self, message, data=None):
        """
        Add bot message to conversation history
        
        Args:
            message: Bot message text
            data: Optional data dictionary
        """
        st.session_state.conversation.append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'type': 'bot',
            'data': data or {}
        })


# Example usage
if __name__ == "__main__":
    # Initialize UI
    ui = SecurityAdvisorUI()

    ui.run()