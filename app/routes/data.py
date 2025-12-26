from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from typing import List
import os
from app.database.graph import get_db
from app.services.etl import ETLPipeline
from app.config import settings
from app.models.schemas import (
    FraudRing, Kingpin, EntityTimeline, AnomalyDetection, RiskAssessment
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/data", tags=["Data Ingestion"])

@router.post("/upload", summary="Upload and ingest cybercrime data")
async def upload_data(
    file_type: str = Query(..., description="Type: calls, transactions, devices, sims, complaints"),
    file: UploadFile = File(...)
):
    """
    Upload CSV data for ETL ingestion
    
    Supported file types:
    - calls: CDR (Call Detail Records)
    - transactions: Bank transactions
    - devices: Device and IP mappings
    - sims: SIM card data
    - complaints: Complaint/incident reports
    """
    try:
        # Validate file type
        if file_type not in ['calls', 'transactions', 'devices', 'sims', 'complaints']:
            raise HTTPException(status_code=400, detail=f"Invalid file_type: {file_type}")
        
        # Save uploaded file
        os.makedirs(settings.upload_dir, exist_ok=True)
        filepath = os.path.join(settings.upload_dir, file.filename)
        
        with open(filepath, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        # Process with ETL pipeline
        db = get_db()
        pipeline = ETLPipeline(db)
        
        if file_type == 'calls':
            result = pipeline.ingest_call_records(filepath)
        elif file_type == 'transactions':
            result = pipeline.ingest_transactions(filepath)
        elif file_type == 'devices':
            result = pipeline.ingest_devices(filepath)
        elif file_type == 'sims':
            result = pipeline.ingest_sims(filepath)
        elif file_type == 'complaints':
            result = pipeline.ingest_complaints(filepath)
        
        return {
            "status": "success",
            "file_type": file_type,
            "filename": file.filename,
            "filepath": filepath,
            "ingestion_result": result
        }
    
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
