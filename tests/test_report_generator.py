"""
Tests pour le module report_generator
"""
import pytest
import os
from modules.report_generator import ReportGenerator
from modules.compliance_checker import ComplianceChecker
from modules.scoring import ComplianceScoring
from modules.visualizations import ComplianceVisualizations

@pytest.fixture
def sample_data():
    """Créer des données de test complètes"""
    checker = ComplianceChecker()
    assessment = checker.start_assessment("Test Organization", "John Tester")
    
    # Ajouter quelques évaluations
    test_controls = [
        ("A.5.1", "Implemented", "Organizational controls"),
        ("A.5.2", "Partially Implemented", "Organizational controls"),
        ("A.8.1", "Not Implemented", "Technological controls"),
    ]
    
    for control_id, status, domain in test_controls:
        checker.assessment['controls_assessment'].append({
            'control_id': control_id,
            'control_title': f"Test Control {control_id}",
            'domain': domain,
            'status': status,
            'evidence': 'Test evidence',
            'comments': 'Test comment',
            'assessed_at': '2026-01-13T12:00:00'
        })
    
    scoring = ComplianceScoring(checker.assessment)
    stats = scoring.get_statistics()
    gaps = scoring.get_gaps()
    
    viz = ComplianceVisualizations(stats)
    charts = {
        'pie_chart': viz.generate_status_pie_chart(),
        'bar_chart': viz.generate_domain_bar_chart()
    }
    
    return {
        'assessment': checker.assessment,
        'statistics': stats,
        'gaps': gaps,
        'charts': charts
    }

class TestReportGenerator:
    
    def test_initialization(self, sample_data):
        """Test l'initialisation du générateur"""
        report_gen = ReportGenerator(
            sample_data['assessment'],
            sample_data['statistics'],
            sample_data['gaps']
        )
        
        assert report_gen is not None
        assert report_gen.assessment == sample_data['assessment']
        assert report_gen.stats == sample_data['statistics']
        assert report_gen.gaps == sample_data['gaps']
    
    def test_generate_pdf(self, sample_data, tmp_path):
        """Test la génération du PDF"""
        # Créer le dossier de sortie
        os.makedirs("data/assessments", exist_ok=True)
        
        report_gen = ReportGenerator(
            sample_data['assessment'],
            sample_data['statistics'],
            sample_data['gaps']
        )
        
        filename = "test_report"
        report_path = report_gen.generate_pdf(filename, sample_data['charts'])
        
        # Vérifier que le fichier existe
        assert os.path.exists(report_path)
        assert report_path.endswith('.pdf')
        
        # Vérifier que le fichier n'est pas vide
        assert os.path.getsize(report_path) > 0
        
        # Nettoyer
        os.remove(report_path)
    
    def test_generate_pdf_without_charts(self, sample_data):
        """Test la génération sans graphiques"""
        os.makedirs("data/assessments", exist_ok=True)
        
        report_gen = ReportGenerator(
            sample_data['assessment'],
            sample_data['statistics'],
            sample_data['gaps']
        )
        
        filename = "test_report_no_charts"
        report_path = report_gen.generate_pdf(filename, {})
        
        assert os.path.exists(report_path)
        assert os.path.getsize(report_path) > 0
        
        # Nettoyer
        os.remove(report_path)
    
    def test_generate_pdf_no_gaps(self, sample_data):
        """Test la génération avec 0 gaps"""
        os.makedirs("data/assessments", exist_ok=True)
        
        # Modifier pour n'avoir aucun gap
        sample_data['gaps'] = []
        
        report_gen = ReportGenerator(
            sample_data['assessment'],
            sample_data['statistics'],
            sample_data['gaps']
        )
        
        filename = "test_report_no_gaps"
        report_path = report_gen.generate_pdf(filename, sample_data['charts'])
        
        assert os.path.exists(report_path)
        
        # Nettoyer
        os.remove(report_path)
