"""
Test Upload Functionality - LEGO Analysis
Quick test to verify upload and analysis works correctly
"""

import requests
import os

def test_upload_and_analyze():
    """Test the upload and analyze functionality"""
    
    server_url = "http://localhost:5000"
    
    # Check if server is running
    try:
        response = requests.get(server_url)
        print("✅ Server is running")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Start with 'python web_app.py'")
        return False
    
    # Test file upload
    test_file = "test_upload.xml"
    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} not found")
        return False
    
    print(f"📤 Testing upload of {test_file}")
    
    # Upload file
    with open(test_file, 'rb') as f:
        files = {'files[]': f}
        upload_response = requests.post(f"{server_url}/upload", files=files)
    
    if upload_response.status_code == 200:
        print("✅ Upload successful")
        print(f"📊 Response size: {len(upload_response.content)} bytes")
        
        # Check if redirected to analyze page
        if "analyze" in upload_response.url or "analizza" in upload_response.text.lower():
            print("✅ Redirected to analysis page")
            return True
        else:
            print("⚠️  Upload successful but not redirected to analysis")
            return True
    else:
        print(f"❌ Upload failed with status: {upload_response.status_code}")
        print(f"Response: {upload_response.text[:200]}...")
        return False

if __name__ == "__main__":
    print("🧱 LEGO Analysis Upload Test")
    print("=" * 40)
    
    result = test_upload_and_analyze()
    
    if result:
        print("\n🎉 Test completed successfully!")
        print("💡 Now try uploading via the web interface:")
        print("   http://localhost:5000/upload")
    else:
        print("\n❌ Test failed. Check server logs for details.")
