"""
Main application entry point for Security Compliance Advisor
"""

import streamlit as st
import logging
import os
import sys
from pathlib import Path
import base64

# Add the project root directory to Python path to fix import issues
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Import components
from core.advisor.questionnaire_processor import QuestionnaireProcessor
from core.risk.risk_scoring_model import RiskScoringModel
from core.compliance.compliance_knowledge import ComplianceKnowledge
from core.advisor.security_advisor import SecurityAdvisor

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
ASSETS_DIR = BASE_DIR / "assets"


def initialize_components():
    """Initialize all system components"""
    try:
        questionnaire_processor = QuestionnaireProcessor()
        risk_model = RiskScoringModel()
        compliance_kb = ComplianceKnowledge()

        # Instantiate advisor without unexpected kwargs
        security_advisor = SecurityAdvisor()

        # Manually assign components to advisor if required
        security_advisor.questionnaire_processor = questionnaire_processor
        security_advisor.risk_model = risk_model
        security_advisor.compliance_knowledge = compliance_kb

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


def get_img_as_base64(file_path):
    """Convert an image to base64 string"""
    with open(file_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def setup_streamlit():
    """Configure Streamlit app settings"""
    st.set_page_config(
        page_title="Aura51 | Security & Compliance Advisor",
        page_icon="🔒",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply custom CSS
    css_path = Path(__file__).parent / "utils" / "styles.css"
    if css_path.exists():
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # CSS to hide file navigator
    st.markdown("""
    <style>
    /* Hide the file navigator in the sidebar */
    [data-testid="stSidebarNav"],
    .sidebar .sidebar-content > div:first-child,
    .css-1d391kg {
        display: none !important;
    }
    
    /* Hide the X close button at the top */
    .sidebar .sidebar-close-button,
    button[kind="header"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'

    if 'assessment' not in st.session_state:
        st.session_state.assessment = None

    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = []

    if 'conversation' not in st.session_state:
        st.session_state.conversation = []

    if 'questionnaire_data' not in st.session_state:
        st.session_state.questionnaire_data = {}

    if 'frameworks' not in st.session_state:
        st.session_state.frameworks = {
            "iso27001": {"name": "ISO/IEC 27001", "description": "International standard for information security management", "coverage": 73},
            "nist_csf": {"name": "NIST Cybersecurity Framework", "description": "Framework for improving critical infrastructure cybersecurity", "coverage": 67},
            "gdpr": {"name": "GDPR", "description": "EU regulation on data protection and privacy", "coverage": 83},
            "hipaa": {"name": "HIPAA", "description": "US healthcare privacy and security regulation", "coverage": 76},
            "pci_dss": {"name": "PCI DSS", "description": "Payment card industry security standard", "coverage": 92},
            "ccpa": {"name": "CCPA", "description": "California Consumer Privacy Act", "coverage": 0},
            "cis": {"name": "CIS Controls", "description": "Critical security controls for cyber defense", "coverage": 0},
            "hitrust": {"name": "HITRUST CSF", "description": "Healthcare industry security framework", "coverage": 0}
        }


def render_sidebar():
    """Render the sidebar navigation with styling"""
    with st.sidebar:
        logo_path = ASSETS_DIR / "Aura51.png"
        logo_base64 = get_img_as_base64(logo_path) if logo_path.exists() else ""
        
        st.markdown(f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_base64}" class="app-logo">
            <h2>Aura51 Security</h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<h4 style='color: #ffb74d; margin-bottom: 15px;'>NAVIGATION</h4>", unsafe_allow_html=True)

        # Dashboard button
        dashboard_active = "active" if st.session_state.current_page == 'dashboard' else ""
        dashboard_html = f"""
        <div class="nav-button {dashboard_active}" onclick="document.getElementById('nav_dashboard').click()">
            📊 Risk Dashboard
        </div>
        """
        st.markdown(dashboard_html, unsafe_allow_html=True)
        button_dashboard = st.button("Risk Dashboard", key="nav_dashboard", help="View risk assessment dashboard")
        if button_dashboard:
            st.session_state.current_page = 'dashboard'
            st.experimental_rerun()

        # Chat button
        chat_active = "active" if st.session_state.current_page == 'chat' else ""
        chat_html = f"""
        <div class="nav-button {chat_active}" onclick="document.getElementById('nav_chat').click()">
            💬 FAQ with Advisor
        </div>
        """
        st.markdown(chat_html, unsafe_allow_html=True)
        button_chat = st.button("FAQ with Advisor", key="nav_chat", help="Chat with the AI security advisor")
        if button_chat:
            st.session_state.current_page = 'chat'
            st.experimental_rerun()

        # Frameworks button
        frameworks_active = "active" if st.session_state.current_page == 'frameworks' else ""
        frameworks_html = f"""
        <div class="nav-button {frameworks_active}" onclick="document.getElementById('nav_frameworks').click()">
            📚 Compliance Frameworks
        </div>
        """
        st.markdown(frameworks_html, unsafe_allow_html=True)
        button_frameworks = st.button("Compliance Frameworks", key="nav_frameworks", help="View compliance frameworks")
        if button_frameworks:
            st.session_state.current_page = 'frameworks'
            st.experimental_rerun()

        # Upload button
        upload_active = "active" if st.session_state.current_page == 'upload' else ""
        upload_html = f"""
        <div class="nav-button {upload_active}" onclick="document.getElementById('nav_upload').click()">
            📋 Assessment Questionnaire
        </div>
        """
        st.markdown(upload_html, unsafe_allow_html=True)
        button_upload = st.button("Assessment Questionnaire", key="nav_upload", help="Upload and process a security questionnaire")
        if button_upload:
            st.session_state.current_page = 'upload'
            st.experimental_rerun()

        st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)
        
        # About section
        st.markdown("""
        <div class="about-section">
            <h3>About Aura51</h3>
            <p>
                Your intelligent security and compliance assistant:
            </p>
            <ul>
                <li>Analyze vendor security questionnaires</li>
                <li>Identify security & compliance risks</li>
                <li>Get recommendations for improvements</li>
                <li>Chat with an AI security advisor</li>
            </ul>
            <div class="footer-text">
                Built with ♥ at NepalHacks 2025
            </div>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main application entry point"""
    setup_streamlit()
    components = initialize_components()
    if components:
        st.session_state.components = components

    render_sidebar()

    # App header with professional styling
    current_page_title = {
        'dashboard': '📊 Risk Assessment Dashboard',
        'chat': '💬 Chat with Security Advisor',
        'frameworks': '📚 Compliance Frameworks',
        'upload': '📋 Vendor Security Assessment'
    }.get(st.session_state.current_page, 'Security Compliance Advisor')
    
    st.markdown(f"""
    <div class="section-header">
        <h1 style="color: #f4f6f9; font-weight: 600;">{current_page_title}</h1>
        <p style="color: #a0aec0; margin-top: 5px;">
            Aura51 Security Compliance Advisor - Intelligent security assessment and compliance management
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Render the selected page
    page = st.session_state.current_page
    if page == 'upload':
        render_questionnaire_page(components.get('security_advisor'))
    elif page == 'chat':
        render_chat_page(components.get('security_advisor'))
    elif page == 'dashboard':
        render_dashboard_page()
    elif page == 'frameworks':
        render_frameworks_page(components.get('compliance_kb'))
    else:
        st.error("Unknown page")


if __name__ == "__main__":
    main()