"""
Chat page for Security Compliance Advisor
This page handles chat interactions with the security advisor.
"""

import streamlit as st
import random
import time
from datetime import datetime

def render_chat_page(security_advisor=None):
    """
    Render the chat page
    
    Args:
        security_advisor: SecurityAdvisor instance (optional)
    """
    st.title("💬 Chat with Security Advisor")
    
    # Initialize session state for chat
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
        
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Context selection
    context_options = [
        "General Security Questions",
        "Compliance Framework Guidance",
        "Risk Assessment Help",
        "Security Best Practices"
    ]
    
    selected_context = st.selectbox("What would you like to discuss?", context_options)
    
    # Industry selection for more targeted responses
    industry_options = [
        "Finance", 
        "Healthcare", 
        "Technology", 
        "Education", 
        "Government",
        "Retail",
        "Manufacturing",
        "Other"
    ]
    
    selected_industry = st.selectbox("Select your industry", industry_options)
    
    # Display conversation history
    for message in st.session_state.conversation:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**Advisor:** {message['content']}")
    
    # Input area
    user_input = st.text_area("Ask a security or compliance question:", 
                              key="user_input", 
                              height=100,
                              placeholder="Example: What are the key requirements for GDPR compliance?")
    
    # Submit button
    if st.button("Send", key="send_button") and user_input.strip():
        # Add user message to conversation
        st.session_state.conversation.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate response
        try:
            with st.spinner("Thinking..."):
                if security_advisor and hasattr(security_advisor, "answer_question"):
                    # Use the actual security advisor
                    response = security_advisor.answer_question(
                        user_input, 
                        context=selected_context,
                        industry=selected_industry
                    )
                else:
                    # Fallback to simulated response
                    response = generate_sample_response(user_input, selected_context, selected_industry)
                    
                # Add small delay for UX
                time.sleep(0.5)
        except Exception as e:
            response = f"I apologize, but I encountered an error while processing your question: {str(e)}. Please try again or ask another question."
        
        # Add assistant message to conversation
        st.session_state.conversation.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Save to chat history
        st.session_state.chat_history.append({
            "user": user_input,
            "bot": response,
            "context": selected_context,
            "industry": selected_industry,
            "timestamp": datetime.now().isoformat()
        })
        
        # Clear input and rerun
        st.experimental_rerun()

    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.conversation = []
        st.session_state.chat_history = []
        st.experimental_rerun()


def generate_sample_response(question, context, industry):
    """
    Generate a simulated response when the security advisor is not available
    
    Args:
        question: User's question
        context: Selected chat context
        industry: Selected industry
        
    Returns:
        Simulated response
    """
    # Basic responses based on question keywords
    question_lower = question.lower()
    
    # Framework specific responses
    if "iso" in question_lower or "27001" in question_lower:
        return """ISO 27001 is an information security standard that provides a framework for implementing an information security management system (ISMS). 

Key requirements include:
- Identifying security risks through risk assessment
- Implementing security controls to mitigate identified risks
- Regular monitoring and review of the ISMS
- Continuous improvement of security practices

For detailed implementation guidance, you may want to review our frameworks page or upload a questionnaire for assessment."""
    
    elif "gdpr" in question_lower:
        return """The General Data Protection Regulation (GDPR) is a comprehensive privacy law in the EU. 

Key requirements include:
- Data processing must have a lawful basis
- Enhanced rights for data subjects (access, deletion, portability)
- Mandatory breach notifications
- Data protection impact assessments
- Privacy by design and default

In the {} industry, particular attention should be paid to consent mechanisms and data minimization.""".format(industry)
    
    elif "hipaa" in question_lower:
        return """HIPAA (Health Insurance Portability and Accountability Act) sets standards for protecting sensitive patient health information.

Key requirements include:
- Physical, technical, and administrative safeguards
- Patient rights to access their health records
- Restrictions on disclosures
- Breach notification requirements
- Business associate agreements

This is particularly relevant for the healthcare industry and their service providers."""
    
    # Context-based responses
    elif context == "Risk Assessment Help":
        return """For risk assessment, I recommend:

1. Identify your critical assets and data
2. Evaluate threats and vulnerabilities
3. Assess potential impacts and likelihood
4. Implement appropriate controls
5. Monitor and review regularly

You can use our questionnaire tool to conduct a basic risk assessment by uploading a completed security questionnaire."""
    
    elif context == "Compliance Framework Guidance":
        return """Compliance frameworks provide structured approaches to meeting regulatory requirements. For your {} industry, consider:

1. Identify applicable regulations (GDPR, HIPAA, PCI DSS, etc.)
2. Map your controls to framework requirements
3. Conduct gap analysis
4. Implement missing controls
5. Regular auditing and testing

Visit our frameworks page for more specific guidance on each framework.""".format(industry)
    
    # General security response
    else:
        general_responses = [
            """Based on your question, I'd recommend focusing on these security areas:
            
1. Access control and authentication
2. Data encryption and protection
3. Regular security assessment and testing
4. Incident response planning
5. Security awareness training

Would you like more specific information on any of these areas?""",
            
            """For organizations in the {} industry, security best practices include:
            
- Implementing multi-factor authentication
- Encryption of sensitive data at rest and in transit
- Regular vulnerability scanning and penetration testing
- Security awareness training for all employees
- Detailed incident response procedures

Our dashboard can help you visualize your current security posture against these practices.""".format(industry),
            
            """To improve your security posture, consider:
            
1. Conducting a thorough risk assessment
2. Implementing defense-in-depth strategies
3. Regular security awareness training
4. Third-party vendor security reviews
5. Continuous monitoring and logging

You can upload a security questionnaire to get a more tailored assessment."""
        ]
        
        return random.choice(general_responses)


if __name__ == "__main__":
    render_chat_page()