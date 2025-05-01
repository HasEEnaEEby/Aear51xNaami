"""
Explainable Risk Module for Security Compliance Advisor
This module provides explainability for risk assessments by analyzing key factors and generating natural language explanations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class ExplainableRiskModule:
    """
    Explainable Risk Module that generates natural language explanations for risk assessments
    to help non-technical stakeholders understand the risk factors and scores.
    """
    
    def __init__(self):
        """Initialize the explainable risk module"""
        # Load templates for explanations
        self.explanation_templates = self._load_explanation_templates()
        
    def _load_explanation_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Load explanation templates for different risk categories and levels
        
        Returns:
            Dictionary of templates by category and level
        """
        return {
            "Data Protection": {
                "positive": [
                    "Strong data protection controls are in place, including {details}.",
                    "Data protection measures exceed industry standards with {details}.",
                    "Comprehensive data protection strategy implemented with {details}."
                ],
                "negative": [
                    "Data protection controls show significant gaps, particularly in {details}.",
                    "Insufficient data protection measures identified, including lack of {details}.",
                    "Data protection implementation is inadequate, with critical issues in {details}."
                ],
                "recommendations": [
                    "Implement encryption for all sensitive data at rest and in transit.",
                    "Establish clear data classification policies and procedures.",
                    "Deploy data loss prevention (DLP) tools.",
                    "Conduct regular data access reviews.",
                    "Document and test data breach response procedures."
                ]
            },
            "Access Control": {
                "positive": [
                    "Access control mechanisms are robust, with {details}.",
                    "Least privilege principles effectively implemented through {details}.",
                    "Strong access management controls in place, including {details}."
                ],
                "negative": [
                    "Access control deficiencies create security gaps, particularly {details}.",
                    "Weak access management identified, including {details}.",
                    "Access control implementation is insufficient, lacking {details}."
                ],
                "recommendations": [
                    "Implement role-based access control (RBAC).",
                    "Enforce multi-factor authentication (MFA) for all privileged accounts.",
                    "Conduct quarterly access reviews.",
                    "Implement a formal user access provisioning and deprovisioning process.",
                    "Segment networks and implement least privilege principles."
                ]
            },
            "Vulnerability Management": {
                "positive": [
                    "Strong vulnerability management program in place with {details}.",
                    "Comprehensive vulnerability detection and remediation through {details}.",
                    "Effective vulnerability management practices including {details}."
                ],
                "negative": [
                    "Vulnerability management shows significant gaps in {details}.",
                    "Insufficient vulnerability remediation processes, particularly {details}.",
                    "Weak vulnerability management practices identified in {details}."
                ],
                "recommendations": [
                    "Implement regular vulnerability scanning across all systems.",
                    "Establish a formal patching policy with defined SLAs.",
                    "Conduct annual penetration testing.",
                    "Implement a risk-based approach to vulnerability remediation.",
                    "Deploy automated vulnerability management tools."
                ]
            },
            "Authentication": {
                "positive": [
                    "Authentication mechanisms are robust with {details}.",
                    "Strong credential management implemented through {details}.",
                    "Advanced authentication controls in place, including {details}."
                ],
                "negative": [
                    "Authentication weaknesses identified, specifically {details}.",
                    "Inadequate credential management, lacking {details}.",
                    "Authentication controls are insufficient, with issues in {details}."
                ],
                "recommendations": [
                    "Implement multi-factor authentication for all users.",
                    "Enforce strong password policies.",
                    "Consider passwordless authentication methods.",
                    "Implement single sign-on (SSO) where appropriate.",
                    "Deploy a privileged access management (PAM) solution."
                ]
            },
            "Encryption": {
                "positive": [
                    "Encryption is properly implemented with {details}.",
                    "Strong encryption strategy in place, including {details}.",
                    "Comprehensive encryption controls implemented, featuring {details}."
                ],
                "negative": [
                    "Encryption implementation is insufficient, particularly {details}.",
                    "Inadequate encryption controls identified, lacking {details}.",
                    "Weak encryption practices observed, especially {details}."
                ],
                "recommendations": [
                    "Implement TLS 1.3 for all communications.",
                    "Deploy encryption for all sensitive data at rest.",
                    "Establish a formal key management program.",
                    "Use strong encryption algorithms (AES-256, RSA-2048).",
                    "Regularly rotate encryption keys."
                ]
            },
            "Network Security": {
                "positive": [
                    "Network security architecture is strong with {details}.",
                    "Comprehensive network protection in place including {details}.",
                    "Effective network security controls implemented with {details}."
                ],
                "negative": [
                    "Network security controls show significant gaps in {details}.",
                    "Insufficient network protection identified, particularly {details}.",
                    "Network security implementation is inadequate, lacking {details}."
                ],
                "recommendations": [
                    "Implement network segmentation.",
                    "Deploy next-generation firewalls.",
                    "Implement intrusion detection/prevention systems.",
                    "Establish network traffic monitoring and analysis.",
                    "Deploy a formal network access control solution."
                ]
            },
            "Incident Response": {
                "positive": [
                    "Incident response capabilities are mature with {details}.",
                    "Strong incident handling procedures in place including {details}.",
                    "Effective incident detection and response through {details}."
                ],
                "negative": [
                    "Incident response capabilities show significant gaps in {details}.",
                    "Insufficient incident handling procedures, particularly {details}.",
                    "Incident response implementation is inadequate, lacking {details}."
                ],
                "recommendations": [
                    "Develop a formal incident response plan.",
                    "Establish an incident response team with defined roles.",
                    "Implement security information and event management (SIEM).",
                    "Conduct regular incident response exercises.",
                    "Establish relationships with external incident response experts."
                ]
            },
            "Business Continuity": {
                "positive": [
                    "Business continuity planning is robust with {details}.",
                    "Comprehensive disaster recovery controls in place including {details}.",
                    "Effective business continuity management through {details}."
                ],
                "negative": [
                    "Business continuity planning shows significant gaps in {details}.",
                    "Insufficient disaster recovery controls, particularly {details}.",
                    "Business continuity implementation is inadequate, lacking {details}."
                ],
                "recommendations": [
                    "Develop business continuity and disaster recovery plans.",
                    "Identify critical systems and recovery time objectives.",
                    "Implement redundant systems for critical infrastructure.",
                    "Regularly test backup and recovery procedures.",
                    "Document and communicate recovery procedures."
                ]
            }
        }
    
    def generate_risk_explanation(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate natural language explanations for risk assessment results
        
        Args:
            assessment: Risk assessment results from RiskScoringModel
            
        Returns:
            Assessment enriched with explanations
        """
        # Check if assessment exists
        if not assessment:
            logger.warning("No assessment data provided for explanation generation")
            return assessment
        
        # Extract key data from assessment
        risk_score = assessment.get('overall_risk_score', 0.5)
        risk_level = assessment.get('risk_level', 'Medium')
        risk_by_category = assessment.get('risk_by_category', {})
        findings = assessment.get('findings', [])
        
        # Define risk level descriptions
        risk_level_descriptions = {
            'Critical': 'critical, requiring immediate attention',
            'High': 'high, requiring prompt remediation',
            'Medium-High': 'medium-high, needing attention in the near term',
            'Medium': 'medium, requiring planned improvements',
            'Medium-Low': 'medium-low, with some improvement opportunities',
            'Low': 'low, representing a relatively strong security posture'
        }
        
        executive_summary = self._generate_executive_summary(
            risk_score, 
            risk_level, 
            risk_level_descriptions.get(risk_level, 'medium'),
            risk_by_category,
            findings
        )
        
        category_explanations = {}
        for category, data in risk_by_category.items():
            category_score = data.get('score', 0.5)
            category_level = data.get('risk_level', 'Medium')
            
            category_findings = [f for f in findings if f.get('category') == category]
            
            category_explanations[category] = self._generate_category_explanation(
                category, 
                category_score, 
                category_level,
                category_findings
            )
        
        recommendations_explanations = self._generate_recommendations_explanations(assessment.get('recommendations', []))
        
        explanations = {
            'executive_summary': executive_summary,
            'category_explanations': category_explanations,
            'recommendations_explanations': recommendations_explanations
        }
        
        assessment['explanations'] = explanations
        
        return assessment
    
    def _generate_executive_summary(self, risk_score: float, risk_level: str, risk_description: str, 
                                  risk_by_category: Dict[str, Any], findings: List[Dict[str, Any]]) -> str:
        """
        Generate executive summary explanation
        
        Args:
            risk_score: Overall risk score (0-1)
            risk_level: Risk level label
            risk_description: Description of risk level
            risk_by_category: Risk scores by category
            findings: List of security findings
            
        Returns:
            Executive summary text
        """
        risk_score_pct = risk_score * 100
        
        categories_sorted = sorted(risk_by_category.items(), key=lambda x: x[1]['score'])
        top_weaknesses = categories_sorted[:min(3, len(categories_sorted))]
        top_strengths = categories_sorted[-min(3, len(categories_sorted)):]
        
        # Count findings by severity
        finding_counts = {
            'Critical': 0,
            'High': 0, 
            'Medium': 0,
            'Low': 0
        }
        
        for finding in findings:
            level = finding.get('level', 'Medium')
            if level in finding_counts:
                finding_counts[level] += 1
        
        # Convert finding counts to description
        findings_description = []
        for level, count in finding_counts.items():
            if count > 0:
                findings_description.append(f"{count} {level.lower()}")
        
        findings_text = ", ".join(findings_description) if findings_description else "no significant"
        
        # Generate summary text
        summary = f"""
        Based on the assessment, the overall security risk level is {risk_level.lower()} ({risk_score_pct:.1f}%), which is considered {risk_description}. 
        The assessment identified {findings_text} security findings across {len(risk_by_category)} risk categories.
        """
        
        # Add weaknesses if any
        if top_weaknesses:
            weakness_text = ", ".join([f"{cat} ({data['score']*100:.1f}%)" for cat, data in top_weaknesses])
            summary += f" The most significant security gaps were observed in {weakness_text}."
        
        # Add strengths if any
        if top_strengths and top_strengths[0][1]['score'] >= 0.7:  # Only mention if score is good
            strength_text = ", ".join([f"{cat} ({data['score']*100:.1f}%)" for cat, data in top_strengths])
            summary += f" The strongest security controls were in {strength_text}."
        
        return summary.strip()
    
    def _generate_category_explanation(self, category: str, score: float, level: str, 
                                     findings: List[Dict[str, Any]]) -> str:
        """
        Generate explanation for a specific risk category
        
        Args:
            category: Risk category name
            score: Category risk score (0-1)
            level: Risk level label
            findings: Related findings for this category
            
        Returns:
            Category explanation text
        """
        if category not in self.explanation_templates:
            templates = {
                "positive": [
                    "Controls in this area are effective with {details}.",
                    "Security measures in this category are strong, including {details}.",
                    "This area demonstrates good security practices such as {details}."
                ],
                "negative": [
                    "This area shows significant security gaps, particularly {details}.",
                    "Controls in this category need improvement, especially {details}.",
                    "Security measures are insufficient, lacking {details}."
                ],
                "recommendations": [
                    "Implement industry-standard controls for this area.",
                    "Review and enhance security measures based on best practices.",
                    "Consider third-party assessment of this security domain.",
                    "Establish formal policies and procedures for this area.",
                    "Provide training to staff on these security practices."
                ]
            }
        else:
            templates = self.explanation_templates[category]
        
        # Format score as percentage
        score_pct = score * 100
        
        # Determine if positive or negative tone based on score
        if score >= 0.7:
            tone = "positive"
            template_list = templates["positive"]
        else:
            tone = "negative"
            template_list = templates["negative"]
        
        # Select a random template
        import random
        template = random.choice(template_list)
        
        # Prepare details based on findings
        if findings:
            if tone == "positive":
                # For positive tone, focus on what's implemented well
                details = "strong policies and controls" if score >= 0.9 else "generally adequate controls with some room for improvement"
            else:
                # For negative tone, focus on top findings
                finding_details = []
                for finding in findings[:2]:  # Use top 2 findings
                    description = finding.get('description', '')
                    # Extract a simplified version of the description
                    simple_desc = description.split("\n")[0] if "\n" in description else description
                    simple_desc = simple_desc[:100] + "..." if len(simple_desc) > 100 else simple_desc
                    finding_details.append(simple_desc)
                
                details = " and ".join(finding_details) if finding_details else "several security control gaps"
        else:
            # Generic details if no specific findings
            if tone == "positive":
                details = "comprehensive implementation of security controls"
            else:
                details = "multiple areas requiring improvement"
        
        # Fill in template
        explanation = template.format(details=details)
        
        # Add score and level context
        context = f"The assessment indicates a {level.lower()} risk level ({score_pct:.1f}%) in {category}. "
        
        # Add specific findings context if available
        if findings:
            finding_counts = {
                'Critical': 0,
                'High': 0, 
                'Medium': 0,
                'Low': 0
            }
            
            for finding in findings:
                level = finding.get('level', 'Medium')
                if level in finding_counts:
                    finding_counts[level] += 1
            
            # Only mention significant findings
            significant_findings = []
            if finding_counts['Critical'] > 0:
                significant_findings.append(f"{finding_counts['Critical']} critical")
            if finding_counts['High'] > 0:
                significant_findings.append(f"{finding_counts['High']} high")
            if finding_counts['Medium'] > 0:
                significant_findings.append(f"{finding_counts['Medium']} medium")
            
            if significant_findings:
                finding_text = ", ".join(significant_findings)
                context += f"The assessment identified {finding_text} risk findings in this category. "
        
        # Combine context and explanation
        full_explanation = context + explanation
        
        return full_explanation.strip()
    
    def _generate_recommendations_explanations(self, recommendations: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Generate explanations for recommendations
        
        Args:
            recommendations: List of recommendation objects
            
        Returns:
            Dictionary of recommendation IDs to explanations
        """
        explanations = {}
        
        for rec in recommendations:
            rec_id = rec.get('id', '')
            category = rec.get('category', '')
            priority = rec.get('priority', 'Medium')
            description = rec.get('description', '')
            
            # Generate explanation based on priority
            if priority == 'High':
                importance = "critical to address promptly as it represents a significant security risk"
            elif priority == 'Medium':
                importance = "important to address as part of a structured security improvement plan"
            else:
                importance = "beneficial to implement to further strengthen your security posture"
            
            # Get category context if available
            if category in self.explanation_templates:
                category_context = f"This recommendation focuses on improving {category} controls, which are essential for protecting your organization's assets. "
            else:
                category_context = ""
            
            # Generate business impact explanation
            if priority == 'High':
                impact = "Implementing this recommendation will significantly reduce security risk and help prevent potential breaches or compliance issues."
            elif priority == 'Medium':
                impact = "This improvement will enhance your security posture and demonstrate due diligence in protecting sensitive information."
            else:
                impact = "This enhancement will further mature your security program and align with industry best practices."
            
            # Combine into full explanation
            explanation = f"This recommendation is {importance}. {category_context}{impact}"
            
            explanations[rec_id] = explanation.strip()
        
        return explanations
    
    def generate_plain_language_report(self, assessment: Dict[str, Any]) -> str:
        """
        Generate a comprehensive plain-language report suitable for non-technical stakeholders
        
        Args:
            assessment: Risk assessment results (with explanations)
            
        Returns:
            Plain language report as string
        """
        # Ensure we have explanations
        if 'explanations' not in assessment:
            assessment = self.generate_risk_explanation(assessment)
        
        explanations = assessment.get('explanations', {})
        executive_summary = explanations.get('executive_summary', '')
        
        # Extract other key information
        risk_score = assessment.get('overall_risk_score', 0.5) * 100
        risk_level = assessment.get('risk_level', 'Medium')
        risk_by_category = assessment.get('risk_by_category', {})
        recommendations = assessment.get('recommendations', [])
        
        # Build the report
        report = []
        
        # Title and date
        from datetime import datetime
        report.append("# Security Risk Assessment Report")
        report.append(f"**Date:** {datetime.now().strftime('%B %d, %Y')}")
        report.append("\n")
        
        # Executive Summary
        report.append("## Executive Summary")
        report.append(executive_summary)
        report.append("\n")
        
        # Overall Risk Rating
        report.append("## Overall Risk Rating")
        report.append(f"**Risk Score:** {risk_score:.1f}%")
        report.append(f"**Risk Level:** {risk_level}")
        report.append("\n")
        
        # Key Risk Areas
        report.append("## Key Risk Areas")
        
        # Sort categories by risk (highest first)
        sorted_categories = sorted(risk_by_category.items(), key=lambda x: x[1]['score'])
        
        for category, data in sorted_categories:
            cat_score = data.get('score', 0.5) * 100
            cat_level = data.get('risk_level', 'Medium')
            
            report.append(f"### {category} ({cat_score:.1f}% - {cat_level} Risk)")
            
            # Add category explanation if available
            cat_explanation = explanations.get('category_explanations', {}).get(category, '')
            if cat_explanation:
                report.append(cat_explanation)
            
            report.append("\n")
        
        # Top Recommendations
        report.append("## Top Recommendations")
        
        # Sort recommendations by priority
        sorted_recommendations = sorted(recommendations, key=lambda x: {'High': 0, 'Medium': 1, 'Low': 2}.get(x.get('priority', 'Medium'), 1))
        
        for i, rec in enumerate(sorted_recommendations[:5]):  # Show top 5 recommendations
            rec_id = rec.get('id', '')
            title = rec.get('title', '')
            priority = rec.get('priority', 'Medium')
            description = rec.get('description', '')
            
            report.append(f"### {i+1}. {title} ({priority} Priority)")
            report.append(description)
            
            # Add recommendation explanation if available
            rec_explanation = explanations.get('recommendations_explanations', {}).get(rec_id, '')
            if rec_explanation:
                report.append(f"\n{rec_explanation}")
            
            # Add detailed actions if available
            detailed_actions = rec.get('detailed_actions', [])
            if detailed_actions:
                report.append("\n**Detailed Actions:**")
                for j, action in enumerate(detailed_actions):
                    report.append(f"* {action}")
            
            report.append("\n")
        
        # Conclusion
        report.append("## Conclusion")
        
        if risk_score >= 80:
            conclusion = "The security assessment indicates a strong security posture with minimal critical issues. Continued maintenance and monitoring are recommended to maintain this level of security."
        elif risk_score >= 60:
            conclusion = "The security assessment shows a moderate security posture with some areas requiring improvement. Addressing the high-priority recommendations will significantly strengthen the overall security posture."
        else:
            conclusion = "The security assessment indicates significant security gaps that require prompt attention. Implementing the high-priority recommendations is critical to reducing security risk."
        
        report.append(conclusion)
        report.append("\n")
        
        # Next Steps
        report.append("## Next Steps")
        report.append("1. Review this assessment with key stakeholders.")
        report.append("2. Develop a remediation plan prioritizing high-risk findings.")
        report.append("3. Implement recommended security controls.")
        report.append("4. Conduct a follow-up assessment to measure progress.")
        report.append("5. Establish a regular security assessment schedule.")
        
        # Join the report sections
        return "\n".join(report)