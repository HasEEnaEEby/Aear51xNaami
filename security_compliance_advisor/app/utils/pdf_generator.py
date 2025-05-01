"""
PDF Generator utility for Security Compliance Advisor
This module provides PDF generation functionality for the application.
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

def generate_pdf_report(assessment, vendor_name, company_name="Your Company", logo_path=None):
    """
    Generate a PDF risk assessment report
    
    Args:
        assessment: Risk assessment results
        vendor_name: Name of the vendor being assessed
        company_name: Name of the company conducting the assessment
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
            name='NormalIndent',
            parent=styles['Normal'],
            leftIndent=20,
            fontSize=10
        ))
        
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
        
        # Add vendor name
        vendor_info = Paragraph(f"VENDOR: {vendor_name.upper()}", styles['Heading2'])
        elements.append(vendor_info)
        elements.append(Spacer(1, 0.1*inch))
        
        # Add overall risk rating
        risk_level = assessment.get('risk_level', 'Medium')
        risk_score = assessment.get('overall_risk_score', 0.5) * 100  # Convert to percentage
        
        elements.append(Paragraph("Overall Risk Rating", styles['Heading3']))
        elements.append(Paragraph(f"Risk Level: {risk_level}", styles['Normal']))
        elements.append(Paragraph(f"Risk Score: {risk_score:.1f}%", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Add executive summary
        elements.append(Paragraph("Executive Summary", styles['Heading3']))
        
        # Create summary text from assessment data
        findings = assessment.get('findings', [])
        findings_count = len(findings)
        high_findings = sum(1 for f in findings if f.get('level') in ['Critical', 'High'])
        
        summary_text = f"""
        A comprehensive risk assessment of {vendor_name} was completed on {datetime.now().strftime('%B %d, %Y')}. 
        The vendor's security controls have been evaluated against {company_name}'s security standards.
        
        The overall vendor risk has been evaluated and classified as {risk_level} ({risk_score:.1f}%).
        
        The assessment identified {findings_count} security findings, of which {high_findings} were classified as Critical or High risk.
        """
        
        elements.append(Paragraph(summary_text, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Add recommendations section
        elements.append(Paragraph("Key Recommendations", styles['Heading3']))
        
        # Get recommendations from assessment
        recommendations = assessment.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations[:5]):  # Show top 5 recommendations
                rec_text = f"{i+1}. {rec.get('title', '')}: {rec.get('description', '')}"
                elements.append(Paragraph(rec_text, styles['NormalIndent']))
                elements.append(Spacer(1, 0.1*inch))
        else:
            elements.append(Paragraph("No specific recommendations available.", styles['Normal']))
        
        # Add findings section
        elements.append(PageBreak())
        elements.append(Paragraph("Detailed Findings", styles['Heading2']))
        
        if findings:
            for i, finding in enumerate(findings):
                finding_title = finding.get('title', f'Finding {i+1}')
                finding_level = finding.get('level', 'Medium')
                finding_description = finding.get('description', '')
                
                elements.append(Paragraph(f"Finding {i+1}: {finding_title}", styles['Heading3']))
                elements.append(Paragraph(f"Risk Level: {finding_level}", styles['Normal']))
                elements.append(Paragraph(f"Description: {finding_description}", styles['Normal']))
                elements.append(Spacer(1, 0.2*inch))
        else:
            elements.append(Paragraph("No specific findings were identified.", styles['Normal']))
        
        # Conclusion
        elements.append(PageBreak())
        elements.append(Paragraph("Conclusion", styles['Heading2']))
        
        conclusion_text = f"""
        Based on our assessment, the overall security posture of {vendor_name} is considered {risk_level.lower()} risk.
        The recommendations provided should be implemented to reduce the security risk to an acceptable level.
        
        This assessment was conducted by {company_name} on {datetime.now().strftime('%B %d, %Y')}.
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
    try:
        # Generate PDF
        pdf_bytes = generate_pdf_report(assessment, vendor_name, company_name, logo_path)
        
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