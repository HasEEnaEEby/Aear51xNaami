"""
Dashboard page for Security Compliance Advisor with PDF Report Generation
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os

from utils.pdf_generator import generate_pdf_report, render_pdf_download_button
from core.risk.explainable_risk_module import ExplainableRiskModule

def render_dashboard_page():
    """Render the dashboard page with risk assessment results"""
    if "assessment" not in st.session_state or st.session_state.assessment is None:
        render_empty_dashboard()
        return
    assessment = st.session_state.assessment
    recommendations = st.session_state.recommendations if "recommendations" in st.session_state else []

    if "explanations" not in assessment:
        st.info("Enriching assessment data with explanations...")
        explainable_risk = ExplainableRiskModule()
        assessment = explainable_risk.generate_risk_explanation(assessment)
        st.session_state.assessment = assessment
        st.success("Assessment enriched with explanations!")

    # Risk Summary Section
    col1, col2, col3 = st.columns([1, 1, 1])
    
    # Get risk data from assessment
    risk_score = assessment.get('overall_risk_score', 0.5) * 100  # Convert to percentage
    risk_level = assessment.get('risk_level', 'Medium')
    
    # Get framework compliance data
    framework_compliance = assessment.get('framework_compliance', {})
    avg_compliance = 0
    if framework_compliance:
        compliance_scores = [data.get('compliance_score', 0) for data in framework_compliance.values()]
        avg_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0
    
    # Count findings by severity
    findings = assessment.get('findings', [])
    high_count = sum(1 for f in findings if f.get('level') in ['Critical', 'High'])
    medium_count = sum(1 for f in findings if f.get('level') in ['Medium', 'Medium-Low'])
    low_count = sum(1 for f in findings if f.get('level') in ['Low'])
    
    with col1:
        st.markdown(f"""
        <div class="dashboard-card">
            <h3 class="card-header">Overall Risk Score</h3>
            <div class="dashboard-metric">{risk_score:.1f}%</div>
            <p>{risk_level} Risk Level</p>
            <div style="margin-top: 10px;">
                <div style="background-color: #FFB74D; height: 8px; width: {risk_score}%; border-radius: 4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="dashboard-card">
            <h3 class="card-header">Framework Compliance</h3>
            <div class="dashboard-metric">{avg_compliance:.1f}%</div>
            <p>Average compliance across frameworks</p>
            <div style="margin-top: 10px;">
                <div style="background-color: #3687d8; height: 8px; width: {avg_compliance}%; border-radius: 4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        total_findings = len(findings)
        st.markdown(f"""
        <div class="dashboard-card">
            <h3 class="card-header">Security Gaps</h3>
            <div class="dashboard-metric">{total_findings}</div>
            <p>Critical security areas needing attention</p>
            <div style="margin-top: 10px; display: flex; justify-content: space-between;">
                <span>🔴 High: {high_count}</span>
                <span>🟠 Medium: {medium_count}</span>
                <span>🟡 Low: {low_count}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Create tabs for different dashboard sections
    tab1, tab2, tab3, tab4 = st.tabs(["Risk Analysis", "Compliance", "Recommendations", "Risk Explanations"])
    
    with tab1:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        render_risk_analysis(assessment)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab2:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        render_compliance_section(assessment)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab3:
        render_recommendations_section(recommendations)
    
    with tab4:
        render_risk_explanations(assessment)
        
    # Add PDF report generation section
    st.markdown("---")
    st.markdown("## Generate Complete Risk Assessment Report")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Try to extract vendor name from questionnaire if available
        default_vendor_name = "Acme Corporation"
        try:
            # Extract from session state or questionnaire data if present
            if "questionnaire_data" in st.session_state and st.session_state.questionnaire_data:
                # Try to find vendor information in metadata
                metadata = st.session_state.questionnaire_data.get('metadata', {})
                if 'vendor_name' in metadata:
                    default_vendor_name = metadata.get('vendor_name')
                
                # Or from the uploaded filename if available
                elif "uploaded_file_name" in st.session_state and st.session_state.uploaded_file_name:
                    filename = st.session_state.uploaded_file_name
                    # Extract name from filename pattern like "Vendor_Name_Assessment.xlsx"
                    if '_' in filename:
                        parts = filename.split('_')
                        if len(parts) >= 2:
                            default_vendor_name = parts[0].replace('.', ' ').title()
        except Exception:
            # Fallback to default if extraction fails
            pass
        
        # Vendor name input with extracted default if available
        vendor_name = st.text_input("Vendor Name", value=default_vendor_name)
        
        # Company name input
        company_name = st.text_input("Your Company Name", value="Security Pal")
        
        # Report customization options
        st.markdown("### Report Options")
        include_explanations = st.checkbox("Include AI-generated risk explanations", value=True)
        include_recommendations = st.checkbox("Include recommendations", value=True)
        include_raw_findings = st.checkbox("Include raw findings data", value=False)
        
        # Generate PDF report button
        if st.button("Generate PDF Report"):
            try:
                with st.spinner("Generating PDF report..."):
                    # Ensure assessment has explanations before generating PDF
                    if include_explanations and "explanations" not in assessment:
                        explainable_risk = ExplainableRiskModule()
                        assessment = explainable_risk.generate_risk_explanation(assessment)
                        st.session_state.assessment = assessment
                    
                    # Add vendor details to assessment if not present
                    if "vendor_details" not in assessment:
                        assessment["vendor_details"] = {
                            "name": vendor_name,
                            "type": "External Vendor",
                            "industry": "Technology"
                        }
                    
                    # Generate the PDF report with options
                    pdf_bytes = generate_pdf_report(
                        assessment, 
                        vendor_name, 
                        company_name,
                        include_explanations=include_explanations,
                        include_recommendations=include_recommendations,
                        include_raw_findings=include_raw_findings
                    )
                    
                    # Create download button for the generated PDF
                    filename = f"{vendor_name.replace(' ', '_')}_Risk_Assessment_{datetime.now().strftime('%Y%m%d')}.pdf"
                    
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf"
                    )
                    
                    st.success("PDF report generated successfully!")
            except Exception as e:
                st.error(f"Error generating PDF report: {str(e)}")
                st.info("Please ensure you've uploaded and analyzed a questionnaire before generating a report.")
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-header">Risk Assessment Report</div>
            <p>Generate a comprehensive PDF risk assessment report that includes:</p>
            <ul>
                <li>Executive summary with key findings</li>
                <li>Detailed risk analysis with likelihood and impact assessments</li>
                <li>Framework compliance status</li>
                <li>Itemized security gaps and recommendations</li>
                <li>AI-generated risk explanations for deeper insights</li>
                <li>Documentation review and exceptions noted</li>
                <li>Risk matrix and scoring methodology</li>
            </ul>
            <p>This report follows industry standard risk assessment methodologies and is suitable for sharing with stakeholders and compliance teams.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show report quality enhancement tips
        st.markdown("""
        <div class="card mt-3">
            <div class="card-header">Tips for Better Reports</div>
            <p>To enhance the quality of your PDF report:</p>
            <ul>
                <li><strong>Include AI explanations</strong> for deeper context on risk findings</li>
                <li>Make sure to <strong>run the assessment</strong> first to generate comprehensive data</li>
                <li>Use the actual <strong>vendor name</strong> for better report readability</li>
                <li>Consider adding <strong>raw findings data</strong> for technical stakeholders</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


def render_empty_dashboard():
    """Render the dashboard when no assessment data is available"""
    st.markdown("""
    <div class="card">
        <div class="card-header">No Assessment Data Available</div>
        <p>Please upload and analyze a security questionnaire to view risk assessment results.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="dashboard-card">
        <h3 class="card-header">Get Started</h3>
        <p>Follow these steps to generate your security assessment:</p>
        <ol>
            <li>Go to the <b>Assessment Questionnaire</b> page</li>
            <li>Upload a security questionnaire file or use a template</li>
            <li>Run the risk assessment</li>
            <li>Return to this dashboard to view results</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample visualization of what the dashboard will look like
    st.markdown("### Sample Dashboard Preview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-header">Risk Domain Analysis</div>
            <p><i>Sample data visualization (upload a questionnaire to see your actual data)</i></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample risk domain data
        domains = ["Access Control", "Data Protection", "Vulnerability Management", "Network Security", "Incident Response"]
        values = [62, 48, 75, 85, 70]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=domains,
            y=values,
            marker_color=['#FFB74D' if v < 70 else '#4CAF50' for v in values],
            text=values,
            textposition='auto',
        ))
        
        fig.update_layout(
            title="Security Domain Scores",
            xaxis_title="",
            yaxis_title="Score (%)",
            template="plotly_dark",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(37, 50, 72, 0.0)',
            plot_bgcolor='rgba(37, 50, 72, 0.0)',
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-header">Framework Compliance</div>
            <p><i>Sample data visualization (upload a questionnaire to see your actual data)</i></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample framework compliance data
        frameworks = ["ISO 27001", "NIST CSF", "GDPR", "HIPAA", "PCI DSS"]
        compliance = [78, 65, 82, 73, 90]
        
        fig = px.line_polar(
            r=compliance, 
            theta=frameworks, 
            line_close=True,
            range_r=[0, 100],
            color_discrete_sequence=["#3687d8"]
        )
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            template="plotly_dark",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(37, 50, 72, 0.0)',
            plot_bgcolor='rgba(37, 50, 72, 0.0)',
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_risk_analysis(assessment):
    """Render the risk analysis section of the dashboard"""
    # Domain Risk Chart
    st.subheader("Security Domain Risk Analysis")
    
    # Extract risk by category from assessment
    risk_by_category = assessment.get('risk_by_category', {})
    
    if risk_by_category:
        # Prepare data for the chart
        domains = list(risk_by_category.keys())
        scores = [data.get('score', 0) * 100 for data in risk_by_category.values()]  # Convert to percentage
        
        # Ensure we have data to display
        if domains and scores:
            # Assign colors based on scores
            colors = []
            for score in scores:
                if score < 50:
                    colors.append('#f44336')  # Red
                elif score < 70:
                    colors.append('#ff9800')  # Orange
                else:
                    colors.append('#4caf50')  # Green
            
            # Create horizontal bar chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=domains,
                x=scores,
                orientation='h',
                marker_color=colors,
                text=[f"{s:.1f}%" for s in scores],
                textposition='auto',
                hoverinfo='text',
                hovertext=[f"{d}: {s:.1f}% score" for d, s in zip(domains, scores)]
            ))
            
            fig.update_layout(
                xaxis_title="Score (%)",
                yaxis=dict(
                    title="",
                    autorange="reversed"
                ),
                template="plotly_dark",
                height=400,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(range=[0, 100]),
                paper_bgcolor='rgba(37, 50, 72, 0.0)',
                plot_bgcolor='rgba(37, 50, 72, 0.0)',
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No domain risk data available for visualization.")
    else:
        # If no real data, display sample data
        domains = ["Data Protection", "Access Control", "Vulnerability Management", "Network Security", "Authentication", "Encryption"]
        scores = [42, 55, 75, 65, 80, 58]
        thresholds = [50, 70, 90]  # Red, Yellow, Green thresholds
        
        # Assign colors based on thresholds
        colors = []
        for score in scores:
            if score < thresholds[0]:
                colors.append('#f44336')
            elif score < thresholds[1]:
                colors.append('#ff9800')
            else:
                colors.append('#4caf50')
        
        # Create horizontal bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=domains,
            x=scores,
            orientation='h',
            marker_color=colors,
            text=[f"{s}%" for s in scores],
            textposition='auto',
            hoverinfo='text',
            hovertext=[f"{d}: {s}% score" for d, s in zip(domains, scores)]
        ))
        
        fig.update_layout(
            xaxis_title="Score (%)",
            yaxis=dict(
                title="",
                autorange="reversed"
            ),
            template="plotly_dark",
            height=400,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(range=[0, 100]),
            paper_bgcolor='rgba(37, 50, 72, 0.0)',
            plot_bgcolor='rgba(37, 50, 72, 0.0)',
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Risk Categories and Controls
    st.subheader("Top Risk Areas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Display top 2 risk areas from assessment data if available
        if risk_by_category:
            # Sort categories by score (ascending) to get the highest risk areas
            sorted_categories = sorted(risk_by_category.items(), key=lambda x: x[1].get('score', 1))
            
            # Display top 2 risk areas (or less if not enough data)
            for i in range(min(2, len(sorted_categories))):
                category, data = sorted_categories[i]
                score = data.get('score', 0) * 100  # Convert to percentage
                
                # Set color based on score
                if score < 50:
                    color = "#f44336"  # Red
                elif score < 70:
                    color = "#ff9800"  # Orange
                else:
                    color = "#4caf50"  # Green
                
                # Get key issues
                key_issues = data.get('key_issues', [])
                if not key_issues:
                    key_issues = ["No specific issues identified"]
                
                st.markdown(f"""
                <div class="card">
                    <div class="card-header">{category}</div>
                    <div style="color: {color}; font-size: 24px; font-weight: bold; margin: 10px 0;">{score:.1f}%</div>
                    <p><b>Key Issues:</b></p>
                    <ul>
                        {"".join(f"<li>{issue}</li>" for issue in key_issues[:3])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Display sample data
            st.markdown("""
            <div class="card">
                <div class="card-header">Data Protection</div>
                <div style="color: #f44336; font-size: 24px; font-weight: bold; margin: 10px 0;">42%</div>
                <p><b>Key Issues:</b></p>
                <ul>
                    <li>No data encryption at rest</li>
                    <li>Weak data classification policies</li>
                    <li>Limited data loss prevention controls</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="card">
                <div class="card-header">Access Control</div>
                <div style="color: #ff9800; font-size: 24px; font-weight: bold; margin: 10px 0;">55%</div>
                <p><b>Key Issues:</b></p>
                <ul>
                    <li>Incomplete privileged access management</li>
                    <li>No regular access review process</li>
                    <li>Inconsistent least privilege implementation</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-header">Risk Matrix</div>
            <p>Interactive risk matrix showing impact vs. likelihood:</p>
        </div>
        """, unsafe_allow_html=True)
        
        impact = ['Negligible(1)', 'Minor(2)', 'Major(3)', 'Severe(4)', 'Catastrophic(5)']
        likelihood = ['Rare(1)', 'Unlikely(2)', 'Possible(3)', 'Probable(4)', 'Certain(5)']
        
        risk_scores = [
            [1, 2, 3, 4, 5],   # Negligible impact
            [2, 4, 6, 8, 10],  # Minor impact
            [3, 6, 9, 12, 15], # Major impact
            [4, 8, 12, 16, 20], # Severe impact
            [5, 10, 15, 20, 25]  # Catastrophic impact
        ]
        
        # Create a heatmap
        fig = go.Figure(data=go.Heatmap(
            z=risk_scores,
            x=likelihood,
            y=impact,
            colorscale=[
                [0, 'green'],
                [0.3, 'yellow'],
                [0.6, 'orange'],
                [1, 'red']
            ],
            showscale=True,
            colorbar=dict(
                title="Risk Score",
                tickvals=[1, 7, 13, 19, 25],
                ticktext=["Low", "Medium-Low", "Medium", "High", "Critical"]
            ),
            text=risk_scores,
            texttemplate="%{text}",
            textfont={"size": 14},
        ))
        
        fig.update_layout(
            title="Risk Assessment Matrix",
            xaxis_title="Likelihood",
            yaxis_title="Impact",
            template="plotly_dark", 
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(37, 50, 72, 0.0)',
            plot_bgcolor='rgba(37, 50, 72, 0.0)',
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_risk_explanations(assessment):
    """Render the AI-generated risk explanations section of the dashboard"""
    st.subheader("AI-Generated Risk Analysis & Explanations")
    
    # Check if explanations exist in the assessment
    explanations = assessment.get('explanations', {})
    
    if explanations:
        # Display overall risk explanation
        if 'overall_risk' in explanations:
            st.markdown("""
            <div class="card">
                <div class="card-header">Overall Risk Assessment</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**{explanations['overall_risk']['title']}**")
            st.markdown(explanations['overall_risk']['explanation'])
        
        # Display domain-specific explanations
        if 'domain_explanations' in explanations and explanations['domain_explanations']:
            st.markdown("""
            <div class="card">
                <div class="card-header">Domain-Specific Risk Analysis</div>
            </div>
            """, unsafe_allow_html=True)
            
            for domain, data in explanations['domain_explanations'].items():
                with st.expander(f"{domain}: {data.get('title', 'Risk Analysis')}"):
                    st.markdown(data.get('explanation', 'No explanation available.'))
                    
                    # Display any related findings
                    if 'related_findings' in data and data['related_findings']:
                        st.markdown("**Key Findings:**")
                        for finding in data['related_findings']:
                            st.markdown(f"- {finding}")
        
        # Display compliance gap explanations
        if 'compliance_gaps' in explanations and explanations['compliance_gaps']:
            st.markdown("""
            <div class="card">
                <div class="card-header">Compliance Gap Analysis</div>
            </div>
            """, unsafe_allow_html=True)
            
            for framework, data in explanations['compliance_gaps'].items():
                with st.expander(f"{framework}: {data.get('title', 'Gap Analysis')}"):
                    st.markdown(data.get('explanation', 'No explanation available.'))
                    
                    # Display key controls
                    if 'key_controls' in data and data['key_controls']:
                        st.markdown("**Key Controls to Implement:**")
                        for control in data['key_controls']:
                            st.markdown(f"- {control}")
        
        # Display actionable insights
        if 'actionable_insights' in explanations and explanations['actionable_insights']:
            st.markdown("""
            <div class="card">
                <div class="card-header">Actionable Security Insights</div>
            </div>
            """, unsafe_allow_html=True)
            
            for insight in explanations['actionable_insights']:
                st.markdown(f"- **{insight['title']}**: {insight['description']}")
    else:
        # Display sample data if no explanations are available
        st.info("No AI-generated risk explanations available. Run the assessment with the Explainable Risk Module to generate insights.")
        
        st.markdown("""
        <div class="card">
            <div class="card-header">How Explainable Risk Analysis Works</div>
            <p>The Explainable Risk Module analyzes your security assessment data and provides:</p>
            <ul>
                <li>Contextual analysis of security gaps and their business impact</li>
                <li>Correlation between different security controls and risk areas</li>
                <li>Compliance-specific insights based on industry frameworks</li>
                <li>Prioritized recommendations with clear rationale</li>
                <li>Technical and business-oriented explanations for stakeholders</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample explanation
        st.markdown("""
        <div style="background-color: rgba(54, 135, 216, 0.1); padding: 15px; border-radius: 4px; margin-top: 15px;">
            <h4>Sample AI-Generated Risk Insight</h4>
            <p>Your organization's highest risk area is Data Protection (42% score), primarily due to the lack of encryption for data at rest and inconsistent data classification. This creates significant compliance gaps in frameworks like PCI DSS (requirement 3.4) and GDPR (Article 32), which explicitly require encryption for sensitive data.</p>
            <p>The lack of encryption correlates with weaknesses in your key management practices and creates downstream risks in your backup and recovery processes. Based on industry benchmarks, implementing encryption at rest would reduce your overall risk score by approximately a 15% and improve compliance scores across multiple frameworks.</p>
            <p>Recommended implementation approach: Start with encrypting the most sensitive data categories (PII, financial data) using industry-standard encryption (AES-256), then expand to other data types based on your classification scheme.</p>
        </div>
        """, unsafe_allow_html=True)

def render_compliance_section(assessment):
    """Render the compliance section of the dashboard"""
    st.subheader("Framework Compliance")
    
    # Extract framework compliance data from the assessment
    framework_compliance = assessment.get('framework_compliance', {})
    
    if framework_compliance:
        # Get frameworks and their compliance scores
        frameworks = []
        compliance_scores = []
        
        for framework_id, data in framework_compliance.items():
            # Format framework name for display
            framework_name = {
                'iso27001': 'ISO 27001',
                'nist_csf': 'NIST CSF',
                'pci_dss': 'PCI DSS',
                'gdpr': 'GDPR',
                'hipaa': 'HIPAA',
                'ccpa': 'CCPA',
                'cis': 'CIS Controls',
                'hitrust': 'HITRUST CSF'
            }.get(framework_id, framework_id)
            
            frameworks.append(framework_name)
            compliance_scores.append(data.get('compliance_score', 0))
        
        if frameworks and compliance_scores:
            # Radar chart for framework compliance
            fig = px.line_polar(
                r=compliance_scores,
                theta=frameworks,
                line_close=True,
                range_r=[0, 100],
                color_discrete_sequence=["#3687d8"]
            )
            
            fig.update_traces(fill='toself', opacity=0.7)
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                template="plotly_dark",
                height=500,
                margin=dict(l=60, r=60, t=20, b=20),
                paper_bgcolor='rgba(37, 50, 72, 0.0)',
                plot_bgcolor='rgba(37, 50, 72, 0.0)',
            )
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("""
                <div class="card">
                    <div class="card-header">Compliance Details</div>
                    <p>Assessment against major security frameworks:</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display compliance details for each framework
                for framework, score in zip(frameworks, compliance_scores):
                    color = "#f44336" if score < 60 else "#ff9800" if score < 80 else "#4caf50"
                    st.markdown(f"""
                    <div style="margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 500;">{framework}</span>
                            <span style="color: {color}; font-weight: bold;">{score:.1f}%</span>
                        </div>
                        <div style="width: 100%; background-color: #1a2234; height: 6px; border-radius: 3px; margin-top: 5px;">
                            <div style="width: {score}%; background-color: {color}; height: 6px; border
                            <div style="width: {score}%; background-color: {color}; height: 6px; border-radius: 3px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No framework compliance data available for visualization.")
    else:
        # Display sample data if no real data
        frameworks = ["ISO 27001", "NIST CSF", "GDPR", "HIPAA", "PCI DSS", "CCPA", "CIS", "SOC 2"]
        compliance_scores = [73, 67, 83, 76, 92, 65, 70, 80]
        
        # Radar chart for framework compliance
        fig = px.line_polar(
            r=compliance_scores,
            theta=frameworks,
            line_close=True,
            range_r=[0, 100],
            color_discrete_sequence=["#3687d8"]
        )
        
        fig.update_traces(fill='toself', opacity=0.7)
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            template="plotly_dark",
            height=500,
            margin=dict(l=60, r=60, t=20, b=20),
            paper_bgcolor='rgba(37, 50, 72, 0.0)',
            plot_bgcolor='rgba(37, 50, 72, 0.0)',
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("""
            <div class="card">
                <div class="card-header">Compliance Details</div>
                <p>Assessment against major security frameworks:</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display compliance details for each framework
            for framework, score in zip(frameworks, compliance_scores):
                color = "#f44336" if score < 60 else "#ff9800" if score < 80 else "#4caf50"
                st.markdown(f"""
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 500;">{framework}</span>
                        <span style="color: {color}; font-weight: bold;">{score}%</span>
                    </div>
                    <div style="width: 100%; background-color: #1a2234; height: 6px; border-radius: 3px; margin-top: 5px;">
                        <div style="width: {score}%; background-color: {color}; height: 6px; border-radius: 3px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Control coverage by category
    st.subheader("Control Coverage by Category")
    
    # Create control coverage data
    categories = ["Identity & Access Management", "Data Protection", "Network Security", 
                "Encryption", "Incident Response", "Business Continuity", "Third-Party Risk"]
    iso_coverage = [85, 65, 90, 70, 80, 60, 75]
    nist_coverage = [75, 60, 85, 65, 70, 55, 60]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories,
        y=iso_coverage,
        name='ISO 27001',
        marker_color='#3687d8',
        opacity=0.7
    ))
    
    fig.add_trace(go.Bar(
        x=categories,
        y=nist_coverage,
        name='NIST CSF',
        marker_color='#ffb74d',
        opacity=0.7
    ))
    
    fig.update_layout(
        xaxis_title="Control Categories",
        yaxis_title="Coverage (%)",
        barmode='group',
        template="plotly_dark",
        height=400,
        margin=dict(l=20, r=20, t=20, b=80),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        paper_bgcolor='rgba(37, 50, 72, 0.0)',
        plot_bgcolor='rgba(37, 50, 72, 0.0)',
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_recommendations_section(recommendations):
    """Render the recommendations section of the dashboard"""
    st.subheader("Security Recommendations")
    
    # If we have real recommendations, display them
    if recommendations and len(recommendations) > 0:
        for i, rec in enumerate(recommendations):
            priority = rec.get('priority', 'Medium')
            category = rec.get('category', 'General')
            title = rec.get('title', f'Recommendation {i+1}')
            description = rec.get('description', 'No description provided.')
            
            # Set color based on priority
            color = {
                'High': '#f44336',
                'Medium': '#ff9800',
                'Low': '#4caf50'
            }.get(priority, '#ff9800')
            
            with st.expander(f"{title}"):
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 4px; margin-right: 10px;">
                        {priority} Priority
                    </div>
                    <div style="background-color: rgba(54, 135, 216, 0.2); color: #3687d8; padding: 3px 8px; border-radius: 4px;">
                        {category}
                    </div>
                </div>
                
                <p><b>Description:</b> {description}</p>
                """, unsafe_allow_html=True)
                
                # Display detailed actions if available
                if 'detailed_actions' in rec and rec['detailed_actions']:
                    st.markdown("<p><b>Detailed Actions:</b></p>", unsafe_allow_html=True)
                    for action in rec['detailed_actions']:
                        st.markdown(f"- {action}")
                
                # Display AI-enhanced recommendations if available
                if 'ai_insights' in rec and rec['ai_insights']:
                    st.markdown(f"""
                    <div style="background-color: rgba(54, 135, 216, 0.1); padding: 10px; border-radius: 4px; margin-top: 15px;">
                        <p><b>AI-Enhanced Insight:</b> {rec['ai_insights']}</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        # Display message if no recommendations available
        st.info("No recommendations available. Run the risk assessment to generate recommendations.")
        
        # Sample recommendation for display purposes
        st.markdown("""
        <div class="card">
            <div class="card-header">Sample Recommendation</div>
            <p><i>This is an example of what recommendations will look like once generated.</i></p>
            <div style="display: flex; align-items: center; margin: 10px 0;">
                <div style="background-color: #f44336; color: white; padding: 3px 8px; border-radius: 4px; margin-right: 10px;">
                    High Priority
                </div>
                <div style="background-color: rgba(54, 135, 216, 0.2); color: #3687d8; padding: 3px 8px; border-radius: 4px;">
                    Data Protection
                </div>
            </div>
            <p><b>Implement Data Encryption at Rest</b></p>
            <p>Encrypt sensitive data at rest using industry-standard encryption algorithms to protect data from unauthorized access in case of storage media compromise.</p>
            <p><b>Detailed Actions:</b></p>
            <ul>
                <li>Inventory and classify all sensitive data</li>
                <li>Implement AES-256 encryption for sensitive data</li>
                <li>Establish proper key management procedures</li>
                <li>Verify encryption implementation with security testing</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)