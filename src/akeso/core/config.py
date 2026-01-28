"""
AKESO CONFIGURATION MANAGER
---------------------------
Handles loading and parsing of user configuration (.akeso.yaml).
Allows customization of:
- Rule ignore patterns (glob-based)
- Health thresholds
- Analyzer settings
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from fnmatch import fnmatch
from ruamel.yaml import YAML

logger = logging.getLogger("akeso.config")

class ConfigManager:
    """
    Manages user configuration state.
    defaults:
      threshold: 70
      ignore: []
    """
    
    DEFAULT_CONFIG = {
        "rules": {
            "threshold": 70,
            "ignore": [
                ".git/*",
                "node_modules/*",
                "venv/*",
                "__pycache__/*"
            ]
        },
        "analyzers": {
            "enabled": ["*"]
        }
    }

    def __init__(self, workspace_root: Path):
        self.workspace = workspace_root
        self.config = self.DEFAULT_CONFIG.copy()
        self._load_config()

    def _load_config(self):
        """Attempts to load .akeso.yaml or .akeso.yml from workspace root."""
        yaml = YAML(typ='safe')
        possible_files = [".akeso.yaml", ".akeso.yml"]
        
        for fname in possible_files:
            config_path = self.workspace / fname
            if config_path.exists():
                try:
                    loaded = yaml.load(config_path)
                    if loaded:
                        self._merge_config(loaded)
                    logger.info(f"Loaded configuration from {fname}")
                    return
                except Exception as e:
                    logger.warning(f"Failed to parse {fname}: {e}")

    def _merge_config(self, user_config: Dict[str, Any]):
        """Deep merge of user config into defaults."""
        # Simple depth-1 merge for now, can be expanded if needed
        if "rules" in user_config:
            self.config["rules"].update(user_config["rules"])
        if "analyzers" in user_config:
            self.config["analyzers"].update(user_config["analyzers"])

    def is_ignored(self, file_path: str, rule_id: Optional[str] = None) -> bool:
        """
        Determines if a file or rule should be ignored.
        
        Args:
            file_path: Relative path to the file.
            rule_id: Optional rule ID (e.g., 'rules/no-latest-tag').
            
        Returns:
            True if ignored, False otherwise.
        """
        ignores = self.config["rules"].get("ignore", [])
        
        # Check explicit ignore patterns
        for pattern in ignores:
            # File match
            if fnmatch(file_path, pattern):
                return True
            # Rule ID match (if provided)
            if rule_id and rule_id == pattern:
                return True
        
        return False

    @property
    def health_threshold(self) -> int:
        return self.config["rules"].get("threshold", 70)
