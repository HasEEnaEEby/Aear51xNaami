"""
Enhanced PDF Generator utility for Security Compliance Advisor
This module provides comprehensive PDF generation functionality for the application.
"""

import io
import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def generate_pdf_report(assessment, vendor_name, company_name="Your Company", 
                        include_explanations=True, include_recommendations=True, 
                        include_raw_findings=False, logo_path=None):
    """
    Generate a comprehensive PDF risk assessment report
    
    Args:
        assessment: Risk assessment results
        vendor_name: Name of the vendor being assessed
        company_name: Name of the company conducting the assessment
        include_explanations: Whether to include AI-generated risk explanations
        include_recommendations: Whether to include recommendations
        include_raw_findings: Whether to include raw findings data
        logo_path: Path to company logo image
        
    Returns:
        PDF report as bytes
    """
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                              rightMargin=0.5*inch, leftMargin=0.5*inch,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='Heading1Bold',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            spaceAfter=12
        ))
        
        styles.add(ParagraphStyle(
            name='Heading2Bold',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            spaceAfter=10
        ))
        
        styles.add(ParagraphStyle(
            name='NormalIndent',
            parent=styles['Normal'],
            leftIndent=20,
            fontSize=10
        ))
        
        # Extract vendor data if available in uploaded file
        try:
            vendor_details = assessment.get('vendor_details', {})
            if vendor_details:
                vendor_name = vendor_details.get('name', vendor_name)
                vendor_type = vendor_details.get('type', 'External Vendor')
                vendor_industry = vendor_details.get('industry', 'Technology')
                vendor_location = vendor_details.get('location', 'Unknown')
            else:
                vendor_type = 'External Vendor'
                vendor_industry = 'Technology'  
                vendor_location = 'Unknown'
        except Exception:
            vendor_type = 'External Vendor'
            vendor_industry = 'Technology'
            vendor_location = 'Unknown'
        
        # Add company logo if provided
        if logo_path:
            try:
                img = Image(logo_path, width=2*inch, height=0.75*inch)
                elements.append(img)
            except Exception as e:
                elements.append(Paragraph(f"Error loading logo: {str(e)}", styles['Normal']))
        
        # Add report title
        title = Paragraph(f"Third Party Risk Assessment Report", styles['Heading1Bold'])
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Add vendor name and date
        current_date = datetime.now().strftime('%B %d, %Y')
        vendor_info = Paragraph(f"VENDOR: {vendor_name.upper()}", styles['Heading2'])
        elements.append(vendor_info)
        elements.append(Paragraph(f"Assessment Date: {current_date}", styles['Normal']))
        elements.append(Paragraph(f"Prepared by: {company_name}", styles['Normal']))
        
        # Add vendor details table if available
        vendor_details_data = [
            ["Vendor Type", vendor_type],
            ["Industry", vendor_industry],
            ["Location", vendor_location]
        ]
        
        vendor_table = Table(vendor_details_data, colWidths=[1.5*inch, 4.5*inch])
        vendor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        
        elements.append(Spacer(1, 0.2*inch))
        elements.append(vendor_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Add overall risk rating
        risk_level = assessment.get('risk_level', 'Medium')
        risk_score = assessment.get('overall_risk_score', 0.5) * 100  # Convert to percentage
        
        elements.append(Paragraph("Overall Risk Rating", styles['Heading2Bold']))
        
        # Create risk rating table with color
        risk_color = get_risk_color(risk_level)
        risk_data = [
            ["Risk Level", "Risk Score"],
            [risk_level, f"{risk_score:.1f}%"]
        ]
        
        risk_table = Table(risk_data, colWidths=[2*inch, 2*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
            ('BACKGROUND', (0, 1), (0, 1), risk_color),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
            ('ALIGN', (0, 0), (1, 1), 'CENTER'),
            ('VALIGN', (0, 0), (1, 1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (1, 1), 0.5, colors.black),
        ]))
        
        elements.append(risk_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Table of Contents
        elements.append(Paragraph("Table of Contents", styles['Heading2Bold']))
        toc_items = [
            "1. Executive Summary",
            "2. Risk Assessment Methodology",
            "3. Framework Compliance Status"
        ]
        
        # Add conditional sections based on parameters
        if include_recommendations:
            toc_items.append("4. Key Recommendations")
            section_num = 5
        else:
            section_num = 4
            
        if include_explanations and 'explanations' in assessment:
            toc_items.append(f"{section_num}. Risk Analysis and Explanations")
            section_num += 1
            
        toc_items.append(f"{section_num}. Detailed Findings")
        section_num += 1
        
        if include_raw_findings:
            toc_items.append(f"{section_num}. Raw Assessment Data")
            section_num += 1
            
        toc_items.append(f"{section_num}. Conclusion")
        
        for item in toc_items:
            elements.append(Paragraph(item, styles['Normal']))
        
        elements.append(PageBreak())
        
        # Executive Summary
        elements.append(Paragraph("1. Executive Summary", styles['Heading2Bold']))
        
        # Create summary text from assessment data or use AI-generated if available
        if include_explanations and 'explanations' in assessment and 'executive_summary' in assessment['explanations']:
            exec_summary = assessment['explanations']['executive_summary']
            elements.append(Paragraph(exec_summary, styles['Normal']))
        else:
            # Generate a standard summary
            findings = assessment.get('findings', [])
            findings_count = len(findings)
            high_findings = sum(1 for f in findings if f.get('level') in ['Critical', 'High'])
            
            summary_text = f"""
            A comprehensive risk assessment of {vendor_name} was completed on {current_date}. 
            The vendor's security controls have been evaluated against {company_name}'s security standards.
            
            The overall vendor risk has been evaluated and classified as {risk_level} ({risk_score:.1f}%).
            
            The assessment identified {findings_count} security findings, of which {high_findings} were classified as Critical or High risk.
            """
            
            elements.append(Paragraph(summary_text, styles['Normal']))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Key Findings Overview
        findings = assessment.get('findings', [])
        if findings:
            elements.append(Paragraph("Key Findings Summary:", styles['Heading3']))
            
            # Create findings summary table
            findings_summary = [["Risk Level", "Count"]]
            
            # Count findings by risk level
            risk_counts = {
                "Critical": 0,
                "High": 0, 
                "Medium": 0,
                "Low": 0
            }
            
            for finding in findings:
                level = finding.get('level', 'Medium')
                if level in risk_counts:
                    risk_counts[level] += 1
                else:
                    risk_counts[level] = 1
            
            for level, count in risk_counts.items():
                if count > 0:  # Only show non-zero counts
                    findings_summary.append([level, str(count)])
            
            summary_table = Table(findings_summary, colWidths=[2*inch, 1*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
                ('ALIGN', (0, 0), (1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (1, -1), 0.5, colors.black),
            ]))
            
            elements.append(summary_table)
        
        elements.append(PageBreak())
        
        # Risk Assessment Methodology
        elements.append(Paragraph("2. Risk Assessment Methodology", styles['Heading2Bold']))
        
        methodology_text = """
        This risk assessment was conducted following industry standard methodologies and frameworks including 
        NIST SP 800-30 (Guide for Conducting Risk Assessments). Risks were evaluated by considering threat events, 
        their likelihood of occurrence, system vulnerabilities, mitigating factors, and the potential consequences.
        
        The assessment evaluates security controls across multiple domains including:
        • Access Control
        • Data Protection
        • Vulnerability Management
        • Network Security
        • Authentication
        • Encryption
        • Incident Response
        • Business Continuity
        
        Each risk is rated based on:
        • Impact: The potential harm that could result if the threat is realized
        • Likelihood: The probability that the threat will occur
        
        Risk scores are calculated by multiplying impact and likelihood values.
        """
        elements.append(Paragraph(methodology_text, styles['Normal']))
        
        # Add risk matrix
        elements.append(Paragraph("Risk Matrix", styles['Heading3']))
        risk_matrix = [
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
        
        matrix_table = Table(risk_matrix)
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
                cell_value = risk_matrix[i][j]
                if cell_value in cell_colors:
                    matrix_style.append(('BACKGROUND', (j, i), (j, i), cell_colors[cell_value]))
        
        matrix_table.setStyle(TableStyle(matrix_style))
        elements.append(matrix_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Framework Compliance Status
        elements.append(PageBreak())
        elements.append(Paragraph("3. Framework Compliance Status", styles['Heading2Bold']))
        
        # Extract framework compliance data
        framework_compliance = assessment.get('framework_compliance', {})
        
        if framework_compliance:
            # Create compliance table
            compliance_data = [["Framework", "Compliance Score", "Status"]]
            
            # Format framework names
            framework_names = {
                'iso27001': 'ISO 27001',
                'nist_csf': 'NIST CSF',
                'pci_dss': 'PCI DSS',
                'gdpr': 'GDPR',
                'hipaa': 'HIPAA',
                'ccpa': 'CCPA',
                'cis': 'CIS Controls',
                'hitrust': 'HITRUST CSF'
            }
            
            for framework_id, data in framework_compliance.items():
                framework_name = framework_names.get(framework_id, framework_id)
                compliance_score = data.get('compliance_score', 0)
                compliance_level = data.get('compliance_level', 'Unknown')
                
                compliance_data.append([framework_name, f"{compliance_score:.1f}%", compliance_level])
            
            compliance_table = Table(compliance_data, colWidths=[2*inch, 1.5*inch, 2*inch])
            compliance_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            
            elements.append(compliance_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Add compliance explanation
            compliance_text = """
            The compliance scores represent the percentage of controls that are fully or partially implemented 
            for each framework. Scores above 80% indicate substantial compliance, while scores below 60% 
            indicate significant gaps that should be addressed.
            """
            elements.append(Paragraph(compliance_text, styles['Normal']))
        else:
            elements.append(Paragraph("No framework compliance data available.", styles['Normal']))
        
        # Key Recommendations Section (conditional)
        if include_recommendations:
            elements.append(PageBreak())
            elements.append(Paragraph("4. Key Recommendations", styles['Heading2Bold']))
            
            # Get recommendations from assessment
            recommendations = assessment.get('recommendations', [])
            if recommendations:
                for i, rec in enumerate(recommendations):
                    priority = rec.get('priority', 'Medium')
                    title = rec.get('title', f'Recommendation {i+1}')
                    description = rec.get('description', '')
                    
                    elements.append(Paragraph(f"{i+1}. {title} ({priority} Priority)", styles['Heading3']))
                    elements.append(Paragraph(description, styles['Normal']))
                    
                    # Add detailed actions if available
                    detailed_actions = rec.get('detailed_actions', [])
                    if detailed_actions:
                        elements.append(Paragraph("Detailed Actions:", styles['Heading4']))
                        for action in detailed_actions:
                            elements.append(Paragraph(f"• {action}", styles['NormalIndent']))
                    
                    elements.append(Spacer(1, 0.2*inch))
            else:
                elements.append(Paragraph("No specific recommendations available.", styles['Normal']))
            
            # Set the section number for the next section
            section_num = 5
        else:
            section_num = 4
        
        # Risk Analysis and Explanations Section (conditional)
        if include_explanations and 'explanations' in assessment:
            elements.append(PageBreak())
            elements.append(Paragraph(f"{section_num}. Risk Analysis and Explanations", styles['Heading2Bold']))
            
            explanations = assessment['explanations']
            
            # Overall risk explanation
            if 'overall_risk' in explanations:
                elements.append(Paragraph("Overall Risk Assessment", styles['Heading3']))
                elements.append(Paragraph(explanations['overall_risk'].get('title', ''), styles['Heading4']))
                elements.append(Paragraph(explanations['overall_risk'].get('explanation', ''), styles['Normal']))
                elements.append(Spacer(1, 0.2*inch))
            
            # Domain-specific explanations
            if 'domain_explanations' in explanations:
                elements.append(Paragraph("Domain-Specific Risk Analysis", styles['Heading3']))
                
                for domain, data in explanations['domain_explanations'].items():
                    elements.append(Paragraph(f"{domain}: {data.get('title', '')}", styles['Heading4']))
                    elements.append(Paragraph(data.get('explanation', ''), styles['Normal']))
                    
                    # Related findings
                    if 'related_findings' in data and data['related_findings']:
                        elements.append(Paragraph("Key Findings:", styles['Heading4']))
                        for finding in data['related_findings']:
                            elements.append(Paragraph(f"• {finding}", styles['NormalIndent']))
                    
                    elements.append(Spacer(1, 0.2*inch))
            
            # Increment section number
            section_num += 1
        
        # Detailed Findings Section
        elements.append(PageBreak())
        elements.append(Paragraph(f"{section_num}. Detailed Findings", styles['Heading2Bold']))
        
        if findings:
            for i, finding in enumerate(findings):
                finding_title = finding.get('title', f'Finding {i+1}')
                finding_level = finding.get('level', 'Medium')
                finding_description = finding.get('description', '')
                finding_category = finding.get('category', 'General')
                
                # Calculate impact and likelihood if available
                impact = finding.get('impact', 3)
                likelihood = finding.get('likelihood', 3)
                risk_score = impact * likelihood
                
                elements.append(Paragraph(f"Finding {i+1}: {finding_title}", styles['Heading3']))
                
                # Create finding details table
                finding_data = [
                    ["Category", finding_category],
                    ["Risk Level", finding_level],
                    ["Impact", str(impact)],
                    ["Likelihood", str(likelihood)],
                    ["Risk Score", str(risk_score)]
                ]
                
                finding_table = Table(finding_data, colWidths=[1.5*inch, 4*inch])
                finding_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ]))
                
                elements.append(finding_table)
                elements.append(Spacer(1, 0.1*inch))
                
                elements.append(Paragraph("Description:", styles['Heading4']))
                elements.append(Paragraph(finding_description, styles['Normal']))
                elements.append(Spacer(1, 0.2*inch))
        else:
            elements.append(Paragraph("No specific findings were identified.", styles['Normal']))
        
        # Increment section number
        section_num += 1
        
        # Raw Assessment Data Section (conditional)
        if include_raw_findings:
            elements.append(PageBreak())
            elements.append(Paragraph(f"{section_num}. Raw Assessment Data", styles['Heading2Bold']))
            
            # Include risk by category data
            elements.append(Paragraph("Risk by Category", styles['Heading3']))
            
            risk_by_category = assessment.get('risk_by_category', {})
            if risk_by_category:
                category_data = [["Category", "Risk Score", "Risk Level"]]
                
                for category, data in risk_by_category.items():
                    score = data.get('score', 0) * 100  # Convert to percentage
                    level = data.get('risk_level', 'Medium')
                    category_data.append([category, f"{score:.1f}%", level])
                
                category_table = Table(category_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
                category_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ]))
                
                elements.append(category_table)
            else:
                elements.append(Paragraph("No risk by category data available.", styles['Normal']))
            
            # Increment section number
            section_num += 1
        
        # Conclusion Section
        elements.append(PageBreak())
        elements.append(Paragraph(f"{section_num}. Conclusion", styles['Heading2Bold']))
        
        conclusion_text = f"""
        Based on our comprehensive assessment, the overall security posture of {vendor_name} is considered {risk_level.lower()} risk.
        
        {"The recommendations provided should be implemented to reduce the security risk to an acceptable level." if include_recommendations else ""}
        
        {"The detailed risk explanations provide context for the findings and should be reviewed to understand the security implications." if include_explanations else ""}
        
        This assessment was conducted by {company_name} on {current_date}.
        """
        
        elements.append(Paragraph(conclusion_text, styles['Normal']))
        
        # Build the PDF document
        doc.build(elements)
        buffer.seek(0)
        
        return buffer.getvalue()
        
    except Exception as e:
        # Create a simple error report instead
        buffer = io.BytesIO()
        
        # Use a simpler approach with canvas directly
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1*inch, 10*inch, "Error Generating PDF Report")
        
        c.setFont("Helvetica", 12)
        c.drawString(1*inch, 9.5*inch, f"An error occurred while generating the PDF: {str(e)}")
        c.drawString(1*inch, 9*inch, f"Vendor: {vendor_name}")
        c.drawString(1*inch, 8.5*inch, f"Date: {datetime.now().strftime('%B %d, %Y')}")
        
        c.save()
        buffer.seek(0)
        
        return buffer.getvalue()

def get_risk_color(risk_level):
    """Get the color for a risk level"""
    if risk_level == "Critical":
        return colors.red
    elif risk_level == "High":
        return colors.orange
    elif risk_level in ["Medium", "Medium-Low"]:
        return colors.yellow
    else:  # Low
        return colors.lightgreen

def render_pdf_download_button(assessment, vendor_name, company_name="Your Company", 
                              include_explanations=True, include_recommendations=True, 
                              include_raw_findings=False, logo_path=None):
    """
    Render a Streamlit download button for the PDF report
    
    Args:
        assessment: Risk assessment results
        vendor_name: Name of the vendor being assessed
        company_name: Name of the company conducting the assessment
        include_explanations: Whether to include AI-generated risk explanations
        include_recommendations: Whether to include recommendations
        include_raw_findings: Whether to include raw findings data
        logo_path: Path to company logo image
        
    Returns:
        Streamlit download button
    """
    try:
        # Generate PDF
        pdf_bytes = generate_pdf_report(
            assessment, 
            vendor_name, 
            company_name,
            include_explanations,
            include_recommendations,
            include_raw_findings,
            logo_path
        )
        
        if not isinstance(pdf_bytes, bytes):
            st.error("PDF generation failed: invalid output format")
            return None
        
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