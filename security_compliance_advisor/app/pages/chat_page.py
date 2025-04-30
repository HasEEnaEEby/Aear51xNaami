"""
Chat page for Security Compliance Advisor
This page provides an interactive chat interface with the security compliance chatbot.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import asyncio
import os
import json
from pathlib import Path

from core.compliance.security_compliance_chatbot import SecurityComplianceChatbot
from core.compliance.compliance_knowledge import ComplianceKnowledge
from core.compliance.policy_loader import PolicyLoader

class ChatPage:
    """Interactive chat interface for the security compliance advisor"""

    def __init__(self):
        """Initialize the chat page"""
        # Initialize the chatbot
        knowledge_base = ComplianceKnowledge()
        self.chatbot = SecurityComplianceChatbot(
            model_dir="data/models",
            api_key=None,  # No API mode
            knowledge_base=knowledge_base
        )
        
        # Initialize session state for chat
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": """
                Hi there! I'm your Security and Compliance Advisor Assistant. 
                
                I can help you with:
                - Understanding security and privacy regulations
                - Implementing compliance controls
                - Security best practices and recommendations
                - Framework-specific requirements
                
                What compliance or security question can I help with today?
                """}
            ]
            
        if "user_context" not in st.session_state:
            st.session_state.user_context = {
                "industry": None,
                "size": None,
                "compliance_needs": []
            }
            
    async def process_message(self, message: str) -> dict:
        """
        Process a message through the chatbot
        
        Args:
            message: User's message text
            
        Returns:
            Response dictionary
        """
        # Get user context
        context = {"organization": st.session_state.user_context} if "user_context" in st.session_state else None
        
        # Process message
        return await self.chatbot.process_message(message, context)

    def display_chat_message(self, message):
        """
        Display a chat message with appropriate styling
        
        Args:
            message: Message dictionary with role and content
        """
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            st.markdown(f'<div class="chat-message user">{content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message bot">{content}</div>', unsafe_allow_html=True)
            
    def show_suggested_questions(self):
        """Display suggested questions based on selected frameworks"""
        st.write("### Suggested Questions")
        
        # Get user's selected frameworks
        selected_frameworks = st.session_state.user_context.get("compliance_needs", [])
        
        # Generate suggestions based on frameworks or default suggestions
        suggestions = []
        
        if not selected_frameworks:
            suggestions = [
                "What are the key requirements of NIST 800-53?",
                "How do GDPR and CCPA differ?",
                "What controls should I implement for basic security?",
                "How do I start a compliance program for my organization?",
                "What documentation is required for ISO 27001?"
            ]
        else:
            # Framework-specific questions
            for framework in selected_frameworks:
                if framework == "GDPR":
                    suggestions.extend([
                        "What are the GDPR data subject rights?",
                        "How do I implement privacy by design for GDPR?",
                        "What is required in a GDPR data processing agreement?"
                    ])
                elif "NIST" in framework:
                    suggestions.extend([
                        f"What are the key controls in {framework}?",
                        f"How do I implement access control per {framework}?",
                        f"What is the {framework} risk assessment framework?"
                    ])
                elif framework == "HIPAA":
                    suggestions.extend([
                        "What are the HIPAA technical safeguards?",
                        "How do I conduct a HIPAA risk assessment?",
                        "What is considered PHI under HIPAA?"
                    ])
                elif "PCI" in framework:
                    suggestions.extend([
                        "What are the PCI-DSS requirements for encryption?",
                        "How do I implement network segmentation for PCI compliance?",
                        "What is the scope of PCI-DSS in my environment?"
                    ])
        
        # Create buttons for suggestions
        col1, col2 = st.columns(2)
        
        for i, suggestion in enumerate(suggestions[:6]):  # Limit to 6 suggestions
            if i % 2 == 0:
                with col1:
                    if st.button(suggestion, key=f"sugg_{i}"):
                        self.add_user_message(suggestion)
                        st.rerun()
            else:
                with col2:
                    if st.button(suggestion, key=f"sugg_{i}"):
                        self.add_user_message(suggestion)
                        st.rerun()
                        
    def setup_user_context(self):
        """Collect information about the user's organization context"""
        with st.sidebar:
            st.header("Organization Context")
            st.write("Help me provide more relevant advice by sharing some information about your organization:")
            
            # Industry selection
            industry = st.selectbox(
                "Industry",
                options=["Healthcare", "Finance", "Technology", "Retail", "Manufacturing", "Government", "Education", "Other"],
                index=None if st.session_state.user_context["industry"] is None else 
                      ["Healthcare", "Finance", "Technology", "Retail", "Manufacturing", "Government", "Education", "Other"].index(st.session_state.user_context["industry"])
            )
            
            # Organization size
            size = st.selectbox(
                "Organization Size",
                options=["Small (1-50 employees)", "Medium (51-500 employees)", "Large (501-5000 employees)", "Enterprise (5000+ employees)"],
                index=None if st.session_state.user_context["size"] is None else
                      ["Small (1-50 employees)", "Medium (51-500 employees)", "Large (501-5000 employees)", "Enterprise (5000+ employees)"].index(st.session_state.user_context["size"])
            )
            
            # Compliance frameworks
            policy_loader = PolicyLoader()
            frameworks = list(policy_loader.get_all_framework_summaries().keys())
            
            selected_frameworks = st.multiselect(
                "Applicable Compliance Frameworks",
                options=frameworks,
                default=st.session_state.user_context["compliance_needs"]
            )
            
            # Update session state
            st.session_state.user_context["industry"] = industry
            st.session_state.user_context["size"] = size
            st.session_state.user_context["compliance_needs"] = selected_frameworks
            
            # Buttons to clear chat or start a new chat about a framework
            st.markdown("---")
            if st.button("Clear Chat History"):
                st.session_state.messages = [st.session_state.messages[0]]  # Keep welcome message
                self.chatbot.clear_conversation_history()
                st.rerun()
                
            if selected_frameworks and st.button("Start Framework Assessment"):
                framework = selected_frameworks[0]
                self.add_user_message(f"I need to implement {framework}. What are the first steps?")
                st.rerun()
                
            # Add a search box in the sidebar
            st.markdown("---")
            st.subheader("Knowledge Base Search")
            search_query = st.text_input("Search for controls or requirements:")
            if search_query:
                search_results = self.chatbot.search_knowledge_base(search_query)
                
                if search_results:
                    st.write("### Search Results")
                    for i, result in enumerate(search_results[:5]):
                        policy = result.get('policy', {})
                        with st.expander(f"{policy.get('framework', '')}-{policy.get('control_id', '')}: {policy.get('title', 'No title')}"):
                            st.write(f"**Description:** {policy.get('description', 'No description')}")
                            
                            if "requirements" in policy:
                                req = policy["requirements"]
                                if isinstance(req, list):
                                    st.write("**Requirements:**")
                                    for r in req:
                                        st.write(f"- {r}")
                                else:
                                    st.write(f"**Requirements:** {req}")
                else:
                    st.write("No results found")
    
    def add_user_message(self, message: str):
        """
        Add a user message to the messages list
        
        Args:
            message: Message text
        """
        st.session_state.messages.append({"role": "user", "content": message})
    
    def add_assistant_message(self, message: str):
        """
        Add an assistant message to the messages list
        
        Args:
            message: Message text
        """
        st.session_state.messages.append({"role": "assistant", "content": message})
    
    def render(self):
        """Render the chat page"""
        st.title("Security Compliance Advisor")
        
        # Setup sidebar for context
        self.setup_user_context()
        
        # Display chat messages
        for message in st.session_state.messages:
            self.display_chat_message(message)
            
        # Show suggested questions
        with st.expander("Need some ideas?", expanded=len(st.session_state.messages) <= 1):
            self.show_suggested_questions()
            
        # Chat input
        user_input = st.chat_input("Ask a security or compliance question...")
        
        if user_input:
            # Add user message to chat
            self.add_user_message(user_input)
            
            # Display the updated messages
            st.rerun()  # This will trigger a rerun to show the message
        
        # Process the last message and display response
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            user_message = st.session_state.messages[-1]["content"]
            
            with st.spinner("Thinking..."):
                # Use asyncio to run the async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(self.process_message(user_message))
                loop.close()
                
            # Add assistant response
            self.add_assistant_message(response["text"])
            
            # Display the updated messages
            st.rerun()  # This will trigger a rerun to show the message

def render_chat_page():
    """
    Render the chat page
    """
    chat_page = ChatPage()
    chat_page.render()

if __name__ == "__main__":
    render_chat_page()