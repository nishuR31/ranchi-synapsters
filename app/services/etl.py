import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime
import logging
import re
from app.database.graph import Neo4jConnection

logger = logging.getLogger(__name__)

class DataNormalizer:
    """Normalize and deduplicate entity data"""
    
    @staticmethod
    def normalize_phone(phone: str) -> str:
        """Normalize phone number to E.164 format"""
        phone = re.sub(r'\D', '', str(phone))
        if len(phone) == 10:
            return f"+91{phone}"
        elif len(phone) == 12 and phone.startswith('91'):
            return f"+{phone}"
        elif len(phone) == 13 and phone.startswith('+91'):
            return phone
        return f"+91{phone[-10:]}"
    
    @staticmethod
    def normalize_account(account: str) -> str:
        """Normalize bank account number"""
        return str(account).strip().upper()
    
    @staticmethod
    def normalize_device_id(device_id: str) -> str:
        """Normalize device identifier"""
        return str(device_id).strip().upper()
    
    @staticmethod
    def normalize_ip(ip: str) -> str:
        """Validate and normalize IP address"""
        return str(ip).strip()

class ETLPipeline:
    """ETL Pipeline for ingesting cybercrime data"""
    
    def __init__(self, db: Neo4jConnection):
        self.db = db
        self.normalizer = DataNormalizer()
    
    def ingest_call_records(self, filepath: str) -> Dict:
        """Ingest CDR (Call Detail Records) data"""
        try:
            df = pd.read_csv(filepath)
            stats = {"inserted": 0, "updated": 0, "errors": 0}
            
            for _, row in df.iterrows():
                try:
                    from_phone = self.normalizer.normalize_phone(row['from_phone'])
                    to_phone = self.normalizer.normalize_phone(row['to_phone'])
                    
                    query = """
                    MERGE (p1:Phone {phone_number: $from_phone})
                    MERGE (p2:Phone {phone_number: $to_phone})
                    MERGE (p1)-[c:MADE {
                        call_id: $call_id,
                        duration: $duration,
                        timestamp: $timestamp,
                        call_type: $call_type
                    }]->(p2)
                    RETURN c
                    """
                    
                    result = self.db.execute_query(query, {
                        'from_phone': from_phone,
                        'to_phone': to_phone,
                        'call_id': str(row.get('call_id', 'call_' + str(row.name))),
                        'duration': int(row.get('duration_seconds', 0)),
                        'timestamp': str(row.get('timestamp', datetime.now().isoformat())),
                        'call_type': str(row.get('call_type', 'outgoing'))
                    })
                    
                    stats["inserted"] += 1
                except Exception as e:
                    logger.warning(f"Error processing call record: {e}")
                    stats["errors"] += 1
            
            logger.info(f"✓ CDR ingestion complete: {stats}")
            return stats
        
        except Exception as e:
            logger.error(f"CDR ingestion failed: {e}")
            raise
    
    def ingest_transactions(self, filepath: str) -> Dict:
        """Ingest bank transaction data"""
        try:
            df = pd.read_csv(filepath)
            stats = {"inserted": 0, "updated": 0, "errors": 0}
            
            for _, row in df.iterrows():
                try:
                    from_acc = self.normalizer.normalize_account(row['from_account'])
                    to_acc = self.normalizer.normalize_account(row['to_account'])
                    
                    query = """
                    MERGE (b1:BankAccount {account_number: $from_acc})
                    MERGE (b2:BankAccount {account_number: $to_acc})
                    MERGE (b1)-[t:SENT {
                        transaction_id: $transaction_id,
                        amount: $amount,
                        timestamp: $timestamp,
                        transaction_type: $transaction_type
                    }]->(b2)
                    RETURN t
                    """
                    
                    self.db.execute_query(query, {
                        'from_acc': from_acc,
                        'to_acc': to_acc,
                        'transaction_id': str(row.get('transaction_id', 'txn_' + str(row.name))),
                        'amount': float(row.get('amount', 0)),
                        'timestamp': str(row.get('timestamp', datetime.now().isoformat())),
                        'transaction_type': str(row.get('transaction_type', 'transfer'))
                    })
                    
                    stats["inserted"] += 1
                except Exception as e:
                    logger.warning(f"Error processing transaction: {e}")
                    stats["errors"] += 1
            
            logger.info(f"✓ Transaction ingestion complete: {stats}")
            return stats
        
        except Exception as e:
            logger.error(f"Transaction ingestion failed: {e}")
            raise
    
    def ingest_devices(self, filepath: str) -> Dict:
        """Ingest device and IP mapping data"""
        try:
            df = pd.read_csv(filepath)
            stats = {"inserted": 0, "updated": 0, "errors": 0}
            
            for _, row in df.iterrows():
                try:
                    device_id = self.normalizer.normalize_device_id(row['device_id'])
                    ip = self.normalizer.normalize_ip(row['ip_address'])
                    phone = self.normalizer.normalize_phone(row.get('phone_number', ''))
                    
                    query = """
                    MERGE (d:Device {device_id: $device_id})
                    SET d.device_type = $device_type, d.imei = $imei
                    MERGE (i:IP {ip_address: $ip})
                    MERGE (d)-[:CONNECTS_VIA {timestamp: $timestamp}]->(i)
                    """
                    
                    if phone:
                        query += """
                        MERGE (p:Phone {phone_number: $phone})
                        MERGE (p)-[:RUNS_ON]->(d)
                        """
                    
                    self.db.execute_query(query, {
                        'device_id': device_id,
                        'ip': ip,
                        'phone': phone,
                        'device_type': str(row.get('device_type', 'unknown')),
                        'imei': str(row.get('imei', 'unknown')),
                        'timestamp': str(row.get('timestamp', datetime.now().isoformat()))
                    })
                    
                    stats["inserted"] += 1
                except Exception as e:
                    logger.warning(f"Error processing device: {e}")
                    stats["errors"] += 1
            
            logger.info(f"✓ Device ingestion complete: {stats}")
            return stats
        
        except Exception as e:
            logger.error(f"Device ingestion failed: {e}")
            raise
    
    def ingest_sims(self, filepath: str) -> Dict:
        """Ingest SIM card data"""
        try:
            df = pd.read_csv(filepath)
            stats = {"inserted": 0, "updated": 0, "errors": 0}
            
            for _, row in df.iterrows():
                try:
                    sim_number = str(row['sim_number']).strip()
                    phone = self.normalizer.normalize_phone(row.get('phone_number', ''))
                    
                    query = """
                    MERGE (s:SIM {sim_number: $sim_number})
                    SET s.provider = $provider, s.activation_date = $activation_date
                    """
                    
                    if phone:
                        query += """
                        MERGE (p:Phone {phone_number: $phone})
                        MERGE (p)-[:HAS_SIM]->(s)
                        """
                    
                    self.db.execute_query(query, {
                        'sim_number': sim_number,
                        'phone': phone,
                        'provider': str(row.get('provider', 'unknown')),
                        'activation_date': str(row.get('activation_date', datetime.now().isoformat()))
                    })
                    
                    stats["inserted"] += 1
                except Exception as e:
                    logger.warning(f"Error processing SIM: {e}")
                    stats["errors"] += 1
            
            logger.info(f"✓ SIM ingestion complete: {stats}")
            return stats
        
        except Exception as e:
            logger.error(f"SIM ingestion failed: {e}")
            raise
    
    def ingest_complaints(self, filepath: str) -> Dict:
        """Ingest complaint/incident reports"""
        try:
            df = pd.read_csv(filepath)
            stats = {"inserted": 0, "updated": 0, "errors": 0}
            
            for _, row in df.iterrows():
                try:
                    person_id = str(row.get('person_id', 'unknown'))
                    
                    query = """
                    MERGE (c:Complaint {complaint_id: $complaint_id})
                    SET c.complaint_type = $complaint_type,
                        c.description = $description,
                        c.timestamp = $timestamp,
                        c.severity = $severity
                    """
                    
                    if person_id != 'unknown':
                        query += """
                        MERGE (p:Person {id: $person_id})
                        MERGE (p)-[:INVOLVED_IN]->(c)
                        """
                    
                    self.db.execute_query(query, {
                        'complaint_id': str(row.get('complaint_id', 'complaint_' + str(row.name))),
                        'person_id': person_id,
                        'complaint_type': str(row.get('complaint_type', 'fraud')),
                        'description': str(row.get('description', '')),
                        'timestamp': str(row.get('timestamp', datetime.now().isoformat())),
                        'severity': str(row.get('severity', 'medium'))
                    })
                    
                    stats["inserted"] += 1
                except Exception as e:
                    logger.warning(f"Error processing complaint: {e}")
                    stats["errors"] += 1
            
            logger.info(f"✓ Complaint ingestion complete: {stats}")
            return stats
        
        except Exception as e:
            logger.error(f"Complaint ingestion failed: {e}")
            raise
