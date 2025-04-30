import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re
import base64
import json

# Set page config
st.set_page_config(
    page_title="Security & Compliance Advisor",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
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

# Define risk scoring function
def calculate_risk_score(questionnaire_data):
    """Calculate risk score based on questionnaire responses"""
    # Define weights for different categories
    category_weights = {
        "access_control": 0.25,
        "data_protection": 0.20,
        "network_security": 0.15,
        "vulnerability_management": 0.15,
        "incident_response": 0.15,
        "vendor_management": 0.10
    }
    
    # Define score mappings for key fields
    score_mappings = {
        # Access Control Category
        "mfa_status": {
            "Not implemented": 100,
            "For privileged users only": 60,
            "For all employees": 30,
            "For all users including third parties": 0
        },
        "password_policy": {
            "Basic (8+ characters)": 80,
            "Medium (10+ chars, mixed case)": 50,
            "Strong (12+ chars, mixed case, symbols, numbers)": 20,
            "Very strong (14+ chars with complexity)": 0
        },
        "privileged_access": {
            "No specific management": 100,
            "Manual tracking": 70,
            "PAM solution for some systems": 40,
            "Comprehensive PAM with monitoring": 0
        },
        "access_reviews": {
            "Never/ad hoc": 100,
            "Annually": 70,
            "Quarterly": 40,
            "Monthly": 20,
            "Continuous monitoring": 0
        },
        
        # Data Protection Category
        "data_classification": {
            "No formal classification": 100,
            "Basic classification exists but not enforced": 70,
            "Classification implemented for sensitive data": 40,
            "Comprehensive classification enforced for all data": 0
        },
        "encryption_status": {
            "Minimal/ad hoc encryption": 100,
            "Encryption for some sensitive data": 60,
            "Encryption for all sensitive data at rest and in transit": 20,
            "End-to-end encryption for all data": 0
        },
        "dlp_status": {
            "No DLP implementation": 100,
            "Basic DLP for email only": 70,
            "DLP for email and endpoints": 40,
            "Comprehensive DLP across all channels": 0
        },
        "data_retention": {
            "No formal policy": 100,
            "Policy exists but not enforced": 70,
            "Policy with manual enforcement": 40,
            "Automated enforcement of retention policies": 0
        },
        
        # Network Security Category
        "network_segmentation": {
            "Minimal/no segmentation": 100,
            "Basic segmentation (e.g., IT vs OT)": 70,
            "Moderate segmentation by department/function": 40,
            "Zero trust architecture/microsegmentation": 0
        },
        "firewall_management": {
            "Basic firewall configuration": 80,
            "Regular but manual reviews": 60,
            "Change management process with reviews": 30,
            "Automated policy management and continuous monitoring": 0
        },
        
        # Vulnerability Management Category
        "vuln_scanning": {
            "Ad hoc or never": 100,
            "Annually": 80,
            "Quarterly": 60,
            "Monthly": 30,
            "Continuous/automated scanning": 0
        },
        "patch_management": {
            "Ad hoc patching": 100,
            "Regular but manual patching": 70,
            "Scheduled patching with SLAs": 30,
            "Automated patch management with verification": 0
        },
        
        # Incident Response Category
        "ir_plan": {
            "No formal plan": 100,
            "Basic plan but not tested": 70,
            "Documented plan with annual testing": 30,
            "Comprehensive plan with regular exercises": 0
        },
        "security_monitoring": {
            "Minimal/ad hoc monitoring": 100,
            "Basic logging without 24/7 monitoring": 70,
            "SIEM solution with business hours monitoring": 40,
            "24/7 SOC with advanced analytics": 0
        },
        "breach_response": {
            "No defined SLAs": 100,
            "Within 24 hours for critical systems": 60,
            "Within 8 hours for critical systems": 30,
            "Within 1 hour with automated containment": 0
        },
        "forensic_capabilities": {
            "No forensic capabilities": 100,
            "Basic log review capabilities": 70,
            "Some forensic tools and training": 40,
            "Advanced forensics team and tools": 0
        },
        
        # Vendor Management Category
        "vendor_assessment": {
            "No formal assessment": 100,
            "Basic security questionnaire": 70,
            "Detailed assessment for critical vendors": 40,
            "Comprehensive assessments with ongoing monitoring": 0
        },
        "vendor_contracts": {
            "Minimal security language": 100,
            "Basic security requirements": 70,
            "Detailed requirements with right-to-audit": 30,
            "Comprehensive requirements with regular verification": 0
        },
        "third_party_access": {
            "Same as employee access": 100,
            "Some restrictions for third parties": 70,
            "Limited access with additional controls": 30,
            "Just-in-time access with comprehensive monitoring": 0
        },
        "vendor_incidents": {
            "No specific process": 100,
            "Basic notification requirements": 70,
            "Formal process for critical vendors": 40,
            "Comprehensive incident management with all vendors": 0
        }
    }
    
    # Map questions to categories
    category_mappings = {
        "access_control": ["mfa_status", "password_policy", "privileged_access", "access_reviews"],
        "data_protection": ["data_classification", "encryption_status", "dlp_status", "data_retention"],
        "network_security": ["network_segmentation", "firewall_management"],
        "vulnerability_management": ["vuln_scanning", "patch_management"],
        "incident_response": ["ir_plan", "security_monitoring", "breach_response", "forensic_capabilities"],
        "vendor_management": ["vendor_assessment", "vendor_contracts", "third_party_access", "vendor_incidents"]
    }
    
    # Calculate category scores
    category_scores = {}
    
    for category, fields in category_mappings.items():
        total_score = 0
        valid_fields = 0
        
        for field in fields:
            if field in questionnaire_data and questionnaire_data[field] in score_mappings.get(field, {}):
                total_score += score_mappings[field][questionnaire_data[field]]
                valid_fields += 1
        
        # Calculate average score for category
        if valid_fields > 0:
            category_scores[category] = total_score / valid_fields
        else:
            category_scores[category] = 50  # Default score if no valid fields
    
    # Calculate weighted overall risk score
    risk_score = 0
    for category, score in category_scores.items():
        risk_score += score * category_weights.get(category, 0)
    
    # Generate top factors
    factors = []
    for category, fields in category_mappings.items():
        for field in fields:
            if field in questionnaire_data and questionnaire_data[field] in score_mappings.get(field, {}):
                score = score_mappings[field][questionnaire_data[field]]
                if score >= 60:  # Only include high-risk factors
                    impact = score * category_weights.get(category, 0) * 0.1
                    
                    factor = {
                        "feature": field,
                        "description": f"{field.replace('_', ' ').title()}: {questionnaire_data[field]}",
                        "impact": impact,
                        "direction": "negative"
                    }
                    factors.append(factor)
    
    # Sort factors by impact (highest first)
    factors.sort(key=lambda x: x['impact'], reverse=True)
    
    # Add some positive factors (good practices)
    for category, fields in category_mappings.items():
        for field in fields:
            if field in questionnaire_data and questionnaire_data[field] in score_mappings.get(field, {}):
                score = score_mappings[field][questionnaire_data[field]]
                if score <= 20:
                    impact = -1 * (100 - score) * category_weights.get(category, 0) * 0.02
                    
                    factor = {
                        "feature": field,
                        "description": f"Good Practice: {field.replace('_', ' ').title()} - {questionnaire_data[field]}",
                        "impact": impact,
                        "direction": "positive"
                    }
                    factors.append(factor)
    
    # Organize factors by category
    categories = {}
    for category_name, fields in category_mappings.items():
        category_display = category_name.replace('_', ' ').title()
        categories[category_display] = [f for f in factors if f['feature'] in fields]
    
    # Calculate framework compliance
    framework_compliance = calculate_framework_compliance(questionnaire_data, category_scores)
    
    # Generate risk level
    risk_level = get_risk_level(risk_score)
    
    # Generate recommendations
    recommendations = generate_recommendations(questionnaire_data, score_mappings)
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "explanation": {
            "top_factors": factors[:10],
            "categories": categories,
            "summary": "The risk score is based on the identified security weaknesses across multiple domains."
        },
        "recommendations": recommendations,
        "framework_compliance": framework_compliance,
        "category_scores": category_scores,
        "timestamp": datetime.now().isoformat()
    }

def get_risk_level(score):
    """Determine risk level based on score"""
    if score < 20:
        return {
            "name": "very low risk",
            "description": "Your security posture is excellent with minimal areas for improvement.",
            "color": "green"
        }
    elif score < 40:
        return {
            "name": "low risk",
            "description": "Your security posture is good with a few minor areas for improvement.",
            "color": "blue"
        }
    elif score < 60:
        return {
            "name": "moderate risk",
            "description": "Your security posture needs attention in several key areas.",
            "color": "yellow"
        }
    elif score < 80:
        return {
            "name": "high risk",
            "description": "Your security posture has significant vulnerabilities that need immediate attention.",
            "color": "orange"
        }
    else:
        return {
            "name": "critical risk",
            "description": "Your security posture has critical vulnerabilities requiring urgent remediation.",
            "color": "red"
        }

def calculate_framework_compliance(questionnaire_data, category_scores):
    """Calculate compliance levels for different frameworks"""
    # Map categories to frameworks
    framework_mappings = {
        "iso27001": {
            "access_control": 0.25,
            "data_protection": 0.2,
            "network_security": 0.15,
            "vulnerability_management": 0.15,
            "incident_response": 0.15,
            "vendor_management": 0.1
        },
        "nist_csf": {
            "access_control": 0.2,
            "data_protection": 0.2,
            "network_security": 0.15,
            "vulnerability_management": 0.2,
            "incident_response": 0.15,
            "vendor_management": 0.1
        },
        "gdpr": {
            "access_control": 0.2,
            "data_protection": 0.4,
            "network_security": 0.1,
            "vulnerability_management": 0.1,
            "incident_response": 0.1,
            "vendor_management": 0.1
        },
        "hipaa": {
            "access_control": 0.25,
            "data_protection": 0.3,
            "network_security": 0.1,
            "vulnerability_management": 0.1,
            "incident_response": 0.15,
            "vendor_management": 0.1
        },
        "pci_dss": {
            "access_control": 0.3,
            "data_protection": 0.25,
            "network_security": 0.2,
            "vulnerability_management": 0.15,
            "incident_response": 0.05,
            "vendor_management": 0.05
        }
    }
    
    framework_compliance = {}
    
    for framework, category_weights in framework_mappings.items():
        compliance_score = 0
        
        for category, weight in category_weights.items():
            if category in category_scores:
                # Convert risk score to compliance percentage (100 - risk_score)
                compliance_score += (100 - category_scores[category]) * weight
        
        framework_compliance[framework] = {
            "compliance_score": compliance_score,
            "gap_areas": []
        }
        
        # Identify gap areas based on category scores
        for category, score in category_scores.items():
            if score >= 70 and category in category_weights and category_weights[category] >= 0.15:
                framework_compliance[framework]["gap_areas"].append({
                    "category": category,
                    "score": score
                })
    
    return framework_compliance

def generate_recommendations(questionnaire_data, score_mappings):
    """Generate recommendations based on questionnaire data"""
    recommendations = []
    
    field_recommendations = {
        "mfa_status": {
            "title": "Implement Multi-Factor Authentication",
            "description": "Deploy MFA for all users, especially those with privileged access. This will significantly reduce the risk of unauthorized access due to compromised credentials.",
            "category": "Access Control",
            "effort": "Medium"
        },
        "password_policy": {
            "title": "Strengthen Password Policy",
            "description": "Update your password policy to require longer passwords (14+ characters) with complexity requirements. Implement a password manager to help users maintain strong, unique passwords.",
            "category": "Access Control",
            "effort": "Low"
        },
        "privileged_access": {
            "title": "Implement Privileged Access Management",
            "description": "Deploy a PAM solution to manage, monitor, and control privileged accounts access. Include just-in-time access and session recording for critical systems.",
            "category": "Access Control",
            "effort": "High"
        },
        "access_reviews": {
            "title": "Establish Regular Access Reviews",
            "description": "Implement quarterly access reviews for all systems, especially those storing sensitive data. Automate the review process where possible to ensure consistency and completion.",
            "category": "Access Control",
            "effort": "Medium"
        },
        "data_classification": {
            "title": "Implement Data Classification",
            "description": "Establish a formal data classification framework and enforce controls based on data sensitivity levels. Train users on proper handling of sensitive information.",
            "category": "Data Protection",
            "effort": "Medium"
        },
        "encryption_status": {
            "title": "Enhance Data Encryption",
            "description": "Implement comprehensive encryption for sensitive data both at rest and in transit using industry-standard algorithms. Establish a key management process.",
            "category": "Data Protection",
            "effort": "Medium"
        },
        "dlp_status": {
            "title": "Deploy Data Loss Prevention",
            "description": "Implement a DLP solution to monitor and protect sensitive data across endpoints, networks, and cloud services. Start with high-risk channels like email and gradually expand coverage.",
            "category": "Data Protection",
            "effort": "High"
        },
        "data_retention": {
            "title": "Implement Data Retention Policy",
            "description": "Develop and enforce a formal data retention policy that automatically archives or deletes data based on retention requirements. Consider compliance requirements in your retention schedules.",
            "category": "Data Protection",
            "effort": "Medium"
        },
        "network_segmentation": {
            "title": "Implement Network Segmentation",
            "description": "Segment your network based on security requirements and data sensitivity. Use firewalls, VLANs, and access controls to restrict lateral movement within the network.",
            "category": "Network Security",
            "effort": "High"
        },
        "firewall_management": {
            "title": "Enhance Firewall Management",
            "description": "Implement a formal change management process for firewall rules, regular rule reviews, and automated policy validation to identify potential security gaps or misconfigurations.",
            "category": "Network Security",
            "effort": "Medium"
        },
        "vuln_scanning": {
            "title": "Implement Regular Vulnerability Scanning",
            "description": "Establish automated, regular vulnerability scanning of all systems and applications with a formal process for remediation prioritized by risk level.",
            "category": "Vulnerability Management",
            "effort": "Medium"
        },
        "patch_management": {
            "title": "Improve Patch Management",
            "description": "Implement an automated patch management system with defined SLAs for critical, high, medium, and low vulnerabilities. Establish a verification process to ensure patches are applied successfully.",
            "category": "Vulnerability Management",
            "effort": "High"
        },
        "ir_plan": {
            "title": "Develop Comprehensive Incident Response Plan",
            "description": "Create and regularly test a formal incident response plan that includes roles, responsibilities, and procedures for handling security incidents. Conduct tabletop exercises to validate the plan.",
            "category": "Incident Response",
            "effort": "Medium"
        },
        "security_monitoring": {
            "title": "Enhance Security Monitoring",
            "description": "Upgrade your security monitoring capabilities with a SIEM solution and 24/7 coverage. Implement automated alerting for critical security events and establish an escalation process.",
            "category": "Incident Response",
            "effort": "High"
        },
        "breach_response": {
            "title": "Improve Breach Response Capabilities",
            "description": "Establish clear SLAs for incident response based on severity levels. Implement automation for containment of common threats and develop playbooks for efficient response.",
            "category": "Incident Response",
            "effort": "Medium"
        },
        "forensic_capabilities": {
            "title": "Enhance Forensic Capabilities",
            "description": "Develop in-house forensic capabilities or establish relationships with external forensic providers. Ensure proper logging and evidence preservation mechanisms are in place.",
            "category": "Incident Response",
            "effort": "High"
        },
        "vendor_assessment": {
            "title": "Formalize Vendor Risk Assessment",
            "description": "Develop a comprehensive vendor risk assessment process that includes initial vetting, ongoing monitoring, and regular reassessment. Prioritize vendors based on data access and business criticality.",
            "category": "Vendor Management",
            "effort": "Medium"
        },
        "vendor_contracts": {
            "title": "Enhance Vendor Security Requirements",
            "description": "Update vendor contracts to include detailed security requirements, right-to-audit clauses, and breach notification obligations. Establish a process to verify compliance with these requirements.",
            "category": "Vendor Management",
            "effort": "Medium"
        },
        "third_party_access": {
            "title": "Secure Third-Party Access",
            "description": "Implement just-in-time access with comprehensive monitoring for all third-party access to your systems and data. Use separate VPNs or other secure access methods specifically for third parties.",
            "category": "Vendor Management",
            "effort": "Medium"
        },
        "vendor_incidents": {
            "title": "Improve Vendor Incident Management",
            "description": "Establish a formal process for handling security incidents involving vendors, including communication protocols, response procedures, and post-incident reviews.",
            "category": "Vendor Management",
            "effort": "Low"
        }
    }
    
    # Generate recommendations for high-risk areas
    for field, values in score_mappings.items():
        if field in questionnaire_data and questionnaire_data[field] in values:
            score = values[questionnaire_data[field]]
            
            # If score is high (indicating risk), add recommendation
            if score >= 60 and field in field_recommendations:
                rec = field_recommendations[field].copy()
                
                # Set impact based on score
                if score >= 90:
                    rec['impact'] = "High"
                elif score >= 70:
                    rec['impact'] = "Medium"
                else:
                    rec['impact'] = "Low"
                
                recommendations.append(rec)
    
    # Sort recommendations by impact
    impact_order = {"High": 0, "Medium": 1, "Low": 2}
    recommendations.sort(key=lambda x: impact_order.get(x.get('impact', "Low"), 3))
    
    return recommendations

def process_excel_questionnaire(file):
    """Process the uploaded Excel questionnaire file"""
    try:
        # Read Excel file
        df = pd.read_excel(file, engine='openpyxl', sheet_name=None)
        
        # Extract questionnaire data
        questionnaire_data = {}
        
        # Look for the main questionnaire sheet
        main_sheet = None
        for sheet_name, sheet_df in df.items():
            if "questionnaire" in sheet_name.lower() or "assessment" in sheet_name.lower() or "security" in sheet_name.lower():
                main_sheet = sheet_df
                break
        
        # If no specific sheet found, use the first one
        if main_sheet is None and len(df) > 0:
            main_sheet = list(df.values())[0]
        
        # Process the main sheet if found
        if main_sheet is not None:
            # Identify question and answer columns
            answer_col = None
            question_col = None
            
            for col in main_sheet.columns:
                col_lower = col.lower() if isinstance(col, str) else str(col).lower()
                if any(kw in col_lower for kw in ["answer", "response", "value", "selection"]):
                    answer_col = col
                if any(kw in col_lower for kw in ["question", "control", "requirement", "check"]):
                    question_col = col
            
            # If question and answer columns found
            if question_col and answer_col:
                for _, row in main_sheet.iterrows():
                    question = str(row[question_col]).strip()
                    answer = str(row[answer_col]).strip() if pd.notna(row[answer_col]) else ""
                    
                    # Map to our expected questionnaire fields
                    field = map_question_to_field(question)
                    if field and answer:
                        questionnaire_data[field] = map_answer_to_option(field, answer)
        
        # If we couldn't extract using standard approach, try to find data in any structured format
        if not questionnaire_data:
            for sheet_name, sheet_df in df.items():
                for i, row in sheet_df.iterrows():
                    for col in sheet_df.columns:
                        # Check if cell contains a key question keyword
                        cell_value = str(row[col]).lower() if pd.notna(row[col]) else ""
                        if any(kw in cell_value for kw in ["mfa", "password", "encryption", "firewall", "vulnerability", "incident"]):
                            # Look for an answer in the nearby cells
                            for offset in range(1, 4):
                                if i + offset < len(sheet_df):
                                    potential_answer = str(sheet_df.iloc[i + offset][col]).strip() if pd.notna(sheet_df.iloc[i + offset][col]) else ""
                                    if potential_answer and potential_answer.lower() not in ["yes", "no", "n/a", "question", "control"]:
                                        field = map_question_to_field(cell_value)
                                        if field:
                                            questionnaire_data[field] = map_answer_to_option(field, potential_answer)
                                            break
        
        return questionnaire_data
    
    except Exception as e:
        st.error(f"Error processing Excel file: {str(e)}")
        return {}

def map_question_to_field(question):
    """Map a question to a standardized field name"""
    question = question.lower()
    
    # MFA
    if any(kw in question for kw in ["multi-factor", "multifactor", "mfa", "two-factor", "2fa"]):
        return "mfa_status"
    
    # Password Policy
    if any(kw in question for kw in ["password policy", "password requirement", "password complexity"]):
        return "password_policy"
    
    # Privileged Access
    if any(kw in question for kw in ["privileged access", "admin account", "administrator", "elevated privilege"]):
        return "privileged_access"
    
    # Access Reviews
    if any(kw in question for kw in ["access review", "account review", "user access", "access recertification"]):
        return "access_reviews"
    
    # Data Classification
    if any(kw in question for kw in ["data classification", "information classification", "classify data"]):
        return "data_classification"
    
    # Encryption
    if any(kw in question for kw in ["encryption", "encrypt", "cryptographic"]):
        return "encryption_status"
    
    # DLP
    if any(kw in question for kw in ["dlp", "data loss", "data leakage", "data exfiltration"]):
        return "dlp_status"
    
    # Data Retention
    if any(kw in question for kw in ["data retention", "retention policy", "data disposal", "data deletion"]):
        return "data_retention"
    
    # Network Segmentation
    if any(kw in question for kw in ["network segmentation", "network segregation", "network isolation"]):
        return "network_segmentation"
    
    # Firewall Management
    if any(kw in question for kw in ["firewall", "network security", "perimeter security"]):
        return "firewall_management"
    
    # Vulnerability Scanning
    if any(kw in question for kw in ["vulnerability scan", "vuln scan", "security scan"]):
        return "vuln_scanning"
    
    # Patch Management
    if any(kw in question for kw in ["patch", "update management", "security update"]):
        return "patch_management"
    
    # Incident Response Plan
    if any(kw in question for kw in ["incident response", "security incident", "breach response", "ir plan"]):
        return "ir_plan"
    
    # Security Monitoring
    if any(kw in question for kw in ["security monitoring", "log monitoring", "siem", "intrusion detection"]):
        return "security_monitoring"
    
    # Breach Response
    if any(kw in question for kw in ["breach response", "incident response time", "security incident sla"]):
        return "breach_response"
    
    # Forensic Capabilities
    if any(kw in question for kw in ["forensic", "investigation", "digital evidence"]):
        return "forensic_capabilities"
    
    # Vendor Assessment
    if any(kw in question for kw in ["vendor assessment", "supplier assessment", "third party assessment"]):
        return "vendor_assessment"
    
    # Vendor Contracts
    if any(kw in question for kw in ["vendor contract", "supplier contract", "third party agreement"]):
        return "vendor_contracts"
    
    # Third Party Access
    if any(kw in question for kw in ["third party access", "vendor access", "supplier access"]):
        return "third_party_access"
    
    # Vendor Incidents
    if any(kw in question for kw in ["vendor incident", "supplier incident", "third party incident"]):
        return "vendor_incidents"
    
    return None

def map_answer_to_option(field, answer):
    """Map a given answer to standardized options"""
    answer_lower = answer.lower()
    
    # MFA Status
    if field == "mfa_status":
        if any(kw in answer_lower for kw in ["not", "none", "no"]):
            return "Not implemented"
        elif any(kw in answer_lower for kw in ["privileged", "admin", "critical"]):
            return "For privileged users only"
        elif any(kw in answer_lower for kw in ["employee", "staff", "internal"]):
            return "For all employees"
        elif any(kw in answer_lower for kw in ["third party", "vendor", "all user", "everyone"]):
            return "For all users including third parties"
        else:
            return "Not implemented"
    
    # Password Policy
    if field == "password_policy":
        if "14" in answer_lower or any(kw in answer_lower for kw in ["very strong", "highest", "robust"]):
            return "Very strong (14+ chars with complexity)"
        elif "12" in answer_lower or any(kw in answer_lower for kw in ["strong", "complex", "symbol", "number"]):
            return "Strong (12+ chars, mixed case, symbols, numbers)"
        elif "10" in answer_lower or any(kw in answer_lower for kw in ["medium", "mixed case"]):
            return "Medium (10+ chars, mixed case)"
        else:
            return "Basic (8+ characters)"
    
    # Privileged Access
    if field == "privileged_access":
        if any(kw in answer_lower for kw in ["comprehensive", "monitor", "full", "complete"]):
            return "Comprehensive PAM with monitoring"
        elif any(kw in answer_lower for kw in ["pam", "some system", "partial"]):
            return "PAM solution for some systems"
        elif any(kw in answer_lower for kw in ["manual", "track", "spreadsheet"]):
            return "Manual tracking"
        else:
            return "No specific management"
    
    # And similar mappings for other fields...
    # For brevity, I'll implement the logic for a few key fields and use defaults for others
    
    # Default mappings based on common responses
    if any(kw in answer_lower for kw in ["none", "no", "not", "never", "ad hoc"]):
        return get_lowest_option(field)
    elif any(kw in answer_lower for kw in ["basic", "minimal", "limited", "some"]):
        return get_low_option(field)
    elif any(kw in answer_lower for kw in ["good", "regular", "most", "many"]):
        return get_medium_option(field)
    elif any(kw in answer_lower for kw in ["comprehensive", "complete", "all", "full", "advanced"]):
        return get_highest_option(field)
    
    # Default to middle option if we can't determine
    return get_medium_option(field)

def get_lowest_option(field):
    """Get the lowest (highest risk) option for a field"""
    options = {
        "mfa_status": "Not implemented",
        "password_policy": "Basic (8+ characters)",
        "privileged_access": "No specific management",
        "access_reviews": "Never/ad hoc",
        "data_classification": "No formal classification",
        "encryption_status": "Minimal/ad hoc encryption",
        "dlp_status": "No DLP implementation",
        "data_retention": "No formal policy",
        "network_segmentation": "Minimal/no segmentation",
        "firewall_management": "Basic firewall configuration",
        "vuln_scanning": "Ad hoc or never",
        "patch_management": "Ad hoc patching",
        "ir_plan": "No formal plan",
        "security_monitoring": "Minimal/ad hoc monitoring",
        "breach_response": "No defined SLAs",
        "forensic_capabilities": "No forensic capabilities",
        "vendor_assessment": "No formal assessment",
        "vendor_contracts": "Minimal security language",
        "third_party_access": "Same as employee access",
        "vendor_incidents": "No specific process"
    }
    return options.get(field, "Not implemented")

def get_low_option(field):
    """Get a low (high risk) option for a field"""
    options = {
        "mfa_status": "For privileged users only",
        "password_policy": "Medium (10+ chars, mixed case)",
        "privileged_access": "Manual tracking",
        "access_reviews": "Annually",
        "data_classification": "Basic classification exists but not enforced",
        "encryption_status": "Encryption for some sensitive data",
        "dlp_status": "Basic DLP for email only",
        "data_retention": "Policy exists but not enforced",
        "network_segmentation": "Basic segmentation (e.g., IT vs OT)",
        "firewall_management": "Regular but manual reviews",
        "vuln_scanning": "Annually",
        "patch_management": "Regular but manual patching",
        "ir_plan": "Basic plan but not tested",
        "security_monitoring": "Basic logging without 24/7 monitoring",
        "breach_response": "Within 24 hours for critical systems",
        "forensic_capabilities": "Basic log review capabilities",
        "vendor_assessment": "Basic security questionnaire",
        "vendor_contracts": "Basic security requirements",
        "third_party_access": "Some restrictions for third parties",
        "vendor_incidents": "Basic notification requirements"
    }
    return options.get(field, "Basic implementation")

def get_medium_option(field):
    """Get a medium option for a field"""
    options = {
        "mfa_status": "For all employees",
        "password_policy": "Strong (12+ chars, mixed case, symbols, numbers)",
        "privileged_access": "PAM solution for some systems",
        "access_reviews": "Quarterly",
        "data_classification": "Classification implemented for sensitive data",
        "encryption_status": "Encryption for all sensitive data at rest and in transit",
        "dlp_status": "DLP for email and endpoints",
        "data_retention": "Policy with manual enforcement",
        "network_segmentation": "Moderate segmentation by department/function",
        "firewall_management": "Change management process with reviews",
        "vuln_scanning": "Quarterly",
        "patch_management": "Scheduled patching with SLAs",
        "ir_plan": "Documented plan with annual testing",
        "security_monitoring": "SIEM solution with business hours monitoring",
        "breach_response": "Within 8 hours for critical systems",
        "forensic_capabilities": "Some forensic tools and training",
        "vendor_assessment": "Detailed assessment for critical vendors",
        "vendor_contracts": "Detailed requirements with right-to-audit",
        "third_party_access": "Limited access with additional controls",
        "vendor_incidents": "Formal process for critical vendors"
    }
    return options.get(field, "Standard implementation")

def get_highest_option(field):
    """Get the highest (lowest risk) option for a field"""
    options = {
        "mfa_status": "For all users including third parties",
        "password_policy": "Very strong (14+ chars with complexity)",
        "privileged_access": "Comprehensive PAM with monitoring",
        "access_reviews": "Continuous monitoring",
        "data_classification": "Comprehensive classification enforced for all data",
        "encryption_status": "End-to-end encryption for all data",
        "dlp_status": "Comprehensive DLP across all channels",
        "data_retention": "Automated enforcement of retention policies",
        "network_segmentation": "Zero trust architecture/microsegmentation",
        "firewall_management": "Automated policy management and continuous monitoring",
        "vuln_scanning": "Continuous/automated scanning",
        "patch_management": "Automated patch management with verification",
        "ir_plan": "Comprehensive plan with regular exercises",
        "security_monitoring": "24/7 SOC with advanced analytics",
        "breach_response": "Within 1 hour with automated containment",
        "forensic_capabilities": "Advanced forensics team and tools",
        "vendor_assessment": "Comprehensive assessments with ongoing monitoring",
        "vendor_contracts": "Comprehensive requirements with regular verification",
        "third_party_access": "Just-in-time access with comprehensive monitoring",
        "vendor_incidents": "Comprehensive incident management with all vendors"
    }
    return options.get(field, "Advanced implementation")

def create_chat_message(sender, message, data=None):
    """Add a message to the chat history"""
    st.session_state.conversation.append({
        "sender": sender,
        "message": message,
        "data": data or {},
        "timestamp": datetime.now().isoformat()
    })

def render_chat_message(message):
    """Render a chat message"""
    sender = message.get("sender", "bot")
    message_text = message.get("message", "")
    message_data = message.get("data", {})
    
    if sender == "user":
        st.markdown(f'<div class="chat-message user">{message_text}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message bot">{message_text}</div>', unsafe_allow_html=True)
        
        # Render any attached data visualizations
        if 'risk_score' in message_data:
            render_risk_score_card(message_data)
        
        if 'recommendations' in message_data and message_data['recommendations']:
            render_recommendations_preview(message_data['recommendations'][:3])

def render_risk_score_card(assessment_data):
    """Render risk score card"""
    risk_score = assessment_data.get('risk_score', 0)
    risk_level = assessment_data.get('risk_level', {})
    risk_name = risk_level.get('name', 'Unknown')
    risk_color = risk_level.get('color', 'gray')
    
    risk_class = risk_name.replace(' ', '-').lower()
    
    st.markdown(f"""
    <div class="card">
        <h3>Security Risk Assessment</h3>
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div style="flex: 1; text-align: center;">
                <div style="font-size: 3rem; font-weight: bold; color: {risk_color};">{risk_score:.1f}</div>
                <div style="font-size: 1.2rem;">out of 100</div>
            </div>
            <div style="flex: 2; padding-left: 1rem;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">Risk Level: <span class="risk-{risk_class}">{risk_name.title()}</span></div>
                <div>{risk_level.get('description', '')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_recommendations_preview(recommendations):
    """Render preview of recommendations"""
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

def render_upload_page():
    """Render the questionnaire upload page"""
    st.markdown('<h1 class="main-header">Security & Compliance Advisor</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <h3>Welcome to the Security & Compliance Advisor</h3>
        <p>Upload your security questionnaire in Excel format (XLSX/XLSM) to receive a comprehensive risk assessment and tailored recommendations.</p>
        <p>The advisor will analyze your responses against security best practices and compliance frameworks to identify areas of risk and provide actionable recommendations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload Security Questionnaire", type=["xlsx", "xlsm"])
    
    if uploaded_file is not None:
        with st.spinner("Processing questionnaire..."):
            # Process the uploaded questionnaire
            questionnaire_data = process_excel_questionnaire(uploaded_file)
            
            if questionnaire_data:
                st.session_state.questionnaire_data = questionnaire_data
                
                # Calculate risk score and recommendations
                assessment = calculate_risk_score(questionnaire_data)
                st.session_state.assessment = assessment
                st.session_state.recommendations = assessment.get('recommendations', [])
                
                # Add initial message to conversation
                risk_score = assessment.get('risk_score', 0)
                risk_level = assessment.get('risk_level', {}).get('name', 'unknown')
                rec_count = len(assessment.get('recommendations', []))
                
                message = f"I've analyzed your security questionnaire. Your risk score is {risk_score:.1f} out of 100, which indicates a {risk_level} level. I've identified {rec_count} recommendations to improve your security posture."
                create_chat_message("bot", message, assessment)
                
                # Navigate to chat page
                st.session_state.current_page = 'chat'
                st.experimental_rerun()
            else:
                st.error("Unable to extract questionnaire data from the uploaded file. Please ensure it contains security assessment questions and responses.")

def render_chat_page():
    """Render chat interface page"""
    st.markdown('<h1 class="main-header">Security & Compliance Advisor</h1>', unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    # Input container
    input_container = st.container()
    
    # Render chat messages
    with chat_container:
        for message in st.session_state.conversation:
            render_chat_message(message)
    
    # Input for new message
    with input_container:
        col1, col2 = st.columns([5, 1])
        
        # Define a callback to handle message submission
        def handle_message_submit():
            user_input = st.session_state.chat_input
            if user_input and user_input != st.session_state.get('last_input', ''):
                # Save current input to avoid duplicate processing
                st.session_state.last_input = user_input
                
                # Add user message to conversation
                create_chat_message("user", user_input)
                
                # Process message and generate response
                response_text, response_data = process_chat_message(user_input)
                
                # Add bot response to conversation
                create_chat_message("bot", response_text, response_data)
                
                # Clear input
                st.session_state.chat_input = ""
                
                # Rerun to update UI
                st.experimental_rerun()
        
        with col1:
            # Initialize session state for chat input if not exists
            if 'chat_input' not in st.session_state:
                st.session_state.chat_input = ""
                
            st.text_input(
                "Type your message...", 
                key="chat_input", 
                on_change=handle_message_submit
            )
        
        with col2:
            st.button("Send", on_click=handle_message_submit)

def process_chat_message(message):
    """Process a chat message and generate a response"""
    # Convert message to lowercase for easier matching
    message_lower = message.lower()
    
    # Check for specific intents
    if any(kw in message_lower for kw in ["risk", "score", "assessment", "analyze"]):
        # Risk assessment request
        if st.session_state.assessment:
            risk_score = st.session_state.assessment.get('risk_score', 0)
            risk_level = st.session_state.assessment.get('risk_level', {}).get('name', 'unknown')
            
            response = f"Based on your questionnaire, your overall security risk score is {risk_score:.1f} out of 100, placing you at a {risk_level} level. Would you like to see a detailed breakdown of risk factors or specific recommendations?"
            return response, st.session_state.assessment
        else:
            return "I don't have enough information to provide a risk assessment. Please upload a security questionnaire first.", {}
    
    elif any(kw in message_lower for kw in ["recommend", "suggestion", "improve", "fix"]):
        # Recommendation request
        if st.session_state.recommendations:
            recs = st.session_state.recommendations[:5]  # Top 5 recommendations
            
            response = "Here are my top recommendations to improve your security posture:\n\n"
            
            return response, {"recommendations": recs}
        else:
            return "I don't have enough information to provide recommendations. Please upload a security questionnaire first.", {}
    
    elif any(kw in message_lower for kw in ["compliance", "framework", "standard", "regulation"]):
        # Compliance information request
        if st.session_state.assessment and 'framework_compliance' in st.session_state.assessment:
            framework_data = st.session_state.assessment['framework_compliance']
            
            response = "Based on your questionnaire, here's your estimated compliance status with major frameworks:\n\n"
            
            for framework_id, framework in st.session_state.frameworks.items():
                if framework_id in framework_data:
                    compliance_score = framework_data[framework_id].get('compliance_score', 0)
                    framework['coverage'] = compliance_score
                    
                    response += f"• {framework['name']}: {compliance_score:.1f}% coverage\n"
            
            response += "\nWould you like specific information about any of these frameworks or gap areas that need to be addressed?"
            
            return response, {"frameworks": st.session_state.frameworks}
        else:
            return "I don't have enough information to assess your compliance status. Please upload a security questionnaire first.", {}
    
    elif any(kw in message_lower for kw in ["dashboard", "visualization", "chart", "graph"]):
        # Dashboard request
        if st.session_state.assessment:
            return "I've prepared a dashboard with your security assessment results. You can view it by clicking on the 'Risk Dashboard' button in the sidebar.", {}
        else:
            return "I don't have enough data to generate a dashboard. Please upload a security questionnaire first.", {}
    
    elif any(kw in message_lower for kw in ["help", "how", "what can you", "capabilities"]):
        # Help request
        response = """I'm your Security & Compliance Advisor. Here's how I can help you:

1. **Risk Assessment**: I can analyze your security questionnaire to identify risks and vulnerabilities
2. **Recommendations**: I can provide tailored recommendations to improve your security posture
3. **Compliance Guidance**: I can help you understand your compliance status with major security frameworks
4. **Security Best Practices**: I can provide information on security controls and best practices

You can ask me questions about specific security areas like access control, encryption, incident response, etc."""
        
        return response, {}
    
    else:
        # Try to handle questions about specific security controls
        security_topics = {
            "mfa": "Multi-Factor Authentication (MFA) is one of the most effective controls to prevent unauthorized access. It requires users to provide multiple forms of verification before gaining access to systems or data.",
            "password": "Strong password policies are essential for security. Best practices include requiring long passwords (14+ characters), checking against known compromised passwords, and implementing a password manager.",
            "access control": "Access control ensures that only authorized users can access sensitive resources. The principle of least privilege is key - users should only have access to what they need for their job functions.",
            "encryption": "Encryption protects data confidentiality by converting it into an unreadable format that can only be decrypted with the proper key. You should encrypt sensitive data both at rest and in transit.",
            "firewall": "Firewalls protect your network by controlling incoming and outgoing traffic based on predetermined security rules. Next-generation firewalls (NGFW) provide additional capabilities like application awareness and intrusion prevention.",
            "vulnerability": "Vulnerability management is the process of identifying, evaluating, treating, and reporting on security vulnerabilities. Regular scanning and prompt patching are essential components.",
            "patch": "Patch management ensures systems are updated with the latest security fixes. Establish clear SLAs for patching based on vulnerability severity (e.g., critical patches within 24-72 hours).",
            "incident": "Incident response is your plan for handling security breaches. An effective plan includes preparation, detection, containment, eradication, recovery, and lessons learned phases.",
            "backup": "Backups protect against data loss from ransomware, system failures, or human error. Follow the 3-2-1 rule: 3 copies of data, on 2 different media types, with 1 copy offsite.",
            "vendor": "Vendor risk management assesses and mitigates risks associated with third-party vendors. Implement a formal assessment process, security requirements in contracts, and ongoing monitoring."
        }
        
        for topic, info in security_topics.items():
            if topic in message_lower:
                # Check if we have assessment data for this topic
                related_field = None
                if topic == "mfa":
                    related_field = "mfa_status"
                elif topic == "password":
                    related_field = "password_policy"
                elif topic == "access control":
                    related_field = "privileged_access"
                elif topic == "encryption":
                    related_field = "encryption_status"
                elif topic == "firewall":
                    related_field = "firewall_management"
                elif topic == "vulnerability":
                    related_field = "vuln_scanning"
                elif topic == "patch":
                    related_field = "patch_management"
                elif topic == "incident":
                    related_field = "ir_plan"
                elif topic == "vendor":
                    related_field = "vendor_assessment"
                
                personalized_info = ""
                if related_field and related_field in st.session_state.questionnaire_data:
                    current_status = st.session_state.questionnaire_data[related_field]
                    personalized_info = f"\n\nBased on your questionnaire, your current approach is: {current_status}."
                
                return info + personalized_info, {}
        
        # Default response
        return "I'm here to help with your security and compliance questions. You can ask about your risk assessment, specific security controls, compliance frameworks, or recommendations to improve your security posture.", {}

def render_dashboard_page():
    """Render risk dashboard page"""
    st.markdown('<h1 class="main-header">Risk Assessment Dashboard</h1>', unsafe_allow_html=True)
    
    # Check if assessment is available
    if not st.session_state.assessment:
        st.warning("No risk assessment data available. Please upload a security questionnaire first.")
        
        if st.button("Upload Questionnaire"):
            st.session_state.current_page = 'upload'
            st.experimental_rerun()
            
        return
    
    # Get assessment data
    assessment = st.session_state.assessment
    risk_score = assessment.get('risk_score', 0)
    risk_level = assessment.get('risk_level', {})
    explanation = assessment.get('explanation', {})
    recommendations = assessment.get('recommendations', [])
    framework_compliance = assessment.get('framework_compliance', {})
    category_scores = assessment.get('category_scores', {})
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card(
            "Risk Score", 
            f"{risk_score:.1f}", 
            "/100", 
            risk_level.get('color', '#6B7280')
        )
    
    with col2:
        risk_factors = len(explanation.get('top_factors', []))
        render_metric_card(
            "Risk Factors", 
            f"{risk_factors}", 
            "Identified", 
            "#1E40AF"
        )
    
    with col3:
        rec_count = len(recommendations)
        render_metric_card(
            "Recommendations", 
            f"{rec_count}", 
            "Actions", 
            "#059669"
        )
    
    with col4:
        # Calculate potential improvement
        potential_improvement = min(100, risk_score * 0.3)  # Simplified estimate
        render_metric_card(
            "Potential Improvement", 
            f"{potential_improvement:.1f}", 
            "Points", 
            "#D97706"
        )
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown('<h2 class="sub-header">Risk Breakdown</h2>', unsafe_allow_html=True)
        
        # Risk factors chart
        if explanation.get('top_factors'):
            render_risk_factors_chart(explanation['top_factors'])
        
        # Risk categories chart
        if category_scores:
            render_risk_categories_chart(category_scores)

            with col2:
        st.markdown('<h2 class="sub-header">Prioritized Actions</h2>', unsafe_allow_html=True)
        
        if recommendations:
            render_recommendations_list(recommendations[:10])
        else:
            st.info("No recommendations available.")
    
    # Compliance impact section
    st.markdown('<h2 class="sub-header">Compliance Impact</h2>', unsafe_allow_html=True)
    render_compliance_impact(framework_compliance)

def render_metric_card(label, value, suffix, color):
    """Render a metric card"""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: {color};">{value}<span style="font-size: 1rem; color: #6B7280;">{suffix}</span></div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def render_risk_factors_chart(factors):
    """Render risk factors chart"""
    factors = sorted(factors, key=lambda x: x['impact'])

    display_factors = []

    neg_factors = [f for f in factors if f['impact'] < 0]
    if neg_factors:
        display_factors.extend(neg_factors[:2])
    
    pos_factors = [f for f in factors if f['impact'] > 0]
    if pos_factors:
        display_factors.extend(pos_factors[-8:])
    
    labels = [f"{f['description'][:30]}..." if len(f['description']) > 30 else f['description'] for f in display_factors]
    values = [f['impact'] for f in display_factors]
    colors = ['#059669' if v < 0 else '#DC2626' for v in values]
    
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

def render_risk_categories_chart(category_scores):
    """Render risk categories chart"""
    categories = []
    scores = []
    
    for category, score in category_scores.items():
        categories.append(category.replace('_', ' ').title())
        scores.append(score)
    
    fig = go.Figure(data=[go.Pie(
        labels=categories,
        values=scores,
        hole=.4,
        marker_colors=px.colors.qualitative.Set2
    )])
    
    fig.update_layout(
        title="Risk by Category",
        height=350,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_recommendations_list(recommendations):
    """Render recommendations list"""
    for i, rec in enumerate(recommendations):
        impact_class = "high-impact" if rec.get('impact') == "High" else (
            "medium-impact" if rec.get('impact') == "Medium" else
            import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re
import base64
import json

# Set page config
st.set_page_config(
    page_title="Security & Compliance Advisor",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
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

# Define risk scoring function
def calculate_risk_score(questionnaire_data):
    """Calculate risk score based on questionnaire responses"""
    # Define weights for different categories
    category_weights = {
        "access_control": 0.25,
        "data_protection": 0.20,
        "network_security": 0.15,
        "vulnerability_management": 0.15,
        "incident_response": 0.15,
        "vendor_management": 0.10
    }
    
    # Define score mappings for key fields
    score_mappings = {
        # Access Control Category
        "mfa_status": {
            "Not implemented": 100,
            "For privileged users only": 60,
            "For all employees": 30,
            "For all users including third parties": 0
        },
        "password_policy": {
            "Basic (8+ characters)": 80,
            "Medium (10+ chars, mixed case)": 50,
            "Strong (12+ chars, mixed case, symbols, numbers)": 20,
            "Very strong (14+ chars with complexity)": 0
        },
        "privileged_access": {
            "No specific management": 100,
            "Manual tracking": 70,
            "PAM solution for some systems": 40,
            "Comprehensive PAM with monitoring": 0
        },
        "access_reviews": {
            "Never/ad hoc": 100,
            "Annually": 70,
            "Quarterly": 40,
            "Monthly": 20,
            "Continuous monitoring": 0
        },
        
        # Data Protection Category
        "data_classification": {
            "No formal classification": 100,
            "Basic classification exists but not enforced": 70,
            "Classification implemented for sensitive data": 40,
            "Comprehensive classification enforced for all data": 0
        },
        "encryption_status": {
            "Minimal/ad hoc encryption": 100,
            "Encryption for some sensitive data": 60,
            "Encryption for all sensitive data at rest and in transit": 20,
            "End-to-end encryption for all data": 0
        },
        "dlp_status": {
            "No DLP implementation": 100,
            "Basic DLP for email only": 70,
            "DLP for email and endpoints": 40,
            "Comprehensive DLP across all channels": 0
        },
        "data_retention": {
            "No formal policy": 100,
            "Policy exists but not enforced": 70,
            "Policy with manual enforcement": 40,
            "Automated enforcement of retention policies": 0
        },
        
        # Network Security Category
        "network_segmentation": {
            "Minimal/no segmentation": 100,
            "Basic segmentation (e.g., IT vs OT)": 70,
            "Moderate segmentation by department/function": 40,
            "Zero trust architecture/microsegmentation": 0
        },
        "firewall_management": {
            "Basic firewall configuration": 80,
            "Regular but manual reviews": 60,
            "Change management process with reviews": 30,
            "Automated policy management and continuous monitoring": 0
        },
        
        # Vulnerability Management Category
        "vuln_scanning": {
            "Ad hoc or never": 100,
            "Annually": 80,
            "Quarterly": 60,
            "Monthly": 30,
            "Continuous/automated scanning": 0
        },
        "patch_management": {
            "Ad hoc patching": 100,
            "Regular but manual patching": 70,
            "Scheduled patching with SLAs": 30,
            "Automated patch management with verification": 0
        },
        
        # Incident Response Category
        "ir_plan": {
            "No formal plan": 100,
            "Basic plan but not tested": 70,
            "Documented plan with annual testing": 30,
            "Comprehensive plan with regular exercises": 0
        },
        "security_monitoring": {
            "Minimal/ad hoc monitoring": 100,
            "Basic logging without 24/7 monitoring": 70,
            "SIEM solution with business hours monitoring": 40,
            "24/7 SOC with advanced analytics": 0
        },
        "breach_response": {
            "No defined SLAs": 100,
            "Within 24 hours for critical systems": 60,
            "Within 8 hours for critical systems": 30,
            "Within 1 hour with automated containment": 0
        },
        "forensic_capabilities": {
            "No forensic capabilities": 100,
            "Basic log review capabilities": 70,
            "Some forensic tools and training": 40,
            "Advanced forensics team and tools": 0
        },
        
        # Vendor Management Category
        "vendor_assessment": {
            "No formal assessment": 100,
            "Basic security questionnaire": 70,
            "Detailed assessment for critical vendors": 40,
            "Comprehensive assessments with ongoing monitoring": 0
        },
        "vendor_contracts": {
            "Minimal security language": 100,
            "Basic security requirements": 70,
            "Detailed requirements with right-to-audit": 30,
            "Comprehensive requirements with regular verification": 0
        },
        "third_party_access": {
            "Same as employee access": 100,
            "Some restrictions for third parties": 70,
            "Limited access with additional controls": 30,
            "Just-in-time access with comprehensive monitoring": 0
        },
        "vendor_incidents": {
            "No specific process": 100,
            "Basic notification requirements": 70,
            "Formal process for critical vendors": 40,
            "Comprehensive incident management with all vendors": 0
        }
    }
    
    # Map questions to categories
    category_mappings = {
        "access_control": ["mfa_status", "password_policy", "privileged_access", "access_reviews"],
        "data_protection": ["data_classification", "encryption_status", "dlp_status", "data_retention"],
        "network_security": ["network_segmentation", "firewall_management"],
        "vulnerability_management": ["vuln_scanning", "patch_management"],
        "incident_response": ["ir_plan", "security_monitoring", "breach_response", "forensic_capabilities"],
        "vendor_management": ["vendor_assessment", "vendor_contracts", "third_party_access", "vendor_incidents"]
    }
    
    # Calculate category scores
    category_scores = {}
    
    for category, fields in category_mappings.items():
        total_score = 0
        valid_fields = 0
        
        for field in fields:
            if field in questionnaire_data and questionnaire_data[field] in score_mappings.get(field, {}):
                total_score += score_mappings[field][questionnaire_data[field]]
                valid_fields += 1
        
        # Calculate average score for category
        if valid_fields > 0:
            category_scores[category] = total_score / valid_fields
        else:
            category_scores[category] = 50  # Default score if no valid fields
    
    # Calculate weighted overall risk score
    risk_score = 0
    for category, score in category_scores.items():
        risk_score += score * category_weights.get(category, 0)
    
    # Generate top factors
    factors = []
    for category, fields in category_mappings.items():
        for field in fields:
            if field in questionnaire_data and questionnaire_data[field] in score_mappings.get(field, {}):
                score = score_mappings[field][questionnaire_data[field]]
                if score >= 60:  # Only include high-risk factors
                    impact = score * category_weights.get(category, 0) * 0.1
                    
                    factor = {
                        "feature": field,
                        "description": f"{field.replace('_', ' ').title()}: {questionnaire_data[field]}",
                        "impact": impact,
                        "direction": "negative"
                    }
                    factors.append(factor)
    
    # Sort factors by impact (highest first)
    factors.sort(key=lambda x: x['impact'], reverse=True)
    
    # Add some positive factors (good practices)
    for category, fields in category_mappings.items():
        for field in fields:
            if field in questionnaire_data and questionnaire_data[field] in score_mappings.get(field, {}):
                score = score_mappings[field][questionnaire_data[field]]
                if score <= 20:  # Good practice
                    impact = -1 * (100 - score) * category_weights.get(category, 0) * 0.02
                    
                    factor = {
                        "feature": field,
                        "description": f"Good Practice: {field.replace('_', ' ').title()} - {questionnaire_data[field]}",
                        "impact": impact,
                        "direction": "positive"
                    }
                    factors.append(factor)
    
    # Organize factors by category
    categories = {}
    for category_name, fields in category_mappings.items():
        category_display = category_name.replace('_', ' ').title()
        categories[category_display] = [f for f in factors if f['feature'] in fields]
    
    # Calculate framework compliance
    framework_compliance = calculate_framework_compliance(questionnaire_data, category_scores)
    
    # Generate risk level
    risk_level = get_risk_level(risk_score)
    
    # Generate recommendations
    recommendations = generate_recommendations(questionnaire_data, score_mappings)
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "explanation": {
            "top_factors": factors[:10],
            "categories": categories,
            "summary": "The risk score is based on the identified security weaknesses across multiple domains."
        },
        "recommendations": recommendations,
        "framework_compliance": framework_compliance,
        "category_scores": category_scores,
        "timestamp": datetime.now().isoformat()
    }

def get_risk_level(score):
    """Determine risk level based on score"""
    if score < 20:
        return {
            "name": "very low risk",
            "description": "Your security posture is excellent with minimal areas for improvement.",
            "color": "green"
        }
    elif score < 40:
        return {
            "name": "low risk",
            "description": "Your security posture is good with a few minor areas for improvement.",
            "color": "blue"
        }
    elif score < 60:
        return {
            "name": "moderate risk",
            "description": "Your security posture needs attention in several key areas.",
            "color": "yellow"
        }
    elif score < 80:
        return {
            "name": "high risk",
            "description": "Your security posture has significant vulnerabilities that need immediate attention.",
            "color": "orange"
        }
    else:
        return {
            "name": "critical risk",
            "description": "Your security posture has critical vulnerabilities requiring urgent remediation.",
            "color": "red"
        }

def calculate_framework_compliance(questionnaire_data, category_scores):
    """Calculate compliance levels for different frameworks"""
    # Map categories to frameworks
    framework_mappings = {
        "iso27001": {
            "access_control": 0.25,
            "data_protection": 0.2,
            "network_security": 0.15,
            "vulnerability_management": 0.15,
            "incident_response": 0.15,
            "vendor_management": 0.1
        },
        "nist_csf": {
            "access_control": 0.2,
            "data_protection": 0.2,
            "network_security": 0.15,
            "vulnerability_management": 0.2,
            "incident_response": 0.15,
            "vendor_management": 0.1
        },
        "gdpr": {
            "access_control": 0.2,
            "data_protection": 0.4,
            "network_security": 0.1,
            "vulnerability_management": 0.1,
            "incident_response": 0.1,
            "vendor_management": 0.1
        },
        "hipaa": {
            "access_control": 0.25,
            "data_protection": 0.3,
            "network_security": 0.1,
            "vulnerability_management": 0.1,
            "incident_response": 0.15,
            "vendor_management": 0.1
        },
        "pci_dss": {
            "access_control": 0.3,
            "data_protection": 0.25,
            "network_security": 0.2,
            "vulnerability_management": 0.15,
            "incident_response": 0.05,
            "vendor_management": 0.05
        }
    }
    
    framework_compliance = {}
    
    for framework, category_weights in framework_mappings.items():
        compliance_score = 0
        
        for category, weight in category_weights.items():
            if category in category_scores:
                # Convert risk score to compliance percentage (100 - risk_score)
                compliance_score += (100 - category_scores[category]) * weight
        
        framework_compliance[framework] = {
            "compliance_score": compliance_score,
            "gap_areas": []
        }
        
        # Identify gap areas based on category scores
        for category, score in category_scores.items():
            if score >= 70 and category in category_weights and category_weights[category] >= 0.15:
                framework_compliance[framework]["gap_areas"].append({
                    "category": category,
                    "score": score
                })
    
    return framework_compliance

def generate_recommendations(questionnaire_data, score_mappings):
    """Generate recommendations based on questionnaire data"""
    recommendations = []
    
    # Map fields to specific recommendations
    field_recommendations = {
        "mfa_status": {
            "title": "Implement Multi-Factor Authentication",
            "description": "Deploy MFA for all users, especially those with privileged access. This will significantly reduce the risk of unauthorized access due to compromised credentials.",
            "category": "Access Control",
            "effort": "Medium"
        },
        "password_policy": {
            "title": "Strengthen Password Policy",
            "description": "Update your password policy to require longer passwords (14+ characters) with complexity requirements. Implement a password manager to help users maintain strong, unique passwords.",
            "category": "Access Control",
            "effort": "Low"
        },
        "privileged_access": {
            "title": "Implement Privileged Access Management",
            "description": "Deploy a PAM solution to manage, monitor, and control privileged accounts access. Include just-in-time access and session recording for critical systems.",
            "category": "Access Control",
            "effort": "High"
        },
        "access_reviews": {
            "title": "Establish Regular Access Reviews",
            "description": "Implement quarterly access reviews for all systems, especially those storing sensitive data. Automate the review process where possible to ensure consistency and completion.",
            "category": "Access Control",
            "effort": "Medium"
        },
        "data_classification": {
            "title": "Implement Data Classification",
            "description": "Establish a formal data classification framework and enforce controls based on data sensitivity levels. Train users on proper handling of sensitive information.",
            "category": "Data Protection",
            "effort": "Medium"
        },
        "encryption_status": {
            "title": "Enhance Data Encryption",
            "description": "Implement comprehensive encryption for sensitive data both at rest and in transit using industry-standard algorithms. Establish a key management process.",
            "category": "Data Protection",
            "effort": "Medium"
        },
        "dlp_status": {
            "title": "Deploy Data Loss Prevention",
            "description": "Implement a DLP solution to monitor and protect sensitive data across endpoints, networks, and cloud services. Start with high-risk channels like email and gradually expand coverage.",
            "category": "Data Protection",
            "effort": "High"
        },
        "data_retention": {
            "title": "Implement Data Retention Policy",
            "description": "Develop and enforce a formal data retention policy that automatically archives or deletes data based on retention requirements. Consider compliance requirements in your retention schedules.",
            "category": "Data Protection",
            "effort": "Medium"
        },
        "network_segmentation": {
            "title": "Implement Network Segmentation",
            "description": "Segment your network based on security requirements and data sensitivity. Use firewalls, VLANs, and access controls to restrict lateral movement within the network.",
            "category": "Network Security",
            "effort": "High"
        },
        "firewall_management": {
            "title": "Enhance Firewall Management",
            "description": "Implement a formal change management process for firewall rules, regular rule reviews, and automated policy validation to identify potential security gaps or misconfigurations.",
            "category": "Network Security",
            "effort": "Medium"
        },
        "vuln_scanning": {
            "title": "Implement Regular Vulnerability Scanning",
            "description": "Establish automated, regular vulnerability scanning of all systems and applications with a formal process for remediation prioritized by risk level.",
            "category": "Vulnerability Management",
            "effort": "Medium"
        },
        "patch_management": {
            "title": "Improve Patch Management",
            "description": "Implement an automated patch management system with defined SLAs for critical, high, medium, and low vulnerabilities. Establish a verification process to ensure patches are applied successfully.",
            "category": "Vulnerability Management",
            "effort": "High"
        },
        "ir_plan": {
            "title": "Develop Comprehensive Incident Response Plan",
            "description": "Create and regularly test a formal incident response plan that includes roles, responsibilities, and procedures for handling security incidents. Conduct tabletop exercises to validate the plan.",
            "category": "Incident Response",
            "effort": "Medium"
        },
        "security_monitoring": {
            "title": "Enhance Security Monitoring",
            "description": "Upgrade your security monitoring capabilities with a SIEM solution and 24/7 coverage. Implement automated alerting for critical security events and establish an escalation process.",
            "category": "Incident Response",
            "effort": "High"
        },
        "breach_response": {
            "title": "Improve Breach Response Capabilities",
            "description": "Establish clear SLAs for incident response based on severity levels. Implement automation for containment of common threats and develop playbooks for efficient response.",
            "category": "Incident Response",
            "effort": "Medium"
        },
        "forensic_capabilities": {
            "title": "Enhance Forensic Capabilities",
            "description": "Develop in-house forensic capabilities or establish relationships with external forensic providers. Ensure proper logging and evidence preservation mechanisms are in place.",
            "category": "Incident Response",
            "effort": "High"
        },
        "vendor_assessment": {
            "title": "Formalize Vendor Risk Assessment",
            "description": "Develop a comprehensive vendor risk assessment process that includes initial vetting, ongoing monitoring, and regular reassessment. Prioritize vendors based on data access and business criticality.",
            "category": "Vendor Management",
            "effort": "Medium"
        },
        "vendor_contracts": {
            "title": "Enhance Vendor Security Requirements",
            "description": "Update vendor contracts to include detailed security requirements, right-to-audit clauses, and breach notification obligations. Establish a process to verify compliance with these requirements.",
            "category": "Vendor Management",
            "effort": "Medium"
        },
        "third_party_access": {
            "title": "Secure Third-Party Access",
            "description": "Implement just-in-time access with comprehensive monitoring for all third-party access to your systems and data. Use separate VPNs or other secure access methods specifically for third parties.",
            "category": "Vendor Management",
            "effort": "Medium"
        },
        "vendor_incidents": {
            "title": "Improve Vendor Incident Management",
            "description": "Establish a formal process for handling security incidents involving vendors, including communication protocols, response procedures, and post-incident reviews.",
            "category": "Vendor Management",
            "effort": "Low"
        }
    }
    
    # Generate recommendations for high-risk areas
    for field, values in score_mappings.items():
        if field in questionnaire_data and questionnaire_data[field] in values:
            score = values[questionnaire_data[field]]
            
            # If score is high (indicating risk), add recommendation
            if score >= 60 and field in field_recommendations:
                rec = field_recommendations[field].copy()
                
                # Set impact based on score
                if score >= 90:
                    rec['impact'] = "High"
                elif score >= 70:
                    rec['impact'] = "Medium"
                else:
                    rec['impact'] = "Low"
                
                recommendations.append(rec)
    
    # Sort recommendations by impact
    impact_order = {"High": 0, "Medium": 1, "Low": 2}
    recommendations.sort(key=lambda x: impact_order.get(x.get('impact', "Low"), 3))
    
    return recommendations

def process_excel_questionnaire(file):
    """Process the uploaded Excel questionnaire file"""
    try:
        # Read Excel file
        df = pd.read_excel(file, engine='openpyxl', sheet_name=None)
        
        # Extract questionnaire data
        questionnaire_data = {}
        
        # Look for the main questionnaire sheet
        main_sheet = None
        for sheet_name, sheet_df in df.items():
            if "questionnaire" in sheet_name.lower() or "assessment" in sheet_name.lower() or "security" in sheet_name.lower():
                main_sheet = sheet_df
                break
        
        # If no specific sheet found, use the first one
        if main_sheet is None and len(df) > 0:
            main_sheet = list(df.values())[0]
        
        # Process the main sheet if found
        if main_sheet is not None:
            # Identify question and answer columns
            answer_col = None
            question_col = None
            
            for col in main_sheet.columns:
                col_lower = col.lower() if isinstance(col, str) else str(col).lower()
                if any(kw in col_lower for kw in ["answer", "response", "value", "selection"]):
                    answer_col = col
                if any(kw in col_lower for kw in ["question", "control", "requirement", "check"]):
                    question_col = col
            
            # If question and answer columns found
            if question_col and answer_col:
                for _, row in main_sheet.iterrows():
                    question = str(row[question_col]).strip()
                    answer = str(row[answer_col]).strip() if pd.notna(row[answer_col]) else ""
                    
                    # Map to our expected questionnaire fields
                    field = map_question_to_field(question)
                    if field and answer:
                        questionnaire_data[field] = map_answer_to_option(field, answer)
        
        # If we couldn't extract using standard approach, try to find data in any structured format
        if not questionnaire_data:
            for sheet_name, sheet_df in df.items():
                for i, row in sheet_df.iterrows():
                    for col in sheet_df.columns:
                        # Check if cell contains a key question keyword
                        cell_value = str(row[col]).lower() if pd.notna(row[col]) else ""
                        if any(kw in cell_value for kw in ["mfa", "password", "encryption", "firewall", "vulnerability", "incident"]):
                            # Look for an answer in the nearby cells
                            for offset in range(1, 4):
                                if i + offset < len(sheet_df):
                                    potential_answer = str(sheet_df.iloc[i + offset][col]).strip() if pd.notna(sheet_df.iloc[i + offset][col]) else ""
                                    if potential_answer and potential_answer.lower() not in ["yes", "no", "n/a", "question", "control"]:
                                        field = map_question_to_field(cell_value)
                                        if field:
                                            questionnaire_data[field] = map_answer_to_option(field, potential_answer)
                                            break
        
        return questionnaire_data
    
    except Exception as e:
        st.error(f"Error processing Excel file: {str(e)}")
        return {}

def map_question_to_field(question):
    """Map a question to a standardized field name"""
    question = question.lower()
    
    # MFA
    if any(kw in question for kw in ["multi-factor", "multifactor", "mfa", "two-factor", "2fa"]):
        return "mfa_status"
    
    # Password Policy
    if any(kw in question for kw in ["password policy", "password requirement", "password complexity"]):
        return "password_policy"
    
    # Privileged Access
    if any(kw in question for kw in ["privileged access", "admin account", "administrator", "elevated privilege"]):
        return "privileged_access"
    
    # Access Reviews
    if any(kw in question for kw in ["access review", "account review", "user access", "access recertification"]):
        return "access_reviews"
    
    # Data Classification
    if any(kw in question for kw in ["data classification", "information classification", "classify data"]):
        return "data_classification"
    
    # Encryption
    if any(kw in question for kw in ["encryption", "encrypt", "cryptographic"]):
        return "encryption_status"
    
    # DLP
    if any(kw in question for kw in ["dlp", "data loss", "data leakage", "data exfiltration"]):
        return "dlp_status"
    
    # Data Retention
    if any(kw in question for kw in ["data retention", "retention policy", "data disposal", "data deletion"]):
        return "data_retention"
    
    # Network Segmentation
    if any(kw in question for kw in ["network segmentation", "network segregation", "network isolation"]):
        return "network_segmentation"
    
    # Firewall Management
    if any(kw in question for kw in ["firewall", "network security", "perimeter security"]):
        return "firewall_management"
    
    # Vulnerability Scanning
    if any(kw in question for kw in ["vulnerability scan", "vuln scan", "security scan"]):
        return "vuln_scanning"
    
    # Patch Management
    if any(kw in question for kw in ["patch", "update management", "security update"]):
        return "patch_management"
    
    # Incident Response Plan
    if any(kw in question for kw in ["incident response", "security incident", "breach response", "ir plan"]):
        return "ir_plan"
    
    # Security Monitoring
    if any(kw in question for kw in ["security monitoring", "log monitoring", "siem", "intrusion detection"]):
        return "security_monitoring"
    
    # Breach Response
    if any(kw in question for kw in ["breach response", "incident response time", "security incident sla"]):
        return "breach_response"
    
    # Forensic Capabilities
    if any(kw in question for kw in ["forensic", "investigation", "digital evidence"]):
        return "forensic_capabilities"
    
    # Vendor Assessment
    if any(kw in question for kw in ["vendor assessment", "supplier assessment", "third party assessment"]):
        return "vendor_assessment"
    
    # Vendor Contracts
    if any(kw in question for kw in ["vendor contract", "supplier contract", "third party agreement"]):
        return "vendor_contracts"
    
    # Third Party Access
    if any(kw in question for kw in ["third party access", "vendor access", "supplier access"]):
        return "third_party_access"
    
    # Vendor Incidents
    if any(kw in question for kw in ["vendor incident", "supplier incident", "third party incident"]):
        return "vendor_incidents"
    
    return None

def map_answer_to_option(field, answer):
    """Map a given answer to standardized options"""
    answer_lower = answer.lower()
    
    # MFA Status
    if field == "mfa_status":
        if any(kw in answer_lower for kw in ["not", "none", "no"]):
            return "Not implemented"
        elif any(kw in answer_lower for kw in ["privileged", "admin", "critical"]):
            return "For privileged users only"
        elif any(kw in answer_lower for kw in ["employee", "staff", "internal"]):
            return "For all employees"
        elif any(kw in answer_lower for kw in ["third party", "vendor", "all user", "everyone"]):
            return "For all users including third parties"
        else:
            return "Not implemented"
    
    # Password Policy
    if field == "password_policy":
        if "14" in answer_lower or any(kw in answer_lower for kw in ["very strong", "highest", "robust"]):
            return "Very strong (14+ chars with complexity)"
        elif "12" in answer_lower or any(kw in answer_lower for kw in ["strong", "complex", "symbol", "number"]):
            return "Strong (12+ chars, mixed case, symbols, numbers)"
        elif "10" in answer_lower or any(kw in answer_lower for kw in ["medium", "mixed case"]):
            return "Medium (10+ chars, mixed case)"
        else:
            return "Basic (8+ characters)"
    
    # Privileged Access
    if field == "privileged_access":
        if any(kw in answer_lower for kw in ["comprehensive", "monitor", "full", "complete"]):
            return "Comprehensive PAM with monitoring"
        elif any(kw in answer_lower for kw in ["pam", "some system", "partial"]):
            return "PAM solution for some systems"
        elif any(kw in answer_lower for kw in ["manual", "track", "spreadsheet"]):
            return "Manual tracking"
        else:
            return "No specific management"
    
    # And similar mappings for other fields...
    # For brevity, I'll implement the logic for a few key fields and use defaults for others
    
    # Default mappings based on common responses
    if any(kw in answer_lower for kw in ["none", "no", "not", "never", "ad hoc"]):
        return get_lowest_option(field)
    elif any(kw in answer_lower for kw in ["basic", "minimal", "limited", "some"]):
        return get_low_option(field)
    elif any(kw in answer_lower for kw in ["good", "regular", "most", "many"]):
        return get_medium_option(field)
    elif any(kw in answer_lower for kw in ["comprehensive", "complete", "all", "full", "advanced"]):
        return get_highest_option(field)
    
    # Default to middle option if we can't determine
    return get_medium_option(field)

def get_lowest_option(field):
    """Get the lowest (highest risk) option for a field"""
    options = {
        "mfa_status": "Not implemented",
        "password_policy": "Basic (8+ characters)",
        "privileged_access": "No specific management",
        "access_reviews": "Never/ad hoc",
        "data_classification": "No formal classification",
        "encryption_status": "Minimal/ad hoc encryption",
        "dlp_status": "No DLP implementation",
        "data_retention": "No formal policy",
        "network_segmentation": "Minimal/no segmentation",
        "firewall_management": "Basic firewall configuration",
        "vuln_scanning": "Ad hoc or never",
        "patch_management": "Ad hoc patching",
        "ir_plan": "No formal plan",
        "security_monitoring": "Minimal/ad hoc monitoring",
        "breach_response": "No defined SLAs",
        "forensic_capabilities": "No forensic capabilities",
        "vendor_assessment": "No formal assessment",
        "vendor_contracts": "Minimal security language",
        "third_party_access": "Same as employee access",
        "vendor_incidents": "No specific process"
    }
    return options.get(field, "Not implemented")

def get_low_option(field):
    """Get a low (high risk) option for a field"""
    options = {
        "mfa_status": "For privileged users only",
        "password_policy": "Medium (10+ chars, mixed case)",
        "privileged_access": "Manual tracking",
        "access_reviews": "Annually",
        "data_classification": "Basic classification exists but not enforced",
        "encryption_status": "Encryption for some sensitive data",
        "dlp_status": "Basic DLP for email only",
        "data_retention": "Policy exists but not enforced",
        "network_segmentation": "Basic segmentation (e.g., IT vs OT)",
        "firewall_management": "Regular but manual reviews",
        "vuln_scanning": "Annually",
        "patch_management": "Regular but manual patching",
        "ir_plan": "Basic plan but not tested",
        "security_monitoring": "Basic logging without 24/7 monitoring",
        "breach_response": "Within 24 hours for critical systems",
        "forensic_capabilities": "Basic log review capabilities",
        "vendor_assessment": "Basic security questionnaire",
        "vendor_contracts": "Basic security requirements",
        "third_party_access": "Some restrictions for third parties",
        "vendor_incidents": "Basic notification requirements"
    }
    return options.get(field, "Basic implementation")

def get_medium_option(field):
    """Get a medium option for a field"""
    options = {
        "mfa_status": "For all employees",
        "password_policy": "Strong (12+ chars, mixed case, symbols, numbers)",
        "privileged_access": "PAM solution for some systems",
        "access_reviews": "Quarterly",
        "data_classification": "Classification implemented for sensitive data",
        "encryption_status": "Encryption for all sensitive data at rest and in transit",
        "dlp_status": "DLP for email and endpoints",
        "data_retention": "Policy with manual enforcement",
        "network_segmentation": "Moderate segmentation by department/function",
        "firewall_management": "Change management process with reviews",
        "vuln_scanning": "Quarterly",
        "patch_management": "Scheduled patching with SLAs",
        "ir_plan": "Documented plan with annual testing",
        "security_monitoring": "SIEM solution with business hours monitoring",
        "breach_response": "Within 8 hours for critical systems",
        "forensic_capabilities": "Some forensic tools and training",
        "vendor_assessment": "Detailed assessment for critical vendors",
        "vendor_contracts": "Detailed requirements with right-to-audit",
        "third_party_access": "Limited access with additional controls",
        "vendor_incidents": "Formal process for critical vendors"
    }
    return options.get(field, "Standard implementation")

def get_highest_option(field):
    """Get the highest (lowest risk) option for a field"""
    options = {
        "mfa_status": "For all users including third parties",
        "password_policy": "Very strong (14+ chars with complexity)",
        "privileged_access": "Comprehensive PAM with monitoring",
        "access_reviews": "Continuous monitoring",
        "data_classification": "Comprehensive classification enforced for all data",
        "encryption_status": "End-to-end encryption for all data",
        "dlp_status": "Comprehensive DLP across all channels",
        "data_retention": "Automated enforcement of retention policies",
        "network_segmentation": "Zero trust architecture/microsegmentation",
        "firewall_management": "Automated policy management and continuous monitoring",
        "vuln_scanning": "Continuous/automated scanning",
        "patch_management": "Automated patch management with verification",
        "ir_plan": "Comprehensive plan with regular exercises",
        "security_monitoring": "24/7 SOC with advanced analytics",
        "breach_response": "Within 1 hour with automated containment",
        "forensic_capabilities": "Advanced forensics team and tools",
        "vendor_assessment": "Comprehensive assessments with ongoing monitoring",
        "vendor_contracts": "Comprehensive requirements with regular verification",
        "third_party_access": "Just-in-time access with comprehensive monitoring",
        "vendor_incidents": "Comprehensive incident management with all vendors"
    }
    return options.get(field, "Advanced implementation")

def create_chat_message(sender, message, data=None):
    """Add a message to the chat history"""
    st.session_state.conversation.append({
        "sender": sender,
        "message": message,
        "data": data or {},
        "timestamp": datetime.now().isoformat()
    })

def render_chat_message(message):
    """Render a chat message"""
    sender = message.get("sender", "bot")
    message_text = message.get("message", "")
    message_data = message.get("data", {})
    
    if sender == "user":
        st.markdown(f'<div class="chat-message user">{message_text}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message bot">{message_text}</div>', unsafe_allow_html=True)
        
        # Render any attached data visualizations
        if 'risk_score' in message_data:
            render_risk_score_card(message_data)
        
        if 'recommendations' in message_data and message_data['recommendations']:
            render_recommendations_preview(message_data['recommendations'][:3])

def render_risk_score_card(assessment_data):
    """Render risk score card"""
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
                <div style="font-size: 3rem; font-weight: bold; color: {risk_color};">{risk_score:.1f}</div>
                <div style="font-size: 1.2rem;">out of 100</div>
            </div>
            <div style="flex: 2; padding-left: 1rem;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">Risk Level: <span class="risk-{risk_class}">{risk_name.title()}</span></div>
                <div>{risk_level.get('description', '')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_recommendations_preview(recommendations):
    """Render preview of recommendations"""
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

def render_upload_page():
    """Render the questionnaire upload page"""
    st.markdown('<h1 class="main-header">Security & Compliance Advisor</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <h3>Welcome to the Security & Compliance Advisor</h3>
        <p>Upload your security questionnaire in Excel format (XLSX/XLSM) to receive a comprehensive risk assessment and tailored recommendations.</p>
        <p>The advisor will analyze your responses against security best practices and compliance frameworks to identify areas of risk and provide actionable recommendations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload Security Questionnaire", type=["xlsx", "xlsm"])
    
    if uploaded_file is not None:
        with st.spinner("Processing questionnaire..."):
            # Process the uploaded questionnaire
            questionnaire_data = process_excel_questionnaire(uploaded_file)
            
            if questionnaire_data:
                st.session_state.questionnaire_data = questionnaire_data
                
                # Calculate risk score and recommendations
                assessment = calculate_risk_score(questionnaire_data)
                st.session_state.assessment = assessment
                st.session_state.recommendations = assessment.get('recommendations', [])
                
                # Add initial message to conversation
                risk_score = assessment.get('risk_score', 0)
                risk_level = assessment.get('risk_level', {}).get('name', 'unknown')
                rec_count = len(assessment.get('recommendations', []))
                
                message = f"I've analyzed your security questionnaire. Your risk score is {risk_score:.1f} out of 100, which indicates a {risk_level} level. I've identified {rec_count} recommendations to improve your security posture."
                create_chat_message("bot", message, assessment)
                
                # Navigate to chat page
                st.session_state.current_page = 'chat'
                st.experimental_rerun()
            else:
                st.error("Unable to extract questionnaire data from the uploaded file. Please ensure it contains security assessment questions and responses.")

def render_chat_page():
    """Render chat interface page"""
    st.markdown('<h1 class="main-header">Security & Compliance Advisor</h1>', unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    # Input container
    input_container = st.container()
    
    # Render chat messages
    with chat_container:
        for message in st.session_state.conversation:
            render_chat_message(message)
    
    # Input for new message
    with input_container:
        col1, col2 = st.columns([5, 1])
        
        # Define a callback to handle message submission
        def handle_message_submit():
            user_input = st.session_state.chat_input
            if user_input and user_input != st.session_state.get('last_input', ''):
                # Save current input to avoid duplicate processing
                st.session_state.last_input = user_input
                
                # Add user message to conversation
                create_chat_message("user", user_input)
                
                # Process message and generate response
                response_text, response_data = process_chat_message(user_input)
                
                # Add bot response to conversation
                create_chat_message("bot", response_text, response_data)
                
                # Clear input
                st.session_state.chat_input = ""
                
                # Rerun to update UI
                st.experimental_rerun()
        
        with col1:
            # Initialize session state for chat input if not exists
            if 'chat_input' not in st.session_state:
                st.session_state.chat_input = ""
                
            st.text_input(
                "Type your message...", 
                key="chat_input", 
                on_change=handle_message_submit
            )
        
        with col2:
            st.button("Send", on_click=handle_message_submit)

def process_chat_message(message):
    """Process a chat message and generate a response"""
    # Convert message to lowercase for easier matching
    message_lower = message.lower()
    
    # Check for specific intents
    if any(kw in message_lower for kw in ["risk", "score", "assessment", "analyze"]):
        # Risk assessment request
        if st.session_state.assessment:
            risk_score = st.session_state.assessment.get('risk_score', 0)
            risk_level = st.session_state.assessment.get('risk_level', {}).get('name', 'unknown')
            
            response = f"Based on your questionnaire, your overall security risk score is {risk_score:.1f} out of 100, placing you at a {risk_level} level. Would you like to see a detailed breakdown of risk factors or specific recommendations?"
            return response, st.session_state.assessment
        else:
            return "I don't have enough information to provide a risk assessment. Please upload a security questionnaire first.", {}
    
    elif any(kw in message_lower for kw in ["recommend", "suggestion", "improve", "fix"]):
        # Recommendation request
        if st.session_state.recommendations:
            recs = st.session_state.recommendations[:5]  # Top 5 recommendations
            
            response = "Here are my top recommendations to improve your security posture:\n\n"
            
            return response, {"recommendations": recs}
        else:
            return "I don't have enough information to provide recommendations. Please upload a security questionnaire first.", {}
    
    elif any(kw in message_lower for kw in ["compliance", "framework", "standard", "regulation"]):
        # Compliance information request
        if st.session_state.assessment and 'framework_compliance' in st.session_state.assessment:
            framework_data = st.session_state.assessment['framework_compliance']
            
            response = "Based on your questionnaire, here's your estimated compliance status with major frameworks:\n\n"
            
            for framework_id, framework in st.session_state.frameworks.items():
                if framework_id in framework_data:
                    compliance_score = framework_data[framework_id].get('compliance_score', 0)
                    framework['coverage'] = compliance_score
                    
                    response += f"• {framework['name']}: {compliance_score:.1f}% coverage\n"
            
            response += "\nWould you like specific information about any of these frameworks or gap areas that need to be addressed?"
            
            return response, {"frameworks": st.session_state.frameworks}
        else:
            return "I don't have enough information to assess your compliance status. Please upload a security questionnaire first.", {}
    
    elif any(kw in message_lower for kw in ["dashboard", "visualization", "chart", "graph"]):
        # Dashboard request
        if st.session_state.assessment:
            return "I've prepared a dashboard with your security assessment results. You can view it by clicking on the 'Risk Dashboard' button in the sidebar.", {}
        else:
            return "I don't have enough data to generate a dashboard. Please upload a security questionnaire first.", {}
    
    elif any(kw in message_lower for kw in ["help", "how", "what can you", "capabilities"]):
        # Help request
        response = """I'm your Security & Compliance Advisor. Here's how I can help you:

1. **Risk Assessment**: I can analyze your security questionnaire to identify risks and vulnerabilities
2. **Recommendations**: I can provide tailored recommendations to improve your security posture
3. **Compliance Guidance**: I can help you understand your compliance status with major security frameworks
4. **Security Best Practices**: I can provide information on security controls and best practices

You can ask me questions about specific security areas like access control, encryption, incident response, etc."""
        
        return response, {}
    
    else:
        # Try to handle questions about specific security controls
        security_topics = {
            "mfa": "Multi-Factor Authentication (MFA) is one of the most effective controls to prevent unauthorized access. It requires users to provide multiple forms of verification before gaining access to systems or data.",
            "password": "Strong password policies are essential for security. Best practices include requiring long passwords (14+ characters), checking against known compromised passwords, and implementing a password manager.",
            "access control": "Access control ensures that only authorized users can access sensitive resources. The principle of least privilege is key - users should only have access to what they need for their job functions.",
            "encryption": "Encryption protects data confidentiality by converting it into an unreadable format that can only be decrypted with the proper key. You should encrypt sensitive data both at rest and in transit.",
            "firewall": "Firewalls protect your network by controlling incoming and outgoing traffic based on predetermined security rules. Next-generation firewalls (NGFW) provide additional capabilities like application awareness and intrusion prevention.",
            "vulnerability": "Vulnerability management is the process of identifying, evaluating, treating, and reporting on security vulnerabilities. Regular scanning and prompt patching are essential components.",
            "patch": "Patch management ensures systems are updated with the latest security fixes. Establish clear SLAs for patching based on vulnerability severity (e.g., critical patches within 24-72 hours).",
            "incident": "Incident response is your plan for handling security breaches. An effective plan includes preparation, detection, containment, eradication, recovery, and lessons learned phases.",
            "backup": "Backups protect against data loss from ransomware, system failures, or human error. Follow the 3-2-1 rule: 3 copies of data, on 2 different media types, with 1 copy offsite.",
            "vendor": "Vendor risk management assesses and mitigates risks associated with third-party vendors. Implement a formal assessment process, security requirements in contracts, and ongoing monitoring."
        }
        
        for topic, info in security_topics.items():
            if topic in message_lower:
                # Check if we have assessment data for this topic
                related_field = None
                if topic == "mfa":
                    related_field = "mfa_status"
                elif topic == "password":
                    related_field = "password_policy"
                elif topic == "access control":
                    related_field = "privileged_access"
                elif topic == "encryption":
                    related_field = "encryption_status"
                elif topic == "firewall":
                    related_field = "firewall_management"
                elif topic == "vulnerability":
                    related_field = "vuln_scanning"
                elif topic == "patch":
                    related_field = "patch_management"
                elif topic == "incident":
                    related_field = "ir_plan"
                elif topic == "vendor":
                    related_field = "vendor_assessment"
                
                personalized_info = ""
                if related_field and related_field in st.session_state.questionnaire_data:
                    current_status = st.session_state.questionnaire_data[related_field]
                    personalized_info = f"\n\nBased on your questionnaire, your current approach is: {current_status}."
                
                return info + personalized_info, {}
        
        # Default response
        return "I'm here to help with your security and compliance questions. You can ask about your risk assessment, specific security controls, compliance frameworks, or recommendations to improve your security posture.", {}

def render_dashboard_page():
    """Render risk dashboard page"""
    st.markdown('<h1 class="main-header">Risk Assessment Dashboard</h1>', unsafe_allow_html=True)
    
    # Check if assessment is available
    if not st.session_state.assessment:
        st.warning("No risk assessment data available. Please upload a security questionnaire first.")
        
        if st.button("Upload Questionnaire"):
            st.session_state.current_page = 'upload'
            st.experimental_rerun()
            
        return
    
    # Get assessment data
    assessment = st.session_state.assessment
    risk_score = assessment.get('risk_score', 0)
    risk_level = assessment.get('risk_level', {})
    explanation = assessment.get('explanation', {})
    recommendations = assessment.get('recommendations', [])
    framework_compliance = assessment.get('framework_compliance', {})
    category_scores = assessment.get('category_scores', {})
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card(
            "Risk Score", 
            f"{risk_score:.1f}", 
            "/100", 
            risk_level.get('color', '#6B7280')
        )
    
    with col2:
        risk_factors = len(explanation.get('top_factors', []))
        render_metric_card(
            "Risk Factors", 
            f"{risk_factors}", 
            "Identified", 
            "#1E40AF"
        )
    
    with col3:
        rec_count = len(recommendations)
        render_metric_card(
            "Recommendations", 
            f"{rec_count}", 
            "Actions", 
            "#059669"
        )
    
    with col4:
        # Calculate potential improvement
        potential_improvement = min(100, risk_score * 0.3)  # Simplified estimate
        render_metric_card(
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
            render_risk_factors_chart(explanation['top_factors'])
        
        # Risk categories chart
        if category_scores:
            render_risk_categories_chart(category_scores)
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

def render_compliance_impact(framework_compliance):
    """Render compliance impact section"""
    # Get framework data
    frameworks = list(st.session_state.frameworks.keys())
    framework_names = [st.session_state.frameworks[f]['name'] for f in frameworks]
    
    # Calculate coverage from compliance data
    coverage = []
    for framework_id in frameworks:
        if framework_id in framework_compliance:
            coverage.append(framework_compliance[framework_id].get('compliance_score', 0))
        else:
            coverage.append(0)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Create horizontal bar chart for compliance coverage
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=coverage,
            y=framework_names,
            orientation='h',
            marker_color='#1E40AF',
            text=[f"{c:.1f}%" for c in coverage],
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
            <p>For a detailed compliance assessment, use the chat to explore specific framework requirements.</p>
        </div>
        """, unsafe_allow_html=True)

def render_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        st.image("https://via.placeholder.com/150x80?text=Security+Advisor", width=200)
        st.markdown("## Navigation")
        
        # Navigation buttons
        if st.button("🔄 Upload Questionnaire", key="nav_upload"):
            st.session_state.current_page = 'upload'
            st.experimental_rerun()
        
        if st.button("💬 Security Chat", key="nav_chat"):
            st.session_state.current_page = 'chat'
            st.experimental_rerun()
        
        if st.button("📊 Risk Dashboard", key="nav_dashboard"):
            st.session_state.current_page = 'dashboard'
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
            
            # Add export button
            if st.download_button(
                label="📥 Export Assessment Report",
                data=generate_assessment_report(),
                file_name="security_assessment_report.json",
                mime="application/json"
            ):
                st.success("Assessment report downloaded successfully!")

def generate_assessment_report():
    """Generate a JSON report of the assessment"""
    if not st.session_state.assessment:
        return "{}"
    
    # Create a simplified version of the assessment for export
    report = {
        "risk_score": st.session_state.assessment.get('risk_score', 0),
        "risk_level": st.session_state.assessment.get('risk_level', {}),
        "timestamp": st.session_state.assessment.get('timestamp', datetime.now().isoformat()),
        "recommendations": st.session_state.assessment.get('recommendations', []),
        "framework_compliance": st.session_state.assessment.get('framework_compliance', {}),
        "questionnaire_data": st.session_state.questionnaire_data
    }
    
    return json.dumps(report, indent=2)

# Main application
def main():
    # Render sidebar
    render_sidebar()
    
    # Render current page
    if st.session_state.current_page == 'upload':
        render_upload_page()
    elif st.session_state.current_page == 'chat':
        render_chat_page()
    elif st.session_state.current_page == 'dashboard':
        render_dashboard_page()

if __name__ == "__main__":
    main()        
    with col2:
        st.markdown('<h2 class="sub-header">Prioritized Actions</h2>', unsafe_allow_html=True)
        
        if recommendations:
            render_recommendations_list(recommendations[:10])
        else:
            st.info("No recommendations available.")
    
    # Compliance impact section
    st.markdown('<h2 class="sub-header">Compliance Impact</h2>', unsafe_allow_html=True)
    render_compliance_impact(framework_compliance)

def render_metric_card(label, value, suffix, color):
    """Render a metric card"""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: {color};">{value}<span style="font-size: 1rem; color: #6B7280;">{suffix}</span></div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def render_risk_factors_chart(factors):
    """Render risk factors chart"""
    # Prepare data
    factors = sorted(factors, key=lambda x: x['impact'])
    
    # Take top/bottom 5 factors
    display_factors = []
    
    # Add negative factors (ones that decrease risk)
    neg_factors = [f for f in factors if f['impact'] < 0]
    if neg_factors:
        display_factors.extend(neg_factors[:2])
    
    # Add positive factors (ones that increase risk)
    pos_factors = [f for f in factors if f['impact'] > 0]
    if pos_factors:
        display_factors.extend(pos_factors[-8:])
    
    # Create chart data
    labels = [f"{f['description'][:30]}..." if len(f['description']) > 30 else f['description'] for f in display_factors]
    values = [f['impact'] for f in display_factors]
    colors = ['#059669' if v < 0 else '#DC2626' for v in values]
    
    # Create horizontal bar chart
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

def render_risk_categories_chart(category_scores):
    """Render risk categories chart"""
    # Prepare data
    categories = []
    scores = []
    
    for category, score in category_scores.items():
        categories.append(category.replace('_', ' ').title())
        scores.append(score)
    
    # Create Plotly pie chart
    fig = go.Figure(data=[go.Pie(
        labels=categories,
        values=scores,
        hole=.4,
        marker_colors=px.colors.qualitative.Set2
    )])
    
    fig.update_layout(
        title="Risk by Category",
        height=350,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_recommendations_list(recommendations):
    """Render recommendations list"""
    for i, rec in enumerate(recommendations):
        impact_class = "high-impact" if rec.get('impact') == "High" else (
            "medium-impact" if rec.get('impact') == "Medium" elseimport streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re
import base64
import json

# Set page config
st.set_page_config(
    page_title="Security & Compliance Advisor",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
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

# Define risk scoring function
def calculate_risk_score(questionnaire_data):
    """Calculate risk score based on questionnaire responses"""
    # Define weights for different categories
    category_weights = {
        "access_control": 0.25,
        "data_protection": 0.20,
        "network_security": 0.15,
        "vulnerability_management": 0.15,
        "incident_response": 0.15,
        "vendor_management": 0.10
    }
    
    # Define score mappings for key fields
    score_mappings = {
        # Access Control Category
        "mfa_status": {
            "Not implemented": 100,
            "For privileged users only": 60,
            "For all employees": 30,
            "For all users including third parties": 0
        },
        "password_policy": {
            "Basic (8+ characters)": 80,
            "Medium (10+ chars, mixed case)": 50,
            "Strong (12+ chars, mixed case, symbols, numbers)": 20,
            "Very strong (14+ chars with complexity)": 0
        },
        "privileged_access": {
            "No specific management": 100,
            "Manual tracking": 70,
            "PAM solution for some systems": 40,
            "Comprehensive PAM with monitoring": 0
        },
        "access_reviews": {
            "Never/ad hoc": 100,
            "Annually": 70,
            "Quarterly": 40,
            "Monthly": 20,
            "Continuous monitoring": 0
        },
        
        # Data Protection Category
        "data_classification": {
            "No formal classification": 100,
            "Basic classification exists but not enforced": 70,
            "Classification implemented for sensitive data": 40,
            "Comprehensive classification enforced for all data": 0
        },
        "encryption_status": {
            "Minimal/ad hoc encryption": 100,
            "Encryption for some sensitive data": 60,
            "Encryption for all sensitive data at rest and in transit": 20,
            "End-to-end encryption for all data": 0
        },
        "dlp_status": {
            "No DLP implementation": 100,
            "Basic DLP for email only": 70,
            "DLP for email and endpoints": 40,
            "Comprehensive DLP across all channels": 0
        },
        "data_retention": {
            "No formal policy": 100,
            "Policy exists but not enforced": 70,
            "Policy with manual enforcement": 40,
            "Automated enforcement of retention policies": 0
        },
        
        # Network Security Category
        "network_segmentation": {
            "Minimal/no segmentation": 100,
            "Basic segmentation (e.g., IT vs OT)": 70,
            "Moderate segmentation by department/function": 40,
            "Zero trust architecture/microsegmentation": 0
        },
        "firewall_management": {
            "Basic firewall configuration": 80,
            "Regular but manual reviews": 60,
            "Change management process with reviews": 30,
            "Automated policy management and continuous monitoring": 0
        },
        
        # Vulnerability Management Category
        "vuln_scanning": {
            "Ad hoc or never": 100,
            "Annually": 80,
            "Quarterly": 60,
            "Monthly": 30,
            "Continuous/automated scanning": 0
        },
        "patch_management": {
            "Ad hoc patching": 100,
            "Regular but manual patching": 70,
            "Scheduled patching with SLAs": 30,
            "Automated patch management with verification": 0
        },
        
        # Incident Response Category
        "ir_plan": {
            "No formal plan": 100,
            "Basic plan but not tested": 70,
            "Documented plan with annual testing": 30,
            "Comprehensive plan with regular exercises": 0
        },
        "security_monitoring": {
            "Minimal/ad hoc monitoring": 100,
            "Basic logging without 24/7 monitoring": 70,
            "SIEM solution with business hours monitoring": 40,
            "24/7 SOC with advanced analytics": 0
        },
        "breach_response": {
            "No defined SLAs": 100,
            "Within 24 hours for critical systems": 60,
            "Within 8 hours for critical systems": 30,
            "Within 1 hour with automated containment": 0
        },
        "forensic_capabilities": {
            "No forensic capabilities": 100,
            "Basic log review capabilities": 70,
            "Some forensic tools and training": 40,
            "Advanced forensics team and tools": 0
        },
        
        # Vendor Management Category
        "vendor_assessment": {
            "No formal assessment": 100,
            "Basic security questionnaire": 70,
            "Detailed assessment for critical vendors": 40,
            "Comprehensive assessments with ongoing monitoring": 0
        },
        "vendor_contracts": {
            "Minimal security language": 100,
            "Basic security requirements": 70,
            "Detailed requirements with right-to-audit": 30,
            "Comprehensive requirements with regular verification": 0
        },
        "third_party_access": {
            "Same as employee access": 100,
            "Some restrictions for third parties": 70,
            "Limited access with additional controls": 30,
            "Just-in-time access with comprehensive monitoring": 0
        },
        "vendor_incidents": {
            "No specific process": 100,
            "Basic notification requirements": 70,
            "Formal process for critical vendors": 40,
            "Comprehensive incident management with all vendors": 0
        }
    }
    
    # Map questions to categories
    category_mappings = {
        "access_control": ["mfa_status", "password_policy", "privileged_access", "access_reviews"],
        "data_protection": ["data_classification", "encryption_status", "dlp_status", "data_retention"],
        "network_security": ["network_segmentation", "firewall_management"],
        "vulnerability_management": ["vuln_scanning", "patch_management"],
        "incident_response": ["ir_plan", "security_monitoring", "breach_response", "forensic_capabilities"],
        "vendor_management": ["vendor_assessment", "vendor_contracts", "third_party_access", "vendor_incidents"]
    }
    
    # Calculate category scores
    category_scores = {}
    
    for category, fields in category_mappings.items():
        total_score = 0
        valid_fields = 0
        
        for field in fields:
            if field in questionnaire_data and questionnaire_data[field] in score_mappings.get(field, {}):
                total_score += score_mappings[field][questionnaire_data[field]]
                valid_fields += 1
        
        # Calculate average score for category
        if valid_fields > 0:
            category_scores[category] = total_score / valid_fields
        else:
            category_scores[category] = 50  # Default score if no valid fields
    
    # Calculate weighted overall risk score
    risk_score = 0
    for category, score in category_scores.items():
        risk_score += score * category_weights.get(category, 0)
    
    # Generate top factors
    factors = []
    for category, fields in category_mappings.items():
        for field in fields:
            if field in questionnaire_data and questionnaire_data[field] in score_mappings.get(field, {}):
                score = score_mappings[field][questionnaire_data[field]]
                if score >= 60:  # Only include high-risk factors
                    impact = score * category_weights.get(category, 0) * 0.1
                    
                    factor = {
                        "feature": field,
                        "description": f"{field.replace('_', ' ').title()}: {questionnaire_data[field]}",
                        "impact": impact,
                        "direction": "negative"
                    }
                    factors.append(factor)
    
    # Sort factors by impact (highest first)
    factors.sort(key=lambda x: x['impact'], reverse=True)
    
    # Add some positive factors (good practices)
    for category, fields in category_mappings.items():
        for field in fields:
            if field in questionnaire_data and questionnaire_data[field] in score_mappings.get(field, {}):
                score = score_mappings[field][questionnaire_data[field]]
                if score <= 20:  # Good practice
                    impact = -1 * (100 - score) * category_weights.get(category, 0) * 0.02
                    
                    factor = {
                        "feature": field,
                        "description": f"Good Practice: {field.replace('_', ' ').title()} - {questionnaire_data[field]}",
                        "impact": impact,
                        "direction": "positive"
                    }
                    factors.append(factor)
    
    # Organize factors by category
    categories = {}
    for category_name, fields in category_mappings.items():
        category_display = category_name.replace('_', ' ').title()
        categories[category_display] = [f for f in factors if f['feature'] in fields]
    
    # Calculate framework compliance
    framework_compliance = calculate_framework_compliance(questionnaire_data, category_scores)
    
    # Generate risk level
    risk_level = get_risk_level(risk_score)
    
    # Generate recommendations
    recommendations = generate_recommendations(questionnaire_data, score_mappings)
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "explanation": {
            "top_factors": factors[:10],
            "categories": categories,
            "summary": "The risk score is based on the identified security weaknesses across multiple domains."
        },
        "recommendations": recommendations,
        "framework_compliance": framework_compliance,
        "category_scores": category_scores,
        "timestamp": datetime.now().isoformat()
    }

def get_risk_level(score):
    """Determine risk level based on score"""
    if score < 20:
        return {
            "name": "very low risk",
            "description": "Your security posture is excellent with minimal areas for improvement.",
            "color": "green"
        }
    elif score < 40:
        return {
            "name": "low risk",
            "description": "Your security posture is good with a few minor areas for improvement.",
            "color": "blue"
        }
    elif score < 60:
        return {
            "name": "moderate risk",
            "description": "Your security posture needs attention in several key areas.",
            "color": "yellow"
        }
    elif score < 80:
        return {
            "name": "high risk",
            "description": "Your security posture has significant vulnerabilities that need immediate attention.",
            "color": "orange"
        }
    else:
        return {
            "name": "critical risk",
            "description": "Your security posture has critical vulnerabilities requiring urgent remediation.",
            "color": "red"
        }

def calculate_framework_compliance(questionnaire_data, category_scores):
    """Calculate compliance levels for different frameworks"""
    # Map categories to frameworks
    framework_mappings = {
        "iso27001": {
            "access_control": 0.25,
            "data_protection": 0.2,
            "network_security": 0.15,
            "vulnerability_management": 0.15,
            "incident_response": 0.15,
            "vendor_management": 0.1
        },
        "nist_csf": {
            "access_control": 0.2,
            "data_protection": 0.2,
            "network_security": 0.15,
            "vulnerability_management": 0.2,
            "incident_response": 0.15,
            "vendor_management": 0.1
        },
        "gdpr": {
            "access_control": 0.2,
            "data_protection": 0.4,
            "network_security": 0.1,
            "vulnerability_management": 0.1,
            "incident_response": 0.1,
            "vendor_management": 0.1
        },
        "hipaa": {
            "access_control": 0.25,
            "data_protection": 0.3,
            "network_security": 0.1,
            "vulnerability_management": 0.1,
            "incident_response": 0.15,
            "vendor_management": 0.1
        },
        "pci_dss": {
            "access_control": 0.3,
            "data_protection": 0.25,
            "network_security": 0.2,
            "vulnerability_management": 0.15,
            "incident_response": 0.05,
            "vendor_management": 0.05
        }
    }
    
    framework_compliance = {}
    
    for framework, category_weights in framework_mappings.items():
        compliance_score = 0
        
        for category, weight in category_weights.items():
            if category in category_scores:
                # Convert risk score to compliance percentage (100 - risk_score)
                compliance_score += (100 - category_scores[category]) * weight
        
        framework_compliance[framework] = {
            "compliance_score": compliance_score,
            "gap_areas": []
        }
        
        # Identify gap areas based on category scores
        for category, score in category_scores.items():
            if score >= 70 and category in category_weights and category_weights[category] >= 0.15:
                framework_compliance[framework]["gap_areas"].append({
                    "category": category,
                    "score": score
                })
    
    return framework_compliance

def generate_recommendations(questionnaire_data, score_mappings):
    """Generate recommendations based on questionnaire data"""
    recommendations = []
    
    # Map fields to specific recommendations
    field_recommendations = {
        "mfa_status": {
            "title": "Implement Multi-Factor Authentication",
            "description": "Deploy MFA for all users, especially those with privileged access. This will significantly reduce the risk of unauthorized access due to compromised credentials.",
            "category": "Access Control",
            "effort": "Medium"
        },
        "password_policy": {
            "title": "Strengthen Password Policy",
            "description": "Update your password policy to require longer passwords (14+ characters) with complexity requirements. Implement a password manager to help users maintain strong, unique passwords.",
            "category": "Access Control",
            "effort": "Low"
        },
        "privileged_access": {
            "title": "Implement Privileged Access Management",
            "description": "Deploy a PAM solution to manage, monitor, and control privileged accounts access. Include just-in-time access and session recording for critical systems.",
            "category": "Access Control",
            "effort": "High"
        },
        "access_reviews": {
            "title": "Establish Regular Access Reviews",
            "description": "Implement quarterly access reviews for all systems, especially those storing sensitive data. Automate the review process where possible to ensure consistency and completion.",
            "category": "Access Control",
            "effort": "Medium"
        },
        "data_classification": {
            "title": "Implement Data Classification",
            "description": "Establish a formal data classification framework and enforce controls based on data sensitivity levels. Train users on proper handling of sensitive information.",
            "category": "Data Protection",
            "effort": "Medium"
        },
        "encryption_status": {
            "title": "Enhance Data Encryption",
            "description": "Implement comprehensive encryption for sensitive data both at rest and in transit using industry-standard algorithms. Establish a key management process.",
            "category": "Data Protection",
            "effort": "Medium"
        },
        "dlp_status": {
            "title": "Deploy Data Loss Prevention",
            "description": "Implement a DLP solution to monitor and protect sensitive data across endpoints, networks, and cloud services. Start with high-risk channels like email and gradually expand coverage.",
            "category": "Data Protection",
            "effort": "High"
        },
        "data_retention": {
            "title": "Implement Data Retention Policy",
            "description": "Develop and enforce a formal data retention policy that automatically archives or deletes data based on retention requirements. Consider compliance requirements in your retention schedules.",
            "category": "Data Protection",
            "effort": "Medium"
        },
        "network_segmentation": {
            "title": "Implement Network Segmentation",
            "description": "Segment your network based on security requirements and data sensitivity. Use firewalls, VLANs, and access controls to restrict lateral movement within the network.",
            "category": "Network Security",
            "effort": "High"
        },
        "firewall_management": {
            "title": "Enhance Firewall Management",
            "description": "Implement a formal change management process for firewall rules, regular rule reviews, and automated policy validation to identify potential security gaps or misconfigurations.",
            "category": "Network Security",
            "effort": "Medium"
        },
        "vuln_scanning": {
            "title": "Implement Regular Vulnerability Scanning",
            "description": "Establish automated, regular vulnerability scanning of all systems and applications with a formal process for remediation prioritized by risk level.",
            "category": "Vulnerability Management",
            "effort": "Medium"
        },
        "patch_management": {
            "title": "Improve Patch Management",
            "description": "Implement an automated patch management system with defined SLAs for critical, high, medium, and low vulnerabilities. Establish a verification process to ensure patches are applied successfully.",
            "category": "Vulnerability Management",
            "effort": "High"
        },
        "ir_plan": {
            "title": "Develop Comprehensive Incident Response Plan",
            "description": "Create and regularly test a formal incident response plan that includes roles, responsibilities, and procedures for handling security incidents. Conduct tabletop exercises to validate the plan.",
            "category": "Incident Response",
            "effort": "Medium"
        },
        "security_monitoring": {
            "title": "Enhance Security Monitoring",
            "description": "Upgrade your security monitoring capabilities with a SIEM solution and 24/7 coverage. Implement automated alerting for critical security events and establish an escalation process.",
            "category": "Incident Response",
            "effort": "High"
        },
        "breach_response": {
            "title": "Improve Breach Response Capabilities",
            "description": "Establish clear SLAs for incident response based on severity levels. Implement automation for containment of common threats and develop playbooks for efficient response.",
            "category": "Incident Response",
            "effort": "Medium"
        },
        "forensic_capabilities": {
            "title": "Enhance Forensic Capabilities",
            "description": "Develop in-house forensic capabilities or establish relationships with external forensic providers. Ensure proper logging and evidence preservation mechanisms are in place.",
            "category": "Incident Response",
            "effort": "High"
        },
        "vendor_assessment": {
            "title": "Formalize Vendor Risk Assessment",
            "description": "Develop a comprehensive vendor risk assessment process that includes initial vetting, ongoing monitoring, and regular reassessment. Prioritize vendors based on data access and business criticality.",
            "category": "Vendor Management",
            "effort": "Medium"
        },
        "vendor_contracts": {
            "title": "Enhance Vendor Security Requirements",
            "description": "Update vendor contracts to include detailed security requirements, right-to-audit clauses, and breach notification obligations. Establish a process to verify compliance with these requirements.",
            "category": "Vendor Management",
            "effort": "Medium"
        },
        "third_party_access": {
            "title": "Secure Third-Party Access",
            "description": "Implement just-in-time access with comprehensive monitoring for all third-party access to your systems and data. Use separate VPNs or other secure access methods specifically for third parties.",
            "category": "Vendor Management",
            "effort": "Medium"
        },
        "vendor_incidents": {
            "title": "Improve Vendor Incident Management",
            "description": "Establish a formal process for handling security incidents involving vendors, including communication protocols, response procedures, and post-incident reviews.",
            "category": "Vendor Management",
            "effort": "Low"
        }
    }
    
    # Generate recommendations for high-risk areas
    for field, values in score_mappings.items():
        if field in questionnaire_data and questionnaire_data[field] in values:
            score = values[questionnaire_data[field]]
            
            # If score is high (indicating risk), add recommendation
            if score >= 60 and field in field_recommendations:
                rec = field_recommendations[field].copy()
                
                # Set impact based on score
                if score >= 90:
                    rec['impact'] = "High"
                elif score >= 70:
                    rec['impact'] = "Medium"
                else:
                    rec['impact'] = "Low"
                
                recommendations.append(rec)
    
    # Sort recommendations by impact
    impact_order = {"High": 0, "Medium": 1, "Low": 2}
    recommendations.sort(key=lambda x: impact_order.get(x.get('impact', "Low"), 3))
    
    return recommendations

def process_excel_questionnaire(file):
    """Process the uploaded Excel questionnaire file"""
    try:
        # Read Excel file
        df = pd.read_excel(file, engine='openpyxl', sheet_name=None)
        
        # Extract questionnaire data
        questionnaire_data = {}
        
        # Look for the main questionnaire sheet
        main_sheet = None
        for sheet_name, sheet_df in df.items():
            if "questionnaire" in sheet_name.lower() or "assessment" in sheet_name.lower() or "security" in sheet_name.lower():
                main_sheet = sheet_df
                break
        
        # If no specific sheet found, use the first one
        if main_sheet is None and len(df) > 0:
            main_sheet = list(df.values())[0]
        
        # Process the main sheet if found
        if main_sheet is not None:
            # Identify question and answer columns
            answer_col = None
            question_col = None
            
            for col in main_sheet.columns:
                col_lower = col.lower() if isinstance(col, str) else str(col).lower()
                if any(kw in col_lower for kw in ["answer", "response", "value", "selection"]):
                    answer_col = col
                if any(kw in col_lower for kw in ["question", "control", "requirement", "check"]):
                    question_col = col
            
            # If question and answer columns found
            if question_col and answer_col:
                for _, row in main_sheet.iterrows():
                    question = str(row[question_col]).strip()
                    answer = str(row[answer_col]).strip() if pd.notna(row[answer_col]) else ""
                    
                    # Map to our expected questionnaire fields
                    field = map_question_to_field(question)
                    if field and answer:
                        questionnaire_data[field] = map_answer_to_option(field, answer)
        
        # If we couldn't extract using standard approach, try to find data in any structured format
        if not questionnaire_data:
            for sheet_name, sheet_df in df.items():
                for i, row in sheet_df.iterrows():
                    for col in sheet_df.columns:
                        # Check if cell contains a key question keyword
                        cell_value = str(row[col]).lower() if pd.notna(row[col]) else ""
                        if any(kw in cell_value for kw in ["mfa", "password", "encryption", "firewall", "vulnerability", "incident"]):
                            # Look for an answer in the nearby cells
                            for offset in range(1, 4):
                                if i + offset < len(sheet_df):
                                    potential_answer = str(sheet_df.iloc[i + offset][col]).strip() if pd.notna(sheet_df.iloc[i + offset][col]) else ""
                                    if potential_answer and potential_answer.lower() not in ["yes", "no", "n/a", "question", "control"]:
                                        field = map_question_to_field(cell_value)
                                        if field:
                                            questionnaire_data[field] = map_answer_to_option(field, potential_answer)
                                            break
        
        return questionnaire_data
    
    except Exception as e:
        st.error(f"Error processing Excel file: {str(e)}")
        return {}

def map_question_to_field(question):
    """Map a question to a standardized field name"""
    question = question.lower()
    
    # MFA
    if any(kw in question for kw in ["multi-factor", "multifactor", "mfa", "two-factor", "2fa"]):
        return "mfa_status"
    
    # Password Policy
    if any(kw in question for kw in ["password policy", "password requirement", "password complexity"]):
        return "password_policy"
    
    # Privileged Access
    if any(kw in question for kw in ["privileged access", "admin account", "administrator", "elevated privilege"]):
        return "privileged_access"
    
    # Access Reviews
    if any(kw in question for kw in ["access review", "account review", "user access", "access recertification"]):
        return "access_reviews"
    
    # Data Classification
    if any(kw in question for kw in ["data classification", "information classification", "classify data"]):
        return "data_classification"
    
    # Encryption
    if any(kw in question for kw in ["encryption", "encrypt", "cryptographic"]):
        return "encryption_status"
    
    # DLP
    if any(kw in question for kw in ["dlp", "data loss", "data leakage", "data exfiltration"]):
        return "dlp_status"
    
    # Data Retention
    if any(kw in question for kw in ["data retention", "retention policy", "data disposal", "data deletion"]):
        return "data_retention"
    
    # Network Segmentation
    if any(kw in question for kw in ["network segmentation", "network segregation", "network isolation"]):
        return "network_segmentation"
    
    # Firewall Management
    if any(kw in question for kw in ["firewall", "network security", "perimeter security"]):
        return "firewall_management"
    
    # Vulnerability Scanning
    if any(kw in question for kw in ["vulnerability scan", "vuln scan", "security scan"]):
        return "vuln_scanning"
    
    # Patch Management
    if any(kw in question for kw in ["patch", "update management", "security update"]):
        return "patch_management"
    
    # Incident Response Plan
    if any(kw in question for kw in ["incident response", "security incident", "breach response", "ir plan"]):
        return "ir_plan"
    
    # Security Monitoring
    if any(kw in question for kw in ["security monitoring", "log monitoring", "siem", "intrusion detection"]):
        return "security_monitoring"
    
    # Breach Response
    if any(kw in question for kw in ["breach response", "incident response time", "security incident sla"]):
        return "breach_response"
    
    # Forensic Capabilities
    if any(kw in question for kw in ["forensic", "investigation", "digital evidence"]):
        return "forensic_capabilities"
    
    # Vendor Assessment
    if any(kw in question for kw in ["vendor assessment", "supplier assessment", "third party assessment"]):
        return "vendor_assessment"
    
    # Vendor Contracts
    if any(kw in question for kw in ["vendor contract", "supplier contract", "third party agreement"]):
        return "vendor_contracts"
    
    # Third Party Access
    if any(kw in question for kw in ["third party access", "vendor access", "supplier access"]):
        return "third_party_access"
    
    # Vendor Incidents
    if any(kw in question for kw in ["vendor incident", "supplier incident", "third party incident"]):
        return "vendor_incidents"
    
    return None

def map_answer_to_option(field, answer):
    """Map a given answer to standardized options"""
    answer_lower = answer.lower()
    
    # MFA Status
    if field == "mfa_status":
        if any(kw in answer_lower for kw in ["not", "none", "no"]):
            return "Not implemented"
        elif any(kw in answer_lower for kw in ["privileged", "admin", "critical"]):
            return "For privileged users only"
        elif any(kw in answer_lower for kw in ["employee", "staff", "internal"]):
            return "For all employees"
        elif any(kw in answer_lower for kw in ["third party", "vendor", "all user", "everyone"]):
            return "For all users including third parties"
        else:
            return "Not implemented"
    
    # Password Policy
    if field == "password_policy":
        if "14" in answer_lower or any(kw in answer_lower for kw in ["very strong", "highest", "robust"]):
            return "Very strong (14+ chars with complexity)"
        elif "12" in answer_lower or any(kw in answer_lower for kw in ["strong", "complex", "symbol", "number"]):
            return "Strong (12+ chars, mixed case, symbols, numbers)"
        elif "10" in answer_lower or any(kw in answer_lower for kw in ["medium", "mixed case"]):
            return "Medium (10+ chars, mixed case)"
        else:
            return "Basic (8+ characters)"
    
    # Privileged Access
    if field == "privileged_access":
        if any(kw in answer_lower for kw in ["comprehensive", "monitor", "full", "complete"]):
            return "Comprehensive PAM with monitoring"
        elif any(kw in answer_lower for kw in ["pam", "some system", "partial"]):
            return "PAM solution for some systems"
        elif any(kw in answer_lower for kw in ["manual", "track", "spreadsheet"]):
            return "Manual tracking"
        else:
            return "No specific management"
    
    # And similar mappings for other fields...
    # For brevity, I'll implement the logic for a few key fields and use defaults for others
    
    # Default mappings based on common responses
    if any(kw in answer_lower for kw in ["none", "no", "not", "never", "ad hoc"]):
        return get_lowest_option(field)
    elif any(kw in answer_lower for kw in ["basic", "minimal", "limited", "some"]):
        return get_low_option(field)
    elif any(kw in answer_lower for kw in ["good", "regular", "most", "many"]):
        return get_medium_option(field)
    elif any(kw in answer_lower for kw in ["comprehensive", "complete", "all", "full", "advanced"]):
        return get_highest_option(field)
    
    # Default to middle option if we can't determine
    return get_medium_option(field)

def get_lowest_option(field):
    """Get the lowest (highest risk) option for a field"""
    options = {
        "mfa_status": "Not implemented",
        "password_policy": "Basic (8+ characters)",
        "privileged_access": "No specific management",
        "access_reviews": "Never/ad hoc",
        "data_classification": "No formal classification",
        "encryption_status": "Minimal/ad hoc encryption",
        "dlp_status": "No DLP implementation",
        "data_retention": "No formal policy",
        "network_segmentation": "Minimal/no segmentation",
        "firewall_management": "Basic firewall configuration",
        "vuln_scanning": "Ad hoc or never",
        "patch_management": "Ad hoc patching",
        "ir_plan": "No formal plan",
        "security_monitoring": "Minimal/ad hoc monitoring",
        "breach_response": "No defined SLAs",
        "forensic_capabilities": "No forensic capabilities",
        "vendor_assessment": "No formal assessment",
        "vendor_contracts": "Minimal security language",
        "third_party_access": "Same as employee access",
        "vendor_incidents": "No specific process"
    }
    return options.get(field, "Not implemented")

def get_low_option(field):
    """Get a low (high risk) option for a field"""
    options = {
        "mfa_status": "For privileged users only",
        "password_policy": "Medium (10+ chars, mixed case)",
        "privileged_access": "Manual tracking",
        "access_reviews": "Annually",
        "data_classification": "Basic classification exists but not enforced",
        "encryption_status": "Encryption for some sensitive data",
        "dlp_status": "Basic DLP for email only",
        "data_retention": "Policy exists but not enforced",
        "network_segmentation": "Basic segmentation (e.g., IT vs OT)",
        "firewall_management": "Regular but manual reviews",
        "vuln_scanning": "Annually",
        "patch_management": "Regular but manual patching",
        "ir_plan": "Basic plan but not tested",
        "security_monitoring": "Basic logging without 24/7 monitoring",
        "breach_response": "Within 24 hours for critical systems",
        "forensic_capabilities": "Basic log review capabilities",
        "vendor_assessment": "Basic security questionnaire",
        "vendor_contracts": "Basic security requirements",
        "third_party_access": "Some restrictions for third parties",
        "vendor_incidents": "Basic notification requirements"
    }
    return options.get(field, "Basic implementation")

def get_medium_option(field):
    """Get a medium option for a field"""
    options = {
        "mfa_status": "For all employees",
        "password_policy": "Strong (12+ chars, mixed case, symbols, numbers)",
        "privileged_access": "PAM solution for some systems",
        "access_reviews": "Quarterly",
        "data_classification": "Classification implemented for sensitive data",
        "encryption_status": "Encryption for all sensitive data at rest and in transit",
        "dlp_status": "DLP for email and endpoints",
        "data_retention": "Policy with manual enforcement",
        "network_segmentation": "Moderate segmentation by department/function",
        "firewall_management": "Change management process with reviews",
        "vuln_scanning": "Quarterly",
        "patch_management": "Scheduled patching with SLAs",
        "ir_plan": "Documented plan with annual testing",
        "security_monitoring": "SIEM solution with business hours monitoring",
        "breach_response": "Within 8 hours for critical systems",
        "forensic_capabilities": "Some forensic tools and training",
        "vendor_assessment": "Detailed assessment for critical vendors",
        "vendor_contracts": "Detailed requirements with right-to-audit",
        "third_party_access": "Limited access with additional controls",
        "vendor_incidents": "Formal process for critical vendors"
    }
    return options.get(field, "Standard implementation")

def get_highest_option(field):
    """Get the highest (lowest risk) option for a field"""
    options = {
        "mfa_status": "For all users including third parties",
        "password_policy": "Very strong (14+ chars with complexity)",
        "privileged_access": "Comprehensive PAM with monitoring",
        "access_reviews": "Continuous monitoring",
        "data_classification": "Comprehensive classification enforced for all data",
        "encryption_status": "End-to-end encryption for all data",
        "dlp_status": "Comprehensive DLP across all channels",
        "data_retention": "Automated enforcement of retention policies",
        "network_segmentation": "Zero trust architecture/microsegmentation",
        "firewall_management": "Automated policy management and continuous monitoring",
        "vuln_scanning": "Continuous/automated scanning",
        "patch_management": "Automated patch management with verification",
        "ir_plan": "Comprehensive plan with regular exercises",
        "security_monitoring": "24/7 SOC with advanced analytics",
        "breach_response": "Within 1 hour with automated containment",
        "forensic_capabilities": "Advanced forensics team and tools",
        "vendor_assessment": "Comprehensive assessments with ongoing monitoring",
        "vendor_contracts": "Comprehensive requirements with regular verification",
        "third_party_access": "Just-in-time access with comprehensive monitoring",
        "vendor_incidents": "Comprehensive incident management with all vendors"
    }
    return options.get(field, "Advanced implementation")

def create_chat_message(sender, message, data=None):
    """Add a message to the chat history"""
    st.session_state.conversation.append({
        "sender": sender,
        "message": message,
        "data": data or {},
        "timestamp": datetime.now().isoformat()
    })

def render_chat_message(message):
    """Render a chat message"""
    sender = message.get("sender", "bot")
    message_text = message.get("message", "")
    message_data = message.get("data", {})
    
    if sender == "user":
        st.markdown(f'<div class="chat-message user">{message_text}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message bot">{message_text}</div>', unsafe_allow_html=True)
        
        # Render any attached data visualizations
        if 'risk_score' in message_data:
            render_risk_score_card(message_data)
        
        if 'recommendations' in message_data and message_data['recommendations']:
            render_recommendations_preview(message_data['recommendations'][:3])

def render_risk_score_card(assessment_data):
    """Render risk score card"""
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
                <div style="font-size: 3rem; font-weight: bold; color: {risk_color};">{risk_score:.1f}</div>
                <div style="font-size: 1.2rem;">out of 100</div>
            </div>
            <div style="flex: 2; padding-left: 1rem;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">Risk Level: <span class="risk-{risk_class}">{risk_name.title()}</span></div>
                <div>{risk_level.get('description', '')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_recommendations_preview(recommendations):
    """Render preview of recommendations"""
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

def render_upload_page():
    """Render the questionnaire upload page"""
    st.markdown('<h1 class="main-header">Security & Compliance Advisor</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <h3>Welcome to the Security & Compliance Advisor</h3>
        <p>Upload your security questionnaire in Excel format (XLSX/XLSM) to receive a comprehensive risk assessment and tailored recommendations.</p>
        <p>The advisor will analyze your responses against security best practices and compliance frameworks to identify areas of risk and provide actionable recommendations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload Security Questionnaire", type=["xlsx", "xlsm"])
    
    if uploaded_file is not None:
        with st.spinner("Processing questionnaire..."):
            # Process the uploaded questionnaire
            questionnaire_data = process_excel_questionnaire(uploaded_file)
            
            if questionnaire_data:
                st.session_state.questionnaire_data = questionnaire_data
                
                # Calculate risk score and recommendations
                assessment = calculate_risk_score(questionnaire_data)
                st.session_state.assessment = assessment
                st.session_state.recommendations = assessment.get('recommendations', [])
                
                # Add initial message to conversation
                risk_score = assessment.get('risk_score', 0)
                risk_level = assessment.get('risk_level', {}).get('name', 'unknown')
                rec_count = len(assessment.get('recommendations', []))
                
                message = f"I've analyzed your security questionnaire. Your risk score is {risk_score:.1f} out of 100, which indicates a {risk_level} level. I've identified {rec_count} recommendations to improve your security posture."
                create_chat_message("bot", message, assessment)
                
                # Navigate to chat page
                st.session_state.current_page = 'chat'
                st.experimental_rerun()
            else:
                st.error("Unable to extract questionnaire data from the uploaded file. Please ensure it contains security assessment questions and responses.")

def render_chat_page():
    """Render chat interface page"""
    st.markdown('<h1 class="main-header">Security & Compliance Advisor</h1>', unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    # Input container
    input_container = st.container()
    
    # Render chat messages
    with chat_container:
        for message in st.session_state.conversation:
            render_chat_message(message)
    
    # Input for new message
    with input_container:
        col1, col2 = st.columns([5, 1])
        
        # Define a callback to handle message submission
        def handle_message_submit():
            user_input = st.session_state.chat_input
            if user_input and user_input != st.session_state.get('last_input', ''):
                # Save current input to avoid duplicate processing
                st.session_state.last_input = user_input
                
                # Add user message to conversation
                create_chat_message("user", user_input)
                
                # Process message and generate response
                response_text, response_data = process_chat_message(user_input)
                
                # Add bot response to conversation
                create_chat_message("bot", response_text, response_data)
                
                # Clear input
                st.session_state.chat_input = ""
                
                # Rerun to update UI
                st.experimental_rerun()
        
        with col1:
            # Initialize session state for chat input if not exists
            if 'chat_input' not in st.session_state:
                st.session_state.chat_input = ""
                
            st.text_input(
                "Type your message...", 
                key="chat_input", 
                on_change=handle_message_submit
            )
        
        with col2:
            st.button("Send", on_click=handle_message_submit)

def process_chat_message(message):
    """Process a chat message and generate a response"""
    # Convert message to lowercase for easier matching
    message_lower = message.lower()
    
    # Check for specific intents
    if any(kw in message_lower for kw in ["risk", "score", "assessment", "analyze"]):
        # Risk assessment request
        if st.session_state.assessment:
            risk_score = st.session_state.assessment.get('risk_score', 0)
            risk_level = st.session_state.assessment.get('risk_level', {}).get('name', 'unknown')
            
            response = f"Based on your questionnaire, your overall security risk score is {risk_score:.1f} out of 100, placing you at a {risk_level} level. Would you like to see a detailed breakdown of risk factors or specific recommendations?"
            return response, st.session_state.assessment
        else:
            return "I don't have enough information to provide a risk assessment. Please upload a security questionnaire first.", {}
    
    elif any(kw in message_lower for kw in ["recommend", "suggestion", "improve", "fix"]):
        # Recommendation request
        if st.session_state.recommendations:
            recs = st.session_state.recommendations[:5]  # Top 5 recommendations
            
            response = "Here are my top recommendations to improve your security posture:\n\n"
            
            return response, {"recommendations": recs}
        else:
            return "I don't have enough information to provide recommendations. Please upload a security questionnaire first.", {}
    
    elif any(kw in message_lower for kw in ["compliance", "framework", "standard", "regulation"]):
        # Compliance information request
        if st.session_state.assessment and 'framework_compliance' in st.session_state.assessment:
            framework_data = st.session_state.assessment['framework_compliance']
            
            response = "Based on your questionnaire, here's your estimated compliance status with major frameworks:\n\n"
            
            for framework_id, framework in st.session_state.frameworks.items():
                if framework_id in framework_data:
                    compliance_score = framework_data[framework_id].get('compliance_score', 0)
                    framework['coverage'] = compliance_score
                    
                    response += f"• {framework['name']}: {compliance_score:.1f}% coverage\n"
            
            response += "\nWould you like specific information about any of these frameworks or gap areas that need to be addressed?"
            
            return response, {"frameworks": st.session_state.frameworks}
        else:
            return "I don't have enough information to assess your compliance status. Please upload a security questionnaire first.", {}
    
    elif any(kw in message_lower for kw in ["dashboard", "visualization", "chart", "graph"]):
        # Dashboard request
        if st.session_state.assessment:
            return "I've prepared a dashboard with your security assessment results. You can view it by clicking on the 'Risk Dashboard' button in the sidebar.", {}
        else:
            return "I don't have enough data to generate a dashboard. Please upload a security questionnaire first.", {}
    
    elif any(kw in message_lower for kw in ["help", "how", "what can you", "capabilities"]):
        # Help request
        response = """I'm your Security & Compliance Advisor. Here's how I can help you:

1. **Risk Assessment**: I can analyze your security questionnaire to identify risks and vulnerabilities
2. **Recommendations**: I can provide tailored recommendations to improve your security posture
3. **Compliance Guidance**: I can help you understand your compliance status with major security frameworks
4. **Security Best Practices**: I can provide information on security controls and best practices

You can ask me questions about specific security areas like access control, encryption, incident response, etc."""
        
        return response, {}
    
    else:
        # Try to handle questions about specific security controls
        security_topics = {
            "mfa": "Multi-Factor Authentication (MFA) is one of the most effective controls to prevent unauthorized access. It requires users to provide multiple forms of verification before gaining access to systems or data.",
            "password": "Strong password policies are essential for security. Best practices include requiring long passwords (14+ characters), checking against known compromised passwords, and implementing a password manager.",
            "access control": "Access control ensures that only authorized users can access sensitive resources. The principle of least privilege is key - users should only have access to what they need for their job functions.",
            "encryption": "Encryption protects data confidentiality by converting it into an unreadable format that can only be decrypted with the proper key. You should encrypt sensitive data both at rest and in transit.",
            "firewall": "Firewalls protect your network by controlling incoming and outgoing traffic based on predetermined security rules. Next-generation firewalls (NGFW) provide additional capabilities like application awareness and intrusion prevention.",
            "vulnerability": "Vulnerability management is the process of identifying, evaluating, treating, and reporting on security vulnerabilities. Regular scanning and prompt patching are essential components.",
            "patch": "Patch management ensures systems are updated with the latest security fixes. Establish clear SLAs for patching based on vulnerability severity (e.g., critical patches within 24-72 hours).",
            "incident": "Incident response is your plan for handling security breaches. An effective plan includes preparation, detection, containment, eradication, recovery, and lessons learned phases.",
            "backup": "Backups protect against data loss from ransomware, system failures, or human error. Follow the 3-2-1 rule: 3 copies of data, on 2 different media types, with 1 copy offsite.",
            "vendor": "Vendor risk management assesses and mitigates risks associated with third-party vendors. Implement a formal assessment process, security requirements in contracts, and ongoing monitoring."
        }
        
        for topic, info in security_topics.items():
            if topic in message_lower:
                # Check if we have assessment data for this topic
                related_field = None
                if topic == "mfa":
                    related_field = "mfa_status"
                elif topic == "password":
                    related_field = "password_policy"
                elif topic == "access control":
                    related_field = "privileged_access"
                elif topic == "encryption":
                    related_field = "encryption_status"
                elif topic == "firewall":
                    related_field = "firewall_management"
                elif topic == "vulnerability":
                    related_field = "vuln_scanning"
                elif topic == "patch":
                    related_field = "patch_management"
                elif topic == "incident":
                    related_field = "ir_plan"
                elif topic == "vendor":
                    related_field = "vendor_assessment"
                
                personalized_info = ""
                if related_field and related_field in st.session_state.questionnaire_data:
                    current_status = st.session_state.questionnaire_data[related_field]
                    personalized_info = f"\n\nBased on your questionnaire, your current approach is: {current_status}."
                
                return info + personalized_info, {}
        
        # Default response
        return "I'm here to help with your security and compliance questions. You can ask about your risk assessment, specific security controls, compliance frameworks, or recommendations to improve your security posture.", {}

def render_dashboard_page():
    """Render risk dashboard page"""
    st.markdown('<h1 class="main-header">Risk Assessment Dashboard</h1>', unsafe_allow_html=True)
    
    # Check if assessment is available
    if not st.session_state.assessment:
        st.warning("No risk assessment data available. Please upload a security questionnaire first.")
        
        if st.button("Upload Questionnaire"):
            st.session_state.current_page = 'upload'
            st.experimental_rerun()
            
        return
    
    # Get assessment data
    assessment = st.session_state.assessment
    risk_score = assessment.get('risk_score', 0)
    risk_level = assessment.get('risk_level', {})
    explanation = assessment.get('explanation', {})
    recommendations = assessment.get('recommendations', [])
    framework_compliance = assessment.get('framework_compliance', {})
    category_scores = assessment.get('category_scores', {})
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card(
            "Risk Score", 
            f"{risk_score:.1f}", 
            "/100", 
            risk_level.get('color', '#6B7280')
        )
    
    with col2:
        risk_factors = len(explanation.get('top_factors', []))
        render_metric_card(
            "Risk Factors", 
            f"{risk_factors}", 
            "Identified", 
            "#1E40AF"
        )
    
    with col3:
        rec_count = len(recommendations)
        render_metric_card(
            "Recommendations", 
            f"{rec_count}", 
            "Actions", 
            "#059669"
        )
    
    with col4:
        # Calculate potential improvement
        potential_improvement = min(100, risk_score * 0.3)  # Simplified estimate
        render_metric_card(
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
            render_risk_factors_chart(explanation['top_factors'])
        
        # Risk categories chart
        if category_scores:
            render_risk_categories_chart(category_scores)