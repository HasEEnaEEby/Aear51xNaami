"""
Security Compliance Advisor Chatbot
This module implements the core chatbot functionality for security compliance advising.
"""

import os
import json
import time
import pickle
import numpy as np
import re
import hashlib
from typing import Dict, List, Any, Union, Optional, Tuple
from datetime import datetime
import logging
from pathlib import Path

from core.compliance.policy_loader import PolicyLoader
from core.compliance.compliance_knowledge import ComplianceKnowledge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecurityComplianceChatbot:
    """
    Advanced chatbot for security compliance advising with semantic search capabilities
    """
    
    def __init__(
        self, 
        model_dir: str = None,
        api_key: str = None,  # Not used, kept for compatibility
        fine_tuned_model: str = None,  # Not used, kept for compatibility
        knowledge_base: Optional[ComplianceKnowledge] = None
    ):
        """
        Initialize the security compliance chatbot
        
        Args:
            model_dir: Directory containing model data
            api_key: Not used in this implementation, kept for compatibility
            fine_tuned_model: Not used in this implementation, kept for compatibility
            knowledge_base: Optional ComplianceKnowledge instance
        """
        self.model_dir = model_dir or os.path.join("data", "models")
        self.knowledge_base = knowledge_base or ComplianceKnowledge()
        
        # Load policy data
        self.policy_loader = PolicyLoader()
        self.policies = self.policy_loader.load_all_policies()
        
        # Load vector store if available
        self.vector_store = self._load_vector_store()
        
        # Chat history
        self.conversation_history = []
        
        # Load model metadata
        self._load_model_metadata()
    
    def _load_model_metadata(self):
        """Load chatbot model metadata"""
        metadata_path = os.path.join(self.model_dir, "chatbot_model_metadata.json")
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    self.model_metadata = json.load(f)
                
                logger.info(f"Loaded model metadata: {self.model_metadata}")
            except Exception as e:
                logger.error(f"Error loading model metadata: {str(e)}")
                self.model_metadata = {}
        else:
            logger.warning(f"No model metadata found at {metadata_path}")
            self.model_metadata = {}
    
    def _load_vector_store(self) -> Dict[str, Any]:
        """
        Load vector store for semantic search
        
        Returns:
            Vector store dictionary
        """
        vector_store_path = os.path.join(self.model_dir, "vector_store.pkl")
        if os.path.exists(vector_store_path):
            try:
                with open(vector_store_path, 'rb') as f:
                    vector_store = pickle.load(f)
                
                logger.info(f"Loaded vector store with {len(vector_store.get('embeddings', {}))} embeddings")
                return vector_store
            except Exception as e:
                logger.error(f"Error loading vector store: {str(e)}")
        
        logger.warning(f"No vector store found at {vector_store_path}")
        return {}
    
    async def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a text (No API version)
        
        Args:
            text: The text to embed
            
        Returns:
            Embedding vector
        """
        # Normalize text
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        
        # Generate a hash of the text
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert hash to a list of floats (pseudo-embedding)
        embedding = []
        for i in range(0, len(hash_hex), 2):
            if i+2 <= len(hash_hex):
                # Convert hex pair to int, then scale to [-1, 1]
                val = int(hash_hex[i:i+2], 16)
                scaled_val = (val / 127.5) - 1
                embedding.append(scaled_val)
        
        # Add some word-based features to improve similarity matching
        common_keywords = ["security", "privacy", "data", "control", "access", "risk", 
                          "compliance", "protection", "policy", "requirement", "audit",
                          "authentication", "authorization", "encryption", "network"]
        
        for keyword in common_keywords:
            # Add a feature based on word presence (1.0 if present, -1.0 if not)
            if keyword in text:
                embedding.append(1.0)
            else:
                embedding.append(-1.0)
                
        # Add term frequency features for common security terms
        for keyword in common_keywords:
            # Count occurrences and normalize
            count = text.count(keyword)
            norm_count = min(count / 5, 1.0)  # Cap at 1.0
            embedding.append(norm_count)
        
        # Use same length as in training
        desired_length = 128
        
        if len(embedding) < desired_length:
            # Pad with zeros
            embedding.extend([0.0] * (desired_length - len(embedding)))
        else:
            # Truncate
            embedding = embedding[:desired_length]
        
        return embedding
    
    def similarity_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find most similar policies for a query embedding
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of policy dictionaries with similarity scores
        """
        if not self.vector_store or not self.vector_store.get('embeddings'):
            logger.warning("No vector store available for similarity search")
            return []
        
        results = []
        
        try:
            # Convert embeddings dictionary to lists for vector operations
            policy_ids = list(self.vector_store['embeddings'].keys())
            embeddings = np.array([self.vector_store['embeddings'][pid] for pid in policy_ids])
            
            # Convert query to numpy array
            query_embedding = np.array(query_embedding)
            
            # Calculate cosine similarity
            similarities = []
            for i, embedding in enumerate(embeddings):
                # Normalize vectors
                norm_query = np.linalg.norm(query_embedding)
                norm_embedding = np.linalg.norm(embedding)
                
                # Avoid division by zero
                if norm_query == 0 or norm_embedding == 0:
                    similarities.append((i, 0))
                    continue
                
                # Calculate cosine similarity
                similarity = np.dot(query_embedding, embedding) / (norm_query * norm_embedding)
                similarities.append((i, similarity))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Get top k results
            for i, similarity in similarities[:top_k]:
                policy_id = policy_ids[i]
                
                # Get policy data
                if policy_id in self.vector_store.get('policies', {}):
                    policy = self.vector_store['policies'][policy_id]
                    
                    # Add to results
                    results.append({
                        "policy_id": policy_id,
                        "similarity": float(similarity),
                        "policy": policy
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            return []
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a user message and generate a response
        
        Args:
            message: User message text
            context: Additional context information
            
        Returns:
            Response dictionary
        """
        # Add message to conversation history
        user_message = {
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(user_message)
        
        # Get message embedding for semantic search
        query_embedding = await self.get_embedding(message)
        
        # Find relevant policies
        relevant_policies = self.similarity_search(query_embedding)
        
        # If no relevant policies found from vector search, try keyword search as fallback
        if not relevant_policies:
            keyword_results = self._keyword_search(message)
            relevant_policies = [
                {"policy_id": r["policy_id"], "similarity": r["score"]/10.0, "policy": r["policy"]}
                for r in keyword_results
            ]
        
        # Generate response based on message type and relevant policies
        response_text = self._generate_intelligent_response(message, relevant_policies, context)
        
        # Create response object
        response = {
            "text": response_text,
            "relevant_policies": [r["policy_id"] for r in relevant_policies],
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to conversation history
        assistant_message = {
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(assistant_message)
        
        return response
    
    def _generate_intelligent_response(self, message: str, relevant_policies: List[Dict[str, Any]], context: Dict[str, Any] = None) -> str:
        """
        Generate a response using rule-based approaches and relevant policies
        
        Args:
            message: User message text
            relevant_policies: List of relevant policies
            context: Additional context information
            
        Returns:
            Generated response text
        """
        message_lower = message.lower()
        
        # Check for specific question types
        if "what is" in message_lower or "tell me about" in message_lower or "explain" in message_lower:
            if relevant_policies:
                # Provide information about the most relevant policy
                return self._generate_explanation_response(relevant_policies)
            else:
                # Check for framework questions
                for framework_id in self.policy_loader.framework_summaries:
                    if framework_id.lower() in message_lower:
                        summary = self.policy_loader.get_framework_summary(framework_id)
                        return f"{summary.get('name', framework_id)} is {summary.get('description', 'a security compliance framework')}. It contains {summary.get('policy_count', 0)} controls or requirements across {len(summary.get('categories', []))} categories."
        
        elif "compare" in message_lower or "difference between" in message_lower or "vs" in message_lower:
            # Extract potential frameworks to compare
            framework_mentions = []
            for framework_id in self.policy_loader.framework_summaries:
                if framework_id.lower() in message_lower:
                    framework_mentions.append(framework_id)
            
            if len(framework_mentions) >= 2:
                # Generate comparison between frameworks
                return self._generate_comparison_response(framework_mentions[0], framework_mentions[1])
        
        elif "how do i implement" in message_lower or "how to implement" in message_lower:
            if relevant_policies:
                # Provide implementation guidance
                return self._generate_implementation_response(relevant_policies)
        
        elif "requirements" in message_lower or "controls" in message_lower:
            if relevant_policies:
                # Provide requirements information
                return self._generate_requirements_response(relevant_policies)
        
        # Default response based on relevant policies
        if relevant_policies:
            top_policy = relevant_policies[0]["policy"]
            
            framework = top_policy.get("framework", "")
            control_id = top_policy.get("control_id", "")
            title = top_policy.get("title", "")
            description = top_policy.get("description", "")
            
            response = f"Based on your question, I found information about {framework} {control_id}: {title}\n\n{description}\n\n"
            
            if "requirements" in top_policy:
                requirements = top_policy["requirements"]
                if isinstance(requirements, list):
                    req_text = "\n".join([f"- {req}" for req in requirements])
                else:
                    req_text = requirements
                    
                response += f"Requirements:\n{req_text}\n\n"
            
            if "implementation" in top_policy:
                response += f"Implementation guidance:\n{top_policy['implementation']}\n\n"
            
            response += "Would you like to know more about this or other related controls?"
            
            return response
        else:
            # No relevant policies found
            return """I don't have specific information about that in my knowledge base. 

I can provide information about security frameworks like NIST 800-53, ISO 27001, HIPAA, GDPR, PCI-DSS, and others. I can help with:

1. Explaining specific controls and requirements
2. Implementation guidance for security controls
3. Information about compliance frameworks
4. Comparisons between different frameworks

Please let me know which security or compliance topic you'd like me to cover."""
    
    def _generate_explanation_response(self, relevant_policies: List[Dict[str, Any]]) -> str:
        """Generate an explanation response based on relevant policies"""
        top_policy = relevant_policies[0]["policy"]
        
        framework = top_policy.get("framework", "")
        control_id = top_policy.get("control_id", "")
        title = top_policy.get("title", "")
        description = top_policy.get("description", "")
        
        response = f"{framework} {control_id}: {title}\n\n{description}\n\n"
        
        # Add category/family information if available
        category = top_policy.get("category", top_policy.get("family", ""))
        if category:
            response += f"Category: {category}\n\n"
        
        # Add additional context from other relevant policies
        if len(relevant_policies) > 1:
            response += "Related controls:\n"
            for i, rel in enumerate(relevant_policies[1:3]):  # Show up to 2 related controls
                rel_policy = rel["policy"]
                rel_framework = rel_policy.get("framework", "")
                rel_control_id = rel_policy.get("control_id", "")
                rel_title = rel_policy.get("title", "")
                
                response += f"- {rel_framework} {rel_control_id}: {rel_title}\n"
        
        return response
    
    def _generate_implementation_response(self, relevant_policies: List[Dict[str, Any]]) -> str:
        """Generate an implementation guidance response"""
        top_policy = relevant_policies[0]["policy"]
        
        framework = top_policy.get("framework", "")
        control_id = top_policy.get("control_id", "")
        title = top_policy.get("title", "")
        
        response = f"Implementation guidance for {framework} {control_id}: {title}\n\n"
        
        if "implementation" in top_policy and top_policy["implementation"]:
            response += f"{top_policy['implementation']}\n\n"
        elif "requirements" in top_policy:
            requirements = top_policy["requirements"]
            if isinstance(requirements, list):
                req_text = "\n".join([f"- {req}" for req in requirements])
            else:
                req_text = requirements
                
            response += f"To implement this control, address these requirements:\n{req_text}\n\n"
        else:
            response += "To implement this control:\n"
            response += "1. Review the control description and understand its purpose\n"
            response += "2. Develop policies and procedures that address the control\n"
            response += "3. Implement technical controls where applicable\n"
            response += "4. Train personnel on the implemented controls\n"
            response += "5. Monitor and verify the effectiveness of the control\n\n"
        
        response += "Would you like implementation guidance for any other controls?"
        
        return response
    
    def _generate_requirements_response(self, relevant_policies: List[Dict[str, Any]]) -> str:
        """Generate a requirements response"""
        top_policy = relevant_policies[0]["policy"]
        
        framework = top_policy.get("framework", "")
        control_id = top_policy.get("control_id", "")
        title = top_policy.get("title", "")
        
        response = f"Requirements for {framework} {control_id}: {title}\n\n"
        
        if "requirements" in top_policy:
            requirements = top_policy["requirements"]
            if isinstance(requirements, list):
                for i, req in enumerate(requirements):
                    response += f"{i+1}. {req}\n"
            else:
                response += f"{requirements}\n"
        else:
            # Extract requirements from description if no explicit requirements
            description = top_policy.get("description", "")
            response += f"Based on the description:\n{description}\n\n"
            
            # Add a generic note
            response += "Note: This control may have specific implementation requirements based on your organization's specific context and risk profile."
        
        return response
    
    def _generate_comparison_response(self, framework1: str, framework2: str) -> str:
        """Generate a comparison between two frameworks"""
        summary1 = self.policy_loader.get_framework_summary(framework1)
        summary2 = self.policy_loader.get_framework_summary(framework2)
        
        name1 = summary1.get("name", framework1)
        name2 = summary2.get("name", framework2)
        
        count1 = summary1.get("policy_count", 0)
        count2 = summary2.get("policy_count", 0)
        
        response = f"Comparison between {name1} and {name2}:\n\n"
        
        response += f"{name1}:\n"
        response += f"- {summary1.get('description', f'A security framework with {count1} controls')}\n"
        response += f"- Contains {count1} controls or requirements\n"
        if "categories" in summary1 and summary1["categories"]:
            cats1 = ", ".join(summary1["categories"][:3])
            response += f"- Key categories include: {cats1}" + ("..." if len(summary1["categories"]) > 3 else "") + "\n"
        
        response += f"\n{name2}:\n"
        response += f"- {summary2.get('description', f'A security framework with {count2} controls')}\n"
        response += f"- Contains {count2} controls or requirements\n"
        if "categories" in summary2 and summary2["categories"]:
            cats2 = ", ".join(summary2["categories"][:3])
            response += f"- Key categories include: {cats2}" + ("..." if len(summary2["categories"]) > 3 else "") + "\n"
        
        # Add simplified difference descriptions based on framework names
        response += "\nKey differences:\n"
        
        if "NIST" in framework1 and "ISO" in framework2:
            response += "- NIST is from the US National Institute of Standards and Technology, while ISO is from the International Organization for Standardization\n"
            response += "- NIST tends to be more prescriptive, while ISO is more principle-based\n"
        elif "ISO" in framework1 and "NIST" in framework2:
            response += "- ISO is from the International Organization for Standardization, while NIST is from the US National Institute of Standards and Technology\n"
            response += "- ISO is more principle-based, while NIST tends to be more prescriptive\n"
        elif "PCI" in framework1 or "PCI" in framework2:
            response += "- PCI DSS is specific to payment card security, while the other framework has broader security scope\n"
        elif "HIPAA" in framework1 or "HIPAA" in framework2:
            response += "- HIPAA is specific to healthcare data protection, while the other framework has broader security scope\n"
        elif "GDPR" in framework1 or "GDPR" in framework2:
            response += "- GDPR is focused on data privacy with an emphasis on individual rights, while the other framework may have broader security focus\n"
        else:
            response += "- They differ in scope, structure, and specific control requirements\n"
            response += "- They may be applicable to different types of organizations or industries\n"
        
        return response
    
    def clear_conversation_history(self):
        """Clear the conversation history"""
        self.conversation_history = []
    
    def get_framework_information(self, framework_id: str) -> Dict[str, Any]:
        """
        Get information about a specific framework
        
        Args:
            framework_id: Framework identifier
            
        Returns:
            Framework information dictionary
        """
        return self.policy_loader.get_framework_summary(framework_id)
    
    def get_control_information(self, framework_id: str, control_id: str) -> Dict[str, Any]:
        """
        Get information about a specific control
        
        Args:
            framework_id: Framework identifier
            control_id: Control identifier
            
        Returns:
            Control information dictionary
        """
        return self.policy_loader.get_policy_by_id(framework_id, control_id)
    
    def search_knowledge_base(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant policies
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching policies
        """
        # Use knowledge base search if available
        if self.knowledge_base:
            return self.knowledge_base.search_controls(query, top_k=limit)
        
        # Fallback to keyword search
        return self._keyword_search(query, limit)
    
    def _keyword_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Perform keyword search on policies
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching policies
        """
        results = []
        query_terms = query.lower().split()
        
        for policy in self.policies:
            score = 0
            
            # Search in title
            if "title" in policy:
                title = policy["title"].lower()
                for term in query_terms:
                    if term in title:
                        score += 3  # Higher weight for title matches
            
            # Search in description
            if "description" in policy:
                description = policy["description"].lower()
                for term in query_terms:
                    if term in description:
                        score += 1
            
            # Search in control ID
            control_id = policy.get("control_id", "").lower()
            framework = policy.get("framework", "").lower()
            
            for term in query_terms:
                if term == control_id or term in control_id:
                    score += 5  # Highest weight for exact control ID match
                
                if term == framework or term in framework:
                    score += 4  # High weight for framework match
            
            # Add to results if score > 0
            if score > 0:
                results.append({
                    "policy": policy,
                    "score": score,
                    "policy_id": f"{policy.get('framework', '')}:{policy.get('control_id', '')}"
                })
        
        # Sort by score and limit results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]