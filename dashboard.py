"""
Interactive Dashboard for LEGO Analysis System
Advanced analytics with Chart.js and real-time filtering
"""

from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import logging

# Import our analysis modules
from LegoStatusBuildAnalysis import LegoColorReport, LegoXmlCombiner
from input_handlers import MultiFormatInputParser
from bricklink_api import BrickLinkAPI, BrickLinkSync, BrickLinkCredentialManager

class DashboardAnalytics:
    """Advanced analytics for dashboard"""
    
    def __init__(self, db_path="analytics.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_count INTEGER,
                total_items INTEGER,
                completion_percentage REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                collection_id INTEGER,
                item_id TEXT,
                item_type TEXT,
                color_id TEXT,
                color_name TEXT,
                min_qty INTEGER,
                qty_filled INTEGER,
                category TEXT,
                price REAL,
                source_file TEXT,
                FOREIGN KEY (collection_id) REFERENCES collections (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS color_stats (
                id INTEGER PRIMARY KEY,
                collection_id INTEGER,
                color_id TEXT,
                color_name TEXT,
                total_pieces INTEGER,
                owned_pieces INTEGER,
                missing_pieces INTEGER,
                completion_rate REAL,
                FOREIGN KEY (collection_id) REFERENCES collections (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY,
                item_key TEXT,
                price REAL,
                currency TEXT,
                date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_collection_analysis(self, collection_name, analysis_data):
        """Save collection analysis to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Calculate stats
            total_items = sum(len(data['items']) for data in analysis_data.values())
            file_count = len(analysis_data)
            
            total_pieces = 0
            owned_pieces = 0
            
            for file_data in analysis_data.values():
                for item in file_data['items']:
                    total_pieces += item['min_qty'] + item['qty_filled']
                    owned_pieces += item['qty_filled']
            
            completion_percentage = (owned_pieces / total_pieces * 100) if total_pieces > 0 else 0
            
            # Insert collection
            cursor.execute("""
                INSERT INTO collections (name, file_count, total_items, completion_percentage)
                VALUES (?, ?, ?, ?)
            """, (collection_name, file_count, total_items, completion_percentage))
            
            collection_id = cursor.lastrowid
            
            # Insert items and calculate color stats
            color_stats = {}
            
            for file_data in analysis_data.values():
                for item in file_data['items']:
                    cursor.execute("""
                        INSERT INTO items (collection_id, item_id, item_type, color_id, 
                                         min_qty, qty_filled, category, source_file)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (collection_id, item['item_id'], item['item_type'], 
                          item['color'], item['min_qty'], item['qty_filled'],
                          item['category'], item['source_file']))
                    
                    # Update color stats
                    color_key = item['color']
                    if color_key not in color_stats:
                        color_stats[color_key] = {
                            'total_pieces': 0,
                            'owned_pieces': 0,
                            'missing_pieces': 0
                        }
                    
                    color_stats[color_key]['total_pieces'] += item['min_qty'] + item['qty_filled']
                    color_stats[color_key]['owned_pieces'] += item['qty_filled']
                    color_stats[color_key]['missing_pieces'] += item['min_qty']
            
            # Insert color stats
            for color_id, stats in color_stats.items():
                completion_rate = (stats['owned_pieces'] / stats['total_pieces'] * 100) if stats['total_pieces'] > 0 else 0
                
                cursor.execute("""
                    INSERT INTO color_stats (collection_id, color_id, total_pieces, 
                                           owned_pieces, missing_pieces, completion_rate)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (collection_id, color_id, stats['total_pieces'], 
                      stats['owned_pieces'], stats['missing_pieces'], completion_rate))
            
            conn.commit()
            logging.info(f"Saved collection analysis: {collection_name}")
            return collection_id
            
        except Exception as e:
            conn.rollback()
            logging.error(f"Error saving collection analysis: {e}")
            raise
        finally:
            conn.close()
    
    def get_collection_dashboard_data(self, collection_id):
        """Get comprehensive dashboard data for a collection"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Collection overview
            cursor.execute("SELECT * FROM collections WHERE id = ?", (collection_id,))
            collection = cursor.fetchone()
            
            if not collection:
                return None
            
            # Color distribution
            cursor.execute("""
                SELECT color_id, total_pieces, owned_pieces, missing_pieces, completion_rate
                FROM color_stats WHERE collection_id = ?
                ORDER BY total_pieces DESC
            """, (collection_id,))
            color_stats = cursor.fetchall()
            
            # Category distribution
            cursor.execute("""
                SELECT category, COUNT(*) as count, SUM(min_qty + qty_filled) as total_pieces
                FROM items WHERE collection_id = ?
                GROUP BY category
                ORDER BY total_pieces DESC
            """, (collection_id,))
            category_stats = cursor.fetchall()
            
            # Top missing items
            cursor.execute("""
                SELECT item_id, color_id, min_qty, source_file
                FROM items WHERE collection_id = ? AND min_qty > 0
                ORDER BY min_qty DESC
                LIMIT 20
            """, (collection_id,))
            missing_items = cursor.fetchall()
            
            # Progress over time (mock data for now)
            progress_data = self._generate_progress_timeline(collection_id)
            
            return {
                'collection': {
                    'id': collection[0],
                    'name': collection[1],
                    'created_at': collection[2],
                    'file_count': collection[3],
                    'total_items': collection[4],
                    'completion_percentage': collection[5]
                },
                'color_stats': color_stats,
                'category_stats': category_stats,
                'missing_items': missing_items,
                'progress_timeline': progress_data
            }
            
        finally:
            conn.close()
    
    def _generate_progress_timeline(self, collection_id):
        """Generate mock progress timeline data"""
        # In a real implementation, this would track actual progress over time
        base_date = datetime.now() - timedelta(days=30)
        timeline = []
        
        for i in range(30):
            date = base_date + timedelta(days=i)
            # Mock progress increase
            progress = min(95, 20 + (i * 2) + (i ** 0.5 * 5))
            timeline.append({
                'date': date.strftime('%Y-%m-%d'),
                'completion_rate': round(progress, 1)
            })
        
        return timeline
    
    def get_collections_summary(self):
        """Get summary of all collections"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, name, created_at, file_count, total_items, completion_percentage
                FROM collections
                ORDER BY created_at DESC
            """)
            collections = cursor.fetchall()
            
            return [
                {
                    'id': row[0],
                    'name': row[1],
                    'created_at': row[2],
                    'file_count': row[3],
                    'total_items': row[4],
                    'completion_percentage': row[5]
                }
                for row in collections
            ]
            
        finally:
            conn.close()
    
    def compare_collections(self, collection_ids):
        """Compare multiple collections"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            comparison_data = {}
            
            for collection_id in collection_ids:
                cursor.execute("SELECT name, completion_percentage FROM collections WHERE id = ?", (collection_id,))
                collection = cursor.fetchone()
                
                if collection:
                    cursor.execute("""
                        SELECT color_id, completion_rate
                        FROM color_stats WHERE collection_id = ?
                        ORDER BY total_pieces DESC
                        LIMIT 10
                    """, (collection_id,))
                    color_stats = cursor.fetchall()
                    
                    comparison_data[collection_id] = {
                        'name': collection[0],
                        'overall_completion': collection[1],
                        'top_colors': color_stats
                    }
            
            return comparison_data
            
        finally:
            conn.close()

def create_dashboard_app():
    """Create Flask app with dashboard routes"""
    app = Flask(__name__)
    app.secret_key = 'dashboard_secret_key_change_in_production'
    
    analytics = DashboardAnalytics()
    
    @app.route('/dashboard')
    def dashboard_home():
        """Main dashboard page"""
        collections = analytics.get_collections_summary()
        return render_template('dashboard.html', collections=collections)
    
    @app.route('/dashboard/collection/<int:collection_id>')
    def collection_dashboard(collection_id):
        """Individual collection dashboard"""
        data = analytics.get_collection_dashboard_data(collection_id)
        if not data:
            return "Collection not found", 404
        return render_template('collection_dashboard.html', data=data)
    
    @app.route('/api/dashboard/collection/<int:collection_id>/data')
    def collection_data_api(collection_id):
        """API endpoint for collection dashboard data"""
        data = analytics.get_collection_dashboard_data(collection_id)
        if not data:
            return jsonify({'error': 'Collection not found'}), 404
        return jsonify(data)
    
    @app.route('/api/dashboard/compare')
    def compare_collections_api():
        """API endpoint for collection comparison"""
        collection_ids = request.args.getlist('ids', type=int)
        if not collection_ids:
            return jsonify({'error': 'No collection IDs provided'}), 400
        
        comparison = analytics.compare_collections(collection_ids)
        return jsonify(comparison)
    
    @app.route('/dashboard/analyze', methods=['POST'])
    def analyze_for_dashboard():
        """Analyze uploaded files and save to dashboard"""
        try:
            data = request.get_json()
            collection_name = data.get('collection_name', f'Collection_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            filenames = data.get('files', [])
            
            if not filenames:
                return jsonify({'error': 'No files provided'}), 400
            
            # Parse files
            parser = MultiFormatInputParser()
            analysis_results = {}
            
            upload_folder = 'uploads'  # Should match main app
            for filename in filenames:
                filepath = os.path.join(upload_folder, filename)
                if os.path.exists(filepath):
                    items = parser.parse_file(filepath)
                    analysis_results[filename] = {
                        'items': items,
                        'count': len(items),
                        'format': parser._get_format_name(filepath)
                    }
            
            # Save to database
            collection_id = analytics.save_collection_analysis(collection_name, analysis_results)
            
            return jsonify({
                'success': True,
                'collection_id': collection_id,
                'dashboard_url': f'/dashboard/collection/{collection_id}'
            })
            
        except Exception as e:
            logging.error(f"Error in dashboard analysis: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/bricklink/sync', methods=['POST'])
    def bricklink_sync_api():
        """API endpoint for BrickLink synchronization"""
        try:
            # Check if BrickLink credentials exist
            cred_manager = BrickLinkCredentialManager()
            try:
                credentials = cred_manager.load_credentials()
            except FileNotFoundError:
                return jsonify({
                    'error': 'BrickLink credentials not configured',
                    'setup_required': True
                }), 400
            
            # Create API client
            api = BrickLinkAPI(**credentials)
            sync = BrickLinkSync(api)
            
            sync_type = request.json.get('type', 'download_inventories')
            
            if sync_type == 'download_inventories':
                files = sync.download_inventories()
                return jsonify({
                    'success': True,
                    'message': f'Downloaded {len(files)} inventories',
                    'files': [str(f) for f in files]
                })
            
            elif sync_type == 'upload_wanted_list':
                xml_file = request.json.get('xml_file')
                list_name = request.json.get('list_name')
                
                if not xml_file:
                    return jsonify({'error': 'XML file required'}), 400
                
                wanted_list_id = sync.upload_wanted_list(xml_file, list_name)
                return jsonify({
                    'success': True,
                    'message': f'Uploaded wanted list: {list_name}',
                    'wanted_list_id': wanted_list_id
                })
            
            else:
                return jsonify({'error': 'Invalid sync type'}), 400
                
        except Exception as e:
            logging.error(f"BrickLink sync error: {e}")
            return jsonify({'error': str(e)}), 500
    
    return app

if __name__ == '__main__':
    # Test the dashboard analytics
    logging.basicConfig(level=logging.INFO)
    
    analytics = DashboardAnalytics()
    print("✅ Dashboard analytics initialized")
    
    # Create test data
    test_data = {
        'test_file.xml': {
            'items': [
                {
                    'item_id': '3001',
                    'item_type': 'P',
                    'color': '1',
                    'min_qty': 5,
                    'qty_filled': 3,
                    'category': 'Brick',
                    'source_file': 'test_file.xml'
                }
            ],
            'count': 1,
            'format': 'XML'
        }
    }
    
    collection_id = analytics.save_collection_analysis("Test Collection", test_data)
    print(f"✅ Created test collection: {collection_id}")
    
    # Test dashboard data
    dashboard_data = analytics.get_collection_dashboard_data(collection_id)
    print(f"✅ Dashboard data: {dashboard_data['collection']['name']}")
