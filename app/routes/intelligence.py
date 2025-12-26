from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from app.database.graph import get_db
from app.services.intelligence import IntelligenceEngine
from app.models.schemas import (
    FraudRing, Kingpin, EntityTimeline, AnomalyDetection, RiskAssessment, GraphSnapshot
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/intelligence", tags=["Cybercrime Intelligence"])

@router.get("/graph", response_model=GraphSnapshot, summary="Graph snapshot")
async def get_graph_snapshot(limit: int = Query(400, ge=50, le=1000, description="Max relationships to include")):
    """Return nodes and edges for visualization without overloading the UI"""
    try:
        db = get_db()
        engine = IntelligenceEngine(db)
        return engine.get_graph_snapshot(limit=limit)
    except Exception as e:
        logger.error(f"Graph snapshot failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clusters", response_model=List[FraudRing], summary="Detect fraud rings")
async def get_fraud_rings(
    ring_type: Optional[str] = Query(None, description="Filter by: sim_mule, call_center, money_laundering")
):
    """
    Detect and return organized fraud rings in the network
    
    Uses Louvain clustering + graph community detection to identify:
    - SIM mule networks
    - Call center fraud operations
    - Money laundering rings
    """
    try:
        db = get_db()
        engine = IntelligenceEngine(db)
        rings = engine.detect_fraud_rings(ring_type)
        
        if not rings:
            return []
        
        return rings
    
    except Exception as e:
        logger.error(f"Cluster detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kingpins", response_model=List[Kingpin], summary="Identify network kingpins")
async def get_kingpins(
    top_k: int = Query(10, ge=1, le=100, description="Return top K kingpins")
):
    """
    Identify the most influential entities (kingpins) in the cybercrime network
    
    Uses:
    - PageRank centrality
    - Betweenness centrality
    - In-degree/Out-degree analysis
    - Influence scoring
    """
    try:
        db = get_db()
        engine = IntelligenceEngine(db)
        kingpins = engine.detect_kingpins(top_k)
        
        return kingpins
    
    except Exception as e:
        logger.error(f"Kingpin detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/timeline/{entity_id}", response_model=EntityTimeline, summary="Get entity timeline")
async def get_timeline(
    entity_id: str = Query(..., description="Phone number (E.164) or account number")
):
    """
    Reconstruct chronological timeline of activities for a given entity
    
    Shows:
    - Calls made/received
    - Transactions sent/received
    - SIM swaps
    - Device changes
    - IP address changes
    """
    try:
        db = get_db()
        engine = IntelligenceEngine(db)
        timeline = engine.get_timeline(entity_id)
        
        return timeline
    
    except Exception as e:
        logger.error(f"Timeline retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk/{entity_id}", response_model=RiskAssessment, summary="Risk assessment")
async def assess_risk(
    entity_id: str = Query(..., description="Phone number (E.164) or account number")
):
    """
    Comprehensive risk assessment for an entity
    
    Factors considered:
    - Network connectivity
    - Activity patterns
    - Anomaly indicators
    - Historical behavior
    
    Risk levels: LOW, MEDIUM, HIGH
    """
    try:
        db = get_db()
        engine = IntelligenceEngine(db)
        assessment = engine.assess_risk(entity_id)
        
        return assessment
    
    except Exception as e:
        logger.error(f"Risk assessment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/anomalies/{entity_id}", response_model=List[AnomalyDetection], summary="Detect anomalies")
async def get_anomalies(
    entity_id: str = Query(..., description="Phone number (E.164) or account number")
):
    """
    Detect anomalous patterns for an entity
    
    Detects:
    - SIM swapping (>2 swaps)
    - Device hopping (>3 device changes)
    - Call bursts (>100 calls)
    - High-velocity money movement (>500k)
    """
    try:
        db = get_db()
        engine = IntelligenceEngine(db)
        anomalies = engine.detect_anomalies(entity_id)
        
        return anomalies
    
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
