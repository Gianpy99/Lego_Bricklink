"""
Input Format Handlers for LEGO Analysis System
Supports XML, CSV, and JSON input formats from various LEGO platforms
"""

import pandas as pd
import json
import xml.etree.ElementTree as ET
import csv
from pathlib import Path
import logging
from abc import ABC, abstractmethod

class InputFormatHandler(ABC):
    """Abstract base class for input format handlers"""
    
    @abstractmethod
    def can_handle(self, file_path: str) -> bool:
        """Check if this handler can process the given file"""
        pass
    
    @abstractmethod
    def parse_file(self, file_path: str) -> list:
        """Parse file and return list of LEGO items"""
        pass
    
    @abstractmethod
    def get_format_name(self) -> str:
        """Return the name of this format"""
        pass

class XMLHandler(InputFormatHandler):
    """Handler for BrickLink XML format"""
    
    def can_handle(self, file_path: str) -> bool:
        return file_path.lower().endswith('.xml')
    
    def parse_file(self, file_path: str) -> list:
        """Parse BrickLink XML file"""
        items = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for item in root.findall('ITEM'):
                parsed_item = {
                    'item_id': self._get_text(item, 'ITEMID', ''),
                    'item_type': self._get_text(item, 'ITEMTYPE', 'P'),
                    'color': self._get_text(item, 'COLOR', '0'),
                    'min_qty': self._get_int(item, 'MINQTY', 0),
                    'qty_filled': self._get_int(item, 'QTYFILLED', 0),
                    'category': self._get_text(item, 'CATEGORY', ''),
                    'condition': self._get_text(item, 'CONDITION', 'N'),
                    'remarks': self._get_text(item, 'REMARKS', ''),
                    'source_file': Path(file_path).name
                }
                items.append(parsed_item)
                
        except ET.ParseError as e:
            logging.error(f"Error parsing XML file {file_path}: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error parsing {file_path}: {e}")
            raise
            
        return items
    
    def get_format_name(self) -> str:
        return "BrickLink XML"
    
    def _get_text(self, item, tag, default=''):
        el = item.find(tag)
        return el.text if el is not None and el.text else default
    
    def _get_int(self, item, tag, default=0):
        el = item.find(tag)
        return int(el.text) if el is not None and el.text and el.text.isdigit() else default

class CSVHandler(InputFormatHandler):
    """Handler for CSV format (Rebrickable, BrickOwl, etc.)"""
    
    def can_handle(self, file_path: str) -> bool:
        return file_path.lower().endswith('.csv')
    
    def parse_file(self, file_path: str) -> list:
        """Parse CSV file with flexible column mapping"""
        items = []
        try:
            df = pd.read_csv(file_path)
            
            # Column mapping for different CSV formats
            column_mapping = self._detect_csv_format(df.columns.tolist())
            
            for _, row in df.iterrows():
                # Helper function to safely get row values
                def safe_get(key, default=''):
                    if key and key in row.index:
                        return row[key] if pd.notna(row[key]) else default
                    return default
                
                parsed_item = {
                    'item_id': str(safe_get(column_mapping['item_id'], '')),
                    'item_type': str(safe_get(column_mapping['item_type'], 'P')),
                    'color': str(safe_get(column_mapping['color'], '0')),
                    'min_qty': self._safe_int(safe_get(column_mapping['min_qty'], 0)),
                    'qty_filled': self._safe_int(safe_get(column_mapping['qty_filled'], 0)),
                    'category': str(safe_get(column_mapping['category'], '')),
                    'condition': str(safe_get(column_mapping['condition'], 'N')),
                    'remarks': str(safe_get(column_mapping['remarks'], '')),
                    'source_file': Path(file_path).name
                }
                items.append(parsed_item)
                
        except Exception as e:
            logging.error(f"Error parsing CSV file {file_path}: {e}")
            raise
            
        return items
    
    def get_format_name(self) -> str:
        return "CSV (Rebrickable/BrickOwl)"
    
    def _detect_csv_format(self, columns):
        """Detect CSV format and return column mapping"""
        columns_lower = [col.lower() for col in columns]
        
        # Default mapping
        mapping = {
            'item_id': None,
            'item_type': None,
            'color': None,
            'min_qty': None,
            'qty_filled': None,
            'category': None,
            'condition': None,
            'remarks': None
        }
        
        # Rebrickable format detection
        if 'part_num' in columns_lower:
            mapping.update({
                'item_id': 'part_num',
                'color': 'color_id',
                'min_qty': 'quantity',
                'item_type': 'part_cat_id'
            })
        
        # BrickOwl format detection
        elif 'boid' in columns_lower:
            mapping.update({
                'item_id': 'boid',
                'color': 'color_name',
                'min_qty': 'wanted_qty',
                'qty_filled': 'owned_qty'
            })
        
        # Generic format detection
        else:
            for col in columns:
                col_lower = col.lower()
                if any(term in col_lower for term in ['part', 'item', 'element']):
                    mapping['item_id'] = col
                elif any(term in col_lower for term in ['color', 'colour']):
                    mapping['color'] = col
                elif any(term in col_lower for term in ['quantity', 'qty', 'needed', 'want']):
                    mapping['min_qty'] = col
                elif any(term in col_lower for term in ['owned', 'have', 'filled']):
                    mapping['qty_filled'] = col
                elif any(term in col_lower for term in ['type', 'category']):
                    mapping['item_type'] = col
        
        return mapping

    def _safe_int(self, value):
        """Safely convert value to int"""
        try:
            if pd.isna(value) or value == '' or value is None:
                return 0
            return int(float(str(value)))
        except (ValueError, TypeError):
            return 0

class JSONHandler(InputFormatHandler):
    """Handler for JSON format"""
    
    def can_handle(self, file_path: str) -> bool:
        return file_path.lower().endswith('.json')
    
    def parse_file(self, file_path: str) -> list:
        """Parse JSON file"""
        items = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                # Array of items
                for item_data in data:
                    items.append(self._parse_json_item(item_data, file_path))
            elif isinstance(data, dict):
                if 'items' in data:
                    # Object with items array
                    for item_data in data['items']:
                        items.append(self._parse_json_item(item_data, file_path))
                else:
                    # Single item object
                    items.append(self._parse_json_item(data, file_path))
                    
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON file {file_path}: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error parsing {file_path}: {e}")
            raise
            
        return items
    
    def get_format_name(self) -> str:
        return "JSON"
    
    def _parse_json_item(self, item_data, file_path):
        """Parse individual JSON item"""
        return {
            'item_id': str(item_data.get('item_id', item_data.get('part_num', item_data.get('id', '')))),
            'item_type': str(item_data.get('item_type', item_data.get('type', 'P'))),
            'color': str(item_data.get('color', item_data.get('color_id', '0'))),
            'min_qty': int(item_data.get('min_qty', item_data.get('quantity', item_data.get('needed', 0)))),
            'qty_filled': int(item_data.get('qty_filled', item_data.get('owned', item_data.get('have', 0)))),
            'category': str(item_data.get('category', '')),
            'condition': str(item_data.get('condition', 'N')),
            'remarks': str(item_data.get('remarks', item_data.get('notes', ''))),
            'source_file': Path(file_path).name
        }

class MultiFormatInputParser:
    """Main parser that handles multiple input formats"""
    
    def __init__(self):
        self.handlers = [
            XMLHandler(),
            CSVHandler(),
            JSONHandler()
        ]
    
    def parse_file(self, file_path: str) -> list:
        """Parse file using appropriate handler"""
        for handler in self.handlers:
            if handler.can_handle(file_path):
                logging.info(f"Parsing {file_path} as {handler.get_format_name()}")
                return handler.parse_file(file_path)
        
        raise ValueError(f"Unsupported file format: {file_path}")
    
    def parse_folder(self, folder_path: str, excluded_files: list = None) -> dict:
        """Parse all supported files in a folder"""
        if excluded_files is None:
            excluded_files = []
        
        results = {}
        folder = Path(folder_path)
        
        for file_path in folder.iterdir():
            if file_path.is_file() and file_path.name not in excluded_files:
                try:
                    if any(handler.can_handle(str(file_path)) for handler in self.handlers):
                        items = self.parse_file(str(file_path))
                        results[file_path.name] = {
                            'items': items,
                            'count': len(items),
                            'format': self._get_format_name(str(file_path))
                        }
                        logging.info(f"Parsed {len(items)} items from {file_path.name}")
                except Exception as e:
                    logging.error(f"Error parsing {file_path.name}: {e}")
                    continue
        
        return results
    
    def _get_format_name(self, file_path: str) -> str:
        """Get format name for a file"""
        for handler in self.handlers:
            if handler.can_handle(file_path):
                return handler.get_format_name()
        return "Unknown"
    
    def get_supported_formats(self) -> list:
        """Get list of supported formats"""
        return [handler.get_format_name() for handler in self.handlers]

# Example usage
if __name__ == "__main__":
    parser = MultiFormatInputParser()
    print("Supported formats:", parser.get_supported_formats())
    
    # Example: Parse a folder with mixed file formats
    # results = parser.parse_folder("path/to/mixed/files")
    # for filename, data in results.items():
    #     print(f"{filename}: {data['count']} items ({data['format']})")
