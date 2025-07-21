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
        """Crea un grafico a torta della distribuzione dei colori"""
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        try:
            # Prepara i dati per il grafico
            colors_data = []
            for color_code, stats in self.analytics['color_analysis'].items():
                color_name = self.color_mapping.get(color_code, f"Color {color_code}")
                colors_data.append((color_name[:15], stats['total']))
            
            # Ordina per numero di pezzi e prendi i top 10
            colors_data.sort(key=lambda x: x[1], reverse=True)
            top_colors = colors_data[:10]
            
            if len(colors_data) > 10:
                other_total = sum(x[1] for x in colors_data[10:])
                top_colors.append(('Other', other_total))
            
            # Crea il grafico
            fig, ax = plt.subplots(figsize=(10, 8))
            labels = [x[0] for x in top_colors]
            sizes = [x[1] for x in top_colors]
            
            colors_palette = plt.cm.Set3(range(len(labels)))
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                            startangle=90, colors=colors_palette)
            
            ax.set_title('Color Distribution', fontsize=16, fontweight='bold', pad=20)
            
            # Migliora la leggibilità
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.tight_layout()
            
            # Salva il grafico in un file temporaneo
            import tempfile
            tmp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            plt.savefig(tmp_file.name, format='png', dpi=300, bbox_inches='tight')
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
        """Crea un grafico a barre del completamento per colore"""
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        try:
            # Prepara i dati
            colors_data = []
            for color_code, stats in self.analytics['color_analysis'].items():
                if stats['total'] > 20:  # Solo colori con almeno 20 pezzi
                    color_name = self.color_mapping.get(color_code, f"Color {color_code}")
                    completion = (stats['owned'] / stats['total'] * 100) if stats['total'] > 0 else 0
                    colors_data.append((color_name[:15], completion, stats['total']))
            
            # Ordina per completamento
            colors_data.sort(key=lambda x: x[1], reverse=True)
            top_colors = colors_data[:12]  # Top 12 colori
            
            # Crea il grafico
            fig, ax = plt.subplots(figsize=(12, 8))
            
            names = [x[0] for x in top_colors]
            completions = [x[1] for x in top_colors]
            totals = [x[2] for x in top_colors]
            
            bars = ax.bar(range(len(names)), completions, 
                         color=['#2E8B57' if c >= 80 else '#FF6B35' if c < 50 else '#4ECDC4' for c in completions])
            
            ax.set_xlabel('Colors', fontsize=12, fontweight='bold')
            ax.set_ylabel('Completion Percentage', fontsize=12, fontweight='bold')
            ax.set_title('Collection Completion by Color', fontsize=16, fontweight='bold', pad=20)
            ax.set_xticks(range(len(names)))
            ax.set_xticklabels(names, rotation=45, ha='right')
            ax.set_ylim(0, 100)
            
            # Aggiungi etichette sui bar
            for i, (bar, total) in enumerate(zip(bars, totals)):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height:.1f}%\n({total} pcs)',
                       ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            
            # Salva il grafico
            import tempfile
            tmp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            plt.savefig(tmp_file.name, format='png', dpi=300, bbox_inches='tight')
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
        """Crea un grafico a barre della completazione dei set"""
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        try:
            # Prepara i dati dei set
            sets_data = sorted(self.analytics['sets_data'], key=lambda x: x['completion'], reverse=True)
            top_sets = sets_data[:10]  # Top 10 set
            
            # Crea il grafico
            fig, ax = plt.subplots(figsize=(12, 8))
            
            names = [x['name'][:20] + '...' if len(x['name']) > 20 else x['name'] for x in top_sets]
            completions = [x['completion'] for x in top_sets]
            
            bars = ax.barh(range(len(names)), completions,
                          color=['#2E8B57' if c >= 90 else '#4ECDC4' if c >= 70 else '#FF6B35' for c in completions])
            
            ax.set_ylabel('LEGO Sets', fontsize=12, fontweight='bold')
            ax.set_xlabel('Completion Percentage', fontsize=12, fontweight='bold')
            ax.set_title('Top 10 Sets by Completion', fontsize=16, fontweight='bold', pad=20)
            ax.set_yticks(range(len(names)))
            ax.set_yticklabels(names)
            ax.set_xlim(0, 100)
            
            # Aggiungi etichette sui bar
            for i, (bar, completion) in enumerate(zip(bars, completions)):
                width = bar.get_width()
                ax.text(width + 1, bar.get_y() + bar.get_height()/2.,
                       f'{completion:.1f}%',
                       ha='left', va='center', fontweight='bold')
            
            plt.tight_layout()
            
            # Salva il grafico
            import tempfile
            tmp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            plt.savefig(tmp_file.name, format='png', dpi=300, bbox_inches='tight')
            plt.close()
            tmp_file.close()
            
            # Track for cleanup
            self.temp_files.append(tmp_file.name)
            return tmp_file.name
                
        except Exception as e:
            logging.error(f"Error creating sets completion chart: {e}")
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
                
                # Add the chart image
                sets_image = RLImage(sets_chart_path, width=6*inch, height=4.8*inch)
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
                
                # Add the chart image
                chart_image = RLImage(chart_path, width=6*inch, height=4.8*inch)
                story.append(chart_image)
                story.append(Spacer(1, 20))
        
        # Add completion chart
        if MATPLOTLIB_AVAILABLE:
            completion_chart_path = self._create_completion_chart()
            if completion_chart_path:
                story.append(Paragraph("Collection Completion by Color", self.styles['SectionHeader']))
                story.append(Spacer(1, 10))
                
                # Add the chart image
                completion_image = RLImage(completion_chart_path, width=6*inch, height=4.8*inch)
                story.append(completion_image)
                story.append(Spacer(1, 20))
        
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
