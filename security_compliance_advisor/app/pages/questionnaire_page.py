"""
Questionnaire page for Security Compliance Advisor
This page handles uploading and processing vendor questionnaires.
"""

import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import json
from datetime import datetime
from pathlib import Path

from core.advisor.questionnaire_processor import QuestionnaireProcessor
from core.risk.risk_scoring_model import RiskScoringModel

class QuestionnairePage:
    """Questionnaire upload and processing page"""
    
    def __init__(self, security_advisor=None):
        """
        Initialize the questionnaire page
        
        Args:
            security_advisor: SecurityAdvisor instance (optional)
        """
        self.security_advisor = security_advisor
        
        if not security_advisor:
            self.questionnaire_processor = QuestionnaireProcessor()
            self.risk_model = RiskScoringModel()
        else:
            self.questionnaire_processor = security_advisor.questionnaire_processor
            self.risk_model = security_advisor.risk_model
        
        # Initialize session state variables if they don't exist
        if "questionnaire_data" not in st.session_state:
            st.session_state.questionnaire_data = {}
            
        if "assessment" not in st.session_state:
            st.session_state.assessment = None
            
        if "recommendations" not in st.session_state:
            st.session_state.recommendations = []
            
        if "uploaded_file_name" not in st.session_state:
            st.session_state.uploaded_file_name = None
        
        # Initialize frameworks if it doesn't exist
        if "frameworks" not in st.session_state:
            st.session_state.frameworks = {
                "iso27001": {"name": "ISO/IEC 27001", "description": "International standard for information security management", "coverage": 0},
                "nist_csf": {"name": "NIST Cybersecurity Framework", "description": "Framework for improving critical infrastructure cybersecurity", "coverage": 0},
                "gdpr": {"name": "GDPR", "description": "EU regulation on data protection and privacy", "coverage": 0},
                "hipaa": {"name": "HIPAA", "description": "US healthcare privacy and security regulation", "coverage": 0},
                "pci_dss": {"name": "PCI DSS", "description": "Payment card industry security standard", "coverage": 0},
                "ccpa": {"name": "CCPA", "description": "California Consumer Privacy Act", "coverage": 0},
                "cis": {"name": "CIS Controls", "description": "Critical security controls for cyber defense", "coverage": 0},
                "hitrust": {"name": "HITRUST CSF", "description": "Healthcare industry security framework", "coverage": 0}
            }
    
    def render(self):
        """Render the questionnaire page"""
        st.title("Vendor Security Assessment")
        
        # Instructions
        st.markdown("""
        ## Upload Vendor Security Questionnaire
        
        Upload a vendor security questionnaire to analyze compliance risks. 
        Supported file formats: CSV, Excel (XLSX, XLS), JSON
        
        The questionnaire will be processed to:
        1. Identify security risks
        2. Assess compliance with major frameworks
        3. Generate actionable recommendations
        """)
        
        # File uploader
        uploaded_file = st.file_uploader("Choose a questionnaire file", 
                                        type=["csv", "xlsx", "xls", "json"],
                                        help="Upload a vendor security questionnaire file")
        
        if uploaded_file:
            st.session_state.uploaded_file_name = uploaded_file.name
            
            # Process the uploaded file
            try:
                with st.spinner("Processing questionnaire..."):
                    questionnaire_data = self._process_uploaded_file(uploaded_file)
                    
                    if questionnaire_data:
                        st.session_state.questionnaire_data = questionnaire_data
                        
                        # Display questionnaire summary
                        self._display_questionnaire_summary(questionnaire_data)
                        
                        # Process for risk assessment
                        if st.button("Run Risk Assessment"):
                            self._run_risk_assessment(questionnaire_data)
                            
                            # Redirect to dashboard if assessment completed
                            if st.session_state.assessment:
                                st.success("Risk assessment completed! View the results on the dashboard.")
                                st.button("View Dashboard", on_click=self._go_to_dashboard)
            
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
                st.exception(e)
        
        # Display sample questionnaire templates if no file uploaded
        elif not st.session_state.questionnaire_data:
            self._display_template_options()
        
        # Show previously uploaded data if available
        elif st.session_state.uploaded_file_name:
            st.info(f"Using previously uploaded file: {st.session_state.uploaded_file_name}")
            
            # Display questionnaire summary
            self._display_questionnaire_summary(st.session_state.questionnaire_data)
            
            # Process for risk assessment
            if st.button("Run Risk Assessment"):
                self._run_risk_assessment(st.session_state.questionnaire_data)
                
                # Redirect to dashboard if assessment completed
                if st.session_state.assessment:
                    st.success("Risk assessment completed! View the results on the dashboard.")
                    st.button("View Dashboard", on_click=self._go_to_dashboard)
            
            # Option to clear data
            if st.button("Clear Data"):
                st.session_state.questionnaire_data = {}
                st.session_state.assessment = None
                st.session_state.recommendations = []
                st.session_state.uploaded_file_name = None
                st.experimental_rerun()
    
    def _process_uploaded_file(self, uploaded_file):
        """
        Process the uploaded questionnaire file
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Processed questionnaire data as dictionary
        """
        # Get file extension
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        # Process based on file type
        if file_extension in ['.csv']:
            # Process CSV file
            df = pd.read_csv(uploaded_file)
            return self._process_questionnaire_df(df)
            
        elif file_extension in ['.xlsx', '.xls']:
            # Process Excel file
            df = pd.read_excel(uploaded_file)
            return self._process_questionnaire_df(df)
            
        elif file_extension in ['.json']:
            # Process JSON file
            try:
                return json.load(uploaded_file)
            except Exception as e:
                st.error(f"Error parsing JSON file: {str(e)}")
                return None
        
        else:
            st.error(f"Unsupported file format: {file_extension}")
            return None
    
    def _process_questionnaire_df(self, df):
        """
        Process questionnaire dataframe into structured data
        
        Args:
            df: Pandas DataFrame with questionnaire data
            
        Returns:
            Processed questionnaire data as dictionary
        """
        # First, try to detect the format of the questionnaire
        format_type = self._detect_questionnaire_format(df)
        
        if format_type == "question_answer":
            # Question-answer format (two columns)
            return self._process_question_answer_format(df)
            
        elif format_type == "category_question_answer":
            # Category-question-answer format (three or more columns)
            return self._process_category_question_format(df)
            
        elif format_type == "standard_template":
            # Standard security questionnaire template
            return self._process_standard_template(df)
            
        else:
            # Default generic processing
            return self._process_generic_format(df)
    
    def _detect_questionnaire_format(self, df):
        """
        Detect the format of the questionnaire
        
        Args:
            df: Pandas DataFrame with questionnaire data
            
        Returns:
            String indicating the detected format
        """
        # Check number of columns
        num_columns = len(df.columns)
        
        # Look for specific column names
        columns_lower = [col.lower() if isinstance(col, str) else str(col).lower() for col in df.columns]
        
        # Check for question-answer format
        if num_columns == 2:
            # Check if the columns might be question and answer
            if any(q in columns_lower[0] for q in ['question', 'control', 'requirement']) and \
               any(a in columns_lower[1] for q in ['answer', 'response', 'compliance', 'status']):
                return "question_answer"
        
        # Check for category-question-answer format
        elif num_columns >= 3:
            # Check if the columns look like category, question, answer
            if any(c in columns_lower[0] for c in ['category', 'section', 'domain', 'control family']):
                if any(q in columns_lower[1] for q in ['question', 'control', 'requirement']) and \
                   any(a in columns_lower[2] for q in ['answer', 'response', 'compliance', 'status']):
                    return "category_question_answer"
        
        # Check for standard templates
        standard_headers = [
            # SIG/SIG Lite
            ['section', 'question', 'response', 'description'],
            # CAIQ
            ['control domain', 'question id', 'control specification', 'consensus assessment questions'],
            # NIST CSF
            ['function', 'category', 'subcategory', 'implementation']
        ]
        
        for template_headers in standard_headers:
            matches = sum(1 for template_col in template_headers if any(
                template_col == col.lower() for col in columns_lower))
            
            if matches >= len(template_headers) // 2:
                return "standard_template"
        
        # Default to generic format
        return "generic"
    
    def _process_question_answer_format(self, df):
        """
        Process a simple question-answer format questionnaire
        
        Args:
            df: Pandas DataFrame with questionnaire data
            
        Returns:
            Processed questionnaire data as dictionary
        """
        # Rename columns to standard format
        df.columns = ['Question', 'Answer'] + list(df.columns[2:])
        
        # Convert to dictionary
        questions = []
        
        for _, row in df.iterrows():
            question = {
                'question': row['Question'],
                'answer': row['Answer']
            }
            
            # Add any additional columns
            for col in df.columns[2:]:
                question[col.lower().replace(' ', '_')] = row[col]
            
            questions.append(question)
        
        # Create structured data
        questionnaire_data = {
            'metadata': {
                'format': 'question_answer',
                'num_questions': len(questions),
                'processed_date': datetime.now().isoformat()
            },
            'questions': questions
        }
        
        return questionnaire_data
    
    def _process_category_question_format(self, df):
        """
        Process a category-question-answer format questionnaire
        
        Args:
            df: Pandas DataFrame with questionnaire data
            
        Returns:
            Processed questionnaire data as dictionary
        """
        # Rename columns to standard format
        df.columns = ['Category', 'Question', 'Answer'] + list(df.columns[3:])
        
        # Convert to dictionary with categories
        categories = {}
        questions = []
        
        for _, row in df.iterrows():
            category = row['Category']
            
            question = {
                'category': category,
                'question': row['Question'],
                'answer': row['Answer']
            }
            
            # Add any additional columns
            for col in df.columns[3:]:
                question[col.lower().replace(' ', '_')] = row[col]
            
            questions.append(question)
            
            # Group by category
            if category not in categories:
                categories[category] = []
                
            categories[category].append(question)
        
        # Create structured data
        questionnaire_data = {
            'metadata': {
                'format': 'category_question_answer',
                'num_questions': len(questions),
                'num_categories': len(categories),
                'processed_date': datetime.now().isoformat()
            },
            'categories': categories,
            'questions': questions  # Flat list of all questions
        }
        
        return questionnaire_data
    
    def _process_standard_template(self, df):
        """
        Process a recognized standard questionnaire template
        
        Args:
            df: Pandas DataFrame with questionnaire data
            
        Returns:
            Processed questionnaire data as dictionary
        """
        # Try to identify which standard template
        columns_lower = [col.lower() if isinstance(col, str) else str(col).lower() for col in df.columns]
        
        # Check for SIG/SIG Lite
        if ('section' in columns_lower and 'question' in columns_lower and 
            ('response' in columns_lower or 'answer' in columns_lower)):
            return self._process_sig_template(df)
            
        # Check for CAIQ
        elif 'control domain' in columns_lower and ('question id' in columns_lower or 'consensus assessment questions' in columns_lower):
            return self._process_caiq_template(df)
            
        # Check for NIST CSF
        elif 'function' in columns_lower and 'category' in columns_lower and 'subcategory' in columns_lower:
            return self._process_nist_csf_template(df)
            
        # Default to category-question-answer format
        else:
            return self._process_category_question_format(df)
    
    def _process_sig_template(self, df):
        """
        Process a SIG/SIG Lite questionnaire template
        
        Args:
            df: Pandas DataFrame with questionnaire data
            
        Returns:
            Processed questionnaire data as dictionary
        """
        # Map column names to standard format
        column_mapping = {}
        columns_lower = [col.lower() if isinstance(col, str) else str(col).lower() for col in df.columns]
        
        for i, col_lower in enumerate(columns_lower):
            if 'section' in col_lower:
                column_mapping[df.columns[i]] = 'Category'
            elif 'question' in col_lower:
                column_mapping[df.columns[i]] = 'Question'
            elif 'response' in col_lower or 'answer' in col_lower:
                column_mapping[df.columns[i]] = 'Answer'
        
        # Rename columns
        df_renamed = df.rename(columns=column_mapping)
        
        # Process as category-question-answer format
        return self._process_category_question_format(df_renamed)
    
    def _process_caiq_template(self, df):
        """
        Process a CAIQ (Cloud Assessment Initiative Questionnaire) template
        
        Args:
            df: Pandas DataFrame with questionnaire data
            
        Returns:
            Processed questionnaire data as dictionary
        """
        # Map column names to standard format
        column_mapping = {}
        columns_lower = [col.lower() if isinstance(col, str) else str(col).lower() for col in df.columns]
        
        for i, col_lower in enumerate(columns_lower):
            if 'control domain' in col_lower:
                column_mapping[df.columns[i]] = 'Category'
            elif 'consensus assessment questions' in col_lower or 'question' in col_lower:
                column_mapping[df.columns[i]] = 'Question'
            elif 'yes' in col_lower or 'no' in col_lower or 'response' in col_lower or 'answer' in col_lower:
                column_mapping[df.columns[i]] = 'Answer'
        
        # Rename columns
        df_renamed = df.rename(columns=column_mapping)
        
        # Process as category-question-answer format
        questionnaire_data = self._process_category_question_format(df_renamed)
        
        # Add metadata specific to CAIQ
        questionnaire_data['metadata']['template_type'] = 'CAIQ'
        
        return questionnaire_data
    
    def _process_nist_csf_template(self, df):
        """
        Process a NIST CSF questionnaire template
        
        Args:
            df: Pandas DataFrame with questionnaire data
            
        Returns:
            Processed questionnaire data as dictionary
        """
        # Map column names to standard format
        column_mapping = {}
        columns_lower = [col.lower() if isinstance(col, str) else str(col).lower() for col in df.columns]
        
        for i, col_lower in enumerate(columns_lower):
            if 'function' in col_lower:
                column_mapping[df.columns[i]] = 'Function'
            elif 'category' in col_lower:
                column_mapping[df.columns[i]] = 'Category'
            elif 'subcategory' in col_lower:
                column_mapping[df.columns[i]] = 'Subcategory'
            elif 'implementation' in col_lower or 'status' in col_lower or 'compliance' in col_lower:
                column_mapping[df.columns[i]] = 'Answer'
        
        # Rename columns
        df_renamed = df.rename(columns=column_mapping)
        
        # Convert to dictionary with hierarchical structure
        functions = {}
        questions = []
        
        for _, row in df_renamed.iterrows():
            function = row.get('Function', '')
            category = row.get('Category', '')
            subcategory = row.get('Subcategory', '')
            answer = row.get('Answer', '')
            
            # Construct question and category
            question_text = f"{subcategory}"
            category_text = f"{function} - {category}"
            
            question = {
                'function': function,
                'category': category_text,
                'question': question_text,
                'answer': answer
            }
            
            # Add any additional columns
            for col in df_renamed.columns:
                if col not in ['Function', 'Category', 'Subcategory', 'Answer']:
                    question[col.lower().replace(' ', '_')] = row.get(col, '')
            
            questions.append(question)
            
            # Group by function and category
            if function not in functions:
                functions[function] = {}
                
            if category not in functions[function]:
                functions[function][category] = []
                
            functions[function][category].append(question)
        
        # Create structured data
        questionnaire_data = {
            'metadata': {
                'format': 'nist_csf',
                'template_type': 'NIST CSF',
                'num_questions': len(questions),
                'num_functions': len(functions),
                'processed_date': datetime.now().isoformat()
            },
            'functions': functions,
            'questions': questions  # Flat list of all questions
        }
        
        return questionnaire_data
    
    def _process_generic_format(self, df):
        """
        Process a generic questionnaire format
        
        Args:
            df: Pandas DataFrame with questionnaire data
            
        Returns:
            Processed questionnaire data as dictionary
        """
        # Convert all column names to strings
        df.columns = [str(col) for col in df.columns]
        
        # Convert to dictionary
        questions = []
        
        for i, row in df.iterrows():
            question = {'row_id': i}
            
            # Add all columns
            for col in df.columns:
                question[col.lower().replace(' ', '_')] = row[col]
            
            questions.append(question)
        
        # Create structured data
        questionnaire_data = {
            'metadata': {
                'format': 'generic',
                'num_questions': len(questions),
                'num_columns': len(df.columns),
                'column_names': list(df.columns),
                'processed_date': datetime.now().isoformat()
            },
            'questions': questions
        }
        
        return questionnaire_data
    
    def _display_questionnaire_summary(self, questionnaire_data):
        """
        Display a summary of the processed questionnaire
        
        Args:
            questionnaire_data: Processed questionnaire data dictionary
        """
        # Get metadata
        metadata = questionnaire_data.get('metadata', {})
        format_type = metadata.get('format', 'unknown')
        template_type = metadata.get('template_type', 'Custom')
        num_questions = metadata.get('num_questions', 0)
        num_categories = metadata.get('num_categories', 0)
        
        # Display summary
        st.subheader("Questionnaire Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Questions", num_questions)
            
        with col2:
            st.metric("Format", f"{format_type.title()}")
            
        with col3:
            st.metric("Template", template_type)
        
        # Show question categories if available
        if 'categories' in questionnaire_data:
            categories = questionnaire_data['categories']
            
            st.subheader("Question Categories")
            
            # Show bar chart of questions per category
            category_counts = {cat: len(questions) for cat, questions in categories.items()}
            category_df = pd.DataFrame({
                'Category': list(category_counts.keys()),
                'Questions': list(category_counts.values())
            })
            
            if not category_df.empty:
                st.bar_chart(category_df.set_index('Category'))
        
        # Show sample questions
        st.subheader("Sample Questions")
        
        questions = questionnaire_data.get('questions', [])
        
        if questions:
            sample_size = min(5, len(questions))
            sample_questions = questions[:sample_size]
            
            for i, question in enumerate(sample_questions):
                with st.expander(f"Q{i+1}: {question.get('question', 'Question')[:100]}..."):
                    st.write(f"**Question:** {question.get('question', 'N/A')}")
                    st.write(f"**Answer:** {question.get('answer', 'N/A')}")
                    
                    # Show additional fields
                    st.write("**Additional Fields:**")
                    additional_fields = {k: v for k, v in question.items() 
                                        if k not in ['question', 'answer', 'category']}
                    
                    if additional_fields:
                        for key, value in additional_fields.items():
                            st.write(f"- {key}: {value}")
                    else:
                        st.write("None")
    
    def _display_template_options(self):
        """Display options to download questionnaire templates"""
        st.subheader("Sample Templates")
        st.write("Don't have a questionnaire? Download one of these templates:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### Basic Template")
            st.write("A simple questionnaire with categories and questions")
            
            # Generate sample data
            df = pd.DataFrame({
                'Category': ['Access Control', 'Access Control', 'Data Protection', 
                            'Data Protection', 'Network Security'],
                'Question': ['Do you have MFA implemented?', 
                            'Is access based on least privilege?',
                            'Is sensitive data encrypted at rest?',
                            'Is sensitive data encrypted in transit?',
                            'Do you have a firewall?'],
                'Answer': ['Yes', 'Yes', 'No', 'Yes', 'Yes'],
                'Notes': ['', '', 'Planning to implement Q3', '', '']
            })
            
            # Create download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="basic_security_questionnaire.csv",
                mime="text/csv"
            )
        
        with col2:
            st.markdown("### CAIQ Template")
            st.write("Cloud Security Alliance CAIQ format")
            
            # Generate sample data
            df = pd.DataFrame({
                'Control Domain': ['Identity & Access Management', 'Identity & Access Management', 
                                'Data Security & Privacy', 'Data Security & Privacy'],
                'Control ID': ['IAM-01', 'IAM-02', 'DSP-01', 'DSP-02'],
                'Question': ['Do you restrict, log, and monitor access to your information security management systems?',
                            'Do you utilize dedicated secure networks to provide management access to your cloud service infrastructure?',
                            'Are data security policies and procedures shared with relevant customers and third-party stakeholders?',
                            'Do you have a policy addressing protection of sensitive data when it is being processed or stored in cloud environments?'],
                'Yes/No': ['Yes', 'Yes', 'No', 'Yes'],
                'Implementation Details': ['Implemented with SIEM', 'Separate management VLAN', '', 'Encryption policies in place']
            })
            
            # Create download button
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False)
            excel_buffer.seek(0)
            
            st.download_button(
                label="Download Excel",
                data=excel_buffer,
                file_name="caiq_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col3:
            st.markdown("### NIST CSF Template")
            st.write("NIST Cybersecurity Framework template")
            
            # Generate sample data
            df = pd.DataFrame({
                'Function': ['Identify', 'Identify', 'Protect', 'Protect', 'Detect'],
                'Category': ['Asset Management', 'Risk Assessment', 'Access Control', 'Data Security', 'Anomalies and Events'],
                'Subcategory': ['ID.AM-1: Physical devices and systems inventoried', 
                              'ID.RA-1: Vulnerabilities identified and documented',
                              'PR.AC-1: Identities and credentials are issued, managed, verified, revoked',
                              'PR.DS-1: Data-at-rest is protected',
                              'DE.AE-1: Baseline of network operations established'],
                'Implementation Status': ['Implemented', 'Partial', 'Implemented', 'Not Implemented', 'Implemented'],
                'Comments': ['Asset inventory system in place', 'Vulnerability scanning scheduled quarterly', 
                           'SSO and MFA implemented', 'Encryption not yet implemented for all systems', 
                           'SIEM solution monitors baseline']
            })
            
            # Create download button
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False)
            excel_buffer.seek(0)
            
            st.download_button(
                label="Download Excel",
                data=excel_buffer,
                file_name="nist_csf_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    def _run_risk_assessment(self, questionnaire_data):
        """
        Run risk assessment on the questionnaire data
        
        Args:
            questionnaire_data: Processed questionnaire data dictionary
        """
        try:
            with st.spinner("Running risk assessment..."):
                if self.security_advisor:
                    processed_data = self.security_advisor.questionnaire_processor.process_questionnaire(questionnaire_data)
                    assessment = self.security_advisor.risk_model.assess_risk(processed_data)
                    recommendations = self.security_advisor.risk_model.generate_recommendations(assessment)
                else:
                    # Otherwise use the components directly
                    processed_data = self.questionnaire_processor.process_questionnaire(questionnaire_data)
                    assessment = self.risk_model.assess_risk(processed_data)
                    recommendations = self.risk_model.generate_recommendations(assessment)
                
                # Store assessment and recommendations in session state
                st.session_state.assessment = assessment
                st.session_state.recommendations = recommendations
                
                # Update framework compliance in session state
                if 'framework_compliance' in assessment:
                    # Make sure frameworks exists in session state
                    if "frameworks" not in st.session_state:
                        st.session_state.frameworks = {
                            "iso27001": {"name": "ISO/IEC 27001", "description": "International standard for information security management", "coverage": 0},
                            "nist_csf": {"name": "NIST Cybersecurity Framework", "description": "Framework for improving critical infrastructure cybersecurity", "coverage": 0},
                            "gdpr": {"name": "GDPR", "description": "EU regulation on data protection and privacy", "coverage": 0},
                            "hipaa": {"name": "HIPAA", "description": "US healthcare privacy and security regulation", "coverage": 0},
                            "pci_dss": {"name": "PCI DSS", "description": "Payment card industry security standard", "coverage": 0}
                        }
                    
                    for framework_id, compliance_data in assessment['framework_compliance'].items():
                        if framework_id in st.session_state.frameworks:
                            st.session_state.frameworks[framework_id]['coverage'] = compliance_data.get('compliance_score', 0)
                
                return assessment
                
        except Exception as e:
            st.error(f"Error running risk assessment: {str(e)}")
            st.exception(e)
            return None
    
    def _go_to_dashboard(self):
        """Redirect to the dashboard page"""
        st.session_state.current_page = 'dashboard'
        st.experimental_rerun()


def render_questionnaire_page(security_advisor=None):
    """
    Render the questionnaire page
    
    Args:
        security_advisor: SecurityAdvisor instance (optional)
    """
    page = QuestionnairePage(security_advisor)
    page.render()


if __name__ == "__main__":
    render_questionnaire_page()