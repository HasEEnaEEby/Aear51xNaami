# # # import streamlit as st

# # # def render_frameworks_page(compliance_knowledge=None):
# # #     """
# # #     Render the compliance frameworks information page
    
# # #     This page displays detailed information about various security and 
# # #     compliance frameworks that organizations might need to adhere to.
    
# # #     Args:
# # #         compliance_knowledge: Optional ComplianceKnowledgeBase instance for dynamic framework data
# # #     """
# # #     st.markdown('<h1 class="main-header">Compliance Frameworks</h1>', unsafe_allow_html=True)
    
# # #     # Display introduction card
# # #     _display_introduction_card()
    
# # #     # Get framework data (either from knowledge base or use static data)
# # #     frameworks_data = _get_frameworks_data(compliance_knowledge)
    
# # #     # Display framework cards in two columns
# # #     col1, col2 = st.columns(2)
    
# # #     # Distribute frameworks between columns
# # #     frameworks = list(frameworks_data.items())
# # #     mid_point = len(frameworks) // 2 + len(frameworks) % 2  # Ensure first column gets extra item if odd number
    
# # #     with col1:
# # #         for framework_id, framework in frameworks[:mid_point]:
# # #             render_framework_card(
# # #                 framework['title'],
# # #                 framework['description'],
# # #                 framework['key_controls'],
# # #                 framework['industries'],
# # #                 framework['region']
# # #             )
    
# # #     with col2:
# # #         for framework_id, framework in frameworks[mid_point:]:
# # #             render_framework_card(
# # #                 framework['title'],
# # #                 framework['description'],
# # #                 framework['key_controls'],
# # #                 framework['industries'],
# # #                 framework['region']
# # #             )

# # # def _display_introduction_card():
# # #     """Display the introductory information about compliance frameworks"""
# # #     st.markdown("""
# # #     <div class="card">
# # #         <h3>Understanding Compliance Frameworks</h3>
# # #         <p>Compliance frameworks provide structured approaches to security, privacy, and risk management. They help organizations establish controls and processes to protect information assets and meet regulatory requirements.</p>
# # #         <p>Explore the common frameworks below to better understand their scope, requirements, and how they might apply to your organization.</p>
# # #     </div>
# # #     """, unsafe_allow_html=True)

# # # def _get_frameworks_data(compliance_knowledge):
# # #     """
# # #     Get framework data either from knowledge base or use static data
    
# # #     Args:
# # #         compliance_knowledge: ComplianceKnowledgeBase instance or None
        
# # #     Returns:
# # #         Dictionary of framework data
# # #     """
# # #     # If we have a knowledge base, use it to get dynamic framework data
# # #     if compliance_knowledge:
# # #         try:
# # #             return compliance_knowledge.get_all_frameworks()
# # #         except Exception as e:
# # #             st.error(f"Error loading frameworks from knowledge base: {str(e)}")
# # #             # Fall back to static data if there's an error
    
# # #     # Static framework data as fallback
# # #     return {
# # #         "iso27001": {
# # #             "title": "ISO/IEC 27001",
# # #             "description": "International standard for information security management systems (ISMS). Provides a systematic approach to managing sensitive information.",
# # #             "key_controls": ["Information Security Management", "Risk Assessment", "Security Policy", "Asset Management", "Access Control"],
# # #             "industries": ["Financial Services", "Healthcare", "Technology", "Government"],
# # #             "region": "global"
# # #         },
# # #         "nist_csf": {
# # #             "title": "NIST Cybersecurity Framework",
# # #             "description": "Voluntary framework consisting of standards, guidelines, and best practices to manage cybersecurity risk.",
# # #             "key_controls": ["Identify", "Protect", "Detect", "Respond", "Recover"],
# # #             "industries": ["Critical Infrastructure", "Government", "Financial Services", "Healthcare"],
# # #             "region": "us"
# # #         },
# # #         "hipaa": {
# # #             "title": "HIPAA",
# # #             "description": "Health Insurance Portability and Accountability Act sets standards for protecting sensitive patient health information.",
# # #             "key_controls": ["Privacy Rule", "Security Rule", "Breach Notification Rule", "Patient Rights", "Administrative Safeguards"],
# # #             "industries": ["Healthcare Providers", "Health Plans", "Healthcare Clearinghouses", "Business Associates"],
# # #             "region": "us"
# # #         },
# # #         "pci_dss": {
# # #             "title": "PCI DSS",
# # #             "description": "Payment Card Industry Data Security Standard is a set of security standards for organizations that handle credit card information.",
# # #             "key_controls": ["Secure Network", "Cardholder Data Protection", "Vulnerability Management", "Access Control", "Monitoring and Testing"],
# # #             "industries": ["Retail", "E-commerce", "Financial Services", "Hospitality"],
# # #             "region": "global"
# # #         },
# # #         "gdpr": {
# # #             "title": "GDPR",
# # #             "description": "General Data Protection Regulation is a regulation on data protection and privacy in the European Union and the European Economic Area.",
# # #             "key_controls": ["Lawful Processing", "Consent", "Data Subject Rights", "Privacy by Design", "Data Protection Officer"],
# # #             "industries": ["Any organization handling EU citizen data", "Online Services", "Multinational Corporations"],
# # #             "region": "eu"
# # #         },
# # #         "soc2": {
# # #             "title": "SOC 2",
# # #             "description": "Service Organization Control 2 is a framework for service organizations to demonstrate their controls relevant to security, availability, processing integrity, confidentiality, and privacy.",
# # #             "key_controls": ["Security", "Availability", "Processing Integrity", "Confidentiality", "Privacy"],
# # #             "industries": ["SaaS Providers", "Cloud Services", "Data Centers", "Managed Services"],
# # #             "region": "us"
# # #         },
# # #         "ccpa": {
# # #             "title": "CCPA/CPRA",
# # #             "description": "California Consumer Privacy Act/California Privacy Rights Act gives California residents certain rights regarding their personal information.",
# # #             "key_controls": ["Right to Know", "Right to Delete", "Right to Opt-Out", "Right to Non-Discrimination", "Data Protection"],
# # #             "industries": ["Any business serving California residents", "Online Services", "Retail", "Marketing"],
# # #             "region": "us-ca"
# # #         },
# # #         "nist_800_53": {
# # #             "title": "NIST 800-53",
# # #             "description": "Security and Privacy Controls for Federal Information Systems and Organizations provides a catalog of security and privacy controls.",
# # #             "key_controls": ["Access Control", "Awareness and Training", "Audit and Accountability", "Configuration Management", "Incident Response"],
# # #             "industries": ["Federal Agencies", "Government Contractors", "Critical Infrastructure"],
# # #             "region": "us"
# # #         }
# # #     }

# # # def render_framework_card(title, description, key_controls, industries, region):
# # #     """
# # #     Render a compliance framework card
    
# # #     Args:
# # #         title: Framework title
# # #         description: Framework description
# # #         key_controls: List of key control categories
# # #         industries: List of applicable industries
# # #         region: Region code (global, us, eu, etc.)
# # #     """
# # #     # Map region to emoji flag
# # #     region_emoji = {
# # #         "global": "🌎",
# # #         "us": "🇺🇸",
# # #         "eu": "🇪🇺",
# # #         "uk": "🇬🇧",
# # #         "us-ca": "🇺🇸 (CA)",
# # #         "au": "🇦🇺",
# # #         "ca": "🇨🇦",
# # #         "jp": "🇯🇵"
# # #     }
    
# # #     flag = region_emoji.get(region, "")
    
# # #     st.markdown(f"""
# # #     <div class="framework-card">
# # #         <div style="display: flex; justify-content: space-between; align-items: center;">
# # #             <h3>{title}</h3>
# # #             <div>{flag}</div>
# # #         </div>
# # #         <p>{description}</p>
# # #         <div style="margin-top: 1rem;">
# # #             <div style="font-weight: bold;">Key Control Categories:</div>
# # #             <ul style="margin-top: 0.5rem; padding-left: 1.5rem;">
# # #     """, unsafe_allow_html=True)
    
# # #     for control in key_controls:
# # #         st.markdown(f"<li>{control}</li>", unsafe_allow_html=True)
    
# # #     st.markdown("""
# # #             </ul>
# # #         </div>
# # #         <div style="margin-top: 1rem;">
# # #             <div style="font-weight: bold;">Commonly Applied In:</div>
# # #             <div style="margin-top: 0.5rem;">
# # #     """, unsafe_allow_html=True)
    
# # #     for industry in industries:
# # #         st.markdown(f"<span style='background-color: #E0F2FE; padding: 0.2rem 0.5rem; border-radius: 4px; margin-right: 0.5rem; font-size: 0.9rem;'>{industry}</span>", unsafe_allow_html=True)
    
# # #     st.markdown("""
# # #             </div>
# # #         </div>
# # #     </div>
# # #     """, unsafe_allow_html=True)



# # import streamlit as st

# # def render_frameworks_page(compliance_knowledge=None):
# #     """
# #     Render the compliance frameworks information page with descriptions and potential risks.

# #     Args:
# #         compliance_knowledge: Optional ComplianceKnowledgeBase instance for dynamic framework data
# #     """
# #     st.markdown('<h1 class="main-header">Compliance Frameworks</h1>', unsafe_allow_html=True)

# #     # Display introduction card
# #     _display_introduction_card()

# #     # Get framework data (either from knowledge base or use static data)
# #     frameworks_data = _get_frameworks_data(compliance_knowledge)

# #     # Display framework cards in two columns
# #     col1, col2 = st.columns(2)

# #     # Distribute frameworks between columns
# #     frameworks = list(frameworks_data.items())
# #     mid_point = len(frameworks) // 2 + len(frameworks) % 2  # Ensure first column gets extra item if odd number

# #     with col1:
# #         for framework_id, framework in frameworks[:mid_point]:
# #             render_framework_card(
# #                 framework['title'],
# #                 framework['description'],
# #                 framework['key_controls'],
# #                 framework['industries'],
# #                 framework['region'],
# #                 framework.get('risks', [])  # Get risks, default to empty list if not present
# #             )

# #     with col2:
# #         for framework_id, framework in frameworks[mid_point:]:
# #             render_framework_card(
# #                 framework['title'],
# #                 framework['description'],
# #                 framework['key_controls'],
# #                 framework['industries'],
# #                 framework['region'],
# #                 framework.get('risks', [])  # Get risks, default to empty list if not present
# #             )

# # def _display_introduction_card():
# #     """Display the introductory information about compliance frameworks"""
# #     st.markdown("""
# #     <div class="card">
# #         <h3>Understanding Compliance Frameworks and Potential Risks</h3>
# #         <p>Compliance frameworks offer structured approaches to security, privacy, and risk management. Understanding the potential risks associated with each framework after analysis is crucial for effective implementation and adherence.</p>
# #         <p>Explore the common frameworks below to better understand their scope, requirements, and potential risks that might arise.</p>
# #     </div>
# #     """, unsafe_allow_html=True)

# # def _get_frameworks_data(compliance_knowledge):
# #     """
# #     Get framework data either from knowledge base or use static data, now including potential risks.

# #     Args:
# #         compliance_knowledge: ComplianceKnowledgeBase instance or None

# #     Returns:
# #         Dictionary of framework data including risks
# #     """
# #     # If we have a knowledge base, use it to get dynamic framework data
# #     if compliance_knowledge:
# #         try:
# #             frameworks_data = compliance_knowledge.get_all_frameworks()
# #             # Assuming the knowledge base also provides risk information for each framework
# #             return frameworks_data
# #         except Exception as e:
# #             st.error(f"Error loading frameworks from knowledge base: {str(e)}")
# #             # Fall back to static data if there's an error

# #     # Static framework data with placeholder risks
# #     return {
# #         "iso27001": {
# #             "title": "ISO/IEC 27001",
# #             "description": "International standard for information security management systems (ISMS). Provides a systematic approach to managing sensitive information.",
# #             "key_controls": ["Information Security Management", "Risk Assessment", "Security Policy", "Asset Management", "Access Control"],
# #             "industries": ["Financial Services", "Healthcare", "Technology", "Government"],
# #             "region": "global",
# #             "risks": [
# #                 "Initial implementation can be resource-intensive.",
# #                 "Maintaining certification requires ongoing effort and audits.",
# #                 "Scope creep if not clearly defined.",
# #                 "Potential for overly bureaucratic processes."
# #             ]
# #         },
# #         "nist_csf": {
# #             "title": "NIST Cybersecurity Framework",
# #             "description": "Voluntary framework consisting of standards, guidelines, and best practices to manage cybersecurity risk.",
# #             "key_controls": ["Identify", "Protect", "Detect", "Respond", "Recover"],
# #             "industries": ["Critical Infrastructure", "Government", "Financial Services", "Healthcare"],
# #             "region": "us",
# #             "risks": [
# #                 "Voluntary nature might lead to inconsistent adoption.",
# #                 "Can be complex to tailor to specific organizational needs.",
# #                 "Effectiveness depends on proper implementation and continuous improvement."
# #             ]
# #         },
# #         "hipaa": {
# #             "title": "HIPAA",
# #             "description": "Health Insurance Portability and Accountability Act sets standards for protecting sensitive patient health information.",
# #             "key_controls": ["Privacy Rule", "Security Rule", "Breach Notification Rule", "Patient Rights", "Administrative Safeguards"],
# #             "industries": ["Healthcare Providers", "Health Plans", "Healthcare Clearinghouses", "Business Associates"],
# #             "region": "us",
# #             "risks": [
# #                 "Strict penalties for non-compliance.",
# #                 "Complex regulations requiring deep understanding.",
# #                 "Challenges in balancing patient access with privacy.",
# #                 "Constant updates to regulations."
# #             ]
# #         },
# #         "pci_dss": {
# #             "title": "PCI DSS",
# #             "description": "Payment Card Industry Data Security Standard is a set of security standards for organizations that handle credit card information.",
# #             "key_controls": ["Secure Network", "Cardholder Data Protection", "Vulnerability Management", "Access Control", "Monitoring and Testing"],
# #             "industries": ["Retail", "E-commerce", "Financial Services", "Hospitality"],
# #             "region": "global",
# #             "risks": [
# #                 "Failure to comply can lead to significant financial penalties and reputational damage.",
# #                 "Maintaining compliance requires ongoing vigilance.",
# #                 "The standard evolves, requiring continuous adaptation."
# #             ]
# #         },
# #         "gdpr": {
# #             "title": "GDPR",
# #             "description": "General Data Protection Regulation is a regulation on data protection and privacy in the European Union and the European Economic Area.",
# #             "key_controls": ["Lawful Processing", "Consent", "Data Subject Rights", "Privacy by Design", "Data Protection Officer"],
# #             "industries": ["Any organization handling EU citizen data", "Online Services", "Multinational Corporations"],
# #             "region": "eu",
# #             "risks": [
# #                 "Broad scope and strict requirements can be challenging to implement.",
# #                 "Significant fines for non-compliance.",
# #                 "Complex rules regarding data transfers and processing.",
# #                 "Requires robust data governance and privacy programs."
# #             ]
# #         },
# #         "soc2": {
# #             "title": "SOC 2",
# #             "description": "Service Organization Control 2 is a framework for service organizations to demonstrate their controls relevant to security, availability, processing integrity, confidentiality, and privacy.",
# #             "key_controls": ["Security", "Availability", "Processing Integrity", "Confidentiality", "Privacy"],
# #             "industries": ["SaaS Providers", "Cloud Services", "Data Centers", "Managed Services"],
# #             "region": "us",
# #             "risks": [
# #                 "The audit process can be time-consuming and expensive.",
# #                 "Requires a strong understanding of the Trust Services Criteria.",
# #                 "Maintaining compliance is an ongoing effort."
# #             ]
# #         },
# #         "ccpa": {
# #             "title": "CCPA/CPRA",
# #             "description": "California Consumer Privacy Act/California Privacy Rights Act gives California residents certain rights regarding their personal information.",
# #             "key_controls": ["Right to Know", "Right to Delete", "Right to Opt-Out", "Right to Non-Discrimination", "Data Protection"],
# #             "industries": ["Any business serving California residents", "Online Services", "Retail", "Marketing"],
# #             "region": "us-ca",
# #             "risks": [
# #                 "Specific to California residents, adding complexity for national businesses.",
# #                 "Evolving regulations require continuous monitoring.",
# #                 "Operational challenges in fulfilling consumer rights requests."
# #             ]
# #         },
# #         "nist_800_53": {
# #             "title": "NIST 800-53",
# #             "description": "Security and Privacy Controls for Federal Information Systems and Organizations provides a catalog of security and privacy controls.",
# #             "key_controls": ["Access Control", "Awareness and Training", "Audit and Accountability", "Configuration Management", "Incident Response"],
# #             "industries": ["Federal Agencies", "Government Contractors", "Critical Infrastructure"],
# #             "region": "us",
# #             "risks": [
# #                 "Extensive set of controls can be overwhelming.",
# #                 "Requires careful selection and tailoring of controls.",
# #                 "Compliance can be a significant undertaking."
# #             ]
# #         }
# #     }

# # def render_framework_card(title, description, key_controls, industries, region, risks):
# #     """
# #     Render a compliance framework card, now including potential risks.

# #     Args:
# #         title: Framework title
# #         description: Framework description
# #         key_controls: List of key control categories
# #         industries: List of applicable industries
# #         region: Region code (global, us, eu, etc.)
# #         risks: List of potential risks associated with the framework
# #     """
# #     # Map region to emoji flag
# #     region_emoji = {
# #         "global": "🌎",
# #         "us": "🇺🇸",
# #         "eu": "🇪🇺",
# #         "uk": "🇬🇧",
# #         "us-ca": "🇺🇸 (CA)",
# #         "au": "🇦🇺",
# #         "ca": "🇨🇦",
# #         "jp": "🇯🇵"
# #     }

# #     flag = region_emoji.get(region, "")

# #     st.markdown(f"""
# #     <div class="framework-card">
# #         <div style="display: flex; justify-content: space-between; align-items: center;">
# #             <h3>{title}</h3>
# #             <div>{flag}</div>
# #         </div>
# #         <p>{description}</p>
# #         <div style="margin-top: 1rem;">
# #             <div style="font-weight: bold;">Key Control Categories:</div>
# #             <ul style="margin-top: 0.5rem; padding-left: 1.5rem;">
# #     """, unsafe_allow_html=True)

# #     for control in key_controls:
# #         st.markdown(f"<li>{control}</li>", unsafe_allow_html=True)

# #     st.markdown("""
# #             </ul>
# #         </div>
# #         <div style="margin-top: 1rem;">
# #             <div style="font-weight: bold;">Commonly Applied In:</div>
# #             <div style="margin-top: 0.5rem;">
# #     """, unsafe_allow_html=True)

# #     for industry in industries:
# #         st.markdown(f"<span style='background-color: #E0F2FE; padding: 0.2rem 0.5rem; border-radius: 4px; margin-right: 0.5rem; font-size: 0.9rem;'>{industry}</span>", unsafe_allow_html=True)

# #     st.markdown("""
# #             </div>
# #         </div>
# #         <div style="margin-top: 1rem;">
# #             <div style="font-weight: bold;">Potential Risks After Analysis:</div>
# #             <ul style="margin-top: 0.5rem; padding-left: 1.5rem;">
# #     """, unsafe_allow_html=True)

# #     if risks:
# #         for risk in risks:
# #             st.markdown(f"<li style='color: orange;'>⚠️ {risk}</li>", unsafe_allow_html=True)
# #     else:
# #         st.markdown("<li style='color: gray;'>No specific risks identified in the analysis.</li>", unsafe_allow_html=True)

# #     st.markdown("""
# #             </ul>
# #         </div>
# #     </div>
# #     """, unsafe_allow_html=True)

# # # Example of how you might use it with a hypothetical ComplianceKnowledgeBase
# # # class ComplianceKnowledgeBase:
# # #     def get_all_frameworks(self):
# # #         # In a real implementation, this would fetch data from your knowledge source
# # #         return {
# # #             "custom_framework": {
# # #                 "title": "Custom Security Framework",
# # #                 "description": "A framework tailored to specific organizational needs.",
# # #                 "key_controls": ["Custom Control 1", "Custom Control 2", "Custom Control 3"],
# # #                 "industries": ["Specific Industry"],
# # #                 "region": "global",
# # #                 "risks": ["Risk of not aligning with industry best practices.", "Challenge in maintaining up-to-date knowledge."]
# # #             }
# # #             # ... more frameworks from the knowledge base
# # #         }

# # # if __name__ == "__main__":
# # #     # Example usage with static data
# # #     render_frameworks_page()

# # #     # Example usage with a ComplianceKnowledgeBase (uncomment to test if you have one)
# # #     # knowledge_base = ComplianceKnowledgeBase()
# # #     # render_frameworks_page(knowledge_base)

# # # Add some custom CSS to style the cards and header
# # st.markdown(
# #     """
# #     <style>
# #     .main-header {
# #         color: #3366FF;
# #         text-align: center;
# #         padding-bottom: 1rem;
# #     }
# #     .card {
# #         background-color: #f7f7f7;
# #         padding: 1rem;
# #         border-radius: 5px;
# #         margin-bottom: 1rem;
# #         border: 1px solid #ddd;
# #     }
# #     .card h3 {
# #         color: #3366FF;
# #         margin-top: 0;
# #     }
# #     .framework-card {
# #         background-color: #fff;
# #         padding: 1rem;
# #         border-radius: 5px;
# #         margin-bottom: 1rem;
# #         border: 1px solid #ddd;
# #     }
# #     .framework-card h3 {
# #         color: #2E86C1;
# #         margin-top: 0;
# #     }
# #     </style>
# #     """,
# #     unsafe_allow_html=True,
# # )


# import streamlit as st

# def render_frameworks_page(compliance_knowledge=None):
#     """
#     Render the compliance frameworks information page with descriptions and potential risks.

#     Args:
#         compliance_knowledge: Optional ComplianceKnowledgeBase instance for dynamic framework data
#     """
#     st.markdown('<h1 class="main-header">Compliance Frameworks</h1>', unsafe_allow_html=True)

#     # Display introduction card
#     _display_introduction_card()

#     # Get framework data (either from knowledge base or use static data)
#     frameworks_data = _get_frameworks_data(compliance_knowledge)

#     # Display framework cards in two columns
#     col1, col2 = st.columns(2)

#     # Distribute frameworks between columns
#     frameworks = list(frameworks_data.items())
#     mid_point = len(frameworks) // 2 + len(frameworks) % 2  # Ensure first column gets extra item if odd number

#     with col1:
#         for framework_id, framework in frameworks[:mid_point]:
#             render_framework_card(
#                 framework['title'],
#                 framework['description'],
#                 framework['key_controls'],
#                 framework['industries'],
#                 framework['region'],
#                 framework.get('risks', [])  # Get risks, default to empty list if not present
#             )

#     with col2:
#         for framework_id, framework in frameworks[mid_point:]:
#             render_framework_card(
#                 framework['title'],
#                 framework['description'],
#                 framework['key_controls'],
#                 framework['industries'],
#                 framework['region'],
#                 framework.get('risks', [])  # Get risks, default to empty list if not present
#             )

# def _display_introduction_card():
#     """Display the introductory information about compliance frameworks"""
#     st.markdown("""
#     <div class="card">
#         <h3>Understanding Compliance Frameworks and Potential Risks</h3>
#         <p>Compliance frameworks offer structured approaches to security, privacy, and risk management. Understanding the potential risks associated with each framework after analysis is crucial for effective implementation and adherence.</p>
#         <p>Explore the common frameworks below to better understand their scope, requirements, and potential risks that might arise.</p>
#     </div>
#     """, unsafe_allow_html=True)

# def _get_frameworks_data(compliance_knowledge):
#     """
#     Get framework data either from knowledge base or use static data, now including potential risks.

#     Args:
#         compliance_knowledge: ComplianceKnowledgeBase instance or None

#     Returns:
#         Dictionary of framework data including risks
#     """
#     # If we have a knowledge base, use it to get dynamic framework data
#     if compliance_knowledge:
#         try:
#             frameworks_data = compliance_knowledge.get_all_frameworks()
#             # Assuming the knowledge base also provides risk information for each framework
#             return frameworks_data
#         except Exception as e:
#             st.error(f"Error loading frameworks from knowledge base: {str(e)}")
#             # Fall back to static data if there's an error

#     # Static framework data with placeholder risks
#     return {
#         "iso27001": {
#             "title": "ISO/IEC 27001",
#             "description": "International standard for information security management systems (ISMS). Provides a systematic approach to managing sensitive information.",
#             "key_controls": ["Information Security Management", "Risk Assessment", "Security Policy", "Asset Management", "Access Control"],
#             "industries": ["Financial Services", "Healthcare", "Technology", "Government"],
#             "region": "global",
#             "risks": [
#                 "Initial implementation can be resource-intensive.",
#                 "Maintaining certification requires ongoing effort and audits.",
#                 "Scope creep if not clearly defined.",
#                 "Potential for overly bureaucratic processes."
#             ]
#         },
#         "nist_csf": {
#             "title": "NIST Cybersecurity Framework",
#             "description": "Voluntary framework consisting of standards, guidelines, and best practices to manage cybersecurity risk.",
#             "key_controls": ["Identify", "Protect", "Detect", "Respond", "Recover"],
#             "industries": ["Critical Infrastructure", "Government", "Financial Services", "Healthcare"],
#             "region": "us",
#             "risks": [
#                 "Voluntary nature might lead to inconsistent adoption.",
#                 "Can be complex to tailor to specific organizational needs.",
#                 "Effectiveness depends on proper implementation and continuous improvement."
#             ]
#         },
#         "hipaa": {
#             "title": "HIPAA",
#             "description": "Health Insurance Portability and Accountability Act sets standards for protecting sensitive patient health information.",
#             "key_controls": ["Privacy Rule", "Security Rule", "Breach Notification Rule", "Patient Rights", "Administrative Safeguards"],
#             "industries": ["Healthcare Providers", "Health Plans", "Healthcare Clearinghouses", "Business Associates"],
#             "region": "us",
#             "risks": [
#                 "Strict penalties for non-compliance.",
#                 "Complex regulations requiring deep understanding.",
#                 "Challenges in balancing patient access with privacy.",
#                 "Constant updates to regulations."
#             ]
#         },
#         "pci_dss": {
#             "title": "PCI DSS",
#             "description": "Payment Card Industry Data Security Standard is a set of security standards for organizations that handle credit card information.",
#             "key_controls": ["Secure Network", "Cardholder Data Protection", "Vulnerability Management", "Access Control", "Monitoring and Testing"],
#             "industries": ["Retail", "E-commerce", "Financial Services", "Hospitality"],
#             "region": "global",
#             "risks": [
#                 "Failure to comply can lead to significant financial penalties and reputational damage.",
#                 "Maintaining compliance requires ongoing vigilance.",
#                 "The standard evolves, requiring continuous adaptation."
#             ]
#         },
#         "gdpr": {
#             "title": "GDPR",
#             "description": "General Data Protection Regulation is a regulation on data protection and privacy in the European Union and the European Economic Area.",
#             "key_controls": ["Lawful Processing", "Consent", "Data Subject Rights", "Privacy by Design", "Data Protection Officer"],
#             "industries": ["Any organization handling EU citizen data", "Online Services", "Multinational Corporations"],
#             "region": "eu",
#             "risks": [
#                 "Broad scope and strict requirements can be challenging to implement.",
#                 "Significant fines for non-compliance.",
#                 "Complex rules regarding data transfers and processing.",
#                 "Requires robust data governance and privacy programs."
#             ]
#         },
#         "soc2": {
#             "title": "SOC 2",
#             "description": "Service Organization Control 2 is a framework for service organizations to demonstrate their controls relevant to security, availability, processing integrity, confidentiality, and privacy.",
#             "key_controls": ["Security", "Availability", "Processing Integrity", "Confidentiality", "Privacy"],
#             "industries": ["SaaS Providers", "Cloud Services", "Data Centers", "Managed Services"],
#             "region": "us",
#             "risks": [
#                 "The audit process can be time-consuming and expensive.",
#                 "Requires a strong understanding of the Trust Services Criteria.",
#                 "Maintaining compliance is an ongoing effort."
#             ]
#         },
#         "ccpa": {
#             "title": "CCPA/CPRA",
#             "description": "California Consumer Privacy Act/California Privacy Rights Act gives California residents certain rights regarding their personal information.",
#             "key_controls": ["Right to Know", "Right to Delete", "Right to Opt-Out", "Right to Non-Discrimination", "Data Protection"],
#             "industries": ["Any business serving California residents", "Online Services", "Retail", "Marketing"],
#             "region": "us-ca",
#             "risks": [
#                 "Specific to California residents, adding complexity for national businesses.",
#                 "Evolving regulations require continuous monitoring.",
#                 "Operational challenges in fulfilling consumer rights requests."
#             ]
#         },
#         "nist_800_53": {
#             "title": "NIST 800-53",
#             "description": "Security and Privacy Controls for Federal Information Systems and Organizations provides a catalog of security and privacy controls.",
#             "key_controls": ["Access Control", "Awareness and Training", "Audit and Accountability", "Configuration Management", "Incident Response"],
#             "industries": ["Federal Agencies", "Government Contractors", "Critical Infrastructure"],
#             "region": "us",
#             "risks": [
#                 "Extensive set of controls can be overwhelming.",
#                 "Requires careful selection and tailoring of controls.",
#                 "Compliance can be a significant undertaking."
#             ]
#         }
#     }

# def render_framework_card(title, description, key_controls, industries, region, risks):
#     """
#     Render a compliance framework card, now including potential risks.

#     Args:
#         title: Framework title
#         description: Framework description
#         key_controls: List of key control categories
#         industries: List of applicable industries
#         region: Region code (global, us, eu, etc.)
#         risks: List of potential risks associated with the framework
#     """
#     # Map region to emoji flag
#     region_emoji = {
#         "global": "🌎",
#         "us": "🇺🇸",
#         "eu": "🇪🇺",
#         "uk": "🇬🇧",
#         "us-ca": "🇺🇸 (CA)",
#         "au": "🇦🇺",
#         "ca": "🇨🇦",
#         "jp": "🇯🇵"
#     }

#     flag = region_emoji.get(region, "")

#     st.markdown(f"""
#     <div class="framework-card">
#         <div style="display: flex; justify-content: space-between; align-items: center;">
#             <h3>{title}</h3>
#             <div>{flag}</div>
#         </div>
#         <p>{description}</p>
#         <div style="margin-top: 1rem;">
#             <div style="font-weight: bold;">Key Control Categories:</div>
#             <ul style="margin-top: 0.5rem; padding-left: 1.5rem;">
#     """, unsafe_allow_html=True)

#     for control in key_controls:
#         st.markdown(f"<li>{control}</li>", unsafe_allow_html=True)

#     st.markdown("""
#             </ul>
#         </div>
#         <div style="margin-top: 1rem;">
#             <div style="font-weight: bold;">Commonly Applied In:</div>
#             <div style="margin-top: 0.5rem;">
#     """, unsafe_allow_html=True)

#     for industry in industries:
#         st.markdown(f"<span style='background-color: #E0F2FE; padding: 0.2rem 0.5rem; border-radius: 4px; margin-right: 0.5rem; font-size: 0.9rem;'>{industry}</span>", unsafe_allow_html=True)

#     st.markdown("""
#             </div>
#         </div>
#         <div style="margin-top: 1rem;">
#             <div style="font-weight: bold;">Potential Risks After Analysis:</div>
#             <ul style="margin-top: 0.5rem; padding-left: 1.5rem;">
#     """, unsafe_allow_html=True)

#     if risks:
#         for risk in risks:
#             st.markdown(f"<li style='color: orange;'>⚠️ {risk}</li>", unsafe_allow_html=True)
#     else:
#         st.markdown("<li style='color: gray;'>No specific risks identified in the analysis.</li>", unsafe_allow_html=True)

#     st.markdown("""
#             </ul>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)

# # Example of how you might use it with a hypothetical ComplianceKnowledgeBase
# # class ComplianceKnowledgeBase:
# #     def get_all_frameworks(self):
# #         # In a real implementation, this would fetch data from your knowledge source
# #         return {
# #             "custom_framework": {
# #                 "title": "Custom Security Framework",
# #                 "description": "A framework tailored to specific organizational needs.",
# #                 "key_controls": ["Custom Control 1", "Custom Control 2", "Custom Control 3"],
# #                 "industries": ["Specific Industry"],
# #                 "region": "global",
# #                 "risks": ["Risk of not aligning with industry best practices.", "Challenge in maintaining up-to-date knowledge."]
# #             }
# #             # ... more frameworks from the knowledge base
# #         }

# if __name__ == "__main__":
#     # Call the function to render the page
#     render_frameworks_page()

# # Add some custom CSS to style the cards and header
# st.markdown(
#     """
#     <style>
#     .main-header {
#         color: #3366FF;
#         text-align: center;
#         padding-bottom: 1rem;
#     }
#     .card {
#         background-color: #f7f7f7;
#         padding: 1rem;
#         border-radius: 5px;
#         margin-bottom: 1rem;
#         border: 1px solid #ddd;
#     }
#     .card h3 {
#         color: #3366FF;
#         margin-top: 0;
#     }
#     .framework-card {
#         background-color: #fff;
#         padding: 1rem;
#         border-radius: 5px;
#         margin-bottom: 1rem;
#         border: 1px solid #ddd;
#     }
#     .framework-card h3 {
#         color: #2E86C1;
#         margin-top: 0;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )
import streamlit as st

def render_frameworks_page(compliance_knowledge=None):
    """
    Render the compliance frameworks information page with descriptions and potential risks.

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
                framework['region'],
                framework.get('risks', [])  # Get risks, default to empty list if not present
            )

    with col2:
        for framework_id, framework in frameworks[mid_point:]:
            render_framework_card(
                framework['title'],
                framework['description'],
                framework['key_controls'],
                framework['industries'],
                framework['region'],
                framework.get('risks', [])  # Get risks, default to empty list if not present
            )

def _display_introduction_card():
    """Display the introductory information about compliance frameworks"""
    st.markdown("""
    <div class="intro-card">
        <h3>Understanding Compliance Frameworks and Potential Risks</h3>
        <p>Compliance frameworks offer structured approaches to security, privacy, and risk management. Understanding the potential risks associated with each framework after analysis is crucial for effective implementation and adherence.</p>
        <p>Explore the common frameworks below to better understand their scope, requirements, and potential risks that might arise.</p>
    </div>
    """, unsafe_allow_html=True)

def _get_frameworks_data(compliance_knowledge):
    """
    Get framework data either from knowledge base or use static data, now including potential risks.

    Args:
        compliance_knowledge: ComplianceKnowledgeBase instance or None

    Returns:
        Dictionary of framework data including risks
    """
    # If we have a knowledge base, use it to get dynamic framework data
    if compliance_knowledge:
        try:
            frameworks_data = compliance_knowledge.get_all_frameworks()
            # Assuming the knowledge base also provides risk information for each framework
            return frameworks_data
        except Exception as e:
            st.error(f"Error loading frameworks from knowledge base: {str(e)}")
            # Fall back to static data if there's an error

    # Static framework data with placeholder risks
    return {
        "iso27001": {
            "title": "ISO/IEC 27001",
            "description": "International standard for information security management systems (ISMS). Provides a systematic approach to managing sensitive information.",
            "key_controls": ["Information Security Management", "Risk Assessment", "Security Policy", "Asset Management", "Access Control"],
            "industries": ["Financial Services", "Healthcare", "Technology", "Government"],
            "region": "global",
            "risks": [
                "Initial implementation can be resource-intensive.",
                "Maintaining certification requires ongoing effort and audits.",
                "Scope creep if not clearly defined.",
                "Potential for overly bureaucratic processes."
            ]
        },
        "nist_csf": {
            "title": "NIST Cybersecurity Framework",
            "description": "Voluntary framework consisting of standards, guidelines, and best practices to manage cybersecurity risk.",
            "key_controls": ["Identify", "Protect", "Detect", "Respond", "Recover"],
            "industries": ["Critical Infrastructure", "Government", "Financial Services", "Healthcare"],
            "region": "us",
            "risks": [
                "Voluntary nature might lead to inconsistent adoption.",
                "Can be complex to tailor to specific organizational needs.",
                "Effectiveness depends on proper implementation and continuous improvement."
            ]
        },
        "hipaa": {
            "title": "HIPAA",
            "description": "Health Insurance Portability and Accountability Act sets standards for protecting sensitive patient health information.",
            "key_controls": ["Privacy Rule", "Security Rule", "Breach Notification Rule", "Patient Rights", "Administrative Safeguards"],
            "industries": ["Healthcare Providers", "Health Plans", "Healthcare Clearinghouses", "Business Associates"],
            "region": "us",
            "risks": [
                "Strict penalties for non-compliance.",
                "Complex regulations requiring deep understanding.",
                "Challenges in balancing patient access with privacy.",
                "Constant updates to regulations."
            ]
        },
        "pci_dss": {
            "title": "PCI DSS",
            "description": "Payment Card Industry Data Security Standard is a set of security standards for organizations that handle credit card information.",
            "key_controls": ["Secure Network", "Cardholder Data Protection", "Vulnerability Management", "Access Control", "Monitoring and Testing"],
            "industries": ["Retail", "E-commerce", "Financial Services", "Hospitality"],
            "region": "global",
            "risks": [
                "Failure to comply can lead to significant financial penalties and reputational damage.",
                "Maintaining compliance requires ongoing vigilance.",
                "The standard evolves, requiring continuous adaptation."
            ]
        },
        "gdpr": {
            "title": "GDPR",
            "description": "General Data Protection Regulation is a regulation on data protection and privacy in the European Union and the European Economic Area.",
            "key_controls": ["Lawful Processing", "Consent", "Data Subject Rights", "Privacy by Design", "Data Protection Officer"],
            "industries": ["Any organization handling EU citizen data", "Online Services", "Multinational Corporations"],
            "region": "eu",
            "risks": [
                "Broad scope and strict requirements can be challenging to implement.",
                "Significant fines for non-compliance.",
                "Complex rules regarding data transfers and processing.",
                "Requires robust data governance and privacy programs."
            ]
        },
        "soc2": {
            "title": "SOC 2",
            "description": "Service Organization Control 2 is a framework for service organizations to demonstrate their controls relevant to security, availability, processing integrity, confidentiality, and privacy.",
            "key_controls": ["Security", "Availability", "Processing Integrity", "Confidentiality", "Privacy"],
            "industries": ["SaaS Providers", "Cloud Services", "Data Centers", "Managed Services"],
            "region": "us",
            "risks": [
                "The audit process can be time-consuming and expensive.",
                "Requires a strong understanding of the Trust Services Criteria.",
                "Maintaining compliance is an ongoing effort."
            ]
        },
        "ccpa": {
            "title": "CCPA/CPRA",
            "description": "California Consumer Privacy Act/California Privacy Rights Act gives California residents certain rights regarding their personal information.",
            "key_controls": ["Right to Know", "Right to Delete", "Right to Opt-Out", "Right to Non-Discrimination", "Data Protection"],
            "industries": ["Any business serving California residents", "Online Services", "Retail", "Marketing"],
            "region": "us-ca",
            "risks": [
                "Specific to California residents, adding complexity for national businesses.",
                "Evolving regulations require continuous monitoring.",
                "Operational challenges in fulfilling consumer rights requests."
            ]
        },
        "nist_800_53": {
            "title": "NIST 800-53",
            "description": "Security and Privacy Controls for Federal Information Systems and Organizations provides a catalog of security and privacy controls.",
            "key_controls": ["Access Control", "Awareness and Training", "Audit and Accountability", "Configuration Management", "Incident Response"],
            "industries": ["Federal Agencies", "Government Contractors", "Critical Infrastructure"],
            "region": "us",
            "risks": [
                "Extensive set of controls can be overwhelming.",
                "Requires careful selection and tailoring of controls.",
                "Compliance can be a significant undertaking."
            ]
        }
    }

def render_framework_card(title, description, key_controls, industries, region, risks):
    """
    Render a compliance framework card, now with adjusted styling.

    Args:
        title: Framework title
        description: Framework description
        key_controls: List of key control categories
        industries: List of applicable industries
        region: Region code (global, us, eu, etc.)
        risks: List of potential risks associated with the framework
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
        <div class="framework-header">
            <h3>{title}</h3>
            <div class="region-flag">{flag}</div>
        </div>
        <p class="framework-description">{description}</p>
        <div class="framework-section">
            <div class="section-title">Key Control Categories:</div>
            <ul class="framework-list">
    """, unsafe_allow_html=True)

    for control in key_controls:
        st.markdown(f"<li class='list-item'>{control}</li>", unsafe_allow_html=True)

    st.markdown("""
            </ul>
        </div>
        <div class="framework-section">
            <div class="section-title">Commonly Applied In:</div>
            <div class="industry-tags">
    """, unsafe_allow_html=True)

    for industry in industries:
        st.markdown(f"<span class='industry-tag'>{industry}</span>", unsafe_allow_html=True)

    st.markdown("""
            </div>
        </div>
        <div class="framework-section">
            <div class="section-title">Potential Risks After Analysis:</div>
            <ul class="framework-list">
    """, unsafe_allow_html=True)

    if risks:
        for risk in risks:
            st.markdown(f"<li class='risk-item'>⚠️ {risk}</li>", unsafe_allow_html=True)
    else:
        st.markdown("<li class='no-risks'>No specific risks identified in the analysis.</li>", unsafe_allow_html=True)

    st.markdown("""
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    # Call the function to render the page
    render_frameworks_page()

# Enhanced custom CSS for better contrast and no white backgrounds
st.markdown(
    """
    <style>
    body {
        background-color: #f0f2f6; /* Light gray background for the whole page */
        color: #333; /* Dark gray default text color */
        font-family: sans-serif;
    }
    .main-header {
        color: #2E86C1; /* A more prominent header color */
        text-align: center;
        padding-bottom: 1.5rem;
        font-weight: bold;
    }
    .intro-card {
        background-color: transparent; /* Remove white background */
        padding: 1.5rem;
        border-radius: 5px;
        margin-bottom: 2rem;
        border: 1px solid #ccc; /* Optional subtle border */
    }
    .intro-card h3 {
        color: #3366FF;
        margin-top: 0;
        font-weight: bold;
    }
    .framework-card {
        background-color: transparent; /* Remove white background */
        padding: 1.5rem;
        border-radius: 5px;
        margin-bottom: 2rem;
        border: 1px solid #ccc; /* Optional subtle border */
    }
    .framework-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    .framework-header h3 {
        color: #1C75BC; /* Darker title for frameworks */
        margin-top: 0;
        font-weight: bold;
    }
    .region-flag {
        font-size: 1.2rem;
    }
    .framework-description {
        color: #555; /* Slightly lighter description text */
        margin-bottom: 1rem;
    }
    .framework-section {
        margin-top: 1rem;
    }
    .section-title {
        font-weight: bold;
        color: #444;
        margin-bottom: 0.5rem;
    }
    .framework-list {
        margin-top: 0.3rem;
        padding-left: 1.5rem;
        list-style-type: disc;
        color: #666;
    }
    .list-item {
        margin-bottom: 0.3rem;
    }
    .industry-tags {
        margin-top: 0.5rem;
    }
    .industry-tag {
        background-color: #e6f2ff; /* Light blue background for tags */
        color: #336699; /* Darker text for tags */
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        margin-right: 0.5rem;
        font-size: 0.9rem;
    }
    .risk-item {
        color: #d35400; /* Orange for risks */
        margin-bottom: 0.3rem;
    }
    .no-risks {
        color: #777;
    }
    </style>
    """,
    unsafe_allow_html=True,
)