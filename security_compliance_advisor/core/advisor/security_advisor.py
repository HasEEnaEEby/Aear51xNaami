"""
Security Advisor Module
This module implements the core advisory logic for the security compliance system.
"""

import json
import os
from pathlib import Path
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from datetime import datetime

from core.compliance.compliance_knowledge import ComplianceKnowledge
from core.risk.risk_scoring_model import RiskScoringModel

class SecurityAdvisor:
    """
    Core security advisor component that provides compliance insights and recommendations
    """
    
    def __init__(self, knowledge_base: Optional[ComplianceKnowledge] = None, risk_model: Optional[RiskScoringModel] = None):
        """
        Initialize the security advisor
        
        Args:
            knowledge_base: Optional ComplianceKnowledge instance
            risk_model: Optional RiskScoringModel instance
        """
        self.knowledge_base = knowledge_base or ComplianceKnowledge()
        self.risk_model = risk_model or RiskScoringModel()
        self.current_assessment = None
        self.current_organization = None
    
    def identify_compliance_gaps(self, answers: Dict[str, Any], frameworks: List[str]) -> List[Dict[str, Any]]:
        """
        Identify compliance gaps based on questionnaire answers
        
        Args:
            answers: Dictionary of questionnaire answers
            frameworks: List of frameworks to check against
            
        Returns:
            List of identified compliance gaps
        """
        gaps = []
        
        # Process answers to identify gaps
        for question_id, answer in answers.items():
            # Skip metadata questions
            if question_id.startswith("meta_"):
                continue
                
            # Identify potential gaps based on negative answers
            is_gap = False
            
            if isinstance(answer, bool) and not answer:
                # Boolean "No" answers indicate gaps
                is_gap = True
            elif isinstance(answer, str) and answer.lower() in ["no", "n/a", "not implemented"]:
                # String negative answers indicate gaps
                is_gap = True
            elif isinstance(answer, (int, float)) and answer < 3:
                # Low scores (assuming 1-5 scale) indicate gaps
                is_gap = True
            elif isinstance(answer, list) and len(answer) == 0:
                # Empty selection indicates gaps
                is_gap = True
                
            # If potential gap identified, find relevant policies
            if is_gap:
                relevant_policies = self.knowledge_base.get_relevant_policies(question_id, frameworks)
                
                # Create gap entries for relevant policies
                for policy in relevant_policies:
                    # Determine gap priority
                    priority = "High"
                    if "priority" in policy:
                        priority = policy["priority"]
                    elif "impact" in policy:
                        priority = policy["impact"]
                    
                    # Create gap entry
                    gap = {
                        "question_id": question_id,
                        "framework": policy.get("framework", "Unknown"),
                        "control_id": policy.get("control_id", "Unknown"),
                        "title": policy.get("title", "Compliance Gap"),
                        "description": policy.get("description", "A compliance gap was identified."),
                        "priority": priority,
                        "recommendation": self._generate_recommendation_for_policy(policy)
                    }
                    
                    gaps.append(gap)
        
        # Sort gaps by priority
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        gaps.sort(key=lambda x: priority_order.get(x["priority"], 4))
        
        return gaps
    
    def _generate_recommendation_for_policy(self, policy: Dict[str, Any]) -> str:
        """
        Generate a recommendation for addressing a policy gap
        
        Args:
            policy: Policy dictionary
            
        Returns:
            Recommendation text
        """
        # Use implementation guidance if available
        if "implementation" in policy and policy["implementation"]:
            return policy["implementation"]
            
        # Use requirements as guidance
        if "requirements" in policy and policy["requirements"]:
            if isinstance(policy["requirements"], list) and len(policy["requirements"]) > 0:
                return "Implement the following requirements: " + "; ".join(policy["requirements"])
            elif isinstance(policy["requirements"], str):
                return f"Implement the following: {policy['requirements']}"
                
        # Generate generic recommendation based on title
        title = policy.get("title", "")
        if title:
            return f"Implement controls to ensure {title.lower()}."
            
        # Fallback
        return "Review your implementation of this control and address any gaps identified."
    
    def generate_recommendations(self, answers: Dict[str, Any], frameworks: List[str], risk_score: float) -> List[Dict[str, Any]]:
        """
        Generate security recommendations based on assessment
        
        Args:
            answers: Dictionary of questionnaire answers
            frameworks: List of frameworks to check against
            risk_score: Overall risk score
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Determine risk level
        risk_level = "medium"
        if risk_score < 30:
            risk_level = "low"
        elif risk_score > 70:
            risk_level = "high"
        
        # Get compliance gaps
        gaps = self.identify_compliance_gaps(answers, frameworks)
        
        # Create recommendations from gaps
        for gap in gaps:
            # Get framework and control
            framework = gap["framework"]
            control_id = gap["control_id"]
            
            # Create recommendation
            recommendation = {
                "title": f"Address {framework} {control_id}: {gap['title']}",
                "description": gap["recommendation"],
                "source": "compliance_gap",
                "framework": framework,
                "control_id": control_id,
                "priority": gap["priority"],
                "impact": "High" if gap["priority"] in ["Critical", "High"] else "Medium",
                "effort": "Medium",
                "timeframe": "30 days" if gap["priority"] in ["Critical", "High"] else "90 days"
            }
            
            recommendations.append(recommendation)
        
        # Add general recommendations based on risk score
        if risk_score > 50:
            # High risk recommendations
            general_recs = [
                {
                    "title": "Conduct Security Risk Assessment",
                    "description": "Perform a comprehensive security risk assessment to identify and prioritize security vulnerabilities.",
                    "source": "best_practice",
                    "impact": "High",
                    "effort": "High",
                    "timeframe": "60 days"
                },
                {
                    "title": "Develop Security Roadmap",
                    "description": "Create a security improvement roadmap with clear milestones and responsibilities.",
                    "source": "best_practice",
                    "impact": "High",
                    "effort": "Medium",
                    "timeframe": "30 days"
                },
                {
                    "title": "Security Awareness Training",
                    "description": "Implement a comprehensive security awareness program for all employees.",
                    "source": "best_practice",
                    "impact": "High",
                    "effort": "Medium",
                    "timeframe": "45 days"
                }
            ]
            recommendations.extend(general_recs)
        
        # Add framework-specific recommendations
        for framework in frameworks:
            framework_recs = self._get_framework_recommendations(framework, risk_level)
            recommendations.extend(framework_recs)
        
        # Deduplicate recommendations
        unique_recs = {}
        for rec in recommendations:
            key = rec["title"]
            if key not in unique_recs or unique_recs[key]["impact"] == "Medium":
                unique_recs[key] = rec
        
        # Sort recommendations by priority and impact
        result = list(unique_recs.values())
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        impact_order = {"High": 0, "Medium": 1, "Low": 2}
        
        result.sort(key=lambda x: (
            priority_order.get(x.get("priority", "Medium"), 4),
            impact_order.get(x.get("impact", "Medium"), 3)
        ))
        
        return result
    
    def _get_framework_recommendations(self, framework: str, risk_level: str) -> List[Dict[str, Any]]:
        """
        Get recommendations specific to a framework
        
        Args:
            framework: Framework identifier
            risk_level: Risk level (high, medium, low)
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Framework-specific recommendations
        if framework == "NIST80053":
            if risk_level == "high":
                recommendations.append({
                    "title": "Implement NIST 800-53 Critical Controls",
                    "description": "Prioritize implementation of NIST 800-53 critical controls including AC-2, AC-3, AC-6, AU-2, CM-6, IA-2, RA-5, SC-7, and SI-4.",
                    "source": "framework",
                    "framework": "NIST80053",
                    "impact": "High",
                    "effort": "High",
                    "timeframe": "90 days"
                })
            elif risk_level == "medium":
                recommendations.append({
                    "title": "Review NIST 800-53 Implementation",
                    "description": "Review your implementation of NIST 800-53 controls and address any gaps in moderate-impact controls.",
                    "source": "framework",
                    "framework": "NIST80053",
                    "impact": "Medium",
                    "effort": "Medium",
                    "timeframe": "120 days"
                })
        
        elif framework == "ISO27001":
            if risk_level == "high":
                recommendations.append({
                    "title": "ISO 27001 Risk Treatment",
                    "description": "Develop and implement a risk treatment plan in accordance with ISO 27001 requirements.",
                    "source": "framework",
                    "framework": "ISO27001",
                    "impact": "High",
                    "effort": "High",
                    "timeframe": "90 days"
                })
            elif risk_level == "medium":
                recommendations.append({
                    "title": "ISO 27001 Internal Audit",
                    "description": "Conduct an internal audit of your information security management system against ISO 27001 requirements.",
                    "source": "framework",
                    "framework": "ISO27001",
                    "impact": "Medium",
                    "effort": "Medium",
                    "timeframe": "60 days"
                })
        
        elif framework == "HIPAA":
            if risk_level in ["high", "medium"]:
                recommendations.append({
                    "title": "HIPAA Security Risk Analysis",
                    "description": "Conduct a comprehensive security risk analysis in accordance with HIPAA Security Rule requirements.",
                    "source": "framework",
                    "framework": "HIPAA",
                    "impact": "High",
                    "effort": "High",
                    "timeframe": "60 days"
                })
        
        elif framework == "GDPR":
            if risk_level in ["high", "medium"]:
                recommendations.append({
                    "title": "GDPR Data Mapping",
                    "description": "Create a comprehensive data map to identify all personal data processing activities within your organization.",
                    "source": "framework",
                    "framework": "GDPR",
                    "impact": "High",
                    "effort": "High",
                    "timeframe": "60 days"
                })
        
        elif framework == "PCIDSS":
            if risk_level == "high":
                recommendations.append({
                    "title": "PCI DSS Compliance Assessment",
                    "description": "Conduct a formal PCI DSS compliance assessment to identify and address all gaps.",
                    "source": "framework",
                    "framework": "PCIDSS",
                    "impact": "High",
                    "effort": "High",
                    "timeframe": "60 days"
                })
        
        return recommendations
    
    def get_framework_requirements(self, framework: str, organization_size: str, industry: str) -> Dict[str, Any]:
        """
        Get key requirements for a framework based on organization context
        
        Args:
            framework: Framework identifier
            organization_size: Organization size category
            industry: Industry type
            
        Returns:
            Requirements information dictionary
        """
        # Get framework information
        framework_info = self.knowledge_base.get_framework_info(framework)
        
        if "error" in framework_info:
            return framework_info
        
        # Get priority controls based on organization context
        priority_controls = self._get_priority_controls(framework, organization_size, industry)
        
        # Get detailed control information
        control_details = []
        for control_id in priority_controls:
            control = self.knowledge_base.get_control(framework, control_id)
            if "error" not in control:
                control_details.append(control)
        
        # Build result dictionary
        result = {
            "framework": framework_info,
            "priority_controls": control_details,
            "implementation_steps": self._get_implementation_steps(framework, organization_size),
            "industry_specific": self._get_industry_guidance(framework, industry)
        }
        
        return result
    
    def _get_priority_controls(self, framework: str, organization_size: str, industry: str) -> List[str]:
        """
        Get priority controls for a framework based on organization context
        
        Args:
            framework: Framework identifier
            organization_size: Organization size category
            industry: Industry type
            
        Returns:
            List of priority control IDs
        """
        # Get all controls for framework
        controls = self.knowledge_base.get_framework_controls(framework)
        
        # Filter to high-priority controls
        priority_controls = []
        
        for control in controls:
            # Check for explicit priority indicator
            is_priority = False
            
            if "priority" in control and control["priority"] in ["High", "Critical"]:
                is_priority = True
            
            # Check for baseline requirements
            if "baseline" in control:
                if organization_size == "Small (1-50 employees)" and "LOW" in control["baseline"]:
                    is_priority = True
                elif organization_size == "Medium (51-500 employees)" and "MODERATE" in control["baseline"]:
                    is_priority = True
                elif organization_size in ["Large (501-5000 employees)", "Enterprise (5000+ employees)"] and "HIGH" in control["baseline"]:
                    is_priority = True
            
            # Check for industry applicability
            if "industries" in control and industry in control["industries"]:
                is_priority = True
            
            # Add to priority list if meets criteria
            if is_priority and "control_id" in control:
                priority_controls.append(control["control_id"])
        
        # If no controls meet criteria, select top controls by default
        if not priority_controls and framework == "NIST80053":
            priority_controls = ["AC-2", "AC-3", "AC-6", "AU-2", "CM-6", "IA-2", "RA-5", "SC-7", "SI-4"]
        elif not priority_controls and framework == "ISO27001":
            priority_controls = ["A.5.1.1", "A.6.1.1", "A.8.1.1", "A.9.2.1", "A.12.2.1"]
        elif not priority_controls and framework == "PCIDSS":
            priority_controls = ["1.1", "2.1", "3.1", "4.1", "5.1", "6.1"]
        elif not priority_controls:
            # Get first 5 controls as default
            priority_controls = [control["control_id"] for control in controls[:5] if "control_id" in control]
        
        return priority_controls
    
    def _get_implementation_steps(self, framework: str, organization_size: str) -> List[Dict[str, str]]:
        """
        Get implementation steps for a framework
        
        Args:
            framework: Framework identifier
            organization_size: Organization size category
            
        Returns:
            List of implementation step dictionaries
        """
        # Framework-specific implementation steps
        if framework == "NIST80053":
            return [
                {
                    "step": "1. Determine Security Categorization",
                    "description": "Categorize your information system based on potential impact of security breaches."
                },
                {
                    "step": "2. Select Security Controls",
                    "description": "Select baseline security controls based on categorization and tailor as needed."
                },
                {
                    "step": "3. Implement Security Controls",
                    "description": "Implement selected security controls within your information systems."
                },
                {
                    "step": "4. Assess Security Controls",
                    "description": "Assess whether controls are implemented correctly and operating as intended."
                },
                {
                    "step": "5. Authorize Information System",
                    "description": "Obtain authorization to operate based on risk assessment."
                },
                {
                    "step": "6. Monitor Security Controls",
                    "description": "Continuously monitor control effectiveness and address changes."
                }
            ]
        elif framework == "ISO27001":
            return [
                {
                    "step": "1. Define ISMS Scope",
                    "description": "Define the boundaries of your Information Security Management System."
                },
                {
                    "step": "2. Develop Security Policy",
                    "description": "Create a comprehensive information security policy aligned with business objectives."
                },
                {
                    "step": "3. Conduct Risk Assessment",
                    "description": "Identify, analyze and evaluate information security risks."
                },
                {
                    "step": "4. Implement Risk Treatment",
                    "description": "Select and implement controls to address identified risks."
                },
                {
                    "step": "5. Measure and Review",
                    "description": "Establish metrics, conduct internal audits, and review effectiveness."
                },
                {
                    "step": "6. Continual Improvement",
                    "description": "Implement improvements based on monitoring and review."
                }
            ]
        elif framework == "GDPR":
            return [
                {
                    "step": "1. Data Mapping",
                    "description": "Identify and document all personal data processing activities."
                },
                {
                    "step": "2. Risk Assessment",
                    "description": "Evaluate risks to data subjects' rights and freedoms."
                },
                {
                    "step": "3. Implement Controls",
                    "description": "Implement technical and organizational measures to ensure compliance."
                },
                {
                    "step": "4. Document Compliance",
                    "description": "Maintain records of processing activities and compliance measures."
                },
                {
                    "step": "5. Review and Update",
                    "description": "Regularly review and update your compliance program."
                }
            ]
        elif framework == "HIPAA":
            return [
                {
                    "step": "1. Security Risk Analysis",
                    "description": "Conduct a comprehensive assessment of potential risks and vulnerabilities."
                },
                {
                    "step": "2. Implement Safeguards",
                    "description": "Implement administrative, physical, and technical safeguards."
                },
                {
                    "step": "3. Develop Policies and Procedures",
                    "description": "Create and document security policies and procedures."
                },
                {
                    "step": "4. Train Workforce",
                    "description": "Provide security awareness training to all staff members."
                },
                {
                    "step": "5. Evaluate Compliance",
                    "description": "Regularly evaluate compliance with Security Rule requirements."
                }
            ]
        else:
            # Generic implementation steps
            return [
                {
                    "step": "1. Understand Requirements",
                    "description": "Review and understand the framework requirements."
                },
                {
                    "step": "2. Assess Current State",
                    "description": "Assess your current security posture against requirements."
                },
                {
                    "step": "3. Develop Implementation Plan",
                    "description": "Create a phased implementation plan for compliance."
                },
                {
                    "step": "4. Implement Controls",
                    "description": "Implement required security controls and measures."
                },
                {
                    "step": "5. Evaluate and Maintain",
                    "description": "Regularly evaluate and maintain your compliance program."
                }
            ]
    
    def _get_industry_guidance(self, framework: str, industry: str) -> Dict[str, str]:
        """
        Get industry-specific guidance for a framework
        
        Args:
            framework: Framework identifier
            industry: Industry type
            
        Returns:
            Industry guidance dictionary
        """
        # Map of framework and industry to specific guidance
        industry_guidance = {
            "HIPAA": {
                "Healthcare": "Focus on patient data protection, access controls, and regular security risk analyses. Implement robust procedures for handling PHI and ensure all business associates are compliant.",
                "Technology": "Ensure robust API security for healthcare integrations and implement strong data segregation for multi-tenant environments.",
                "Finance": "Implement strict controls for financial transactions involving healthcare payments and ensure secure handling of explanation of benefits data."
            },
            "GDPR": {
                "Healthcare": "Focus on patient consent mechanisms, data minimization, and ensuring lawful basis for all processing of health data.",
                "Finance": "Implement strong controls for profiling activities and automated decision-making. Ensure transparency in how customer financial data is used.",
                "Retail": "Focus on marketing consent management, e-commerce data protection, and customer profiling controls.",
                "Technology": "Implement privacy by design principles in product development and ensure robust data protection impact assessments."
            },
            "PCIDSS": {
                "Retail": "Implement point-of-sale security, strong network segmentation, and robust card data protection measures.",
                "Finance": "Focus on secure payment applications, strong authentication for payment systems, and comprehensive logging of all payment activities.",
                "Technology": "Implement secure coding practices for payment applications and ensure robust testing of payment processing components."
            }
        }
        
        # Check if we have specific guidance
        if framework in industry_guidance and industry in industry_guidance[framework]:
            return {
                "guidance": industry_guidance[framework][industry],
                "industry": industry,
                "framework": framework
            }
        
        # Generic guidance based on industry
        generic_industry_guidance = {
            "Healthcare": "Focus on patient data protection, strict access controls, and regular security assessments. Consider specific regulations like HIPAA in your implementation.",
            "Finance": "Implement strong controls for financial transactions, customer data protection, and regulatory reporting. Consider specific regulations like SOX and GLBA.",
            "Technology": "Focus on secure development practices, data protection by design, and strong API security. Consider privacy regulations and international data transfer requirements.",
            "Retail": "Implement robust point-of-sale security, secure e-commerce platforms, and customer data protection measures. Focus on PCI DSS compliance for payment data.",
            "Manufacturing": "Focus on operational technology security, intellectual property protection, and supply chain risk management.",
            "Government": "Implement stringent controls for sensitive data, focus on compliance with government-specific regulations, and ensure robust access management.",
            "Education": "Focus on student data protection, network security for diverse campus environments, and compliance with education-specific regulations."
        }
        
        if industry in generic_industry_guidance:
            return {
                "guidance": generic_industry_guidance[industry],
                "industry": industry,
                "framework": framework
            }
        
        # Default guidance
        return {
            "guidance": "Implement a risk-based approach to compliance focusing on the most critical security controls for your specific business operations.",
            "industry": industry,
            "framework": framework
        }
    
    def analyze_questionnaire_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze questionnaire responses for insights
        
        Args:
            responses: Dictionary of questionnaire responses
            
        Returns:
            Analysis results dictionary
        """
        # Store responses as current assessment
        self.current_assessment = responses
        
        # Get metadata
        metadata = {k: v for k, v in responses.items() if k.startswith("meta_")}
        
        # Extract critical information
        frameworks = []
        if "meta_frameworks" in metadata:
            if isinstance(metadata["meta_frameworks"], list):
                frameworks = metadata["meta_frameworks"]
            elif isinstance(metadata["meta_frameworks"], str):
                frameworks = metadata["meta_frameworks"].split(",")
        
        organization_size = metadata.get("meta_org_size", "Medium (51-500 employees)")
        industry = metadata.get("meta_industry", "Technology")
        
        # Calculate risk score
        risk_score = 50.0  # Default medium risk
        
        if self.risk_model:
            try:
                risk_score = self.risk_model.calculate_risk_score(responses, frameworks)
            except Exception as e:
                risk_score = self._calculate_simple_risk_score(responses)
        else:
            risk_score = self._calculate_simple_risk_score(responses)
        
        # Identify gaps
        compliance_gaps = self.identify_compliance_gaps(responses, frameworks)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(responses, frameworks, risk_score)
        
        # Calculate category scores
        category_scores = self._calculate_category_scores(responses)
        
        # Create result
        result = {
            "timestamp": datetime.now().isoformat(),
            "risk_score": risk_score,
            "risk_level": self._get_risk_level(risk_score),
            "compliance_gaps": compliance_gaps,
            "recommendations": recommendations,
            "category_scores": category_scores,
            "metadata": metadata,
            "frameworks": frameworks
        }
        
        return result
    
    def _calculate_simple_risk_score(self, responses: Dict[str, Any]) -> float:
        """
        Calculate a simple risk score based on questionnaire responses
        
        Args:
            responses: Dictionary of questionnaire responses
            
        Returns:
            Risk score (0-100)
        """
        # Skip metadata
        actual_responses = {k: v for k, v in responses.items() if not k.startswith("meta_")}
        
        if not actual_responses:
            return 50.0  # Default medium risk
        
        # Count negative responses
        negative_count = 0
        total_count = len(actual_responses)
        
        for key, value in actual_responses.items():
            if isinstance(value, bool) and not value:
                negative_count += 1
            elif isinstance(value, str) and value.lower() in ["no", "n/a", "not implemented"]:
                negative_count += 1
            elif isinstance(value, (int, float)) and value < 3:  # Assuming 1-5 scale
                negative_count += 1
            elif isinstance(value, list) and len(value) == 0:
                negative_count += 1
        
        # Calculate risk score (more negative responses = higher risk)
        risk_percentage = (negative_count / total_count) * 100 if total_count > 0 else 50
        
        # Apply weighting to avoid extreme scores
        weighted_score = (risk_percentage * 0.8) + 10  # Range 10-90
        
        return weighted_score
    
    def _get_risk_level(self, risk_score: float) -> Dict[str, str]:
        """
        Get risk level information based on risk score
        
        Args:
            risk_score: Risk score (0-100)
            
        Returns:
            Risk level dictionary
        """
        if risk_score < 20:
            return {
                "name": "Very Low",
                "description": "Your security posture is excellent with minimal areas for improvement.",
                "color": "green"
            }
        elif risk_score < 40:
            return {
                "name": "Low",
                "description": "Your security posture is good with a few minor areas for improvement.",
                "color": "blue"
            }
        elif risk_score < 60:
            return {
                "name": "Moderate",
                "description": "Your security posture needs attention in several key areas.",
                "color": "yellow"
            }
        elif risk_score < 80:
            return {
                "name": "High",
                "description": "Your security posture has significant vulnerabilities that need immediate attention.",
                "color": "orange"
            }
        else:
            return {
                "name": "Critical",
                "description": "Your security posture has critical vulnerabilities requiring urgent remediation.",
                "color": "red"
            }
    
    def _calculate_category_scores(self, responses: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Calculate scores for different security categories
        
        Args:
            responses: Dictionary of questionnaire responses
            
        Returns:
            Dictionary of category scores
        """
        # Define categories and related question prefixes
        categories = {
            "Access Control": ["access_", "auth_", "password_"],
            "Data Protection": ["encrypt_", "data_", "privacy_"],
            "Network Security": ["network_", "firewall_", "segmentation_"],
            "Vulnerability Management": ["patch_", "vuln_", "scan_"],
            "Incident Response": ["incident_", "response_", "breach_"],
            "Security Governance": ["policy_", "procedure_", "governance_"],
            "Security Awareness": ["training_", "awareness_", "phishing_"]
        }
        
        # Calculate scores for each category
        category_scores = {}
        
        for category, prefixes in categories.items():
            # Find questions related to this category
            category_questions = {}
            
            for key, value in responses.items():
                # Skip metadata
                if key.startswith("meta_"):
                    continue
                    
                # Check if question belongs to category
                if any(key.startswith(prefix) for prefix in prefixes):
                    category_questions[key] = value
            
            # Calculate category score if we have questions
            if category_questions:
                # Count negative responses
                negative_count = 0
                total_count = len(category_questions)
                
                for key, value in category_questions.items():
                    if isinstance(value, bool) and not value:
                        negative_count += 1
                    elif isinstance(value, str) and value.lower() in ["no", "n/a", "not implemented"]:
                        negative_count += 1
                    elif isinstance(value, (int, float)) and value < 3:  # Assuming 1-5 scale
                        negative_count += 1
                    elif isinstance(value, list) and len(value) == 0:
                        negative_count += 1
                
                # Calculate category score
                if total_count > 0:
                    # Higher percentage of negative responses = higher risk
                    risk_percentage = (negative_count / total_count) * 100
                    
                    # Maturity score is inverse of risk (higher is better)
                    maturity_score = 100 - risk_percentage
                    
                    category_scores[category] = {
                        "score": maturity_score,
                        "questions_count": total_count,
                        "maturity_level": self._get_maturity_level(maturity_score)
                    }
        
        return category_scores
    
    def _get_maturity_level(self, maturity_score: float) -> str:
        """
        Get maturity level based on score
        
        Args:
            maturity_score: Maturity score (0-100)
            
        Returns:
            Maturity level string
        """
        if maturity_score < 20:
            return "Initial"
        elif maturity_score < 40:
            return "Developing"
        elif maturity_score < 60:
            return "Defined"
        elif maturity_score < 80:
            return "Managed"
        else:
            return "Optimized"