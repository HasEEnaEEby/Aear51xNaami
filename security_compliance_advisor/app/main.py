"""
Main application entry point for Security Compliance Advisor
"""

import streamlit as st
import logging
import os
import sys
from pathlib import Path

# Add the project root directory to Python path to fix import issues
# This ensures that 'core' module can be found
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Import components - Fixed import paths
from core.advisor.security_advisor import SecurityAdvisor
from core.advisor.questionnaire_processor import QuestionnaireProcessor
from core.risk.risk_scoring_model import RiskScoringModel
from core.compliance.compliance_knowledge import ComplianceKnowledge

# Import UI modules
from app.pages.chat_page import render_chat_page
from app.pages.dashboard_page import render_dashboard_page
from app.pages.questionnaire_page import render_questionnaire_page
from app.pages.frameworks_page import render_frameworks_page

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define file paths
DATA_DIR = BASE_DIR / "data"
FRAMEWORKS_DIR = DATA_DIR / "frameworks"
MAPPINGS_DIR = DATA_DIR / "mappings"
POLICIES_DIR = DATA_DIR / "policies"
MODELS_DIR = DATA_DIR / "models"

def initialize_components():
    """Initialize all system components"""
    try:
        # Initialize questionnaire processor
        questionnaire_processor = QuestionnaireProcessor(
            field_mappings_path=MAPPINGS_DIR / "field_mappings.json" if (MAPPINGS_DIR / "field_mappings.json").exists() else None
        )
        
        # Initialize risk model
        risk_model = RiskScoringModel(
            feature_mappings_path=MAPPINGS_DIR / "feature_mappings.json" if (MAPPINGS_DIR / "feature_mappings.json").exists() else None,
            compliance_mappings_path=MAPPINGS_DIR / "compliance_mappings.json" if (MAPPINGS_DIR / "compliance_mappings.json").exists() else None,
            recommendations_path=MAPPINGS_DIR / "recommendations.json" if (MAPPINGS_DIR / "recommendations.json").exists() else None
        )
        
        # Initialize compliance knowledge base
        compliance_kb = ComplianceKnowledge(
            frameworks_dir=str(FRAMEWORKS_DIR) if FRAMEWORKS_DIR.exists() else None,
            mappings_file=str(MAPPINGS_DIR / "control_mappings.json") if (MAPPINGS_DIR / "control_mappings.json").exists() else None
        )
        
        # Initialize security advisor
        security_advisor = SecurityAdvisor(
            questionnaire_processor=questionnaire_processor,
            risk_model=risk_model,
            compliance_knowledge=compliance_kb,
            config_path=BASE_DIR / "config.py" if (BASE_DIR / "config.py").exists() else None,
            output_dir=BASE_DIR / "outputs" if not (BASE_DIR / "outputs").exists() else BASE_DIR / "outputs"
        )
        
        return {
            "questionnaire_processor": questionnaire_processor,
            "risk_model": risk_model,
            "compliance_kb": compliance_kb,
            "security_advisor": security_advisor
        }
    
    except Exception as e:
        logger.error(f"Error initializing components: {str(e)}")
        st.error(f"Error initializing application components: {str(e)}")
        return {}

def setup_streamlit():
    """Configure Streamlit app settings"""
    st.set_page_config(
        page_title="Security & Compliance Advisor",
        page_icon="🔒",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS
    css_path = Path(__file__).parent / "utils" / "styles.css"
    if css_path.exists():
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'  # Changed default to dashboard
    
    if 'assessment' not in st.session_state:
        st.session_state.assessment = None
    
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = []
    
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    
    if 'questionnaire_data' not in st.session_state:
        st.session_state.questionnaire_data = {}
    
    # Initialize frameworks in session state
    if 'frameworks' not in st.session_state:
        st.session_state.frameworks = {
            "iso27001": {
                "name": "ISO/IEC 27001",
                "description": "International standard for information security management",
                "coverage": 73
            },
            "nist_csf": {
                "name": "NIST Cybersecurity Framework",
                "description": "Framework for improving critical infrastructure cybersecurity",
                "coverage": 67
            },
            "gdpr": {
                "name": "GDPR",
                "description": "EU regulation on data protection and privacy",
                "coverage": 83
            },
            "hipaa": {
                "name": "HIPAA",
                "description": "US healthcare privacy and security regulation",
                "coverage": 76
            },
            "pci_dss": {
                "name": "PCI DSS",
                "description": "Payment card industry security standard",
                "coverage": 92
            },
            "ccpa": {
                "name": "CCPA",
                "description": "California Consumer Privacy Act",
                "coverage": 0
            },
            "cis": {
                "name": "CIS Controls",
                "description": "Critical security controls for cyber defense",
                "coverage": 0
            },
            "hitrust": {
                "name": "HITRUST CSF",
                "description": "Healthcare industry security framework",
                "coverage": 0
            }
        }

def render_sidebar():
    """Render the sidebar navigation with enhanced styling"""
    with st.sidebar:
        # Logo and title with custom styling
        st.markdown("""
        <div class="logo-container">
            <img src="https://user-content.gitlab-static.net/dd4d5ed9ef6a9cfdae899aa9e63afd8e4ab982f5/68747470733a2f2f692e6962622e636f2f30465859546a4d2f41757261353170696e672e706e67" class="app-logo">
            <h2>Security Compliance Advisor</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation with improved styling
        st.markdown("<h3 style='color: white;'>Navigation</h3>", unsafe_allow_html=True)
        
        # Dashboard
        if st.button("📊 Risk Dashboard", key="nav_dashboard", use_container_width=True):
            st.session_state.current_page = 'dashboard'
            st.experimental_rerun()
        
        # Chat with advisor
        if st.button("💬 Chat with Advisor", key="nav_chat", use_container_width=True):
            st.session_state.current_page = 'chat'
            st.experimental_rerun()
        
        # View frameworks
        if st.button("📚 Compliance Frameworks", key="nav_frameworks", use_container_width=True):
            st.session_state.current_page = 'frameworks'
            st.experimental_rerun()
        
        # Upload questionnaire
        if st.button("📋 Questionnaire", key="nav_upload", use_container_width=True):
            st.session_state.current_page = 'upload'
            st.experimental_rerun()
        
        st.markdown("---")
        
        # Add info about the app with better styling
        st.markdown("""
        <div style="background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
            <h3 style="color: white;">About</h3>
            <p style="color: rgba(255,255,255,0.8);">
                This Security & Compliance Advisor helps you:
            </p>
            <ul style="color: rgba(255,255,255,0.8);">
                <li>Analyze vendor security questionnaires</li>
                <li>Identify security & compliance risks</li>
                <li>Get recommendations for improvements</li>
                <li>Chat with an AI security advisor</li>
            </ul>
            <p style="color: rgba(255,255,255,0.8); margin-top: 15px; font-style: italic;">
                Built with ♥ at NepalHacks 2025
            </p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application entry point"""
    # Setup Streamlit
    setup_streamlit()
    
    # Initialize components
    components = initialize_components()
    
    # Store components in session state for reuse
    if components:
        st.session_state.components = components
    
    # Render sidebar
    render_sidebar()
    
    # Custom header for main content
    st.markdown("""
    <div class="custom-header">
        <h1 style="margin-bottom: 0;">🔒 Security Compliance Advisor</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Render current page
    if st.session_state.current_page == 'upload':
        render_questionnaire_page(components.get('security_advisor') if 'components' in st.session_state else None)
    elif st.session_state.current_page == 'chat':
        render_chat_page(components.get('security_advisor') if 'components' in st.session_state else None)
    elif st.session_state.current_page == 'dashboard':
        render_dashboard_page()
    elif st.session_state.current_page == 'frameworks':
        render_frameworks_page(components.get('compliance_kb') if 'components' in st.session_state else None)
    else:
        st.error("Unknown page")

if __name__ == "__main__":
    main()