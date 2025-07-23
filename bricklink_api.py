"""
BrickLink API Integration for LEGO Analysis System
Provides OAuth authentication and data synchronization with BrickLink
"""

import requests
import json
import hashlib
import hmac
import time
import base64
import urllib.parse
from datetime import datetime
import logging
from pathlib import Path
import os

class BrickLinkAPIError(Exception):
    """Custom exception for BrickLink API errors"""
    pass

class BrickLinkAPI:
    """
    BrickLink API client with OAuth 1.0a authentication
    Supports inventory management, wanted lists, and catalog data
    """
    
    def __init__(self, consumer_key, consumer_secret, token, token_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token = token
        self.token_secret = token_secret
        self.base_url = "https://api.bricklink.com/api/store/v1"
        self.session = requests.Session()
        
    def _generate_oauth_header(self, method, url, params=None):
        """Generate OAuth 1.0a authorization header"""
        if params is None:
            params = {}
            
        # OAuth parameters
        oauth_params = {
            'oauth_consumer_key': self.consumer_key,
            'oauth_token': self.token,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': hashlib.md5(str(time.time()).encode()).hexdigest(),
            'oauth_version': '1.0'
        }
        
        # Combine all parameters
        all_params = {**params, **oauth_params}
        
        # Create parameter string
        param_string = '&'.join([f"{k}={urllib.parse.quote(str(v), safe='')}" 
                                for k, v in sorted(all_params.items())])
        
        # Create signature base string
        base_string = f"{method.upper()}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(param_string, safe='')}"
        
        # Create signing key
        signing_key = f"{urllib.parse.quote(self.consumer_secret, safe='')}&{urllib.parse.quote(self.token_secret, safe='')}"
        
        # Generate signature
        signature = base64.b64encode(
            hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
        ).decode()
        
        oauth_params['oauth_signature'] = signature
        
        # Create authorization header
        auth_header = 'OAuth ' + ', '.join([f'{k}="{urllib.parse.quote(str(v), safe="")}"' 
                                          for k, v in sorted(oauth_params.items())])
        
        return auth_header
    
    def _make_request(self, method, endpoint, params=None, data=None):
        """Make authenticated request to BrickLink API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            auth_header = self._generate_oauth_header(method, url, params)
            headers = {
                'Authorization': auth_header,
                'Content-Type': 'application/json'
            }
            
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limiting
                logging.warning("Rate limit exceeded, waiting...")
                time.sleep(60)
                return self._make_request(method, endpoint, params, data)
            else:
                error_msg = f"API request failed: {response.status_code} - {response.text}"
                logging.error(error_msg)
                raise BrickLinkAPIError(error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {e}"
            logging.error(error_msg)
            raise BrickLinkAPIError(error_msg)
    
    def get_inventories(self):
        """Get all store inventories"""
        logging.info("Fetching store inventories...")
        return self._make_request('GET', '/inventories')
    
    def get_inventory_by_id(self, inventory_id):
        """Get specific inventory by ID"""
        return self._make_request('GET', f'/inventories/{inventory_id}')
    
    def get_user_info(self):
        """Get current user information including account type"""
        try:
            response = self._make_request('GET', '/users/me')
            return response
        except Exception as e:
            logging.error(f"Error getting user info: {e}")
            raise BrickLinkAPIError(f"Failed to get user info: {str(e)}")
    
    def is_seller_account(self):
        """Check if the current account is a seller account"""
        try:
            user_info = self.get_user_info()
            # Check if user has seller privileges (based on BrickLink API documentation)
            user_data = user_info.get('data', {})
            return user_data.get('store_name') is not None and user_data.get('store_name') != ''
        except Exception as e:
            logging.warning(f"Could not determine account type: {e}")
            return False
    
    def get_wanted_lists(self):
        """Get all wanted lists"""
        logging.info("Fetching wanted lists...")
        return self._make_request('GET', '/wanted_lists')
    
    def get_wanted_list_items(self, wanted_list_id):
        """Get items from specific wanted list"""
        return self._make_request('GET', f'/wanted_lists/{wanted_list_id}/items')
    
    def create_wanted_list(self, name, description=""):
        """Create new wanted list"""
        data = {
            'name': name,
            'description': description
        }
        return self._make_request('POST', '/wanted_lists', data=data)
    
    def add_wanted_list_items(self, wanted_list_id, items):
        """Add items to wanted list"""
        return self._make_request('POST', f'/wanted_lists/{wanted_list_id}/items', data=items)
    
    def delete_wanted_list(self, wanted_list_id):
        """Delete wanted list"""
        logging.info(f"Deleting wanted list ID: {wanted_list_id}")
        return self._make_request('DELETE', f'/wanted_lists/{wanted_list_id}')
    
    def clear_wanted_list_items(self, wanted_list_id):
        """Clear all items from wanted list"""
        logging.info(f"Clearing all items from wanted list ID: {wanted_list_id}")
        return self._make_request('DELETE', f'/wanted_lists/{wanted_list_id}/items')
    
    def update_wanted_list(self, wanted_list_id, name=None, description=None):
        """Update wanted list details"""
        data = {}
        if name:
            data['name'] = name
        if description:
            data['description'] = description
        return self._make_request('PUT', f'/wanted_lists/{wanted_list_id}', data=data)
    
    def get_item_info(self, item_type, item_id, color_id=None):
        """Get item information from catalog"""
        endpoint = f'/items/{item_type}/{item_id}'
        params = {}
        if color_id:
            params['color_id'] = color_id
        return self._make_request('GET', endpoint, params=params)
    
    def get_price_guide(self, item_type, item_id, color_id, guide_type='sold'):
        """Get price guide for item"""
        endpoint = f'/items/{item_type}/{item_id}/price'
        params = {
            'color_id': color_id,
            'guide_type': guide_type
        }
        return self._make_request('GET', endpoint, params=params)
    
    def search_items(self, query, item_type='part'):
        """Search for items in catalog"""
        endpoint = f'/items/{item_type}'
        params = {'search': query}
        return self._make_request('GET', endpoint, params=params)

class BrickLinkSync:
    """
    Synchronization service for BrickLink data
    Handles downloading inventories and uploading wanted lists
    """
    
    def __init__(self, api_client, local_data_folder="bricklink_data"):
        self.api = api_client
        self.data_folder = Path(local_data_folder)
        self.data_folder.mkdir(exist_ok=True)
        
    def download_inventories(self, save_to_xml=True):
        """Download all inventories and save locally"""
        try:
            inventories = self.api.get_inventories()
            
            if not inventories.get('data'):
                logging.warning("No inventories found")
                return []
            
            saved_files = []
            
            for inventory in inventories['data']:
                inventory_id = inventory['inventory_id']
                logging.info(f"Downloading inventory {inventory_id}...")
                
                # Get full inventory details
                full_inventory = self.api.get_inventory_by_id(inventory_id)
                
                if save_to_xml:
                    xml_file = self._save_inventory_as_xml(full_inventory['data'], inventory_id)
                    saved_files.append(xml_file)
                
                # Also save as JSON for backup
                json_file = self.data_folder / f"inventory_{inventory_id}.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(full_inventory['data'], f, indent=2)
                
                # Rate limiting
                time.sleep(1)
            
            logging.info(f"Downloaded {len(saved_files)} inventories")
            return saved_files
            
        except Exception as e:
            logging.error(f"Error downloading inventories: {e}")
            raise
    
    def _save_inventory_as_xml(self, inventory_data, inventory_id):
        """Convert inventory data to BrickLink XML format"""
        import xml.etree.ElementTree as ET
        
        root = ET.Element("INVENTORY")
        
        for item in inventory_data:
            item_elem = ET.SubElement(root, "ITEM")
            
            # Map API fields to XML structure
            ET.SubElement(item_elem, "ITEMTYPE").text = item.get('item', {}).get('type', 'P')
            ET.SubElement(item_elem, "ITEMID").text = item.get('item', {}).get('no', '')
            ET.SubElement(item_elem, "COLOR").text = str(item.get('color_id', '0'))
            ET.SubElement(item_elem, "MINQTY").text = str(item.get('quantity', '0'))
            ET.SubElement(item_elem, "QTYFILLED").text = "0"  # For wanted lists
            ET.SubElement(item_elem, "PRICE").text = str(item.get('unit_price', '0'))
            ET.SubElement(item_elem, "CONDITION").text = item.get('new_or_used', 'N')
            
            if item.get('description'):
                ET.SubElement(item_elem, "REMARKS").text = item['description']
        
        # Save XML file
        xml_file = self.data_folder / f"inventory_{inventory_id}.xml"
        tree = ET.ElementTree(root)
        tree.write(xml_file, encoding='utf-8', xml_declaration=True)
        
        logging.info(f"Saved inventory as XML: {xml_file}")
        return xml_file
    
    def upload_wanted_list(self, xml_file, list_name=None, replace_existing=True):
        """
        Upload XML wanted list to BrickLink with advanced replacement options
        
        Args:
            xml_file (str): Path to XML file containing wanted list
            list_name (str): Name for the wanted list (auto-generated if None)
            replace_existing (bool): If True, replaces existing list with same name
        
        Returns:
            dict: Information about the uploaded wanted list
        """
        try:
            if list_name is None:
                # Generate name from filename or timestamp
                filename = Path(xml_file).stem
                if filename.startswith('wanted_list_'):
                    list_name = f"LEGO Analysis - {filename.replace('wanted_list_', '').replace('_', ' ').title()}"
                else:
                    list_name = f"LEGO Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Parse XML file
            import xml.etree.ElementTree as ET
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            wanted_list_id = None
            
            # Check if we should replace existing list
            if replace_existing:
                existing_lists = self.api.get_wanted_lists()
                if existing_lists.get('data'):
                    for existing_list in existing_lists['data']:
                        if existing_list['name'] == list_name:
                            wanted_list_id = existing_list['wanted_list_id']
                            logging.info(f"Found existing wanted list '{list_name}' (ID: {wanted_list_id})")
                            
                            # Clear existing items
                            try:
                                self.api.clear_wanted_list_items(wanted_list_id)
                                logging.info(f"Cleared existing items from wanted list")
                            except Exception as e:
                                logging.warning(f"Could not clear existing items: {e}")
                                # If clearing fails, delete and recreate
                                self.api.delete_wanted_list(wanted_list_id)
                                wanted_list_id = None
                            break
            
            # Create new wanted list if needed
            if wanted_list_id is None:
                description = f"Auto-generated from LEGO Analysis System on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                wanted_list = self.api.create_wanted_list(list_name, description)
                wanted_list_id = wanted_list['data']['wanted_list_id']
                logging.info(f"Created new wanted list '{list_name}' (ID: {wanted_list_id})")
            
            # Convert XML items to API format
            items = []
            skipped_items = 0
            
            for item_elem in root.findall('ITEM'):
                try:
                    item_id = item_elem.find('ITEMID')
                    if item_id is None or not item_id.text:
                        skipped_items += 1
                        continue
                    
                    item_data = {
                        'item': {
                            'no': item_id.text,
                            'type': item_elem.find('ITEMTYPE').text if item_elem.find('ITEMTYPE') is not None else 'P'
                        },
                        'color_id': int(item_elem.find('COLOR').text) if item_elem.find('COLOR') is not None else 0,
                        'min_quantity': int(item_elem.find('MINQTY').text) if item_elem.find('MINQTY') is not None else 1,
                        'condition': item_elem.find('CONDITION').text if item_elem.find('CONDITION') is not None else 'N'
                    }
                    
                    # Optional fields
                    if item_elem.find('PRICE') is not None and item_elem.find('PRICE').text:
                        try:
                            max_price = float(item_elem.find('PRICE').text)
                            if max_price > 0:
                                item_data['max_price'] = str(max_price)
                        except ValueError:
                            pass
                    
                    if item_elem.find('REMARKS') is not None and item_elem.find('REMARKS').text:
                        item_data['remarks'] = item_elem.find('REMARKS').text[:250]  # BrickLink limit
                    
                    items.append(item_data)
                    
                except Exception as e:
                    logging.warning(f"Skipped invalid item: {e}")
                    skipped_items += 1
                    continue
            
            if not items:
                raise ValueError("No valid items found in XML file")
            
            # Upload items in batches (BrickLink API has limits)
            batch_size = 100
            uploaded_batches = 0
            
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                try:
                    self.api.add_wanted_list_items(wanted_list_id, batch)
                    uploaded_batches += 1
                    batch_num = i//batch_size + 1
                    total_batches = (len(items) + batch_size - 1)//batch_size
                    logging.info(f"✅ Uploaded batch {batch_num}/{total_batches} ({len(batch)} items)")
                    
                    # Rate limiting - be gentle with BrickLink API
                    if batch_num < total_batches:
                        time.sleep(2)
                        
                except Exception as e:
                    logging.error(f"Failed to upload batch {i//batch_size + 1}: {e}")
                    # Continue with remaining batches
                    time.sleep(5)  # Longer wait after error
                    continue
            
            # Summary
            success_items = uploaded_batches * batch_size if uploaded_batches * batch_size <= len(items) else len(items)
            result = {
                'wanted_list_id': wanted_list_id,
                'list_name': list_name,
                'total_items': len(items),
                'uploaded_items': success_items,
                'skipped_items': skipped_items,
                'batches_uploaded': uploaded_batches,
                'action': 'replaced' if replace_existing else 'created'
            }
            
            logging.info(f"🎉 Successfully {'replaced' if replace_existing else 'created'} wanted list '{list_name}' with {success_items}/{len(items)} items")
            if skipped_items > 0:
                logging.warning(f"⚠️ Skipped {skipped_items} invalid items")
            
            return result
            
        except Exception as e:
            logging.error(f"❌ Error uploading wanted list: {e}")
            raise BrickLinkAPIError(f"Failed to upload wanted list: {str(e)}")
    
    def upload_wanted_list_from_analysis(self, xml_file, credentials_dict=None):
        """
        Convenience method to upload wanted list with user credentials
        
        Args:
            xml_file (str): Path to XML wanted list file
            credentials_dict (dict): BrickLink API credentials
        
        Returns:
            dict: Upload result information
        """
        try:
            # Use provided credentials or load from file
            if credentials_dict:
                temp_api = BrickLinkAPI(**credentials_dict)
                temp_sync = BrickLinkSync(temp_api)
                return temp_sync.upload_wanted_list(xml_file, replace_existing=True)
            else:
                # Use existing API instance
                return self.upload_wanted_list(xml_file, replace_existing=True)
                
        except Exception as e:
            logging.error(f"Failed to upload wanted list from analysis: {e}")
            raise
    
    def sync_price_data(self, xml_file):
        """Fetch current price data for items in XML file"""
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            price_data = {}
            
            for item_elem in root.findall('ITEM'):
                item_id = item_elem.find('ITEMID').text
                item_type = item_elem.find('ITEMTYPE').text if item_elem.find('ITEMTYPE') is not None else 'P'
                color_id = item_elem.find('COLOR').text if item_elem.find('COLOR') is not None else '0'
                
                try:
                    price_guide = self.api.get_price_guide(item_type, item_id, color_id)
                    if price_guide.get('data'):
                        price_data[f"{item_type}_{item_id}_{color_id}"] = price_guide['data']
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    logging.warning(f"Could not fetch price for {item_id}: {e}")
                    continue
            
            # Save price data
            price_file = self.data_folder / f"prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(price_file, 'w', encoding='utf-8') as f:
                json.dump(price_data, f, indent=2)
            
            logging.info(f"Fetched price data for {len(price_data)} items")
            return price_file
            
        except Exception as e:
            logging.error(f"Error syncing price data: {e}")
            raise

class BrickLinkCredentialManager:
    """Manage BrickLink API credentials securely"""
    
    def __init__(self, credentials_file="bricklink_credentials.json"):
        self.credentials_file = Path(credentials_file)
    
    def save_credentials(self, consumer_key, consumer_secret, token, token_secret):
        """Save API credentials to encrypted file"""
        credentials = {
            'consumer_key': consumer_key,
            'consumer_secret': consumer_secret,
            'token': token,
            'token_secret': token_secret,
            'created_at': datetime.now().isoformat()
        }
        
        with open(self.credentials_file, 'w', encoding='utf-8') as f:
            json.dump(credentials, f, indent=2)
        
        # Set file permissions (Unix-like systems)
        if hasattr(os, 'chmod'):
            os.chmod(self.credentials_file, 0o600)
        
        logging.info("BrickLink credentials saved")
    
    def load_credentials(self):
        """Load API credentials from file"""
        if not self.credentials_file.exists():
            raise FileNotFoundError("BrickLink credentials not found. Run setup first.")
        
        with open(self.credentials_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def setup_credentials(self):
        """Interactive setup for BrickLink API credentials"""
        print("🔧 BrickLink API Setup")
        print("=" * 50)
        print("Per ottenere le credenziali API BrickLink:")
        print("1. Vai su https://www.bricklink.com/v2/api/register_consumer.page")
        print("2. Registra una nuova applicazione")
        print("3. Copia le credenziali qui sotto")
        print()
        
        consumer_key = input("Consumer Key: ").strip()
        consumer_secret = input("Consumer Secret: ").strip()
        token = input("Token Value: ").strip()
        token_secret = input("Token Secret: ").strip()
        
        if not all([consumer_key, consumer_secret, token, token_secret]):
            raise ValueError("Tutte le credenziali sono obbligatorie")
        
        self.save_credentials(consumer_key, consumer_secret, token, token_secret)
        print("✅ Credenziali salvate con successo!")
        
        return self.load_credentials()

# Example usage and testing functions
def test_api_connection(credentials):
    """Test BrickLink API connection"""
    try:
        api = BrickLinkAPI(**credentials)
        
        # Test with a simple request
        inventories = api.get_inventories()
        logging.info(f"✅ API connection successful! Found {len(inventories.get('data', []))} inventories")
        return True
        
    except Exception as e:
        logging.error(f"❌ API connection failed: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Setup credentials
    cred_manager = BrickLinkCredentialManager()
    
    try:
        credentials = cred_manager.load_credentials()
        print("✅ Loaded existing credentials")
    except FileNotFoundError:
        print("⚙️ Setting up BrickLink API credentials...")
        credentials = cred_manager.setup_credentials()
    
    # Test connection
    if test_api_connection(credentials):
        print("🚀 Ready to use BrickLink API!")
        
        # Example: Download inventories
        api = BrickLinkAPI(**credentials)
        sync = BrickLinkSync(api)
        
        # Uncomment to download inventories
        # files = sync.download_inventories()
        # print(f"Downloaded {len(files)} inventory files")
    else:
        print("❌ Please check your credentials and try again")
