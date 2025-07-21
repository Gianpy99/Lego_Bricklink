"""
Test Upload XML Reale - London Set
"""

import requests
import os
import time

def test_real_xml_upload():
    """Test upload of real BrickLink XML file"""
    
    server_url = "http://localhost:5000"
    test_file = "21034 - London.xml"
    
    print(f"🧱 Test Upload: {test_file}")
    print("=" * 50)
    
    # Verifica file
    if not os.path.exists(test_file):
        print(f"❌ File {test_file} non trovato")
        return False
    
    file_size = os.path.getsize(test_file)
    print(f"📄 File: {test_file}")
    print(f"📊 Size: {file_size:,} bytes")
    
    # Test server
    try:
        response = requests.get(server_url, timeout=5)
        print("✅ Server raggiungibile")
    except Exception as e:
        print(f"❌ Server non raggiungibile: {e}")
        return False
    
    # Upload del file
    print("\n📤 Inizio upload...")
    start_time = time.time()
    
    try:
        with open(test_file, 'rb') as f:
            files = {'files[]': (test_file, f, 'text/xml')}
            
            response = requests.post(
                f"{server_url}/upload", 
                files=files, 
                allow_redirects=False,
                timeout=30
            )
        
        upload_time = time.time() - start_time
        print(f"⏱️  Upload completato in {upload_time:.2f}s")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 302:  # Redirect
            location = response.headers.get('Location', '')
            print(f"🔄 Redirect: {location}")
            
            if '/analyze' in location:
                print("✅ Upload successful, seguendo redirect...")
                
                # Segui redirect per analisi
                if location.startswith('/'):
                    analyze_url = f"{server_url}{location}"
                else:
                    analyze_url = location
                
                print(f"📊 Analisi URL: {analyze_url}")
                
                analyze_response = requests.get(analyze_url, timeout=30)
                
                print(f"📊 Analisi Status: {analyze_response.status_code}")
                
                if analyze_response.status_code == 200:
                    content = analyze_response.text
                    
                    # Cerca indicatori di successo/errore
                    if "Error analyzing files" in content:
                        print("❌ Errore nell'analisi trovato nella pagina")
                        # Estrai l'errore specifico
                        import re
                        error_match = re.search(r'Error analyzing files: ([^<\n]+)', content)
                        if error_match:
                            print(f"🔍 Errore specifico: {error_match.group(1)}")
                        return False
                    elif "items" in content.lower() or "analysis" in content.lower():
                        print("✅ Pagina di analisi caricata con successo")
                        
                        # Cerca statistiche
                        if "London" in content:
                            print("🏙️  Set London rilevato nel contenuto")
                        
                        # Cerca conteggio items
                        import re
                        count_match = re.search(r'(\d+)\s*items?', content, re.IGNORECASE)
                        if count_match:
                            print(f"📊 Items trovati: {count_match.group(1)}")
                        
                        return True
                    else:
                        print("⚠️  Pagina caricata ma contenuto sospetto")
                        print(f"📝 Primi 200 caratteri: {content[:200]}...")
                        return False
                else:
                    print(f"❌ Errore pagina analisi: {analyze_response.status_code}")
                    return False
            else:
                print(f"⚠️  Redirect inaspettato: {location}")
                return False
        else:
            print(f"❌ Upload fallito: {response.status_code}")
            print(f"📝 Response: {response.text[:300]}...")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante upload: {e}")
        return False

if __name__ == "__main__":
    result = test_real_xml_upload()
    
    if result:
        print("\n🎉 Test completato con SUCCESSO!")
        print("💡 Il file XML reale è stato processato correttamente")
    else:
        print("\n❌ Test FALLITO")
        print("🔍 Controllare i log del server per dettagli")
