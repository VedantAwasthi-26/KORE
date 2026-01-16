"""
KORE Layer 3: Task Planner
Coordinates between Gemini AI and Rules Engine
Creates execution plans for Layer 1
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from layer3_rules import RulesEngine

class TaskPlanner:
    """
    Main coordination layer - decides whether to use AI or rules
    Creates execution plans for Layer 1
    """
    
    def __init__(self, use_ai: bool = False):
        self.use_ai = False  # force offline mode
        
        # Always initialize rules engine
        self.rules = RulesEngine()
        
        self.ai = None
        print("📋 Rule-based planning only (offline mode)")


        
    
    def create_plan(self, query: str, files: List[Dict[str, Any]], source_folder: str) -> Dict[str, Any]:
        """
        Main entry point - create execution plan
        
        Args:
            query: User's natural language query
            files: List of files from Layer 1 scanner
            source_folder: Source folder path
            
        Returns:
            Complete execution plan for Layer 1
        """
        plan = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'source_folder': source_folder,
            'mode': 'ai' if self.use_ai else 'rules',
            'operations': [],
            'risk_level': 'low',
            'requires_confirmation': True,
            'reasoning': ''
        }
        
        try:
            """
            # Determine which planning method to use
            if self._should_use_ai(query) and self.use_ai:
                # Use AI for complex queries
                plan = self._plan_with_ai(query, files, source_folder)
            else:
                # Use rules for simple organization
                plan = self._plan_with_rules(files, source_folder)
            """
            plan = self._plan_with_rules(files, source_folder)


            # Assess risk level
            plan['risk_level'] = self._assess_risk(plan)
            
            # Validate plan before returning
            plan = self._validate_plan(plan)
            
            return plan
            
        except Exception as e:
            return {
                'action': 'error',
                'error': str(e),
                'message': 'Failed to create plan',
                'timestamp': datetime.now().isoformat()
            }
    
    def _should_use_ai(self, query: str) -> bool:
        """
        Decide if query needs AI or just rules
        
        Args:
            query: User query
            
        Returns:
            True if AI should be used
        """
        # Simple keywords that rules can handle
        simple_keywords = ['organize', 'sort', 'clean', 'tidy']
        
        query_lower = query.lower()
        
        # If query is just asking to organize, use rules (faster, cheaper)
        if any(keyword in query_lower for keyword in simple_keywords) and len(query.split()) < 10:
            return False
        
        # Complex queries need AI
        return True
    
    def _plan_with_ai(self, query: str, files: List[Dict[str, Any]], source_folder: str) -> Dict[str, Any]:
        """Use Gemini AI to create plan"""
        ai_plan = self.ai.parse_user_query(query, files)
        
        # Convert AI plan to standard format
        if ai_plan.get('action') == 'error':
            return ai_plan
        
        # Enhance AI plan with full paths
        operations = []
        for op in ai_plan.get('operations', []):
            file_name = op.get('file')
            destination = op.get('destination')
            
            # Find full source path
            source_path = None
            for f in files:
                if f['name'] == file_name or f['path'].endswith(file_name):
                    source_path = f['path']
                    break
            
            if source_path:
                operations.append({
                    'source': source_path,
                    'destination': os.path.join(destination, os.path.basename(source_path)),
                    'reason': op.get('reason', 'AI recommendation')
                })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'source_folder': source_folder,
            'mode': 'ai',
            'action': ai_plan.get('action', 'organize_files'),
            'operations': operations,
            'reasoning': ai_plan.get('reasoning', 'AI-generated plan'),
            'risk_level': ai_plan.get('risk_level', 'medium'),
            'requires_confirmation': ai_plan.get('requires_confirmation', True)
        }
    
    def _plan_with_rules(self, files: List[Dict[str, Any]], source_folder: str) -> Dict[str, Any]:
        """Use rule-based classification"""
        classifications = self.rules.classify_batch(files)
        
        operations = []
        for item in classifications:
            source_path = item['file']
            dest_folder = item['destination']
            file_name = item['name']
            
            # Build full destination path
            dest_path = os.path.join(dest_folder, file_name)
            
            operations.append({
                'source': source_path,
                'destination': dest_path,
                'reason': item['reason']
            })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'query': 'Organize files by rules',
            'source_folder': source_folder,
            'mode': 'rules',
            'action': 'organize_files',
            'operations': operations,
            'reasoning': f'Organized {len(files)} files using predefined classification rules',
            'risk_level': 'low',
            'requires_confirmation': True
        }
    
    def _assess_risk(self, plan: Dict[str, Any]) -> str:
        """
        Assess risk level of plan
        
        Returns:
            'low', 'medium', or 'high'
        """
        operations = plan.get('operations', [])
        
        if not operations:
            return 'low'
        
        # Check for system file paths
        high_risk_paths = [
            'System32', 'Windows', 'Program Files', 
            '/bin', '/usr', '/etc', '/System'
        ]
        
        for op in operations:
            source = op.get('source', '')
            if any(risky in source for risky in high_risk_paths):
                return 'high'
        
        # Medium risk: many operations
        if len(operations) > 50:
            return 'medium'
        
        # Check if moving to system locations
        for op in operations:
            dest = op.get('destination', '')
            if any(risky in dest for risky in high_risk_paths):
                return 'high'
        
        return 'low'
    
    def _validate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate plan for safety
        Remove dangerous operations
        """
        if plan.get('action') == 'error':
            return plan
        
        operations = plan.get('operations', [])
        safe_operations = []
        warnings = []
        
        for op in operations:
            source = op.get('source', '')
            dest = op.get('destination', '')
            
            # Skip if source doesn't exist
            if not os.path.exists(source):
                warnings.append(f"Skipped: {source} does not exist")
                continue
            
            # Skip if destination is in source (circular move)
            if dest.startswith(source):
                warnings.append(f"Skipped: Circular move detected for {source}")
                continue
            
            safe_operations.append(op)
        
        plan['operations'] = safe_operations
        
        if warnings:
            plan['warnings'] = warnings
        
        return plan
    
    def explain_plan(self, plan: Dict[str, Any]) -> str:
        """
        Generate human-readable explanation
        
        Args:
            plan: Execution plan
            
        Returns:
            Formatted explanation string
        """
        if plan.get('action') == 'error':
            return f"❌ Error: {plan.get('message')}"
        
        explanation = []
        explanation.append("=" * 60)
        explanation.append("📋 KORE EXECUTION PLAN")
        explanation.append("=" * 60)
        explanation.append(f"Mode: {plan.get('mode', 'unknown').upper()}")
        explanation.append(f"Source: {plan.get('source_folder')}")
        explanation.append(f"Timestamp: {plan.get('timestamp')}")
        explanation.append("")
        explanation.append(f"Reasoning: {plan.get('reasoning')}")
        explanation.append("")
        
        operations = plan.get('operations', [])
        explanation.append(f"📦 Operations: {len(operations)} total")
        explanation.append("")
        
        # Show first 10 operations
        for i, op in enumerate(operations[:10], 1):
            source_name = os.path.basename(op['source'])
            dest_folder = os.path.dirname(op['destination'])
            explanation.append(f"  {i}. {source_name}")
            explanation.append(f"     → {dest_folder}")
            explanation.append(f"     Reason: {op.get('reason', 'No reason given')}")
            explanation.append("")
        
        if len(operations) > 10:
            explanation.append(f"  ... and {len(operations) - 10} more operations")
            explanation.append("")
        
        # Risk assessment
        risk = plan.get('risk_level', 'unknown')
        risk_symbols = {'low': '✅', 'medium': '⚠️', 'high': '🚨'}
        risk_symbol = risk_symbols.get(risk, '❓')
        
        explanation.append(f"{risk_symbol} Risk Level: {risk.upper()}")
        
        if plan.get('requires_confirmation'):
            explanation.append("")
            explanation.append("⚠️  USER CONFIRMATION REQUIRED BEFORE EXECUTION")
        
        if plan.get('warnings'):
            explanation.append("")
            explanation.append("⚠️  Warnings:")
            for warning in plan['warnings']:
                explanation.append(f"  - {warning}")
        
        explanation.append("=" * 60)
        
        return "\n".join(explanation)


if __name__ == "__main__":
    planner = TaskPlanner()
    
    sample_files = [
        ...
    ]
    
    # Sample files
    sample_files = [
        {
            "name": "report.pdf",
            "path": "test_files/messy_downloads/report.pdf",
            "extension": ".pdf",
            "size_mb": 2.5,
            "modified_date": datetime.now().isoformat()
        },
        {
            "name": "vacation.jpg",
            "path": "test_files/messy_downloads/vacation.jpg",
            "extension": ".jpg",
            "size_mb": 3.2,
            "modified_date": datetime.now().isoformat()
        },
        {
            "name": "video.mp4",
            "path": "test_files/messy_downloads/video.mp4",
            "extension": ".mp4",
            "size_mb": 150.0,
            "modified_date": datetime.now().isoformat()
        }
    ]
    
    # Test planning
    print("\n🧪 Testing: Simple organization query")
    plan = planner.create_plan(
        query="Understand my entire downloads folder, infer which files are academic, which are personal photos, which are software, and organize them into a smart hierarchy",
        files=sample_files,
        source_folder="test_files/messy_downloads"
    )
    
    print("\n" + planner.explain_plan(plan))
    
    # Save plan to file
    plan_file = "logs/test_plan.json"
    os.makedirs("logs", exist_ok=True)
    with open(plan_file, 'w') as f:
        json.dump(plan, indent=2, fp=f)
    print(f"\n💾 Plan saved to: {plan_file}")
