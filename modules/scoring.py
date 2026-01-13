"""
Module de calcul de scoring de conformité
"""
from typing import Dict, List
import pandas as pd

class ComplianceScoring:
    def __init__(self, assessment: Dict):
        """Initialise avec une évaluation"""
        self.assessment = assessment
        self.controls_df = pd.DataFrame(assessment['controls_assessment'])
    
    def calculate_overall_score(self) -> float:
        """
        Calcule le score global de conformité (0-100)
        
        Implemented = 100%
        Partially Implemented = 50%
        Not Implemented = 0%
        Not Applicable = exclu du calcul
        """
        if self.controls_df.empty:
            return 0.0
        
        # Exclure les "Not Applicable"
        applicable_controls = self.controls_df[
            self.controls_df['status'] != 'Not Applicable'
        ]
        
        if applicable_controls.empty:
            return 0.0
        
        weights = {
            'Implemented': 1.0,
            'Partially Implemented': 0.5,
            'Not Implemented': 0.0
        }
        
        scores = applicable_controls['status'].map(weights)
        overall_score = (scores.sum() / len(applicable_controls)) * 100
        
        return round(overall_score, 2)
    
    def calculate_domain_scores(self) -> Dict[str, float]:
        """Calcule le score par domaine"""
        domains = {}
        
        for domain in self.controls_df['domain'].unique():
            domain_controls = self.controls_df[
                (self.controls_df['domain'] == domain) & 
                (self.controls_df['status'] != 'Not Applicable')
            ]
            
            if not domain_controls.empty:
                weights = {
                    'Implemented': 1.0,
                    'Partially Implemented': 0.5,
                    'Not Implemented': 0.0
                }
                scores = domain_controls['status'].map(weights)
                domain_score = (scores.sum() / len(domain_controls)) * 100
                domains[domain] = round(domain_score, 2)
        
        return domains
    
    def get_gaps(self) -> List[Dict]:
        """Identifie les gaps de conformité"""
        gaps = self.controls_df[
            self.controls_df['status'].isin(['Not Implemented', 'Partially Implemented'])
        ]
        
        return gaps[['control_id', 'control_title', 'domain', 'status']].to_dict('records')
    
    def get_statistics(self) -> Dict:
        """Statistiques globales"""
        total = len(self.controls_df)
        
        status_counts = self.controls_df['status'].value_counts().to_dict()
        
        return {
            "total_controls": total,
            "implemented": status_counts.get('Implemented', 0),
            "partially_implemented": status_counts.get('Partially Implemented', 0),
            "not_implemented": status_counts.get('Not Implemented', 0),
            "not_applicable": status_counts.get('Not Applicable', 0),
            "overall_score": self.calculate_overall_score(),
            "domain_scores": self.calculate_domain_scores()
        }
