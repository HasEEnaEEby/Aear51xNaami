import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

class RiskScoringModel:
    """
    Calculates security risk scores based on questionnaire responses
    and generates recommendations for improvement.
    """
    
    def __init__(self, 
                 feature_mappings_path: Optional[str] = None,
                 compliance_mappings_path: Optional[str] = None,
                 recommendations_path: Optional[str] = None):
        """
        Initialize the risk scoring model
        
        Args:
            feature_mappings_path: Path to feature mappings configuration
            compliance_mappings_path: Path to compliance mappings configuration
            recommendations_path: Path to recommendation templates file
        """
        self.logger = logging.getLogger(__name__)
        
        # Default category weights
        self.category_weights = {
            "access_control": 0.25,
            "data_protection": 0.20,
            "network_security": 0.15,
            "vulnerability_management": 0.15,
            "incident_response": 0.15,
            "vendor_management": 0.10
        }
        
        # Default score mappings for fields
        self.score_mappings = {
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
        
        # Category to field mapping
        self.category_mappings = {
            "access_control": ["mfa_status", "password_policy", "privileged_access", "access_reviews"],
            "data_protection": ["data_classification", "encryption_status", "dlp_status", "data_retention"],
            "network_security": ["network_segmentation", "firewall_management"],
            "vulnerability_management": ["vuln_scanning", "patch_management"],
            "incident_response": ["ir_plan", "security_monitoring", "breach_response", "forensic_capabilities"],
            "vendor_management": ["vendor_assessment", "vendor_contracts", "third_party_access", "vendor_incidents"]
        }
        
        # Compliance framework mappings
        self.framework_mappings = {
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
        
        # Recommendation templates
        self.recommendation_templates = {}
        
        # Load custom configurations if provided
        if feature_mappings_path:
            self._load_feature_mappings(feature_mappings_path)
        
        if compliance_mappings_path:
            self._load_compliance_mappings(compliance_mappings_path)
        
        if recommendations_path:
            self._load_recommendation_templates(recommendations_path)
    
    def _load_feature_mappings(self, file_path: str):
        """Load feature mappings from a JSON file"""
        try:
            with open(file_path, 'r') as f:
                mappings = json.load(f)
                
            if 'category_weights' in mappings:
                self.category_weights.update(mappings['category_weights'])
                
            if 'score_mappings' in mappings:
                for field, values in mappings['score_mappings'].items():
                    if field in self.score_mappings:
                        self.score_mappings[field].update(values)
                    else:
                        self.score_mappings[field] = values
                        
            if 'category_mappings' in mappings:
                self.category_mappings.update(mappings['category_mappings'])
                
            self.logger.info(f"Loaded feature mappings from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error loading feature mappings: {str(e)}")
    
    def _load_compliance_mappings(self, file_path: str):
        """Load compliance mappings from a JSON file"""
        try:
            with open(file_path, 'r') as f:
                mappings = json.load(f)
                
            if 'framework_mappings' in mappings:
                for framework, values in mappings['framework_mappings'].items():
                    if framework in self.framework_mappings:
                        self.framework_mappings[framework].update(values)
                    else:
                        self.framework_mappings[framework] = values
                        
            self.logger.info(f"Loaded compliance mappings from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error loading compliance mappings: {str(e)}")
    
    def _load_recommendation_templates(self, file_path: str):
        """Load recommendation templates from a JSON file"""
        try:
            with open(file_path, 'r') as f:
                self.recommendation_templates = json.load(f)
                
            self.logger.info(f"Loaded {len(self.recommendation_templates)} recommendation templates from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error loading recommendation templates: {str(e)}")
            
            # Set default recommendation templates if loading fails
            self.recommendation_templates = {
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
                }
            }
    
    def assess_risk(self, questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate risk score based on questionnaire responses
        
        Args:
            questionnaire_data: Dictionary of questionnaire responses
            
        Returns:
            Assessment result dictionary with risk score, level, and explanation
        """
        # Calculate category scores
        category_scores = self._calculate_category_scores(questionnaire_data)
        
        # Calculate overall risk score
        risk_score = 0
        for category, score in category_scores.items():
            risk_score += score * self.category_weights.get(category, 0)
        
        # Generate risk factors
        risk_factors = self._generate_risk_factors(questionnaire_data, category_scores)
        
        # Organize factors by category
        categorized_factors = {}
        for category, fields in self.category_mappings.items():
            category_display = category.replace('_', ' ').title()
            categorized_factors[category_display] = [f for f in risk_factors if f['feature'] in fields]
        
        # Calculate framework compliance
        framework_compliance = self._calculate_framework_compliance(category_scores)
        
        # Generate risk level
        risk_level = self._get_risk_level(risk_score)
        
        # Return assessment result
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "explanation": {
                "top_factors": sorted(risk_factors, key=lambda x: abs(x['impact']), reverse=True)[:10],
                "categories": categorized_factors,
                "summary": "The risk score is based on the identified security weaknesses across multiple domains."
            },
            "framework_compliance": framework_compliance,
            "category_scores": category_scores,
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_category_scores(self, questionnaire_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate risk scores for each category
        
        Args:
            questionnaire_data: Dictionary of questionnaire responses
            
        Returns:
            Dictionary of category risk scores
        """
        category_scores = {}
        
        for category, fields in self.category_mappings.items():
            total_score = 0
            valid_fields = 0
            
            for field in fields:
                if field in questionnaire_data and questionnaire_data[field] in self.score_mappings.get(field, {}):
                    total_score += self.score_mappings[field][questionnaire_data[field]]
                    valid_fields += 1
            
            # Calculate average score for category
            if valid_fields > 0:
                category_scores[category] = total_score / valid_fields
            else:
                category_scores[category] = 50  # Default score if no valid fields
        
        return category_scores
    
    def _generate_risk_factors(self, 
                              questionnaire_data: Dict[str, Any], 
                              category_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Generate risk factors that contribute to the risk score
        
        Args:
            questionnaire_data: Dictionary of questionnaire responses
            category_scores: Dictionary of category risk scores
            
        Returns:
            List of risk factors with impact values
        """
        factors = []
        
        # Generate negative factors (high risk)
        for category, fields in self.category_mappings.items():
            for field in fields:
                if field in questionnaire_data and field in self.score_mappings:
                    if questionnaire_data[field] in self.score_mappings[field]:
                        score = self.score_mappings[field][questionnaire_data[field]]
                        
                        # Only include high-risk factors
                        if score >= 60:
                            impact = score * self.category_weights.get(category, 0) * 0.1
                            
                            factor = {
                                "feature": field,
                                "description": f"{field.replace('_', ' ').title()}: {questionnaire_data[field]}",
                                "impact": impact,
                                "direction": "negative"
                            }
                            factors.append(factor)
        
        # Generate positive factors (good practices)
        for category, fields in self.category_mappings.items():
            for field in fields:
                if field in questionnaire_data and field in self.score_mappings:
                    if questionnaire_data[field] in self.score_mappings[field]:
                        score = self.score_mappings[field][questionnaire_data[field]]
                        
                        # Only include good practice factors
                        if score <= 20:
                            impact = -1 * (100 - score) * self.category_weights.get(category, 0) * 0.02
                            
                            factor = {
                                "feature": field,
                                "description": f"Good Practice: {field.replace('_', ' ').title()} - {questionnaire_data[field]}",
                                "impact": impact,
                                "direction": "positive"
                            }
                            factors.append(factor)
        
        return factors
    
    def _calculate_framework_compliance(self, category_scores: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """
        Calculate compliance levels for different frameworks
        
        Args:
            category_scores: Dictionary of category risk scores
            
        Returns:
            Dictionary of framework compliance scores and gap areas
        """
        framework_compliance = {}
        
        for framework, category_weights in self.framework_mappings.items():
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
    
    def _get_risk_level(self, score: float) -> Dict[str, str]:
        """
        Determine risk level based on score
        
        Args:
            score: Overall risk score
            
        Returns:
            Dictionary with risk level name, description, and color
        """
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
    
    def generate_recommendations(self, assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on risk assessment
        
        Args:
            assessment: Risk assessment result dictionary
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        if "explanation" not in assessment or "top_factors" not in assessment["explanation"]:
            return recommendations
        
        # Get top risk factors (negative impact)
        risk_factors = [factor for factor in assessment["explanation"]["top_factors"] 
                       if factor["direction"] == "negative"]
        
        # Generate recommendations for each high-risk factor
        for factor in risk_factors:
            feature = factor.get("feature")
            
            if feature in self.recommendation_templates:
                rec = self.recommendation_templates[feature].copy()
                
                # Set impact based on factor impact
                impact_value = abs(factor.get("impact", 0))
                if impact_value >= 7:
                    rec["impact"] = "High"
                elif impact_value >= 4:
                    rec["impact"] = "Medium"
                else:
                    rec["impact"] = "Low"
                
                recommendations.append(rec)
        
        # Sort recommendations by impact
        impact_order = {"High": 0, "Medium": 1, "Low": 2}
        recommendations.sort(key=lambda x: impact_order.get(x.get("impact", "Low"), 3))
        
        return recommendations