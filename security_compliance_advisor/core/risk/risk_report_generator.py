"""
PDF Risk Report Generator for Security Compliance Advisor
This module generates detailed PDF risk assessment reports based on questionnaire analysis.
"""

import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus.flowables import HRFlowable
import base64
from PIL import Image as PILImage
import plotly.graph_objects as go
import io
import os

class RiskReportGenerator:
    """
    Generates detailed PDF risk assessment reports from questionnaire data and assessment results.
    """
    
    def __init__(self, company_name="Your Company"):
        """Initialize the report generator with company information"""
        self.company_name = company_name
        self.styles = getSampleStyleSheet()
        
        # Define custom styles
        self.styles.add(ParagraphStyle(
            name='Heading1Bold',
            parent=self.styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='NormalIndent',
            parent=self.styles['Normal'],
            leftIndent=20,
            fontSize=10
        ))
        
        # Define risk color mapping
        self.risk_colors = {
            'Critical': colors.indianred,
            'High': colors.orangered,
            'Moderate': colors.orange,
            'Medium': colors.orange,
            'Low': colors.green,
            'Negligible': colors.lightgreen
        }
        
        # Define impact and likelihood levels
        self.impact_levels = {
            5: "Catastrophic",
            4: "Severe",
            3: "Major",
            2: "Minor",
            1: "Negligible"
        }
        
        self.likelihood_levels = {
            5: "Certain",
            4: "Probable",
            3: "Possible",
            2: "Unlikely",
            1: "Rare"
        }
    
    def generate_risk_matrix_image(self):
        """Generate risk matrix image"""
        plt.figure(figsize=(6, 5))
        
        # Create the matrix
        matrix_data = [
            [25, 20, 15, 10, 5],
            [20, 16, 12, 8, 4],
            [15, 12, 9, 6, 3],
            [10, 8, 6, 4, 2],
            [5, 4, 3, 2, 1]
        ]
        
        # Create a plot
        plt.imshow(matrix_data, cmap='RdYlGn_r', interpolation='nearest', aspect='equal')
        plt.colorbar(label='Risk Score')
        
        # Add labels
        plt.xlabel('Likelihood')
        plt.ylabel('Impact')
        
        plt.title('Risk Matrix')
        
        # Set axis labels
        plt.xticks([0, 1, 2, 3, 4], ['Certain(5)', 'Probable(4)', 'Possible(3)', 'Unlikely(2)', 'Rare(1)'])
        plt.yticks([0, 1, 2, 3, 4], ['Catastrophic(5)', 'Severe(4)', 'Major(3)', 'Minor(2)', 'Negligible(1)'])
        
        # Adjust layout
        plt.tight_layout()
        
        # Save to buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    def generate_risk_count_chart(self, risk_counts):
        """Generate risk count chart"""
        plt.figure(figsize=(6, 4))
        
        categories = list(risk_counts.keys())
        values = list(risk_counts.values())
        
        # Set colors for each risk level
        colors_map = {
            'Critical': 'red',
            'High': 'orange',
            'Moderate': 'yellow',
            'Low': 'green'
        }
        
        colors_list = [colors_map.get(category, 'blue') for category in categories]
        
        # Create bar chart
        plt.bar(categories, values, color=colors_list)
        
        # Add labels and title
        plt.xlabel('Risk Level')
        plt.ylabel('Risk Count')
        plt.title('Identified Risks')
        
        # Add value labels on top of bars
        for i, v in enumerate(values):
            plt.text(i, v + 0.5, str(v), ha='center')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save to buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    def create_pdf_report(self, assessment, vendor_name, logo_path=None):
        """
        Create a comprehensive PDF risk assessment report
        
        Args:
            assessment: Risk assessment results
            vendor_name: Name of the vendor being assessed
            logo_path: Path to company logo image
            
        Returns:
            PDF report as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                              rightMargin=0.5*inch, leftMargin=0.5*inch,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Add company logo if provided
        if logo_path and os.path.exists(logo_path):
            img = Image(logo_path, width=2*inch, height=0.75*inch)
            elements.append(img)
        
        # Add report title
        title = Paragraph(f"Third Party Risk Assessment Report", self.styles['Heading1Bold'])
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Add vendor name
        vendor_info = Paragraph(f"VENDOR: {vendor_name.upper()}", self.styles['Heading2'])
        elements.append(vendor_info)
        elements.append(Spacer(1, 0.1*inch))
        
        # Add overall risk rating
        risk_level = assessment.get('risk_level', 'Medium')
        risk_score = assessment.get('overall_risk_score', 0.5) * 100  # Convert to percentage
        
        elements.append(Paragraph("Overall Risk Rating", self.styles['Heading3']))
        
        # Create risk rating color bar
        risk_levels = [
            ('Low', colors.lightgreen), 
            ('Moderate', colors.yellow), 
            ('High', colors.orange), 
            ('Critical', colors.red)
        ]
        
        risk_table_data = [[]]
        for label, color in risk_levels:
            cell_style = [
                ('BACKGROUND', (0, 0), (0, 0), color),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.black),
                ('BOX', (0, 0), (0, 0), 0.5, colors.black),
            ]
            
            # Highlight the current risk level
            if label.lower() == risk_level.lower():
                cell_style.append(('LINEWIDTH', (0, 0), (0, 0), 2))
            
            cell = Paragraph(label, self.styles['Normal'])
            risk_table_data[0].append(cell)
        
        risk_table = Table(risk_table_data, colWidths=[1.2*inch]*len(risk_levels))
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.lightgreen),
            ('BACKGROUND', (1, 0), (1, 0), colors.yellow),
            ('BACKGROUND', (2, 0), (2, 0), colors.orange),
            ('BACKGROUND', (3, 0), (3, 0), colors.red),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        
        elements.append(risk_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Add page break
        elements.append(PageBreak())
        
        # Add table of contents
        elements.append(Paragraph("Table of Contents", self.styles['Heading1']))
        toc_items = [
            "Executive Summary",
            "Vendor Profile",
            "Risk Assessment Approach",
            "Risk Assessment Findings",
            "Documentation Review",
            "Identified Risks",
            "Exceptions Noted",
            "Recommendation",
            "Conclusion"
        ]
        
        for i, item in enumerate(toc_items):
            elements.append(Paragraph(f"{i+1}. {item}", self.styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        elements.append(PageBreak())
        
        # Executive Summary
        elements.append(Paragraph("Executive Summary", self.styles['Heading1']))
        
        # Generate executive summary from assessment explanations if available
        if 'explanations' in assessment and 'executive_summary' in assessment['explanations']:
            exec_summary = assessment['explanations']['executive_summary']
        else:
            # Generate a basic summary
            risk_by_category = assessment.get('risk_by_category', {})
            findings = assessment.get('findings', [])
            
            findings_count = len(findings)
            high_findings = sum(1 for f in findings if f.get('level') in ['Critical', 'High'])
            
            exec_summary = f"""
            A comprehensive risk assessment of {vendor_name} was completed on {datetime.now().strftime('%B %d, %Y')}. 
            The vendor's security controls have been evaluated against our security standards.
            
            The overall vendor risk has been evaluated and classified as {risk_level} ({risk_score:.1f}%).
            
            The assessment identified {findings_count} security findings, of which {high_findings} were classified as Critical or High risk.
            """
        
        elements.append(Paragraph(exec_summary, self.styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Key Findings
        elements.append(Paragraph("Key Findings:", self.styles['Heading3']))
        
        # Extract top findings
        findings = assessment.get('findings', [])
        if findings:
            # Sort findings by impact
            sorted_findings = sorted(findings, key=lambda x: x.get('score_impact', 0), reverse=True)
            
            # Create findings table
            findings_data = [["#", "Risk Description", "Risk Rating"]]
            
            for i, finding in enumerate(sorted_findings[:5]):  # Show top 5 findings
                level = finding.get('level', 'Medium')
                description = finding.get('title', '')
                if len(description) > 100:
                    description = description[:97] + "..."
                
                # Calculate risk score
                impact = finding.get('impact', 3)
                likelihood = finding.get('likelihood', 3)
                risk_score = impact * likelihood
                
                findings_data.append([i+1, description, f"{level} ({risk_score})"])
            
            findings_table = Table(findings_data, colWidths=[0.3*inch, 4*inch, 1.2*inch])
            findings_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            
            elements.append(findings_table)
        else:
            elements.append(Paragraph("No significant findings were identified.", self.styles['Normal']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Documentation Review
        elements.append(Paragraph("Essential documentation has been tabulated below:", self.styles['Normal']))
        
        doc_data = [["Description", "Status", "Provided by Vendor"]]
        
        # Sample documentation status - replace with actual assessment data
        doc_status = {
            "ISO 27001 Certification": {"status": "Certified", "provided": "Yes"},
            "SOC 2 Type 2 Attestation": {"status": "Not attested", "provided": "No"},
            "Privacy Shield": {"status": "Not certified", "provided": "No"},
            "GDPR Compliance": {"status": "Partial", "provided": "Yes"},
            "PCI DSS": {"status": "Not applicable", "provided": "N/A"}
        }
        
        # Get framework compliance data if available
        frameworks = assessment.get('framework_compliance', {})
        if frameworks:
            for framework_id, data in frameworks.items():
                # Format framework name for display
                framework_name = {
                    'iso27001': 'ISO 27001 Certification',
                    'nist_csf': 'NIST CSF Assessment',
                    'pci_dss': 'PCI DSS Certification',
                    'gdpr': 'GDPR Compliance',
                    'hipaa': 'HIPAA Compliance',
                    'ccpa': 'CCPA Compliance',
                    'cis': 'CIS Controls Assessment',
                    'hitrust': 'HITRUST CSF Certification'
                }.get(framework_id, framework_id)
                
                compliance_score = data.get('compliance_score', 0)
                
                # Determine status based on compliance score
                if compliance_score >= 90:
                    status = "Certified/Compliant"
                elif compliance_score >= 70:
                    status = "Substantially Compliant"
                elif compliance_score >= 50:
                    status = "Partially Compliant"
                else:
                    status = "Not Compliant"
                
                doc_status[framework_name] = {
                    "status": status,
                    "provided": "Yes" if compliance_score > 0 else "No"
                }
        
        for doc, info in doc_status.items():
            doc_data.append([doc, info["status"], info["provided"]])
        
        doc_table = Table(doc_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        doc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        
        elements.append(doc_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Additional Findings
        elements.append(Paragraph("Additional Findings", self.styles['Heading3']))
        
        # Get exceptions noted from assessment
        exceptions = []
        for finding in findings:
            if finding.get('level') in ['Critical', 'High', 'Medium']:
                exceptions.append(finding.get('description', ''))
        
        if exceptions:
            for i, exception in enumerate(exceptions[:5]):  # Limit to 5 major exceptions
                # Format and truncate exception text
                exception_text = exception.replace('\n', ' ')
                if len(exception_text) > 200:
                    exception_text = exception_text[:197] + "..."
                
                elements.append(Paragraph(f"● {exception_text}", self.styles['NormalIndent']))
                elements.append(Spacer(1, 0.1*inch))
        else:
            elements.append(Paragraph("No significant exceptions were noted.", self.styles['Normal']))
        
        # Add page break
        elements.append(PageBreak())
        
        # Risk Assessment Approach
        elements.append(Paragraph("Risk Assessment Approach", self.styles['Heading1']))
        
        # Describe risk assessment methodology
        methodology_text = """
        This risk assessment is conducted following industry standard methodologies and frameworks including 
        NIST SP 800-30 (Guide for Conducting Risk Assessments). Risks were evaluated by considering threat events, 
        their likelihood of occurrence, system vulnerabilities, mitigating factors, and the potential consequences/impact.
        
        The assessment involved:
        - Questionnaire responses analysis
        - Document review
        - Control implementation verification
        - Gap analysis against security standards
        - Risk scoring using impact and likelihood factors
        """
        
        elements.append(Paragraph(methodology_text, self.styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Add impact and likelihood tables
        elements.append(Paragraph("Impact Levels and Description", self.styles['Heading3']))
        
        impact_data = [["Impact", "Impact Description"]]
        for level, name in self.impact_levels.items():
            description = {
                5: "A threat event could be expected to have a catastrophic adverse effect on operations, assets, or individuals.",
                4: "A threat event could be expected to have a severe adverse effect on operations, assets, or individuals.",
                3: "A threat event could be expected to have a serious adverse effect on operations, assets, or individuals.",
                2: "A threat event could be expected to have a limited adverse effect on operations, assets, or individuals.",
                1: "A threat event could be expected to have a negligible adverse effect on operations, assets, or individuals."
            }.get(level, "")
            
            impact_data.append([f"{name}({level})", description])
        
        impact_table = Table(impact_data, colWidths=[1.5*inch, 4.5*inch])
        impact_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        
        elements.append(impact_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Likelihood table
        elements.append(Paragraph("Likelihood Levels and Descriptions", self.styles['Heading3']))
        
        likelihood_data = [["Likelihood", "Likelihood Description"]]
        for level, name in self.likelihood_levels.items():
            description = {
                5: "Threat event is almost certain to occur.",
                4: "Threat event is highly likely to occur.",
                3: "Threat event is somewhat likely to occur.",
                2: "Threat event is unlikely to occur.",
                1: "Threat event is highly unlikely to occur."
            }.get(level, "")
            
            likelihood_data.append([f"{name}({level})", description])
        
        likelihood_table = Table(likelihood_data, colWidths=[1.5*inch, 4.5*inch])
        likelihood_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        
        elements.append(likelihood_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Risk Matrix
        elements.append(Paragraph("Risk Matrix", self.styles['Heading3']))
        elements.append(Paragraph("Risk = Likelihood * Impact", self.styles['Normal']))
        
        # Create risk matrix
        matrix_data = [
            ["", "Likelihood", "", "", "", ""],
            ["", "Certain(5)", "Probable(4)", "Possible(3)", "Unlikely(2)", "Rare(1)"],
            ["Impact", "", "", "", "", ""],
            ["Catastrophic(5)", "25", "20", "15", "10", "5"],
            ["Severe(4)", "20", "16", "12", "8", "4"],
            ["Major(3)", "15", "12", "9", "6", "3"],
            ["Minor(2)", "10", "8", "6", "4", "2"],
            ["Negligible(1)", "5", "4", "3", "2", "1"]
        ]
        
        # Define cell colors based on risk level
        cell_colors = {
            "25": colors.red, "20": colors.red,
            "15": colors.orange, "16": colors.orange, "12": colors.orange, "10": colors.orange,
            "9": colors.yellow, "8": colors.yellow, "6": colors.yellow, "5": colors.yellow, "4": colors.yellow,
            "3": colors.lightgreen, "2": colors.lightgreen, "1": colors.lightgreen
        }
        
        matrix_table = Table(matrix_data)
        matrix_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (0, 2), (-1, 2), colors.lightgrey),
            ('SPAN', (1, 0), (5, 0)),  # Merge "Likelihood" cells
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        
        # Add cell colors for risk values
        for i in range(3, 8):
            for j in range(1, 6):
                cell_value = matrix_data[i][j]
                if cell_value in cell_colors:
                    matrix_style.append(('BACKGROUND', (j, i), (j, i), cell_colors[cell_value]))
        
        matrix_table.setStyle(TableStyle(matrix_style))
        elements.append(matrix_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Risk Levels table
        elements.append(Paragraph("Risk Levels and Descriptions", self.styles['Heading3']))
        
        risk_level_data = [["Risk Level", "Risk Description"]]
        
        risk_descriptions = {
            "Low(1-3)": "A threat event could be expected to have a limited adverse effect on organizational operations, mission capabilities, assets, individuals, customers or other organizations.",
            "Moderate(4-9)": "A threat event could be expected to have a significant adverse effect on organizational operations, mission capabilities, assets, individuals, customers or other organizations.",
            "High(10-19)": "A threat event could be expected to have a significant adverse effect on organizational operations, mission capabilities, assets, individuals, customers or other organizations.",
            "Critical(20-25)": "A threat event could be expected to have a critical adverse effect on organizational operations, mission capabilities, assets, individuals, customers or other organizations."
        }
        
        for level, description in risk_descriptions.items():
            risk_level_data.append([level, description])
        
        risk_level_table = Table(risk_level_data, colWidths=[1.5*inch, 4.5*inch])
        risk_level_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        
        elements.append(risk_level_table)
        
        # Add page break
        elements.append(PageBreak())
        
        # Risk Assessment Findings
        elements.append(Paragraph("Risk Assessment Findings", self.styles['Heading1']))
        
        # Add assessment summary
        assessment_date = datetime.now().strftime('%B %d, %Y')
        assessment_summary = f"""
        Security assessment was performed between {self.company_name} and {vendor_name} on {assessment_date}. 
        The majority of controls were found to be in alignment with our security standards. 
        """
        
        if findings:
            assessment_summary += f"However, {len(findings)} gaps were identified during the assessment."
        else:
            assessment_summary += "No significant gaps were identified during the assessment."
        
        elements.append(Paragraph(assessment_summary, self.styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Count findings by risk level
        risk_counts = {
            "Low(1-3)": 0,
            "Moderate(4-9)": 0,
            "High(10-19)": 0,
            "Critical(20-25)": 0
        }
        
        for finding in findings:
            level = finding.get('level', 'Medium')
            if level in ['Critical']:
                risk_counts["Critical(20-25)"] += 1
            elif level in ['High']:
                risk_counts["High(10-19)"] += 1
            elif level in ['Medium', 'Moderate']:
                risk_counts["Moderate(4-9)"] += 1
            else:
                risk_counts["Low(1-3)"] += 1
        
        # If no findings, provide default counts
        if not findings:
            # Check if we have risk_by_category data
            risk_by_category = assessment.get('risk_by_category', {})
            if risk_by_category:
                # Count by risk level in categories
                for category, data in risk_by_category.items():
                    level = data.get('risk_level', 'Medium')
                    if level in ['Critical']:
                        risk_counts["Critical(20-25)"] += 1
                    elif level in ['High']:
                        risk_counts["High(10-19)"] += 1
                    elif level in ['Medium', 'Medium-Low']:
                        risk_counts["Moderate(4-9)"] += 1
                    else:
                        risk_counts["Low(1-3)"] += 1
            else:
                # Default counts for demo
                risk_counts["Low(1-3)"] = 85
                risk_counts["Moderate(4-9)"] = 2
                risk_counts["High(10-19)"] = 0
                risk_counts["Critical(20-25)"] = 0
        
        # Create risk count table
        risk_count_data = [["Risk Level", "Risk Count"]]
        
        for level, count in risk_counts.items():
            risk_count_data.append([level, count])
        
        risk_count_table = Table(risk_count_data, colWidths=[3*inch, 3*inch])
        risk_count_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        
        elements.append(risk_count_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Add risk count chart
        try:
            risk_count_img = self.generate_risk_count_chart(risk_counts)
            elements.append(Image(risk_count_img, width=6*inch, height=4*inch))
        except Exception as e:
            elements.append(Paragraph(f"Error generating chart: {str(e)}", self.styles['Normal']))
        
        # Add page break
        elements.append(PageBreak())
        
        # Documentation Review
        elements.append(Paragraph("Documentation Review", self.styles['Heading1']))
        
        # Create more detailed documentation review table
        doc_review_data = [
            ["Required Document", "Status", "Vendor Comment", "Exception Noted", "Remarks"]
        ]
        
        # Sample documentation review data - replace with actual assessment data
        doc_review_items = [
            {
                "document": "Data Processing Addendum (DPA)",
                "status": "Not uploaded",
                "comment": "None",
                "exception": "No exception noted.",
                "remarks": "None"
            },
            {
                "document": "ISO 27001",
                "status": "Uploaded",
                "comment": "None",
                "exception": "No exceptions noted.",
                "remarks": "None"
            },
            {
                "document": "MSA",
                "status": "Uploaded",
                "comment": "None",
                "exception": "Exception noted.",
                "remarks": "The MSA is yet to be signed by both parties."
            },
            {
                "document": "SOW",
                "status": "Not Uploaded",
                "comment": "None",
                "exception": "No exceptions noted.",
                "remarks": "None"
            },
            {
                "document": "Pentest Report",
                "status": "Not uploaded",
                "comment": "None",
                "exception": "No exceptions noted.",
                "remarks": "None"
            },
            {
                "document": "SOC 2 Type 2",
                "status": "Not uploaded",
                "comment": "None",
                "exception": "No exception noted.",
                "remarks": "None"
            },
            {
                "document": "SOC 1 Type 2",
                "status": "Not uploaded",
                "comment": "None",
                "exception": "No exceptions noted.",
                "remarks": "None"
            }
        ]
        
        for item in doc_review_items:
            doc_review_data.append([
                item["document"],
                item["status"],
                item["comment"],
                item["exception"],
                item["remarks"]
            ])
        
        # Create table with appropriate column widths
        doc_review_table = Table(doc_review_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1.5*inch, 1*inch])
        doc_review_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        
        elements.append(doc_review_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Identified Risks
        elements.append(PageBreak())
        elements.append(Paragraph("Identified Risks", self.styles['Heading1']))
        
        # Create detailed risk tables for each finding
        if findings:
            for i, finding in enumerate(findings):
                if i > 0:
                    elements.append(Spacer(1, 0.3*inch))
                
                elements.append(Paragraph(f"Risk #{i+1}", self.styles['Heading3']))
                
                # Extract finding details
                description = finding.get('title', 'No description provided')
                level = finding.get('level', 'Medium')
                
                level_to_likelihood = {
                    'Critical': 5,
                    'High': 4,
                    'Medium': 3,
                    'Low': 2,
                    'Negligible': 1
                }
                
                level_to_impact = {
                    'Critical': 5,
                    'High': 4,
                    'Medium': 3,
                    'Low': 2,
                    'Negligible': 1
                }
                
                likelihood = finding.get('likelihood', level_to_likelihood.get(level, 3))
                impact = finding.get('impact', level_to_impact.get(level, 3))
                
                likelihood_text = self.likelihood_levels.get(likelihood, f"Level {likelihood}")
                impact_text = self.impact_levels.get(impact, f"Level {impact}")
                
                # Calculate risk score
                risk_score = likelihood * impact
                
                # Map risk score to risk level
                if risk_score >= 20:
                    risk_level_text = "Critical"
                elif risk_score >= 10:
                    risk_level_text = "High"
                elif risk_score >= 4:
                    risk_level_text = "Moderate"
                else:
                    risk_level_text = "Low"
                
                # Get recommendations for this finding
                recommendations = assessment.get('recommendations', [])
                finding_rec = None
                
                for rec in recommendations:
                    if rec.get('finding_id') == finding.get('id'):
                        finding_rec = rec
                        break
                
                # Create risk details table
                risk_details_data = [
                    ["Risk Description", description],
                    ["Likelihood", f"{likelihood_text} ({likelihood})"],
                    ["Impact", f"{impact_text} ({impact})"],
                    ["Risk Level", f"{risk_level_text} ({risk_score})"]
                ]
                
                if finding_rec:
                    risk_details_data.append(["Proposed Remediation", finding_rec.get('description', 'No remediation specified')])
                else:
                    # Generate generic remediation based on finding category
                    category = finding.get('category', 'General')
                    remediation = f"Implement controls to address {category} risks in accordance with industry best practices."
                    risk_details_data.append(["Proposed Remediation", remediation])
                
                # Add vendor comment if available
                vendor_comment = finding.get('vendor_comment', '')
                if vendor_comment:
                    risk_details_data.append(["Vendor's Comment", vendor_comment])
                
                risk_details_table = Table(risk_details_data, colWidths=[1.5*inch, 4.5*inch])
                risk_details_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ]))
                
                elements.append(risk_details_table)
                
                # Add detailed actions if available
                if finding_rec and 'detailed_actions' in finding_rec:
                    elements.append(Spacer(1, 0.1*inch))
                    elements.append(Paragraph("Detailed Remediation Actions:", self.styles['Heading4']))
                    
                    for action in finding_rec['detailed_actions']:
                        elements.append(Paragraph(f"• {action}", self.styles['NormalIndent']))
        else:
            elements.append(Paragraph("No significant risks were identified during the assessment.", self.styles['Normal']))
        
        # Exceptions Noted
        elements.append(PageBreak())
        elements.append(Paragraph("Exceptions Noted", self.styles['Heading1']))
        
        # Generate exceptions text from findings and documentation review
        exceptions = []
        
        # Get exceptions from findings
        for finding in findings:
            if finding.get('level') in ['Critical', 'High', 'Medium']:
                exceptions.append(finding.get('description', ''))
        
        # Get exceptions from documentation review
        for item in doc_review_items:
            if "Exception noted" in item["exception"]:
                exceptions.append(f"{item['document']}: {item['remarks']}")
        
        # Add additional exceptions from assessment
        additional_exceptions = [
            "The vendor has mentioned that the parent company is SOC 2 Type 2 compliant. However, they have not provided the SOC report.",
            "It is mentioned that the data will not be destroyed on demand by the client but will be destroyed as per what is agreed in the client contract.",
            "The vendor does not participate in any privacy program or certification. However, the 27701 standard in ISO 27001 certification is on the roadmap during the next certification audit, starting in April 2025.",
            "Additionally, the vendor does not specifically mention public guidelines for law enforcement seeking access to customer data. It outlines the conditions under which personal information may be disclosed, including compliance with legal obligations such as court orders and government requests. However, it does not provide detailed public guidelines for law enforcement access."
        ]
        
        exceptions.extend(additional_exceptions)
        
        if exceptions:
            for exception in exceptions:
                elements.append(Paragraph(f"- {exception}", self.styles['Normal']))
                elements.append(Spacer(1, 0.1*inch))
        else:
            elements.append(Paragraph("No exceptions were noted during the assessment.", self.styles['Normal']))
        
        # Add missing documents section
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Additionally, the vendor did not submit the following documents:", self.styles['Normal']))
        
        missing_docs = [item["document"] for item in doc_review_items if item["status"] == "Not uploaded"]
        
        for i, doc in enumerate(missing_docs):
            elements.append(Paragraph(f"{i+1}. {doc}", self.styles['NormalIndent']))
        
        # Recommendation
        elements.append(PageBreak())
        elements.append(Paragraph("Recommendation", self.styles['Heading1']))
        
        # Generate recommendation based on risk level
        recommendation_text = f"""
        After conducting a comprehensive review of {vendor_name} on {datetime.now().strftime('%B %d, %Y')}, 
        it is evident that the vendor is aligned with the specific business requirements and goals of {self.company_name}. 
        The vendor has demonstrated cooperation by providing the required assessment documents and additional resources 
        regarding its IT policies and practices.
        
        After a thorough risk assessment, it is recommended that {self.company_name} 
        """
        
        if risk_level in ['Low', 'Medium-Low']:
            recommendation_text += f"approve the vendor as their offerings are aligned with {self.company_name}'s needs, and the identified risks can be effectively managed through strategic mitigation measures."
        elif risk_level in ['Medium', 'Medium-High']:
            recommendation_text += f"conditionally approve the vendor, contingent upon addressing the identified medium-risk issues within 90 days and implementing the recommended controls."
        else:
            recommendation_text += f"not proceed with this vendor until the critical and high-risk issues have been adequately addressed and a follow-up assessment confirms the implementation of required security controls."
        
        elements.append(Paragraph(recommendation_text, self.styles['Normal']))
        
        # Conclusion
        elements.append(PageBreak())
        elements.append(Paragraph("Conclusion", self.styles['Heading1']))
        
        # Generate conclusion based on assessment results
        majority_controls_aligned = True  # Assume majority controls aligned by default
        
        conclusion_text = f"""
        In conclusion, {"majority controls are" if majority_controls_aligned else "some controls are not"} aligned with {self.company_name}'s security standards. 
        """
        
        if findings:
            conclusion_text += f"As a result of the assessment, we identified {len(findings)} specific gaps. "
            
            finding_levels = [finding.get('level', 'Medium') for finding in findings]
            critical_count = sum(1 for level in finding_levels if level == 'Critical')
            high_count = sum(1 for level in finding_levels if level == 'High')
            medium_count = sum(1 for level in finding_levels if level == 'Medium')
            low_count = sum(1 for level in finding_levels if level == 'Low')
            
            level_counts = []
            if critical_count > 0:
                level_counts.append(f"{critical_count} critical")
            if high_count > 0:
                level_counts.append(f"{high_count} high")
            if medium_count > 0:
                level_counts.append(f"{medium_count} moderate")
            if low_count > 0:
                level_counts.append(f"{low_count} low")
            
            level_text = ", ".join(level_counts)
            conclusion_text += f"These include {level_text} risk issues. "
        else:
            conclusion_text += "No significant gaps were identified during the assessment. "
        
        conclusion_text += f"We have provided appropriate recommendations to mitigate these risks effectively. "
        conclusion_text += f"The vendor risk assigned to {vendor_name} is classified as {risk_level}, considering the nature of the products, services, and identified risk factors. "
        conclusion_text += f"By adhering to the assessment findings and recommendations, {self.company_name} can strengthen its vendor risk management practices and ensure the security of its systems and data.\n\n"
        conclusion_text += f"{self.company_name} is encouraged to refer to the detailed assessment report for a thorough analysis, tailored recommendations for each risk, and any additional requirements specific to the services provided."
        
        elements.append(Paragraph(conclusion_text, self.styles['Normal']))
        
        # Build the PDF document
        doc.build(elements)
        buffer.seek(0)
        
        return buffer.getvalue()

    def streamlit_download_button(self, assessment, vendor_name, logo_path=None):
        """
        Create a Streamlit download button for the PDF report
        
        Args:
            assessment: Risk assessment results
            vendor_name: Name of the vendor being assessed
            logo_path: Path to company logo image
            
        Returns:
            Streamlit download button
        """
        try:
            # Generate PDF
            pdf_bytes = self.create_pdf_report(assessment, vendor_name, logo_path)
            
            # Create a download button
            filename = f"{vendor_name.replace(' ', '_')}_Risk_Assessment_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            return st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error generating PDF report: {str(e)}")
            return None
            
def generate_pdf_report(assessment, vendor_name, company_name="Your Company", logo_path=None):
    """
    Generate a PDF risk assessment report using the RiskReportGenerator
    
    Args:
        assessment: Risk assessment results
        vendor_name: Name of the vendor being assessed
        company_name: Name of the company conducting the assessment
        logo_path: Path to company logo image
        
    Returns:
        PDF report as bytes
    """
    generator = RiskReportGenerator(company_name)
    return generator.create_pdf_report(assessment, vendor_name, logo_path)

def render_pdf_download_button(assessment, vendor_name, company_name="Your Company", logo_path=None):
    """
    Render a Streamlit download button for the PDF report
    
    Args:
        assessment: Risk assessment results
        vendor_name: Name of the vendor being assessed
        company_name: Name of the company conducting the assessment
        logo_path: Path to company logo image
        
    Returns:
        Streamlit download button
    """
    generator = RiskReportGenerator(company_name)
    return generator.streamlit_download_button(assessment, vendor_name, logo_path)