import streamlit as st
import logging
import os
from pathlib import Path

# Import components
from security_compliance_advisor.core.advisor.security_advisor import SecurityAdvisor
from security_compliance_advisor.core.advisor.questionnaire_processor import QuestionnaireProcessor
from security_compliance_advisor.core.risk.risk_scoring_model import RiskScoringModel
from security_compliance_advisor.core.compliance.compliance_knowledge import ComplianceKnowledgeBase

# Import UI modules
from security_compliance_advisor.app.pages.chat_page import render_chat_page
from security_compliance_advisor.app.pages.dashboard_page import render_dashboard_page
from security_compliance_advisor.app.pages.questionnaire_page import render_questionnaire_page
from security_compliance_advisor.app.pages.frameworks_page import render_frameworks_page
from security_compliance_advisor.app.components.sidebar import render_sidebar

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define file paths
BASE_DIR = Path(__file__).parent.parent.parent
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
        compliance_kb = ComplianceKnowledgeBase(
            frameworks_dir=str(FRAMEWORKS_DIR) if FRAMEWORKS_DIR.exists() else None,
            mappings_file=str(MAPPINGS_DIR / "control_mappings.json") if (MAPPINGS_DIR / "control_mappings.json").exists() else None
        )
        
        # Initialize security advisor
        security_advisor = SecurityAdvisor(
            questionnaire_processor=questionnaire_processor,
            risk_model=risk_model,
            compliance_knowledge=compliance_kb,
            config_path=BASE_DIR / "config.py" if (BASE_DIR / "config.py").exists() else None,
            output_dir=BASE_DIR / "outputs"
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
    with open(Path(__file__).parent / "utils" / "styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'upload'
    
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
                "coverage": 0
            },
            "nist_csf": {
                "name": "NIST Cybersecurity Framework",
                "description": "Framework for improving critical infrastructure cybersecurity",
                "coverage": 0
            },
            "gdpr": {
                "name": "GDPR",
                "description": "EU regulation on data protection and privacy",
                "coverage": 0
            },
            "hipaa": {
                "name": "HIPAA",
                "description": "US healthcare privacy and security regulation",
                "coverage": 0
            },
            "pci_dss": {
                "name": "PCI DSS",
                "description": "Payment card industry security standard",
                "coverage": 0
            }
        }

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