"""
Test Upload via HTTP Request - Simulazione precisa interfaccia web
"""

import requests
import os

def test_real_upload():
    """Test real HTTP upload like web interface"""
    
    server_url = "http://localhost:5000"
    
    # Verifica server
    try:
        response = requests.get(server_url)
        print("✅ Server raggiungibile")
    except:
        print("❌ Server non raggiungibile")
        return False
    
    # Test upload
    test_file = "test_upload.xml"
    if not os.path.exists(test_file):
        print(f"❌ File {test_file} non trovato")
        return False
    
    print(f"📤 Upload di {test_file}...")
    
    # Simula esattamente l'upload form
    with open(test_file, 'rb') as f:
        files = {'files[]': f}
        
        try:
            response = requests.post(f"{server_url}/upload", files=files, allow_redirects=False)
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📍 Headers: {dict(response.headers)}")
            
            if response.status_code == 302:  # Redirect
                location = response.headers.get('Location', '')
                print(f"🔄 Redirect to: {location}")
                
                if '/analyze' in location:
                    print("✅ Upload successful, redirected to analyze")
                    
                    # Segui il redirect manualmente per vedere l'errore
                    analyze_url = f"{server_url}{location}" if location.startswith('/') else location
                    print(f"📊 Following redirect to: {analyze_url}")
                    
                    analyze_response = requests.get(analyze_url)
                    print(f"📊 Analyze Status: {analyze_response.status_code}")
                    
                    if analyze_response.status_code == 200:
                        print("✅ Analyze page loaded successfully")
                        return True
                    else:
                        print(f"❌ Analyze page error: {analyze_response.status_code}")
                        print(f"Response: {analyze_response.text[:500]}...")
                        return False
                else:
                    print(f"⚠️  Redirect to unexpected location: {location}")
                    return False
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"Response: {response.text[:500]}...")
                return False
                
        except Exception as e:
            print(f"❌ Request error: {e}")
            return False

if __name__ == "__main__":
    print("🧱 LEGO HTTP Upload Test")
    print("=" * 40)
    
    result = test_real_upload()
    
    if result:
        print("\n🎉 Test HTTP completato con successo!")
    else:
        print("\n❌ Test HTTP fallito")
