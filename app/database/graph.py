# from neo4j import GraphDatabase, Session
# from typing import Optional, List, Dict, Any
# # from app.config import settings
# from config import settings
# import logging

# logger = logging.getLogger(__name__)

# class Neo4jConnection:
#     """Neo4j Graph Database Connection Manager"""
    
#     def __init__(self, uri: str, user: str, password: str, database: str):
#         self.uri = uri
#         self.user = user
#         self.password = password
#         self.database = database
#         self.driver = None
    
#     def connect(self):
#         """Establish connection to Neo4j"""
#         try:
#             self.driver = GraphDatabase.driver(
#                 self.uri,
#                 auth=(self.user, self.password),
#                 encrypted=True
#             )
#             # Verify connection
#             with self.driver.session(database=self.database) as session:
#                 session.run("RETURN 1")
#             logger.info("✓ Connected to Neo4j successfully")
#         except Exception as e:
#             logger.error(f"✗ Failed to connect to Neo4j: {e}")
#             raise
    
#     def close(self):
#         """Close connection"""
#         if self.driver:
#             self.driver.close()
#             logger.info("✓ Neo4j connection closed")
    
#     def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict]:
#         """Execute a Cypher query"""
#         if not self.driver:
#             raise RuntimeError("Database connection not established")
        
#         with self.driver.session(database=self.database) as session:
#             result = session.run(query, params or {})
#             return [record.data() for record in result]
    
#     def create_indexes(self):
#         """Create database indexes for performance"""
#         queries = [
#             "CREATE INDEX person_id IF NOT EXISTS FOR (p:Person) ON (p.id)",
#             "CREATE INDEX phone_id IF NOT EXISTS FOR (p:Phone) ON (p.phone_number)",
#             "CREATE INDEX sim_id IF NOT EXISTS FOR (s:SIM) ON (s.sim_number)",
#             "CREATE INDEX device_id IF NOT EXISTS FOR (d:Device) ON (d.device_id)",
#             "CREATE INDEX ip_id IF NOT EXISTS FOR (i:IP) ON (i.ip_address)",
#             "CREATE INDEX account_id IF NOT EXISTS FOR (b:BankAccount) ON (b.account_number)",
#             "CREATE INDEX complaint_id IF NOT EXISTS FOR (c:Complaint) ON (c.complaint_id)",
#         ]
        
#         for query in queries:
#             try:
#                 self.execute_query(query)
#                 logger.info(f"✓ Index created: {query.split('FOR')[1][:30]}...")
#             except Exception as e:
#                 logger.warning(f"Index creation warning: {e}")

# # Global connection instance
# _neo4j: Optional[Neo4jConnection] = None

# def get_db() -> Neo4jConnection:
#     """Get or create database connection"""
#     global _neo4j
#     if _neo4j is None:
#         _neo4j = Neo4jConnection(
#             uri=settings.neo4j_uri,
#             user=settings.neo4j_user,
#             password=settings.neo4j_password,
#             database=settings.database_name
#         )
#         _neo4j.connect()
#         _neo4j.create_indexes()
#     return _neo4j

# def close_db():
#     """Close database connection"""
#     global _neo4j
#     if _neo4j:
#         _neo4j.close()
#         _neo4j = None


from neo4j import GraphDatabase
from typing import Optional, List, Dict, Any
from config import settings
import logging

logger = logging.getLogger(__name__)

class Neo4jConnection:
    """Neo4j Graph Database Connection Manager (Aura compatible)"""

    def __init__(self, uri: str, user: str, password: str, database: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self.driver = None

    def connect(self):
        """Establish connection to Neo4j Aura"""
        try:
            # DO NOT pass encrypted / ssl / trust for Aura
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
            )

            # Verify connection
            self.driver.verify_connectivity()

            logger.info("✓ Connected to Neo4j Aura successfully")

        except Exception as e:
            logger.error(f"✗ Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        """Close connection"""
        if self.driver:
            self.driver.close()
            logger.info("✓ Neo4j connection closed")

    def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict]:
        """Execute a Cypher query"""
        if not self.driver:
            raise RuntimeError("Database connection not established")

        with self.driver.session(database=self.database) as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]

    def create_indexes(self):
        """Create database indexes for performance"""
        queries = [
            "CREATE INDEX person_id IF NOT EXISTS FOR (p:Person) ON (p.id)",
            "CREATE INDEX phone_id IF NOT EXISTS FOR (p:Phone) ON (p.phone_number)",
            "CREATE INDEX sim_id IF NOT EXISTS FOR (s:SIM) ON (s.sim_number)",
            "CREATE INDEX device_id IF NOT EXISTS FOR (d:Device) ON (d.device_id)",
            "CREATE INDEX ip_id IF NOT EXISTS FOR (i:IP) ON (i.ip_address)",
            "CREATE INDEX account_id IF NOT EXISTS FOR (b:BankAccount) ON (b.account_number)",
            "CREATE INDEX complaint_id IF NOT EXISTS FOR (c:Complaint) ON (c.complaint_id)",
        ]

        for query in queries:
            try:
                self.execute_query(query)
                logger.info(f"✓ Index ensured")
            except Exception as e:
                logger.warning(f"Index creation warning: {e}")


# ------------------------------------------------------------------
# Global connection
# ------------------------------------------------------------------

_neo4j: Optional[Neo4jConnection] = None


def get_db() -> Neo4jConnection:
    global _neo4j

    if _neo4j is None:
        _neo4j = Neo4jConnection(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD,
            database=settings.DATABASE_NAME,
        )
        _neo4j.connect()
        _neo4j.create_indexes()

    return _neo4j


def close_db():
    global _neo4j
    if _neo4j:
        _neo4j.close()
        _neo4j = None
