"""
Tests pour le module compliance_checker
"""
import pytest
import json
import os
from modules.compliance_checker import ComplianceChecker

@pytest.fixture
def checker():
    """Fixture pour créer une instance de ComplianceChecker"""
    return ComplianceChecker()

@pytest.fixture
def sample_assessment(checker):
    """Fixture pour créer une évaluation de test"""
    return checker.start_assessment("Test Corp", "Jane Doe")

class TestComplianceChecker:
    
    def test_initialization(self, checker):
        """Test l'initialisation du checker"""
        assert checker is not None
        assert len(checker.controls) > 0
        assert isinstance(checker.controls, list)
    
    def test_start_assessment(self, checker):
        """Test le démarrage d'une nouvelle évaluation"""
        assessment = checker.start_assessment("Acme Corp", "John Smith")
        
        assert assessment is not None
        assert assessment['metadata']['organization'] == "Acme Corp"
        assert assessment['metadata']['assessor'] == "John Smith"
        assert assessment['metadata']['standard'] == "ISO/IEC 27001:2022"
        assert 'date' in assessment['metadata']
        assert assessment['controls_assessment'] == []
    
    def test_assess_control_valid(self, checker, sample_assessment):
        """Test l'évaluation d'un contrôle valide"""
        result = checker.assess_control(
            control_id="A.5.1",
            status="Implemented",
            evidence="Policy document in SharePoint",
            comments="Approved by CISO"
        )
        
        assert result is True
        assert len(checker.assessment['controls_assessment']) == 1
        
        assessed_control = checker.assessment['controls_assessment'][0]
        assert assessed_control['control_id'] == "A.5.1"
        assert assessed_control['status'] == "Implemented"
        assert assessed_control['evidence'] == "Policy document in SharePoint"
        assert assessed_control['comments'] == "Approved by CISO"
    
    def test_assess_control_invalid_id(self, checker, sample_assessment):
        """Test l'évaluation avec un ID de contrôle invalide"""
        result = checker.assess_control(
            control_id="A.99.99",
            status="Implemented"
        )
        
        assert result is False
        assert len(checker.assessment['controls_assessment']) == 0
    
    def test_assess_multiple_controls(self, checker, sample_assessment):
        """Test l'évaluation de plusieurs contrôles"""
        controls = [
            ("A.5.1", "Implemented"),
            ("A.5.2", "Partially Implemented"),
            ("A.8.1", "Not Implemented")
        ]
        
        for control_id, status in controls:
            checker.assess_control(control_id, status)
        
        assert len(checker.assessment['controls_assessment']) == 3
    
    def test_get_domain_controls(self, checker):
        """Test la récupération des contrôles par domaine"""
        domain = "Organizational controls"
        controls = checker.get_domain_controls(domain)
        
        assert isinstance(controls, list)
        assert len(controls) > 0
        assert all(c['domain'] == domain for c in controls)
    
    def test_get_all_domains(self, checker):
        """Test la récupération de tous les domaines"""
        domains = checker.get_all_domains()
        
        assert isinstance(domains, list)
        assert len(domains) > 0
        assert "Organizational controls" in domains
    
    def test_save_and_load_assessment(self, checker, sample_assessment, tmp_path):
        """Test la sauvegarde et le chargement d'une évaluation"""
        # Modifier le chemin de sauvegarde pour le test
        os.makedirs("data/assessments", exist_ok=True)
        
        # Ajouter quelques évaluations
        checker.assess_control("A.5.1", "Implemented", "Test evidence")
        checker.assess_control("A.5.2", "Not Implemented")
        
        # Sauvegarder
        filename = "test_assessment"
        checker.save_assessment(filename)
        
        # Créer un nouveau checker et charger
        new_checker = ComplianceChecker()
        loaded_assessment = new_checker.load_assessment(filename)
        
        assert loaded_assessment['metadata']['organization'] == "Test Corp"
        assert len(loaded_assessment['controls_assessment']) == 2
        
        # Nettoyer
        os.remove(f"data/assessments/{filename}.json")
    
    def test_assessment_with_all_statuses(self, checker, sample_assessment):
        """Test l'évaluation avec tous les statuts possibles"""
        statuses = [
            "Implemented",
            "Partially Implemented",
            "Not Implemented",
            "Not Applicable"
        ]
        
        controls_ids = ["A.5.1", "A.5.2", "A.8.1", "A.8.2"]
        
        for control_id, status in zip(controls_ids, statuses):
            result = checker.assess_control(control_id, status)
            assert result is True
        
        assert len(checker.assessment['controls_assessment']) == 4
