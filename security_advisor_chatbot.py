import pandas as pd
import numpy as np
import json
import re
from datetime import datetime
from pathlib import Path
import os
import pickle
import shap
import xgboost as xgb
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

class SecurityAdvisorChatbot:
    def __init__(self, knowledge_base=None, model_path=None):
        """
        Initialize the security advisor chatbot
        
        Args:
            knowledge_base: ComplianceKnowledgeBase instance
            model_path: Path to trained risk assessment model
        """
        self.knowledge_base = knowledge_base
        self.risk_model = None
        self.explainer = None
        self.feature_names = None
        self.preprocessor = None
        self.conversation_history = []
        self.current_organization = None
        self.current_assessment = None
        self.user_profile = None
        
        # Load risk model if provided
        if model_path:
            self.load_risk_model(model_path)
    
    def load_risk_model(self, model_path):
        """
        Load the risk assessment model
        
        Args:
            model_path: Path to model directory
        """
        model_dir = Path(model_path)
        
        # Load the model pipeline
        with open(model_dir / "model_pipeline.pkl", "rb") as f:
            self.risk_model = pickle.load(f)
        
        # Extract preprocessor from pipeline
        if hasattr(self.risk_model, 'named_steps') and 'preprocessor' in self.risk_model.named_steps:
            self.preprocessor = self.risk_model.named_steps['preprocessor']
        
        # Load feature names
        with open(model_dir / "feature_names.json", "r") as f:
            self.feature_names = json.load(f)
        
        # Create explainer
        model = self.risk_model.named_steps['model'] if hasattr(self.risk_model, 'named_steps') else self.risk_model
        
        if isinstance(model, xgb.XGBRegressor):
            self.explainer = shap.TreeExplainer(model)
        else:
            self.explainer = shap.Explainer(model)
        
        return True
    
    def process_message(self, message, user_id=None, organization_id=None):
        """
        Process a user message and generate a response
        
        Args:
            message: User message text
            user_id: Optional user identifier
            organization_id: Optional organization identifier
            
        Returns:
            Response object with text and any additional data
        """
        # Add message to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'organization_id': organization_id,
            'message': message,
            'type': 'user'
        })
        
        # Set current organization if provided
        if organization_id:
            self.current_organization = organization_id
        
        # Parse intent from message
        intent, entities = self._parse_intent(message)
        
        # Generate response based on intent
        response = self._generate_response(intent, entities, message)
        
        # Add response to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'organization_id': organization_id,
            'message': response['text'],
            'type': 'bot',
            'data': response.get('data', {})
        })
        
        return response
    
    def _parse_intent(self, message):
        """
        Parse intent and entities from message
        
        Args:
            message: User message text
            
        Returns:
            Tuple of (intent, entities)
        """
        # Simple rule-based intent parsing
        # In a real system, you'd use NLU/NLP for this
        message_lower = message.lower()
        
        # Define intent patterns
        intent_patterns = {
            'greeting': [r'\bhello\b', r'\bhi\b', r'\bhey\b', r'\bgreetings\b'],
            'assess_risk': [r'\brisk\b.*\bassess', r'\bassess.*\brisk', r'\bevaluate\b.*\brisk', r'\brisk\b.*\bscore', r'\bsecurity\b.*\bposture'],
            'compliance_info': [r'\bcompliance\b', r'\bframework\b', r'\bstandard\b', r'\bregulation\b', r'\biso\b', r'\bnist\b', r'\bhipaa\b', r'\bgdpr\b'],
            'control_info': [r'\bcontrol\b', r'\brequirement\b', r'\bpolicy\b'],
            'recommendation': [r'\brecommend', r'\bsuggest', r'\badvice\b', r'\bmitigation\b', r'\bimprove\b'],
            'explain': [r'\bexplain\b', r'\bclarify\b', r'\bwhy\b', r'\bhow\b.*\bwork'],
            'compare': [r'\bcompare\b', r'\bdifference\b', r'\bvs\b', r'\bversus\b'],
            'help': [r'\bhelp\b', r'\bguide\b', r'\bassist\b'],
            'questionnaire': [r'\bquestionnaire\b', r'\bsurvey\b', r'\bform\b']
        }
        
        # Check for intents
        detected_intent = 'unknown'
        confidence = 0
        
        for intent, patterns in intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    detected_intent = intent
                    confidence = 0.8  # Arbitrary confidence score
                    break
            if detected_intent != 'unknown':
                break
        
        # Extract entities
        entities = self._extract_entities(message)
        
        # If we couldn't determine intent but found framework entities, assume compliance_info intent
        if detected_intent == 'unknown' and any(e['type'] == 'framework' for e in entities):
            detected_intent = 'compliance_info'
        
        return detected_intent, entities
    
    def _extract_entities(self, message):
        """
        Extract entities from message
        
        Args:
            message: User message text
            
        Returns:
            List of entity dictionaries
        """
        entities = []
        message_lower = message.lower()
        
        # Framework entities
        frameworks = {
            'iso': {'value': 'ISO27001', 'name': 'ISO 27001'},
            'iso 27001': {'value': 'ISO27001', 'name': 'ISO 27001'},
            'iso27001': {'value': 'ISO27001', 'name': 'ISO 27001'},
            'nist': {'value': 'NIST80053', 'name': 'NIST 800-53'},
            'nist 800-53': {'value': 'NIST80053', 'name': 'NIST 800-53'},
            'nist 800 53': {'value': 'NIST80053', 'name': 'NIST 800-53'},
            'nist80053': {'value': 'NIST80053', 'name': 'NIST 800-53'},
            'hipaa': {'value': 'HIPAA', 'name': 'HIPAA'},
            'gdpr': {'value': 'GDPR', 'name': 'GDPR'},
            'ccpa': {'value': 'CCPA', 'name': 'CCPA'},
            'pci': {'value': 'PCIDSS', 'name': 'PCI DSS'},
            'pci dss': {'value': 'PCIDSS', 'name': 'PCI DSS'},
            'pcidss': {'value': 'PCIDSS', 'name': 'PCI DSS'},
            'cis': {'value': 'CIS', 'name': 'CIS Controls'},
            'hitrust': {'value': 'HITRUST', 'name': 'HITRUST CSF'},
            'nist csf': {'value': 'NISTCSF', 'name': 'NIST CSF'},
            'nistcsf': {'value': 'NISTCSF', 'name': 'NIST CSF'},
            'scf': {'value': 'SCF', 'name': 'Secure Controls Framework'}
        }
        
        for key, info in frameworks.items():
            if re.search(r'\b' + key + r'\b', message_lower):
                entities.append({
                    'type': 'framework',
                    'value': info['value'],
                    'name': info['name']
                })
        
        # Risk category entities
        risk_categories = [
            'access control', 'authentication', 'encryption', 'network security',
            'patch management', 'backup', 'incident response', 'security policies',
            'training', 'physical security', 'vendor', 'compliance', 'audit',
            'data protection', 'endpoint security'
        ]
        
        for category in risk_categories:
            if re.search(r'\b' + category + r'\b', message_lower):
                entities.append({
                    'type': 'risk_category',
                    'value': category
                })
        
        # Control ID entities - this is a simplified pattern
        # In reality, you'd need more complex patterns for different framework control IDs
        control_patterns = [
            (r'(?:ISO|iso).*?([A-Z]\.\d+\.\d+\.\d+)', 'ISO'),  # ISO control pattern
            (r'(?:NIST|nist).*?([A-Z]{2}-\d+)', 'NIST'),        # NIST control pattern
            (r'\b([A-Z]{2}-\d+)\b', 'NIST')                     # Standalone NIST pattern
        ]
        
        for pattern, framework in control_patterns:
            matches = re.findall(pattern, message)
            for match in matches:
                entities.append({
                    'type': 'control',
                    'value': match,
                    'framework': framework
                })
        
        return entities
    
    def _generate_response(self, intent, entities, original_message):
        """
        Generate a response based on intent and entities
        
        Args:
            intent: Detected intent
            entities: Extracted entities
            original_message: Original user message
            
        Returns:
            Response object with text and any additional data
        """
        response = {
            'text': '',
            'data': {}
        }
        
        # Handle different intents
        if intent == 'greeting':
            response['text'] = self._generate_greeting()
        
        elif intent == 'assess_risk':
            response['text'], response['data'] = self._handle_risk_assessment(entities)
        
        elif intent == 'compliance_info':
            response['text'] = self._handle_compliance_info(entities)
        
        elif intent == 'control_info':
            response['text'] = self._handle_control_info(entities)
        
        elif intent == 'recommendation':
            response['text'], response['data'] = self._handle_recommendation(entities)
        
        elif intent == 'explain':
            response['text'] = self._handle_explanation(entities, original_message)
        
        elif intent == 'compare':
            response['text'] = self._handle_comparison(entities)
        
        elif intent == 'help':
            response['text'] = self._generate_help()
        
        elif intent == 'questionnaire':
            response['text'] = self._handle_questionnaire(entities)
        
        else:
            response['text'] = "I'm not sure I understand. Could you rephrase your question? You can ask about risk assessments, compliance frameworks, security controls, or recommendations."
        
        return response
    
    def _generate_greeting(self):
        """Generate a greeting response"""
        greetings = [
            "Hello! I'm your Security and Compliance Advisor. How can I help you today?",
            "Hi there! I'm here to help with your security and compliance questions. What would you like to know?",
            "Welcome! I can assist with risk assessments, compliance information, and security recommendations. What do you need help with?"
        ]
        return np.random.choice(greetings)
    
    def _handle_risk_assessment(self, entities):
        """
        Handle risk assessment intent
        
        Args:
            entities: Extracted entities
            
        Returns:
            Tuple of (response_text, response_data)
        """
        # Check if we have a risk model
        if self.risk_model is None:
            return "I need a trained risk model to perform risk assessments. Please provide questionnaire data first.", {}
        
        # Check if we have current assessment data
        if self.current_assessment is None:
            return "I don't have any assessment data for your organization. Would you like to start a new assessment by filling out a questionnaire?", {}
        
        # Use the risk model to generate a score
        try:
            # Get relevant data for prediction
            assessment_data = pd.DataFrame([self.current_assessment])
            
            # Make prediction
            risk_score = float(self.risk_model.predict(assessment_data)[0])
            
            # Generate explanation
            explanation = self._explain_risk_score(assessment_data)
            
            # Format response data
            response_data = {
                'risk_score': risk_score,
                'risk_level': self._risk_level_from_score(risk_score),
                'explanation': explanation,
                'timestamp': datetime.now().isoformat()
            }
            
            # Generate text response
            response_text = f"Your organization's security risk score is {risk_score:.1f}/100, which is considered {response_data['risk_level']['name']}.\n\n"
            response_text += f"{response_data['risk_level']['description']}\n\n"
            response_text += "Key factors affecting your score:\n"
            
            # Add top positive and negative factors
            for factor in explanation['top_factors'][:3]:
                response_text += f"• {factor['description']} ({factor['impact']:+.1f} points)\n"
            
            response_text += "\nWould you like to see detailed recommendations for improving your security posture?"
            
            return response_text, response_data
            
        except Exception as e:
            return f"I encountered an error while generating your risk assessment: {str(e)}", {}
    
    def _explain_risk_score(self, assessment_data):
        """
        Generate explanation for risk score
        
        Args:
            assessment_data: DataFrame with assessment data
            
        Returns:
            Explanation dictionary
        """
        if self.explainer is None:
            return {"error": "Explainer not available"}
        
        try:
            # Process data through preprocessor if available
            if self.preprocessor:
                processed_data = self.preprocessor.transform(assessment_data)
            else:
                processed_data = assessment_data
            
            # Generate SHAP values
            shap_values = self.explainer(processed_data)
            
            # Extract and sort factors by importance
            factors = []
            
            for i in range(len(shap_values.values[0])):
                shap_value = shap_values.values[0][i]
                
                # Skip factors with minimal impact
                if abs(shap_value) < 0.1:
                    continue
                
                # Get feature name
                feature_name = self.feature_names[i] if i < len(self.feature_names) else f"Feature {i}"
                
                # Get human-readable description
                description = self._feature_to_description(feature_name)
                
                factors.append({
                    'feature': feature_name,
                    'description': description,
                    'impact': float(shap_value),
                    'direction': 'positive' if shap_value < 0 else 'negative'
                })
            
            # Sort by absolute impact
            factors.sort(key=lambda x: abs(x['impact']), reverse=True)
            
            # Group factors by category
            categorized_factors = {}
            for factor in factors:
                category = self._get_factor_category(factor['feature'])
                if category not in categorized_factors:
                    categorized_factors[category] = []
                categorized_factors[category].append(factor)
            
            return {
                'top_factors': factors[:10],
                'categories': categorized_factors
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _feature_to_description(self, feature_name):
        """
        Convert feature name to human-readable description
        
        Args:
            feature_name: Technical feature name
            
        Returns:
            Human-readable description
        """
        # Remove prefixes like 'text_', 'num_', 'cat_'
        clean_name = re.sub(r'^(text_|num_|cat_)', '', feature_name)
        
        # Replace underscores with spaces
        clean_name = clean_name.replace('_', ' ')
        
        # Make first letter uppercase
        clean_name = clean_name.capitalize()
        
        # Map to known question if available
        if hasattr(self, 'question_mapping') and clean_name in self.question_mapping:
            return self.question_mapping[clean_name]
        
        return clean_name
    
    def _get_factor_category(self, feature_name):
        """
        Get category for a feature
        
        Args:
            feature_name: Feature name
            
        Returns:
            Category name
        """
        # Simple keyword mapping
        keywords = {
            'password': 'Access Control',
            'auth': 'Authentication',
            'encrypt': 'Encryption',
            'network': 'Network Security',
            'patch': 'Patch Management',
            'backup': 'Backup and Recovery',
            'incident': 'Incident Response',
            'policy': 'Security Policies',
            'train': 'Security Awareness',
            'physical': 'Physical Security',
            'vendor': 'Third-Party Risk',
            'compliance': 'Compliance',
            'audit': 'Audit and Logging',
            'data': 'Data Protection',
            'device': 'Endpoint Security'
        }
        
        feature_lower = feature_name.lower()
        
        for keyword, category in keywords.items():
            if keyword in feature_lower:
                return category
        
        return 'Other'
    
    def _risk_level_from_score(self, score):
        """
        Convert numerical score to risk level
        
        Args:
            score: Numerical risk score (0-100)
            
        Returns:
            Risk level dictionary
        """
        if score < 20:
            return {
                'name': 'very low risk',
                'description': 'Your security posture is excellent with minimal areas for improvement.',
                'color': 'green'
            }
        elif score < 40:
            return {
                'name': 'low risk',
                'description': 'Your security posture is good with a few minor areas for improvement.',
                'color': 'blue'
            }
        elif score < 60:
            return {
                'name': 'moderate risk',
                'description': 'Your security posture needs attention in several key areas.',
                'color': 'yellow'
            }
        elif score < 80:
            return {
                'name': 'high risk',
                'description': 'Your security posture has significant vulnerabilities that need immediate attention.',
                'color': 'orange'
            }
        else:
            return {
                'name': 'critical risk',
                'description': 'Your security posture has critical vulnerabilities requiring urgent remediation.',
                'color': 'red'
            }
    
    def _handle_compliance_info(self, entities):
        """
        Handle compliance information request
        
        Args:
            entities: Extracted entities
            
        Returns:
            Response text
        """
        # Check if we have knowledge base
        if self.knowledge_base is None:
            return "I need a compliance knowledge base to provide information about frameworks. Please make sure it's loaded."
        
        # Check if specific frameworks were mentioned
        framework_entities = [e for e in entities if e['type'] == 'framework']
        
        if not framework_entities:
            # No specific framework mentioned, provide general information
            frameworks_list = ', '.join([f"{f}" for f in self.knowledge_base.frameworks.keys()])
            return f"I can provide information about various compliance frameworks including {frameworks_list}. Which framework would you like to know more about?"
        
        # Provide information about the requested frameworks
        responses = []
        
        for entity in framework_entities:
            framework_id = entity['value']
            if framework_id in self.knowledge_base.frameworks:
                framework = self.knowledge_base.frameworks[framework_id]
                responses.append(f"{entity['name']} ({framework_id}): {framework.get('description', 'No description available')}.\n")
                
                # Add control count if available
                control_count = len(framework.get('controls', {}))
                if control_count > 0:
                    responses.append(f"It consists of {control_count} controls across multiple categories.\n")
                
                # Add categories if available
                categories = set()
                for control in framework.get('controls', {}).values():
                    if 'category' in control:
                        categories.add(control['category'])
                
                if categories:
                    categories_list = ', '.join(sorted(categories))
                    responses.append(f"Key categories include: {categories_list}.\n")
            else:
                responses.append(f"I don't have detailed information about {entity['name']} in my knowledge base.\n")
        
        if len(responses) > 0:
            return ''.join(responses)
        else:
            return "I couldn't find information about the requested compliance frameworks. Please specify which framework you're interested in."
    
    def _handle_control_info(self, entities):
        """
        Handle control information request
        
        Args:
            entities: Extracted entities
            
        Returns:
            Response text
        """
        # Check if we have knowledge base
        if self.knowledge_base is None:
            return "I need a compliance knowledge base to provide information about controls. Please make sure it's loaded."
        
        # Check if specific controls were mentioned
        control_entities = [e for e in entities if e['type'] == 'control']
        
        if not control_entities:
            # Check if frameworks were mentioned
            framework_entities = [e for e in entities if e['type'] == 'framework']
            
            if framework_entities:
                # Mention some controls from this framework
                framework_id = framework_entities[0]['value']
                if framework_id in self.knowledge_base.frameworks:
                    controls = list(self.knowledge_base.frameworks[framework_id].get('controls', {}).items())
                    if controls:
                        sample_controls = controls[:3]
                        controls_list = ', '.join([f"{c[0]}" for c in sample_controls])
                        return f"The {framework_entities[0]['name']} framework includes controls such as {controls_list}. Which specific control would you like information about?"
            
            return "Please specify which control you'd like information about. For example, 'Tell me about ISO 27001 A.5.1.1' or 'What is NIST 800-53 AC-1?'"
        
        # Provide information about the requested controls
        responses = []
        
        for entity in control_entities:
            framework_id = entity.get('framework')
            control_id = entity['value']
            
            if framework_id:
                # Look for specific control in framework
                full_control_id = f"{framework_id}:{control_id}"
                control = self.knowledge_base.controls.get(full_control_id)
                
                if control:
                    responses.append(f"{framework_id} {control_id}: {control.get('title', 'No title available')}\n")
                    responses.append(f"Description: {control.get('description', 'No description available')}\n")
                    
                    # Add category if available
                    if 'category' in control:
                        responses.append(f"Category: {control['category']}\n")
                    
                    # Add related controls if available
                    related_controls = self.knowledge_base.get_mapped_controls(framework_id, control_id)
                    if related_controls:
                        related_list = ', '.join(related_controls[:3])
                        responses.append(f"Related controls in other frameworks: {related_list}\n")
                else:
                    responses.append(f"I couldn't find control {control_id} in the {framework_id} framework.\n")
            else:
                # Search across all frameworks
                found = False
                for framework_id, framework in self.knowledge_base.frameworks.items():
                    if control_id in framework.get('controls', {}):
                        control = framework['controls'][control_id]
                        responses.append(f"{framework_id} {control_id}: {control.get('title', 'No title available')}\n")
                        responses.append(f"Description: {control.get('description', 'No description available')}\n")
                        found = True
                        break
                
                if not found:
                    responses.append(f"I couldn't find control {control_id} in any framework.\n")
        
        if len(responses) > 0:
            return ''.join(responses)
        else:
            return "I couldn't find information about the requested controls. Please check the control IDs and try again."
    
    def _handle_recommendation(self, entities):
        """
        Handle recommendation request
        
        Args:
            entities: Extracted entities
            
        Returns:
            Tuple of (response_text, response_data)
        """
        # Check if we have current assessment
        if self.current_assessment is None:
            return "I need assessment data to provide tailored recommendations. Would you like to start a new assessment?", {}
        
        # Check if we have risk model and knowledge base
        if self.risk_model is None or self.knowledge_base is None:
            return "I need both a risk model and compliance knowledge base to provide recommendations.", {}
        
        # Generate risk assessment if not already done
        if not hasattr(self, 'last_assessment') or not self.last_assessment:
            assessment_data = pd.DataFrame([self.current_assessment])
            risk_score = float(self.risk_model.predict(assessment_data)[0])
            explanation = self._explain_risk_score(assessment_data)
            self.last_assessment = {
                'risk_score': risk_score,
                'risk_level': self._risk_level_from_score(risk_score),
                'explanation': explanation,
                'timestamp': datetime.now().isoformat()
            }
        
        # Check if specific category was requested
        category_entities = [e for e in entities if e['type'] == 'risk_category']
        
        recommendations = []
        
        if category_entities:
            # Provide recommendations for specific categories
            for entity in category_entities:
                category = entity['value'].title()
                category_recommendations = self._generate_recommendations_for_category(
                    category, 
                    self.last_assessment['risk_level']['name'],
                    self.last_assessment['explanation']
                )
                recommendations.extend(category_recommendations)
        else:
            # Provide recommendations across categories
            # Get top 3 categories from risk assessment
            categories = []
            for category, factors in self.last_assessment['explanation'].get('categories', {}).items():
                if factors:
                    # Calculate total impact for category
                    total_impact = sum(abs(f['impact']) for f in factors)
                    categories.append((category, total_impact))
            
            # Sort by total impact
            categories.sort(key=lambda x: x[1], reverse=True)
            
            # Get recommendations for top categories
            for category, _ in categories[:3]:
                category_recommendations = self._generate_recommendations_for_category(
                    category, 
                    self.last_assessment['risk_level']['name'],
                    self.last_assessment['explanation']
                )
                recommendations.extend(category_recommendations)
        
        # Format response
        response_data = {
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
        
        response_text = "Based on your security assessment, here are my recommendations:\n\n"
        
        for i, rec in enumerate(recommendations[:5]):
            response_text += f"{i+1}. {rec['title']}\n"
            response_text += f"   {rec['description']}\n"
            response_text += f"   Impact: {rec['impact']} | Effort: {rec['effort']}\n\n"
        
        if len(recommendations) > 5:
            response_text += f"I have {len(recommendations)} total recommendations. Would you like to see more?"
        
        return response_text, response_data
    
    def _generate_recommendations_for_category(self, category, risk_level, explanation):
        """
        Generate recommendations for a specific category
        
        Args:
            category: Category name
            risk_level: Risk level
            explanation: Risk explanation
            
        Returns:
            List of recommendation dictionaries
        """
        # Map risk level to recommendation level
        level_mapping = {
            'very low risk': 'low',
            'low risk': 'low',
            'moderate risk': 'medium',
            'high risk': 'high',
            'critical risk': 'high'
        }
        rec_level = level_mapping.get(risk_level, 'medium')
        
        # Get template from knowledge base if available
        template = ""
        if self.knowledge_base and hasattr(self.knowledge_base, 'get_recommendation_template'):
            template = self.knowledge_base.get_recommendation_template(category, rec_level)
        
        # Create recommendations
        recommendations = []
        
        # Add template-based recommendation if available
        if template:
            recommendations.append({
                'title': f"Improve {category}",
                'description': template,
                'category': category,
                'impact': 'High' if rec_level == 'high' else ('Medium' if rec_level == 'medium' else 'Low'),
                'effort': 'Medium',
                'source': 'template'
            })
        
        # Add factor-specific recommendations
        factors = explanation.get('categories', {}).get(category, [])
        for factor in factors:
            if factor['direction'] == 'negative':
                # This factor increased risk, recommend fixing it
                recommendations.append({
                    'title': f"Address {self._feature_to_description(factor['feature'])}",
                    'description': f"Improve your security posture by addressing the issue with {factor['description']}.",
                    'category': category,
                    'impact': 'High' if abs(factor['impact']) > 5 else ('Medium' if abs(factor['impact']) > 2 else 'Low'),
                    'effort': 'Medium',
                    'source': 'factor',
                    'factor': factor
                })
        
        return recommendations
    
    def _handle_explanation(self, entities, original_message):
        """
        Handle explanation request
        
        Args:
            entities: Extracted entities
            original_message: Original user message
            
        Returns:
            Response text
        """
        # Check what user is asking to explain
        message_lower = original_message.lower()
        
        if 'risk' in message_lower and ('score' in message_lower or 'assessment' in message_lower):
            # Explain risk score
            if not hasattr(self, 'last_assessment') or not self.last_assessment:
                return "I haven't performed a risk assessment yet. Would you like me to do that?"
            
            explanation = self.last_assessment['explanation']
            risk_score = self.last_assessment['risk_score']
            risk_level = self.last_assessment['risk_level']
            
            response = f"Your risk score of {risk_score:.1f} is calculated based on your responses to the security questionnaire. Here's how different factors contributed to this score:\n\n"
            
            # Add top positive factors
            positive_factors = [f for f in explanation['top_factors'] if f['direction'] == 'positive']
            if positive_factors:
                response += "Positive factors that reduced your risk:\n"
                for factor in positive_factors[:3]:
                    response += f"• {factor['description']} reduced your risk by {abs(factor['impact']):.1f} points\n"
                response += "\n"
            
            # Add top negative factors
            negative_factors = [f for f in explanation['top_factors'] if f['direction'] == 'negative']
            if negative_factors:
                response += "Negative factors that increased your risk:\n"
                for factor in negative_factors[:3]:
                    response += f"• {factor['description']} increased your risk by {factor['impact']:.1f} points\n"
                response += "\n"
            
            return response
            
        elif any(keyword in message_lower for keyword in ['framework', 'standard', 'regulation', 'compliance']):
            # Explain compliance framework
            framework_entities = [e for e in entities if e['type'] == 'framework']
            
            if not framework_entities:
                # No specific framework mentioned
                return "Compliance frameworks are standardized approaches to security and privacy that organizations follow to protect their data and systems. Examples include ISO 27001, NIST 800-53, HIPAA, GDPR, and PCI DSS. Which framework would you like me to explain?"
            
            # Use the compliance info handler
            return self._handle_compliance_info(entities)
            
        elif 'control' in message_lower:
            # Explain control
            return self._handle_control_info(entities)
            
        elif 'recommendation' in message_lower:
            # Explain recommendation logic
            return "My recommendations are based on your risk assessment results. I identify the areas with the highest risk factors and suggest mitigation strategies based on industry best practices and compliance requirements. The recommendations are prioritized by their potential impact on reducing your overall risk score."
            
        else:
            return "I can explain various aspects of security and compliance. What specifically would you like me to explain? For example, you can ask about your risk score, compliance frameworks, specific controls, or how recommendations are generated."
    
    def _handle_comparison(self, entities):
        """
        Handle comparison request
        
        Args:
            entities: Extracted entities
            
        Returns:
            Response text
        """
        # Check if comparing frameworks
        framework_entities = [e for e in entities if e['type'] == 'framework']
        
        if len(framework_entities) >= 2:
            # Compare frameworks
            framework1 = framework_entities[0]
            framework2 = framework_entities[1]
            
            response = f"Comparing {framework1['name']} and {framework2['name']}:\n\n"
            
            # Check if we have knowledge base
            if self.knowledge_base is None:
                return response + "I need a compliance knowledge base to provide detailed comparisons."
            
            # Get framework details
            f1_data = self.knowledge_base.frameworks.get(framework1['value'])
            f2_data = self.knowledge_base.frameworks.get(framework2['value'])
            
            if not f1_data or not f2_data:
                return response + "I don't have detailed information about one or both frameworks."
            
            # Compare scope
            response += "Scope and Focus:\n"
            response += f"• {framework1['name']}: {f1_data.get('description', 'No description available')}\n"
            response += f"• {framework2['name']}: {f2_data.get('description', 'No description available')}\n\n"
            
            # Compare structure
            f1_controls = len(f1_data.get('controls', {}))
            f2_controls = len(f2_data.get('controls', {}))
            
            response += "Structure:\n"
            response += f"• {framework1['name']} has {f1_controls} controls\n"
            response += f"• {framework2['name']} has {f2_controls} controls\n\n"
            
            # Compare categories
            f1_categories = set()
            for control in f1_data.get('controls', {}).values():
                if 'category' in control:
                    f1_categories.add(control['category'])
                    
            f2_categories = set()
            for control in f2_data.get('controls', {}).values():
                if 'category' in control:
                    f2_categories.add(control['category'])
            
            common_categories = f1_categories.intersection(f2_categories)
            
            response += "Common Categories:\n"
            for category in common_categories:
                response += f"• {category}\n"
            
            return response
        
        elif len(framework_entities) == 1:
            return f"To compare frameworks, please mention at least two. You've only mentioned {framework_entities[0]['name']}. Which other framework would you like to compare it with?"
        
        else:
            return "I can compare different compliance frameworks for you. Please specify which frameworks you'd like to compare, for example: 'Compare ISO 27001 and NIST 800-53' or 'What's the difference between GDPR and CCPA?'"
    
    def _generate_help(self):
        """Generate help response"""
        help_text = "I'm your Security and Compliance Advisor. Here's how I can help you:\n\n"
        help_text += "• Assess your security risk based on questionnaire responses\n"
        help_text += "• Provide information about compliance frameworks (ISO, NIST, HIPAA, GDPR, etc.)\n"
        help_text += "• Explain specific security controls and requirements\n"
        help_text += "• Generate recommendations to improve your security posture\n"
        help_text += "• Compare different compliance frameworks\n"
        help_text += "• Explain how risk scores and recommendations are calculated\n\n"
        help_text += "What would you like to know about?"
        
        return help_text
    
    def _handle_questionnaire(self, entities):
        """
        Handle questionnaire intent
        
        Args:
            entities: Extracted entities
            
        Returns:
            Response text
        """
        return "I can help you with security questionnaires. You can upload your questionnaire responses for analysis, or I can provide a template questionnaire covering key security controls. Would you like me to provide a template, or would you prefer to upload your own data?"
    
    def start_assessment(self, questionnaire_data):
        """
        Start a new assessment with questionnaire data
        
        Args:
            questionnaire_data: Dictionary of questionnaire responses
            
        Returns:
            Success message
        """
        self.current_assessment = questionnaire_data
        self.last_assessment = None  # Clear any previous assessment
        
        return "Assessment data received. You can now ask me to assess your risk, provide recommendations, or explain specific security controls."
    
    def get_assessment_summary(self):
        """
        Get summary of current assessment
        
        Returns:
            Assessment summary dictionary
        """
        if not hasattr(self, 'last_assessment') or not self.last_assessment:
            return {"error": "No assessment has been performed yet"}
        
        return self.last_assessment
    
    def save_conversation(self, filepath):
        """
        Save conversation history to file
        
        Args:
            filepath: Path to save file
            
        Returns:
            Success message
        """
        with open(filepath, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
        
        return f"Conversation saved to {filepath}"
    
    def load_question_mapping(self, mapping_data):
        """
        Load question mapping data
        
        Args:
            mapping_data: Dictionary mapping feature names to questions
            
        Returns:
            Success message
        """
        self.question_mapping = mapping_data
        return f"Loaded {len(mapping_data)} question mappings"


# Example usage
if __name__ == "__main__":
    # Initialize chatbot
    chatbot = SecurityAdvisorChatbot()
    
    # Process a sample message
    response = chatbot.process_message("Hello, I need help with security compliance")
    print(f"Bot: {response['text']}")
    
    # Process another message
    response = chatbot.process_message("Can you tell me about ISO 27001?")
    print(f"Bot: {response['text']}")