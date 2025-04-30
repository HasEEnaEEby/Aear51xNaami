"""
Security Compliance Questionnaire Page Implementation
This module implements an interactive questionnaire interface that guides users through 
compliance assessment questions and integrates with the security advisor system.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple

from core.advisor.questionnaire_processor import QuestionnaireProcessor
from core.advisor.security_advisor import SecurityAdvisor
from core.compliance.policy_processor import PolicyProcessor
from core.risk.risk_scoring_model import RiskScoringModel
from core.compliance.compliance_knowledge import ComplianceKnowledge
from app.utils.styles.css import apply_styling

class QuestionnairePage:
    """Interactive questionnaire for security compliance assessment"""

    def __init__(self):
        self.processor = QuestionnaireProcessor()
        self.advisor = SecurityAdvisor()
        self.policy_processor = PolicyProcessor()
        self.risk_model = RiskScoringModel()
        self.compliance_knowledge = ComplianceKnowledge()
        
        # Initialize session state for questionnaire progress
        if "current_question_index" not in st.session_state:
            st.session_state.current_question_index = 0
            
        if "answers" not in st.session_state:
            st.session_state.answers = {}
            
        if "selected_frameworks" not in st.session_state:
            st.session_state.selected_frameworks = []
            
        if "assessment_complete" not in st.session_state:
            st.session_state.assessment_complete = False
            
        if "risk_score" not in st.session_state:
            st.session_state.risk_score = None
            
        if "compliance_gaps" not in st.session_state:
            st.session_state.compliance_gaps = []

    def load_questions(self) -> List[Dict[str, Any]]:
        """Load dynamically adjusted questions based on organization profile and selected frameworks"""
        # Get base questions
        questions = self.processor.get_questions()
        
        # If user has selected frameworks, add framework-specific questions
        if st.session_state.selected_frameworks:
            for framework in st.session_state.selected_frameworks:
                framework_questions = self.processor.get_framework_specific_questions(framework)
                questions.extend(framework_questions)
                
        return questions

    def select_compliance_frameworks(self):
        """Allow user to select which compliance frameworks they need to adhere to"""
        st.subheader("Select Applicable Compliance Frameworks")
        
        # Get available frameworks from compliance knowledge
        available_frameworks = self.compliance_knowledge.get_available_frameworks()
        
        # Create multi-select for frameworks
        selected = st.multiselect(
            "Which compliance frameworks apply to your organization?",
            options=available_frameworks,
            default=st.session_state.selected_frameworks
        )
        
        # Update session state if selection changed
        if selected != st.session_state.selected_frameworks:
            st.session_state.selected_frameworks = selected
            # Reset questionnaire if frameworks change
            st.session_state.current_question_index = 0
            st.session_state.answers = {}
            st.session_state.assessment_complete = False
            
        # Display framework descriptions for selected frameworks
        if selected:
            st.write("### Selected Framework Information")
            for framework in selected:
                with st.expander(f"{framework} Details"):
                    framework_info = self.compliance_knowledge.get_framework_info(framework)
                    st.write(f"**Description:** {framework_info.get('description', 'No description available')}")
                    st.write(f"**Scope:** {framework_info.get('scope', 'No scope information available')}")
                    st.write(f"**Number of Controls:** {framework_info.get('control_count', 'Unknown')}")

    def display_question(self, question: Dict[str, Any]):
        """Display a single question with appropriate input controls"""
        st.write(f"### {question['question']}")
        
        if "description" in question and question["description"]:
            st.write(question["description"])
            
        question_id = question["id"]
        question_type = question.get("type", "text")
        
        # Different input types based on question type
        if question_type == "multiple_choice":
            options = question.get("options", [])
            default = st.session_state.answers.get(question_id, None)
            response = st.radio(
                "Select the best option:",
                options,
                index=options.index(default) if default in options else 0
            )
            
        elif question_type == "checkbox":
            options = question.get("options", [])
            default = st.session_state.answers.get(question_id, [])
            response = st.multiselect(
                "Select all that apply:",
                options=options,
                default=default
            )
            
        elif question_type == "slider":
            min_val = question.get("min", 0)
            max_val = question.get("max", 10)
            default = st.session_state.answers.get(question_id, min_val)
            response = st.slider(
                "Select a value:",
                min_value=min_val,
                max_value=max_val,
                value=default
            )
            
        else:  # Default to text input
            default = st.session_state.answers.get(question_id, "")
            response = st.text_area(
                "Your answer:",
                value=default,
                height=100
            )
            
        # Store the response
        st.session_state.answers[question_id] = response
        
        # Show contextual help if available
        if "help" in question and question["help"]:
            with st.expander("Need help with this question?"):
                st.write(question["help"])
                
                # Get relevant policy information
                if st.session_state.selected_frameworks:
                    relevant_policies = self.policy_processor.get_relevant_policies(
                        question["id"], 
                        st.session_state.selected_frameworks
                    )
                    if relevant_policies:
                        st.write("### Relevant Policy Information")
                        for policy in relevant_policies[:3]:  # Limit to top 3 relevant policies
                            st.write(f"**{policy['framework']}:** {policy['description']}")

    def navigate_questionnaire(self, questions: List[Dict[str, Any]]):
        """Handle navigation through the questionnaire"""
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.current_question_index > 0:
                if st.button("← Previous"):
                    st.session_state.current_question_index -= 1
                    st.rerun()
        
        with col2:
            if st.session_state.current_question_index < len(questions) - 1:
                if st.button("Next →"):
                    st.session_state.current_question_index += 1
                    st.rerun()
            else:
                if st.button("Complete Assessment"):
                    self.complete_assessment(questions)
                    st.rerun()
                    
        # Display progress
        progress = (st.session_state.current_question_index + 1) / len(questions)
        st.progress(progress)
        st.write(f"Question {st.session_state.current_question_index + 1} of {len(questions)}")

    def complete_assessment(self, questions: List[Dict[str, Any]]):
        """Process completed questionnaire and generate insights"""
        # Mark assessment as complete
        st.session_state.assessment_complete = True
        
        # Calculate risk score
        st.session_state.risk_score = self.risk_model.calculate_risk_score(
            st.session_state.answers,
            st.session_state.selected_frameworks
        )
        
        # Identify compliance gaps
        st.session_state.compliance_gaps = self.advisor.identify_compliance_gaps(
            st.session_state.answers,
            st.session_state.selected_frameworks
        )

    def display_results(self):
        """Display assessment results and recommendations"""
        st.write("## Assessment Results")
        
        # Display risk score with gauge chart
        st.write("### Overall Risk Score")
        score = st.session_state.risk_score
        
        # Create a color based on the risk score
        color = "green" if score < 30 else "orange" if score < 70 else "red"
        
        # Display score as a large number with colored background
        st.markdown(
            f"""
            <div style="background-color: {color}; color: white; padding: 20px; 
            border-radius: 10px; text-align: center; width: 150px;">
            <h1 style="margin: 0;">{score}</h1>
            <p style="margin: 0;">Risk Score</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Display risk level explanation
        risk_level = "Low" if score < 30 else "Medium" if score < 70 else "High"
        st.write(f"**Risk Level:** {risk_level}")
        st.write(self.risk_model.get_risk_explanation(score))
        
        # Display compliance gaps
        st.write("### Identified Compliance Gaps")
        
        if not st.session_state.compliance_gaps:
            st.success("No significant compliance gaps identified!")
        else:
            for i, gap in enumerate(st.session_state.compliance_gaps):
                with st.expander(f"Gap #{i+1}: {gap['title']}"):
                    st.write(f"**Framework:** {gap['framework']}")
                    st.write(f"**Control ID:** {gap['control_id']}")
                    st.write(f"**Description:** {gap['description']}")
                    st.write(f"**Recommendation:** {gap['recommendation']}")
                    st.write(f"**Priority:** {gap['priority']}")
                    
                    # Add button to start a chat about this gap
                    if st.button(f"Get Help with this Gap", key=f"help_gap_{i}"):
                        # Store the gap to discuss in session state for the chat page
                        st.session_state.chat_topic = f"How to address {gap['title']} in {gap['framework']}"
                        st.switch_page("app/pages/chat_page.py")
        
        # Generate detailed report
        st.write("### Next Steps")
        st.write("Based on your assessment, we recommend the following actions:")
        
        recommendations = self.advisor.generate_recommendations(
            st.session_state.answers,
            st.session_state.selected_frameworks,
            st.session_state.risk_score
        )
        
        for i, rec in enumerate(recommendations):
            st.write(f"{i+1}. **{rec['title']}**: {rec['description']}")
            
        # Button to restart assessment
        if st.button("Start New Assessment"):
            # Reset session state
            st.session_state.current_question_index = 0
            st.session_state.answers = {}
            st.session_state.assessment_complete = False
            st.session_state.risk_score = None
            st.session_state.compliance_gaps = []
            st.rerun()
            
        # Button to download report
        if st.download_button(
            label="Download Detailed Report",
            data=self.generate_report_pdf(),
            file_name="compliance_assessment_report.pdf",
            mime="application/pdf"
        ):
            st.success("Report downloaded successfully!")
            
    def generate_report_pdf(self) -> bytes:
        """Generate a detailed PDF report of assessment results"""
        # This would typically use a PDF generation library
        # For now, we'll return a placeholder binary content
        return b"Placeholder PDF content"

    def render(self):
        """Render the questionnaire page"""
        st.title("Security Compliance Assessment")
        st.write("""
        Complete this questionnaire to assess your organization's security posture
        and compliance readiness across multiple regulatory frameworks.
        """)
        
        # Apply custom styling
        apply_styling()
        
        # First step: Select compliance frameworks
        self.select_compliance_frameworks()
        
        # Only proceed if frameworks are selected
        if not st.session_state.selected_frameworks:
            st.info("Please select at least one compliance framework to begin the assessment.")
            return
            
        # Show a separator
        st.markdown("---")
        
        # If assessment is complete, show results instead of questions
        if st.session_state.assessment_complete:
            self.display_results()
            return
            
        # Load questions based on selected frameworks
        questions = self.load_questions()
        
        # If no questions available
        if not questions:
            st.error("No questions available for the selected frameworks.")
            return
            
        # Display current question
        current_index = st.session_state.current_question_index
        if 0 <= current_index < len(questions):
            current_question = questions[current_index]
            self.display_question(current_question)
            
            # Question navigation
            st.markdown("---")
            self.navigate_questionnaire(questions)