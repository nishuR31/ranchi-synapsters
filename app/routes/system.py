from fastapi import APIRouter, HTTPException
from app.database.graph import get_db
from app.models.schemas import GraphStats, HealthCheck
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/system", tags=["System"])

@router.get("/health", response_model=HealthCheck, summary="Health check")
async def health_check():
    """System health check endpoint"""
    try:
        db = get_db()
        
        # Test database connection
        result = db.execute_query("RETURN 1 as status")
        neo4j_connected = len(result) > 0
        
        return HealthCheck(
            status="operational" if neo4j_connected else "degraded",
            neo4j_connected=neo4j_connected,
            message="System is operational" if neo4j_connected else "Database connection failed"
        )
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheck(
            status="down",
            neo4j_connected=False,
            message=f"System error: {str(e)}"
        )

@router.get("/graph/stats", response_model=GraphStats, summary="Graph statistics")
async def get_graph_stats():
    """Get statistics about the knowledge graph"""
    try:
        db = get_db()
        
        # Get node counts
        node_query = """
        CALL db.labels() YIELD label
        RETURN label, count(*) as count
        """
        
        node_results = db.execute_query("""
        MATCH (n)
        RETURN labels(n)[0] as node_type, count(*) as count
        GROUP BY labels(n)[0]
        """)
        
        node_breakdown = {}
        total_nodes = 0
        for result in node_results:
            node_type = result.get('node_type', 'Unknown')
            count = result.get('count', 0)
            node_breakdown[node_type] = count
            total_nodes += count
        
        # Get relationship counts
        rel_results = db.execute_query("""
        MATCH ()-[r]-()
        RETURN type(r) as rel_type, count(*) as count
        GROUP BY type(r)
        """)
        
        relationship_breakdown = {}
        total_rels = 0
        for result in rel_results:
            rel_type = result.get('rel_type', 'Unknown')
            count = result.get('count', 0)
            relationship_breakdown[rel_type] = count
            total_rels += count
        
        # Calculate density
        if total_nodes > 1:
            max_edges = total_nodes * (total_nodes - 1)
            density = total_rels / max_edges if max_edges > 0 else 0
        else:
            density = 0
        
        return GraphStats(
            total_nodes=total_nodes,
            total_relationships=total_rels,
            node_breakdown=node_breakdown,
            relationship_breakdown=relationship_breakdown,
            density=min(1.0, density)
        )
    
    except Exception as e:
        logger.error(f"Graph stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
