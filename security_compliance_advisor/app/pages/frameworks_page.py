"""
Frameworks page for Security Compliance Advisor
This page displays compliance frameworks and their requirements.
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

def _display_controls_list(controls):
    """
    Display a list of controls in an organized way
    
    Args:
        controls: List of control dictionaries with domain and controls
    """
    for control_group in controls:
        domain = control_group.get('domain', '')
        control_list = control_group.get('controls', [])
        
        st.markdown(f"### {domain}")
        
        for control in control_list:
            st.markdown(f"- {control}")
        
        st.markdown("---")

def render_frameworks_page(compliance_kb=None):
    """
    Render the frameworks page
    
    Args:
        compliance_kb: ComplianceKnowledge instance (optional)
    """
    st.title("Compliance Frameworks")
    
    # Initialize session state
    if "frameworks" not in st.session_state:
        st.session_state.frameworks = {
            "iso27001": {"name": "ISO/IEC 27001", "description": "International standard for information security management", "coverage": 0},
            "nist_csf": {"name": "NIST Cybersecurity Framework", "description": "Framework for improving critical infrastructure cybersecurity", "coverage": 0},
            "gdpr": {"name": "GDPR", "description": "EU regulation on data protection and privacy", "coverage": 0},
            "hipaa": {"name": "HIPAA", "description": "US healthcare privacy and security regulation", "coverage": 0},
            "pci_dss": {"name": "PCI DSS", "description": "Payment card industry security standard", "coverage": 0}
        }
    
    # Instructions
    st.markdown("""
    ## Explore Compliance Frameworks
    
    This page provides information about major security and compliance frameworks. 
    Use this to understand different regulatory requirements and how they relate to your organization.
    
    Your current compliance coverage is shown for each framework based on your most recent assessment.
    """)
    
    # Display frameworks
    st.subheader("Frameworks")
    
    # Create framework cards in a grid
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**ISO 27001**  \nInternational standard for information security management")
        
    with col2:
        st.info("**NIST CSF**  \nCybersecurity Framework for critical infrastructure") 
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.info("**GDPR**  \nEU regulation on data protection and privacy")
        
    with col4:
        st.info("**HIPAA**  \nUS healthcare privacy and security regulation")
    
    # Information about frameworks
    st.subheader("About Compliance Frameworks")
    
    st.markdown("""
    Compliance frameworks provide structured approaches to managing security and privacy risks. 
    They typically include:
    
    - **Controls and requirements**: Specific security measures to implement
    - **Assessment procedures**: Methods to evaluate compliance
    - **Implementation guidance**: Best practices for meeting requirements
    
    To assess your compliance with these frameworks, upload a security questionnaire on the Questionnaire page.
    """)
    
    # Add assessment option
    st.markdown("### Take Action")
    
    assessment_col, resources_col = st.columns(2)
    
    with assessment_col:
        st.markdown("Start a compliance assessment:")
        if st.button("Begin Assessment", key="begin_assessment"):
            st.session_state.current_page = 'upload'
            st.experimental_rerun()
    
    with resources_col:
        st.markdown("Get framework-specific guidance:")
        if st.button("Chat with Advisor", key="chat_advisor"):
            st.session_state.current_page = 'chat'
            st.experimental_rerun()


if __name__ == "__main__":
    render_frameworks_page()