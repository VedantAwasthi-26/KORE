"""
KORE Layer 3: Rules Engine
Deterministic file classification based on extension, size, date
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timedelta

class RulesEngine:
    """Rule-based file classification - no AI needed for basic sorting"""
    
    def __init__(self, rules_file: str = "config/rules.json"):
        """
        Initialize rules engine
        
        Args:
            rules_file: Path to JSON file containing classification rules
        """
        self.rules_file = rules_file
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, Any]:
        """Load classification rules from JSON file"""
        if os.path.exists(self.rules_file):
            with open(self.rules_file, 'r') as f:
                return json.load(f)
        else:
            # Return default rules if file doesn't exist
            return self._get_default_rules()
    
    def _get_default_rules(self) -> Dict[str, Any]:
        """Default file organization rules"""
        return {
            "extension_mapping": {
                # Documents
                ".pdf": "Documents/PDFs",
                ".doc": "Documents/Word",
                ".docx": "Documents/Word",
                ".txt": "Documents/Text",
                ".odt": "Documents/Text",
                ".rtf": "Documents/Text",
                
                # Spreadsheets
                ".xls": "Documents/Excel",
                ".xlsx": "Documents/Excel",
                ".csv": "Documents/Excel",
                
                # Presentations
                ".ppt": "Documents/PowerPoint",
                ".pptx": "Documents/PowerPoint",
                
                # Images
                ".jpg": "Pictures/Photos",
                ".jpeg": "Pictures/Photos",
                ".png": "Pictures/Screenshots",
                ".gif": "Pictures/GIFs",
                ".bmp": "Pictures/Photos",
                ".svg": "Pictures/Vector",
                ".webp": "Pictures/Photos",
                
                # Videos
                ".mp4": "Videos",
                ".avi": "Videos",
                ".mkv": "Videos",
                ".mov": "Videos",
                ".wmv": "Videos",
                ".flv": "Videos",
                
                # Audio
                ".mp3": "Music",
                ".wav": "Music",
                ".flac": "Music",
                ".aac": "Music",
                ".m4a": "Music",
                
                # Archives
                ".zip": "Archives",
                ".rar": "Archives",
                ".7z": "Archives",
                ".tar": "Archives",
                ".gz": "Archives",
                
                # Programs
                ".exe": "Downloads/Installers",
                ".msi": "Downloads/Installers",
                ".dmg": "Downloads/Installers",
                ".app": "Applications",
                
                # Code
                ".py": "Code/Python",
                ".js": "Code/JavaScript",
                ".html": "Code/Web",
                ".css": "Code/Web",
                ".java": "Code/Java",
                ".cpp": "Code/C++",
                ".c": "Code/C",
            },
            
            "size_rules": {
                "large_file_threshold_mb": 100,
                "large_file_destination": "LargeFiles"
            },
            
            "date_rules": {
                "old_file_days": 180,  # Files older than 6 months
                "old_file_destination": "Archive/Old"
            }
        }
    
    def save_rules(self, rules: Dict[str, Any] = None):
        """Save current rules to JSON file"""
        rules_to_save = rules if rules else self.rules
        
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(self.rules_file), exist_ok=True)
        
        with open(self.rules_file, 'w') as f:
            json.dump(rules_to_save, indent=2, fp=f)
        
        print(f"✅ Rules saved to {self.rules_file}")
    
    def classify_file(self, file_info: Dict[str, Any]) -> str:
        """
        Classify a single file based on rules
        
        Args:
            file_info: Dictionary with file metadata (extension, size_mb, modified_date, etc.)
            
        Returns:
            Destination folder path
        """
        extension = file_info.get('extension', '').lower()
        size_mb = file_info.get('size_mb', 0)
        modified_date = file_info.get('modified_date')
        
        # Rule 1: Check if it's a large file
        large_threshold = self.rules['size_rules']['large_file_threshold_mb']
        if size_mb > large_threshold:
            return self.rules['size_rules']['large_file_destination']
        
        # Rule 2: Check if it's an old file
        if modified_date:
            old_days = self.rules['date_rules']['old_file_days']
            cutoff_date = datetime.now() - timedelta(days=old_days)
            
            if isinstance(modified_date, str):
                modified_date = datetime.fromisoformat(modified_date)
            
            if modified_date < cutoff_date:
                return self.rules['date_rules']['old_file_destination']
        
        # Rule 3: Classify by extension
        extension_map = self.rules['extension_mapping']
        if extension in extension_map:
            return extension_map[extension]
        
        # Default: Unknown file type
        return "Uncategorized"
    
    def classify_batch(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Classify multiple files at once
        
        Args:
            files: List of file info dictionaries
            
        Returns:
            List of classification results with destinations
        """
        results = []
        
        for file in files:
            destination = self.classify_file(file)
            
            results.append({
                'file': file.get('path', file.get('name')),
                'name': file.get('name'),
                'extension': file.get('extension'),
                'destination': destination,
                'reason': f"Classified as {destination} based on {file.get('extension')} extension"
            })
        
        return results
    
    def get_statistics(self, classifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate statistics about file classifications
        
        Args:
            classifications: List of classified files
            
        Returns:
            Statistics dictionary
        """
        stats = {
            'total_files': len(classifications),
            'by_destination': {},
            'by_extension': {}
        }
        
        for item in classifications:
            # Count by destination
            dest = item['destination']
            stats['by_destination'][dest] = stats['by_destination'].get(dest, 0) + 1
            
            # Count by extension
            ext = item['extension']
            stats['by_extension'][ext] = stats['by_extension'].get(ext, 0) + 1
        
        return stats


# TESTING CODE
if __name__ == "__main__":
    print("📋 KORE Layer 3: Rules Engine")
    print("=" * 50)
    
    # TEST 1: Initialize rules engine
    rules = RulesEngine()
    print("✅ Rules engine initialized")
    
    # TEST 2: Save default rules
    rules.save_rules()
    print(f"✅ Default rules saved to {rules.rules_file}")
    
    # TEST 3: Classify sample files
    print("\n" + "=" * 50)
    print("🧪 Testing file classification")
    print("=" * 50)
    
    sample_files = [
        {
            "name": "report.pdf",
            "path": "Downloads/report.pdf",
            "extension": ".pdf",
            "size_mb": 2.5,
            "modified_date": datetime.now().isoformat()
        },
        {
            "name": "vacation.jpg",
            "path": "Downloads/vacation.jpg",
            "extension": ".jpg",
            "size_mb": 3.2,
            "modified_date": datetime.now().isoformat()
        },
        {
            "name": "movie.mp4",
            "path": "Downloads/movie.mp4",
            "extension": ".mp4",
            "size_mb": 1500.0,  # Large file!
            "modified_date": datetime.now().isoformat()
        },
        {
            "name": "old_doc.docx",
            "path": "Downloads/old_doc.docx",
            "extension": ".docx",
            "size_mb": 0.5,
            "modified_date": (datetime.now() - timedelta(days=200)).isoformat()  # Old file!
        }
    ]
    
    classifications = rules.classify_batch(sample_files)
    
    print("\n📊 Classification Results:")
    for item in classifications:
        print(f"  {item['name']} → {item['destination']}")
        print(f"     Reason: {item['reason']}\n")
    
    # TEST 4: Statistics
    stats = rules.get_statistics(classifications)
    print("📈 Statistics:")
    print(f"  Total files: {stats['total_files']}")
    print(f"  Destinations: {json.dumps(stats['by_destination'], indent=4)}")
