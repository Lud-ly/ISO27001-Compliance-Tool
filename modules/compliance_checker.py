"""
Module de vérification de conformité ISO 27001
"""
import json
from datetime import datetime
from typing import Dict, List

class ComplianceChecker:
    def __init__(self, controls_file: str = "data/iso27001_controls.json"):
        """Initialise le checker avec les contrôles ISO 27001"""
        with open(controls_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.controls = data['controls']
        
        self.assessment = {}
        self.results = {}
    
    def start_assessment(self, organization: str, assessor: str) -> Dict:
        """Démarre une nouvelle évaluation"""
        self.assessment = {
            "metadata": {
                "organization": organization,
                "assessor": assessor,
                "date": datetime.now().isoformat(),
                "standard": "ISO/IEC 27001:2022"
            },
            "controls_assessment": []
        }
        return self.assessment
    
    def assess_control(self, control_id: str, status: str, 
                       evidence: str = "", comments: str = "") -> bool:
        """
        Évalue un contrôle spécifique
        
        Args:
            control_id: ID du contrôle (ex: "A.5.1")
            status: "Implemented" | "Partially Implemented" | "Not Implemented" | "Not Applicable"
            evidence: Description de la preuve
            comments: Commentaires additionnels
        
        Returns:
            True si succès, False sinon
        """
        control = next((c for c in self.controls if c['id'] == control_id), None)
        if not control:
            return False
        
        assessment_item = {
            "control_id": control_id,
            "control_title": control['title'],
            "domain": control['domain'],
            "status": status,
            "evidence": evidence,
            "comments": comments,
            "assessed_at": datetime.now().isoformat()
        }
        
        self.assessment['controls_assessment'].append(assessment_item)
        return True
    
    def get_domain_controls(self, domain: str) -> List[Dict]:
        """Retourne tous les contrôles d'un domaine"""
        return [c for c in self.controls if c['domain'] == domain]
    
    def get_all_domains(self) -> List[str]:
        """Retourne la liste des domaines"""
        return list(set(c['domain'] for c in self.controls))
    
    def save_assessment(self, filename: str) -> None:
        """Sauvegarde l'évaluation en JSON"""
        with open(f"data/assessments/{filename}.json", 'w', encoding='utf-8') as f:
            json.dump(self.assessment, f, indent=2, ensure_ascii=False)
    
    def load_assessment(self, filename: str) -> Dict:
        """Charge une évaluation existante"""
        with open(f"data/assessments/{filename}.json", 'r', encoding='utf-8') as f:
            self.assessment = json.load(f)
        return self.assessment
