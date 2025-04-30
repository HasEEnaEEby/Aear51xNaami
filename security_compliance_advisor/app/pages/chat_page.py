import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

def render_chat_page(security_advisor=None):
    """
    Render the chat interface page
    
    Args:
        security_advisor: SecurityAdvisor instance
    """
    st.markdown('<h1 class="main-header">Security & Compliance Advisor</h1>', unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    # Input container
    input_container = st.container()
    
    # Render chat messages
    with chat_container:
        for message in st.session_state.conversation:
            render_chat_message(message)
    
    # Input for new message
    with input_container:
        col1, col2 = st.columns([5, 1])
        
        # Define a callback to handle message submission
        def handle_message_submit():
            user_input = st.session_state.chat_input
            if user_input and user_input != st.session_state.get('last_input', ''):
                # Save current input to avoid duplicate processing
                st.session_state.last_input = user_input
                
                # Add user message to conversation
                add_user_message(user_input)
                
                # Process message and generate response
                if security_advisor:
                    response = security_advisor.process_chat_message(
                        user_input, 
                        st.session_state.conversation,
                        st.session_state.assessment if 'assessment' in st.session_state else None
                    )
                    
                    add_bot_message(response['text'], response.get('data', {}))
                    
                    # Update assessment and recommendations if included in response
                    if 'risk_score' in response.get('data', {}):
                        st.session_state.assessment = response['data']
                    
                    if 'recommendations' in response.get('data', {}):
                        st.session_state.recommendations = response['data']['recommendations']
                else:
                    # Dummy response if security advisor not available
                    add_bot_message("I'm just a demo right now. A fully implemented chatbot would process your message.")
                
                # Clear input
                st.session_state.chat_input = ""
                
                # Rerun to update UI
                st.experimental_rerun()
        
        with col1:
            # Initialize session state for chat input if not exists
            if 'chat_input' not in st.session_state:
                st.session_state.chat_input = ""
                
            st.text_input(
                "Type your message...", 
                key="chat_input", 
                on_change=handle_message_submit
            )
        
        with col2:
            st.button("Send", on_click=handle_message_submit)

def render_chat_message(message):
    """
    Render a single chat message
    
    Args:
        message: Message dictionary with sender, message, and optional data
    """
    sender = message.get("sender", "bot")
    message_text = message.get("message", "")
    message_data = message.get("data", {})
    
    if sender == "user":
        st.markdown(f'<div class="chat-message user">{message_text}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message bot">{message_text}</div>', unsafe_allow_html=True)
        
        # Render any attached data visualizations
        if 'risk_score' in message_data:
            render_risk_score_card(message_data)
        
        if 'recommendations' in message_data and message_data['recommendations']:
            render_recommendations_preview(message_data['recommendations'][:3])

def render_risk_score_card(assessment_data):
    """
    Render risk score card
    
    Args:
        assessment_data: Assessment data dictionary
    """
    risk_score = assessment_data.get('risk_score', 0)
    risk_level = assessment_data.get('risk_level', {})
    risk_name = risk_level.get('name', 'Unknown')
    risk_color = risk_level.get('color', 'gray')
    
    # Format risk level with color
    risk_class = risk_name.replace(' ', '-').lower()
    
    st.markdown(f"""
    <div class="card">
        <h3>Security Risk Assessment</h3>
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div style="flex: 1; text-align: center;">
                <div style="font-size: 3rem; font-weight: bold; color: {risk_color};">{risk_score:.1f}</div>
                <div style="font-size: 1.2rem;">out of 100</div>
            </div>
            <div style="flex: 2; padding-left: 1rem;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">Risk Level: <span class="risk-{risk_class}">{risk_name.title()}</span></div>
                <div>{risk_level.get('description', '')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_recommendations_preview(recommendations):
    """
    Render preview of recommendations
    
    Args:
        recommendations: List of recommendation dictionaries
    """
    if not recommendations:
        return
    
    st.markdown("<h4>Top Recommendations</h4>", unsafe_allow_html=True)
    
    for rec in recommendations:
        impact_class = "high-impact" if rec.get('impact') == "High" else (
            "medium-impact" if rec.get('impact') == "Medium" else "low-impact"
        )
        
        st.markdown(f"""
        <div class="recommendation-card {impact_class}">
            <div style="font-weight: bold;">{rec.get('title', 'Recommendation')}</div>
            <div style="margin-top: 0.5rem;">{rec.get('description', '')}</div>
            <div style="margin-top: 0.5rem; font-size: 0.8rem;">
                <span style="margin-right: 1rem;">Impact: {rec.get('impact', 'Medium')}</span>
                <span>Effort: {rec.get('effort', 'Medium')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def add_user_message(message):
    """
    Add user message to conversation history
    
    Args:
        message: User message text
    """
    st.session_state.conversation.append({
        "sender": "user",
        "message": message,
        "timestamp": datetime.now().isoformat()
    })

def add_bot_message(message, data=None):
    """
    Add bot message to conversation history
    
    Args:
        message: Bot message text
        data: Optional data dictionary
    """
    st.session_state.conversation.append({
        "sender": "bot",
        "message": message,
        "data": data or {},
        "timestamp": datetime.now().isoformat()
    })