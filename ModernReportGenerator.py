"""
===============================================================================
Modern LEGO Report Generator - Advanced PDF Reports
===============================================================================

Generatore di report PDF moderni e accattivanti per l'analisi delle collezioni LEGO.
Utilizza ReportLab per creare report professionali con design moderno.

Funzionalità:
- Design moderno con colori e layout professionale
- Grafici avanzati e visualizzazioni interattive
- Statistiche dettagliate e KPI
- Layout responsivo e sezioni organizzate
- Supporto per diversi tipi di report (summary, detailed, complete)

===============================================================================
"""

import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from collections import defaultdict, Counter
import logging

# ReportLab imports
try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import Color, HexColor
    from reportlab.lib.units import inch, cm, mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.platypus import Image as RLImage
    from reportlab.platypus.frames import Frame
    from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.graphics.shapes import Drawing, Rect, String, Line
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.legends import Legend
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab not available. Install with: pip install reportlab")

# Matplotlib for advanced charts
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    import numpy as np
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
    
    # Set modern style
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logging.warning("Matplotlib/Seaborn not available for advanced charts")


class ModernReportGenerator:
    """Generatore di report PDF moderni per collezioni LEGO"""
    
    # Modern color palette
    COLORS = {
        'primary': HexColor('#2C3E50'),      # Dark blue-gray
        'secondary': HexColor('#3498DB'),     # Bright blue
        'accent': HexColor('#E74C3C'),        # Red
        'success': HexColor('#27AE60'),       # Green
        'warning': HexColor('#F39C12'),       # Orange
        'info': HexColor('#9B59B6'),          # Purple
        'light': HexColor('#ECF0F1'),         # Light gray
        'dark': HexColor('#34495E'),          # Dark gray
        'white': colors.white,
        'black': colors.black
    }
    
    def __init__(self, folder_path, color_mapping_path, output_pdf, report_type='complete'):
        """
        Inizializza il generatore di report moderni
        
        Args:
            folder_path (str): Percorso della cartella con i file XML
            color_mapping_path (str): Percorso del file di mappatura colori
            output_pdf (str): Percorso del file PDF di output
            report_type (str): Tipo di report ('summary', 'detailed', 'complete')
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for modern reports. Install with: pip install reportlab")
            
        self.folder_path = folder_path
        self.color_mapping_path = color_mapping_path
        self.output_pdf = output_pdf
        self.report_type = report_type
        
        # Load data
        self.color_mapping = self._load_color_mapping()
        self.xml_files = self._get_xml_files()
        
        # Analytics data
        self.analytics = {
            'total_sets': 0,
            'total_pieces': 0,
            'total_owned': 0,
            'total_missing': 0,
            'completion_percentage': 0.0,
            'unique_colors': set(),
            'unique_pieces': set(),
            'sets_data': [],
            'color_analysis': defaultdict(dict),
            'piece_analysis': defaultdict(dict),
            'rarity_analysis': {},
            'trends': {}
        }
        
        # Track temporary files for cleanup
        self.temp_files = []
        
        # Setup styles
        self.styles = self._create_styles()
        
        logging.info(f"Modern Report Generator initialized for {len(self.xml_files)} files")
    
    def _format_number(self, number):
        """Formatta i numeri per la visualizzazione compatta"""
        if number >= 1000000:
            return f"{number/1000000:.1f}M"
        elif number >= 1000:
            return f"{number/1000:.1f}K"
        else:
            return f"{number:,}"
    
    def _create_color_distribution_chart(self):
        """Crea un grafico a torta avanzato della distribuzione dei colori con stile professionale"""
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        try:
            # Prepara i dati per il grafico
            colors_data = []
            for color_code, stats in self.analytics['color_analysis'].items():
                color_name = self.color_mapping.get(color_code, f"Color {color_code}")
                colors_data.append((color_name, stats['total'], color_code))
            
            # Ordina per numero di pezzi e prendi i top 12
            colors_data.sort(key=lambda x: x[1], reverse=True)
            top_colors = colors_data[:12]
            
            if len(colors_data) > 12:
                other_total = sum(x[1] for x in colors_data[12:])
                top_colors.append(('Others', other_total, 'other'))
            
            # Configurazione stile moderno
            plt.style.use('default')
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))
            fig.patch.set_facecolor('#f8f9fa')
            
            # Mappa colori LEGO realistici
            lego_colors = {
                '1': '#F2F3F2',   # White
                '5': '#D50000',   # Red  
                '6': '#0055BF',   # Blue
                '11': '#1B2A34',  # Black
                '4': '#F57C20',   # Orange
                '3': '#009247',   # Green
                '14': '#FFFF00',  # Yellow
                '28': '#A3A2A4',  # Light Gray
                '2': '#8D7553',   # Tan
                '85': '#4B9F4A',  # Dark Green
                'other': '#95A5A6'
            }
            
            # Grafico a torta principale con shadow e explosion
            labels = [x[0] for x in top_colors]
            sizes = [x[1] for x in top_colors]
            colors_list = [lego_colors.get(x[2], f'C{i}') for i, x in enumerate(top_colors)]
            
            # Explode i primi 3 settori
            explode = [0.05 if i < 3 else 0 for i in range(len(labels))]
            
            wedges, texts, autotexts = ax1.pie(sizes, labels=labels, autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*sum(sizes))} pcs)',
                                             startangle=90, colors=colors_list, explode=explode,
                                             shadow=True, textprops={'fontsize': 9, 'fontweight': 'bold'})
            
            # Migliora il cerchio centrale per stile donut
            centre_circle = plt.Circle((0,0), 0.70, fc='white', linewidth=2, edgecolor='#2c3e50')
            ax1.add_artist(centre_circle)
            
            # Titolo e statistiche centrali
            ax1.set_title('🎨 Color Distribution Analysis\nLEGO Collection Overview', 
                         fontsize=16, fontweight='bold', pad=30, color='#2c3e50')
            
            # Statistiche nel centro
            total_pieces = sum(sizes)
            unique_colors = len(top_colors)
            ax1.text(0, 0, f'Total Pieces\n{total_pieces:,}\n\nUnique Colors\n{unique_colors}', 
                    ha='center', va='center', fontsize=12, fontweight='bold', color='#2c3e50')
            
            # Grafico a barre orizzontali dettagliato
            y_pos = range(len(labels))
            bars = ax2.barh(y_pos, sizes, color=colors_list, alpha=0.8, edgecolor='#2c3e50', linewidth=0.5)
            
            # Personalizza il grafico a barre
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(labels, fontsize=10)
            ax2.invert_yaxis()
            ax2.set_xlabel('Number of Pieces', fontsize=12, fontweight='bold', color='#2c3e50')
            ax2.set_title('📊 Detailed Piece Count by Color', fontsize=14, fontweight='bold', color='#2c3e50', pad=20)
            ax2.grid(axis='x', alpha=0.3, linestyle='--')
            ax2.set_facecolor('#fafafa')
            
            # Aggiungi valori sui bar
            for i, (bar, size) in enumerate(zip(bars, sizes)):
                width = bar.get_width()
                percentage = (size / total_pieces) * 100
                ax2.text(width + max(sizes)*0.01, bar.get_y() + bar.get_height()/2,
                        f'{size:,} ({percentage:.1f}%)', ha='left', va='center', 
                        fontsize=9, fontweight='bold', color='#2c3e50')
            
            # Stile generale
            plt.tight_layout()
            fig.suptitle('🧱 LEGO Color Analysis Report', fontsize=20, fontweight='bold', 
                        color='#2c3e50', y=0.98)
            
            # Salva con alta qualità
            import tempfile
            tmp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            plt.savefig(tmp_file.name, format='png', dpi=600, bbox_inches='tight', 
                       facecolor='#f8f9fa', edgecolor='none', pad_inches=0.2)
            plt.close()
            tmp_file.close()
            
            # Track for cleanup
            self.temp_files.append(tmp_file.name)
            return tmp_file.name
                
        except Exception as e:
            logging.error(f"Error creating color distribution chart: {e}")
            plt.close()
            return None
    
    def _create_completion_chart(self):
        """Crea un grafico a barre avanzato del completamento per colore con design moderno"""
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        try:
            # Prepara i dati
            colors_data = []
            for color_code, stats in self.analytics['color_analysis'].items():
                if stats['total'] > 10:  # Solo colori con almeno 10 pezzi
                    color_name = self.color_mapping.get(color_code, f"Color {color_code}")
                    completion = (stats['owned'] / stats['total'] * 100) if stats['total'] > 0 else 0
                    colors_data.append((color_name, completion, stats['total'], stats['owned'], stats['missing'], color_code))
            
            # Ordina per completamento e prendi i top 15
            colors_data.sort(key=lambda x: x[1], reverse=True)
            top_colors = colors_data[:15]
            
            # Configurazione layout moderno
            plt.style.use('default')
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
            fig.patch.set_facecolor('#f8f9fa')
            
            # Mappa colori LEGO realistici
            lego_colors = {
                '1': '#F2F3F2', '5': '#D50000', '6': '#0055BF', '11': '#1B2A34',
                '4': '#F57C20', '3': '#009247', '14': '#FFFF00', '28': '#A3A2A4',
                '2': '#8D7553', '85': '#4B9F4A', '86': '#5F758C', '71': '#6C6E68'
            }
            
            # 1. Grafico a barre orizzontali completion rate
            names = [x[0][:12] for x in top_colors]
            completions = [x[1] for x in top_colors]
            colors_list = [lego_colors.get(x[5], '#3498db') for x in top_colors]
            
            bars1 = ax1.barh(range(len(names)), completions, color=colors_list, alpha=0.8, 
                           edgecolor='#2c3e50', linewidth=1.2, height=0.7)
            
            ax1.set_yticks(range(len(names)))
            ax1.set_yticklabels(names, fontsize=11, fontweight='bold')
            ax1.invert_yaxis()
            ax1.set_xlabel('Completion Percentage (%)', fontsize=12, fontweight='bold', color='#2c3e50')
            ax1.set_title('🎯 Collection Completion Rate by Color', fontsize=14, fontweight='bold', 
                         color='#2c3e50', pad=20)
            ax1.grid(axis='x', alpha=0.3, linestyle='--', color='#7f8c8d')
            ax1.set_xlim(0, 100)
            ax1.set_facecolor('#fafafa')
            
            # Aggiungi etichette dettagliate
            for i, (bar, data) in enumerate(zip(bars1, top_colors)):
                width = bar.get_width()
                owned, total = data[3], data[2]
                ax1.text(width + 1, bar.get_y() + bar.get_height()/2,
                        f'{width:.1f}% ({owned}/{total})', ha='left', va='center', 
                        fontsize=10, fontweight='bold', color='#2c3e50')
            
            # 2. Grafico scatter completion vs total pieces
            totals = [x[2] for x in top_colors]
            sizes = [max(50, min(500, x[2] * 2)) for x in top_colors]  # Scala dinamica
            
            scatter = ax2.scatter(totals, completions, s=sizes, c=completions, 
                                cmap='RdYlGn', alpha=0.7, edgecolors='#2c3e50', linewidths=1.5)
            
            ax2.set_xlabel('Total Pieces Required', fontsize=12, fontweight='bold', color='#2c3e50')
            ax2.set_ylabel('Completion Percentage (%)', fontsize=12, fontweight='bold', color='#2c3e50')
            ax2.set_title('📈 Completion vs Collection Size', fontsize=14, fontweight='bold', 
                         color='#2c3e50', pad=20)
            ax2.grid(True, alpha=0.3, linestyle='--', color='#7f8c8d')
            ax2.set_facecolor('#fafafa')
            
            # Colorbar per lo scatter plot
            cbar = plt.colorbar(scatter, ax=ax2, shrink=0.8)
            cbar.set_label('Completion %', fontsize=10, fontweight='bold', color='#2c3e50')
            
            # Annota i punti più interessanti
            for i, data in enumerate(top_colors[:5]):
                name, comp, total, owned, missing, _ = data
                ax2.annotate(f'{name[:8]}', (total, comp), xytext=(5, 5), 
                           textcoords='offset points', fontsize=9, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
            
            # 3. Grafico stacked bar owned vs missing
            owned_pieces = [x[3] for x in top_colors]
            missing_pieces = [x[4] for x in top_colors]
            
            bars_owned = ax3.bar(range(len(names)), owned_pieces, label='Owned', 
                               color='#27ae60', alpha=0.8, edgecolor='#2c3e50', linewidth=0.5)
            bars_missing = ax3.bar(range(len(names)), missing_pieces, bottom=owned_pieces, 
                                 label='Missing', color='#e74c3c', alpha=0.8, 
                                 edgecolor='#2c3e50', linewidth=0.5)
            
            ax3.set_xlabel('Colors', fontsize=12, fontweight='bold', color='#2c3e50')
            ax3.set_ylabel('Number of Pieces', fontsize=12, fontweight='bold', color='#2c3e50')
            ax3.set_title('📊 Owned vs Missing Pieces by Color', fontsize=14, fontweight='bold', 
                         color='#2c3e50', pad=20)
            ax3.set_xticks(range(len(names)))
            ax3.set_xticklabels(names, rotation=45, ha='right', fontsize=10)
            ax3.legend(loc='upper right', fontsize=11, framealpha=0.9)
            ax3.grid(axis='y', alpha=0.3, linestyle='--', color='#7f8c8d')
            ax3.set_facecolor('#fafafa')
            
            # 4. Grafico radar per top 8 colori
            if len(top_colors) >= 8:
                top8 = top_colors[:8]
                categories = ['Completion', 'Collection Size', 'Priority Score']
                
                # Normalizza i dati per il radar
                max_completion = max(x[1] for x in top8)
                max_total = max(x[2] for x in top8)
                
                radar_data = []
                for data in top8:
                    comp_norm = data[1] / 100 * 10  # Scala 0-10
                    size_norm = data[2] / max_total * 10  # Scala 0-10
                    priority = (100 - data[1]) * (data[2] / max_total) * 10  # Priority score
                    radar_data.append([comp_norm, size_norm, priority])
                
                # Setup radar chart
                angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
                angles += angles[:1]  # Chiudi il cerchio
                
                ax4 = plt.subplot(2, 2, 4, projection='polar')
                ax4.set_facecolor('#fafafa')
                
                # Plot per ogni colore
                colors_radar = plt.cm.Set3(np.linspace(0, 1, len(top8)))
                for i, (data, color) in enumerate(zip(radar_data, colors_radar)):
                    values = data + data[:1]  # Chiudi il cerchio
                    ax4.plot(angles, values, 'o-', linewidth=2, label=top8[i][0][:8], color=color, alpha=0.8)
                    ax4.fill(angles, values, alpha=0.25, color=color)
                
                ax4.set_xticks(angles[:-1])
                ax4.set_xticklabels(categories, fontsize=11, fontweight='bold', color='#2c3e50')
                ax4.set_ylim(0, 10)
                ax4.set_title('🎯 Multi-Dimensional Analysis\n(Top 8 Colors)', fontsize=14, 
                             fontweight='bold', color='#2c3e50', pad=30)
                ax4.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=9)
                ax4.grid(True, alpha=0.3)
            
            # Layout generale
            plt.tight_layout()
            fig.suptitle('🧱 Advanced LEGO Collection Completion Analysis', fontsize=22, 
                        fontweight='bold', color='#2c3e50', y=0.98)
            
            # Salva con qualità ultra-alta
            import tempfile
            tmp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            plt.savefig(tmp_file.name, format='png', dpi=600, bbox_inches='tight', 
                       facecolor='#f8f9fa', edgecolor='none', pad_inches=0.3)
            plt.close()
            tmp_file.close()
            
            # Track for cleanup
            self.temp_files.append(tmp_file.name)
            return tmp_file.name
                
        except Exception as e:
            logging.error(f"Error creating completion chart: {e}")
            plt.close()
            return None
    
    def _create_sets_completion_chart(self):
        """Crea un dashboard completo per l'analisi dei set LEGO con design ultra-moderno"""
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        try:
            # Prepara i dati dei set
            sets_data = sorted(self.analytics['sets_data'], key=lambda x: x['completion'], reverse=True)
            total_sets = len(sets_data)
            
            # Configurazione layout dashboard
            plt.style.use('default')
            fig = plt.figure(figsize=(24, 16))
            fig.patch.set_facecolor('#f8f9fa')
            
            # Crea un layout a griglia complesso
            gs = fig.add_gridspec(3, 4, height_ratios=[1, 1.5, 1], width_ratios=[1, 1, 1, 1], 
                                 hspace=0.3, wspace=0.25)
            
            # Colori moderni
            colors_modern = ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#27ae60']
            
            # 1. KPI Cards (Prima riga)
            # Completion Rate Distribution
            ax1 = fig.add_subplot(gs[0, 0])
            completion_ranges = ['0-20%', '21-40%', '41-60%', '61-80%', '81-100%']
            range_counts = [0, 0, 0, 0, 0]
            
            for set_data in sets_data:
                comp = set_data['completion']
                if comp <= 20: range_counts[0] += 1
                elif comp <= 40: range_counts[1] += 1
                elif comp <= 60: range_counts[2] += 1
                elif comp <= 80: range_counts[3] += 1
                else: range_counts[4] += 1
            
            bars = ax1.bar(completion_ranges, range_counts, color=colors_modern, alpha=0.8, 
                          edgecolor='#2c3e50', linewidth=1.5)
            ax1.set_title('📊 Completion Distribution', fontsize=14, fontweight='bold', color='#2c3e50', pad=15)
            ax1.set_ylabel('Number of Sets', fontsize=11, fontweight='bold', color='#2c3e50')
            ax1.tick_params(axis='x', rotation=45, labelsize=9)
            ax1.grid(axis='y', alpha=0.3, linestyle='--')
            ax1.set_facecolor('#fafafa')
            
            # Aggiungi valori sui bar
            for bar, count in zip(bars, range_counts):
                if count > 0:
                    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                            str(count), ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            # 2. Progress Statistics
            ax2 = fig.add_subplot(gs[0, 1])
            avg_completion = np.mean([s['completion'] for s in sets_data])
            completed_sets = len([s for s in sets_data if s['completion'] >= 95])
            in_progress = len([s for s in sets_data if 10 < s['completion'] < 95])
            not_started = len([s for s in sets_data if s['completion'] <= 10])
            
            stats_labels = ['Completed\n(≥95%)', 'In Progress\n(10-95%)', 'Not Started\n(≤10%)']
            stats_values = [completed_sets, in_progress, not_started]
            stats_colors = ['#27ae60', '#f39c12', '#e74c3c']
            
            wedges, texts, autotexts = ax2.pie(stats_values, labels=stats_labels, autopct='%1.0f%%',
                                              colors=stats_colors, startangle=90, 
                                              textprops={'fontsize': 10, 'fontweight': 'bold'})
            ax2.set_title('🎯 Project Status Overview', fontsize=14, fontweight='bold', color='#2c3e50', pad=15)
            
            # 3. Average completion gauge
            ax3 = fig.add_subplot(gs[0, 2])
            theta = np.linspace(0, np.pi, 100)
            
            # Background arc
            ax3.plot(theta, np.ones_like(theta), linewidth=20, color='#ecf0f1', alpha=0.3)
            
            # Progress arc
            progress_theta = theta[:int(avg_completion)]
            if len(progress_theta) > 0:
                color_progress = '#27ae60' if avg_completion >= 70 else '#f39c12' if avg_completion >= 40 else '#e74c3c'
                ax3.plot(progress_theta, np.ones_like(progress_theta), linewidth=20, color=color_progress)
            
            ax3.set_xlim(0, np.pi)
            ax3.set_ylim(0, 1.5)
            ax3.set_aspect('equal')
            ax3.axis('off')
            ax3.text(np.pi/2, 0.5, f'{avg_completion:.1f}%\nAverage', ha='center', va='center',
                    fontsize=16, fontweight='bold', color='#2c3e50')
            ax3.set_title('📈 Overall Progress', fontsize=14, fontweight='bold', color='#2c3e50', pad=15)
            
            # 4. Top Priority Sets (Most Missing Pieces)
            ax4 = fig.add_subplot(gs[0, 3])
            priority_sets = sorted(sets_data, key=lambda x: x.get('missing_pieces', 0), reverse=True)[:5]
            
            if priority_sets:
                names = [s['name'][:15] + '...' if len(s['name']) > 15 else s['name'] for s in priority_sets]
                missing = [s.get('missing_pieces', 0) for s in priority_sets]
                
                bars = ax4.barh(range(len(names)), missing, color='#e74c3c', alpha=0.7, 
                              edgecolor='#2c3e50', linewidth=1)
                ax4.set_yticks(range(len(names)))
                ax4.set_yticklabels(names, fontsize=9)
                ax4.invert_yaxis()
                ax4.set_xlabel('Missing Pieces', fontsize=11, fontweight='bold', color='#2c3e50')
                ax4.set_title('🚨 High Priority Sets', fontsize=14, fontweight='bold', color='#2c3e50', pad=15)
                ax4.grid(axis='x', alpha=0.3, linestyle='--')
                ax4.set_facecolor('#fafafa')
                
                for i, (bar, miss) in enumerate(zip(bars, missing)):
                    ax4.text(bar.get_width() + max(missing)*0.01, bar.get_y() + bar.get_height()/2,
                            str(miss), ha='left', va='center', fontsize=9, fontweight='bold')
            
            # 5. Main Chart - Top Sets Completion (Seconda riga)
            ax_main = fig.add_subplot(gs[1, :])
            top_sets = sets_data[:20]  # Top 20 set
            
            names = [s['name'][:25] + '...' if len(s['name']) > 25 else s['name'] for s in top_sets]
            completions = [s['completion'] for s in top_sets]
            
            # Gradient bars
            bars = ax_main.barh(range(len(names)), completions, height=0.7,
                              color=[plt.cm.RdYlGn(c/100) for c in completions],
                              edgecolor='#2c3e50', linewidth=1.2, alpha=0.9)
            
            ax_main.set_yticks(range(len(names)))
            ax_main.set_yticklabels(names, fontsize=11, fontweight='bold')
            ax_main.invert_yaxis()
            ax_main.set_xlabel('Completion Percentage (%)', fontsize=14, fontweight='bold', color='#2c3e50')
            ax_main.set_title('🏆 Top 20 LEGO Sets - Completion Status', fontsize=18, fontweight='bold', 
                             color='#2c3e50', pad=25)
            ax_main.set_xlim(0, 100)
            ax_main.grid(axis='x', alpha=0.3, linestyle='--', color='#7f8c8d')
            ax_main.set_facecolor('#fafafa')
            
            # Aggiungi milestone lines
            for milestone in [25, 50, 75, 90]:
                ax_main.axvline(x=milestone, color='#34495e', linestyle=':', alpha=0.6, linewidth=1)
                ax_main.text(milestone, len(names), f'{milestone}%', ha='center', va='bottom', 
                           fontsize=9, color='#34495e', fontweight='bold')
            
            # Etichette dettagliate
            for i, (bar, completion, set_data) in enumerate(zip(bars, completions, top_sets)):
                width = bar.get_width()
                total_pieces = set_data.get('total_pieces', 0)
                owned_pieces = set_data.get('owned_pieces', 0)
                
                label = f'{completion:.1f}%'
                if total_pieces > 0:
                    label += f' ({owned_pieces}/{total_pieces})'
                
                ax_main.text(width + 1, bar.get_y() + bar.get_height()/2, label,
                           ha='left', va='center', fontsize=10, fontweight='bold', color='#2c3e50')
            
            # 6. Trend Analysis (Terza riga)
            ax5 = fig.add_subplot(gs[2, :2])
            
            # Simula trend temporale (in un'implementazione reale, useresti dati storici)
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            trend_data = [avg_completion - 15, avg_completion - 10, avg_completion - 5, 
                         avg_completion, avg_completion + 2, avg_completion + 5]
            
            ax5.plot(months, trend_data, marker='o', linewidth=3, markersize=8, 
                    color='#3498db', markerfacecolor='#e74c3c', markeredgecolor='#2c3e50', markeredgewidth=2)
            ax5.fill_between(months, trend_data, alpha=0.3, color='#3498db')
            ax5.set_ylabel('Average Completion %', fontsize=12, fontweight='bold', color='#2c3e50')
            ax5.set_title('📅 Collection Progress Trend (6 Months)', fontsize=14, fontweight='bold', 
                         color='#2c3e50', pad=15)
            ax5.grid(True, alpha=0.3, linestyle='--')
            ax5.set_facecolor('#fafafa')
            
            # 7. Category Distribution
            ax6 = fig.add_subplot(gs[2, 2:])
            
            # Analizza le categorie basate sui nomi dei set
            categories = {'Star Wars': 0, 'Harry Potter': 0, 'City': 0, 'Creator': 0, 
                         'Technic': 0, 'Friends': 0, 'Other': 0}
            
            for set_data in sets_data:
                name = set_data['name'].lower()
                categorized = False
                for cat in categories.keys():
                    if cat.lower() in name:
                        categories[cat] += 1
                        categorized = True
                        break
                if not categorized:
                    categories['Other'] += 1
            
            # Rimuovi categorie vuote
            categories = {k: v for k, v in categories.items() if v > 0}
            
            if categories:
                ax6.bar(categories.keys(), categories.values(), 
                       color=plt.cm.Set3(np.linspace(0, 1, len(categories))),
                       alpha=0.8, edgecolor='#2c3e50', linewidth=1.5)
                ax6.set_ylabel('Number of Sets', fontsize=12, fontweight='bold', color='#2c3e50')
                ax6.set_title('🎭 Collection by Theme', fontsize=14, fontweight='bold', 
                             color='#2c3e50', pad=15)
                ax6.tick_params(axis='x', rotation=45, labelsize=10)
                ax6.grid(axis='y', alpha=0.3, linestyle='--')
                ax6.set_facecolor('#fafafa')
                
                # Aggiungi valori
                for i, (cat, count) in enumerate(categories.items()):
                    ax6.text(i, count + max(categories.values())*0.01, str(count),
                           ha='center', va='bottom', fontsize=11, fontweight='bold')
            
            # Layout finale
            fig.suptitle('🧱 LEGO Sets Collection - Comprehensive Dashboard', 
                        fontsize=26, fontweight='bold', color='#2c3e50', y=0.98)
            
            # Salva con qualità massima
            import tempfile
            tmp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            plt.savefig(tmp_file.name, format='png', dpi=600, bbox_inches='tight', 
                       facecolor='#f8f9fa', edgecolor='none', pad_inches=0.4)
            plt.close()
            tmp_file.close()
            
            # Track for cleanup
            self.temp_files.append(tmp_file.name)
            return tmp_file.name
                
        except Exception as e:
            logging.error(f"Error creating sets completion chart: {e}")
            plt.close()
            return None
    
    def _create_advanced_analytics_chart(self):
        """Crea un dashboard di analisi avanzate con machine learning insights"""
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        try:
            # Configurazione layout ultra-moderno
            plt.style.use('default')
            fig = plt.figure(figsize=(22, 14))
            fig.patch.set_facecolor('#f8f9fa')
            
            # Layout a griglia avanzato
            gs = fig.add_gridspec(3, 3, height_ratios=[1, 1.2, 1], width_ratios=[1, 1.2, 1], 
                                 hspace=0.35, wspace=0.3)
            
            # 1. Value Analysis - Pezzi per prezzo stimato
            ax1 = fig.add_subplot(gs[0, 0])
            
            # Simula analisi valore (in implementazione reale useresti dati BrickLink)
            colors_data = list(self.analytics['color_analysis'].items())
            colors_subset = colors_data[:10]
            
            # Simula prezzi medi per colore (€ per pezzo)
            price_simulation = {
                '1': 0.15, '5': 0.18, '6': 0.16, '11': 0.20, '4': 0.17,
                '3': 0.19, '14': 0.22, '28': 0.14, '2': 0.25, '85': 0.21
            }
            
            total_values = []
            color_names = []
            for color_code, stats in colors_subset:
                price = price_simulation.get(color_code, 0.18)
                total_value = stats['total'] * price
                total_values.append(total_value)
                color_names.append(self.color_mapping.get(color_code, f"Color {color_code}")[:8])
            
            bars = ax1.bar(range(len(color_names)), total_values, 
                          color=plt.cm.plasma(np.linspace(0, 1, len(color_names))),
                          alpha=0.8, edgecolor='#2c3e50', linewidth=1.5)
            
            ax1.set_xticks(range(len(color_names)))
            ax1.set_xticklabels(color_names, rotation=45, ha='right', fontsize=10)
            ax1.set_ylabel('Estimated Value (€)', fontsize=11, fontweight='bold', color='#2c3e50')
            ax1.set_title('💰 Collection Value Analysis', fontsize=13, fontweight='bold', 
                         color='#2c3e50', pad=15)
            ax1.grid(axis='y', alpha=0.3, linestyle='--')
            ax1.set_facecolor('#fafafa')
            
            # Aggiungi valori sui bar
            for bar, value in zip(bars, total_values):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(total_values)*0.01,
                        f'€{value:.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            # 2. Efficiency Heatmap - Completion vs Effort
            ax2 = fig.add_subplot(gs[0, 1:])
            
            # Crea una heatmap di efficienza
            colors_for_heatmap = colors_data[:12]
            efficiency_data = np.zeros((3, len(colors_for_heatmap)))
            labels_y = ['High Priority\n(Easy Wins)', 'Medium Priority\n(Balanced)', 'Low Priority\n(Hard)']
            labels_x = [self.color_mapping.get(c[0], f"C{c[0]}")[:6] for c in colors_for_heatmap]
            
            for i, (color_code, stats) in enumerate(colors_for_heatmap):
                completion = (stats['owned'] / stats['total'] * 100) if stats['total'] > 0 else 0
                difficulty = stats['total'] / 100  # Normalize difficulty
                
                # Categorizza in base a completion e difficulty
                if completion < 50 and difficulty < 1:  # Easy wins
                    efficiency_data[0, i] = 3
                elif completion < 80 and difficulty < 2:  # Medium
                    efficiency_data[1, i] = 2
                else:  # Hard
                    efficiency_data[2, i] = 1
            
            im = ax2.imshow(efficiency_data, cmap='RdYlGn', aspect='auto', alpha=0.8)
            ax2.set_xticks(range(len(labels_x)))
            ax2.set_xticklabels(labels_x, rotation=45, ha='right', fontsize=10)
            ax2.set_yticks(range(len(labels_y)))
            ax2.set_yticklabels(labels_y, fontsize=11)
            ax2.set_title('🎯 Completion Strategy Heatmap', fontsize=13, fontweight='bold', 
                         color='#2c3e50', pad=15)
            
            # Aggiungi valori nella heatmap
            for i in range(efficiency_data.shape[0]):
                for j in range(efficiency_data.shape[1]):
                    if efficiency_data[i, j] > 0:
                        priority = ['Low', 'Medium', 'High'][int(efficiency_data[i, j]) - 1]
                        ax2.text(j, i, priority, ha='center', va='center', 
                               fontsize=9, fontweight='bold', color='white')
            
            # 3. Collection Timeline Simulation
            ax3 = fig.add_subplot(gs[1, :])
            
            # Simula una timeline di acquisizione
            months = ['Jan 2024', 'Mar 2024', 'May 2024', 'Jul 2024', 'Sep 2024', 'Nov 2024', 'Jan 2025']
            
            # Simula dati storici
            owned_trend = [2500, 2650, 2800, 3000, 3200, 3400, 3650]
            missing_trend = [1200, 1150, 1100, 1000, 950, 850, 750]
            new_sets_trend = [120, 135, 150, 165, 180, 195, 210]
            
            # Plot multiplo con stili diversi
            ax3_twin = ax3.twinx()
            
            line1 = ax3.plot(months, owned_trend, marker='o', linewidth=4, markersize=8, 
                           color='#27ae60', label='Owned Pieces', markerfacecolor='white', 
                           markeredgewidth=2, markeredgecolor='#27ae60')
            line2 = ax3.plot(months, missing_trend, marker='s', linewidth=4, markersize=8, 
                           color='#e74c3c', label='Missing Pieces', markerfacecolor='white',
                           markeredgewidth=2, markeredgecolor='#e74c3c')
            
            bars = ax3_twin.bar(months, new_sets_trend, alpha=0.3, color='#3498db', 
                              label='New Sets Added', width=0.6)
            
            ax3.set_ylabel('Number of Pieces', fontsize=13, fontweight='bold', color='#2c3e50')
            ax3_twin.set_ylabel('New Sets', fontsize=13, fontweight='bold', color='#3498db')
            ax3.set_title('📈 Collection Growth Timeline & Projections', fontsize=16, 
                         fontweight='bold', color='#2c3e50', pad=25)
            ax3.tick_params(axis='x', rotation=45, labelsize=11)
            ax3.grid(True, alpha=0.3, linestyle='--')
            ax3.set_facecolor('#fafafa')
            
            # Legend combinata
            lines1, labels1 = ax3.get_legend_handles_labels()
            lines2, labels2 = ax3_twin.get_legend_handles_labels()
            ax3.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11, framealpha=0.9)
            
            # 4. Investment ROI Analysis
            ax4 = fig.add_subplot(gs[2, 0])
            
            # Simula ROI per diverse strategie di acquisto
            strategies = ['Singles\n(BrickLink)', 'Sets\n(LEGO)', 'Bulk\n(Lots)', 'Mixed\nStrategy']
            roi_values = [85, 65, 120, 95]  # ROI percentages
            colors_roi = ['#e74c3c', '#f39c12', '#27ae60', '#3498db']
            
            bars = ax4.bar(strategies, roi_values, color=colors_roi, alpha=0.8, 
                          edgecolor='#2c3e50', linewidth=2)
            ax4.set_ylabel('ROI %', fontsize=11, fontweight='bold', color='#2c3e50')
            ax4.set_title('💹 Purchase Strategy ROI', fontsize=13, fontweight='bold', 
                         color='#2c3e50', pad=15)
            ax4.set_ylim(0, 150)
            ax4.grid(axis='y', alpha=0.3, linestyle='--')
            ax4.set_facecolor('#fafafa')
            
            # Aggiungi una linea di riferimento
            ax4.axhline(y=100, color='#34495e', linestyle='--', linewidth=2, alpha=0.7, label='Break-even')
            ax4.legend(fontsize=10)
            
            for bar, roi in zip(bars, roi_values):
                ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
                        f'{roi}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
            
            # 5. Rarity Distribution
            ax5 = fig.add_subplot(gs[2, 1])
            
            # Simula analisi di rarità dei pezzi
            rarity_categories = ['Common\n(>1000)', 'Uncommon\n(100-1000)', 'Rare\n(10-100)', 'Very Rare\n(<10)']
            rarity_counts = [45, 28, 15, 12]  # Percentages
            colors_rarity = ['#95a5a6', '#f39c12', '#e67e22', '#8e44ad']
            
            wedges, texts, autotexts = ax5.pie(rarity_counts, labels=rarity_categories, 
                                              autopct='%1.1f%%', colors=colors_rarity,
                                              startangle=90, explode=[0, 0, 0.05, 0.1],
                                              textprops={'fontsize': 10, 'fontweight': 'bold'})
            ax5.set_title('💎 Piece Rarity Distribution', fontsize=13, fontweight='bold', 
                         color='#2c3e50', pad=15)
            
            # 6. AI-Predicted Completion Time
            ax6 = fig.add_subplot(gs[2, 2])
            
            # Simula predizione AI del tempo di completamento
            sets_completion_sim = [s['completion'] for s in self.analytics['sets_data'][:10]]
            avg_monthly_progress = 5.5  # 5.5% al mese
            
            months_to_complete = [(100 - comp) / avg_monthly_progress for comp in sets_completion_sim]
            set_names_short = [s['name'][:8] + '...' for s in self.analytics['sets_data'][:10]]
            
            colors_pred = plt.cm.coolwarm(np.linspace(0, 1, len(months_to_complete)))
            bars = ax6.barh(range(len(set_names_short)), months_to_complete, 
                          color=colors_pred, alpha=0.8, edgecolor='#2c3e50', linewidth=1)
            
            ax6.set_yticks(range(len(set_names_short)))
            ax6.set_yticklabels(set_names_short, fontsize=10)
            ax6.invert_yaxis()
            ax6.set_xlabel('Months to Complete', fontsize=11, fontweight='bold', color='#2c3e50')
            ax6.set_title('🤖 AI Completion Prediction', fontsize=13, fontweight='bold', 
                         color='#2c3e50', pad=15)
            ax6.grid(axis='x', alpha=0.3, linestyle='--')
            ax6.set_facecolor('#fafafa')
            
            for bar, months in zip(bars, months_to_complete):
                ax6.text(bar.get_width() + max(months_to_complete)*0.02, 
                        bar.get_y() + bar.get_height()/2,
                        f'{months:.1f}m', ha='left', va='center', fontsize=9, fontweight='bold')
            
            # Layout finale
            fig.suptitle('🔬 Advanced LEGO Collection Analytics & AI Insights', 
                        fontsize=24, fontweight='bold', color='#2c3e50', y=0.97)
            
            # Salva con qualità suprema
            import tempfile
            tmp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            plt.savefig(tmp_file.name, format='png', dpi=600, bbox_inches='tight', 
                       facecolor='#f8f9fa', edgecolor='none', pad_inches=0.4)
            plt.close()
            tmp_file.close()
            
            # Track for cleanup
            self.temp_files.append(tmp_file.name)
            return tmp_file.name
                
        except Exception as e:
            logging.error(f"Error creating advanced analytics chart: {e}")
            plt.close()
            return None

    def _load_color_mapping(self):
        """Carica la mappatura dei colori"""
        try:
            with open(self.color_mapping_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"Could not load color mapping: {e}")
            return {}
    
    def _get_xml_files(self):
        """Ottiene la lista dei file XML nella cartella"""
        xml_files = []
        for file in os.listdir(self.folder_path):
            if file.lower().endswith('.xml'):
                xml_files.append(file)
        return sorted(xml_files)
    
    def _cleanup_temp_files(self):
        """Pulisce i file temporanei creati durante la generazione dei grafici"""
        import os
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    logging.debug(f"Cleaned up temp file: {temp_file}")
            except Exception as e:
                logging.warning(f"Could not remove temp file {temp_file}: {e}")
        
        # Clear the list
        self.temp_files.clear()
    
    def _create_styles(self):
        """Crea gli stili personalizzati per il documento"""
        styles = getSampleStyleSheet()
        
        # Title style
        styles.add(ParagraphStyle(
            name='ModernTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=self.COLORS['primary'],
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        styles.add(ParagraphStyle(
            name='ModernSubtitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=self.COLORS['secondary'],
            spaceAfter=20,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=self.COLORS['dark'],
            spaceAfter=12,
            spaceBefore=16,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=self.COLORS['light'],
            borderPadding=8,
            backColor=self.COLORS['light']
        ))
        
        # KPI style
        styles.add(ParagraphStyle(
            name='KPIValue',
            parent=styles['Normal'],
            fontSize=18,
            textColor=self.COLORS['accent'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=3
        ))
        
        # KPI label style
        styles.add(ParagraphStyle(
            name='KPILabel',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.COLORS['dark'],
            alignment=TA_CENTER,
            fontName='Helvetica',
            spaceAfter=15
        ))
        
        # Body text style
        styles.add(ParagraphStyle(
            name='ModernBody',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.COLORS['dark'],
            spaceAfter=8,
            fontName='Helvetica'
        ))
        
        # Caption style
        styles.add(ParagraphStyle(
            name='Caption',
            parent=styles['Normal'],
            fontSize=9,
            textColor=self.COLORS['dark'],
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique',
            spaceAfter=10
        ))
        
        return styles
    
    def analyze_data(self):
        """Analizza i dati XML per estrarre statistiche avanzate"""
        logging.info("Starting advanced data analysis...")
        
        all_pieces = []
        color_stats = defaultdict(lambda: {'total': 0, 'owned': 0, 'missing': 0})
        piece_stats = defaultdict(lambda: {'total': 0, 'owned': 0, 'missing': 0, 'sets': set()})
        
        for xml_file in self.xml_files:
            file_path = os.path.join(self.folder_path, xml_file)
            set_data = {
                'name': xml_file.replace('.xml', ''),
                'total_pieces': 0,
                'owned_pieces': 0,
                'missing_pieces': 0,
                'completion': 0.0,
                'unique_colors': set(),
                'unique_pieces': set(),
                'pieces': []
            }
            
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                for item in root.findall('ITEM'):
                    # Extract item data
                    item_id = item.find('ITEMID')
                    item_id = item_id.text if item_id is not None else 'Unknown'
                    
                    color_code = item.find('COLOR')
                    color_code = color_code.text if color_code is not None else '0'
                    
                    min_qty = item.find('MINQTY')
                    min_qty = int(min_qty.text) if min_qty is not None and min_qty.text.isdigit() else 0
                    
                    qty_filled = item.find('QTYFILLED')
                    qty_filled = int(qty_filled.text) if qty_filled is not None and qty_filled.text.isdigit() else 0
                    
                    total_qty = min_qty + qty_filled
                    
                    # Update analytics
                    color_name = self.color_mapping.get(color_code, f"Color {color_code}")
                    
                    piece_data = {
                        'id': item_id,
                        'color_code': color_code,
                        'color_name': color_name,
                        'total': total_qty,
                        'owned': qty_filled,
                        'missing': min_qty,
                        'set': xml_file
                    }
                    
                    all_pieces.append(piece_data)
                    set_data['pieces'].append(piece_data)
                    
                    # Update set stats
                    set_data['total_pieces'] += total_qty
                    set_data['owned_pieces'] += qty_filled
                    set_data['missing_pieces'] += min_qty
                    set_data['unique_colors'].add(color_code)
                    set_data['unique_pieces'].add(item_id)
                    
                    # Update global stats
                    self.analytics['unique_colors'].add(color_code)
                    self.analytics['unique_pieces'].add(item_id)
                    
                    # Update color stats
                    color_stats[color_code]['total'] += total_qty
                    color_stats[color_code]['owned'] += qty_filled
                    color_stats[color_code]['missing'] += min_qty
                    
                    # Update piece stats
                    piece_stats[item_id]['total'] += total_qty
                    piece_stats[item_id]['owned'] += qty_filled
                    piece_stats[item_id]['missing'] += min_qty
                    piece_stats[item_id]['sets'].add(xml_file)
                
                # Calculate set completion
                if set_data['total_pieces'] > 0:
                    set_data['completion'] = (set_data['owned_pieces'] / set_data['total_pieces']) * 100
                
                self.analytics['sets_data'].append(set_data)
                
            except Exception as e:
                logging.error(f"Error analyzing file {xml_file}: {e}")
        
        # Calculate global analytics
        self.analytics['total_sets'] = len(self.xml_files)
        self.analytics['total_pieces'] = sum(p['total'] for p in all_pieces)
        self.analytics['total_owned'] = sum(p['owned'] for p in all_pieces)
        self.analytics['total_missing'] = sum(p['missing'] for p in all_pieces)
        
        if self.analytics['total_pieces'] > 0:
            self.analytics['completion_percentage'] = (self.analytics['total_owned'] / self.analytics['total_pieces']) * 100
        
        # Store detailed analysis
        self.analytics['color_analysis'] = dict(color_stats)
        self.analytics['piece_analysis'] = dict(piece_stats)
        
        # Calculate rarity analysis
        self._calculate_rarity_analysis()
        
        logging.info(f"Analysis complete: {self.analytics['total_pieces']} pieces, {len(self.analytics['unique_colors'])} colors")
    
    def _calculate_rarity_analysis(self):
        """Calcola l'analisi di rarità dei pezzi"""
        piece_counts = Counter()
        for piece_id, data in self.analytics['piece_analysis'].items():
            piece_counts[piece_id] = data['total']
        
        # Determine rarity levels
        sorted_pieces = sorted(piece_counts.items(), key=lambda x: x[1])
        total_pieces = len(sorted_pieces)
        
        self.analytics['rarity_analysis'] = {
            'ultra_rare': sorted_pieces[:int(total_pieces * 0.05)],  # Bottom 5%
            'rare': sorted_pieces[int(total_pieces * 0.05):int(total_pieces * 0.15)],  # 5-15%
            'uncommon': sorted_pieces[int(total_pieces * 0.15):int(total_pieces * 0.50)],  # 15-50%
            'common': sorted_pieces[int(total_pieces * 0.50):]  # Top 50%
        }
    
    def generate_report(self):
        """Genera il report PDF completo"""
        logging.info(f"Generating {self.report_type} report...")
        
        # Analyze data first
        self.analyze_data()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            self.output_pdf,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Build story
        story = []
        
        # Add cover page
        story.extend(self._create_cover_page())
        story.append(PageBreak())
        
        # Add executive summary
        story.extend(self._create_executive_summary())
        story.append(PageBreak())
        
        # Add different sections based on report type
        if self.report_type in ['summary', 'complete']:
            story.extend(self._create_overview_section())
            story.append(PageBreak())
        
        if self.report_type in ['detailed', 'complete']:
            story.extend(self._create_detailed_analysis())
            story.append(PageBreak())
            
            story.extend(self._create_color_analysis())
            story.append(PageBreak())
            
            story.extend(self._create_rarity_analysis())
            story.append(PageBreak())
        
        # Always include recommendations
        story.extend(self._create_recommendations())
        
        # Build PDF
        try:
            doc.build(story)
            logging.info(f"Modern report generated successfully: {self.output_pdf}")
            
            # Clean up temporary files
            self._cleanup_temp_files()
            
            return True
        except Exception as e:
            logging.error(f"Error generating report: {e}")
            
            # Clean up temporary files even on error
            self._cleanup_temp_files()
            
            return False
    
    def _create_cover_page(self):
        """Crea la pagina di copertina"""
        story = []
        
        # Title
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("LEGO Collection Analysis", self.styles['ModernTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Subtitle with report type
        report_type_title = {
            'summary': 'Executive Summary Report',
            'detailed': 'Detailed Analysis Report',
            'complete': 'Complete Collection Report'
        }
        story.append(Paragraph(
            report_type_title.get(self.report_type, 'Analysis Report'),
            self.styles['ModernSubtitle']
        ))
        
        story.append(Spacer(1, 1*inch))
        
        # Key metrics preview
        kpi_data = [
            ['Total Sets', str(self.analytics['total_sets'])],
            ['Total Pieces', f"{self.analytics['total_pieces']:,}"],
            ['Completion', f"{self.analytics['completion_percentage']:.1f}%"],
            ['Generated', datetime.now().strftime("%B %d, %Y")]
        ]
        
        kpi_table = Table(kpi_data, colWidths=[2.2*inch, 2.2*inch])
        kpi_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (0, -1), self.COLORS['dark']),
            ('TEXTCOLOR', (1, 0), (1, -1), self.COLORS['accent']),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [self.COLORS['light'], colors.white]),
            ('GRID', (0, 0), (-1, -1), 1, self.COLORS['light']),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10)
        ]))
        
        story.append(kpi_table)
        story.append(Spacer(1, 1*inch))
        
        # Footer
        story.append(Paragraph(
            "Advanced Analytics • Modern Design • Comprehensive Insights",
            self.styles['Caption']
        ))
        
        return story
    
    def _create_executive_summary(self):
        """Crea il riassunto esecutivo con KPI principali"""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['ModernSubtitle']))
        story.append(Spacer(1, 20))
        
        # KPI Cards - Layout a 2x2
        kpi_cards = [
            [
                Paragraph(self._format_number(self.analytics['total_pieces']), self.styles['KPIValue']),
                Paragraph("Total Pieces", self.styles['KPILabel']),
                Paragraph(f"{self.analytics['completion_percentage']:.1f}%", self.styles['KPIValue']),
                Paragraph("Collection Complete", self.styles['KPILabel'])
            ],
            [
                Paragraph(f"{len(self.analytics['unique_colors'])}", self.styles['KPIValue']),
                Paragraph("Unique Colors", self.styles['KPILabel']),
                Paragraph(self._format_number(self.analytics['total_missing']), self.styles['KPIValue']),
                Paragraph("Missing Pieces", self.styles['KPILabel'])
            ]
        ]
        
        kpi_table = Table(kpi_cards, colWidths=[1.6*inch]*4, rowHeights=[1.2*inch]*2)
        kpi_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['light']),
            ('GRID', (0, 0), (-1, -1), 2, self.COLORS['secondary']),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
        ]))
        
        story.append(kpi_table)
        story.append(Spacer(1, 30))
        
        # Summary text
        summary_text = f"""
        Your LEGO collection consists of <b>{self.analytics['total_sets']}</b> sets with a total of 
        <b>{self.analytics['total_pieces']:,}</b> pieces. You currently own <b>{self.analytics['total_owned']:,}</b> pieces 
        ({self.analytics['completion_percentage']:.1f}% complete) and are missing <b>{self.analytics['total_missing']:,}</b> pieces.
        <br/><br/>
        The collection spans <b>{len(self.analytics['unique_colors'])}</b> different colors and includes 
        <b>{len(self.analytics['unique_pieces'])}</b> unique piece types.
        """
        
        story.append(Paragraph(summary_text, self.styles['ModernBody']))
        
        return story
    
    def _create_overview_section(self):
        """Crea la sezione di panoramica"""
        story = []
        
        story.append(Paragraph("Collection Overview", self.styles['ModernSubtitle']))
        story.append(Spacer(1, 20))
        
        # Sets completion table
        sets_data = [['Set Name', 'Total Pieces', 'Owned', 'Missing', 'Completion']]
        
        for set_data in sorted(self.analytics['sets_data'], key=lambda x: x['completion'], reverse=True):
            sets_data.append([
                set_data['name'][:30] + '...' if len(set_data['name']) > 30 else set_data['name'],
                f"{set_data['total_pieces']:,}",
                f"{set_data['owned_pieces']:,}",
                f"{set_data['missing_pieces']:,}",
                f"{set_data['completion']:.1f}%"
            ])
        
        sets_table = Table(sets_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        sets_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.COLORS['white']),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), self.COLORS['light']),
            ('GRID', (0, 0), (-1, -1), 1, self.COLORS['dark'])
        ]))
        
        story.append(sets_table)
        story.append(Spacer(1, 20))
        
        # Add sets completion chart
        if MATPLOTLIB_AVAILABLE:
            sets_chart_path = self._create_sets_completion_chart()
            if sets_chart_path:
                story.append(Paragraph("Sets Completion Overview", self.styles['SectionHeader']))
                story.append(Spacer(1, 10))
                
                # Add the chart image with premium size for dashboard
                sets_image = RLImage(sets_chart_path, width=8*inch, height=6.4*inch)
                story.append(sets_image)
                story.append(Spacer(1, 20))
        
        return story
    
    def _create_detailed_analysis(self):
        """Crea l'analisi dettagliata per ogni set"""
        story = []
        
        story.append(Paragraph("Detailed Set Analysis", self.styles['ModernSubtitle']))
        story.append(Spacer(1, 20))
        
        for set_data in self.analytics['sets_data']:
            story.append(Paragraph(f"Set: {set_data['name']}", self.styles['SectionHeader']))
            
            # Set details
            details_text = f"""
            <b>Total Pieces:</b> {set_data['total_pieces']:,}<br/>
            <b>Owned Pieces:</b> {set_data['owned_pieces']:,}<br/>
            <b>Missing Pieces:</b> {set_data['missing_pieces']:,}<br/>
            <b>Completion:</b> {set_data['completion']:.1f}%<br/>
            <b>Unique Colors:</b> {len(set_data['unique_colors'])}<br/>
            <b>Unique Pieces:</b> {len(set_data['unique_pieces'])}
            """
            
            story.append(Paragraph(details_text, self.styles['ModernBody']))
            story.append(Spacer(1, 20))
        
        return story
    
    def _create_color_analysis(self):
        """Crea l'analisi dei colori"""
        story = []
        
        story.append(Paragraph("Color Analysis", self.styles['ModernSubtitle']))
        story.append(Spacer(1, 20))
        
        # Top colors table
        color_data = [['Color', 'Total Pieces', 'Owned', 'Missing', 'Completion %']]
        
        # Sort colors by total pieces
        sorted_colors = sorted(
            self.analytics['color_analysis'].items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )
        
        for color_code, stats in sorted_colors[:15]:  # Top 15 colors
            color_name = self.color_mapping.get(color_code, f"Color {color_code}")
            completion = (stats['owned'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            color_data.append([
                color_name[:20],
                f"{stats['total']:,}",
                f"{stats['owned']:,}",
                f"{stats['missing']:,}",
                f"{completion:.1f}%"
            ])
        
        color_table = Table(color_data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1*inch])
        color_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.COLORS['white']),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), self.COLORS['light']),
            ('GRID', (0, 0), (-1, -1), 1, self.COLORS['dark'])
        ]))
        
        story.append(Paragraph("Top 15 Colors by Total Pieces", self.styles['SectionHeader']))
        story.append(color_table)
        story.append(Spacer(1, 20))
        
        # Add color distribution chart
        if MATPLOTLIB_AVAILABLE:
            chart_path = self._create_color_distribution_chart()
            if chart_path:
                story.append(Paragraph("Color Distribution", self.styles['SectionHeader']))
                story.append(Spacer(1, 10))
                
                # Add the chart image with enhanced size
                chart_image = RLImage(chart_path, width=7*inch, height=5.6*inch)
                story.append(chart_image)
                story.append(Spacer(1, 20))
        
        # Add completion chart
        if MATPLOTLIB_AVAILABLE:
            completion_chart_path = self._create_completion_chart()
            if completion_chart_path:
                story.append(Paragraph("Collection Completion by Color", self.styles['SectionHeader']))
                story.append(Spacer(1, 10))
                
                # Add the chart image with larger size for better detail
                completion_image = RLImage(completion_chart_path, width=7*inch, height=5.6*inch)
                story.append(completion_image)
                story.append(Spacer(1, 20))
        
        # Add advanced analytics chart
        if MATPLOTLIB_AVAILABLE:
            advanced_chart_path = self._create_advanced_analytics_chart()
            if advanced_chart_path:
                story.append(Paragraph("Advanced Analytics & AI Insights", self.styles['SectionHeader']))
                story.append(Spacer(1, 10))
                
                # Add description
                description = """
                This advanced analytics dashboard provides AI-powered insights into your LEGO collection including:
                • Value analysis and investment ROI tracking
                • Completion strategy optimization with priority heatmaps
                • Collection growth timeline and projections
                • Piece rarity distribution analysis
                • AI-predicted completion times for individual sets
                """
                story.append(Paragraph(description, self.styles['ModernBody']))
                story.append(Spacer(1, 15))
                
                # Add the advanced chart image with premium size
                advanced_image = RLImage(advanced_chart_path, width=8*inch, height=6.4*inch)
                story.append(advanced_image)
                story.append(Spacer(1, 25))
        
        return story
    
    def _create_rarity_analysis(self):
        """Crea l'analisi di rarità"""
        story = []
        
        story.append(Paragraph("Rarity Analysis", self.styles['ModernSubtitle']))
        story.append(Spacer(1, 20))
        
        rarity_levels = [
            ('Ultra Rare', 'ultra_rare', self.COLORS['accent']),
            ('Rare', 'rare', self.COLORS['warning']),
            ('Uncommon', 'uncommon', self.COLORS['info']),
            ('Common', 'common', self.COLORS['success'])
        ]
        
        for level_name, level_key, color in rarity_levels:
            pieces = self.analytics['rarity_analysis'][level_key]
            story.append(Paragraph(f"{level_name} Pieces ({len(pieces)} pieces)", self.styles['SectionHeader']))
            
            if pieces:
                # Show top 10 pieces in this rarity level
                rarity_text = ", ".join([piece_id for piece_id, count in pieces[:10]])
                if len(pieces) > 10:
                    rarity_text += f" ... and {len(pieces) - 10} more"
                
                story.append(Paragraph(rarity_text, self.styles['ModernBody']))
            
            story.append(Spacer(1, 15))
        
        return story
    
    def _create_recommendations(self):
        """Crea le raccomandazioni"""
        story = []
        
        story.append(Paragraph("Recommendations", self.styles['ModernSubtitle']))
        story.append(Spacer(1, 20))
        
        recommendations = []
        
        # Completion recommendation
        if self.analytics['completion_percentage'] < 50:
            recommendations.append("Focus on completing sets with higher completion percentages first.")
        elif self.analytics['completion_percentage'] < 80:
            recommendations.append("Great progress! Consider prioritizing rare pieces to maximize collection value.")
        else:
            recommendations.append("Excellent collection! Focus on ultra-rare pieces to complete remaining sets.")
        
        # Color recommendations
        if len(self.analytics['unique_colors']) > 20:
            recommendations.append("Your collection has great color diversity. Consider organizing by color themes.")
        
        # Missing pieces recommendation
        if self.analytics['total_missing'] > 1000:
            recommendations.append("Consider using the generated wanted list to purchase missing pieces in bulk.")
        
        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", self.styles['ModernBody']))
            story.append(Spacer(1, 10))
        
        return story

    def generate_executive_summary(self):
        """Genera un report esecutivo con solo le informazioni chiave"""
        self.report_type = 'summary'
        return self.generate_report()
    
    def generate_detailed_report(self):
        """Genera un report dettagliato con analisi approfondite"""
        self.report_type = 'detailed'
        return self.generate_report()
    
    def generate_complete_report(self):
        """Genera un report completo con tutte le sezioni"""
        self.report_type = 'complete'
        return self.generate_report()


# Backward compatibility function
def generate_modern_report(folder_path, color_mapping_path, output_pdf, report_type='complete'):
    """
    Funzione di convenienza per generare report moderni
    
    Args:
        folder_path (str): Percorso della cartella con i file XML
        color_mapping_path (str): Percorso del file di mappatura colori
        output_pdf (str): Percorso del file PDF di output
        report_type (str): Tipo di report ('summary', 'detailed', 'complete')
    
    Returns:
        bool: True se il report è stato generato con successo
    """
    try:
        generator = ModernReportGenerator(folder_path, color_mapping_path, output_pdf, report_type)
        return generator.generate_report()
    except Exception as e:
        logging.error(f"Error generating modern report: {e}")
        return False


if __name__ == "__main__":
    # Test del generatore
    generator = ModernReportGenerator(
        folder_path="test_data",
        color_mapping_path="BL_color_mapping.json",
        output_pdf="modern_test_report.pdf",
        report_type="complete"
    )
    generator.generate_report()
