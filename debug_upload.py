"""
Debug Upload Issue - Test exact web upload behavior
"""

import os
import tempfile
import shutil
from pathlib import Path

# Simulate the exact upload process from web_app.py
def simulate_upload_process():
    """Simulate the exact file upload process"""
    
    print("🔍 Simulazione processo upload web...")
    
    # Simulate Flask upload process
    UPLOAD_FOLDER = 'uploads'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Simulate uploaded file
    test_file = 'test_upload.xml'
    if not os.path.exists(test_file):
        print(f"❌ File di test {test_file} non trovato")
        return False
    
    print(f"📂 Cartella upload: {UPLOAD_FOLDER}")
    print(f"📄 File di test: {test_file}")
    
    # Simulate timestamp and secure filename
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{test_file}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    print(f"📝 Nome file finale: {filename}")
    print(f"📍 Path completo: {filepath}")
    
    # Simulate the save process with temp file
    try:
        print("💾 Simulazione salvataggio file...")
        temp_filepath = filepath + '.tmp'
        
        # Copy file to temp location
        shutil.copy2(test_file, temp_filepath)
        print(f"✅ File copiato in temp: {temp_filepath}")
        
        # Rename to final location
        shutil.move(temp_filepath, filepath)
        print(f"✅ File spostato in finale: {filepath}")
        
        # Simulate analysis process
        print("🔄 Simulazione processo analisi...")
        
        # Import and test parser
        from input_handlers import MultiFormatInputParser
        parser = MultiFormatInputParser()
        
        print(f"📊 Analisi file: {filepath}")
        items = parser.parse_file(filepath)
        
        analysis_results = {
            filename: {
                'items': items,
                'count': len(items),
                'format': parser._get_format_name(filepath)
            }
        }
        
        print(f"✅ Analisi completata: {len(items)} items")
        print(f"📋 Formato rilevato: {analysis_results[filename]['format']}")
        
        # Cleanup
        os.remove(filepath)
        print("🧹 File temporaneo rimosso")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore durante simulazione: {e}")
        print(f"🔍 Tipo errore: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧱 LEGO Upload Debug - Simulazione Completa")
    print("=" * 50)
    
    result = simulate_upload_process()
    
    if result:
        print("\n🎉 Simulazione completata con successo!")
    else:
        print("\n❌ Simulazione fallita - controllare errori sopra")
