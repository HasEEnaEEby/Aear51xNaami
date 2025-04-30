import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import argparse
import logging

# Import our custom modules
# Uncomment these when using the actual implementation
from compliance_knowledge import ComplianceKnowledgeBase
from security_advisor_chatbot import SecurityAdvisorChatbot
from explainable_risk_module import ExplainableRiskScoringModule

class SecurityAdvisorSystem:
    def __init__(self, 
                 model_path=None, 
                 frameworks_dir=None, 
                 mappings_file=None, 
                 recommendations_file=None,
                 feature_mappings_file=None,
                 compliance_mappings_file=None,
                 output_dir='outputs'):
        """
        Initialize the Security Advisor System
        
        Args:
            model_path: Path to pre-trained risk model
            frameworks_dir: Directory containing compliance framework files
            mappings_file: Path to control mappings file
            recommendations_file: Path to recommendation templates file
            feature_mappings_file: Path to feature mappings file
            compliance_mappings_file: Path to compliance mappings file
            output_dir: Directory for output files
        """
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('security_advisor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('SecurityAdvisor')
        
        # Create output directory
        self.output_dir = Path(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize components
        self.knowledge_base = None
        self.risk_module = None
        self.chatbot = None
        
        # Load knowledge base if paths provided
        if frameworks_dir or mappings_file or recommendations_file:
            self._load_knowledge_base(frameworks_dir, mappings_file, recommendations_file)
        
        # Load risk module if model path provided
        if model_path:
            self._load_risk_module(model_path, feature_mappings_file, compliance_mappings_file)
        
        # Initialize chatbot with loaded components
        self._initialize_chatbot()
        
        self.logger.info("Security Advisor System initialized")
    
    def _load_knowledge_base(self, frameworks_dir, mappings_file, recommendations_file):
        """
        Load the compliance knowledge base
        
        Args:
            frameworks_dir: Directory containing framework files
            mappings_file: Path to mappings file
            recommendations_file: Path to recommendation templates file
        """
        try:
            # Initialize knowledge base
            # Uncomment when using actual implementation
            # self.knowledge_base = ComplianceKnowledgeBase()
            
            # Load frameworks
            if frameworks_dir:
                frameworks_path = Path(frameworks_dir)
                if frameworks_path.exists() and frameworks_path.is_dir():
                    # Uncomment when using actual implementation
                    # framework_count = self.knowledge_base.load_all_frameworks(frameworks_dir)
                    # self.logger.info(f"Loaded {framework_count} compliance frameworks")
                    self.logger.info(f"Framework directory found: {frameworks_dir}")
            
            # Load mappings
            if mappings_file:
                mappings_path = Path(mappings_file)
                if mappings_path.exists() and mappings_path.is_file():
                    # Uncomment when using actual implementation
                    # self.knowledge_base.load_mappings(mappings_file)
                    # self.logger.info(f"Loaded control mappings from {mappings_file}")
                    self.logger.info(f"Mappings file found: {mappings_file}")
            
            # Load recommendation templates
            if recommendations_file:
                recommendations_path = Path(recommendations_file)
                if recommendations_path.exists() and recommendations_path.is_file():
                    # Uncomment when using actual implementation
                    # self.knowledge_base.load_recommendation_templates(recommendations_file)
                    # self.logger.info(f"Loaded recommendation templates from {recommendations_file}")
                    self.logger.info(f"Recommendations file found: {recommendations_file}")
            
        except Exception as e:
            self.logger.error(f"Error loading knowledge base: {str(e)}")
    
    def _load_risk_module(self, model_path, feature_mappings_file, compliance_mappings_file):
        """
        Load the risk scoring module
        
        Args:
            model_path: Path to pre-trained model
            feature_mappings_file: Path to feature mappings file
            compliance_mappings_file: Path to compliance mappings file
        """
        try:
            # Initialize risk module
            # Uncomment when using actual implementation
            # self.risk_module = ExplainableRiskScoringModule(
            #     model_path=model_path,
            #     knowledge_base=self.knowledge_base
            # )
            
            # For demo purposes, create a placeholder
            self.risk_module = type('DummyRiskModule', (), {
                'assess_risk': lambda self, data: {'risk_score': 65, 'risk_level': {'name': 'high risk'}},
                'generate_recommendations': lambda self, assessment: [],
                'generate_risk_report': lambda self, assessment, recommendations, fmt: "Sample report"
            })()
            
            self.logger.info(f"Risk module initialized with model from {model_path}")
            
            # Load feature mappings
            if feature_mappings_file:
                feature_mappings_path = Path(feature_mappings_file)
                if feature_mappings_path.exists() and feature_mappings_path.is_file():
                    # Uncomment when using actual implementation
                    # self.risk_module.load_feature_mappings(feature_mappings_file)
                    # self.logger.info(f"Loaded feature mappings from {feature_mappings_file}")
                    self.logger.info(f"Feature mappings file found: {feature_mappings_file}")
            
            # Load compliance mappings
            if compliance_mappings_file:
                compliance_mappings_path = Path(compliance_mappings_file)
                if compliance_mappings_path.exists() and compliance_mappings_path.is_file():
                    # Uncomment when using actual implementation
                    # self.risk_module.load_compliance_mappings(compliance_mappings_file)
                    # self.logger.info(f"Loaded compliance mappings from {compliance_mappings_file}")
                    self.logger.info(f"Compliance mappings file found: {compliance_mappings_file}")
            
        except Exception as e:
            self.logger.error(f"Error loading risk module: {str(e)}")
    
    def _initialize_chatbot(self):
        """Initialize the security advisor chatbot"""
        try:
            # Initialize chatbot with loaded components
            # Uncomment when using actual implementation
            # self.chatbot = SecurityAdvisorChatbot(
            #     knowledge_base=self.knowledge_base,
            #     model_path=None  # We'll use our risk_module directly instead
            # )
            
            # For demo purposes, create a placeholder
            self.chatbot = type('DummyChatbot', (), {
                'process_message': lambda self, message, user_id=None, organization_id=None: {
                    'text': f"Processed: {message}",
                    'data': {}
                },
                'start_assessment': lambda self, data: "Assessment started"
            })()
            
            self.logger.info("Chatbot initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing chatbot: {str(e)}")
    
    def process_questionnaire(self, questionnaire_file, organization_id=None):
        """
        Process a security questionnaire and generate assessment
        
        Args:
            questionnaire_file: Path to questionnaire responses file (CSV or JSON)
            organization_id: Optional organization identifier
            
        Returns:
            Assessment result dictionary
        """
        try:
            # Load questionnaire data
            questionnaire_path = Path(questionnaire_file)
            
            if not questionnaire_path.exists():
                self.logger.error(f"Questionnaire file not found: {questionnaire_file}")
                return {'error': 'File not found'}
            
            # Load data based on file type
            if questionnaire_path.suffix.lower() == '.csv':
                questionnaire_data = pd.read_csv(questionnaire_path)
                # Convert to dictionary (use first row if multiple)
                questionnaire_dict = questionnaire_data.iloc[0].to_dict() if len(questionnaire_data) > 0 else {}
            
            elif questionnaire_path.suffix.lower() == '.json':
                with open(questionnaire_path, 'r') as f:
                    questionnaire_dict = json.load(f)
            
            else:
                self.logger.error(f"Unsupported file format: {questionnaire_path.suffix}")
                return {'error': 'Unsupported file format'}
            
            # Start assessment with chatbot
            if self.chatbot:
                self.chatbot.start_assessment(questionnaire_dict)
                self.logger.info(f"Started assessment for questionnaire: {questionnaire_file}")
            
            # Generate risk assessment
            if self.risk_module:
                assessment = self.risk_module.assess_risk(questionnaire_dict)
                self.logger.info(f"Generated risk assessment with score: {assessment.get('risk_score', 'N/A')}")
                
                # Generate recommendations
                recommendations = self.risk_module.generate_recommendations(assessment)
                self.logger.info(f"Generated {len(recommendations)} recommendations")
                
                # Generate report
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                org_prefix = f"{organization_id}_" if organization_id else ""
                
                # Save JSON report
                json_report_path = self.output_dir / f"{org_prefix}risk_assessment_{timestamp}.json"
                with open(json_report_path, 'w') as f:
                    json.dump({
                        'assessment': assessment,
                        'recommendations': recommendations,
                        'organization_id': organization_id,
                        'timestamp': timestamp
                    }, f, indent=2)
                
                # Save HTML report
                html_report = self.risk_module.generate_risk_report(assessment, recommendations, 'html')
                html_report_path = self.output_dir / f"{org_prefix}risk_assessment_{timestamp}.html"
                with open(html_report_path, 'w') as f:
                    f.write(html_report)
                
                self.logger.info(f"Saved assessment reports to {json_report_path} and {html_report_path}")
                
                # Return assessment result with paths
                return {
                    'assessment': assessment,
                    'recommendations': recommendations,
                    'reports': {
                        'json': str(json_report_path),
                        'html': str(html_report_path)
                    }
                }
            else:
                self.logger.error("Risk module not initialized")
                return {'error': 'Risk module not initialized'}
            
        except Exception as e:
            self.logger.error(f"Error processing questionnaire: {str(e)}")
            return {'error': str(e)}
    
    def process_message(self, message, user_id=None, organization_id=None):
        """
        Process a user message with the chatbot
        
        Args:
            message: User message text
            user_id: Optional user identifier
            organization_id: Optional organization identifier
            
        Returns:
            Response from chatbot
        """
        if not self.chatbot:
            self.logger.error("Chatbot not initialized")
            return {'text': "Chatbot not initialized", 'error': True}
        
        try:
            # Process message
            response = self.chatbot.process_message(
                message, 
                user_id=user_id,
                organization_id=organization_id
            )
            
            # Log message and response
            self.logger.info(f"User message: '{message}' -> Response: '{response['text'][:50]}...'")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return {'text': f"Error processing message: {str(e)}", 'error': True}
    
    def start_webserver(self, host='0.0.0.0', port=8000):
        """
        Start a web server for the chatbot UI
        
        Args:
            host: Host address to bind
            port: Port to bind
        """
        self.logger.info(f"Starting web server on {host}:{port}")
        
        # This would typically use Flask, FastAPI, or Streamlit
        # For this example, we'll just log a message
        self.logger.info("Web server functionality would be implemented here")
        self.logger.info("Consider using the provided Streamlit UI component instead")


def main():
    """Main entry point for the command-line interface"""
    parser = argparse.ArgumentParser(description='Security Advisor System')
    parser.add_argument('--model', help='Path to pre-trained risk model')
    parser.add_argument('--frameworks', help='Directory containing compliance framework files')
    parser.add_argument('--mappings', help='Path to control mappings file')
    parser.add_argument('--recommendations', help='Path to recommendation templates file')
    parser.add_argument('--feature-mappings', help='Path to feature mappings file')
    parser.add_argument('--compliance-mappings', help='Path to compliance mappings file')
    parser.add_argument('--output', help='Directory for output files', default='outputs')
    parser.add_argument('--questionnaire', help='Path to questionnaire file to process')
    parser.add_argument('--organization', help='Organization ID for the assessment')
    parser.add_argument('--server', action='store_true', help='Start web server')
    parser.add_argument('--port', type=int, default=8000, help='Port for web server')
    
    args = parser.parse_args()
    
    # Initialize system
    system = SecurityAdvisorSystem(
        model_path=args.model,
        frameworks_dir=args.frameworks,
        mappings_file=args.mappings,
        recommendations_file=args.recommendations,
        feature_mappings_file=args.feature_mappings,
        compliance_mappings_file=args.compliance_mappings,
        output_dir=args.output
    )
    
    # Process questionnaire if provided
    if args.questionnaire:
        result = system.process_questionnaire(args.questionnaire, args.organization)
        print(json.dumps(result, indent=2))
    
    # Start web server if requested
    if args.server:
        system.start_webserver(port=args.port)


if __name__ == "__main__":
    main()