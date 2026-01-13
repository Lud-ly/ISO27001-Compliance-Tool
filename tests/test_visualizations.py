"""
Tests pour le module visualizations
"""
import pytest
import base64
from modules.visualizations import ComplianceVisualizations

@pytest.fixture
def sample_statistics():
    """Statistiques de test"""
    return {
        'total_controls': 10,
        'implemented': 6,
        'partially_implemented': 2,
        'not_implemented': 1,
        'not_applicable': 1,
        'overall_score': 70.0,
        'domain_scores': {
            'Organizational controls': 80.0,
            'Technological controls': 60.0,
            'Physical controls': 75.0
        }
    }

@pytest.fixture
def viz(sample_statistics):
    """Créer une instance de ComplianceVisualizations"""
    return ComplianceVisualizations(sample_statistics)

class TestComplianceVisualizations:
    
    def test_initialization(self, sample_statistics):
        """Test l'initialisation"""
        viz = ComplianceVisualizations(sample_statistics)
        
        assert viz is not None
        assert viz.stats == sample_statistics
    
    def test_generate_status_pie_chart(self, viz):
        """Test la génération du pie chart"""
        chart_base64 = viz.generate_status_pie_chart()
        
        assert isinstance(chart_base64, str)
        assert len(chart_base64) > 0
        
        # Vérifier que c'est du base64 valide
        try:
            decoded = base64.b64decode(chart_base64)
            assert len(decoded) > 0
        except Exception as e:
            pytest.fail(f"Invalid base64: {e}")
    
    def test_generate_domain_bar_chart(self, viz):
        """Test la génération du bar chart"""
        chart_base64 = viz.generate_domain_bar_chart()
        
        assert isinstance(chart_base64, str)
        assert len(chart_base64) > 0
        
        # Vérifier que c'est du base64 valide
        try:
            decoded = base64.b64decode(chart_base64)
            assert len(decoded) > 0
        except Exception as e:
            pytest.fail(f"Invalid base64: {e}")
    
    def test_charts_with_empty_data(self):
        """Test la génération avec des données vides"""
        empty_stats = {
            'total_controls': 0,
            'implemented': 0,
            'partially_implemented': 0,
            'not_implemented': 0,
            'not_applicable': 0,
            'overall_score': 0.0,
            'domain_scores': {}
        }
        
        viz = ComplianceVisualizations(empty_stats)
        
        # Les graphiques devraient quand même se générer
        pie_chart = viz.generate_status_pie_chart()
        assert isinstance(pie_chart, str)
        
        bar_chart = viz.generate_domain_bar_chart()
        assert isinstance(bar_chart, str)
