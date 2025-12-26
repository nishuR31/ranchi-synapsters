# 🧠 Ranchi Synapsters – Cybercrime Network Intelligence Engine

> **Production-grade AI backend for detecting organized fraud rings and kingpins in cybercrime hotspots.**

A **network-level cyber-intelligence system** built with FastAPI, Neo4j, and graph machine learning to ingest, analyze, and expose law-enforcement-ready intelligence from CDRs, bank transactions, SIMs, devices, IPs, and complaints.

---

## 🔥 Tech Stack

- **Python 3.10+**
- **FastAPI** – High-performance async web framework
- **Neo4j** – Knowledge graph database
- **PyTorch** – Deep learning
- **PyTorch Geometric** – Graph neural networks
- **NetworkX** – Graph algorithms (Louvain, PageRank, centrality)
- **Pandas** – Data processing
- **Scikit-learn** – ML utilities

---

## 📊 Graph Data Model

### Nodes

```
Person         – Individual entities
Phone          – Phone numbers
SIM            – SIM cards
Device         – Devices (smartphones, laptops)
BankAccount    – Bank accounts
IP             – IP addresses
Call           – Call records
Transaction    – Financial transactions
Complaint      – Complaints/reports
```

### Relationships

```
Person        -[USES]-->          Phone
Phone         -[HAS_SIM]-->       SIM
Phone         -[RUNS_ON]-->       Device
Device        -[CONNECTS_VIA]-->  IP
Person        -[OWNS]-->          BankAccount
BankAccount   -[SENT]-->          Transaction
Transaction   -[TO]-->            BankAccount
Phone         -[MADE]-->          Call
Call          -[TO]-->            Phone
Person        -[INVOLVED_IN]-->   Complaint
```

---

## 🚀 Quick Start

### 1. **Setup Environment**

```bash
cd ranchi-synapsters

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy .env file
cp .env.example .env
```

### 2. **Configure Neo4j**

Update `.env` with your Neo4j instance:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<your-password>
DATABASE_NAME=neo4j
```

> **Local setup:** `docker run -d -p 7687:7687 -p 7474:7474 neo4j`

### 3. **Run Server**

```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server runs at: **http://localhost:8000**

Visit **http://localhost:8000/docs** for interactive API documentation.

### 4. **Launch Frontend Dashboard**

```bash
cd frontend
cp .env.example .env   # adjust VITE_API_BASE if needed
npm install            # or pnpm/yarn
npm run dev            # http://localhost:5173
```

The UI pulls live data from the FastAPI endpoints and renders stats, graph, kingpins, rings, timelines, anomalies, and risk.

---

## 📥 Data Ingestion (ETL)

Upload CSV files to ingest data:

```bash
curl -X POST "http://localhost:8000/api/v1/data/upload?file_type=calls" \
  -H "accept: application/json" \
  -F "file=@cdr_data.csv"
```

### Supported File Types

#### 1. **Calls (CDR)**

```csv
call_id,from_phone,to_phone,duration_seconds,timestamp,call_type
1,9876543210,9123456789,300,2024-01-15T10:30:00,outgoing
2,9123456789,9876543210,150,2024-01-15T11:00:00,incoming
```

#### 2. **Transactions**

```csv
transaction_id,from_account,to_account,amount,timestamp,transaction_type
TXN001,ACC123456,ACC654321,50000,2024-01-15T10:30:00,transfer
TXN002,ACC654321,ACC123456,75000,2024-01-15T11:30:00,transfer
```

#### 3. **Devices**

```csv
device_id,phone_number,ip_address,device_type,imei,timestamp
DEV001,9876543210,192.168.1.100,smartphone,123456789012345,2024-01-15T09:00:00
```

#### 4. **SIMs**

```csv
sim_number,phone_number,provider,activation_date
SIM001,9876543210,Airtel,2024-01-01
SIM002,9123456789,Jio,2024-01-05
```

#### 5. **Complaints**

```csv
complaint_id,person_id,complaint_type,description,timestamp,severity
CMP001,PERSON001,fraud,Unauthorized transactions,2024-01-15T10:00:00,high
CMP002,PERSON002,sim_swap,SIM swapped without consent,2024-01-15T11:00:00,critical
```

---

## 🧠 Intelligence Endpoints

### 1. **Detect Fraud Rings**

```bash
GET /api/v1/intelligence/clusters
GET /api/v1/intelligence/clusters?ring_type=sim_mule
```

**Response:**

```json
[
  {
    "ring_id": "ring_0",
    "member_count": 15,
    "members": ["+919876543210", "+919123456789", ...],
    "total_calls": 2500,
    "total_money_moved": 500000.0,
    "risk_score": 87.5,
    "ring_type": "money_laundering",
    "confidence": 0.95
  }
]
```

### 2. **Identify Kingpins**

```bash
GET /api/v1/intelligence/kingpins?top_k=10
```

**Response:**

```json
[
  {
    "entity_id": "+919876543210",
    "entity_type": "phone",
    "influence_score": 0.89,
    "pagerank_score": 0.045,
    "betweenness_centrality": 0.234,
    "connections": 47,
    "risk_level": "HIGH",
    "connected_rings": ["ring_0", "ring_2"]
  }
]
```

### 3. **Timeline Reconstruction**

```bash
GET /api/v1/intelligence/timeline/+919876543210
```

**Response:**

```json
{
  "entity_id": "+919876543210",
  "entity_type": "phone",
  "events": [
    {
      "timestamp": "2024-01-15T10:30:00",
      "event_type": "call",
      "from_entity": "+919876543210",
      "to_entity": "+919123456789",
      "details": {
        "call_id": "call_1",
        "duration_seconds": 300
      }
    },
    {
      "timestamp": "2024-01-15T11:30:00",
      "event_type": "transaction",
      "from_entity": "+919876543210",
      "to_entity": "ACC654321",
      "details": {
        "transaction_id": "TXN002",
        "amount": 75000.0
      }
    }
  ],
  "event_count": 47
}
```

### 4. **Risk Assessment**

```bash
GET /api/v1/intelligence/risk/+919876543210
```

**Response:**

```json
{
  "entity_id": "+919876543210",
  "entity_type": "phone",
  "risk_level": "HIGH",
  "risk_score": 78.5,
  "factors": {
    "connection_count": 470,
    "event_count": 235,
    "network_density": 94.0
  },
  "recommendations": [
    "Immediate investigation recommended",
    "Monitor all associated entities",
    "Block suspicious accounts"
  ],
  "last_updated": "2024-01-15T12:00:00"
}
```

### 5. **Anomaly Detection**

```bash
GET /api/v1/intelligence/anomalies/+919876543210
```

**Response:**

```json
[
  {
    "entity_id": "+919876543210",
    "anomaly_type": "sim_swap",
    "confidence": 0.92,
    "risk_level": "HIGH",
    "timestamp": "2024-01-15T12:00:00",
    "details": { "swap_count": 5 }
  },
  {
    "entity_id": "+919876543210",
    "anomaly_type": "money_movement",
    "confidence": 0.87,
    "risk_level": "HIGH",
    "timestamp": "2024-01-15T12:00:00",
    "details": {
      "total_amount": 2500000.0,
      "transaction_count": 42
    }
  }
]
```

### 6. **System Health**

```bash
GET /api/v1/system/health
```

### 7. **Graph Statistics**

```bash
GET /api/v1/system/graph/stats
```

---

## 🎯 Key Features

### 🔴 **Fraud Ring Detection**

- **Louvain / Leiden clustering** for community detection
- Identifies SIM mule networks, call centers, money laundering rings
- Risk scoring based on network size, activity volume, and financial movement
- Confidence metrics for each ring

### 👑 **Kingpin Identification**

- **PageRank** for importance ranking
- **Betweenness centrality** for bridge/control nodes
- **Influence scoring** combining multiple factors
- Connected ring association

### 📍 **Timeline Reconstruction**

- Chronological event sequence for any entity
- Call, transaction, SIM swap, device change, IP change events
- Temporal pattern analysis for behavior profiling

### ⚠️ **Anomaly Detection**

- SIM swapping (>2 swaps = suspicious)
- Device hopping (>3 device changes = suspicious)
- Call bursts (>100 calls = burst activity)
- High-velocity money movement (>500k = flag)

### 🎨 **Risk Assessment**

- Multi-factor risk scoring (0-100)
- Risk levels: LOW, MEDIUM, HIGH
- Personalized recommendations
- Real-time factor breakdown

---

## 📦 Project Structure

```
ranchi-synapsters/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Settings
│   ├── database/
│   │   └── graph.py            # Neo4j connection
│   ├── services/
│   │   ├── etl.py              # Data ingestion
│   │   ├── intelligence.py      # AI/ML analysis
│   │   └── __init__.py
│   ├── routes/
│   │   ├── data.py             # Upload endpoints
│   │   ├── intelligence.py      # Intelligence endpoints
│   │   ├── system.py           # System endpoints
│   │   └── __init__.py
│   ├── models/
│   │   ├── schemas.py          # Pydantic models
│   │   └── __init__.py
│   └── __init__.py
├── data/
│   └── uploads/                # CSV upload directory
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔧 Configuration

Edit `.env`:

```env
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
DATABASE_NAME=neo4j

# FastAPI
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
DEBUG=True

# Upload
UPLOAD_DIR=./data/uploads
MAX_UPLOAD_SIZE=104857600  # 100MB
```

---

## 🧪 Testing the System

### 1. **Check Health**

```bash
curl http://localhost:8000/api/v1/system/health
```

### 2. **Upload Sample Data**

```bash
curl -X POST "http://localhost:8000/api/v1/data/upload?file_type=calls" \
  -F "file=@sample_calls.csv"
```

### 3. **Get Fraud Rings**

```bash
curl http://localhost:8000/api/v1/intelligence/clusters
```

### 4. **Get Kingpins**

```bash
curl http://localhost:8000/api/v1/intelligence/kingpins?top_k=5
```

### 5. **Get Timeline**

```bash
curl "http://localhost:8000/api/v1/intelligence/timeline/+919876543210"
```

---

## 📊 Performance & Scalability

- **Neo4j indexes** on all entity IDs for O(1) lookup
- **Graph algorithms** leverage NetworkX (Louvain, PageRank, centrality)
- **Async FastAPI** handles concurrent requests
- **Batch processing** for large CSV imports
- **Connection pooling** for database efficiency

---

## 🛡️ Law Enforcement Ready

✓ Network-level cyber-intelligence  
✓ Real-time anomaly detection  
✓ Explainable risk scoring  
✓ Timeline reconstruction  
✓ Kingpin identification  
✓ Fraud ring mapping  
✓ Actionable recommendations

---

## 📝 License

MIT

---

## 🚀 Next Steps

1. **Docker containerization** – Production deployment
2. **Graph embedding models** – GNN-based entity clustering
3. **Real-time streaming** – Kafka/Redis integration
4. **Advanced ML** – Transfer learning on fraud patterns
5. **Mobile dashboard** – Law enforcement UI
6. **API authentication** – OAuth2 + API keys

---

**Built for Cybercrime Intelligence in Jamtara, Deoghar, and Beyond.**
