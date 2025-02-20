import pandas as pd
import json
from pathlib import Path
import sqlite3
from datetime import datetime
import csv
from typing import List, Dict, Any
import shutil

class DataManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.backup_dir = Path.home() / '.chiropractic_app' / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, report_type: str, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Generate various types of reports"""
        reports = {
            'patient_summary': self._patient_summary_report,
            'appointment_history': self._appointment_history_report,
            'financial_summary': self._financial_summary_report,
            'treatment_outcomes': self._treatment_outcomes_report
        }
        
        if report_type not in reports:
            raise ValueError(f"Unknown report type: {report_type}")
            
        return reports[report_type](parameters or {})
    
    def export_data(self, data: pd.DataFrame, format: str, filepath: str, options: Dict[str, Any] = None):
        """Export data to various formats"""
        options = options or {}
        
        if format.lower() == 'excel':
            self._export_excel(data, filepath, options)
        elif format.lower() == 'csv':
            self._export_csv(data, filepath, options)
        elif format.lower() == 'json':
            self._export_json(data, filepath, options)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_data(self, filepath: str, import_type: str, options: Dict[str, Any] = None) -> pd.DataFrame:
        """Import data from various formats"""
        options = options or {}
        
        # Validate file exists
        if not Path(filepath).exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Determine file type from extension
        ext = Path(filepath).suffix.lower()
        
        if ext == '.xlsx':
            data = pd.read_excel(filepath, **options)
        elif ext == '.csv':
            data = pd.read_csv(filepath, **options)
        elif ext == '.json':
            data = pd.read_json(filepath, **options)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
        
        # Validate imported data
        self._validate_import(data, import_type)
        
        return data
    
    def create_backup(self, backup_type: str = 'full') -> str:
        """Create a backup of the database"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f"backup_{backup_type}_{timestamp}.db"
        
        # Create backup
        shutil.copy2(self.db_path, backup_path)
        
        return str(backup_path)
    
    def restore_backup(self, backup_path: str):
        """Restore database from backup"""
        if not Path(backup_path).exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        # Verify backup integrity
        try:
            conn = sqlite3.connect(backup_path)
            conn.close()
        except sqlite3.Error:
            raise ValueError("Invalid backup file")
        
        # Create backup of current database before restore
        self.create_backup(backup_type='pre_restore')
        
        # Restore backup
        shutil.copy2(backup_path, self.db_path)
    
    def _patient_summary_report(self, parameters: Dict[str, Any]) -> pd.DataFrame:
        """Generate patient summary report"""
        query = """
        SELECT 
            p.id,
            p.first_name,
            p.last_name,
            p.gender,
            p.age,
            p.phone,
            p.email,
            p.registration_date,
            COUNT(DISTINCT a.id) as total_appointments,
            MAX(a.appointment_date) as last_appointment
        FROM patients p
        LEFT JOIN appointments_{current_month} a ON p.id = a.patient_id
        GROUP BY p.id
        """
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn)
    
    def _appointment_history_report(self, parameters: Dict[str, Any]) -> pd.DataFrame:
        """Generate appointment history report"""
        date_from = parameters.get('date_from', '1900-01-01')
        date_to = parameters.get('date_to', '2100-12-31')
        
        query = """
        SELECT 
            a.appointment_date,
            a.appointment_time,
            a.status,
            p.first_name,
            p.last_name,
            p.phone
        FROM appointments_{current_month} a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.appointment_date BETWEEN ? AND ?
        ORDER BY a.appointment_date, a.appointment_time
        """
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn, params=[date_from, date_to])
    
    def _financial_summary_report(self, parameters: Dict[str, Any]) -> pd.DataFrame:
        """Generate financial summary report"""
        # Implementation depends on financial tracking features
        pass
    
    def _treatment_outcomes_report(self, parameters: Dict[str, Any]) -> pd.DataFrame:
        """Generate treatment outcomes report"""
        query = """
        SELECT 
            p.first_name,
            p.last_name,
            sh.session_date,
            sh.treatment_notes,
            sh.follow_up_instructions
        FROM session_history sh
        JOIN patients p ON sh.patient_id = p.id
        ORDER BY sh.session_date DESC
        """
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn)
    
    def _export_excel(self, data: pd.DataFrame, filepath: str, options: Dict[str, Any]):
        """Export data to Excel format"""
        writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
        data.to_excel(writer, index=False, **options)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Sheet1']
        for idx, col in enumerate(data.columns):
            max_length = max(
                data[col].astype(str).apply(len).max(),
                len(str(col))
            ) + 2
            worksheet.set_column(idx, idx, max_length)
        
        writer.close()
    
    def _export_csv(self, data: pd.DataFrame, filepath: str, options: Dict[str, Any]):
        """Export data to CSV format"""
        data.to_csv(filepath, index=False, **options)
    
    def _export_json(self, data: pd.DataFrame, filepath: str, options: Dict[str, Any]):
        """Export data to JSON format"""
        data.to_json(filepath, orient='records', **options)
    
    def _validate_import(self, data: pd.DataFrame, import_type: str):
        """Validate imported data structure"""
        required_columns = {
            'patients': ['first_name', 'last_name', 'gender', 'age', 'phone'],
            'appointments': ['patient_id', 'appointment_date', 'appointment_time', 'status'],
            'session_history': ['patient_id', 'session_date', 'treatment_notes']
        }
        
        if import_type not in required_columns:
            raise ValueError(f"Unknown import type: {import_type}")
            
        missing_columns = set(required_columns[import_type]) - set(data.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
            
        # Additional validation based on import type
        if import_type == 'patients':
            if not data['phone'].str.match(r'^\+?1?\d{9,15}$').all():
                raise ValueError("Invalid phone number format in data")
            if not data['age'].between(0, 150).all():
                raise ValueError("Invalid age values in data")
            if not data['gender'].isin(['Male', 'Female', 'Other']).all():
                raise ValueError("Invalid gender values in data") 