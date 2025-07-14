"""
===============================================================================
LEGO Status Build Analysis - Report e Gestione Inventari XML
===============================================================================

Questo script consente di:
- Generare report PDF dettagliati sull'avanzamento della collezione LEGO, analizzando i file inventario XML esportati da BrickLink.
- Combinare e filtrare più file XML in un unico file per la gestione degli ordini di parti mancanti.

Funzionalità principali:
------------------------
1. Analisi e report PDF:
   - Estrae quantità minime, quantità possedute e totali per ogni colore e set.
   - Genera grafici a barre e a torta per ogni set e per la collezione complessiva.
   - Evidenzia eventuali codici colore mancanti nella mappatura.
   - Salva il report in un unico file PDF multi-pagina.

2. Combinazione e filtro XML:
   - Esclude file XML specificati dall’analisi.
   - Filtra solo gli elementi con quantità minima > 0.
   - Combina gli elementi uguali (stesso tipo e colore) sommando le quantità.
   - Crea file XML filtrati per ogni inventario e un file XML combinato per l’ordine.

Struttura del codice:
---------------------
- Classe `LegoColorReport`: gestisce la generazione del report PDF.
- Classe `LegoXmlCombiner`: gestisce la combinazione e il filtro dei file XML.
- Sezione `if __name__ == "__main__"`: configura e avvia i processi di report e combinazione.

Dipendenze:
-----------
- Python 3.x
- matplotlib
- xml.etree.ElementTree
- collections
- json
- os

Utilizzo:
---------
1. Aggiorna i percorsi delle cartelle e dei file secondo la tua struttura locale.
2. Assicurati che il file di mappatura colori JSON sia presente e aggiornato.
3. Esegui lo script per generare i report PDF e i file XML combinati/filtrati.

Output:
-------
- Report PDF con grafici e riepiloghi per ogni set e per la collezione.
- File XML filtrati e combinati pronti per l’importazione su BrickLink.

===============================================================================
"""

import os
import json
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from collections import defaultdict
from matplotlib.backends.backend_pdf import PdfPages

class LegoColorReport:
    def __init__(self, folder_path, color_mapping_path, output_pdf):
        self.folder_path = folder_path
        self.color_mapping_path = color_mapping_path
        self.output_pdf = output_pdf
        self.color_mapping = self.load_color_mapping()
        self.xml_files = [f for f in os.listdir(self.folder_path) if f.endswith('.xml')]
        self.all_warnings = []
        self.overall_status = []
        self.parts_count = []
        self.parts_count_owned = []
        self.total_min_qty = 0
        self.total_qty_filled = 0
        self.overall_color_distribution = defaultdict(int)
        self.overall_color_filled_distribution = defaultdict(int)

    def load_color_mapping(self):
        with open(self.color_mapping_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def process(self):
        print("XML files found:", self.xml_files)
        with PdfPages(self.output_pdf) as pdf:
            for xml_file in self.xml_files:
                self.process_single_file(xml_file, pdf)
            self.add_overall_summary(pdf)
            self.add_warnings_page(pdf)
        print(f"Report saved to {self.output_pdf}")

    def process_single_file(self, xml_file, pdf):
        file_path = os.path.join(self.folder_path, xml_file)
        min_qty_data = defaultdict(int)
        qty_filled_data = defaultdict(int)
        total_qty_data = defaultdict(int)
        set_min_qty = 0
        set_qty_filled = 0

        tree = ET.parse(file_path)
        root = tree.getroot()

        for item in root.findall('ITEM'):
            color = self.get_xml_text(item, 'COLOR', default='0', numeric=True)
            min_qty = self.get_xml_int(item, 'MINQTY')
            qty_filled = self.get_xml_int(item, 'QTYFILLED')
            item_id = self.get_xml_text(item, 'ITEMID', default='Unknown ID')

            total_qty = min_qty + qty_filled
            min_qty_data[color] += min_qty
            qty_filled_data[color] += qty_filled
            total_qty_data[color] += total_qty
            self.overall_color_distribution[color] += total_qty
            self.overall_color_filled_distribution[color] += qty_filled
            set_min_qty += min_qty
            set_qty_filled += qty_filled

        set_completion_status = (set_qty_filled / (set_qty_filled + set_min_qty)) * 100 if (set_qty_filled + set_min_qty) > 0 else 0
        self.overall_status.append((xml_file, set_completion_status))
        self.parts_count.append((xml_file, set_qty_filled + set_min_qty))
        self.parts_count_owned.append((xml_file, set_qty_filled))
        self.total_min_qty += set_min_qty
        self.total_qty_filled += set_qty_filled

        self.plot_set_chart(
            xml_file, min_qty_data, qty_filled_data, total_qty_data,
            set_min_qty, set_qty_filled, pdf
        )

    def plot_set_chart(self, xml_file, min_qty_data, qty_filled_data, total_qty_data, set_min_qty, set_qty_filled, pdf):
        colors = list(min_qty_data.keys())
        min_qty_values = [min_qty_data[c] for c in colors]
        qty_filled_values = [qty_filled_data[c] for c in colors]
        total_qty_values = [total_qty_data[c] for c in colors]

        # Sort by total_qty_values descending
        sorted_indices = sorted(range(len(total_qty_values)), key=lambda k: total_qty_values[k], reverse=True)
        colors = [colors[i] for i in sorted_indices]
        min_qty_values = [min_qty_values[i] for i in sorted_indices]
        qty_filled_values = [qty_filled_values[i] for i in sorted_indices]
        total_qty_values = [total_qty_values[i] for i in sorted_indices]

        color_names = []
        for color in colors:
            if color in self.color_mapping:
                color_names.append(self.color_mapping[color])
            else:
                color_names.append(color)
                warning = f"Warning: Color code {color} not found in color mapping. Using color code as label. File: {xml_file}"
                self.all_warnings.append(warning)

        x = range(len(colors))
        plt.figure(figsize=(14, 8))
        bar_width = 0.25
        plt.bar(x, min_qty_values, width=bar_width, label='Min Qty', align='center', color='#0072B2')
        plt.bar([p + bar_width for p in x], qty_filled_values, width=bar_width, label='Qty Filled', align='center', color='#E69F00')
        plt.bar([p + bar_width * 2 for p in x], total_qty_values, width=bar_width, label='Total Qty', align='center', color='#009E73')
        plt.xlabel('Color')
        plt.ylabel('Quantity')
        plt.title(f'LEGO Set Color Quantities - {xml_file}')
        plt.xticks([p + bar_width for p in x], color_names, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()

        # Pie chart inset
        inset_ax = plt.axes([0.65, 0.55, 0.3, 0.3])
        labels = ['Qty Filled', 'Qty Not Filled']
        sizes = [set_qty_filled, set_min_qty]
        pie_colors = ['#ff9999', '#66b3ff']
        explode = (0.1, 0)
        inset_ax.pie(sizes, explode=explode, labels=labels, colors=pie_colors, autopct='%1.1f%%',
                     shadow=True, startangle=140)
        inset_ax.axis('equal')
        inset_ax.set_title('Completion')
        pdf.savefig()
        plt.close()

    def add_overall_summary(self, pdf):
        overall_completion_status = (self.total_qty_filled / (self.total_qty_filled + self.total_min_qty)) * 100 if (self.total_qty_filled + self.total_min_qty) > 0 else 0
        total_bricks = sum(self.overall_color_distribution.values())
        total_bricks_owned = sum(self.overall_color_filled_distribution.values())
        combined_text = "\n".join([
            f"{xml_file}: {status:.2f}% - {count} bricks"
            for (xml_file, status), (_, count) in zip(self.overall_status, self.parts_count)
        ])

        plt.figure(figsize=(8, 14))
        plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        plt.text(0.1, 0.95, f'Overall Collection Completion Status: {overall_completion_status:.2f}%', ha='left', va='top', fontsize=14, wrap=True)
        plt.text(0.1, 0.9, f'Overall number of Bricks: {total_bricks:.0f}', ha='left', va='top', fontsize=14, wrap=True)
        plt.text(0.1, 0.85, f'Overall number of Bricks Owned: {total_bricks_owned:.0f}', ha='left', va='top', fontsize=14, wrap=True)
        plt.text(0.1, 0.8, "Set Completion Status:\n" + combined_text, ha='left', va='top', fontsize=11, wrap=True)
        plt.axis('off')
        pdf.savefig()
        plt.close()

        # Overall color distribution
        overall_colors = list(self.overall_color_distribution.keys())
        overall_color_values = [self.overall_color_distribution[c] for c in overall_colors]
        overall_color_filled_values = [self.overall_color_filled_distribution[c] for c in overall_colors]
        overall_color_names = [self.color_mapping.get(c, c) for c in overall_colors]

        sorted_indices = sorted(range(len(overall_color_values)), key=lambda k: overall_color_values[k], reverse=True)
        overall_colors = [overall_colors[i] for i in sorted_indices]
        overall_color_values = [overall_color_values[i] for i in sorted_indices]
        overall_color_filled_values = [overall_color_filled_values[i] for i in sorted_indices]
        overall_color_names = [overall_color_names[i] for i in sorted_indices]

        plt.figure(figsize=(14, 8))
        bar_width = 0.35
        plt.bar(range(len(overall_colors)), overall_color_values, width=bar_width, label='Total Qty', align='center', color='#009E73')
        plt.bar([p + bar_width for p in range(len(overall_colors))], overall_color_filled_values, width=bar_width, label='Qty Filled', align='center', color='#E69F00')
        plt.xlabel('Color')
        plt.ylabel('Total Quantity')
        plt.title('Overall Color Distribution')
        plt.xticks([p + bar_width / 2 for p in range(len(overall_colors))], overall_color_names, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()

        # Pie chart inset
        inset_ax = plt.axes([0.65, 0.55, 0.3, 0.3])
        labels = ['Qty Filled', 'Qty Not Filled']
        sizes = [self.total_qty_filled, self.total_min_qty]
        pie_colors = ['#ff9999', '#66b3ff']
        explode = (0.1, 0)
        inset_ax.pie(sizes, explode=explode, labels=labels, colors=pie_colors, autopct='%1.1f%%',
                     shadow=True, startangle=140)
        inset_ax.axis('equal')
        inset_ax.set_title('Overall Completion')
        pdf.savefig()
        plt.close()

    def add_warnings_page(self, pdf):
        unique_warnings = list(set(self.all_warnings))
        if unique_warnings:
            plt.figure(figsize=(14, 8))
            plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
            plt.text(0.5, 0.9, "Warnings:", ha='center', va='top', fontsize=14, wrap=True)
            plt.text(0.1, 0.8, "\n".join(unique_warnings), ha='left', va='top', fontsize=10, wrap=True)
            plt.axis('off')
            pdf.savefig()
            plt.close()

    @staticmethod
    def get_xml_text(item, tag, default='', numeric=False):
        el = item.find(tag)
        if el is not None and el.text:
            if numeric:
                return el.text if el.text.isdigit() else default
            return el.text
        return default

    @staticmethod
    def get_xml_int(item, tag):
        el = item.find(tag)
        return int(el.text) if el is not None and el.text and el.text.isdigit() else 0

class LegoXmlCombiner:
    def __init__(self, folder_path, filtered_folder, output_file, excluded_files=None):
        self.folder_path = folder_path
        self.filtered_folder = filtered_folder
        self.output_file = output_file
        self.excluded_files = excluded_files if excluded_files else []
        os.makedirs(self.filtered_folder, exist_ok=True)
        self.xml_files = [f for f in os.listdir(self.folder_path) if f.endswith('.xml') and f not in self.excluded_files]
        self.combined_root = ET.Element("INVENTORY")
        self.item_tracker = {}

    def process(self):
        print("XML files found (excluding specified files):", self.xml_files)
        for xml_file in self.xml_files:
            self.process_single_file(xml_file)
        self.write_combined_xml()

    def process_single_file(self, xml_file):
        file_path = os.path.join(self.folder_path, xml_file)
        tree = ET.parse(file_path)
        root = tree.getroot()
        filtered_root = ET.Element(root.tag)

        for item in root.findall('ITEM'):
            min_qty = self.get_xml_int(item, 'MINQTY')
            item_type = self.get_xml_text(item, 'ITEMID')
            color = self.get_xml_text(item, 'COLOR')

            if min_qty > 0 and item_type and color:
                item_key = (item_type, color)
                # Combined file logic
                if item_key in self.item_tracker:
                    existing_item = self.item_tracker[item_key]
                    existing_min_qty = int(existing_item.find('MINQTY').text)
                    existing_item.find('MINQTY').text = str(existing_min_qty + min_qty)
                else:
                    new_combined_item = self.copy_item(item, xml_file)
                    self.combined_root.append(new_combined_item)
                    self.item_tracker[item_key] = new_combined_item
                # Filtered file logic
                new_filtered_item = self.copy_item(item)
                filtered_root.append(new_filtered_item)

        filtered_file_path = os.path.join(self.filtered_folder, f"filtered_{xml_file}")
        filtered_tree = ET.ElementTree(filtered_root)
        filtered_tree.write(filtered_file_path, encoding='utf-8', xml_declaration=True)

    def write_combined_xml(self):
        combined_tree = ET.ElementTree(self.combined_root)
        combined_tree.write(self.output_file, encoding='utf-8', xml_declaration=True)
        print(f"Combined wanted list XML file created: {self.output_file}")

    @staticmethod
    def copy_item(item, remarks=None):
        new_item = ET.Element('ITEM')
        for sub_element in item:
            new_sub_element = ET.SubElement(new_item, sub_element.tag)
            if sub_element.tag == 'QTYFILLED':
                new_sub_element.text = '0'
            else:
                new_sub_element.text = sub_element.text
        if remarks:
            remarks_element = ET.SubElement(new_item, 'REMARKS')
            remarks_element.text = remarks
        return new_item

    @staticmethod
    def get_xml_text(item, tag):
        el = item.find(tag)
        return el.text if el is not None else None

    @staticmethod
    def get_xml_int(item, tag):
        el = item.find(tag)
        return int(el.text) if el is not None and el.text and el.text.isdigit() else 0

# --- USAGE EXAMPLES ---

if __name__ == "__main__":
    # Definizione dei report da generare
    reports = [
        {
            "folder_path": r'C:\Development\BrickLinkReport',
            "color_mapping_path": 'BL_color_mapping.json',
            "output_pdf": os.path.join(r'C:\Development\BrickLinkReport', 'LEGO_Set_Color_Quantities_Report.pdf')
        },
        {
            "folder_path": r'C:\Development\BrickLinkReport_Other',
            "color_mapping_path": 'BL_color_mapping.json',
            "output_pdf": os.path.join(r'C:\Development\BrickLinkReport_Other', 'LEGO_Set_Color_Quantities_Report_NonLOTR.pdf')
        }
    ]

    # Generazione dei report PDF
    for report_cfg in reports:
        report = LegoColorReport(
            folder_path=report_cfg["folder_path"],
            color_mapping_path=report_cfg["color_mapping_path"],
            output_pdf=report_cfg["output_pdf"]
        )
        report.process()

    # Definizione delle combinazioni XML da generare
    combiners = [
        {
            "folder_path": r'C:\Development\BrickLinkReport',
            "filtered_folder": r'C:\Development\BrickLinkReport\Filtered',
            "output_file": os.path.join(r'C:\Development\BrickLinkReport\Filtered', "wanted_list.xml"),
            "excluded_files": [    
                "79007 - Battle at the Black Gate.xml",
                "10333 - Barad-dur.xml",
                "10237 - Tower of Orthanc.xml"
            ]
        },
        {
            "folder_path": r'C:\Development\BrickLinkReport_Other',
            "filtered_folder": r'C:\Development\BrickLinkReport_Other\Filtered',
            "output_file": os.path.join(r'C:\Development\BrickLinkReport_Other\Filtered', "wanted_list_Other.xml"),
            "excluded_files": []
        }
    ]

    # Generazione dei file XML combinati e filtrati
    for combiner_cfg in combiners:
        combiner = LegoXmlCombiner(
            folder_path=combiner_cfg["folder_path"],
            filtered_folder=combiner_cfg["filtered_folder"],
            output_file=combiner_cfg["output_file"],
            excluded_files=combiner_cfg["excluded_files"]
        )
        combiner.process()