"""
Complete updated PolicyLoader that includes all required properties and methods
for compatibility with chatbot_trainer.py
"""
import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

class PolicyLoader:
    """Loads security compliance policy data from JSON files"""
    
    def __init__(self, policy_dir: str = None):
        """
        Initialize the PolicyLoader
        
        Args:
            policy_dir: Directory containing policy files (optional)
        """
        if policy_dir is None:
            # Default to data/policies in the project root
            self.policy_dir = os.path.join("data", "policies")
        else:
            self.policy_dir = policy_dir
            
        # Path to combined policies file
        self.combined_policies_path = os.path.join(self.policy_dir, "all_policies_with_embeddings.json")
        
        # Path to separate policies directory
        self.separate_policies_dir = os.path.join(self.policy_dir, "Seperate policies json")
        
        # Dictionary to store loaded policies by framework ID
        self.policies_by_framework = {}
        
        # Dictionary to store framework summaries (required by ChatbotTrainer)
        self.framework_summaries = {}
        
        # Dictionary to store frameworks (required by ChatbotTrainer)
        self.frameworks = {}
        
        # Load policies on initialization
        self.load_policies()
        
        # Update the frameworks and framework_summaries properties with loaded frameworks
        self.frameworks = self.get_all_framework_summaries()
        self.framework_summaries = self.frameworks  # Both point to the same data
    
    def load_policies(self) -> None:
        """Load all available policies from files"""
        logger.info(f"Loading combined policies from {self.combined_policies_path}")
        
        # Try to load combined policies file first
        combined_policies = self.load_combined_policies()
        if combined_policies:
            self.process_policies(combined_policies)
        
        # Load policies from individual files
        logger.info(f"Loading policies from individual files in {self.separate_policies_dir}")
        self.load_individual_policy_files()
    
    def load_all_policies(self) -> List[Dict[str, Any]]:
        """
        Load and return all policies from all frameworks
        
        Returns:
            List of all policy dictionaries
        """
        # If already loaded, gather all policies from self.policies_by_framework
        all_policies = []
        
        for framework_id, framework_data in self.policies_by_framework.items():
            policies = framework_data.get('policies', [])
            all_policies.extend(policies)
        
        # If no policies loaded yet, try to load them
        if not all_policies:
            self.load_policies()
            
            # Try again to gather all policies
            for framework_id, framework_data in self.policies_by_framework.items():
                policies = framework_data.get('policies', [])
                all_policies.extend(policies)
        
        return all_policies
    
    def generate_training_data(self) -> List[Dict[str, Any]]:
        """
        Generate training data for the chatbot
        
        Returns:
            List of training examples
        """
        training_data = []
        policies = self.load_all_policies()
        
        # Generate one example per policy
        for policy in policies:
            framework = policy.get('framework', '')
            control_id = policy.get('control_id', '')
            
            if not framework or not control_id:
                continue
                
            # Create a simple training example
            example = {
                "question": f"What is {framework} {control_id}?",
                "answer": self._generate_answer_for_policy(policy),
                "policy_id": f"{framework}:{control_id}",
                "framework": framework,
                "control_id": control_id
            }
            
            training_data.append(example)
            
            # Add a few more question variations
            variations = [
                f"Tell me about {framework} {control_id}",
                f"Explain {control_id} in {framework}",
                f"What are the requirements for {framework} {control_id}?"
            ]
            
            for question in variations[:2]:  # Limit to 2 variations to avoid too many examples
                example = {
                    "question": question,
                    "answer": self._generate_answer_for_policy(policy),
                    "policy_id": f"{framework}:{control_id}",
                    "framework": framework,
                    "control_id": control_id
                }
                training_data.append(example)
        
        # Add framework-level questions
        for framework_id, summary in self.frameworks.items():
            # Basic question about the framework
            example = {
                "question": f"What is {framework_id}?",
                "answer": self._generate_answer_for_framework(framework_id, summary),
                "policy_id": None,
                "framework": framework_id,
                "control_id": None
            }
            training_data.append(example)
            
        # Add some comparison questions if multiple frameworks exist
        framework_ids = list(self.frameworks.keys())
        if len(framework_ids) >= 2:
            for i in range(min(5, len(framework_ids) - 1)):
                fw1 = framework_ids[i]
                fw2 = framework_ids[i + 1]
                
                example = {
                    "question": f"Compare {fw1} and {fw2}",
                    "answer": self._generate_comparison_answer(fw1, fw2),
                    "policy_id": None,
                    "framework": [fw1, fw2],
                    "control_id": None
                }
                training_data.append(example)
                
        # Add general security and compliance questions
        general_questions = [
            {
                "question": "What are the key components of a security program?",
                "answer": "A security program typically includes risk assessment, security policies and procedures, access controls, security awareness training, incident response planning, business continuity and disaster recovery, security monitoring and testing, and compliance management."
            },
            {
                "question": "How do I start implementing a compliance program?",
                "answer": "To start implementing a compliance program: 1) Identify applicable regulations and frameworks, 2) Conduct a gap assessment, 3) Develop policies and procedures, 4) Implement required controls, 5) Train staff, 6) Monitor and test controls, 7) Document everything, and 8) Continuously improve."
            },
            {
                "question": "What is the difference between security and compliance?",
                "answer": "Security focuses on protecting systems, data, and operations from threats and attacks, while compliance involves meeting specific regulatory requirements and standards. Security is about actual protection, while compliance demonstrates adherence to defined rules and frameworks."
            }
        ]
        
        for item in general_questions:
            example = {
                "question": item["question"],
                "answer": item["answer"],
                "policy_id": None,
                "framework": None,
                "control_id": None
            }
            training_data.append(example)
            
        logger.info(f"Generated {len(training_data)} training examples")
        return training_data
    
    def _generate_answer_for_policy(self, policy: Dict[str, Any]) -> str:
        """
        Generate an answer about a specific policy
        
        Args:
            policy: Policy dictionary
            
        Returns:
            Generated answer
        """
        framework = policy.get('framework', '')
        control_id = policy.get('control_id', '')
        title = policy.get('title', '')
        description = policy.get('description', '')
        
        answer = f"{framework} {control_id}"
        if title:
            answer += f" - {title}"
        
        answer += "\n\n"
        
        if description:
            answer += f"{description}\n\n"
            
        # Add requirements if available
        requirements = policy.get('requirements', [])
        if requirements:
            answer += "Requirements:\n"
            if isinstance(requirements, list):
                for i, req in enumerate(requirements):
                    answer += f"{i+1}. {req}\n"
            else:
                answer += f"{requirements}\n"
                
        # Add implementation guidance if available
        implementation = policy.get('implementation', '')
        if implementation:
            answer += f"\nImplementation Guidance:\n{implementation}"
            
        return answer
    
    def _generate_answer_for_framework(self, framework_id: str, summary: Dict[str, Any]) -> str:
        """
        Generate an answer about a framework
        
        Args:
            framework_id: Framework ID
            summary: Framework summary dictionary
            
        Returns:
            Generated answer
        """
        name = summary.get('name', framework_id)
        description = summary.get('description', '')
        policy_count = summary.get('policy_count', 0)
        
        answer = f"{name} is a security and compliance framework"
        if description:
            answer += f" that {description}"
        
        answer += f". It contains {policy_count} controls or requirements."
        
        return answer
    
    def _generate_comparison_answer(self, framework1: str, framework2: str) -> str:
        """
        Generate an answer comparing two frameworks
        
        Args:
            framework1: First framework ID
            framework2: Second framework ID
            
        Returns:
            Generated answer
        """
        summary1 = self.frameworks.get(framework1, {})
        summary2 = self.frameworks.get(framework2, {})
        
        name1 = summary1.get('name', framework1)
        name2 = summary2.get('name', framework2)
        description1 = summary1.get('description', '')
        description2 = summary2.get('description', '')
        count1 = summary1.get('policy_count', 0)
        count2 = summary2.get('policy_count', 0)
        
        answer = f"Comparison of {name1} and {name2}:\n\n"
        
        answer += f"{name1}: "
        if description1:
            answer += f"{description1}. "
        answer += f"Contains {count1} controls.\n\n"
        
        answer += f"{name2}: "
        if description2:
            answer += f"{description2}. "
        answer += f"Contains {count2} controls.\n\n"
        
        # Add a general comparison
        answer += f"Key differences: {name1} has {count1} controls while {name2} has {count2} controls. "
        
        if count1 > count2:
            answer += f"{name1} is more comprehensive in terms of control count."
        elif count2 > count1:
            answer += f"{name2} is more comprehensive in terms of control count."
        else:
            answer += f"Both frameworks have the same number of controls, but they may focus on different aspects of security and compliance."
            
        return answer
    
    def export_training_data_to_jsonl(self, output_path: str) -> str:
        """
        Export training data to JSONL format
        
        Args:
            output_path: Path to save the JSONL file
            
        Returns:
            Path to the saved file
        """
        # Generate training data
        training_data = self.generate_training_data()
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write to JSONL
            with open(output_path, 'w', encoding='utf-8') as f:
                for example in training_data:
                    f.write(json.dumps(example) + '\n')
                    
            logger.info(f"Exported {len(training_data)} training examples to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting training data to JSONL: {str(e)}")
            return None
    
    def load_combined_policies(self) -> List[Dict[str, Any]]:
        """
        Load policies from the combined policies file
        
        Returns:
            List of policy dictionaries or empty list if file doesn't exist
        """
        if not os.path.exists(self.combined_policies_path):
            return []
            
        try:
            with open(self.combined_policies_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Handle both array and object formats
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'policies' in data:
                return data['policies']
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error loading combined policies: {str(e)}")
            return []
    
    def load_individual_policy_files(self) -> None:
        """Load policies from individual framework files"""
        if not os.path.exists(self.separate_policies_dir):
            return
            
        for filename in os.listdir(self.separate_policies_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.separate_policies_dir, filename)
                framework_id = filename.replace('.json', '')
                
                policies = self.load_policy_file(filepath, framework_id)
                if policies:
                    self.process_policies(policies)
    
    def load_policy_file(self, filepath: str, framework_id: str) -> List[Dict[str, Any]]:
        """
        Load policy data from a single file
        
        Args:
            filepath: Path to the policy file
            framework_id: ID of the framework
            
        Returns:
            List of policy dictionaries
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # FIX: Handle both list and dict formats for policy files
            policies = []
            
            if isinstance(data, list):
                # If the data is a list, process each item directly
                for item in data:
                    if isinstance(item, dict):
                        # Add framework_id if not present
                        if 'framework' not in item:
                            item['framework'] = framework_id
                        policies.append(item)
                    else:
                        logger.warning(f"Unexpected item type in {filepath}: {type(item)}")
            elif isinstance(data, dict):
                # If the data is a dictionary, look for policies key or use the dict itself
                if 'policies' in data and isinstance(data['policies'], list):
                    policies = data['policies']
                    # Add framework_id if not present in each policy
                    for policy in policies:
                        if 'framework' not in policy:
                            policy['framework'] = framework_id
                else:
                    # Treat the dict as a single policy
                    if 'framework' not in data:
                        data['framework'] = framework_id
                    policies.append(data)
            
            return policies
            
        except Exception as e:
            logger.error(f"Error loading {filepath}: {str(e)}")
            return []
    
    def process_policies(self, policies: List[Dict[str, Any]]) -> None:
        """
        Process loaded policies and organize by framework
        
        Args:
            policies: List of policy dictionaries
        """
        for policy in policies:
            if not isinstance(policy, dict):
                logger.warning(f"Skipping non-dictionary policy: {policy}")
                continue
                
            # Get the framework ID from the policy
            framework_id = policy.get('framework')
            if not framework_id:
                logger.warning(f"Policy missing framework ID: {policy}")
                continue
            
            # Initialize framework entry if it doesn't exist
            if framework_id not in self.policies_by_framework:
                self.policies_by_framework[framework_id] = {
                    'name': policy.get('framework_name', framework_id),
                    'description': policy.get('framework_description', ''),
                    'policies': []
                }
            
            # Add the policy to the framework
            self.policies_by_framework[framework_id]['policies'].append(policy)
    
    def get_all_framework_summaries(self) -> Dict[str, Dict[str, Any]]:
        """
        Get summaries of all loaded frameworks
        
        Returns:
            Dictionary mapping framework IDs to framework summaries
        """
        summaries = {}
        
        for framework_id, framework_data in self.policies_by_framework.items():
            summaries[framework_id] = {
                'name': framework_data.get('name', framework_id),
                'description': framework_data.get('description', ''),
                'policy_count': len(framework_data.get('policies', []))
            }
        
        return summaries
    
    def get_framework_policies(self, framework_id: str) -> List[Dict[str, Any]]:
        """
        Get all policies for a specific framework
        
        Args:
            framework_id: ID of the framework
            
        Returns:
            List of policy dictionaries
        """
        framework_data = self.policies_by_framework.get(framework_id, {})
        return framework_data.get('policies', [])
    
    def get_policy(self, framework_id: str, control_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific policy by framework and control ID
        
        Args:
            framework_id: ID of the framework
            control_id: ID of the control
            
        Returns:
            Policy dictionary or None if not found
        """
        policies = self.get_framework_policies(framework_id)
        
        for policy in policies:
            if policy.get('control_id') == control_id:
                return policy
        
        return None