import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

def render_dashboard_page():
    """
    Render the risk assessment dashboard page
    
    This function displays the main risk assessment dashboard with metrics,
    risk breakdown charts, recommendations, and compliance impact information.
    """
    st.markdown('<h1 class="main-header">Risk Assessment Dashboard</h1>', unsafe_allow_html=True)
    
    # Check if assessment is available
    if not st.session_state.assessment:
        _display_no_assessment_warning()
        return
    
    # Get assessment data
    assessment = st.session_state.assessment
    risk_score = assessment.get('risk_score', 0)
    risk_level = assessment.get('risk_level', {})
    explanation = assessment.get('explanation', {})
    recommendations = st.session_state.recommendations if 'recommendations' in st.session_state else []
    framework_compliance = assessment.get('framework_compliance', {})
    category_scores = assessment.get('category_scores', {})
    
    # Display dashboard sections
    _display_summary_metrics(risk_score, risk_level, explanation, recommendations)
    _display_risk_breakdown_and_recommendations(explanation, recommendations)
    _display_compliance_impact(framework_compliance)

def _display_no_assessment_warning():
    """Show warning and guidance when no assessment is available"""
    st.warning("No risk assessment data available. Please complete the questionnaire or chat with the advisor to get a risk assessment.")
    
    if st.button("Go to Questionnaire"):
        st.session_state.current_page = 'questionnaire'
        st.experimental_rerun()

def _display_summary_metrics(risk_score, risk_level, explanation, recommendations):
    """
    Display the summary metrics cards at the top of the dashboard
    
    Args:
        risk_score: Overall risk score
        risk_level: Risk level dictionary with name, description, color
        explanation: Risk explanation dictionary with factors
        recommendations: List of recommendation dictionaries
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card(
            "Risk Score", 
            f"{risk_score:.1f}", 
            "/100", 
            risk_level.get('color', '#6B7280')
        )
    
    with col2:
        risk_factors = len(explanation.get('top_factors', []))
        render_metric_card(
            "Risk Factors", 
            f"{risk_factors}", 
            "Identified", 
            "#1E40AF"
        )
    
    with col3:
        rec_count = len(recommendations)
        render_metric_card(
            "Recommendations", 
            f"{rec_count}", 
            "Actions", 
            "#059669"
        )
    
    with col4:
        # Calculate potential improvement (this is an estimate)
        potential_improvement = min(100, risk_score * 0.3)
        render_metric_card(
            "Potential Improvement", 
            f"{potential_improvement:.1f}", 
            "Points", 
            "#D97706"
        )

def _display_risk_breakdown_and_recommendations(explanation, recommendations):
    """
    Display the risk breakdown charts and prioritized recommendations
    
    Args:
        explanation: Risk explanation dictionary with factors and categories
        recommendations: List of recommendation dictionaries
    """
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown('<h2 class="sub-header">Risk Breakdown</h2>', unsafe_allow_html=True)
        
        # Display risk factors chart
        if explanation.get('top_factors'):
            render_risk_factors_chart(explanation['top_factors'])
        
        # Display risk categories chart
        categories = explanation.get('categories', {})
        if categories:
            render_risk_categories_chart(categories)
    
    with col2:
        st.markdown('<h2 class="sub-header">Prioritized Actions</h2>', unsafe_allow_html=True)
        
        if recommendations:
            render_recommendations_list(recommendations[:10])
        else:
            st.info("No recommendations available. Please chat with the advisor to get personalized recommendations.")

def _display_compliance_impact(framework_compliance):
    """
    Display the compliance impact section
    
    Args:
        framework_compliance: Dictionary of framework compliance data
    """
    st.markdown('<h2 class="sub-header">Compliance Impact</h2>', unsafe_allow_html=True)
    render_compliance_impact(framework_compliance)

def render_metric_card(label, value, suffix, color):
    """
    Render a metric card with value and label
    
    Args:
        label: Metric label
        value: Metric value
        suffix: Text to show after value
        color: Color for the value
    """
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: {color};">{value}<span style="font-size: 1rem; color: #6B7280;">{suffix}</span></div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def render_risk_factors_chart(factors):
    """
    Render horizontal bar chart showing risk factors
    
    Args:
        factors: List of risk factors with impact values
    """
    # Sort factors by impact
    factors = sorted(factors, key=lambda x: x['impact'])
    
    # Take top/bottom factors
    display_factors = []
    
    # Add negative factors (ones that decrease risk)
    neg_factors = [f for f in factors if f['impact'] < 0]
    if neg_factors:
        display_factors.extend(neg_factors[:3])
    
    # Add positive factors (ones that increase risk)
    pos_factors = [f for f in factors if f['impact'] > 0]
    if pos_factors:
        display_factors.extend(pos_factors[-5:])
    
    # Create chart data
    labels = [f"{f['description'][:30]}..." if len(f['description']) > 30 else f['description'] for f in display_factors]
    values = [f['impact'] for f in display_factors]
    colors = ['#059669' if v < 0 else '#DC2626' for v in values]
    
    # Create Plotly horizontal bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=labels,
        x=values,
        orientation='h',
        marker_color=colors
    ))
    
    fig.update_layout(
        title="Top Risk Factors",
        xaxis_title="Impact on Risk Score",
        height=400,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_risk_categories_chart(categories):
    """
    Render pie chart showing risk by category
    
    Args:
        categories: Dictionary of risk categories with factors
    """
    # Calculate total impact by category
    category_impact = {}
    
    for category, factors in categories.items():
        total_impact = sum(f['impact'] for f in factors if f['impact'] > 0)
        if total_impact > 0:
            category_impact[category] = total_impact
    
    # Sort and prepare data
    sorted_categories = sorted(category_impact.items(), key=lambda x: x[1], reverse=True)
    
    # Take top 5 categories
    top_categories = sorted_categories[:5]
    
    # Prepare chart data
    labels = [c[0] for c in top_categories]
    values = [c[1] for c in top_categories]
    
    # Create Plotly pie chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.4,
        marker_colors=px.colors.qualitative.Set2
    )])
    
    fig.update_layout(
        title="Risk by Category",
        height=350,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_recommendations_list(recommendations):
    """
    Render expandable list of recommendations
    
    Args:
        recommendations: List of recommendation dictionaries
    """
    for i, rec in enumerate(recommendations):
        impact_class = "high-impact" if rec.get('impact') == "High" else (
            "medium-impact" if rec.get('impact') == "Medium" else "low-impact"
        )
        
        expander = st.expander(f"{i+1}. {rec.get('title', 'Recommendation')}")
        
        with expander:
            st.markdown(f"""
            <div class="recommendation-card {impact_class}" style="border-left-width: 8px;">
                <div style="font-size: 1.1rem; font-weight: bold;">{rec.get('title', 'Recommendation')}</div>
                <div style="margin-top: 0.8rem;">{rec.get('description', '')}</div>
                <div style="margin-top: 1rem; display: flex; justify-content: space-between;">
                    <div>
                        <span style="font-weight: bold;">Impact:</span> {rec.get('impact', 'Medium')}
                    </div>
                    <div>
                        <span style="font-weight: bold;">Effort:</span> {rec.get('effort', 'Medium')}
                    </div>
                    <div>
                        <span style="font-weight: bold;">Category:</span> {rec.get('category', 'General')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_compliance_impact(framework_compliance):
    """
    Render compliance impact section with coverage chart
    
    Args:
        framework_compliance: Dictionary of framework compliance data
    """
    # Get frameworks and their coverage from session state or compliance data
    frameworks = []
    framework_names = []
    coverage = []
    
    if 'frameworks' in st.session_state:
        for framework_id, framework in st.session_state.frameworks.items():
            frameworks.append(framework_id)
            framework_names.append(framework['name'])
            
            if framework_compliance and framework_id in framework_compliance:
                coverage.append(framework_compliance[framework_id].get('compliance_score', 0))
            else:
                coverage.append(0)
    else:
        # Fallback to example data if no frameworks in session state
        framework_names = ["ISO 27001", "NIST 800-53", "HIPAA", "GDPR", "PCI DSS"]
        coverage = [65, 78, 42, 59, 71]
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Create horizontal bar chart for compliance coverage
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=coverage,
            y=framework_names,
            orientation='h',
            marker_color='#1E40AF',
            text=[f"{c:.1f}%" for c in coverage],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Compliance Coverage",
            xaxis_title="Coverage Percentage",
            xaxis=dict(
                tickmode='array',
                tickvals=[0, 25, 50, 75, 100],
                range=[0, 100]
            ),
            height=300,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>Compliance Gap Analysis</h3>
            <p>The chart shows your estimated compliance coverage based on your risk assessment. This is not a full compliance audit but provides an indication of how well your security controls align with major frameworks.</p>
            <p>For a detailed compliance assessment, use the chat to explore specific framework requirements.</p>
        </div>
        """, unsafe_allow_html=True)

        # Display gap areas if available
        if framework_compliance:
            _display_compliance_gaps(framework_compliance, frameworks)

def _display_compliance_gaps(framework_compliance, frameworks):
    """
    Display compliance gap areas for the frameworks
    
    Args:
        framework_compliance: Dictionary of framework compliance data
        frameworks: List of framework IDs
    """
    gap_found = False
    
    for framework_id in frameworks:
        if framework_id in framework_compliance and 'gap_areas' in framework_compliance[framework_id]:
            gap_areas = framework_compliance[framework_id]['gap_areas']
            
            if gap_areas:
                if not gap_found:
                    st.markdown("<h4>Key Compliance Gaps</h4>", unsafe_allow_html=True)
                    gap_found = True
                
                framework_name = st.session_state.frameworks[framework_id]['name'] if framework_id in st.session_state.frameworks else framework_id
                
                st.markdown(f"**{framework_name}**")
                
                for gap in gap_areas[:3]:  # Show top 3 gaps
                    category = gap.get('category', '').replace('_', ' ').title()
                    st.markdown(f"- {category}")