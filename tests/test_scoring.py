"""
Tests pour le module scoring
"""
import pytest
from modules.compliance_checker import ComplianceChecker
from modules.scoring import ComplianceScoring

@pytest.fixture
def sample_assessment():
    """Créer une évaluation de test avec des données"""
    checker = ComplianceChecker()
    assessment = checker.start_assessment("Test Org", "Tester")
    
    # Ajouter des évaluations de test
    test_data = [
        ("A.5.1", "Implemented", "Organizational controls"),
        ("A.5.2", "Implemented", "Organizational controls"),
        ("A.8.1", "Partially Implemented", "Technological controls"),
        ("A.8.2", "Not Implemented", "Technological controls"),
        ("A.8.3", "Not Applicable", "Technological controls"),
    ]
    
    for control_id, status, domain in test_data:
        # Simuler l'ajout direct
        checker.assessment['controls_assessment'].append({
            'control_id': control_id,
            'control_title': f"Test Control {control_id}",
            'domain': domain,
            'status': status,
            'evidence': 'Test evidence',
            'comments': 'Test comment',
            'assessed_at': '2026-01-13T12:00:00'
        })
    
    return checker.assessment

@pytest.fixture
def scoring(sample_assessment):
    """Créer une instance de ComplianceScoring"""
    return ComplianceScoring(sample_assessment)

class TestComplianceScoring:
    
    def test_initialization(self, sample_assessment):
        """Test l'initialisation du scoring"""
        scoring = ComplianceScoring(sample_assessment)
        
        assert scoring is not None
        assert len(scoring.controls_df) == 5
    
    def test_calculate_overall_score(self, scoring):
        """Test le calcul du score global"""
        score = scoring.calculate_overall_score()
        
        # Calcul attendu:
        # - 2 Implemented (100% chacun) = 2.0
        # - 1 Partially Implemented (50%) = 0.5
        # - 1 Not Implemented (0%) = 0.0
        # - 1 Not Applicable (exclu)
        # Total: 2.5 / 4 = 62.5%
        
        assert isinstance(score, float)
        assert score == 62.5
    
    def test_calculate_overall_score_empty(self):
        """Test le score avec une évaluation vide"""
        checker = ComplianceChecker()
        assessment = checker.start_assessment("Empty Org", "Tester")
        scoring = ComplianceScoring(assessment)
        
        score = scoring.calculate_overall_score()
        assert score == 0.0
    
    def test_calculate_domain_scores(self, scoring):
        """Test le calcul des scores par domaine"""
        domain_scores = scoring.calculate_domain_scores()
        
        assert isinstance(domain_scores, dict)
        assert "Organizational controls" in domain_scores
        assert "Technological controls" in domain_scores
        
        # Organizational: 2 Implemented sur 2 = 100%
        assert domain_scores["Organizational controls"] == 100.0
        
        # Technological: 1 Partially (50%) + 1 Not (0%) sur 2 = 25%
        assert domain_scores["Technological controls"] == 25.0
    
    def test_get_gaps(self, scoring):
        """Test l'identification des gaps"""
        gaps = scoring.get_gaps()
        
        assert isinstance(gaps, list)
        assert len(gaps) == 2  # 1 Partially + 1 Not Implemented
        
        # Vérifier que tous les gaps sont bien des non-conformités
        for gap in gaps:
            assert gap['status'] in ['Not Implemented', 'Partially Implemented']
    
    def test_get_statistics(self, scoring):
        """Test la récupération des statistiques complètes"""
        stats = scoring.get_statistics()
        
        assert isinstance(stats, dict)
        assert 'total_controls' in stats
        assert 'implemented' in stats
        assert 'partially_implemented' in stats
        assert 'not_implemented' in stats
        assert 'not_applicable' in stats
        assert 'overall_score' in stats
        assert 'domain_scores' in stats
        
        assert stats['total_controls'] == 5
        assert stats['implemented'] == 2
        assert stats['partially_implemented'] == 1
        assert stats['not_implemented'] == 1
        assert stats['not_applicable'] == 1
        assert stats['overall_score'] == 62.5
    
    def test_full_compliance_score(self):
        """Test le score à 100% de conformité"""
        checker = ComplianceChecker()
        assessment = checker.start_assessment("Perfect Org", "Tester")
        
        # Tous les contrôles implémentés
        for i in range(3):
            checker.assessment['controls_assessment'].append({
                'control_id': f"A.5.{i}",
                'control_title': f"Control {i}",
                'domain': "Organizational controls",
                'status': "Implemented",
                'evidence': 'Evidence',
                'comments': '',
                'assessed_at': '2026-01-13T12:00:00'
            })
        
        scoring = ComplianceScoring(checker.assessment)
        score = scoring.calculate_overall_score()
        
        assert score == 100.0
    
    def test_zero_compliance_score(self):
        """Test le score à 0% de conformité"""
        checker = ComplianceChecker()
        assessment = checker.start_assessment("Bad Org", "Tester")
        
        # Tous les contrôles non implémentés
        for i in range(3):
            checker.assessment['controls_assessment'].append({
                'control_id': f"A.5.{i}",
                'control_title': f"Control {i}",
                'domain': "Organizational controls",
                'status': "Not Implemented",
                'evidence': '',
                'comments': '',
                'assessed_at': '2026-01-13T12:00:00'
            })
        
        scoring = ComplianceScoring(checker.assessment)
        score = scoring.calculate_overall_score()
        
        assert score == 0.0
