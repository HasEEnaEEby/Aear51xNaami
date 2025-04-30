#!/usr/bin/env python3
"""
Script to train and set up the Security Compliance Advisor Chatbot
This script loads policy data, trains the chatbot, and prepares it for use.
"""

import os
import json
import argparse
import logging
from pathlib import Path
import sys
import asyncio

# Add parent directory to path for imports
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from core.compliance.policy_loader import PolicyLoader
from core.advisor.chatbot_trainer import ChatbotTrainer
from core.compliance.security_compliance_chatbot import SecurityComplianceChatbot
from core.compliance.compliance_knowledge import ComplianceKnowledge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_chatbot(chatbot, test_questions=None):
    """
    Test the chatbot with sample questions
    
    Args:
        chatbot: SecurityComplianceChatbot instance
        test_questions: Optional list of test questions
    """
    if not test_questions:
        test_questions = [
            "What is NIST 800-53?",
            "Tell me about AC-2 in NIST 800-53",
            "What are the requirements for GDPR?",
            "Compare HIPAA and GDPR",
            "How do I implement PCI-DSS requirement 3.4?",
            "What are the key security controls for a healthcare organization?",
            "How do I prepare for an ISO 27001 audit?",
            "What documentation is required for HIPAA compliance?"
        ]
    
    logger.info(f"Testing chatbot with {len(test_questions)} questions")
    
    for i, question in enumerate(test_questions):
        logger.info(f"Test question {i+1}: {question}")
        
        # Process message
        response = await chatbot.process_message(question)
        
        logger.info(f"Response: {response['text'][:200]}...")
        logger.info(f"Relevant policies: {response['relevant_policies']}")
        logger.info("-" * 80)

def train_chatbot(args):
    """
    Train the security compliance chatbot
    
    Args:
        args: Command line arguments
    """
    logger.info("Starting security compliance chatbot training (No API mode)")
    
    # Create trainer
    trainer = ChatbotTrainer(
        model_dir=args.model_dir,
        api_key=None  # No API mode
    )
    
    # Load policy data
    policy_loader = PolicyLoader(policy_dir=args.policy_dir)
    frameworks = policy_loader.get_all_framework_summaries()
    
    logger.info(f"Found {len(frameworks)} frameworks: {', '.join(frameworks.keys())}")
    
    # Train the model
    logger.info("Training chatbot model")
    success = trainer.train(force_retrain=args.force)
    
    if success:
        logger.info("Chatbot training completed successfully")
    else:
        logger.error("Chatbot training failed")
        return False
    
    # Create vector store
    logger.info("Creating vector store for semantic search")
    vector_store_success = trainer.create_vector_store(force_rebuild=args.force)
    
    if vector_store_success:
        logger.info("Vector store created successfully")
    else:
        logger.warning("Vector store creation failed or was skipped")
    
    # Generate QA dataset for evaluation
    logger.info("Generating QA evaluation dataset")
    qa_path = trainer.generate_qa_dataset()
    
    if qa_path:
        logger.info(f"QA dataset generated at {qa_path}")
    else:
        logger.warning("QA dataset generation failed")
    
    return True

async def interactive_session(chatbot):
    """
    Run an interactive chat session with the chatbot
    
    Args:
        chatbot: SecurityComplianceChatbot instance
    """
    print("\n" + "="*80)
    print("Security Compliance Advisor Chatbot Interactive Session")
    print("="*80)
    print("Type 'quit', 'exit', or press Ctrl+C to end the session")
    print("Type 'clear' to clear conversation history")
    print("Type 'frameworks' to list available frameworks")
    print("Type 'search query' to search the knowledge base")
    print("="*80 + "\n")
    
    while True:
        try:
            # Get user input
            user_input = input("You: ")
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit']:
                print("Ending session")
                break
            
            # Check for clear command
            elif user_input.lower() == 'clear':
                chatbot.clear_conversation_history()
                print("Conversation history cleared")
                continue
        
            elif user_input.lower() == 'frameworks':
                policy_loader = PolicyLoader()
                frameworks = policy_loader.get_all_framework_summaries()
                
                print("\nAvailable frameworks:")
                for fw_id, summary in frameworks.items():
                    print(f"- {fw_id}: {summary.get('name', fw_id)} ({summary.get('policy_count', 0)} controls)")
                print()
                continue
            
            elif user_input.lower().startswith('search '):
                query = user_input[7:].strip()
                results = chatbot.search_knowledge_base(query)
                
                print(f"\nSearch results for '{query}':")
                for i, result in enumerate(results):
                    policy = result.get('policy', {})
                    print(f"{i+1}. {policy.get('framework', '')}-{policy.get('control_id', '')}: {policy.get('title', 'No title')}")
                print()
                continue
        
            response = await chatbot.process_message(user_input)
            print(f"\nChatbot: {response['text']}\n")
            
        except KeyboardInterrupt:
            print("\nEnding session")
            break
        
        except Exception as e:
            print(f"Error: {str(e)}")

def main():
    """Main function to train and test the chatbot"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Train and test the Security Compliance Advisor Chatbot")
    parser.add_argument("--policy-dir", type=str, help="Directory containing policy files", default=os.path.join("data", "policies"))
    parser.add_argument("--model-dir", type=str, help="Directory for model data", default=os.path.join("data", "models"))
    parser.add_argument("--force", action="store_true", help="Force retraining even if model exists")
    parser.add_argument("--test", action="store_true", help="Run test questions after training")
    parser.add_argument("--interactive", action="store_true", help="Start interactive chat session")
    parser.add_argument("--skip-train", action="store_true", help="Skip training and just run testing or interactive mode")
    
    args = parser.parse_args()
    
    # Train chatbot if not skipped
    if not args.skip_train:
        train_success = train_chatbot(args)
        
        if not train_success:
            logger.error("Chatbot training failed, exiting")
            return 1
    
    # Initialize chatbot
    knowledge_base = ComplianceKnowledge()
    chatbot = SecurityComplianceChatbot(
        model_dir=args.model_dir,
        api_key=None,  # No API mode
        knowledge_base=knowledge_base
    )
    
    # Create asyncio event loop for async functions
    loop = asyncio.get_event_loop()
    
    # Test if requested
    if args.test:
        logger.info("Running chatbot tests")
        loop.run_until_complete(test_chatbot(chatbot))
    
    # Run interactive session if requested
    if args.interactive:
        logger.info("Starting interactive chat session")
        loop.run_until_complete(interactive_session(chatbot))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())