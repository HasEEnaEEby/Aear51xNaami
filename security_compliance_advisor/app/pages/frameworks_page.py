import streamlit as st

def render_frameworks_page(compliance_knowledge=None):
    """
    Render the compliance frameworks information page
    
    This page displays detailed information about various security and 
    compliance frameworks that organizations might need to adhere to.
    
    Args:
        compliance_knowledge: Optional ComplianceKnowledgeBase instance for dynamic framework data
    """
    st.markdown('<h1 class="main-header">Compliance Frameworks</h1>', unsafe_allow_html=True)
    
    # Display introduction card
    _display_introduction_card()
    
    # Get framework data (either from knowledge base or use static data)
    frameworks_data = _get_frameworks_data(compliance_knowledge)
    
    # Display framework cards in two columns
    col1, col2 = st.columns(2)
    
    # Distribute frameworks between columns
    frameworks = list(frameworks_data.items())
    mid_point = len(frameworks) // 2 + len(frameworks) % 2  # Ensure first column gets extra item if odd number
    
    with col1:
        for framework_id, framework in frameworks[:mid_point]:
            render_framework_card(
                framework['title'],
                framework['description'],
                framework['key_controls'],
                framework['industries'],
                framework['region']
            )
    
    with col2:
        for framework_id, framework in frameworks[mid_point:]:
            render_framework_card(
                framework['title'],
                framework['description'],
                framework['key_controls'],
                framework['industries'],
                framework['region']
            )

def _display_introduction_card():
    """Display the introductory information about compliance frameworks"""
    st.markdown("""
    <div class="card">
        <h3>Understanding Compliance Frameworks</h3>
        <p>Compliance frameworks provide structured approaches to security, privacy, and risk management. They help organizations establish controls and processes to protect information assets and meet regulatory requirements.</p>
        <p>Explore the common frameworks below to better understand their scope, requirements, and how they might apply to your organization.</p>
    </div>
    """, unsafe_allow_html=True)

def _get_frameworks_data(compliance_knowledge):
    """
    Get framework data either from knowledge base or use static data
    
    Args:
        compliance_knowledge: ComplianceKnowledgeBase instance or None
        
    Returns:
        Dictionary of framework data
    """
    # If we have a knowledge base, use it to get dynamic framework data
    if compliance_knowledge:
        try:
            return compliance_knowledge.get_all_frameworks()
        except Exception as e:
            st.error(f"Error loading frameworks from knowledge base: {str(e)}")
            # Fall back to static data if there's an error
    
    # Static framework data as fallback
    return {
        "iso27001": {
            "title": "ISO/IEC 27001",
            "description": "International standard for information security management systems (ISMS). Provides a systematic approach to managing sensitive information.",
            "key_controls": ["Information Security Management", "Risk Assessment", "Security Policy", "Asset Management", "Access Control"],
            "industries": ["Financial Services", "Healthcare", "Technology", "Government"],
            "region": "global"
        },
        "nist_csf": {
            "title": "NIST Cybersecurity Framework",
            "description": "Voluntary framework consisting of standards, guidelines, and best practices to manage cybersecurity risk.",
            "key_controls": ["Identify", "Protect", "Detect", "Respond", "Recover"],
            "industries": ["Critical Infrastructure", "Government", "Financial Services", "Healthcare"],
            "region": "us"
        },
        "hipaa": {
            "title": "HIPAA",
            "description": "Health Insurance Portability and Accountability Act sets standards for protecting sensitive patient health information.",
            "key_controls": ["Privacy Rule", "Security Rule", "Breach Notification Rule", "Patient Rights", "Administrative Safeguards"],
            "industries": ["Healthcare Providers", "Health Plans", "Healthcare Clearinghouses", "Business Associates"],
            "region": "us"
        },
        "pci_dss": {
            "title": "PCI DSS",
            "description": "Payment Card Industry Data Security Standard is a set of security standards for organizations that handle credit card information.",
            "key_controls": ["Secure Network", "Cardholder Data Protection", "Vulnerability Management", "Access Control", "Monitoring and Testing"],
            "industries": ["Retail", "E-commerce", "Financial Services", "Hospitality"],
            "region": "global"
        },
        "gdpr": {
            "title": "GDPR",
            "description": "General Data Protection Regulation is a regulation on data protection and privacy in the European Union and the European Economic Area.",
            "key_controls": ["Lawful Processing", "Consent", "Data Subject Rights", "Privacy by Design", "Data Protection Officer"],
            "industries": ["Any organization handling EU citizen data", "Online Services", "Multinational Corporations"],
            "region": "eu"
        },
        "soc2": {
            "title": "SOC 2",
            "description": "Service Organization Control 2 is a framework for service organizations to demonstrate their controls relevant to security, availability, processing integrity, confidentiality, and privacy.",
            "key_controls": ["Security", "Availability", "Processing Integrity", "Confidentiality", "Privacy"],
            "industries": ["SaaS Providers", "Cloud Services", "Data Centers", "Managed Services"],
            "region": "us"
        },
        "ccpa": {
            "title": "CCPA/CPRA",
            "description": "California Consumer Privacy Act/California Privacy Rights Act gives California residents certain rights regarding their personal information.",
            "key_controls": ["Right to Know", "Right to Delete", "Right to Opt-Out", "Right to Non-Discrimination", "Data Protection"],
            "industries": ["Any business serving California residents", "Online Services", "Retail", "Marketing"],
            "region": "us-ca"
        },
        "nist_800_53": {
            "title": "NIST 800-53",
            "description": "Security and Privacy Controls for Federal Information Systems and Organizations provides a catalog of security and privacy controls.",
            "key_controls": ["Access Control", "Awareness and Training", "Audit and Accountability", "Configuration Management", "Incident Response"],
            "industries": ["Federal Agencies", "Government Contractors", "Critical Infrastructure"],
            "region": "us"
        }
    }

def render_framework_card(title, description, key_controls, industries, region):
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
        "us-ca": "🇺🇸 (CA)",
        "au": "🇦🇺",
        "ca": "🇨🇦",
        "jp": "🇯🇵"
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