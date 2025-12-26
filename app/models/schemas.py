from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

# ==================== Input Models ====================

class PersonCreate(BaseModel):
    person_id: str = Field(..., description="Unique person identifier")
    name: Optional[str] = None
    age: Optional[int] = None
    location: Optional[str] = None

class PhoneCreate(BaseModel):
    phone_number: str = Field(..., description="Phone number in E.164 format")
    sim_id: Optional[str] = None
    device_id: Optional[str] = None

class SIMCreate(BaseModel):
    sim_number: str = Field(..., description="SIM serial number")
    provider: Optional[str] = None
    activation_date: Optional[str] = None

class DeviceCreate(BaseModel):
    device_id: str
    device_type: str  # smartphone, laptop, etc.
    imei: Optional[str] = None
    ip_address: Optional[str] = None

class BankAccountCreate(BaseModel):
    account_number: str
    account_holder: str
    bank_name: Optional[str] = None
    balance: float = 0.0

class CallRecordCreate(BaseModel):
    call_id: str
    from_phone: str
    to_phone: str
    duration_seconds: int
    timestamp: str
    call_type: str = "outgoing"  # incoming, outgoing

class TransactionCreate(BaseModel):
    transaction_id: str
    from_account: str
    to_account: str
    amount: float
    timestamp: str
    transaction_type: str = "transfer"

class ComplaintCreate(BaseModel):
    complaint_id: str
    person_id: str
    complaint_type: str
    description: str
    timestamp: str
    severity: str = "medium"

# ==================== Upload Models ====================

class ETLUpload(BaseModel):
    file_type: str  # "calls", "transactions", "devices", "sims", "complaints"
    filename: str

# ==================== Output Models ====================

class FraudRing(BaseModel):
    ring_id: str
    member_count: int
    members: List[str]
    total_calls: int
    total_money_moved: float
    risk_score: float
    ring_type: str  # "sim_mule", "call_center", "money_laundering"
    confidence: float

class Kingpin(BaseModel):
    entity_id: str
    entity_type: str  # "person", "phone", "account"
    influence_score: float
    pagerank_score: float
    betweenness_centrality: float
    connections: int
    risk_level: RiskLevel
    connected_rings: List[str]

class TimelineEvent(BaseModel):
    timestamp: str
    event_type: str  # "call", "transaction", "sim_swap", "device_change"
    from_entity: str
    to_entity: str
    details: Dict[str, Any]

class EntityTimeline(BaseModel):
    entity_id: str
    entity_type: str
    events: List[TimelineEvent]
    event_count: int

class AnomalyDetection(BaseModel):
    entity_id: str
    anomaly_type: str  # "sim_swap", "device_hop", "call_burst", "money_movement"
    confidence: float
    risk_level: RiskLevel
    timestamp: str
    details: Dict[str, Any]

class RiskAssessment(BaseModel):
    entity_id: str
    entity_type: str
    risk_level: RiskLevel
    risk_score: float  # 0-100
    factors: Dict[str, float]
    recommendations: List[str]
    last_updated: str

class GraphNode(BaseModel):
    id: str
    label: str
    entity_id: str
    risk_level: Optional[RiskLevel] = None
    degree: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str
    weight: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GraphSnapshot(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

class GraphStats(BaseModel):
    total_nodes: int
    total_relationships: int
    node_breakdown: Dict[str, int]
    relationship_breakdown: Dict[str, int]
    density: float

class HealthCheck(BaseModel):
    status: str
    neo4j_connected: bool
    message: str
