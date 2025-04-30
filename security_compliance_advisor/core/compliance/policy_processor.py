# security_compliance_advisor/core/compliance/policy_processor.py

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import json
import logging

class PolicyProcessor:
    """
    Processes policy data for use in the security advisor chatbot.
    Handles embedding search, policy lookup, and recommendation generation.
    """
    
    def __init__(self, policies_file_path: str):
        """
        Initialize the policy processor
        
        Args:
            policies_file_path: Path to the policy data file (CSV with embeddings)
        """
        self.logger = logging.getLogger(__name__)
        self.policies = None
        self.embeddings = None
        self.load_policies(policies_file_path)
    
    def load_policies(self, file_path: str) -> None:
        """
        Load policy data from CSV file
        
        Args:
            file_path: Path to the policy data file
        """
        try:
            # Load the policy data
            df = pd.read_csv(file_path)
            
            # Extract embeddings if available
            if 'embedding' in df.columns:
                # Convert string representation of embedding to numpy arrays
                self.embeddings = np.array([
                    json.loads(embedding) if isinstance(embedding, str) else embedding 
                    for embedding in df['embedding']
                ])
                
                # Remove embedding column from policies dataframe
                policies_df = df.drop(columns=['embedding'])
                self.policies = policies_df
            else:
                self.policies = df
                self.logger.warning("No embedding column found in policy data")
            
            self.logger.info(f"Loaded {len(self.policies)} policies")
            
        except Exception as e:
            self.logger.error(f"Error loading policy data: {str(e)}")
            raise
    
    def search_policies(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search policies by semantic similarity to query
        
        Args:
            query: Search query string
            top_k: Number of results to return
            
        Returns:
            List of matching policy dictionaries
        """
        # This is where you'd implement semantic search using embeddings
        # For now, just do a simple keyword search as placeholder
        matches = []
        
        if self.policies is not None:
            # Simple keyword search as placeholder
            for _, row in self.policies.iterrows():
                # Convert row to dictionary
                policy = row.to_dict()
                
                # Check if query appears in statement or policy text
                statement = str(policy.get('statement', ''))
                policy_text = str(policy.get('policy_text', ''))
                
                if query.lower() in statement.lower() or query.lower() in policy_text.lower():
                    matches.append(policy)
                    
                if len(matches) >= top_k:
                    break
        
        return matches[:top_k]
    
    def get_relevant_policies(self, category: str) -> List[Dict[str, Any]]:
        """
        Get policies in a specific category
        
        Args:
            category: Policy category
            
        Returns:
            List of matching policy dictionaries
        """
        if self.policies is not None and 'category' in self.policies.columns:
            category_policies = self.policies[self.policies['category'] == category]
            return category_policies.to_dict('records')
        
        return []
    
    def get_policy_by_id(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific policy by ID
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            Policy dictionary or None if not found
        """
        if self.policies is not None and 'id' in self.policies.columns:
            policy = self.policies[self.policies['id'] == policy_id]
            if len(policy) > 0:
                return policy.iloc[0].to_dict()
        
        return None
    
    def find_applicable_policies(self, questionnaire_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find policies applicable to a given questionnaire response set
        
        Args:
            questionnaire_data: Dictionary of questionnaire responses
            
        Returns:
            List of applicable policy dictionaries
        """
        applicable_policies = []
        
        # This is where you'd implement more sophisticated policy matching
        # based on questionnaire responses
        # For now, just return a simple match based on MFA status as example
        
        if 'mfa_status' in questionnaire_data:
            mfa_status = questionnaire_data['mfa_status']
            # Example: If MFA not implemented, find MFA-related policies
            if mfa_status == "Not implemented":
                mfa_policies = self.search_policies("multi-factor authentication")
                applicable_policies.extend(mfa_policies)
        
        # Add more policy matching logic for other questionnaire responses
        
        return applicable_policies