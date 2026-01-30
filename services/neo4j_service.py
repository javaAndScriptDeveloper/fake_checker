import os
import uuid
from datetime import datetime
from typing import Optional, Tuple

from neo4j import GraphDatabase

from dal.dal import Note, Source
from utils.logger import get_logger

logger = get_logger(__name__)


class Neo4jService:
    """Service for saving notes and sources to Neo4j graph database."""

    def __init__(self, uri: Optional[str] = None,
                 auth: Optional[Tuple[str, str]] = None,
                 database: Optional[str] = None):
        # Read Neo4j config from environment variables if not explicitly provided
        uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        auth = auth or (
            os.getenv("NEO4J_USER", "neo4j"),
            os.getenv("NEO4J_PASSWORD", "your_strong_password"),
        )
        database = database or os.getenv("NEO4J_DATABASE", "neo4j")
        """
        Initialize Neo4j service.
        
        Args:
            uri: Neo4j connection URI
            auth: Tuple of (username, password)
            database: Database name
        """
        self.driver = GraphDatabase.driver(uri, auth=auth)
        self.database = database
        try:
            self.driver.verify_connectivity()
            logger.info("Connection to Neo4j established")
        except Exception as e:
            logger.warning(f"Could not connect to Neo4j: {e}. Neo4j operations will be skipped.")

    def close(self):
        """Close the Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def _execute_write(self, query: str, parameters: Optional[dict] = None):
        """Helper for write operations, ensuring 'w' routing."""
        try:
            records, summary, _ = self.driver.execute_query(
                query, parameters_=parameters, database_=self.database, routing_="w"
            )
            return records, summary
        except Exception as e:
            logger.error(f"Error executing Neo4j write query: {e}", exc_info=True)
            return None, None

    def _execute_read(self, query: str, parameters: Optional[dict] = None) -> Optional[list]:
        """Helper for read operations, ensuring 'r' routing."""
        try:
            records, _, _ = self.driver.execute_query(
                query, parameters_=parameters, database_=self.database, routing_="r"
            )
            return records
        except Exception as e:
            logger.error(f"Error executing Neo4j read query: {e}", exc_info=True)
            return None

    def is_connected(self) -> bool:
        """Check if Neo4j connection is available."""
        try:
            self.driver.verify_connectivity()
            return True
        except Exception:
            return False

    def get_full_network(self, limit: int = 100) -> Optional[dict]:
        """
        Get sources, notes, and all relationships for visualization.

        Args:
            limit: Maximum number of nodes to return

        Returns:
            Dictionary with nodes and edges lists, or None if error
        """
        query = """
        MATCH (s:Source)
        OPTIONAL MATCH (s)-[:PUBLISHED]->(n:Note)
        WITH s, collect(DISTINCT n)[0..$note_limit] AS notes
        UNWIND notes + [null] AS note
        WITH s, note
        WHERE note IS NOT NULL OR NOT EXISTS((s)-[:PUBLISHED]->())
        RETURN
            collect(DISTINCT {
                id: 'source_' + toString(s.postgres_id),
                type: 'source',
                name: s.name,
                platform: s.platform,
                rating: s.rating
            }) AS sources,
            collect(DISTINCT CASE WHEN note IS NOT NULL THEN {
                id: 'note_' + toString(note.postgres_id),
                type: 'note',
                title: COALESCE(note.title, 'Untitled'),
                total_score: note.total_score,
                is_propaganda: note.is_propaganda
            } END) AS notes
        LIMIT 1
        """

        records = self._execute_read(query, {"note_limit": limit})
        if not records:
            return {"nodes": [], "edges": []}

        sources = records[0]["sources"] if records[0]["sources"] else []
        notes = [n for n in records[0]["notes"] if n is not None]
        nodes = sources + notes

        # Get edges (relationships)
        edge_query = """
        MATCH (s:Source)-[:PUBLISHED]->(n:Note)
        RETURN 'source_' + toString(s.postgres_id) AS from_id,
               'note_' + toString(n.postgres_id) AS to_id,
               'PUBLISHED' AS type
        UNION
        MATCH (n:Note)-[:REPOSTS_FROM]->(s:Source)
        RETURN 'note_' + toString(n.postgres_id) AS from_id,
               'source_' + toString(s.postgres_id) AS to_id,
               'REPOSTS_FROM' AS type
        UNION
        MATCH (n1:Note)-[:REFERENCES]->(n2:Note)
        RETURN 'note_' + toString(n1.postgres_id) AS from_id,
               'note_' + toString(n2.postgres_id) AS to_id,
               'REFERENCES' AS type
        """

        edge_records = self._execute_read(edge_query)
        edges = []
        if edge_records:
            for record in edge_records:
                edges.append({
                    "from": record["from_id"],
                    "to": record["to_id"],
                    "type": record["type"]
                })

        return {"nodes": nodes, "edges": edges}

    def get_source_statistics(self) -> Optional[list]:
        """
        Get statistics per source: note count, avg propaganda score, repost count.

        Returns:
            List of source statistics dictionaries, or None if error
        """
        query = """
        MATCH (s:Source)
        OPTIONAL MATCH (s)-[:PUBLISHED]->(n:Note)
        OPTIONAL MATCH (n2:Note)-[:REPOSTS_FROM]->(s)
        WITH s,
             count(DISTINCT n) AS note_count,
             avg(n.total_score) AS avg_score,
             count(DISTINCT n2) AS repost_count
        RETURN s.name AS name,
               s.platform AS platform,
               note_count,
               COALESCE(avg_score, 0) AS avg_propaganda_score,
               repost_count
        ORDER BY note_count DESC
        """

        records = self._execute_read(query)
        if not records:
            return []

        return [
            {
                "name": r["name"],
                "platform": r["platform"],
                "note_count": r["note_count"],
                "avg_propaganda_score": r["avg_propaganda_score"],
                "repost_count": r["repost_count"]
            }
            for r in records
        ]

    def get_repost_chains(self, max_depth: int = 5) -> Optional[list]:
        """
        Get note propagation chains via REFERENCES relationships.

        Args:
            max_depth: Maximum chain depth to traverse

        Returns:
            List of repost chain dictionaries, or None if error
        """
        query = """
        MATCH path = (n1:Note)-[:REFERENCES*1..5]->(n2:Note)
        WHERE length(path) <= $max_depth
        WITH n1, n2, length(path) AS chain_length
        MATCH (s1:Source)-[:PUBLISHED]->(n1)
        MATCH (s2:Source)-[:PUBLISHED]->(n2)
        RETURN n1.title AS reposted_title,
               s1.name AS reposting_source,
               n2.title AS original_title,
               s2.name AS original_source,
               chain_length
        ORDER BY chain_length DESC
        LIMIT 50
        """

        records = self._execute_read(query, {"max_depth": max_depth})
        if not records:
            return []

        return [
            {
                "reposted_title": r["reposted_title"],
                "reposting_source": r["reposting_source"],
                "original_title": r["original_title"],
                "original_source": r["original_source"],
                "chain_length": r["chain_length"]
            }
            for r in records
        ]

    def get_most_influential_sources(self, limit: int = 10) -> Optional[list]:
        """
        Get sources ranked by connection count (published + reposted).

        Args:
            limit: Maximum number of sources to return

        Returns:
            List of influential source dictionaries, or None if error
        """
        query = """
        MATCH (s:Source)
        OPTIONAL MATCH (s)-[:PUBLISHED]->(n:Note)
        OPTIONAL MATCH (n2:Note)-[:REPOSTS_FROM]->(s)
        WITH s,
             count(DISTINCT n) AS published_count,
             count(DISTINCT n2) AS reposted_count,
             avg(n.total_score) AS avg_score
        WITH s, published_count, reposted_count, avg_score,
             published_count + reposted_count AS total_connections
        RETURN s.name AS name,
               s.platform AS platform,
               published_count,
               reposted_count,
               total_connections,
               COALESCE(avg_score, 0) AS avg_propaganda_score
        ORDER BY total_connections DESC
        LIMIT $limit
        """

        records = self._execute_read(query, {"limit": limit})
        if not records:
            return []

        return [
            {
                "name": r["name"],
                "platform": r["platform"],
                "published_count": r["published_count"],
                "reposted_count": r["reposted_count"],
                "total_connections": r["total_connections"],
                "avg_propaganda_score": r["avg_propaganda_score"]
            }
            for r in records
        ]

    def save_source(self, source: Source) -> Optional[str]:
        """
        Save or update a Source in Neo4j.
        
        Args:
            source: Source object to save
            
        Returns:
            UUID of the created/updated source node, or None if error
        """
        query = """
        MERGE (s:Source {postgres_id: $postgres_id})
        ON CREATE SET s.uuid = $uuid,
                      s.created_at = $created_at
        SET s.external_id = $external_id,
            s.platform = $platform,
            s.name = $name,
            s.rating = $rating,
            s.is_hidden = $is_hidden,
            s.updated_at = $updated_at
        RETURN COALESCE(s.uuid, $uuid) AS uuid
        """
        
        source_uuid = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        params = {
            "postgres_id": source.id,
            "external_id": source.external_id,
            "platform": source.platform,
            "name": source.name,
            "rating": float(source.rating) if source.rating is not None else None,
            "is_hidden": source.is_hidden if source.is_hidden is not None else False,
            "uuid": source_uuid,
            "created_at": now,
            "updated_at": now
        }
        
        records, summary = self._execute_write(query, params)
        if records and summary:
            logger.info(f"Saved Source to Neo4j: {source.name} (ID: {source.id})")
            return records[0]["uuid"] if records else source_uuid
        return None

    def save_note(self, note: Note, source: Source, title: Optional[str] = None) -> Optional[str]:
        """
        Save a Note to Neo4j and link it to its Source.
        
        Args:
            note: Note object to save
            source: Source object that published this note
            title: Optional title of the note
            
        Returns:
            UUID of the created note node, or None if error
        """
        # First ensure source exists
        source_uuid = self.save_source(source)
        
        # Create note node
        note_uuid = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Convert datetime objects to ISO strings if they exist
        created_at = note.created_at.isoformat() if note.created_at else now
        updated_at = note.updated_at.isoformat() if note.updated_at else now
        
        query = """
        MERGE (n:Note {postgres_id: $postgres_id})
        ON CREATE SET n.uuid = $uuid,
                      n.created_at = $created_at
        SET n.hash = $hash,
            n.content = $content,
            n.title = $title,
            n.sentimental_score = $sentimental_score,
            n.sentimental_score_raw = $sentimental_score_raw,
            n.sentimental_score_coeff = $sentimental_score_coeff,
            n.triggered_keywords = $triggered_keywords,
            n.triggered_keywords_raw = $triggered_keywords_raw,
            n.triggered_keywords_coeff = $triggered_keywords_coeff,
            n.triggered_topics = $triggered_topics,
            n.triggered_topics_raw = $triggered_topics_raw,
            n.triggered_topics_coeff = $triggered_topics_coeff,
            n.text_simplicity_deviation = $text_simplicity_deviation,
            n.text_simplicity_deviation_raw = $text_simplicity_deviation_raw,
            n.text_simplicity_deviation_coeff = $text_simplicity_deviation_coeff,
            n.confidence_factor = $confidence_factor,
            n.confidence_factor_raw = $confidence_factor_raw,
            n.confidence_factor_coeff = $confidence_factor_coeff,
            n.clickbait = $clickbait,
            n.clickbait_raw = $clickbait_raw,
            n.clickbait_coeff = $clickbait_coeff,
            n.subjective = $subjective,
            n.subjective_raw = $subjective_raw,
            n.subjective_coeff = $subjective_coeff,
            n.call_to_action = $call_to_action,
            n.call_to_action_raw = $call_to_action_raw,
            n.call_to_action_coeff = $call_to_action_coeff,
            n.repeated_take = $repeated_take,
            n.repeated_take_raw = $repeated_take_raw,
            n.repeated_take_coeff = $repeated_take_coeff,
            n.repeated_note = $repeated_note,
            n.repeated_note_raw = $repeated_note_raw,
            n.repeated_note_coeff = $repeated_note_coeff,
            n.messianism = $messianism,
            n.messianism_raw = $messianism_raw,
            n.messianism_coeff = $messianism_coeff,
            n.generalization_of_opponents = $generalization_of_opponents,
            n.generalization_of_opponents_raw = $generalization_of_opponents_raw,
            n.generalization_of_opponents_coeff = $generalization_of_opponents_coeff,
            n.opposition_to_opponents = $opposition_to_opponents,
            n.opposition_to_opponents_raw = $opposition_to_opponents_raw,
            n.opposition_to_opponents_coeff = $opposition_to_opponents_coeff,
            n.total_score = $total_score,
            n.total_score_raw = $total_score_raw,
            n.total_score_coeff = $total_score_coeff,
            n.cosine_similarity = $cosine_similarity,
            n.cosine_similarity_raw = $cosine_similarity_raw,
            n.cosine_similarity_coeff = $cosine_similarity_coeff,
            n.fehner_type = $fehner_type,
            n.is_propaganda = $is_propaganda,
            n.reason = $reason,
            n.amount_of_propaganda_scores = $amount_of_propaganda_scores,
            n.updated_at = $updated_at
        WITH n
        MATCH (s:Source {postgres_id: $source_id})
        MERGE (s)-[:PUBLISHED]->(n)
        RETURN COALESCE(n.uuid, $uuid) AS uuid
        """
        
        def safe_float(value):
            """Safely convert value to float, handling None."""
            if value is None:
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        
        def safe_bool(value):
            """Safely convert value to boolean, handling None."""
            if value is None:
                return None
            return bool(value)
        
        params = {
            "postgres_id": note.id,
            "uuid": note_uuid,
            "hash": note.hash,
            "content": note.content,
            "title": title or "",
            "sentimental_score": safe_float(note.sentimental_score),
            "sentimental_score_raw": safe_float(note.sentimental_score_raw),
            "sentimental_score_coeff": safe_float(note.sentimental_score_coeff),
            "triggered_keywords": safe_float(note.triggered_keywords),
            "triggered_keywords_raw": safe_float(note.triggered_keywords_raw),
            "triggered_keywords_coeff": safe_float(note.triggered_keywords_coeff),
            "triggered_topics": safe_float(note.triggered_topics),
            "triggered_topics_raw": safe_float(note.triggered_topics_raw),
            "triggered_topics_coeff": safe_float(note.triggered_topics_coeff),
            "text_simplicity_deviation": safe_float(note.text_simplicity_deviation),
            "text_simplicity_deviation_raw": safe_float(note.text_simplicity_deviation_raw),
            "text_simplicity_deviation_coeff": safe_float(note.text_simplicity_deviation_coeff),
            "confidence_factor": safe_float(note.confidence_factor),
            "confidence_factor_raw": safe_float(note.confidence_factor_raw),
            "confidence_factor_coeff": safe_float(note.confidence_factor_coeff),
            "clickbait": safe_float(note.clickbait),
            "clickbait_raw": safe_float(note.clickbait_raw),
            "clickbait_coeff": safe_float(note.clickbait_coeff),
            "subjective": safe_float(note.subjective),
            "subjective_raw": safe_float(note.subjective_raw),
            "subjective_coeff": safe_float(note.subjective_coeff),
            "call_to_action": safe_float(note.call_to_action),
            "call_to_action_raw": safe_float(note.call_to_action_raw),
            "call_to_action_coeff": safe_float(note.call_to_action_coeff),
            "repeated_take": safe_float(note.repeated_take),
            "repeated_take_raw": safe_float(note.repeated_take_raw),
            "repeated_take_coeff": safe_float(note.repeated_take_coeff),
            "repeated_note": safe_float(note.repeated_note),
            "repeated_note_raw": safe_float(note.repeated_note_raw),
            "repeated_note_coeff": safe_float(note.repeated_note_coeff),
            "messianism": safe_float(note.messianism),
            "messianism_raw": safe_float(note.messianism_raw),
            "messianism_coeff": safe_float(note.messianism_coeff),
            "generalization_of_opponents": safe_float(note.generalization_of_opponents),
            "generalization_of_opponents_raw": safe_float(note.generalization_of_opponents_raw),
            "generalization_of_opponents_coeff": safe_float(note.generalization_of_opponents_coeff),
            "opposition_to_opponents": safe_float(note.opposition_to_opponents),
            "opposition_to_opponents_raw": safe_float(note.opposition_to_opponents_raw),
            "opposition_to_opponents_coeff": safe_float(note.opposition_to_opponents_coeff),
            "total_score": safe_float(note.total_score),
            "total_score_raw": safe_float(note.total_score_raw),
            "total_score_coeff": safe_float(note.total_score_coeff),
            "cosine_similarity": safe_float(note.cosine_similarity),
            "cosine_similarity_raw": safe_float(note.cosine_similarity_raw),
            "cosine_similarity_coeff": safe_float(note.cosine_similarity_coeff),
            "fehner_type": note.fehner_type,
            "is_propaganda": safe_bool(note.is_propaganda),
            "reason": note.reason,
            "amount_of_propaganda_scores": safe_float(note.amount_of_propaganda_scores),
            "created_at": created_at,
            "updated_at": updated_at,
            "source_id": source.id
        }
        
        records, summary = self._execute_write(query, params)
        if records and summary:
            note_uuid_result = records[0]["uuid"] if records else note_uuid
            logger.info(f"Saved Note to Neo4j: {title or 'Untitled'} (ID: {note.id})")
            
            # Create REPOST relationship if this note reposts from another source
            if note.reposted_from_source_id:
                self._create_repost_relationship(note.id, note.reposted_from_source_id)
                self._link_to_original_note(note.id, note.reposted_from_source_id)
            
            return note_uuid_result
        return None
    
    def _link_to_original_note(self, note_id: int, original_source_id: int):
        """
        Attempt to link a reposted note to the actual note it's referencing, 
        if that original note was published by the original source.
        """
        query = """
        MATCH (new_note:Note {postgres_id: $note_id})
        MATCH (old_note:Note)-[:PUBLISHED]-(s:Source {postgres_id: $original_source_id})
        WHERE old_note.hash = new_note.hash AND old_note.postgres_id <> new_note.postgres_id
        MERGE (new_note)-[:REFERENCES]->(old_note)
        """
        params = {"note_id": note_id, "original_source_id": original_source_id}
        self._execute_write(query, params)

    def _create_repost_relationship(self, reposting_note_id: int, reposted_source_id: int):
        """
        Create a REPOST relationship between a note and the source it reposted from in Neo4j.
        
        Args:
            reposting_note_id: ID of the note that is reposting
            reposted_source_id: ID of the source that was reposted from
        """
        query = """
        MATCH (reposting:Note {postgres_id: $reposting_id})
        MATCH (reposted_source:Source {postgres_id: $reposted_source_id})
        MERGE (reposting)-[r:REPOSTS_FROM]->(reposted_source)
        SET r.created_at = $created_at
        RETURN r
        """
        
        params = {
            "reposting_id": reposting_note_id,
            "reposted_source_id": reposted_source_id,
            "created_at": datetime.now().isoformat()
        }
        
        records, summary = self._execute_write(query, params)
        if records and summary:
            logger.info(f"Created REPOST relationship: Note {reposting_note_id} -> Source {reposted_source_id}")
        else:
            logger.warning(f"Could not create REPOST relationship between note {reposting_note_id} and source {reposted_source_id}")

