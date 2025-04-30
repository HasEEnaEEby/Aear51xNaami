"""
Compliance Knowledge Base for Security Advisor System
This module implements a knowledge base for compliance frameworks with vector search capabilities.
"""

import json
import os
from pathlib import Path
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd

class ComplianceKnowledge:
    """
    Knowledge base for compliance frameworks with semantic search capabilities
    """

    def __init__(self, frameworks_dir: Optional[str] = None, mappings_file: Optional[str] = None, load_from_json: bool = True):
        """
        Initialize the compliance knowledge base

        Args:
            frameworks_dir: Directory for compliance frameworks
            mappings_file: Optional path to mappings
            load_from_json: Load from JSON files or CSV
        """
        self.frameworks_dir = Path(frameworks_dir) if frameworks_dir else Path("data/policies")
        self.mappings_file = Path(mappings_file) if mappings_file else None
        self.frameworks = {}
        self.controls = {}
        self.policy_data = None
        self.policy_embeddings = None
        self.crosswalks = {}
        self.recommendation_templates = {}

        if load_from_json:
            self.load_from_json()
        else:
            self.load_from_csv()

    def load_from_json(self):
        base_dir = self.frameworks_dir
        combined_path = base_dir / "all_policies_with_embeddings.json"

        if combined_path.exists():
            with open(combined_path, 'r') as f:
                self.policy_data = json.load(f)

            if "frameworks" in self.policy_data:
                for framework in self.policy_data["frameworks"]:
                    if isinstance(framework, dict) and "id" in framework:
                        self.frameworks[framework["id"]] = framework

            if "policies" in self.policy_data:
                for policy in self.policy_data["policies"]:
                    if "framework" in policy and "control_id" in policy:
                        control_key = f"{policy['framework']}:{policy['control_id']}"
                        self.controls[control_key] = policy

                        if policy["framework"] not in self.frameworks:
                            self.frameworks[policy["framework"]] = {"id": policy["framework"], "name": policy["framework"], "controls": {}}

                        if "controls" not in self.frameworks[policy["framework"]]:
                            self.frameworks[policy["framework"]]["controls"] = {}

                        self.frameworks[policy["framework"]]["controls"][policy["control_id"]] = policy

                embeddings_list = [policy.get("embedding", [0.0] * 1536) for policy in self.policy_data["policies"]]
                self.policy_embeddings = np.array(embeddings_list)

        else:
            for policy_file in base_dir.glob("*.json"):
                if policy_file.name.startswith("all_policies"):
                    continue
                framework_id = policy_file.stem
                with open(policy_file, 'r') as f:
                    framework_data = json.load(f)
                framework_info = framework_data.get("meta", {"id": framework_id, "name": framework_id})
                self.frameworks[framework_id] = framework_info
                self.frameworks[framework_id]["controls"] = {}
                for policy in framework_data.get("policies", []):
                    if "control_id" in policy:
                        control_id = policy["control_id"]
                        control_key = f"{framework_id}:{control_id}"
                        policy["framework"] = framework_id
                        self.controls[control_key] = policy
                        self.frameworks[framework_id]["controls"][control_id] = policy

        crosswalk_path = base_dir.parent / "mappings" / "framework_crosswalks.json"
        if crosswalk_path.exists():
            with open(crosswalk_path, 'r') as f:
                self.crosswalks = json.load(f)

        template_path = base_dir.parent / "recommendations" / "templates.json"
        if template_path.exists():
            with open(template_path, 'r') as f:
                self.recommendation_templates = json.load(f)
        else:
            self._load_default_templates()

    def _load_default_templates(self):
        self.recommendation_templates = {
            "Access Control": {
                "high": "Implement multi-factor authentication for all privileged accounts and review access rights quarterly.",
                "medium": "Review access control policies and implement least privilege principles.",
                "low": "Ensure password policies meet industry standards."
            },
            "Encryption": {
                "high": "Implement end-to-end encryption for all sensitive data both in transit and at rest.",
                "medium": "Review encryption standards and ensure all sensitive data is encrypted.",
                "low": "Verify that encryption is used for sensitive communications."
            }
        }

    def load_from_csv(self):
        csv_path = self.frameworks_dir / "all_policies_with_embeddings.csv"
        if not csv_path.exists():
            return
        df = pd.read_csv(csv_path)
        for framework_id in df["framework"].unique():
            self.frameworks[framework_id] = {"id": framework_id, "name": framework_id, "controls": {}}
        for _, row in df.iterrows():
            if "framework" in row and "control_id" in row:
                framework_id = row["framework"]
                control_id = row["control_id"]
                control_key = f"{framework_id}:{control_id}"
                self.controls[control_key] = row.to_dict()
                self.frameworks[framework_id]["controls"][control_id] = row.to_dict()
        if "embedding" in df.columns:
            import re
            self.policy_embeddings = np.array([
                [float(x) for x in re.findall(r"[-+]?\d*\.\d+|\d+", str(val))] if isinstance(val, str) else [0.0]*1536
                for val in df["embedding"]
            ])
