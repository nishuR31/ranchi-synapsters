import networkx as nx
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict
import logging
from datetime import datetime
from app.database.graph import Neo4jConnection
from app.models.schemas import (
    FraudRing, Kingpin, EntityTimeline, TimelineEvent,
    AnomalyDetection, RiskAssessment, RiskLevel,
    GraphSnapshot, GraphNode, GraphEdge
)

logger = logging.getLogger(__name__)

class IntelligenceEngine:
    """Cybercrime Network Intelligence Engine"""
    
    def __init__(self, db: Neo4jConnection):
        self.db = db

    def get_graph_snapshot(self, limit: int = 400) -> GraphSnapshot:
        """Return a trimmed graph snapshot for visualization"""
        query = """
        MATCH (n)-[r]->(m)
        WHERE type(r) IN ['MADE','SENT','USES','OWNS','RUNS_ON','HAS_SIM','CONNECTS_VIA','INVOLVED_IN']
        RETURN id(n) as source_id,
               id(m) as target_id,
               labels(n)[0] as source_label,
               labels(m)[0] as target_label,
               coalesce(n.phone_number, n.account_number, n.device_id, n.sim_number, n.person_id, n.ip_address, n.complaint_id, toString(id(n))) as source_entity,
               coalesce(m.phone_number, m.account_number, m.device_id, m.sim_number, m.person_id, m.ip_address, m.complaint_id, toString(id(m))) as target_entity,
               type(r) as relation,
               r.amount as amount,
               r.duration as duration,
               r.timestamp as timestamp
        LIMIT $limit
        """

        records = self.db.execute_query(query, {"limit": limit})

        nodes: Dict[str, GraphNode] = {}
        edges: List[GraphEdge] = []
        degree: Dict[str, int] = defaultdict(int)

        for record in records:
            source_id = str(record.get("source_id"))
            target_id = str(record.get("target_id"))
            source_entity = record.get("source_entity", "unknown")
            target_entity = record.get("target_entity", "unknown")
            source_label = record.get("source_label", "Unknown")
            target_label = record.get("target_label", "Unknown")
            relation = record.get("relation", "RELATED")
            amount = record.get("amount")
            duration = record.get("duration")
            timestamp = record.get("timestamp")

            if source_id not in nodes:
                nodes[source_id] = GraphNode(
                    id=source_id,
                    label=source_label,
                    entity_id=source_entity,
                    metadata={"entity": source_entity}
                )
            if target_id not in nodes:
                nodes[target_id] = GraphNode(
                    id=target_id,
                    label=target_label,
                    entity_id=target_entity,
                    metadata={"entity": target_entity}
                )

            degree[source_id] += 1
            degree[target_id] += 1

            weight = 1.0
            if amount:
                weight = float(amount)
            elif duration:
                weight = float(duration)

            edges.append(GraphEdge(
                source=source_id,
                target=target_id,
                relation=relation,
                weight=weight,
                metadata={"amount": amount, "duration": duration, "timestamp": timestamp}
            ))

        # Assign risk levels based on degree heuristics
        for node_id, node in nodes.items():
            deg = degree.get(node_id, 0)
            node.degree = deg
            if deg > 15:
                node.risk_level = RiskLevel.HIGH
            elif deg > 8:
                node.risk_level = RiskLevel.MEDIUM
            else:
                node.risk_level = RiskLevel.LOW

        logger.info(f"✓ Graph snapshot built with {len(nodes)} nodes and {len(edges)} edges")
        return GraphSnapshot(nodes=list(nodes.values()), edges=edges)
    
    def detect_fraud_rings(self, ring_type: Optional[str] = None) -> List[FraudRing]:
        """Detect fraud rings using Louvain clustering on call/transaction networks"""
        try:
            # Get network data from Neo4j
            query = """
            MATCH (n1)-[r]->(n2)
            WHERE type(r) IN ['MADE', 'SENT']
            RETURN n1.phone_number as from_node, n2.phone_number as to_node, 
                   type(r) as relation_type, r.amount as amount, 
                   r.duration as duration, r.timestamp as timestamp
            UNION ALL
            MATCH (b1:BankAccount)-[r:SENT]->(b2:BankAccount)
            RETURN b1.account_number as from_node, b2.account_number as to_node,
                   type(r) as relation_type, r.amount as amount,
                   r.duration as duration, r.timestamp as timestamp
            """
            
            records = self.db.execute_query(query)
            
            # Build NetworkX graph
            G = nx.DiGraph()
            total_money = defaultdict(float)
            call_counts = defaultdict(int)
            
            for record in records:
                from_node = record.get('from_node', '')
                to_node = record.get('to_node', '')
                relation = record.get('relation_type', '')
                
                G.add_edge(from_node, to_node, weight=1)
                
                if relation == 'SENT':
                    amount = record.get('amount', 0)
                    total_money[f"{from_node}-{to_node}"] += amount
                elif relation == 'MADE':
                    call_counts[f"{from_node}-{to_node}"] += 1
            
            # Detect communities
            if G.number_of_nodes() > 0:
                undirected_G = G.to_undirected()
                communities = list(nx.community.greedy_modularity_communities(undirected_G))
            else:
                communities = []
            
            fraud_rings = []
            for i, community in enumerate(communities):
                if len(community) > 1:
                    subgraph = G.subgraph(community)
                    
                    # Calculate ring characteristics
                    total_calls = sum(call_counts[f"{u}-{v}"] for u, v in subgraph.edges())
                    total_moved = sum(total_money[f"{u}-{v}"] for u, v in subgraph.edges())
                    
                    # Risk scoring
                    node_count = len(community)
                    risk_score = min(100, (node_count * 10) + (total_calls / 10) + (total_moved / 1000))
                    
                    # Determine ring type
                    if total_moved > 100000:
                        ring_type_detected = "money_laundering"
                    elif total_calls > 500:
                        ring_type_detected = "call_center"
                    else:
                        ring_type_detected = "sim_mule"
                    
                    fraud_rings.append(FraudRing(
                        ring_id=f"ring_{i}",
                        member_count=len(community),
                        members=list(community),
                        total_calls=total_calls,
                        total_money_moved=total_moved,
                        risk_score=risk_score,
                        ring_type=ring_type_detected,
                        confidence=min(0.99, len(community) / 100)
                    ))
            
            logger.info(f"✓ Detected {len(fraud_rings)} fraud rings")
            return fraud_rings
        
        except Exception as e:
            logger.error(f"Fraud ring detection failed: {e}")
            raise
    
    def detect_kingpins(self, top_k: int = 10) -> List[Kingpin]:
        """Identify kingpins using PageRank and centrality measures"""
        try:
            query = """
            MATCH (n)-[r]->(m)
            WHERE type(r) IN ['MADE', 'SENT', 'USES', 'OWNS', 'RUNS_ON']
            RETURN n.phone_number as from_node, m.phone_number as to_node,
                   n.account_number as from_acc, m.account_number as to_acc,
                   type(r) as relation
            """
            
            records = self.db.execute_query(query)
            
            # Build NetworkX graph
            G = nx.DiGraph()
            for record in records:
                from_node = record.get('from_node') or record.get('from_acc') or 'unknown'
                to_node = record.get('to_node') or record.get('to_acc') or 'unknown'
                G.add_edge(from_node, to_node)
            
            if G.number_of_nodes() == 0:
                return []
            
            # Calculate centrality measures
            pagerank = nx.pagerank(G)
            betweenness = nx.betweenness_centrality(G)
            in_degree = dict(G.in_degree())
            out_degree = dict(G.out_degree())
            
            # Identify kingpins
            kingpins_data = []
            for node in G.nodes():
                influence = (
                    pagerank.get(node, 0) * 0.4 +
                    betweenness.get(node, 0) * 0.3 +
                    (in_degree.get(node, 0) / max(in_degree.values()) if max(in_degree.values()) > 0 else 0) * 0.15 +
                    (out_degree.get(node, 0) / max(out_degree.values()) if max(out_degree.values()) > 0 else 0) * 0.15
                )
                
                kingpins_data.append({
                    'entity_id': node,
                    'influence': influence,
                    'pagerank': pagerank.get(node, 0),
                    'betweenness': betweenness.get(node, 0),
                    'connections': in_degree.get(node, 0) + out_degree.get(node, 0)
                })
            
            # Sort and get top K
            kingpins_data.sort(key=lambda x: x['influence'], reverse=True)
            kingpins_data = kingpins_data[:top_k]
            
            kingpins = []
            for data in kingpins_data:
                risk_level = RiskLevel.HIGH if data['influence'] > 0.5 else RiskLevel.MEDIUM if data['influence'] > 0.2 else RiskLevel.LOW
                
                kingpins.append(Kingpin(
                    entity_id=data['entity_id'],
                    entity_type="phone" if data['entity_id'].startswith('+') else "account",
                    influence_score=data['influence'],
                    pagerank_score=data['pagerank'],
                    betweenness_centrality=data['betweenness'],
                    connections=data['connections'],
                    risk_level=risk_level,
                    connected_rings=[]
                ))
            
            logger.info(f"✓ Identified {len(kingpins)} kingpins")
            return kingpins
        
        except Exception as e:
            logger.error(f"Kingpin detection failed: {e}")
            raise
    
    def get_timeline(self, entity_id: str) -> EntityTimeline:
        """Reconstruct chronological timeline for an entity"""
        try:
            query = """
            MATCH (n {phone_number: $entity_id})-[r]-(m)
            RETURN type(r) as relation, 
                   m.phone_number as to_entity,
                   r.timestamp as timestamp,
                   r.duration as duration,
                   r.amount as amount,
                   r.call_id as call_id,
                   r.transaction_id as transaction_id
            UNION ALL
            MATCH (n {account_number: $entity_id})-[r]-(m)
            RETURN type(r) as relation,
                   m.account_number as to_entity,
                   r.timestamp as timestamp,
                   r.amount as amount,
                   r.transaction_id as transaction_id,
                   NULL as duration,
                   NULL as call_id
            ORDER BY timestamp DESC
            """
            
            records = self.db.execute_query(query, {'entity_id': entity_id})
            
            events = []
            for record in records:
                relation = record.get('relation', '')
                timestamp = record.get('timestamp', datetime.now().isoformat())
                to_entity = record.get('to_entity', 'unknown')
                
                # Map relation to event type
                if relation == 'MADE':
                    event_type = "call"
                    details = {
                        'call_id': record.get('call_id'),
                        'duration_seconds': record.get('duration')
                    }
                elif relation == 'SENT':
                    event_type = "transaction"
                    details = {
                        'transaction_id': record.get('transaction_id'),
                        'amount': record.get('amount')
                    }
                elif relation == 'HAS_SIM':
                    event_type = "sim_swap"
                    details = {'sim_id': to_entity}
                elif relation == 'RUNS_ON':
                    event_type = "device_change"
                    details = {'device_id': to_entity}
                elif relation == 'CONNECTS_VIA':
                    event_type = "ip_change"
                    details = {'ip_address': to_entity}
                else:
                    event_type = relation.lower()
                    details = {}
                
                events.append(TimelineEvent(
                    timestamp=timestamp,
                    event_type=event_type,
                    from_entity=entity_id,
                    to_entity=to_entity,
                    details=details
                ))
            
            return EntityTimeline(
                entity_id=entity_id,
                entity_type="phone" if entity_id.startswith('+') else "account",
                events=events,
                event_count=len(events)
            )
        
        except Exception as e:
            logger.error(f"Timeline reconstruction failed: {e}")
            raise
    
    def assess_risk(self, entity_id: str) -> RiskAssessment:
        """Comprehensive risk assessment for an entity"""
        try:
            # Get entity connections
            query = """
            MATCH (n)
            WHERE n.phone_number = $entity_id OR n.account_number = $entity_id
            OPTIONAL MATCH (n)-[r]-(m)
            RETURN count(distinct m) as connection_count,
                   collect(type(r)) as relation_types
            """
            
            result = self.db.execute_query(query, {'entity_id': entity_id})
            connection_count = result[0].get('connection_count', 0) if result else 0
            
            # Get timeline
            timeline = self.get_timeline(entity_id)
            
            # Calculate risk factors
            factors = {
                'connection_count': min(100, connection_count * 10),
                'event_count': min(100, timeline.event_count * 5),
                'network_density': min(100, (connection_count / max(1, timeline.event_count)) * 20)
            }
            
            # Aggregate risk score
            risk_score = sum(factors.values()) / len(factors)
            
            # Determine risk level
            if risk_score > 70:
                risk_level = RiskLevel.HIGH
            elif risk_score > 40:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            # Generate recommendations
            recommendations = []
            if risk_score > 70:
                recommendations.append("Immediate investigation recommended")
                recommendations.append("Monitor all associated entities")
                recommendations.append("Block suspicious accounts")
            elif risk_score > 40:
                recommendations.append("Enhanced monitoring advised")
                recommendations.append("Review recent transactions")
            
            return RiskAssessment(
                entity_id=entity_id,
                entity_type="phone" if entity_id.startswith('+') else "account",
                risk_level=risk_level,
                risk_score=risk_score,
                factors=factors,
                recommendations=recommendations,
                last_updated=datetime.now().isoformat()
            )
        
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            raise
    
    def detect_anomalies(self, entity_id: str) -> List[AnomalyDetection]:
        """Detect anomalous patterns"""
        try:
            timeline = self.get_timeline(entity_id)
            anomalies = []
            
            # Check for SIM swapping
            sim_swaps = [e for e in timeline.events if e.event_type == 'sim_swap']
            if len(sim_swaps) > 2:
                anomalies.append(AnomalyDetection(
                    entity_id=entity_id,
                    anomaly_type="sim_swap",
                    confidence=min(1.0, len(sim_swaps) / 5),
                    risk_level=RiskLevel.HIGH,
                    timestamp=datetime.now().isoformat(),
                    details={'swap_count': len(sim_swaps)}
                ))
            
            # Check for device hopping
            device_changes = [e for e in timeline.events if e.event_type == 'device_change']
            if len(device_changes) > 3:
                anomalies.append(AnomalyDetection(
                    entity_id=entity_id,
                    anomaly_type="device_hop",
                    confidence=min(1.0, len(device_changes) / 6),
                    risk_level=RiskLevel.HIGH,
                    timestamp=datetime.now().isoformat(),
                    details={'device_change_count': len(device_changes)}
                ))
            
            # Check for call bursts
            calls = [e for e in timeline.events if e.event_type == 'call']
            if len(calls) > 100:
                anomalies.append(AnomalyDetection(
                    entity_id=entity_id,
                    anomaly_type="call_burst",
                    confidence=min(1.0, len(calls) / 500),
                    risk_level=RiskLevel.MEDIUM,
                    timestamp=datetime.now().isoformat(),
                    details={'call_count': len(calls)}
                ))
            
            # Check for high-velocity transactions
            transactions = [e for e in timeline.events if e.event_type == 'transaction']
            total_amount = sum(float(e.details.get('amount', 0)) for e in transactions)
            if total_amount > 500000:
                anomalies.append(AnomalyDetection(
                    entity_id=entity_id,
                    anomaly_type="money_movement",
                    confidence=min(1.0, total_amount / 1000000),
                    risk_level=RiskLevel.HIGH,
                    timestamp=datetime.now().isoformat(),
                    details={'total_amount': total_amount, 'transaction_count': len(transactions)}
                ))
            
            logger.info(f"✓ Detected {len(anomalies)} anomalies for {entity_id}")
            return anomalies
        
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            raise
