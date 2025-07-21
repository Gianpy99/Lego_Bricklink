"""
Email Notification System for LEGO Analysis
Automated alerts for missing parts, price changes, and inventory updates
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from typing import List, Dict, Optional
import threading
import schedule
import time

class EmailConfig:
    """Email configuration management"""
    
    def __init__(self, config_file="email_config.json"):
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """Load email configuration from file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
                self.smtp_port = config.get('smtp_port', 587)
                self.sender_email = config.get('sender_email', '')
                self.sender_password = config.get('sender_password', '')
                self.recipients = config.get('recipients', [])
                self.enabled = config.get('enabled', False)
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default email configuration"""
        default_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "",
            "sender_password": "",
            "recipients": [],
            "enabled": False,
            "notifications": {
                "missing_parts": True,
                "price_alerts": True,
                "inventory_updates": True,
                "weekly_summary": True
            },
            "thresholds": {
                "min_missing_parts": 5,
                "price_change_percentage": 10.0,
                "max_missing_value": 100.0
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        
        logging.info(f"Created default email config: {self.config_file}")
        self.load_config()
    
    def update_config(self, **kwargs):
        """Update email configuration"""
        try:
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            
            config.update(kwargs)
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            
            self.load_config()
            logging.info("Email configuration updated")
            return True
            
        except Exception as e:
            logging.error(f"Error updating email config: {e}")
            return False

class EmailTemplates:
    """Email template management"""
    
    @staticmethod
    def missing_parts_alert(collection_name: str, missing_items: List[Dict]) -> Dict[str, str]:
        """Generate missing parts alert email"""
        
        html_items = ""
        total_missing = 0
        
        for item in missing_items[:20]:  # Limit to top 20
            html_items += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{item['item_id']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{item['color_name']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">{item['quantity']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">€{item.get('estimated_price', 'N/A')}</td>
            </tr>
            """
            total_missing += item['quantity']
        
        subject = f"🧱 LEGO Alert: {len(missing_items)} pezzi mancanti in {collection_name}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #d50000 0%, #ff5722 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">🧱 LEGO Collection Alert</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Pezzi mancanti rilevati</p>
                </div>
                
                <div style="background: white; padding: 20px; border: 1px solid #ddd; border-top: none;">
                    <h2 style="color: #d50000; margin-top: 0;">Collezione: {collection_name}</h2>
                    
                    <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <strong>⚠️ Riepilogo:</strong><br>
                        • {len(missing_items)} tipi di pezzi mancanti<br>
                        • {total_missing} pezzi totali richiesti<br>
                        • Valore stimato: €{sum(item.get('estimated_price', 0) * item['quantity'] for item in missing_items):.2f}
                    </div>
                    
                    <h3>Top Pezzi Mancanti:</h3>
                    <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                        <thead>
                            <tr style="background: #f8f9fa;">
                                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">ID Pezzo</th>
                                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Colore</th>
                                <th style="padding: 10px; border: 1px solid #ddd; text-align: center;">Quantità</th>
                                <th style="padding: 10px; border: 1px solid #ddd; text-align: right;">Prezzo Est.</th>
                            </tr>
                        </thead>
                        <tbody>
                            {html_items}
                        </tbody>
                    </table>
                    
                    {"<p><em>... e altri pezzi. Vedi dashboard per lista completa.</em></p>" if len(missing_items) > 20 else ""}
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="http://localhost:5000/dashboard" 
                           style="background: #d50000; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            🔍 Visualizza Dashboard Completa
                        </a>
                    </div>
                </div>
                
                <div style="background: #f8f9fa; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #666;">
                    <p>Questo messaggio è stato generato automaticamente dal sistema LEGO Analysis.<br>
                    Per disattivare le notifiche, aggiorna le impostazioni nella dashboard.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        LEGO Collection Alert: {collection_name}
        
        Pezzi mancanti rilevati: {len(missing_items)}
        Quantità totale richiesta: {total_missing}
        
        Top pezzi mancanti:
        """ + "\n".join([f"• {item['item_id']} ({item['color_name']}): {item['quantity']}" for item in missing_items[:10]])
        
        return {
            'subject': subject,
            'html_body': html_body,
            'text_body': text_body
        }
    
    @staticmethod
    def price_alert(items_with_changes: List[Dict]) -> Dict[str, str]:
        """Generate price change alert email"""
        
        html_items = ""
        for item in items_with_changes[:15]:
            change_color = "#d4edda" if item['price_change'] < 0 else "#f8d7da"
            change_icon = "📉" if item['price_change'] < 0 else "📈"
            
            html_items += f"""
            <tr style="background: {change_color};">
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{item['item_id']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">€{item['old_price']:.2f}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">€{item['new_price']:.2f}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">
                    {change_icon} {item['price_change']:+.1f}%
                </td>
            </tr>
            """
        
        subject = f"💰 LEGO Alert: Variazioni prezzi su {len(items_with_changes)} pezzi"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">💰 LEGO Price Alert</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Variazioni prezzi significative</p>
                </div>
                
                <div style="background: white; padding: 20px; border: 1px solid #ddd; border-top: none;">
                    <h2 style="color: #ff9800; margin-top: 0;">Variazioni Prezzi Rilevate</h2>
                    
                    <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                        <thead>
                            <tr style="background: #f8f9fa;">
                                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Pezzo</th>
                                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Prezzo Precedente</th>
                                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Nuovo Prezzo</th>
                                <th style="padding: 10px; border: 1px solid #ddd; text-align: center;">Variazione</th>
                            </tr>
                        </thead>
                        <tbody>
                            {html_items}
                        </tbody>
                    </table>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="http://localhost:5000/dashboard" 
                           style="background: #ff9800; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            📊 Visualizza Trend Prezzi
                        </a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        LEGO Price Alert
        
        Variazioni prezzi rilevate su {len(items_with_changes)} pezzi.
        
        Maggiori dettagli disponibili nella dashboard.
        """
        
        return {
            'subject': subject,
            'html_body': html_body,
            'text_body': text_body
        }
    
    @staticmethod
    def weekly_summary(collections_data: Dict) -> Dict[str, str]:
        """Generate weekly summary email"""
        
        total_collections = len(collections_data)
        total_items = sum(c.get('total_items', 0) for c in collections_data.values())
        avg_completion = sum(c.get('completion_percentage', 0) for c in collections_data.values()) / total_collections if total_collections > 0 else 0
        
        collections_html = ""
        for name, data in collections_data.items():
            status_color = "#d4edda" if data['completion_percentage'] > 80 else "#fff3cd" if data['completion_percentage'] > 50 else "#f8d7da"
            
            collections_html += f"""
            <tr style="background: {status_color};">
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{name}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">{data['total_items']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">{data['completion_percentage']:.1f}%</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">{data.get('missing_count', 0)}</td>
            </tr>
            """
        
        subject = f"📊 LEGO Weekly Summary - {total_collections} collezioni"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">📊 LEGO Weekly Summary</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Settimana del {datetime.now().strftime('%d/%m/%Y')}</p>
                </div>
                
                <div style="background: white; padding: 20px; border: 1px solid #ddd; border-top: none;">
                    <div style="display: flex; justify-content: space-around; margin: 20px 0; text-align: center;">
                        <div>
                            <h3 style="margin: 0; color: #0d47a1;">{total_collections}</h3>
                            <small>Collezioni</small>
                        </div>
                        <div>
                            <h3 style="margin: 0; color: #388e3c;">{total_items:,}</h3>
                            <small>Elementi Totali</small>
                        </div>
                        <div>
                            <h3 style="margin: 0; color: #ff9800;">{avg_completion:.1f}%</h3>
                            <small>Completamento Medio</small>
                        </div>
                    </div>
                    
                    <h3>Stato Collezioni:</h3>
                    <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                        <thead>
                            <tr style="background: #f8f9fa;">
                                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Collezione</th>
                                <th style="padding: 10px; border: 1px solid #ddd; text-align: center;">Elementi</th>
                                <th style="padding: 10px; border: 1px solid #ddd; text-align: center;">Completamento</th>
                                <th style="padding: 10px; border: 1px solid #ddd; text-align: center;">Mancanti</th>
                            </tr>
                        </thead>
                        <tbody>
                            {collections_html}
                        </tbody>
                    </table>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="http://localhost:5000/dashboard" 
                           style="background: #0d47a1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            🔍 Visualizza Dashboard Completa
                        </a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        LEGO Weekly Summary
        
        Statistiche settimana del {datetime.now().strftime('%d/%m/%Y')}:
        • {total_collections} collezioni attive
        • {total_items:,} elementi totali
        • {avg_completion:.1f}% completamento medio
        
        Visualizza i dettagli completi nella dashboard.
        """
        
        return {
            'subject': subject,
            'html_body': html_body,
            'text_body': text_body
        }

class EmailNotificationSystem:
    """Main email notification system"""
    
    def __init__(self, analytics_db="analytics.db"):
        self.config = EmailConfig()
        self.analytics_db = analytics_db
        self.scheduler_running = False
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def send_email(self, to_emails: List[str], subject: str, html_body: str, text_body: str = None, attachments: List[str] = None) -> bool:
        """Send email notification"""
        
        if not self.config.enabled:
            self.logger.info("Email notifications disabled")
            return False
        
        if not self.config.sender_email or not self.config.sender_password:
            self.logger.error("Email credentials not configured")
            return False
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.config.sender_email
            message["To"] = ", ".join(to_emails)
            
            # Add text and HTML parts
            if text_body:
                text_part = MIMEText(text_body, "plain")
                message.attach(text_part)
            
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        message.attach(part)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.config.sender_email, self.config.sender_password)
                text = message.as_string()
                server.sendmail(self.config.sender_email, to_emails, text)
            
            self.logger.info(f"Email sent successfully to {to_emails}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    def check_missing_parts(self):
        """Check for collections with significant missing parts"""
        try:
            conn = sqlite3.connect(self.analytics_db)
            cursor = conn.cursor()
            
            # Get collections with many missing items
            cursor.execute("""
                SELECT c.id, c.name, COUNT(i.id) as missing_count
                FROM collections c
                JOIN items i ON c.id = i.collection_id
                WHERE i.min_qty > 0
                GROUP BY c.id, c.name
                HAVING missing_count >= ?
            """, (self.config.thresholds.get('min_missing_parts', 5),))
            
            collections_with_missing = cursor.fetchall()
            
            for collection_id, collection_name, missing_count in collections_with_missing:
                # Get detailed missing items
                cursor.execute("""
                    SELECT item_id, color_id, min_qty, category
                    FROM items
                    WHERE collection_id = ? AND min_qty > 0
                    ORDER BY min_qty DESC
                    LIMIT 50
                """, (collection_id,))
                
                missing_items = [
                    {
                        'item_id': row[0],
                        'color_name': row[1],
                        'quantity': row[2],
                        'category': row[3],
                        'estimated_price': 0.50  # Mock price
                    }
                    for row in cursor.fetchall()
                ]
                
                if missing_items:
                    email_content = EmailTemplates.missing_parts_alert(collection_name, missing_items)
                    self.send_email(
                        self.config.recipients,
                        email_content['subject'],
                        email_content['html_body'],
                        email_content['text_body']
                    )
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error checking missing parts: {e}")
    
    def send_weekly_summary(self):
        """Send weekly collection summary"""
        try:
            conn = sqlite3.connect(self.analytics_db)
            cursor = conn.cursor()
            
            # Get all collections with stats
            cursor.execute("""
                SELECT c.id, c.name, c.total_items, c.completion_percentage,
                       COUNT(CASE WHEN i.min_qty > 0 THEN 1 END) as missing_count
                FROM collections c
                LEFT JOIN items i ON c.id = i.collection_id
                GROUP BY c.id, c.name, c.total_items, c.completion_percentage
            """)
            
            collections_data = {}
            for row in cursor.fetchall():
                collections_data[row[1]] = {
                    'id': row[0],
                    'total_items': row[2],
                    'completion_percentage': row[3],
                    'missing_count': row[4]
                }
            
            if collections_data:
                email_content = EmailTemplates.weekly_summary(collections_data)
                self.send_email(
                    self.config.recipients,
                    email_content['subject'],
                    email_content['html_body'],
                    email_content['text_body']
                )
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error sending weekly summary: {e}")
    
    def start_scheduler(self):
        """Start scheduled email notifications"""
        if self.scheduler_running:
            return
        
        # Schedule notifications
        schedule.every().day.at("09:00").do(self.check_missing_parts)
        schedule.every().monday.at("08:00").do(self.send_weekly_summary)
        
        self.scheduler_running = True
        
        def run_scheduler():
            while self.scheduler_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        self.logger.info("Email scheduler started")
    
    def stop_scheduler(self):
        """Stop scheduled email notifications"""
        self.scheduler_running = False
        schedule.clear()
        self.logger.info("Email scheduler stopped")
    
    def test_email_configuration(self) -> bool:
        """Test email configuration"""
        test_content = {
            'subject': 'LEGO System - Test Email',
            'html_body': '''
            <html>
            <body>
                <h2>🧱 LEGO Analysis System</h2>
                <p>Questo è un messaggio di test per verificare la configurazione email.</p>
                <p>Se ricevi questo messaggio, la configurazione è corretta!</p>
            </body>
            </html>
            ''',
            'text_body': 'LEGO Analysis System - Messaggio di test configurazione email.'
        }
        
        return self.send_email(
            self.config.recipients,
            test_content['subject'],
            test_content['html_body'],
            test_content['text_body']
        )

# Configuration utility functions
def setup_email_notifications():
    """Interactive setup for email notifications"""
    print("🔧 Configurazione Notifiche Email LEGO")
    print("=" * 50)
    
    config = EmailConfig()
    
    # Basic configuration
    sender_email = input("Email mittente (Gmail): ").strip()
    sender_password = input("Password app Gmail: ").strip()
    
    recipients = []
    while True:
        recipient = input("Email destinatario (Enter per finire): ").strip()
        if not recipient:
            break
        recipients.append(recipient)
    
    # Update configuration
    config.update_config(
        sender_email=sender_email,
        sender_password=sender_password,
        recipients=recipients,
        enabled=True
    )
    
    # Test configuration
    notification_system = EmailNotificationSystem()
    print("\n📧 Test invio email...")
    if notification_system.test_email_configuration():
        print("✅ Configurazione email completata con successo!")
    else:
        print("❌ Errore nella configurazione email. Verifica le credenziali.")
    
    return config

if __name__ == '__main__':
    # Interactive setup
    setup_email_notifications()
    
    # Start notification system
    notification_system = EmailNotificationSystem()
    notification_system.start_scheduler()
    
    print("📧 Sistema di notifiche email avviato!")
    print("📅 Notifiche programmate:")
    print("   • Controllo pezzi mancanti: ogni giorno alle 09:00")
    print("   • Riepilogo settimanale: ogni lunedì alle 08:00")
    print("   • Test email: comando test disponibile")
    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        notification_system.stop_scheduler()
        print("\n📧 Sistema di notifiche fermato.")
