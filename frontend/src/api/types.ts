export type RiskLevel = "LOW" | "MEDIUM" | "HIGH";

export interface GraphNode {
  id: string;
  label: string;
  entity_id: string;
  risk_level?: RiskLevel;
  degree: number;
  metadata: Record<string, unknown>;
}

export interface GraphEdge {
  source: string;
  target: string;
  relation: string;
  weight: number;
  metadata: Record<string, unknown>;
}

export interface GraphSnapshot {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface GraphStats {
  total_nodes: number;
  total_relationships: number;
  node_breakdown: Record<string, number>;
  relationship_breakdown: Record<string, number>;
  density: number;
}

export interface FraudRing {
  ring_id: string;
  member_count: number;
  members: string[];
  total_calls: number;
  total_money_moved: number;
  risk_score: number;
  ring_type: string;
  confidence: number;
}

export interface Kingpin {
  entity_id: string;
  entity_type: string;
  influence_score: number;
  pagerank_score: number;
  betweenness_centrality: number;
  connections: number;
  risk_level: RiskLevel;
  connected_rings: string[];
}

export interface TimelineEvent {
  timestamp: string;
  event_type: string;
  from_entity: string;
  to_entity: string;
  details: Record<string, unknown>;
}

export interface EntityTimeline {
  entity_id: string;
  entity_type: string;
  events: TimelineEvent[];
  event_count: number;
}

export interface RiskAssessment {
  entity_id: string;
  entity_type: string;
  risk_level: RiskLevel;
  risk_score: number;
  factors: Record<string, number>;
  recommendations: string[];
  last_updated: string;
}

export interface AnomalyDetection {
  entity_id: string;
  anomaly_type: string;
  confidence: number;
  risk_level: RiskLevel;
  timestamp: string;
  details: Record<string, unknown>;
}
