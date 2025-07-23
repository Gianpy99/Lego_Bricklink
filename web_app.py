"""
Web Interface for LEGO Analysis System
Simple Flask web app for uploading files and viewing reports
"""

# Configure matplotlib backend before importing anything else
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for web applications
import matplotlib.pyplot as plt
plt.ioff()  # Turn off interactive mode

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, send_from_directory
import os
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import json
import logging
from pathlib import Path
import tempfile
import zipfile
import time
from datetime import datetime
import sys

# Import our analysis modules with error handling
try:
    from LegoStatusBuildAnalysis import LegoColorReport, LegoXmlCombiner
    from ModernReportGenerator import ModernReportGenerator
except ImportError as e:
    print(f"⚠️  Warning: Could not import LegoStatusBuildAnalysis: {e}")
    LegoColorReport = None
    LegoXmlCombiner = None
    ModernReportGenerator = None

try:
    from input_handlers import MultiFormatInputParser
except ImportError as e:
    print(f"⚠️  Warning: Could not import input_handlers: {e}")
    MultiFormatInputParser = None

try:
    from dashboard import DashboardAnalytics, create_dashboard_app
    DASHBOARD_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Could not import dashboard: {e}")
    print("   Dashboard functionality will be disabled")
    DashboardAnalytics = None
    create_dashboard_app = None
    DASHBOARD_AVAILABLE = False

try:
    from bricklink_api import BrickLinkAPI, BrickLinkSync, BrickLinkCredentialManager, BrickLinkAPIError
    BRICKLINK_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Could not import bricklink_api: {e}")
    print("   BrickLink integration will be disabled")
    BrickLinkAPI = None
    BrickLinkSync = None  
    BrickLinkCredentialManager = None
    BrickLinkAPIError = None
    BRICKLINK_AVAILABLE = False

# Load configuration
def load_config():
    """Load application configuration"""
    try:
        with open('app_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning("Configuration file not found, using defaults")
        return {
            "server": {"debug": False, "auto_reload": False},
            "upload": {"max_file_size": 16777216},
            "logging": {"level": "INFO"}
        }

config = load_config()

app = Flask(__name__)
app.secret_key = 'lego_analysis_secret_key_change_in_production'

# Configuration
UPLOAD_FOLDER = config.get('upload', {}).get('upload_folder', 'uploads')
REPORTS_FOLDER = config.get('reports', {}).get('output_folder', 'reports')
ALLOWED_EXTENSIONS = set(config.get('upload', {}).get('allowed_extensions', ['xml', 'csv', 'json']))
MAX_FILE_SIZE = config.get('upload', {}).get('max_file_size', 16 * 1024 * 1024)  # 16MB

# Configure Flask to not watch upload directory for changes
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching
app.config['TEMPLATES_AUTO_RELOAD'] = config.get('server', {}).get('auto_reload', False)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['EXPLAIN_TEMPLATE_LOADING'] = False  # Disable template monitoring

# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Color mapping function
def get_color_hex(color_id):
    """Convert BrickLink color ID to hex color for display"""
    # Basic color mapping - can be extended with more colors
    color_map = {
        '1': '#FFFFFF',   # White
        '5': '#D60026',   # Red
        '6': '#00AA5F',   # Green
        '7': '#0055BF',   # Blue
        '8': '#6C4516',   # Brown
        '9': '#9C9291',   # Light Gray
        '10': '#6B5A5A',  # Dark Gray
        '11': '#222222',  # Black
        '12': '#FFFFFF',  # Trans-Clear (displayed as white)
        '3': '#FFD700',   # Yellow
        '4': '#FFA500',   # Orange
        '86': '#9C9C9C',  # Light Bluish Gray
        '85': '#505050',  # Dark Bluish Gray
        '99': '#E6E3DA',  # Very Light Bluish Gray
        '49': '#BEBEBE',  # Very Light Gray
        '59': '#8B0000',  # Dark Red
        '2': '#DEB887',   # Tan
        '25': '#FF7F7F',  # Salmon
        '26': '#FFB3BA',  # Light Salmon
        '58': '#B22222',  # Sand Red
        '120': '#654321', # Dark Brown
        '168': '#8B4513', # Umber
    }
    return color_map.get(str(color_id), '#CCCCCC')  # Default gray for unknown colors

# Make function available in templates
@app.context_processor
def utility_processor():
    return dict(get_color_hex=get_color_hex)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_files():
    """Upload and process LEGO inventory files"""
    if request.method == 'POST':
        if 'files[]' not in request.files:
            flash('No files selected')
            return redirect(request.url)
        
        files = request.files.getlist('files[]')
        uploaded_files = []
        
        for file in files:
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                
                # Save file safely without triggering auto-reload
                try:
                    # Use a temporary name first, then rename to avoid filesystem watching
                    temp_filepath = filepath + '.tmp'
                    file.save(temp_filepath)
                    
                    # Quick rename to final name
                    import shutil
                    shutil.move(temp_filepath, filepath)
                    
                    uploaded_files.append(filename)
                    logging.info(f"File uploaded successfully: {filename}")
                except Exception as e:
                    # Clean up temp file if it exists
                    temp_filepath = filepath + '.tmp'
                    if os.path.exists(temp_filepath):
                        os.remove(temp_filepath)
                    logging.error(f"Error saving file {filename}: {e}")
                    flash(f'Error uploading {filename}: {str(e)}')
        
        if uploaded_files:
            flash(f'Successfully uploaded {len(uploaded_files)} files')
            return redirect(url_for('analyze', files=','.join(uploaded_files)))
        else:
            flash('No valid files uploaded')
    
    return render_template('upload.html')

@app.route('/analyze')
def analyze():
    """Analyze uploaded files"""
    try:
        logging.info("=== ANALYZE ROUTE START ===")
        
        files_param = request.args.get('files', '')
        logging.info(f"Files parameter: {files_param}")
        
        if not files_param:
            logging.warning("No files parameter found")
            flash('No files to analyze')
            return redirect(url_for('upload_files'))
        
        filenames = files_param.split(',')
        logging.info(f"Parsed filenames: {filenames}")
        
        # Check if MultiFormatInputParser is available
        if MultiFormatInputParser is None:
            logging.error("MultiFormatInputParser is None")
            flash('Input parser not available. Please check dependencies.')
            return redirect(url_for('upload_files'))
        
        logging.info("Creating MultiFormatInputParser instance")
        # Parse files using multi-format parser
        parser = MultiFormatInputParser()
        analysis_results = {}
        
        for filename in filenames:
            logging.info(f"Processing file: {filename}")
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            logging.info(f"Full filepath: {filepath}")
            
            if os.path.exists(filepath):
                logging.info(f"File exists, parsing: {filepath}")
                items = parser.parse_file(filepath)
                logging.info(f"Parsed {len(items)} items")
                
                format_name = parser._get_format_name(filepath)
                logging.info(f"Format detected: {format_name}")
                
                analysis_results[filename] = {
                    'parsed_items': items,  # Rinomino da 'items' a 'parsed_items' per evitare conflitto con .items()
                    'count': len(items),
                    'format': format_name
                }
                logging.info(f"Added to results: {filename}")
                logging.info(f"Items type: {type(items)}, Count: {len(items)}")
                if items:
                    logging.info(f"First item: {items[0].__dict__ if hasattr(items[0], '__dict__') else items[0]}")
            else:
                logging.warning(f"File not found: {filepath}")
        
        logging.info("=== ANALYZE ROUTE SUCCESS ===")
        return render_template('analyze.html', results=analysis_results)
        
    except Exception as e:
        logging.error(f"=== ANALYZE ROUTE ERROR ===")
        logging.error(f"Error type: {type(e).__name__}")
        logging.error(f"Error message: {str(e)}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        flash(f'Error analyzing files: {str(e)}')
        return redirect(url_for('upload_files'))

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """Generate PDF report from uploaded files with different report types"""
    try:
        data = request.get_json()
        filenames = data.get('files', [])
        report_type = data.get('report_type', 'summary')  # 'summary', 'detailed', 'complete'
        
        logging.info(f"=== PDF REPORT GENERATION STARTED ===")
        logging.info(f"Report type: {report_type}")
        logging.info(f"Selected files: {len(filenames)} file(s)")
        
        if not filenames:
            return jsonify({'error': 'No files specified'}), 400
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy selected files to temp directory
            copied_files = 0
            for filename in filenames:
                src = os.path.join(UPLOAD_FOLDER, filename)
                # Remove timestamp from filename (format: YYYYMMDD_HHMMSS_original_name.xml)
                original_name = '_'.join(filename.split('_')[2:])  # Remove first two timestamp parts
                dst = os.path.join(temp_dir, original_name)
                if os.path.exists(src):
                    import shutil
                    shutil.copy2(src, dst)
                    copied_files += 1
                    logging.info(f"Copied file {copied_files}/{len(filenames)}: {original_name}")
            
            logging.info(f"Successfully copied {copied_files} files to temporary directory")
            
            # Generate report with type-specific filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_type_suffix = f"_{report_type}" if report_type != 'summary' else ""
            report_filename = f"lego_report{report_type_suffix}_{timestamp}.pdf"
            report_path = os.path.join(REPORTS_FOLDER, report_filename)
            
            logging.info(f"Generating {report_type} report: {report_filename}")
            
            # Use new ModernReportGenerator for enhanced PDF reports
            if ModernReportGenerator:
                report_generator = ModernReportGenerator(
                    folder_path=temp_dir,
                    color_mapping_path='BL_color_mapping.json',
                    output_pdf=report_path
                )
                
                # Generate report based on type
                if report_type == 'summary':
                    report_generator.generate_executive_summary()
                elif report_type == 'detailed':
                    report_generator.generate_detailed_report()
                else:  # complete
                    report_generator.generate_complete_report()
            else:
                # Fallback to existing LegoColorReport if ModernReportGenerator not available
                report = LegoColorReport(
                    folder_path=temp_dir,
                    color_mapping_path='BL_color_mapping.json',
                    output_pdf=report_path
                )
                report.process()
            
            logging.info(f"=== PDF REPORT GENERATION COMPLETED ===")
            logging.info(f"Output file: {report_filename}")
            
            return jsonify({
                'success': True,
                'report_url': f'/download_report/{report_filename}',
                'filename': report_filename,
                'report_type': report_type,
                'files_processed': copied_files
            })
    
    except Exception as e:
        logging.error(f"Error generating report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/download_report/<filename>')
def download_report(filename):
    """Download generated report"""
    report_path = os.path.join(REPORTS_FOLDER, filename)
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    else:
        flash('Report not found')
        return redirect(url_for('index'))

@app.route('/generate_wanted_list', methods=['POST'])
def generate_wanted_list():
    """Generate wanted list XML from selected files with detailed logging"""
    try:
        data = request.get_json()
        filenames = data.get('files', [])
        
        if not filenames:
            return jsonify({'error': 'No files specified'}), 400

        logging.info(f"=== WANTED LIST GENERATION STARTED ===")
        logging.info(f"Selected files: {len(filenames)} file(s)")
        for i, filename in enumerate(filenames, 1):
            logging.info(f"  {i}. {filename}")

        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            logging.info(f"Created temporary directory: {temp_dir}")
            
            # Copy selected files to temp directory
            copied_files = 0
            for filename in filenames:
                src = os.path.join(UPLOAD_FOLDER, filename)
                # Remove timestamp from filename (format: YYYYMMDD_HHMMSS_original_name.xml)
                original_name = '_'.join(filename.split('_')[2:])  # Remove first two timestamp parts
                dst = os.path.join(temp_dir, original_name)
                if os.path.exists(src):
                    import shutil
                    shutil.copy2(src, dst)
                    copied_files += 1
                    logging.info(f"Copied file {copied_files}/{len(filenames)}: {original_name}")
            
            logging.info(f"Successfully copied {copied_files} files to temporary directory")
            
            # Generate wanted list XML
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            wanted_list_filename = f"wanted_list_{timestamp}.xml"
            wanted_list_path = os.path.join(REPORTS_FOLDER, wanted_list_filename)
            filtered_folder = os.path.join(REPORTS_FOLDER, f"filtered_{timestamp}")
            
            # Create filtered folder
            os.makedirs(filtered_folder, exist_ok=True)
            logging.info(f"Created filtered folder: {filtered_folder}")
            
            # Use existing LegoXmlCombiner class
            logging.info("Initializing LegoXmlCombiner...")
            combiner = LegoXmlCombiner(
                folder_path=temp_dir,
                filtered_folder=filtered_folder,
                output_file=wanted_list_path
            )
            
            logging.info("Starting XML processing...")
            combiner.process()
            logging.info("XML processing completed successfully!")
            
            # Add performance info
            combiner.stats['processing_time'] = f"{time.time() - request.start_time:.2f}s" if hasattr(request, 'start_time') else 'unknown'
            
            logging.info(f"=== WANTED LIST GENERATION COMPLETED ===")
            logging.info(f"Output file: {wanted_list_filename}")
            logging.info(f"Statistics: {combiner.stats}")
            
            return jsonify({
                'success': True,
                'wanted_list_url': f'/download_report/{wanted_list_filename}',
                'filename': wanted_list_filename,
                'stats': combiner.stats
            })
            
    except Exception as e:
        logging.error(f"Error generating wanted list: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def api_stats():
    """API endpoint for system statistics"""
    try:
        upload_count = len(os.listdir(UPLOAD_FOLDER))
        
        # Count different types of reports
        report_files = os.listdir(REPORTS_FOLDER)
        total_reports = len(report_files)
        wanted_list_count = len([f for f in report_files if f.startswith('wanted_list_')])
        
        # Get file format distribution
        parser = MultiFormatInputParser()
        format_stats = {}
        
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                format_name = parser._get_format_name(filepath)
                format_stats[format_name] = format_stats.get(format_name, 0) + 1
        
        return jsonify({
            'uploads': upload_count,
            'reports': total_reports,
            'wanted_lists': wanted_list_count,
            'supported_formats': parser.get_supported_formats(),
            'format_distribution': format_stats
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup_files():
    """Clean up old uploaded files and reports"""
    try:
        # Remove files older than 24 hours
        import time
        current_time = time.time()
        cleanup_count = 0
        
        for folder in [UPLOAD_FOLDER, REPORTS_FOLDER]:
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getctime(filepath)
                    if file_age > 86400:  # 24 hours
                        os.remove(filepath)
                        cleanup_count += 1
        
        return jsonify({
            'success': True,
            'cleaned_files': cleanup_count
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reports/<filename>')
def download_xml_file(filename):
    """Download XML or PDF reports"""
    try:
        reports_dir = os.path.join(os.getcwd(), 'reports')
        file_path = os.path.join(reports_dir, filename)
        
        # Verifica che il file esista e sia nella cartella reports
        if not os.path.exists(file_path) or not file_path.startswith(reports_dir):
            return jsonify({'error': 'File non trovato'}), 404
        
        return send_from_directory(reports_dir, filename, as_attachment=True)
        
    except Exception as e:
        logging.error(f"Error downloading file {filename}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/bricklink')
def bricklink_page():
    """BrickLink integration page"""
    return render_template('bricklink.html')

@app.route('/bricklink/xml-files')
def bricklink_xml_files():
    """Get available XML files for upload"""
    try:
        reports_dir = 'reports'
        if not os.path.exists(reports_dir):
            return jsonify({'xml_files': []})
        
        xml_files = []
        for file in os.listdir(reports_dir):
            if file.endswith('.xml'):
                file_path = os.path.join(reports_dir, file)
                stat = os.stat(file_path)
                xml_files.append({
                    'name': file,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # Ordina per data di modifica (più recente prima)
        xml_files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({'xml_files': xml_files})
        
    except Exception as e:
        logging.error(f"Error listing XML files: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test-upload')
def test_upload():
    """Test page for debugging upload restart bug"""
    return render_template('test_upload.html')

@app.route('/bricklink/setup', methods=['GET', 'POST'])
def bricklink_setup():
    """Setup or update BrickLink API credentials"""
    if not BRICKLINK_AVAILABLE:
        return jsonify({'error': 'BrickLink integration not available'}), 503
    
    if request.method == 'GET':
        # Check if credentials exist
        cred_manager = BrickLinkCredentialManager()
        try:
            cred_manager.load_credentials()
            has_credentials = True
        except FileNotFoundError:
            has_credentials = False
        
        return jsonify({'has_credentials': has_credentials})
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['consumer_key', 'consumer_secret', 'token', 'token_secret']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Save credentials
            cred_manager = BrickLinkCredentialManager()
            cred_manager.save_credentials(
                data['consumer_key'],
                data['consumer_secret'], 
                data['token'],
                data['token_secret']
            )
            
            # Test connection
            credentials = cred_manager.load_credentials()
            api = BrickLinkAPI(**credentials)
            
            try:
                # Test with a simple API call
                test_result = api.get_wanted_lists()
                logging.info("✅ BrickLink API connection successful")
                
                return jsonify({
                    'success': True,
                    'message': 'BrickLink credentials saved and tested successfully!',
                    'test_result': f"Connected successfully. Found {len(test_result.get('data', []))} wanted lists."
                })
                
            except Exception as e:
                logging.error(f"❌ BrickLink API test failed: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Credentials saved but API test failed: {str(e)}',
                    'test_failed': True
                }), 400
                
        except Exception as e:
            logging.error(f"Error setting up BrickLink credentials: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/bricklink/upload', methods=['POST'])
def bricklink_upload():
    """Upload wanted list to BrickLink"""
    if not BRICKLINK_AVAILABLE:
        return jsonify({'error': 'BrickLink integration not available'}), 503
    
    try:
        data = request.get_json()
        xml_file = data.get('xml_file')
        list_name = data.get('list_name')
        
        if not xml_file:
            return jsonify({'error': 'No XML file specified'}), 400
        
        # Check if file exists
        xml_path = os.path.join('reports', xml_file)
        if not os.path.exists(xml_path):
            return jsonify({'error': f'XML file not found: {xml_file}'}), 404
        
        # Load credentials
        try:
            cred_manager = BrickLinkCredentialManager()
            credentials = cred_manager.load_credentials()
        except FileNotFoundError:
            return jsonify({'error': 'BrickLink credentials not configured. Please set up credentials first.'}), 401
        
        # Initialize API and sync
        api = BrickLinkAPI(**credentials)
        sync = BrickLinkSync(api)
        
        # Upload with automatic replacement
        logging.info(f"📤 Starting BrickLink upload for: {xml_file}")
        result = sync.upload_wanted_list(xml_path, list_name, replace_existing=True)
        
        return jsonify({
            'success': True,
            'message': f'Successfully {result["action"]} wanted list on BrickLink!',
            'details': {
                'list_name': result['list_name'],
                'wanted_list_id': result['wanted_list_id'],
                'total_items': result['total_items'],
                'uploaded_items': result['uploaded_items'],
                'skipped_items': result['skipped_items'],
                'action': result['action']
            }
        })
        
    except BrickLinkAPIError as e:
        logging.error(f"BrickLink API error: {e}")
        return jsonify({'error': f'BrickLink API error: {str(e)}'}), 500
    except Exception as e:
        logging.error(f"Error uploading to BrickLink: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/bricklink/status')
def bricklink_status():
    """Check BrickLink integration status"""
    if not BRICKLINK_AVAILABLE:
        return jsonify({
            'available': False,
            'error': 'BrickLink integration not available - missing dependencies'
        })
    
    try:
        # Check credentials
        cred_manager = BrickLinkCredentialManager()
        credentials = cred_manager.load_credentials()
        
        # Test API connection
        api = BrickLinkAPI(**credentials)
        user_info = api.get_user_info()
        is_seller = api.is_seller_account()
        
        return jsonify({
            'available': True,
            'connected': True,
            'is_seller': is_seller,
            'user_name': user_info.get('data', {}).get('real_name', 'Unknown'),
            'store_name': user_info.get('data', {}).get('store_name', None),
            'message': f'Connected as {"SELLER" if is_seller else "BUYER"} account'
        })
        
    except FileNotFoundError:
        return jsonify({
            'available': True,
            'connected': False,
            'message': 'BrickLink credentials not configured'
        })
    except Exception as e:
        return jsonify({
            'available': True,
            'connected': False,
            'error': str(e),
            'message': 'BrickLink connection failed'
        })

@app.route('/bricklink/lists')
def bricklink_lists():
    """Get user's BrickLink wanted lists"""
    if not BRICKLINK_AVAILABLE:
        return jsonify({'error': 'BrickLink integration not available'}), 503
    
    try:
        # Load credentials
        cred_manager = BrickLinkCredentialManager()
        credentials = cred_manager.load_credentials()
        
        # Get wanted lists
        api = BrickLinkAPI(**credentials)
        result = api.get_wanted_lists()
        
        wanted_lists = []
        for wl in result.get('data', []):
            wanted_lists.append({
                'id': wl['wanted_list_id'],
                'name': wl['name'],
                'description': wl.get('description', ''),
                'items_count': wl.get('items_count', 0),
                'created': wl.get('date_created', '')
            })
        
        return jsonify({'wanted_lists': wanted_lists})
        
    except FileNotFoundError:
        return jsonify({'error': 'BrickLink credentials not configured'}), 401
    except Exception as e:
        logging.error(f"Error fetching BrickLink wanted lists: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Avvio LEGO Analysis System...")
    
    # Initialize dashboard analytics if available
    if DASHBOARD_AVAILABLE:
        try:
            analytics = DashboardAnalytics()
            
            # Register dashboard routes
            dashboard_app = create_dashboard_app()
            
            # Register dashboard blueprints with main app
            from flask import Blueprint
            dashboard_bp = Blueprint('dashboard_routes', __name__)
            
            # Copy dashboard routes to main app
            for rule in dashboard_app.url_map.iter_rules():
                if rule.endpoint.startswith('dashboard') or rule.endpoint.startswith('api'):
                    endpoint_func = dashboard_app.view_functions[rule.endpoint]
                    app.add_url_rule(rule.rule, rule.endpoint, endpoint_func, methods=rule.methods)
            
            print("✅ Dashboard Interattiva Configurata!")
        except Exception as e:
            print(f"⚠️  Dashboard non disponibile: {e}")
            DASHBOARD_AVAILABLE = False
    
    if DASHBOARD_AVAILABLE:
        print("📊 Funzionalità disponibili:")
        print("   • Chart.js per grafici interattivi")
        print("   • Filtri real-time per dati")
        print("   • Confronto collezioni")
        print("   • Esportazione multi-formato")
        print("   • Integrazione BrickLink API")
        print("   • Timeline progressi")
        print("   • Database SQLite per analytics")
    else:
        print("📊 Modalità BASE attiva:")
        print("   • Upload e analisi file XML/CSV")
        print("   • Generazione report PDF")
        print("   • Interfaccia web semplificata")
        print("   • Funzionalità core LEGO analysis")
    
    # Get server configuration
    server_config = config.get('server', {})
    debug_mode = '--debug' in sys.argv or server_config.get('debug', False)
    
    print(f"\n🚀 Avvio server in modalità {'DEBUG' if debug_mode else 'PRODUZIONE'}...")
    
    if debug_mode:
        print("⚠️  Modalità debug: auto-reload abilitato (esclusi uploads)")
        # Debug mode with selective file watching
        app.run(
            debug=True, 
            host=server_config.get('host', '0.0.0.0'), 
            port=server_config.get('port', 5000),
            use_reloader=True,
            reloader_options={
                'exclude_patterns': server_config.get('exclude_patterns', [
                    'uploads/*', '*.log', 'reports/*', 'analytics.db'
                ])
            }
        )
    else:
        print("✅ Modalità produzione: server stabile, nessun riavvio automatico")
        # Production mode - completely disable file monitoring
        app.run(
            debug=False, 
            host=server_config.get('host', '0.0.0.0'), 
            port=server_config.get('port', 5000),
            use_reloader=False,
            use_debugger=False,
            passthrough_errors=False,
            threaded=True  # Enable threading for better performance
        )
