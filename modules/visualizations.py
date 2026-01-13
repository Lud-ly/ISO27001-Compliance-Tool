"""
Module de génération de graphiques
"""
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from typing import Dict
import io
import base64

class ComplianceVisualizations:
    def __init__(self, statistics: Dict):
        """Initialise avec les statistiques"""
        self.stats = statistics
    
    def generate_status_pie_chart(self) -> str:
        """Génère un pie chart du statut des contrôles (base64 PNG)"""
        labels = ['Implemented', 'Partially Implemented', 'Not Implemented', 'Not Applicable']
        sizes = [
            self.stats['implemented'],
            self.stats['partially_implemented'],
            self.stats['not_implemented'],
            self.stats['not_applicable']
        ]
        colors = ['#28a745', '#ffc107', '#dc3545', '#6c757d']
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Gérer le cas où toutes les valeurs sont à 0
        if sum(sizes) == 0:
            ax.text(0.5, 0.5, 'No data available', 
                    ha='center', va='center', fontsize=16, color='gray')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        else:
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
        
        plt.title('ISO 27001 Controls Status Distribution', fontsize=14, fontweight='bold')
        
        # Convertir en base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return image_base64
    
    def generate_domain_bar_chart(self) -> str:
        """Génère un bar chart des scores par domaine (base64 PNG)"""
        domains = self.stats['domain_scores']
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Gérer le cas où il n'y a pas de domaines
        if not domains:
            ax.text(0.5, 0.5, 'No domain data available', 
                    ha='center', va='center', fontsize=16, color='gray')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        else:
            bars = ax.bar(domains.keys(), domains.values(), color='#007bff', alpha=0.7)
            
            # Ligne de référence 80% (conformité acceptable)
            ax.axhline(y=80, color='green', linestyle='--', label='Target (80%)')
            
            ax.set_xlabel('Domains', fontsize=12)
            ax.set_ylabel('Compliance Score (%)', fontsize=12)
            ax.set_ylim(0, 100)
            plt.xticks(rotation=45, ha='right')
            plt.legend()
            plt.grid(axis='y', alpha=0.3)
        
        ax.set_title('ISO 27001 Compliance Score by Domain', fontsize=14, fontweight='bold')
        
        # Convertir en base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return image_base64
    
    def generate_heatmap_plotly(self) -> str:
        """Génère une heatmap interactive (HTML Plotly)"""
        domains = list(self.stats['domain_scores'].keys())
        scores = list(self.stats['domain_scores'].values())
        
        # Gérer le cas vide
        if not domains:
            return "<div style='text-align:center; padding:50px; color:gray;'>No domain data available</div>"
        
        fig = go.Figure(data=go.Heatmap(
            z=[scores],
            x=domains,
            y=['Compliance Score'],
            colorscale='RdYlGn',
            text=[scores],
            texttemplate='%{text:.1f}%',
            textfont={"size": 12},
            colorbar=dict(title="Score (%)")
        ))
        
        fig.update_layout(
            title='ISO 27001 Compliance Heatmap',
            xaxis_title='Domains',
            height=300
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
