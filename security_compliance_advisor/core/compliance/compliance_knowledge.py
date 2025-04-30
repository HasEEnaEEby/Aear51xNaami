# import json
# import os
# import numpy as np
# from typing import Dict, List, Any, Optional, Union, Tuple

# class ComplianceKnowledgeBase:
#     """
#     Knowledge base for compliance frameworks, standards, and security controls.
#     This class provides methods to access and query information about various
#     compliance frameworks and map questionnaire responses to compliance requirements.
#     """
    
#     def __init__(self, data_path: Optional[str] = None):
#         """
#         Initialize the Compliance Knowledge Base
        
#         Args:
#             data_path: Optional path to JSON files containing framework definitions
#         """
#         self.frameworks = {}
#         self.controls = {}
#         self.control_mappings = {}
#         self.risk_patterns = {}
        
#         # Load default frameworks if no data path provided
#         if not data_path:
#             self._load_default_frameworks()
#         else:
#             self._load_frameworks_from_path(data_path)
    
#     def _load_default_frameworks(self):
#         """Load default built-in frameworks"""
#         # ISO 27001 Framework
#         self.frameworks["iso27001"] = {
#             "name": "ISO/IEC 27001",
#             "description": "International standard for information security management systems (ISMS)",
#             "version": "2013",
#             "categories": [
#                 {"id": "A5", "name": "Information Security Policies"},
#                 {"id": "A6", "name": "Organization of Information Security"},
#                 {"id": "A7", "name": "Human Resource Security"},
#                 {"id": "A8", "name": "Asset Management"},
#                 {"id": "A9", "name": "Access Control"},
#                 {"id": "A10", "name": "Cryptography"},
#                 {"id": "A11", "name": "Physical and Environmental Security"},
#                 {"id": "A12", "name": "Operations Security"},
#                 {"id": "A13", "name": "Communications Security"},
#                 {"id": "A14", "name": "System Acquisition, Development and Maintenance"},
#                 {"id": "A15", "name": "Supplier Relationships"},
#                 {"id": "A16", "name": "Information Security Incident Management"},
#                 {"id": "A17", "name": "Information Security Aspects of BCM"},
#                 {"id": "A18", "name": "Compliance"}
#             ],
#             "controls": self._load_iso27001_controls()
#         }
        
#         # NIST Cybersecurity Framework
#         self.frameworks["nist_csf"] = {
#             "name": "NIST Cybersecurity Framework",
#             "description": "Framework for improving critical infrastructure cybersecurity",
#             "version": "1.1",
#             "categories": [
#                 {"id": "ID", "name": "Identify"},
#                 {"id": "PR", "name": "Protect"},
#                 {"id": "DE", "name": "Detect"},
#                 {"id": "RS", "name": "Respond"},
#                 {"id": "RC", "name": "Recover"}
#             ],
#             "controls": self._load_nist_csf_controls()
#         }
        
#         # GDPR Framework
#         self.frameworks["gdpr"] = {
#             "name": "General Data Protection Regulation",
#             "description": "EU regulation on data protection and privacy",
#             "version": "2016/679",
#             "categories": [
#                 {"id": "C1", "name": "Lawfulness, Fairness and Transparency"},
#                 {"id": "C2", "name": "Purpose Limitation"},
#                 {"id": "C3", "name": "Data Minimization"},
#                 {"id": "C4", "name": "Accuracy"},
#                 {"id": "C5", "name": "Storage Limitation"},
#                 {"id": "C6", "name": "Integrity and Confidentiality"},
#                 {"id": "C7", "name": "Accountability"},
#                 {"id": "C8", "name": "Data Subject Rights"}
#             ],
#             "controls": self._load_gdpr_controls()
#         }
        
#         # HIPAA Framework
#         self.frameworks["hipaa"] = {
#             "name": "Health Insurance Portability and Accountability Act",
#             "description": "US legislation for data privacy and security provisions for medical information",
#             "version": "1996",
#             "categories": [
#                 {"id": "P", "name": "Privacy Rule"},
#                 {"id": "S", "name": "Security Rule"},
#                 {"id": "B", "name": "Breach Notification Rule"}
#             ],
#             "controls": self._load_hipaa_controls()
#         }
        
#         # PCI DSS Framework
#         self.frameworks["pci_dss"] = {
#             "name": "Payment Card Industry Data Security Standard",
#             "description": "Information security standard for organizations that handle credit card data",
#             "version": "4.0",
#             "categories": [
#                 {"id": "R1", "name": "Build and Maintain a Secure Network and Systems"},
#                 {"id": "R2", "name": "Protect Account Data"},
#                 {"id": "R3", "name": "Maintain a Vulnerability Management Program"},
#                 {"id": "R4", "name": "Implement Strong Access Control Measures"},
#                 {"id": "R5", "name": "Regularly Monitor and Test Networks"},
#                 {"id": "R6", "name": "Maintain an Information Security Policy"}
#             ],
#             "controls": self._load_pci_dss_controls()
#         }
        
#         # Map controls across frameworks
#         self._generate_control_mappings()
        
#         # Load common risk patterns
#         self._load_risk_patterns()
    
#     def _load_frameworks_from_path(self, data_path: str):
#         """
#         Load frameworks from JSON files in the given path
        
#         Args:
#             data_path: Path to directory containing framework JSON files
#         """
#         if not os.path.exists(data_path):
#             raise FileNotFoundError(f"Data path {data_path} does not exist")
        
#         # Load each JSON file in the directory
#         for filename in os.listdir(data_path):
#             if filename.endswith('.json'):
#                 file_path = os.path.join(data_path, filename)
#                 try:
#                     with open(file_path, 'r') as f:
#                         framework_data = json.load(f)
                    
#                     if 'id' in framework_data and 'name' in framework_data:
#                         self.frameworks[framework_data['id']] = framework_data
#                 except Exception as e:
#                     print(f"Error loading framework from {file_path}: {e}")
        
#         # Generate control mappings
#         self._generate_control_mappings()
    
#     def _load_iso27001_controls(self):
#         """Load ISO 27001 controls"""
#         # Sample of key controls - in a real implementation, this would include all controls
#         return [
#             {
#                 "id": "A.5.1.1",
#                 "name": "Information Security Policy",
#                 "description": "A set of policies for information security shall be defined, approved by management, published and communicated to employees and relevant external parties.",
#                 "category": "A5",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "A.6.1.1",
#                 "name": "Information Security Roles and Responsibilities",
#                 "description": "All information security responsibilities shall be defined and allocated.",
#                 "category": "A6",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "A.9.2.3",
#                 "name": "Management of Privileged Access Rights",
#                 "description": "The allocation and use of privileged access rights shall be restricted and controlled.",
#                 "category": "A9",
#                 "risk_level": "critical"
#             },
#             {
#                 "id": "A.9.4.2",
#                 "name": "Secure Log-on Procedures",
#                 "description": "Where required by the access control policy, access to systems and applications shall be controlled by a secure log-on procedure.",
#                 "category": "A9",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "A.10.1.1",
#                 "name": "Policy on the Use of Cryptographic Controls",
#                 "description": "A policy on the use of cryptographic controls for protection of information shall be developed and implemented.",
#                 "category": "A10",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "A.12.6.1",
#                 "name": "Management of Technical Vulnerabilities",
#                 "description": "Information about technical vulnerabilities of information systems being used shall be obtained in a timely fashion, the organization's exposure to such vulnerabilities evaluated and appropriate measures taken to address the associated risk.",
#                 "category": "A12",
#                 "risk_level": "critical"
#             },
#             {
#                 "id": "A.15.1.1",
#                 "name": "Information Security Policy for Supplier Relationships",
#                 "description": "Information security requirements for mitigating the risks associated with supplier's access to the organization's assets shall be agreed with the supplier and documented.",
#                 "category": "A15",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "A.16.1.1",
#                 "name": "Responsibilities and Procedures",
#                 "description": "Management responsibilities and procedures shall be established to ensure a quick, effective and orderly response to information security incidents.",
#                 "category": "A16",
#                 "risk_level": "high"
#             }
#         ]
    
#     def _load_nist_csf_controls(self):
#         """Load NIST CSF controls"""
#         # Sample of key controls
#         return [
#             {
#                 "id": "ID.AM-1",
#                 "name": "Physical devices and systems inventoried",
#                 "description": "Physical devices and systems within the organization are inventoried",
#                 "category": "ID",
#                 "subcategory": "Asset Management",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "ID.GV-1",
#                 "name": "Organizational security policy established",
#                 "description": "Organizational information security policy is established and communicated",
#                 "category": "ID",
#                 "subcategory": "Governance",
#                 "risk_level": "medium"
#             },
#             {
#                 "id": "ID.RA-1",
#                 "name": "Asset vulnerabilities identified",
#                 "description": "Asset vulnerabilities are identified and documented",
#                 "category": "ID",
#                 "subcategory": "Risk Assessment",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "PR.AC-1",
#                 "name": "Identities and credentials managed",
#                 "description": "Identities and credentials are issued, managed, verified, revoked, and audited for authorized devices, users and processes",
#                 "category": "PR",
#                 "subcategory": "Access Control",
#                 "risk_level": "critical"
#             },
#             {
#                 "id": "PR.AC-4",
#                 "name": "Access permissions managed",
#                 "description": "Access permissions and authorizations are managed, incorporating the principles of least privilege and separation of duties",
#                 "category": "PR",
#                 "subcategory": "Access Control",
#                 "risk_level": "critical"
#             },
#             {
#                 "id": "PR.DS-1",
#                 "name": "Data-at-rest protected",
#                 "description": "Data-at-rest is protected",
#                 "category": "PR",
#                 "subcategory": "Data Security",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "PR.DS-2",
#                 "name": "Data-in-transit protected",
#                 "description": "Data-in-transit is protected",
#                 "category": "PR",
#                 "subcategory": "Data Security",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "DE.CM-8",
#                 "name": "Vulnerability scans performed",
#                 "description": "Vulnerability scans are performed",
#                 "category": "DE",
#                 "subcategory": "Continuous Monitoring",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "RS.CO-2",
#                 "name": "Incidents reported",
#                 "description": "Incidents are reported consistent with established criteria",
#                 "category": "RS",
#                 "subcategory": "Communications",
#                 "risk_level": "medium"
#             },
#             {
#                 "id": "RS.MI-2",
#                 "name": "Incidents mitigated",
#                 "description": "Incidents are mitigated",
#                 "category": "RS",
#                 "subcategory": "Mitigation",
#                 "risk_level": "high"
#             }
#         ]
    
#     def _load_gdpr_controls(self):
#         """Load GDPR controls"""
#         return [
#             {
#                 "id": "GDPR.C1.1",
#                 "name": "Lawful basis for processing",
#                 "description": "Personal data shall be processed lawfully, requiring a valid lawful basis for each processing activity",
#                 "category": "C1",
#                 "article": "Art. 6",
#                 "risk_level": "critical"
#             },
#             {
#                 "id": "GDPR.C1.2",
#                 "name": "Transparency of processing",
#                 "description": "Information about processing activities must be provided to data subjects in a concise, transparent, intelligible and easily accessible form",
#                 "category": "C1",
#                 "article": "Art. 12",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "GDPR.C3.1",
#                 "name": "Data minimization principle",
#                 "description": "Personal data shall be adequate, relevant and limited to what is necessary in relation to the purposes for which they are processed",
#                 "category": "C3",
#                 "article": "Art. 5(1)(c)",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "GDPR.C6.1",
#                 "name": "Security of processing",
#                 "description": "Implement appropriate technical and organizational measures to ensure a level of security appropriate to the risk",
#                 "category": "C6",
#                 "article": "Art. 32",
#                 "risk_level": "critical"
#             },
#             {
#                 "id": "GDPR.C7.1",
#                 "name": "Records of processing activities",
#                 "description": "Each controller shall maintain a record of processing activities under its responsibility",
#                 "category": "C7",
#                 "article": "Art. 30",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "GDPR.C7.2",
#                 "name": "Data Protection Impact Assessment",
#                 "description": "Where processing is likely to result in high risk to rights and freedoms, the controller shall carry out an assessment of the impact",
#                 "category": "C7",
#                 "article": "Art. 35",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "GDPR.C8.1",
#                 "name": "Right of access",
#                 "description": "The data subject shall have the right to obtain confirmation as to whether personal data concerning them are being processed",
#                 "category": "C8",
#                 "article": "Art. 15",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "GDPR.C8.4",
#                 "name": "Right to erasure",
#                 "description": "The data subject shall have the right to obtain the erasure of personal data concerning them without undue delay",
#                 "category": "C8",
#                 "article": "Art. 17",
#                 "risk_level": "high"
#             }
#         ]
    
#     def _load_hipaa_controls(self):
#         """Load HIPAA controls"""
#         return [
#             {
#                 "id": "HIPAA.S.1",
#                 "name": "Security Management Process",
#                 "description": "Implement policies and procedures to prevent, detect, contain, and correct security violations",
#                 "category": "S",
#                 "section": "164.308(a)(1)",
#                 "risk_level": "critical"
#             },
#             {
#                 "id": "HIPAA.S.2",
#                 "name": "Risk Analysis",
#                 "description": "Conduct an accurate and thorough assessment of the potential risks and vulnerabilities to the confidentiality, integrity, and availability of ePHI",
#                 "category": "S",
#                 "section": "164.308(a)(1)(ii)(A)",
#                 "risk_level": "critical"
#             },
#             {
#                 "id": "HIPAA.S.7",
#                 "name": "Access Control",
#                 "description": "Implement technical policies and procedures for electronic information systems that maintain ePHI to allow access only to authorized persons or software programs",
#                 "category": "S",
#                 "section": "164.312(a)(1)",
#                 "risk_level": "critical"
#             },
#             {
#                 "id": "HIPAA.S.8",
#                 "name": "Audit Controls",
#                 "description": "Implement hardware, software, and/or procedural mechanisms that record and examine activity in information systems that contain or use ePHI",
#                 "category": "S",
#                 "section": "164.312(b)",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "HIPAA.S.9",
#                 "name": "Integrity",
#                 "description": "Implement policies and procedures to protect ePHI from improper alteration or destruction",
#                 "category": "S",
#                 "section": "164.312(c)(1)",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "HIPAA.S.10",
#                 "name": "Transmission Security",
#                 "description": "Implement technical security measures to guard against unauthorized access to ePHI that is being transmitted over an electronic communications network",
#                 "category": "S",
#                 "section": "164.312(e)(1)",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "HIPAA.P.1",
#                 "name": "Notice of Privacy Practices",
#                 "description": "A covered entity must provide a notice of its privacy practices",
#                 "category": "P",
#                 "section": "164.520",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "HIPAA.B.1",
#                 "name": "Breach Notification",
#                 "description": "A covered entity shall provide notification following the discovery of a breach of unsecured PHI",
#                 "category": "B",
#                 "section": "164.404",
#                 "risk_level": "critical"
#             }
#         ]
    
#     def _load_pci_dss_controls(self):
#         """Load PCI DSS controls"""
#         return [
#             {
#                 "id": "PCI.1.1",
#                 "name": "Firewall Configuration",
#                 "description": "Install and maintain a firewall configuration to protect cardholder data",
#                 "category": "R1",
#                 "requirement": "1.1",
#                 "risk_level": "critical"
#             },
#             {
#                 "id": "PCI.2.1",
#                 "name": "Default Security Parameters",
#                 "description": "Change vendor-supplied defaults for system passwords and other security parameters",
#                 "category": "R1",
#                 "requirement": "2.1",
#                 "risk_level": "critical"
#             },
#             {
#                 "id": "PCI.3.1",
#                 "name": "Protect Stored Cardholder Data",
#                 "description": "Keep cardholder data storage to a minimum by implementing data retention and disposal policies",
#                 "category": "R2",
#                 "requirement": "3.1",
#                 "risk_level": "critical"
#             },
#             {
#                 "id": "PCI.3.4",
#                 "name": "Render PAN Unreadable",
#                 "description": "Render PAN unreadable anywhere it is stored",
#                 "category": "R2",
#                 "requirement": "3.4",
#                 "risk_level": "critical"
#             },
#             {
#                 "id": "PCI.4.1",
#                 "name": "Encrypt Transmission",
#                 "description": "Use strong cryptography and security protocols to safeguard sensitive cardholder data during transmission over open, public networks",
#                 "category": "R2",
#                 "requirement": "4.1",
#                 "risk_level": "critical"
#             },
#             {
#                 "id": "PCI.6.1",
#                 "name": "Security Vulnerabilities",
#                 "description": "Establish a process to identify security vulnerabilities, using reputable outside sources for security vulnerability information",
#                 "category": "R3",
#                 "requirement": "6.1",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "PCI.8.2",
#                 "name": "User Identification and Authentication",
#                 "description": "Employ at least one of these authentication methods: something you know, something you have, something you are",
#                 "category": "R4",
#                 "requirement": "8.2",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "PCI.9.1",
#                 "name": "Physical Access Controls",
#                 "description": "Use appropriate facility entry controls to limit and monitor physical access to systems that store, process, or transmit cardholder data",
#                 "category": "R4",
#                 "requirement": "9.1",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "PCI.10.2",
#                 "name": "Audit Logs",
#                 "description": "Implement automated audit trails for all system components",
#                 "category": "R5",
#                 "requirement": "10.2",
#                 "risk_level": "high"
#             },
#             {
#                 "id": "PCI.12.1",
#                 "name": "Security Policy",
#                 "description": "Establish, publish, maintain, and disseminate a security policy",
#                 "category": "R6",
#                 "requirement": "12.1",
#                 "risk_level": "high"
#             }
#         ]
    
#     def _generate_control_mappings(self):
#         """Generate mappings between controls across different frameworks"""
#         # This would normally be a comprehensive mapping of equivalent controls
#         # Here's a simplified example mapping some key controls
#         self.control_mappings = {
#             # Access Control Mappings
#             "ISO27001_ACCESS": ["A.9.2.3", "A.9.4.2"],
#             "NIST_ACCESS": ["PR.AC-1", "PR.AC-4"],
#             "PCI_ACCESS": ["PCI.8.2"],
#             "HIPAA_ACCESS": ["HIPAA.S.7"],
            
#             # Data Protection Mappings
#             "ISO27001_DATA": ["A.10.1.1"],
#             "NIST_DATA": ["PR.DS-1", "PR.DS-2"],
#             "GDPR_DATA": ["GDPR.C3.1", "GDPR.C6.1"],
#             "PCI_DATA": ["PCI.3.1", "PCI.3.4", "PCI.4.1"],
#             "HIPAA_DATA": ["HIPAA.S.9", "HIPAA.S.10"],
            
#             # Vulnerability Management Mappings
#             "ISO27001_VULN": ["A.12.6.1"],
#             "NIST_VULN": ["DE.CM-8"],
#             "PCI_VULN": ["PCI.6.1"],
            
#             # Incident Response Mappings
#             "ISO27001_IR": ["A.16.1.1"],
#             "NIST_IR": ["RS.CO-2", "RS.MI-2"],
#             "HIPAA_IR": ["HIPAA.B.1"],
            
#             # Cross-Framework Mappings (equivalents)
#             "ACCESS_CONTROLS": ["A.9.2.3", "PR.AC-1", "PCI.8.2", "HIPAA.S.7"],
#             "DATA_PROTECTION": ["A.10.1.1", "PR.DS-1", "GDPR.C6.1", "PCI.3.4", "HIPAA.S.9"],
#             "VULNERABILITY_MGMT": ["A.12.6.1", "DE.CM-8", "PCI.6.1"],
#             "INCIDENT_RESPONSE": ["A.16.1.1", "RS.MI-2", "HIPAA.B.1"]
#         }
    
#     def _load_risk_patterns(self):
#         """Load common risk patterns for assessment"""
#         self.risk_patterns = {
#             "access_control": {
#                 "name": "Access Control Weaknesses",
#                 "description": "Weaknesses in access control mechanisms that may lead to unauthorized access",
#                 "indicators": [
#                     {"field": "mfa_status", "values": ["Not implemented", "For privileged users only"], "risk_score": 30},
#                     {"field": "password_policy", "values": ["Basic (8+ characters)"], "risk_score": 25},
#                     {"field": "privileged_access", "values": ["No specific management", "Manual tracking"], "risk_score": 35},
#                     {"field": "access_reviews", "values": ["Never/ad hoc", "Annually"], "risk_score": 20}
#                 ],
#                 "frameworks": {
#                     "iso27001": ["A.12.6.1"],
#                     "nist_csf": ["DE.CM-8"],
#                     "pci_dss": ["PCI.6.1"]
#                 }
#             },
#             "incident_response": {
#                 "name": "Incident Response Weaknesses",
#                 "description": "Insufficient incident response capabilities that may lead to ineffective handling of security incidents",
#                 "indicators": [
#                     {"field": "ir_plan", "values": ["No formal plan", "Basic plan but not tested"], "risk_score": 30},
#                     {"field": "security_monitoring", "values": ["Minimal/ad hoc monitoring", "Basic logging without 24/7 monitoring"], "risk_score": 25},
#                     {"field": "breach_response", "values": ["No defined SLAs", "Within 24 hours for critical systems"], "risk_score": 20},
#                     {"field": "forensic_capabilities", "values": ["No forensic capabilities", "Basic log review capabilities"], "risk_score": 15}
#                 ],
#                 "frameworks": {
#                     "iso27001": ["A.16.1.1"],
#                     "nist_csf": ["RS.CO-2", "RS.MI-2"],
#                     "hipaa": ["HIPAA.B.1"]
#                 }
#             },
#             "vendor_management": {
#                 "name": "Vendor Management Weaknesses",
#                 "description": "Insufficient vendor risk management processes that may lead to third-party security risks",
#                 "indicators": [
#                     {"field": "vendor_assessment", "values": ["No formal assessment", "Basic security questionnaire"], "risk_score": 25},
#                     {"field": "vendor_contracts", "values": ["Minimal security language", "Basic security requirements"], "risk_score": 20},
#                     {"field": "third_party_access", "values": ["Same as employee access", "Some restrictions for third parties"], "risk_score": 30},
#                     {"field": "vendor_incidents", "values": ["No specific process", "Basic notification requirements"], "risk_score": 20}
#                 ],
#                 "frameworks": {
#                     "iso27001": ["A.15.1.1"],
#                     "nist_csf": ["ID.AM-1", "ID.GV-1"],
#                     "gdpr": ["GDPR.C7.1"],
#                     "hipaa": ["HIPAA.S.1"]
#                 }
#             },
#             "network_security": {
#                 "name": "Network Security Weaknesses",
#                 "description": "Insufficient network security controls that may lead to unauthorized access or data breaches",
#                 "indicators": [
#                     {"field": "network_segmentation", "values": ["Minimal/no segmentation", "Basic segmentation (e.g., IT vs OT)"], "risk_score": 30},
#                     {"field": "firewall_management", "values": ["Basic firewall configuration", "Regular but manual reviews"], "risk_score": 25}
#                 ],
#                 "frameworks": {
#                     "iso27001": ["A.13.1.1", "A.13.1.3"],
#                     "nist_csf": ["PR.AC-5", "PR.PT-4"],
#                     "pci_dss": ["PCI.1.1", "PCI.1.2"]
#                 }
#             }
#         }
    
#     def get_frameworks(self) -> Dict[str, Any]:
#         """Get all available compliance frameworks"""
#         return self.frameworks
    
#     def get_framework(self, framework_id: str) -> Dict[str, Any]:
#         """
#         Get a specific compliance framework by ID
        
#         Args:
#             framework_id: Framework identifier
            
#         Returns:
#             Framework data dictionary or empty dict if not found
#         """
#         return self.frameworks.get(framework_id, {})
    
#     def get_control(self, control_id: str) -> Dict[str, Any]:
#         """
#         Get a specific control by ID
        
#         Args:
#             control_id: Control identifier
            
#         Returns:
#             Control data dictionary or empty dict if not found
#         """
#         # Search for control in all frameworks
#         for framework_id, framework in self.frameworks.items():
#             for control in framework.get('controls', []):
#                 if control['id'] == control_id:
#                     return control
        
#         return {}
    
#     def get_controls_by_category(self, framework_id: str, category_id: str) -> List[Dict[str, Any]]:
#         """
#         Get controls for a specific framework category
        
#         Args:
#             framework_id: Framework identifier
#             category_id: Category identifier
            
#         Returns:
#             List of control dictionaries
#         """
#         framework = self.get_framework(framework_id)
#         if not framework:
#             return []
        
#         return [
#             control for control in framework.get('controls', [])
#             if control.get('category') == category_id
#         ]
    
#     def get_equivalent_controls(self, control_id: str) -> List[str]:
#         """
#         Get equivalent controls across different frameworks
        
#         Args:
#             control_id: Control identifier
            
#         Returns:
#             List of equivalent control IDs
#         """
#         # Look through mappings for the control
#         for mapping_group, controls in self.control_mappings.items():
#             if control_id in controls:
#                 return [c for c in controls if c != control_id]
        
#         return []
    
#     def analyze_questionnaire(self, questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Analyze questionnaire data against compliance frameworks
        
#         Args:
#             questionnaire_data: Dictionary of questionnaire responses
            
#         Returns:
#             Analysis results with risk patterns, affected controls, and framework compliance
#         """
#         results = {
#             "risk_patterns": [],
#             "affected_controls": [],
#             "framework_compliance": {}
#         }
        
#         # Check for risk patterns
#         for pattern_id, pattern in self.risk_patterns.items():
#             pattern_match = {
#                 "pattern_id": pattern_id,
#                 "name": pattern['name'],
#                 "description": pattern['description'],
#                 "matched_indicators": [],
#                 "risk_score": 0,
#                 "affected_frameworks": {}
#             }
            
#             # Check each indicator
#             for indicator in pattern['indicators']:
#                 field = indicator['field']
#                 if field in questionnaire_data and questionnaire_data[field] in indicator['values']:
#                     pattern_match['matched_indicators'].append({
#                         "field": field,
#                         "value": questionnaire_data[field],
#                         "risk_score": indicator['risk_score']
#                     })
#                     pattern_match['risk_score'] += indicator['risk_score']
            
#             # If indicators matched, add affected frameworks and controls
#             if pattern_match['matched_indicators']:
#                 for framework_id, control_ids in pattern['frameworks'].items():
#                     framework = self.get_framework(framework_id)
#                     if framework:
#                         controls = []
#                         for control_id in control_ids:
#                             control = self.get_control(control_id)
#                             if control:
#                                 controls.append(control)
#                                 # Add to global affected controls if not already there
#                                 if control not in results['affected_controls']:
#                                     results['affected_controls'].append(control)
                        
#                         if controls:
#                             pattern_match['affected_frameworks'][framework_id] = {
#                                 "name": framework['name'],
#                                 "controls": controls
#                             }
                
#                 # Normalize risk score to 0-100 scale
#                 pattern_match['risk_score'] = min(100, pattern_match['risk_score'])
#                 results['risk_patterns'].append(pattern_match)
        
#         # Calculate framework compliance scores
#         for framework_id, framework in self.frameworks.items():
#             total_controls = len(framework.get('controls', []))
#             affected_controls = [
#                 c for c in results['affected_controls'] 
#                 if c.get('id', '').startswith(framework_id.split('_')[0].upper())
#             ]
            
#             # Simple compliance calculation (affected controls reduce compliance)
#             affected_count = len(affected_controls)
#             compliance_score = 100 - (affected_count / total_controls * 100) if total_controls > 0 else 100
            
#             results['framework_compliance'][framework_id] = {
#                 "name": framework['name'],
#                 "compliance_score": max(0, min(100, compliance_score)),
#                 "affected_controls": affected_controls
#             }
        
#         return results
    
#     def generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
#         """
#         Generate recommendations based on analysis results
        
#         Args:
#             analysis_results: Results from analyze_questionnaire
            
#         Returns:
#             List of recommendation dictionaries
#         """
#         recommendations = []
        
#         # Generate recommendations for each risk pattern
#         for pattern in analysis_results.get('risk_patterns', []):
#             # Basic recommendation based on pattern
#             recommendation = {
#                 "title": f"Address {pattern['name']}",
#                 "description": f"Implement controls to address {pattern['description'].lower()}.",
#                 "category": pattern['name'].split(' ')[0],  # First word as category
#                 "impact": self._calculate_impact(pattern['risk_score']),
#                 "effort": "Medium",  # Default effort
#                 "controls": []
#             }
            
#             # Add specific controls to implement
#             for framework_id, framework_data in pattern.get('affected_frameworks', {}).items():
#                 for control in framework_data.get('controls', []):
#                     if control not in recommendation['controls']:
#                         recommendation['controls'].append(control)
            
#             # More specific recommendations based on matched indicators
#             specific_recs = self._generate_specific_recommendations(pattern)
#             if specific_recs:
#                 recommendations.extend(specific_recs)
#             else:
#                 recommendations.append(recommendation)
        
#         return recommendations
    
#     def _calculate_impact(self, risk_score: float) -> str:
#         """
#         Calculate impact level based on risk score
        
#         Args:
#             risk_score: Numeric risk score
            
#         Returns:
#             Impact level (Low, Medium, High)
#         """
#         if risk_score >= 70:
#             return "High"
#         elif risk_score >= 40:
#             return "Medium"
#         else:
#             return "Low"
    
#     def _generate_specific_recommendations(self, pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
#         """
#         Generate specific recommendations based on pattern
        
#         Args:
#             pattern: Risk pattern data
            
#         Returns:
#             List of specific recommendation dictionaries
#         """
#         recommendations = []
        
#         # Map fields to specific recommendations
#         field_recommendations = {
#             "mfa_status": {
#                 "title": "Implement Multi-Factor Authentication",
#                 "description": "Deploy MFA for all users to mitigate the risk of unauthorized access from compromised credentials.",
#                 "category": "Access Control",
#                 "effort": "Medium"
#             },
#             "password_policy": {
#                 "title": "Strengthen Password Policy",
#                 "description": "Update your password policy to require longer, more complex passwords and implement a password manager to help users maintain strong, unique passwords.",
#                 "category": "Access Control",
#                 "effort": "Low"
#             },
#             "privileged_access": {
#                 "title": "Implement Privileged Access Management",
#                 "description": "Deploy a PAM solution to manage, control, and monitor privileged accounts and access to critical systems.",
#                 "category": "Access Control",
#                 "effort": "High"
#             },
#             "access_reviews": {
#                 "title": "Establish Regular Access Reviews",
#                 "description": "Implement a formal process for regularly reviewing and validating user access rights to systems and applications.",
#                 "category": "Access Control",
#                 "effort": "Medium"
#             },
#             "data_classification": {
#                 "title": "Implement Data Classification",
#                 "description": "Establish a formal data classification framework and enforce controls based on data sensitivity levels.",
#                 "category": "Data Protection",
#                 "effort": "Medium"
#             },
#             "encryption_status": {
#                 "title": "Enhance Data Encryption",
#                 "description": "Implement comprehensive encryption for sensitive data both at rest and in transit using industry-standard algorithms.",
#                 "category": "Data Protection",
#                 "effort": "Medium"
#             },
#             "dlp_status": {
#                 "title": "Deploy Data Loss Prevention",
#                 "description": "Implement a DLP solution to monitor and protect sensitive data across endpoints, networks, and cloud services.",
#                 "category": "Data Protection",
#                 "effort": "High"
#             },
#             "vuln_scanning": {
#                 "title": "Implement Regular Vulnerability Scanning",
#                 "description": "Establish automated, regular vulnerability scanning of all systems and applications with a formal process for remediation.",
#                 "category": "Vulnerability Management",
#                 "effort": "Medium"
#             },
#             "patch_management": {
#                 "title": "Improve Patch Management",
#                 "description": "Implement an automated patch management system with defined SLAs for critical, high, medium, and low vulnerabilities.",
#                 "category": "Vulnerability Management",
#                 "effort": "High"
#             },
#             "ir_plan": {
#                 "title": "Develop Comprehensive Incident Response Plan",
#                 "description": "Create and regularly test a formal incident response plan that includes roles, responsibilities, and procedures for handling security incidents.",
#                 "category": "Incident Response",
#                 "effort": "Medium"
#             },
#             "security_monitoring": {
#                 "title": "Enhance Security Monitoring",
#                 "description": "Implement 24/7 security monitoring with a SIEM solution and automated alerting for critical security events.",
#                 "category": "Incident Response",
#                 "effort": "High"
#             },
#             "network_segmentation": {
#                 "title": "Implement Network Segmentation",
#                 "description": "Segment your network based on security requirements and data sensitivity to limit lateral movement within the network.",
#                 "category": "Network Security",
#                 "effort": "High"
#             },
#             "firewall_management": {
#                 "title": "Enhance Firewall Management",
#                 "description": "Implement automated firewall policy management, regular reviews, and continuous monitoring of rule effectiveness.",
#                 "category": "Network Security",
#                 "effort": "Medium"
#             },
#             "vendor_assessment": {
#                 "title": "Formalize Vendor Risk Assessment",
#                 "description": "Develop a comprehensive vendor risk assessment process that includes initial vetting, ongoing monitoring, and regular reassessment.",
#                 "category": "Vendor Management",
#                 "effort": "Medium"
#             },
#             "third_party_access": {
#                 "title": "Secure Third-Party Access",
#                 "description": "Implement just-in-time access with comprehensive monitoring for all third-party access to your systems and data.",
#                 "category": "Vendor Management",
#                 "effort": "Medium"
#             }
#         }
        
#         # Generate recommendations for matched indicators
#         for indicator in pattern.get('matched_indicators', []):
#             field = indicator.get('field')
#             if field in field_recommendations:
#                 rec = field_recommendations[field].copy()
#                 rec['impact'] = self._calculate_impact(indicator.get('risk_score', 0))
                
#                 # Add controls specific to this recommendation
#                 rec['controls'] = []
#                 for framework_id, framework_data in pattern.get('affected_frameworks', {}).items():
#                     for control in framework_data.get('controls', []):
#                         if control not in rec['controls']:
#                             rec['controls'].append(control)
                
#                 recommendations.append(rec)
        
#         return recommendations": {
#                     "iso27001": ["A.9.2.3", "A.9.4.2"],
#                     "nist_csf": ["PR.AC-1", "PR.AC-4"],
#                     "pci_dss": ["PCI.8.2"],
#                     "hipaa": ["HIPAA.S.7"]
#                 }
#             },
#             "data_protection": {
#                 "name": "Data Protection Weaknesses",
#                 "description": "Insufficient protection of sensitive data that may lead to data breaches",
#                 "indicators": [
#                     {"field": "data_classification", "values": ["No formal classification", "Basic classification exists but not enforced"], "risk_score": 25},
#                     {"field": "encryption_status", "values": ["Minimal/ad hoc encryption", "Encryption for some sensitive data"], "risk_score": 30},
#                     {"field": "dlp_status", "values": ["No DLP implementation", "Basic DLP for email only"], "risk_score": 20},
#                     {"field": "data_retention", "values": ["No formal policy", "Policy exists but not enforced"], "risk_score": 15}
#                 ],
#                 "frameworks": {
#                     "iso27001": ["A.10.1.1"],
#                     "nist_csf": ["PR.DS-1", "PR.DS-2"],
#                     "gdpr": ["GDPR.C3.1", "GDPR.C6.1"],
#                     "pci_dss": ["PCI.3.1", "PCI.3.4", "PCI.4.1"],
#                     "hipaa": ["HIPAA.S.9", "HIPAA.S.10"]
#                 }
#             },
#             "vulnerability_management": {
#                 "name": "Vulnerability Management Weaknesses",
#                 "description": "Insufficient processes for identifying and addressing security vulnerabilities",
#                 "indicators": [
#                     {"field": "vuln_scanning", "values": ["Ad hoc or never", "Annually"], "risk_score": 35},
#                     {"field": "patch_management", "values": ["Ad hoc patching", "Regular but manual patching"], "risk_score": 30}
#                 ],
#                 "frameworks