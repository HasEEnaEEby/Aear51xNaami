"""
Dashboard page for Security Compliance Advisor
This page displays the risk assessment results and recommendations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import altair as alt

def render_dashboard_page():
    """Render the dashboard page"""
    st.title("Risk Assessment Dashboard")
    
    # Initialize session state
    if "frameworks" not in st.session_state:
        st.session_state.frameworks = {
            "iso27001": {"name": "ISO/IEC 27001", "description": "International standard for information security management", "coverage": 0},
            "nist_csf": {"name": "NIST Cybersecurity Framework", "description": "Framework for improving critical infrastructure cybersecurity", "coverage": 0},
            "gdpr": {"name": "GDPR", "description": "EU regulation on data protection and privacy", "coverage": 0},
            "hipaa": {"name": "HIPAA", "description": "US healthcare privacy and security regulation", "coverage": 0},
            "pci_dss": {"name": "PCI DSS", "description": "Payment card industry security standard", "coverage": 0},
            "ccpa": {"name": "CCPA", "description": "California Consumer Privacy Act", "coverage": 0},
            "cis": {"name": "CIS Controls", "description": "Critical security controls for cyber defense", "coverage": 0},
            "hitrust": {"name": "HITRUST CSF", "description": "Healthcare industry security framework", "coverage": 0}
        }
    
    if "assessment" not in st.session_state:
        st.session_state.assessment = None
        
    if "recommendations" not in st.session_state:
        st.session_state.recommendations = []
    
    # Check if assessment data is available
    assessment = st.session_state.assessment
    
    if not assessment:
        # Display instructions if no assessment data
        st.info("No risk assessment data available yet. Please upload and analyze a security questionnaire first.")
        
        if st.button("Go to Questionnaire Page"):
            st.session_state.current_page = 'upload'
            st.experimental_rerun()
            
        # Display demo data option
        st.markdown("---")
        st.subheader("Want to see a demo?")
        
        if st.button("Load Demo Data"):
            _load_demo_data()
            st.experimental_rerun()
            
        return
    
    # If we have assessment data, show the dashboard
    assessment_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Get risk level and score
    risk_level = assessment.get('risk_level', 'Unknown')
    risk_score = assessment.get('risk_score', 0)
    
    # Display risk summary
    st.markdown(f"## Overall Security Posture: <span style='color:{_get_risk_color(risk_level)};'>{risk_level} Risk</span>", unsafe_allow_html=True)
    
    # Display assessment summary
    assessment_summary = assessment.get('assessment_summary', '')
    if assessment_summary:
        st.markdown(assessment_summary)
    
    # Create metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Risk Score", 
            f"{risk_score:.1f}%", 
            delta=None,
            delta_color="inverse"
        )
        
    with col2:
        # Get top framework compliance
        framework_scores = [
            (framework_id, data.get('compliance_score', 0))
            for framework_id, data in assessment.get('framework_compliance', {}).items()
        ]
        
        if framework_scores:
            # Sort by score (highest first)
            framework_scores.sort(key=lambda x: x[1], reverse=True)
            top_framework_id, top_framework_score = framework_scores[0]
            
            # Format framework name
            framework_name = top_framework_id.upper()
            if top_framework_id == 'nist_csf':
                framework_name = 'NIST CSF'
            elif top_framework_id == 'iso27001':
                framework_name = 'ISO 27001'
            
            st.metric(
                f"Top Framework Compliance ({framework_name})",
                f"{top_framework_score:.1f}%",
                delta=None
            )
        else:
            st.metric(
                "Framework Compliance",
                "N/A",
                delta=None
            )
        
    with col3:
        # Count high-risk domains
        domain_scores = assessment.get('domain_scores', {})
        high_risk_count = sum(1 for domain, data in domain_scores.items() 
                             if data.get('risk_level') == 'High')
        
        st.metric(
            "High Risk Domains",
            f"{high_risk_count}",
            delta=None,
            delta_color="inverse"
        )
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Risk Analysis", "Compliance", "Recommendations"])
    
    with tab1:
        _render_risk_analysis_tab(assessment)
        
    with tab2:
        _render_compliance_tab(assessment)
        
    with tab3:
        _render_recommendations_tab(st.session_state.recommendations)
    
    # Add option to clear data
    st.markdown("---")
    if st.button("Clear Assessment Data"):
        st.session_state.assessment = None
        st.session_state.recommendations = []
        st.experimental_rerun()


def _render_risk_analysis_tab(assessment):
    """
    Render the risk analysis tab
    
    Args:
        assessment: Risk assessment data
    """
    st.subheader("Domain Risk Analysis")
    
    # Get domain scores
    domain_scores = assessment.get('domain_scores', {})
    
    if not domain_scores:
        st.warning("No domain risk data available.")
        return
    
    # Create domain risk dataframe
    domain_data = []
    
    for domain, data in domain_scores.items():
        # Skip 'uncategorized' domain
        if domain == 'uncategorized':
            continue
            
        # Format domain name for display
        domain_name = domain.replace('_', ' ').title()
        
        domain_data.append({
            'Domain': domain_name,
            'Score': data.get('score', 0),
            'Risk Level': data.get('risk_level', 'Unknown'),
            'Weight': data.get('weight', 0.05) * 100  # Convert to percentage
        })
    
    # Sort by score (lowest first)
    domain_df = pd.DataFrame(domain_data)
    domain_df = domain_df.sort_values('Score')
    
    # Create domain risk chart
    if not domain_df.empty:
        chart = alt.Chart(domain_df).mark_bar().encode(
            x=alt.X('Score', title='Score (%)'),
            y=alt.Y('Domain', sort='-x', title=None),
            color=alt.Color('Risk Level', 
                         scale=alt.Scale(
                             domain=['High', 'Medium', 'Low'],
                             range=['#f63366', '#ffbd45', '#00cc96']
                         )),
            tooltip=['Domain', 'Score', 'Risk Level', 'Weight']
        ).properties(
            height=300
        )
        
        st.altair_chart(chart, use_container_width=True)
    
    # Display top risk domains
    st.subheader("Top Risk Areas")
    
    top_risk_domains = assessment.get('top_risk_domains', [])
    
    if top_risk_domains:
        for i, domain_info in enumerate(top_risk_domains):
            domain = domain_info.get('domain', '')
            risk_level = domain_info.get('risk_level', 'Unknown')
            score = domain_info.get('score', 0)
            
            # Format domain name
            domain_name = domain.replace('_', ' ').title()
            
            # Display in expander
            with st.expander(f"{i+1}. {domain_name} - {risk_level} Risk ({score:.1f}%)"):
                # Find specific security gaps for this domain
                security_gaps = assessment.get('security_gaps', [])
                domain_gaps = [gap for gap in security_gaps if gap.get('category') == domain]
                
                if domain_gaps:
                    gap = domain_gaps[0]  # Take first gap
                    
                    # Display negative responses
                    negative_responses = gap.get('negative_responses', [])
                    
                    if negative_responses:
                        st.markdown("**Key Issues:**")
                        
                        for j, response in enumerate(negative_responses[:5]):  # Show top 5
                            question = response.get('question', '')
                            st.markdown(f"- {question}")
                else:
                    st.write("No specific issues identified for this domain.")
    else:
        st.info("No specific risk areas identified.")


def _render_compliance_tab(assessment):
    """
    Render the compliance tab
    
    Args:
        assessment: Risk assessment data
    """
    st.subheader("Compliance Framework Coverage")
    
    # Get framework compliance data
    framework_compliance = assessment.get('framework_compliance', {})
    
    if not framework_compliance:
        st.warning("No compliance data available.")
        return
    
    # Create framework compliance dataframe
    framework_data = []
    
    for framework_id, data in framework_compliance.items():
        # Get framework name
        framework_name = framework_id.upper()
        if framework_id == 'nist_csf':
            framework_name = 'NIST CSF'
        elif framework_id == 'iso27001':
            framework_name = 'ISO 27001'
        
        # Get compliance score
        compliance_score = data.get('compliance_score', 0)
        
        # Update session state frameworks
        if framework_id in st.session_state.frameworks:
            st.session_state.frameworks[framework_id]['coverage'] = compliance_score
        
        # Get gap areas
        gap_areas = data.get('gap_areas', [])
        
        framework_data.append({
            'Framework': framework_name,
            'Compliance Score': compliance_score,
            'Gap Count': len(gap_areas)
        })
    
    # Sort by compliance score (highest first)
    framework_df = pd.DataFrame(framework_data)
    framework_df = framework_df.sort_values('Compliance Score', ascending=False)
    
    # Create compliance chart
    if not framework_df.empty:
        chart = alt.Chart(framework_df).mark_bar().encode(
            x=alt.X('Compliance Score', title='Compliance Score (%)'),
            y=alt.Y('Framework', sort='-x', title=None),
            color=alt.Color('Compliance Score',
                         scale=alt.Scale(
                             domain=[0, 50, 100], 
                             range=['#f63366', '#ffbd45', '#00cc96']
                         )),
            tooltip=['Framework', 'Compliance Score', 'Gap Count']
        ).properties(
            height=300
        )
        
        st.altair_chart(chart, use_container_width=True)
    
    # Display framework details
    st.subheader("Framework Details")
    
    for framework_id, data in framework_compliance.items():
        # Get framework name
        framework_name = framework_id.upper()
        if framework_id == 'nist_csf':
            framework_name = 'NIST CSF'
        elif framework_id == 'iso27001':
            framework_name = 'ISO 27001'
        
        # Get compliance score
        compliance_score = data.get('compliance_score', 0)
        
        # Format compliance level
        compliance_level = "Low"
        if compliance_score >= 80:
            compliance_level = "High"
        elif compliance_score >= 60:
            compliance_level = "Medium"
        
        # Display in expander
        with st.expander(f"{framework_name} - {compliance_level} Compliance ({compliance_score:.1f}%)"):
            # Show domain scores if available
            domain_scores = data.get('domain_scores', {})
            
            if domain_scores:
                # Create domain scores dataframe
                domain_data = [
                    {
                        'Domain': domain.replace('_', ' ').title(),
                        'Score': score
                    }
                    for domain, score in domain_scores.items()
                ]
                
                # Sort by score (lowest first)
                domain_df = pd.DataFrame(domain_data)
                if not domain_df.empty:
                    domain_df = domain_df.sort_values('Score')
                    
                    # Show as a bar chart
                    domain_chart = alt.Chart(domain_df).mark_bar().encode(
                        x=alt.X('Score', title='Score (%)'),
                        y=alt.Y('Domain', sort='-x', title=None),
                        color=alt.Color('Score',
                                     scale=alt.Scale(
                                         domain=[0, 50, 100], 
                                         range=['#f63366', '#ffbd45', '#00cc96']
                                     )),
                        tooltip=['Domain', 'Score']
                    ).properties(
                        height=min(200, len(domain_df) * 25)
                    )
                    
                    st.altair_chart(domain_chart, use_container_width=True)
            
            # Show gap areas
            gap_areas = data.get('gap_areas', [])
            
            if gap_areas:
                st.markdown("**Key Gap Areas:**")
                
                for i, gap in enumerate(gap_areas[:5]):  # Show top 5
                    category = gap.get('category', '').replace('_', ' ').title()
                    score = gap.get('score', 0)
                    
                    st.markdown(f"- {category} ({score:.1f}%)")
            else:
                st.write("No significant gap areas identified.")


def _render_recommendations_tab(recommendations):
    """
    Render the recommendations tab
    
    Args:
        recommendations: List of recommendation dictionaries
    """
    st.subheader("Security Recommendations")
    
    if not recommendations:
        st.warning("No recommendations available.")
        return
    
    # Group recommendations by priority
    high_priority = [r for r in recommendations if r.get('priority') == 1]
    medium_priority = [r for r in recommendations if r.get('priority') == 2]
    low_priority = [r for r in recommendations if r.get('priority') == 3]
    
    # Display high priority recommendations
    if high_priority:
        st.markdown("### High Priority Actions")
        
        for i, rec in enumerate(high_priority):
            category = rec.get('category', '').replace('_', ' ').title()
            recommendation = rec.get('recommendation', '')
            
            st.markdown(f"**{i+1}. {category}**")
            st.markdown(f"{recommendation}")
            st.markdown("---")
    
    # Display medium priority recommendations
    if medium_priority:
        st.markdown("### Medium Priority Actions")
        
        for i, rec in enumerate(medium_priority):
            category = rec.get('category', '').replace('_', ' ').title()
            recommendation = rec.get('recommendation', '')
            
            st.markdown(f"**{i+1}. {category}**")
            st.markdown(f"{recommendation}")
            st.markdown("---")
    
    # Display low priority recommendations
    if low_priority:
        st.markdown("### Low Priority Actions")
        
        for i, rec in enumerate(low_priority):
            category = rec.get('category', '').replace('_', ' ').title()
            recommendation = rec.get('recommendation', '')
            
            st.markdown(f"**{i+1}. {category}**")
            st.markdown(f"{recommendation}")
            st.markdown("---")


def _load_demo_data():
    """Load demo data for dashboard demonstration"""
    # Create demo assessment data
    assessment = {
        'risk_level': 'Medium',
        'risk_score': 68.5,
        'domain_scores': {
            'access_control': {'score': 60, 'risk_level': 'Medium', 'weight': 0.15},
            'data_protection': {'score': 45, 'risk_level': 'High', 'weight': 0.15},
            'vulnerability_management': {'score': 70, 'risk_level': 'Medium', 'weight': 0.15},
            'incident_response': {'score': 65, 'risk_level': 'Medium', 'weight': 0.10},
            'network_security': {'score': 80, 'risk_level': 'Low', 'weight': 0.10},
            'physical_security': {'score': 75, 'risk_level': 'Medium', 'weight': 0.07},
            'security_policies': {'score': 85, 'risk_level': 'Low', 'weight': 0.08},
            'risk_management': {'score': 60, 'risk_level': 'Medium', 'weight': 0.05},
            'security_awareness': {'score': 50, 'risk_level': 'High', 'weight': 0.05},
            'bcdr': {'score': 70, 'risk_level': 'Medium', 'weight': 0.05},
            'asset_management': {'score': 75, 'risk_level': 'Medium', 'weight': 0.05}
        },
        'top_risk_domains': [
            {'domain': 'data_protection', 'risk_level': 'High', 'score': 45, 'weight': 0.15},
            {'domain': 'security_awareness', 'risk_level': 'High', 'score': 50, 'weight': 0.05},
            {'domain': 'access_control', 'risk_level': 'Medium', 'score': 60, 'weight': 0.15}
        ],
        'framework_compliance': {
            'nist_csf': {
                'compliance_score': 72.5,
                'domain_scores': {
                    'access_control': 60,
                    'data_protection': 45,
                    'vulnerability_management': 70,
                    'incident_response': 65,
                    'network_security': 80
                },
                'gap_areas': [
                    {'category': 'data_protection', 'score': 45},
                    {'category': 'access_control', 'score': 60}
                ]
            },
            'iso27001': {
                'compliance_score': 68.0,
                'domain_scores': {
                    'access_control': 60,
                    'data_protection': 45,
                    'security_policies': 85,
                    'risk_management': 60,
                    'physical_security': 75
                },
                'gap_areas': [
                    {'category': 'data_protection', 'score': 45},
                    {'category': 'access_control', 'score': 60},
                    {'category': 'risk_management', 'score': 60}
                ]
            },
            'gdpr': {
                'compliance_score': 58.0,
                'domain_scores': {
                    'data_protection': 45,
                    'access_control': 60,
                    'incident_response': 65
                },
                'gap_areas': [
                    {'category': 'data_protection', 'score': 45},
                    {'category': 'access_control', 'score': 60}
                ]
            }
        },
        'security_gaps': [
            {
                'category': 'data_protection',
                'risk_level': 'High',
                'score': 45,
                'negative_responses': [
                    {'question': 'Is sensitive data encrypted at rest?'},
                    {'question': 'Do you have a data classification policy?'},
                    {'question': 'Is there a data loss prevention (DLP) solution in place?'}
                ]
            },
            {
                'category': 'security_awareness',
                'risk_level': 'High',
                'score': 50,
                'negative_responses': [
                    {'question': 'Do you conduct regular security awareness training?'},
                    {'question': 'Do you run phishing simulations?'}
                ]
            }
        ],
        'assessment_summary': """The security assessment indicates an overall **Medium Risk** level with a risk score of 68.5%. 
The top risk areas that need attention are: Data Protection, Security Awareness, and Access Control. 
The highest compliance score is 72.5% for NIST CSF."""
    }
    
    # Create demo recommendations
    recommendations = [
        {
            'category': 'data_protection',
            'risk_level': 'High',
            'recommendation': 'Implement comprehensive data encryption for sensitive data at rest and in transit. Develop and implement a data classification policy to identify and properly protect different types of data.',
            'priority': 1
        },
        {
            'category': 'security_awareness',
            'risk_level': 'High',
            'recommendation': 'Establish a formal security awareness training program with regular sessions for all employees. Implement phishing simulations to test effectiveness.',
            'priority': 1
        },
        {
            'category': 'access_control',
            'risk_level': 'Medium',
            'recommendation': 'Enhance access controls with periodic access reviews and improved authentication. Implement multi-factor authentication for all critical systems and administrative access.',
            'priority': 2
        },
        {
            'category': 'vulnerability_management',
            'risk_level': 'Medium',
            'recommendation': 'Improve vulnerability scanning frequency and patch critical systems more rapidly. Establish formal SLAs for patching based on vulnerability severity.',
            'priority': 2
        },
        {
            'category': 'network_security',
            'risk_level': 'Low',
            'recommendation': 'Maintain current network security controls and consider advanced threat detection. Review network segmentation to ensure appropriate isolation of sensitive systems.',
            'priority': 3
        }
    ]
    
    # Update session state
    st.session_state.assessment = assessment
    st.session_state.recommendations = recommendations
    
    # Update framework coverage in session state
    for framework_id, data in assessment['framework_compliance'].items():
        if framework_id in st.session_state.frameworks:
            st.session_state.frameworks[framework_id]['coverage'] = data.get('compliance_score', 0)


def _get_risk_color(risk_level):
    """
    Get color for risk level
    
    Args:
        risk_level: Risk level string
        
    Returns:
        Color hex code
    """
    risk_colors = {
        'High': '#f63366',    # Red
        'Medium': '#ffbd45',  # Amber/Orange
        'Low': '#00cc96'      # Green
    }
    
    return risk_colors.get(risk_level, '#36c') 