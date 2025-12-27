
from fastapi import APIRouter, Path, Query, HTTPException
from typing import List, Optional
import logging

from database.graph import get_db
from services.intelligence import IntelligenceEngine
from models.schemas import (
    FraudRing,
    Kingpin,
    EntityTimeline,
    AnomalyDetection,
    RiskAssessment,
    GraphSnapshot,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/intelligence",
    tags=["Cybercrime Intelligence"],
)

# -------------------------------------------------------------------
# Graph snapshot
# -------------------------------------------------------------------
@router.get("/graph", response_model=GraphSnapshot, summary="Graph snapshot")
async def get_graph_snapshot(
    limit: int = Query(400, ge=50, le=1000, description="Max relationships to include")
):
    try:
        db = get_db()
        engine = IntelligenceEngine(db)
        return engine.get_graph_snapshot(limit=limit)
    except Exception as e:
        logger.error(f"Graph snapshot failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------------
# Fraud rings
# -------------------------------------------------------------------
@router.get("/clusters", response_model=List[FraudRing], summary="Detect fraud rings")
async def get_fraud_rings(
    ring_type: Optional[str] = Query(
        None, description="Filter by: sim_mule, call_center, money_laundering"
    )
):
    try:
        db = get_db()
        engine = IntelligenceEngine(db)
        return engine.detect_fraud_rings(ring_type) or []
    except Exception as e:
        logger.error(f"Cluster detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------------
# Kingpins
# -------------------------------------------------------------------
@router.get("/kingpins", response_model=List[Kingpin], summary="Identify network kingpins")
async def get_kingpins(
    top_k: int = Query(10, ge=1, le=100, description="Return top K kingpins")
):
    try:
        db = get_db()
        engine = IntelligenceEngine(db)
        return engine.detect_kingpins(top_k)
    except Exception as e:
        logger.error(f"Kingpin detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------------
# Timeline
# -------------------------------------------------------------------
@router.get("/timeline/{entity_id}", response_model=EntityTimeline, summary="Get entity timeline")
async def get_timeline(
    entity_id: str = Path(..., description="Phone number (E.164) or account number")
):
    try:
        db = get_db()
        engine = IntelligenceEngine(db)
        return engine.get_timeline(entity_id)
    except Exception as e:
        logger.error(f"Timeline retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------------
# Risk
# -------------------------------------------------------------------
@router.get("/risk/{entity_id}", response_model=RiskAssessment, summary="Risk assessment")
async def assess_risk(
    entity_id: str = Path(..., description="Phone number (E.164) or account number")
):
    try:
        db = get_db()
        engine = IntelligenceEngine(db)
        return engine.assess_risk(entity_id)
    except Exception as e:
        logger.error(f"Risk assessment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------------
# Anomalies
# -------------------------------------------------------------------
@router.get("/anomalies/{entity_id}", response_model=List[AnomalyDetection], summary="Detect anomalies")
async def get_anomalies(
    entity_id: str = Path(..., description="Phone number (E.164) or account number")
):
    try:
        db = get_db()
        engine = IntelligenceEngine(db)
        return engine.detect_anomalies(entity_id)
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
