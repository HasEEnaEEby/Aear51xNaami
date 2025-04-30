import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import os
import json
from .risk_scoring_model import RiskScoringModel

class ExplainableRiskModule:
    def __init__(self, model: RiskScoringModel = None, frameworks_path: str = None):
        """
        Initialize the Explainable Risk Module.
        
        Args:
            model: Trained RiskScoringModel instance
            frameworks_path: Path to compliance frameworks data
        """
        self.model = model or RiskScoringModel()
        self.frameworks_path = frameworks_path
        self.frameworks_data = self._load_frameworks_data() if frameworks_path else {}
        
        # Load mitigation recommendations knowledge base
        self.recommendations_map = self._load_recommendations_map()
    
    def _load_frameworks_data(self) -> Dict:
        """Load compliance frameworks data from files"""
        frameworks_data = {}
        if os.path.exists(self.frameworks_path):
            for filename in os.listdir(self.frameworks_path):
                if filename.endswith('.json'):
                    with open(os.path.join(self.frameworks_path, filename), 'r') as f:
                        framework_name = filename.split('.')[0]
                        frameworks_data[framework_name] = json.load(f)
        return frameworks_data
    
    def _load_recommendations_map(self) -> Dict:
        """Load mapping of risk factors to recommendations"""
        # This would normally load from a file, but for this example we'll define inline
        return {
            # Authentication and access control
            "auth_": {
                "recommendations": [
                    "Implement multi-factor authentication for all users",
                    "Enforce strong password policies",
                    "Implement least privilege access controls",
                    "Review user access permissions quarterly"
                ],
                "frameworks": ["NIST 800-53", "ISO", "CIS"]
            },
            "password_": {
                "recommendations": [
                    "Implement password complexity requirements",
                    "Set up regular password rotation",
                    "Use secure password storage with proper hashing"
                ],
                "frameworks": ["NIST 800-53", "CIS", "PCI-DSS"]
            },
            # Data protection
            "encryption_": {
                "recommendations": [
                    "Encrypt all sensitive data at rest",
                    "Implement TLS for all data in transit",
                    "Use strong encryption algorithms (AES-256)"
                ],
                "frameworks": ["NIST 800-53", "ISO", "HIPPA", "PCI-DSS"]
            },
            "data_": {
                "recommendations": [
                    "Implement data classification policies",
                    "Set up data loss prevention tools",
                    "Create data retention and disposal procedures"
                ],
                "frameworks": ["GDPR", "CCPA", "ISO", "HIPPA"]
            },
            # Network security
            "network_": {
                "recommendations": [
                    "Implement network segmentation",
                    "Deploy next-generation firewalls",
                    "Conduct regular network vulnerability scans"
                ],
                "frameworks": ["NIST 800-53", "CIS", "ISO"]
            },
            "firewall_": {
                "recommendations": [
                    "Configure firewall rules using deny-by-default stance",
                    "Implement web application firewall",
                    "Document and regularly review firewall rules"
                ],
                "frameworks": ["PCI-DSS", "CIS", "NIST 800-53"]
            },
            # Incident response
            "incident_": {
                "recommendations": [
                    "Develop a formal incident response plan",
                    "Conduct tabletop exercises regularly",
                    "Establish an incident response team",
                    "Deploy security monitoring and alerting tools"
                ],
                "frameworks": ["NIST 800-53", "ISO", "HITRUST"]
            },
            "backup_": {
                "recommendations": [
                    "Implement 3-2-1 backup strategy",
                    "Test data restoration procedures regularly",
                    "Encrypt backup data"
                ],
                "frameworks": ["NIST 800-53", "ISO", "CIS"]
            },
            # Default category
            "default": {
                "recommendations": [
                    "Implement security awareness training",
                    "Conduct regular risk assessments",
                    "Develop and maintain security policies",
                    "Establish a security governance structure"
                ],
                "frameworks": ["NIST 800-53", "ISO", "CIS", "HITRUST"]
            }
        }
    
    def _map_factor_to_recommendations(self, factor_name: str) -> Dict:
        """Map a factor name to relevant recommendations"""
        for category, content in self.recommendations_map.items():
            if category in factor_name:
                return content
        return self.recommendations_map["default"]
    
    def _get_question_mapping(self, factor_name: str, questionnaire_data: Dict) -> str:
        """Map technical feature name to human-readable question"""
        # This would normally use a mapping file, but for demo purposes we'll handle directly
        # Format: "text_12" -> "question_text"
        if factor_name.startswith("text_"):
            try:
                index = int(factor_name.split("_")[1])
                question_keys = list(questionnaire_data.keys())
                if index < len(question_keys):
                    return question_keys[index]
            except:
                pass
        return factor_name
    
    def analyze_questionnaire(self, questionnaire_data: Dict) -> Dict[str, Any]:
        """
        Analyze questionnaire responses and generate risk assessment with explanations.
        
        Args:
            questionnaire_data: Dictionary of questionnaire responses
            
        Returns:
            Dictionary containing risk score, explanations, and recommendations
        """
        # Convert questionnaire data to DataFrame for model
        df = pd.DataFrame([questionnaire_data])
        
        # Generate risk score and raw explanations
        risk_results = self.model.predict(df)
        
        # Process explanations into human-readable format
        positive_explanations = []
        negative_explanations = []
        
        # Process positive factors
        for factor_name, impact in risk_results["positive_factors"]:
            question = self._get_question_mapping(factor_name, questionnaire_data)
            positive_explanations.append({
                "factor": question,
                "impact": float(impact),
                "explanation": f"Your response to '{question}' demonstrates good security practices."
            })
        
        # Process negative factors
        for factor_name, impact in risk_results["negative_factors"]:
            question = self._get_question_mapping(factor_name, questionnaire_data)
            negative_explanations.append({
                "factor": question,
                "impact": float(impact),
                "explanation": f"Your response to '{question}' indicates potential security gaps."
            })
        
        # Generate recommendations based on negative factors
        prioritized_recommendations = []
        used_recommendations = set()
        
        for factor_name, _ in risk_results["negative_factors"]:
            recs = self._map_factor_to_recommendations(factor_name)
            
            for rec in recs["recommendations"]:
                if rec not in used_recommendations:
                    frameworks = recs["frameworks"]
                    prioritized_recommendations.append({
                        "recommendation": rec,
                        "frameworks": frameworks,
                        "priority": len(prioritized_recommendations) + 1
                    })
                    used_recommendations.add(rec)
                    if len(prioritized_recommendations) >= 10:  # Limit to top 10
                        break
        
        # Generate summary explanation
        summary = self._generate_summary(
            risk_results["risk_score"], 
            risk_results["risk_level"],
            positive_explanations,
            negative_explanations
        )
        
        return {
            "risk_score": risk_results["risk_score"],
            "risk_level": risk_results["risk_level"],
            "summary": summary,
            "positive_factors": positive_explanations,
            "negative_factors": negative_explanations,
            "recommendations": prioritized_recommendations
        }
    
    def _generate_summary(self, risk_score: float, risk_level: str, 
                         positive_factors: List[Dict], negative_factors: List[Dict]) -> str:
        """Generate a plain-language summary of the risk assessment"""
        
        # Count factors
        pos_count = len(positive_factors)
        neg_count = len(negative_factors)
        
        # Generate introduction based on risk level
        if risk_level == "Low Risk":
            intro = (f"Your organization demonstrates a strong security posture with a risk score "
                    f"of {risk_score:.2f} (Low Risk).")
        elif risk_level == "Medium Risk":
            intro = (f"Your organization has a moderate security posture with a risk score "
                    f"of {risk_score:.2f} (Medium Risk).")
        else:
            intro = (f"Your organization shows significant security gaps with a risk score "
                    f"of {risk_score:.2f} (High Risk).")
        
        # Add positive factors overview
        if pos_count > 0:
            positives = ("We identified " + (
                f"{pos_count} areas where your security practices are strong. " if pos_count > 1 
                else "one area where your security practice is strong. "
            ))
            top_positive = positive_factors[0]["factor"]
            positives += f"Most notably, your approach to '{top_positive}' demonstrates good security practices."
        else:
            positives = "We did not identify any strong security practices in your responses."
        
        # Add negative factors overview
        if neg_count > 0:
            negatives = ("However, there " + (
                f"are {neg_count} areas that need improvement. " if neg_count > 1 
                else "is one area that needs improvement. "
            ))
            top_negative = negative_factors[0]["factor"]
            negatives += f"The most critical gap is in '{top_negative}', which significantly impacts your risk score."
        else:
            negatives = "We did not identify any significant security gaps in your responses."
        
        # Add recommendation overview
        if neg_count > 0:
            recommendations = ("We've provided targeted recommendations to address these gaps "
                              "and improve your overall security posture.")
        else:
            recommendations = ("While your security posture is strong, we still recommend regular "
                              "security assessments to maintain this level.")
        
        # Combine all parts
        return f"{intro} {positives} {negatives} {recommendations}"