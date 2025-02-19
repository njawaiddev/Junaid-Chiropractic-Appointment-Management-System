import os
import json
import shutil
from datetime import datetime, timedelta
import threading
import time

class BackupScheduler:
    def __init__(self, db_manager):
        self.db = db_manager
        self.backup_config_file = os.path.join(self.db._get_app_data_dir(), "backup_config.json")
        self.running = False
        self.thread = None
        self.load_config()
    
    def load_config(self):
        """Load backup configuration"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.backup_config_file), exist_ok=True)
            
            if os.path.exists(self.backup_config_file):
                with open(self.backup_config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    'schedule': 'never',
                    'last_backup': None,
                    'backup_path': os.path.join(self.db._get_app_data_dir(), 'backups')
                }
                self.save_config()
        except Exception as e:
            print(f"Error loading backup config: {str(e)}")
            self.config = {
                'schedule': 'never',
                'last_backup': None,
                'backup_path': os.path.join(self.db._get_app_data_dir(), 'backups')
            }
    
    def start(self):
        """Start the backup scheduler"""
        if not self.running and self.config['schedule'] != 'never':
            self.running = True
            self.thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop the backup scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                self.load_config()  # Reload config to check for changes
                
                if self.config['schedule'] == 'never':
                    self.running = False
                    break
                
                # Check if backup is needed
                if self._is_backup_needed():
                    self._perform_backup()
                
                # Sleep for appropriate interval
                time.sleep(self._get_sleep_interval())
                
            except Exception as e:
                print(f"Error in scheduler loop: {str(e)}")
                time.sleep(3600)  # Sleep for an hour on error
    
    def _is_backup_needed(self):
        """Check if backup is needed based on schedule"""
        if not self.config['last_backup']:
            return True
        
        last_backup = datetime.fromisoformat(self.config['last_backup'])
        now = datetime.now()
        
        if self.config['schedule'] == 'daily':
            return (now - last_backup).days >= 1
        
        elif self.config['schedule'] == 'weekly':
            return (now - last_backup).days >= 7
        
        elif self.config['schedule'] == 'monthly':
            # Check if it's been roughly a month (30 days)
            return (now - last_backup).days >= 30
        
        return False
    
    def _get_sleep_interval(self):
        """Get sleep interval based on schedule"""
        if self.config['schedule'] == 'daily':
            return 3600  # Check every hour
        elif self.config['schedule'] == 'weekly':
            return 3600 * 6  # Check every 6 hours
        elif self.config['schedule'] == 'monthly':
            return 3600 * 12  # Check every 12 hours
        return 3600  # Default to 1 hour
    
    def _perform_backup(self):
        """Perform the actual backup"""
        try:
            # Create backup directory if it doesn't exist
            backup_dir = self.config['backup_path']
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"chiropractic_backup_{timestamp}.db")
            
            # Close any existing database connections
            self.db.close()
            
            # Copy database file
            shutil.copy2(self.db.db_path, backup_file)
            
            # Update last backup time
            self.config['last_backup'] = datetime.now().isoformat()
            self.save_config()
            
            print(f"Automatic backup completed: {backup_file}")
            
        except Exception as e:
            print(f"Error performing automatic backup: {str(e)}")
            
        finally:
            # Ensure we have a database connection
            if not self.db.conn:
                self.db.connect()
    
    def save_config(self):
        """Save backup configuration"""
        try:
            with open(self.backup_config_file, 'w') as f:
                json.dump(self.config, f)
        except Exception as e:
            print(f"Error saving backup config: {str(e)}") 