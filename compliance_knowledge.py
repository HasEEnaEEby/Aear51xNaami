import json
import pandas as pd
import numpy as np
from pathlib import Path
import re
import os

class ComplianceKnowledgeBase:
    def __init__(self):
        """Initialize the compliance knowledge base"""
        self.frameworks = {}
        self.controls = {}
        self.mappings = {}
        self.categories = {}
        self.risk_categories = {}
        self.recommendation_templates = {}
        
    def load_framework(self, framework_id, file_path, format='json'):
        """
        Load a compliance framework from file
        
        Args:
            framework_id: Identifier for the framework (e.g., 'ISO27001')
            file_path: Path to the framework file
            format: File format ('json' or 'csv')
        """
        if format == 'json':
            with open(file_path, 'r') as f:
                framework_data = json.load(f)
        elif format == 'csv':
            framework_data = pd.read_csv(file_path).to_dict(orient='records')
        else:
            raise ValueError(f"Unsupported format: {format}")
            
        # Store the framework
        self.frameworks[framework_id] = {
            'name': framework_data.get('name', framework_id),
            'description': framework_data.get('description', ''),
            'version': framework_data.get('version', ''),
            'controls': {}
        }
        
        # Process controls
        for control in framework_data.get('controls', []):
            control_id = control.get('id')
            if not control_id:
                continue
                
            # Store in framework's controls
            self.frameworks[framework_id]['controls'][control_id] = control
            
            # Store in global controls with framework reference
            full_control_id = f"{framework_id}:{control_id}"
            self.controls[full_control_id] = {
                **control,
                'framework': framework_id
            }
            
            # Add to categories
            category = control.get('category')
            if category:
                if category not in self.categories:
                    self.categories[category] = []
                self.categories[category].append(full_control_id)
                
            # Add to risk categories
            risk_category = control.get('risk_category')
            if risk_category:
                if risk_category not in self.risk_categories:
                    self.risk_categories[risk_category] = []
                self.risk_categories[risk_category].append(full_control_id)
        
        return True
    
    def load_all_frameworks(self, directory):
        """
        Load all frameworks from a directory
        
        Args:
            directory: Directory containing framework files
        """
        directory_path = Path(directory)
        
        for file_path in directory_path.glob('*'):
            if file_path.is_file():
                # Determine format based on file extension
                if file_path.suffix.lower() == '.json':
                    format = 'json'
                elif file_path.suffix.lower() == '.csv':
                    format = 'csv'
                else:
                    continue  # Skip unsupported file types
                
                # Extract framework ID from filename
                framework_id = file_path.stem.upper()
                
                # Load framework
                self.load_framework(framework_id, str(file_path), format)
        
        return len(self.frameworks)
    
    def load_mappings(self, mapping_file):
        """
        Load mappings between frameworks
        
        Args:
            mapping_file: Path to mapping file (JSON or CSV)
        """
        file_path = Path(mapping_file)
        
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'r') as f:
                self.mappings = json.load(f)
        elif file_path.suffix.lower() == '.csv':
            mappings_df = pd.read_csv(file_path)
            
            # Process each row into mappings dictionary
            for _, row in mappings_df.iterrows():
                source_framework = row.get('source_framework')
                source_control = row.get('source_control')
                target_framework = row.get('target_framework')
                target_control = row.get('target_control')
                
                if not all([source_framework, source_control, target_framework, target_control]):
                    continue
                
                # Create mapping key
                source_key = f"{source_framework}:{source_control}"
                target_key = f"{target_framework}:{target_control}"
                
                # Add to mappings
                if source_key not in self.mappings:
                    self.mappings[source_key] = []
                self.mappings[source_key].append(target_key)
        
        return True
    
    def load_recommendation_templates(self, templates_file):
        """
        Load recommendation templates
        
        Args:
            templates_file: Path to templates file (JSON)
        """
        with open(templates_file, 'r') as f:
            self.recommendation_templates = json.load(f)
        
        return True
    
    def get_control(self, framework_id, control_id):
        """
        Get a specific control from a framework
        
        Args:
            framework_id: Framework identifier
            control_id: Control identifier
            
        Returns:
            Control data or None if not found
        """
        full_control_id = f"{framework_id}:{control_id}"
        return self.controls.get(full_control_id)
    
    def get_mapped_controls(self, framework_id, control_id):
        """
        Get controls from other frameworks mapped to this control
        
        Args:
            framework_id: Framework identifier
            control_id: Control identifier
            
        Returns:
            List of mapped controls across frameworks
        """
        source_key = f"{framework_id}:{control_id}"
        return self.mappings.get(source_key, [])
    
    def get_controls_by_category(self, category):
        """
        Get all controls in a specific category
        
        Args:
            category: Category name
            
        Returns:
            List of controls in the category
        """
        return self.categories.get(category, [])
    
    def get_controls_by_risk_category(self, risk_category):
        """
        Get all controls in a specific risk category
        
        Args:
            risk_category: Risk category name
            
        Returns:
            List of controls in the risk category
        """
        return self.risk_categories.get(risk_category, [])
    
    def get_recommendation_template(self, category, risk_level='medium'):
        """
        Get recommendation template for a category and risk level
        
        Args:
            category: Category name
            risk_level: Risk level (low, medium, high)
            
        Returns:
            Recommendation template text
        """
        category_templates = self.recommendation_templates.get(category, {})
        return category_templates.get(risk_level, category_templates.get('default', ''))
    
    def search_controls(self, query):
        """
        Search for controls matching a query
        
        Args:
            query: Search query
            
        Returns:
            List of matching controls
        """
        results = []
        
        # Create regex pattern for case-insensitive search
        pattern = re.compile(query, re.IGNORECASE)
        
        for control_id, control in self.controls.items():
            # Search in title, description, and other relevant fields
            searchable_text = ' '.join([
                str(control.get('title', '')),
                str(control.get('description', '')),
                str(control.get('requirements', ''))
            ])
            
            if pattern.search(searchable_text):
                results.append(control_id)
        
        return results
    
    def export_to_json(self, output_file):
        """
        Export the knowledge base to a JSON file
        
        Args:
            output_file: Path to output file
        """
        export_data = {
            'frameworks': self.frameworks,
            'mappings': self.mappings,
            'categories': self.categories,
            'risk_categories': self.risk_categories
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return True


# Example usage
if __name__ == "__main__":
    # Initialize knowledge base
    kb = ComplianceKnowledgeBase()
    
    # Example implementation - in a real system you'd have actual data files
    # Create sample data directory and files for demonstration
    os.makedirs("frameworks", exist_ok=True)
    
    # Sample ISO27001 data
    iso27001 = {
        "name": "ISO/IEC 27001:2013",
        "description": "Information Security Management System (ISMS) standard",
        "version": "2013",
        "controls": [
            {
                "id": "A.5.1.1",
                "title": "Policies for information security",
                "description": "A set of policies for information security shall be defined, approved by management, published and communicated to employees and relevant external parties.",
                "category": "Security Policy",
                "risk_category": "Governance"
            },
            {
                "id": "A.8.2.3",
                "title": "Handling of assets",
                "description": "Procedures for handling assets shall be developed and implemented in accordance with the information classification scheme.",
                "category": "Asset Management",
                "risk_category": "Data Protection"
            }
        ]
    }
    
    # Sample NIST data
    nist80053 = {
        "name": "NIST SP 800-53 Rev. 5",
        "description": "Security and Privacy Controls for Information Systems and Organizations",
        "version": "Revision 5",
        "controls": [
            {
                "id": "AC-1",
                "title": "Policy and Procedures",
                "description": "Establish and maintain an access control policy and procedures.",
                "category": "Access Control",
                "risk_category": "Access Management"
            },
            {
                "id": "CM-2",
                "title": "Baseline Configuration",
                "description": "Develop, document, and maintain under configuration control, a current baseline configuration of the system.",
                "category": "Configuration Management",
                "risk_category": "Change Management"
            }
        ]
    }
    
    # Write sample files
    with open("frameworks/iso27001.json", "w") as f:
        json.dump(iso27001, f)
        
    with open("frameworks/nist80053.json", "w") as f:
        json.dump(nist80053, f)
    
    # Sample mappings
    mappings = [
        {
            "source_framework": "ISO27001",
            "source_control": "A.5.1.1",
            "target_framework": "NIST80053",
            "target_control": "AC-1"
        },
        {
            "source_framework": "NIST80053",
            "source_control": "CM-2",
            "target_framework": "ISO27001",
            "target_control": "A.8.2.3"
        }
    ]
    
    mappings_df = pd.DataFrame(mappings)
    mappings_df.to_csv("frameworks/mappings.csv", index=False)
    
    # Sample recommendation templates
    recommendation_templates = {
        "Access Control": {
            "high": "Implement multi-factor authentication across all systems immediately. Review access controls monthly and remove unnecessary privileges.",
            "medium": "Review current access controls and implement MFA for critical systems. Conduct quarterly reviews of user privileges.",
            "low": "Consider implementing stronger access controls such as role-based access. Review user privileges annually.",
            "default": "Improve access control with regular privilege reviews."
        },
        "Data Protection": {
            "high": "Encrypt all sensitive data at rest and in transit. Implement DLP solutions to prevent data leakage.",
            "medium": "Review encryption practices and ensure sensitive data is protected. Consider data loss prevention measures.",
            "low": "Evaluate current data protection measures and improve where necessary.",
            "default": "Enhance data protection with appropriate encryption."
        }
    }
    
    with open("frameworks/recommendation_templates.json", "w") as f:
        json.dump(recommendation_templates, f, indent=2)
    
    # Load data into knowledge base
    kb.load_all_frameworks("frameworks")
    kb.load_mappings("frameworks/mappings.csv")
    kb.load_recommendation_templates("frameworks/recommendation_templates.json")
    
    # Example usage
    print(f"Loaded {len(kb.frameworks)} frameworks")
    print(f"Total controls: {len(kb.controls)}")
    
    # Search for controls
    search_results = kb.search_controls("policy")
    print(f"Search results for 'policy': {search_results}")
    
    # Get recommendation
    ac_rec = kb.get_recommendation_template("Access Control", "medium")
    print(f"Access Control recommendation: {ac_rec}")
    
    # Export knowledge base
    kb.export_to_json("frameworks/knowledge_base.json")