"""
Module de génération de rapports PDF
"""
from fpdf import FPDF
from datetime import datetime
from typing import Dict, List
import base64
import tempfile
import os

class ISO27001Report(FPDF):
    def header(self):
        """En-tête du PDF"""
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'ISO/IEC 27001:2022 Compliance Report', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        """Pied de page du PDF"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

class ReportGenerator:
    def __init__(self, assessment: Dict, statistics: Dict, gaps: List[Dict]):
        """Initialise le générateur de rapport"""
        self.assessment = assessment
        self.stats = statistics
        self.gaps = gaps
    
    def generate_pdf(self, output_filename: str, charts: Dict[str, str]) -> str:
        """
        Génère le rapport PDF complet
        
        Args:
            output_filename: Nom du fichier de sortie
            charts: Dict contenant les graphiques en base64
        
        Returns:
            Chemin du fichier généré
        """
        pdf = ISO27001Report()
        pdf.add_page()
        
        # Section 1: Executive Summary
        self._add_executive_summary(pdf)
        
        # Section 2: Assessment Metadata
        self._add_metadata(pdf)
        
        # Section 3: Overall Score
        self._add_overall_score(pdf)
        
        # Section 4: Graphiques
        if 'pie_chart' in charts:
            self._add_chart(pdf, charts['pie_chart'], 'Controls Status Distribution')
        
        if 'bar_chart' in charts:
            pdf.add_page()
            self._add_chart(pdf, charts['bar_chart'], 'Compliance Score by Domain')
        
        # Section 5: Domain Scores
        pdf.add_page()
        self._add_domain_scores(pdf)
        
        # Section 6: Identified Gaps
        pdf.add_page()
        self._add_gaps_analysis(pdf)
        
        # Section 7: Recommendations
        pdf.add_page()
        self._add_recommendations(pdf)
        
        # Sauvegarder
        output_path = f"data/assessments/{output_filename}.pdf"
        pdf.output(output_path)
        
        return output_path
    
    def _add_executive_summary(self, pdf: FPDF):
        """Ajoute le résumé exécutif"""
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, '1. Executive Summary', 0, 1)
        pdf.set_font('Arial', '', 11)
        
        overall_score = self.stats['overall_score']
        status = "Compliant" if overall_score >= 80 else "Non-Compliant"
        
        summary = f"""
This report presents the ISO/IEC 27001:2022 compliance assessment for 
{self.assessment['metadata']['organization']}.

Overall Compliance Score: {overall_score}% - {status}

Total Controls Assessed: {self.stats['total_controls']}
- Implemented: {self.stats['implemented']}
- Partially Implemented: {self.stats['partially_implemented']}
- Not Implemented: {self.stats['not_implemented']}
- Not Applicable: {self.stats['not_applicable']}

Identified Gaps: {len(self.gaps)} controls require attention.
        """
        
        pdf.multi_cell(0, 6, summary.strip())
        pdf.ln(5)
    
    def _add_metadata(self, pdf: FPDF):
        """Ajoute les métadonnées"""
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, '2. Assessment Information', 0, 1)
        pdf.set_font('Arial', '', 11)
        
        meta = self.assessment['metadata']
        info = f"""
Organization: {meta['organization']}
Assessor: {meta['assessor']}
Assessment Date: {meta['date'][:10]}
Standard: {meta['standard']}
        """
        
        pdf.multi_cell(0, 6, info.strip())
        pdf.ln(5)
    
    def _add_overall_score(self, pdf: FPDF):
        """Ajoute le score global"""
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, '3. Overall Compliance Score', 0, 1)
        
        score = self.stats['overall_score']
        color = (40, 167, 69) if score >= 80 else (220, 53, 69)
        
        pdf.set_font('Arial', 'B', 36)
        pdf.set_text_color(*color)
        pdf.cell(0, 15, f"{score}%", 0, 1, 'C')
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
    
    def _add_chart(self, pdf: FPDF, chart_base64: str, title: str):
        """Ajoute un graphique au PDF"""
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, title, 0, 1)
        
        # Décoder base64 et insérer image
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                tmp.write(base64.b64decode(chart_base64))
                tmp_path = tmp.name
            
            pdf.image(tmp_path, x=10, w=190)
            
            # Nettoyer le fichier temporaire
            os.unlink(tmp_path)
        except Exception as e:
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 10, f'[Chart could not be generated: {str(e)}]', 0, 1)
        
        pdf.ln(5)
    
    def _add_domain_scores(self, pdf: FPDF):
        """Ajoute les scores par domaine"""
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, '4. Compliance Score by Domain', 0, 1)
        
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(120, 8, 'Domain', 1)
        pdf.cell(40, 8, 'Score (%)', 1)
        pdf.cell(30, 8, 'Status', 1)
        pdf.ln()
        
        pdf.set_font('Arial', '', 10)
        for domain, score in self.stats['domain_scores'].items():
            # Pas de caractères Unicode - texte simple
            status = "COMPLIANT" if score >= 80 else "GAP"
            pdf.cell(120, 8, domain, 1)
            pdf.cell(40, 8, f"{score}%", 1, 0, 'C')
            pdf.cell(30, 8, status, 1)
            pdf.ln()
    
    def _add_gaps_analysis(self, pdf: FPDF):
        """Ajoute l'analyse des gaps"""
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, '5. Identified Gaps', 0, 1)
        
        if not self.gaps:
            pdf.set_font('Arial', 'I', 11)
            pdf.cell(0, 8, 'No gaps identified. Full compliance achieved!', 0, 1)
            return
        
        pdf.set_font('Arial', '', 10)
        for idx, gap in enumerate(self.gaps, 1):
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, f"{idx}. {gap['control_id']} - {gap['control_title']}", 0, 1)
            pdf.set_font('Arial', '', 9)
            pdf.cell(0, 5, f"   Domain: {gap['domain']} | Status: {gap['status']}", 0, 1)
            pdf.ln(2)
    
    def _add_recommendations(self, pdf: FPDF):
        """Ajoute les recommandations"""
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, '6. Recommendations', 0, 1)
        pdf.set_font('Arial', '', 11)
        
        not_implemented_count = len([g for g in self.gaps if g['status'] == 'Not Implemented'])
        partially_implemented_count = len([g for g in self.gaps if g['status'] == 'Partially Implemented'])
        
        recommendations = f"""
Based on the assessment findings, the following actions are recommended:

1. Priority Actions:
   - Address {not_implemented_count} not implemented controls
   - Complete {partially_implemented_count} partially implemented controls

2. Timeline:
   - Critical gaps: 30 days
   - High priority gaps: 90 days
   - Medium priority gaps: 180 days

3. Next Steps:
   - Create detailed remediation plan
   - Assign ownership for each gap
   - Schedule follow-up assessment in 6 months

4. Resources:
   - Allocate budget for security controls implementation
   - Provide ISO 27001 training to relevant personnel
   - Engage external consultants if needed for complex controls

5. Continuous Improvement:
   - Establish regular review cycles (quarterly)
   - Update risk assessments based on new threats
   - Monitor effectiveness of implemented controls
        """
        
        pdf.multi_cell(0, 6, recommendations.strip())
        pdf.ln(5)
        
        # Ajouter note de bas de page
        pdf.set_font('Arial', 'I', 9)
        pdf.set_text_color(100, 100, 100)
        pdf.multi_cell(0, 5, 
            "Note: This assessment is for internal use only. Official ISO 27001 certification "
            "requires audit by an accredited certification body."
        )
        pdf.set_text_color(0, 0, 0)
