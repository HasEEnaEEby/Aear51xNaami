"""
Chatbot Trainer for Security Compliance Advisor
This module handles training of the security compliance chatbot without requiring external APIs.
"""

import os
import json
import time
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
import re
import hashlib

from core.compliance.policy_loader import PolicyLoader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChatbotTrainer:
    """
    Trainer for security compliance chatbot (No API version)
    """
    
    def __init__(self, model_dir: str = None, api_key: str = None):
        """
        Initialize the chatbot trainer
        
        Args:
            model_dir: Directory for saving model data
            api_key: Not used in this implementation, kept for compatibility
        """
        self.model_dir = model_dir or os.path.join("data", "models")
        self.policy_loader = PolicyLoader()
        
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.embedding_cache = {}
        self.embeddings_loaded = False
    
    def train(self, force_retrain: bool = False) -> bool:
        """
        Train the chatbot model
        
        Args:
            force_retrain: Force retraining even if model exists
            
        Returns:
            Success indicator
        """
        logger.info("Starting chatbot training process (No API mode)")
        
        model_file = os.path.join(self.model_dir, "chatbot_model_metadata.json")
        if os.path.exists(model_file) and not force_retrain:
            logger.info(f"Model already exists at {model_file}, skipping training")
            return True
        
        # Step 1: Load policies
        logger.info("Loading policy data")
        policies = self.policy_loader.load_all_policies()
        if not policies:
            logger.error("No policy data found, cannot train model")
            return False
        
        logger.info(f"Loaded {len(policies)} policies from {len(self.policy_loader.frameworks)} frameworks")
        
        # Step 2: Generate training data
        logger.info("Generating training data")
        training_data = self.policy_loader.generate_training_data()
        
        # Step 3: Save training data
        training_path = os.path.join(self.model_dir, "training_data.json")
        with open(training_path, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2)
        
        # Export to JSONL format as well
        jsonl_path = self.policy_loader.export_training_data_to_jsonl(
            os.path.join(self.model_dir, "chatbot_training_data.jsonl")
        )
        
        # Step 4: Generate embeddings for policies
        logger.info("Generating simple embeddings for policies")
        embeddings_success = self._generate_embeddings(policies)
        if not embeddings_success:
            logger.warning("Failed to generate embeddings, continuing without them")
        
        # Step 5: Save model metadata
        metadata = {
            "trained_at": datetime.now().isoformat(),
            "num_policies": len(policies),
            "num_training_examples": len(training_data),
            "frameworks": list(self.policy_loader.frameworks.keys()),
            "has_embeddings": embeddings_success,
            "training_data_path": training_path,
            "jsonl_path": jsonl_path,
            "model_type": "no_api_mode"
        }
        
        with open(model_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Chatbot training completed, model metadata saved to {model_file}")
        return True
    
    def _generate_embeddings(self, policies: List[Dict[str, Any]]) -> bool:
        """
        Generate embeddings for policies without external API
        
        Args:
            policies: List of policy dictionaries
            
        Returns:
            Success indicator
        """
        try:
            logger.info("Generating simple embeddings (No API mode)")
            
            # Check if embeddings already exist in policies
            existing_embeddings = 0
            for policy in policies:
                if "embedding" in policy and policy["embedding"]:
                    existing_embeddings += 1
            
            if existing_embeddings == len(policies):
                logger.info(f"All {len(policies)} policies already have embeddings")
                return True
            
            logger.info(f"Found {existing_embeddings} existing embeddings, generating missing embeddings")
            
            # Generate embeddings for policies without them
            updated_count = 0
            for i, policy in enumerate(policies):
                if "embedding" not in policy or not policy["embedding"]:
                    # Create text for embedding
                    text = self._create_embedding_text(policy)
                    
                    # Generate simple embedding using hash-based approach
                    embedding = self._generate_simple_embedding(text)
                    
                    if embedding:
                        policy["embedding"] = embedding
                        updated_count += 1
                    
                    # Log progress periodically
                    if i % 50 == 0:
                        logger.info(f"Generated {updated_count} embeddings so far, processed {i+1}/{len(policies)} policies")
            
            logger.info(f"Generated {updated_count} new embeddings")
            
            # Save updated policies with embeddings
            self._save_policies_with_embeddings(policies)
            
            return True
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return False
    
    def _create_embedding_text(self, policy: Dict[str, Any]) -> str:
        """
        Create text representation of a policy for embedding
        
        Args:
            policy: Policy dictionary
            
        Returns:
            Text representation
        """
        text_parts = []
        
        # Add framework and control ID
        framework = policy.get("framework", "")
        control_id = policy.get("control_id", "")
        if framework and control_id:
            text_parts.append(f"{framework} {control_id}")
        
        # Add title
        if "title" in policy:
            text_parts.append(policy["title"])
        
        # Add description
        if "description" in policy:
            text_parts.append(policy["description"])
        
        # Add requirements
        if "requirements" in policy:
            requirements = policy["requirements"]
            if isinstance(requirements, list):
                text_parts.append(" ".join(requirements))
            elif isinstance(requirements, str):
                text_parts.append(requirements)
        
        # Add implementation guidance
        if "implementation" in policy:
            text_parts.append(policy["implementation"])
        
        # Join all parts
        return " ".join(text_parts)
    
    def _generate_simple_embedding(self, text: str) -> List[float]:
        """
        Generate a simple embedding vector without using API
        
        Args:
            text: Text to embed
            
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
        
        # Pad or truncate to get a vector of desired length
        desired_length = 128  # Much smaller than API embeddings but sufficient
        
        if len(embedding) < desired_length:
            # Pad with zeros
            embedding.extend([0.0] * (desired_length - len(embedding)))
        else:
            # Truncate
            embedding = embedding[:desired_length]
        
        return embedding
    
    def _save_policies_with_embeddings(self, policies: List[Dict[str, Any]]) -> bool:
        """
        Save policies with embeddings to file
        
        Args:
            policies: List of policy dictionaries with embeddings
            
        Returns:
            Success indicator
        """
        try:
            # Create data structure
            data = {
                "timestamp": datetime.now().isoformat(),
                "frameworks": list(self.policy_loader.frameworks.values()),
                "policies": policies
            }
            
            # Save to JSON
            json_path = os.path.join(self.policy_loader.policy_dir, "all_policies_with_embeddings.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
            
            # Also save to CSV for compatibility
            csv_path = os.path.join(self.policy_loader.policy_dir, "all_policies_with_embeddings.csv")
            
            # Convert to dataframe
            policies_flat = []
            for policy in policies:
                # Create flattened version of policy
                policy_flat = policy.copy()
                
                # Convert embedding to string if present
                if "embedding" in policy_flat and policy_flat["embedding"]:
                    policy_flat["embedding"] = str(policy_flat["embedding"])
                
                # Convert list fields to strings
                for key, value in policy_flat.items():
                    if isinstance(value, list):
                        policy_flat[key] = json.dumps(value)
                
                policies_flat.append(policy_flat)
            
            # Create dataframe and save
            if policies_flat:
                df = pd.DataFrame(policies_flat)
                df.to_csv(csv_path, index=False)
            
            logger.info(f"Saved policies with embeddings to {json_path} and {csv_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving policies with embeddings: {str(e)}")
            return False
    
    def load_embeddings(self) -> Dict[str, List[float]]:
        """
        Load policy embeddings into memory
        
        Returns:
            Dictionary mapping policy IDs to embeddings
        """
        if self.embeddings_loaded:
            return self.embedding_cache
        
        try:
            # Try loading from combined file
            json_path = os.path.join(self.policy_loader.policy_dir, "all_policies_with_embeddings.json")
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if "policies" in data:
                        for policy in data["policies"]:
                            if "embedding" in policy and policy["embedding"]:
                                # Create policy ID
                                framework = policy.get("framework", "")
                                control_id = policy.get("control_id", "")
                                policy_id = f"{framework}:{control_id}" if framework and control_id else hash(json.dumps(policy))
                                
                                # Store in cache
                                self.embedding_cache[policy_id] = policy["embedding"]
                
                self.embeddings_loaded = True
                logger.info(f"Loaded {len(self.embedding_cache)} embeddings")
                return self.embedding_cache
            else:
                logger.warning(f"Embeddings file not found at {json_path}")
                return {}
                
        except Exception as e:
            logger.error(f"Error loading embeddings: {str(e)}")
            return {}
    
    def create_vector_store(self, force_rebuild: bool = False) -> bool:
        """
        Create a vector store for semantic search
        
        Args:
            force_rebuild: Force rebuilding even if store exists
            
        Returns:
            Success indicator
        """
        # Check if vector store already exists
        vector_store_path = os.path.join(self.model_dir, "vector_store.pkl")
        if os.path.exists(vector_store_path) and not force_rebuild:
            logger.info(f"Vector store already exists at {vector_store_path}")
            return True
        
        # Load embeddings
        embeddings = self.load_embeddings()
        if not embeddings:
            logger.error("No embeddings available, cannot create vector store")
            return False
        
        try:
            # Load policies
            policies = self.policy_loader.load_all_policies()
            
            # Create simple vector store dictionary
            vector_store = {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "embedding_count": len(embeddings),
                    "policy_count": len(policies),
                    "model_type": "no_api_mode"
                },
                "embeddings": embeddings,
                "policies": {
                    f"{p.get('framework', '')}:{p.get('control_id', '')}": p 
                    for p in policies if p.get('framework') and p.get('control_id')
                }
            }
            
            # Save to file
            with open(vector_store_path, 'wb') as f:
                pickle.dump(vector_store, f)
            
            logger.info(f"Vector store created with {len(embeddings)} embeddings and saved to {vector_store_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            return False
    
    def generate_qa_dataset(self, output_path: str = None) -> str:
        """
        Generate a Q&A dataset for evaluation
        
        Args:
            output_path: Path to save the dataset
            
        Returns:
            Path to the saved dataset
        """
        if not output_path:
            output_path = os.path.join(self.model_dir, "qa_evaluation_dataset.json")
        
        # Load policies
        policies = self.policy_loader.load_all_policies()
        if not policies:
            logger.error("No policy data found, cannot generate dataset")
            return None
        
        try:
            # Generate QA pairs
            qa_pairs = []
            
            # Sample policies (max 100 for evaluation)
            sample_size = min(100, len(policies))
            np.random.seed(42)  # For reproducibility
            sampled_indices = np.random.choice(len(policies), sample_size, replace=False)
            sampled_policies = [policies[i] for i in sampled_indices]
            
            for policy in sampled_policies:
                framework = policy.get("framework", "")
                control_id = policy.get("control_id", "")
                
                if not framework or not control_id:
                    continue
                
                # Generate questions for this policy
                questions = [
                    f"What is {framework} {control_id}?",
                    f"Explain {control_id} in {framework}",
                    f"What are the requirements for {framework} {control_id}?",
                    f"How do I implement {framework} {control_id}?"
                ]
                
                # Sample 1-2 questions per policy
                num_questions = min(2, len(questions))
                selected_questions = np.random.choice(questions, num_questions, replace=False)
                
                for question in selected_questions:
                    qa_pairs.append({
                        "question": question,
                        "policy_id": f"{framework}:{control_id}",
                        "framework": framework,
                        "control_id": control_id
                    })
            
            # Add framework-level questions
            for framework_id, summary in self.policy_loader.framework_summaries.items():
                qa_pairs.append({
                    "question": f"What is {framework_id}?",
                    "policy_id": None,
                    "framework": framework_id,
                    "control_id": None
                })
                
                qa_pairs.append({
                    "question": f"How many controls are in {framework_id}?",
                    "policy_id": None,
                    "framework": framework_id,
                    "control_id": None
                })
            
            # Add some comparison questions
            frameworks = list(self.policy_loader.framework_summaries.keys())
            if len(frameworks) >= 2:
                for _ in range(min(5, len(frameworks))):
                    fw1, fw2 = np.random.choice(frameworks, 2, replace=False)
                    qa_pairs.append({
                        "question": f"Compare {fw1} and {fw2}",
                        "policy_id": None,
                        "framework": [fw1, fw2],
                        "control_id": None
                    })
            
            # Add general questions
            general_questions = [
                "What are the key components of a security program?",
                "How do I start implementing a compliance program?",
                "What is the difference between security and compliance?",
                "What frameworks should a healthcare organization follow?",
                "What are the most critical security controls?",
                "How do I prepare for a security audit?",
                "What documentation is needed for compliance?",
                "How often should security assessments be performed?",
                "What are the common security vulnerabilities?",
                "How do I develop a security policy?"
            ]
            
            for question in general_questions:
                qa_pairs.append({
                    "question": question,
                    "policy_id": None,
                    "framework": None,
                    "control_id": None
                })
            
            # Save dataset
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(qa_pairs, f, indent=2)
            
            logger.info(f"Generated QA dataset with {len(qa_pairs)} questions and saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating QA dataset: {str(e)}")
            return None