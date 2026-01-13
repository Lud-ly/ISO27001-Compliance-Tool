"""
ISO 27001 Compliance Tool - CLI Version
"""
import os
from modules.compliance_checker import ComplianceChecker
from modules.scoring import ComplianceScoring
from modules.visualizations import ComplianceVisualizations
from modules.report_generator import ReportGenerator

def main():
    print("=" * 60)
    print("  ISO/IEC 27001:2022 Compliance Assessment Tool")
    print("=" * 60)
    print()
    
    # Initialiser le checker
    checker = ComplianceChecker()
    
    # Démarrer une nouvelle évaluation
    org = input("Organization name: ")
    assessor = input("Assessor name: ")
    
    assessment = checker.start_assessment(org, assessor)
    print(f"\n✓ Assessment started for {org}\n")
    
    # Exemple: évaluer quelques contrôles (mode démo)
    print("Demo mode: Assessing sample controls...\n")
    
    sample_assessments = [
        ("A.5.1", "Implemented", "Security policy documented and approved", ""),
        ("A.5.2", "Partially Implemented", "Roles defined but not fully documented", "Need update"),
        ("A.8.1", "Not Implemented", "", "Endpoint protection missing"),
        ("A.8.2", "Implemented", "Privileged access controls in place", ""),
    ]
    
    for control_id, status, evidence, comments in sample_assessments:
        checker.assess_control(control_id, status, evidence, comments)
        print(f"  ✓ Assessed {control_id}: {status}")
    
    print(f"\n✓ Assessment completed: {len(sample_assessments)} controls assessed\n")
    
    # Calculer les scores
    scoring = ComplianceScoring(assessment)
    stats = scoring.get_statistics()
    gaps = scoring.get_gaps()
    
    print("=" * 60)
    print("  RESULTS")
    print("=" * 60)
    print(f"Overall Compliance Score: {stats['overall_score']}%")
    print(f"Total Controls: {stats['total_controls']}")
    print(f"  - Implemented: {stats['implemented']}")
    print(f"  - Partially Implemented: {stats['partially_implemented']}")
    print(f"  - Not Implemented: {stats['not_implemented']}")
    print(f"  - Not Applicable: {stats['not_applicable']}")
    print()
    
    # Générer visualisations
    print("Generating visualizations...")
    viz = ComplianceVisualizations(stats)
    pie_chart = viz.generate_status_pie_chart()
    bar_chart = viz.generate_domain_bar_chart()
    
    charts = {
        'pie_chart': pie_chart,
        'bar_chart': bar_chart
    }
    
    # Générer rapport PDF
    print("Generating PDF report...")
    report_gen = ReportGenerator(assessment, stats, gaps)
    
    # Créer dossier si nécessaire
    os.makedirs("data/assessments", exist_ok=True)
    
    report_path = report_gen.generate_pdf(f"{org.replace(' ', '_')}_ISO27001_Report", charts)
    
    print(f"\n✓ Report generated: {report_path}")
    print("\nAssessment completed successfully!")

if __name__ == "__main__":
    main()
