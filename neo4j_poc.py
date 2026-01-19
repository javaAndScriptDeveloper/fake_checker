import json
import uuid
from datetime import datetime

from neo4j import GraphDatabase

# --- Configuration (Must match your docker-compose.yml) ---
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "your_strong_password")  # Change this to your actual password
DATABASE = "neo4j"  # Default database name


class NoteManager:
    """Manages CRUD operations for Notes and Authors in Neo4j."""

    def __init__(self, uri, auth, database):
        self.driver = GraphDatabase.driver(uri, auth=auth)
        self.database = database
        self.driver.verify_connectivity()
        print("✅ Connection to Neo4j established.")

    def close(self):
        self.driver.close()
        print("Connection closed.")

    def _execute_write(self, query, parameters=None):
        """Helper for write operations, ensuring 'w' routing."""
        records, summary, _ = self.driver.execute_query(
            query, parameters_=parameters, database_=self.database, routing_="w"
        )
        return summary, records

    def _execute_read(self, query, parameters=None):
        """Helper for read operations, ensuring 'r' routing."""
        records, _, _ = self.driver.execute_query(
            query, parameters_=parameters, database_=self.database, routing_="r"
        )
        return records

    # --- CRUD Operations ---

    def create_author(self, name):
        """Create or find an Author node."""
        query = """
        MERGE (a:Author {name: $name})
        RETURN a
        """
        _, records = self._execute_write(query, {"name": name})
        print(f"Created/Found Author: {name}")
        return records[0]["a"]["name"]

    def create_note(self, author_name, name, text, ref_note_uuid=None):
        """Create a new Note, link it to an Author, and optionally link to a referenced Note."""
        note_uuid = str(uuid.uuid4())
        creation_date = datetime.now().isoformat()

        query = """
        MATCH (a:Author {name: $author_name})
        CREATE (n:Note {
            uuid: $uuid,
            name: $name,
            text: $text,
            creationDate: $date
        })
        MERGE (a)-[:WROTE]->(n)
        """

        params = {
            "author_name": author_name,
            "uuid": note_uuid,
            "name": name,
            "text": text,
            "date": creation_date
        }

        summary, _ = self._execute_write(query, params)
        print(f"Created Note: '{name}' by {author_name}. Status: {summary.counters.nodes_created} node(s) created.")

        # Add REFERENCES relationship if ref_note_uuid is provided
        if ref_note_uuid:
            self._link_notes(note_uuid, ref_note_uuid)

        return note_uuid

    def _link_notes(self, source_uuid, target_uuid):
        """Creates a REFERENCES relationship between two notes."""
        link_query = """
        MATCH (n1:Note {uuid: $source_uuid}), (n2:Note {uuid: $target_uuid})
        MERGE (n1)-[:REFERENCES]->(n2)
        """
        self._execute_write(link_query, {"source_uuid": source_uuid, "target_uuid": target_uuid})
        print(f"Linked Note {source_uuid[:8]}... REFERENCES Note {target_uuid[:8]}...")

    def read_note(self, note_uuid):
        """Read a Note and its Author/References."""
        query = """
        MATCH (n:Note {uuid: $uuid})<-[:WROTE]-(a:Author)
        OPTIONAL MATCH (n)-[r:REFERENCES]->(ref:Note)
        RETURN n, a.name AS author_name, collect(ref.name) AS references
        """
        records = self._execute_read(query, {"uuid": note_uuid})
        if records:
            record = records[0]
            note = dict(record["n"])
            note["author"] = record["author_name"]
            note["references"] = record["references"]
            return note
        return None

    def update_note_text(self, note_uuid, new_text):
        """Update the text of an existing Note."""
        query = """
        MATCH (n:Note {uuid: $uuid})
        SET n.text = $new_text
        RETURN n
        """
        summary, _ = self._execute_write(query, {"uuid": note_uuid, "new_text": new_text})
        print(f"Updated Note {note_uuid[:8]}... Text modified: {summary.counters.properties_set}")
        return summary.counters.properties_set > 0

    def delete_note(self, note_uuid):
        """Delete a Note and all its relationships."""
        query = """
        MATCH (n:Note {uuid: $uuid})
        DETACH DELETE n
        """
        summary, _ = self._execute_write(query, {"uuid": note_uuid})
        print(f"Deleted Note {note_uuid[:8]}... Nodes deleted: {summary.counters.nodes_deleted}")
        return summary.counters.nodes_deleted > 0

    # --- Visualization and Analytics Queries ---

    def get_notes_network_cypher(self):
        """Cypher query to return a sample graph for visualization in Neo4j Browser."""
        query = """
        MATCH (a:Author)-[:WROTE]->(n:Note)
        OPTIONAL MATCH (n)-[:REFERENCES]->(ref:Note)
        RETURN a, n, ref
        LIMIT 100
        """
        print("\n--- Visualization Query ---")
        print("Run the following Cypher query in the Neo4j Browser/Bloom to see the graph:")
        print("-" * 70)
        print(query)
        print("-" * 70)

        # Optionally, read the data to confirm it's structured for the browser
        records = self._execute_read(query)
        print(f"Query returned {len(records)} records for visualization.")
        return records

    def get_repost_depth_cypher(self):
        """Cypher query to calculate the depth of reposts (chains of REFERENCES)."""
        query = """
        MATCH path = (n:Note)-[:REFERENCES*]->(root:Note)
        WHERE NOT (root)-[:REFERENCES]->()
        RETURN n.name AS Note, root.name AS OriginalPost, length(path) AS Depth
        ORDER BY Depth DESC
        """
        print("\n--- Repost Depth Query ---")
        print("Run the following Cypher query to see the depth of reposts:")
        print("-" * 70)
        print(query)
        print("-" * 70)

        records = self._execute_read(query)
        print(f"Found {len(records)} repost chains.")
        for record in records:
            print(f"Note: '{record['Note']}' is at depth {record['Depth']} from original: '{record['OriginalPost']}'")
        return records


# --- Sample Data and Execution ---

def run_sample_data(manager):
    """Creates sample Authors and Notes."""
    print("\n\n=============== Sample Data Setup ===============")

    # Create Authors
    manager.create_author("Alice")
    manager.create_author("Bob")
    manager.create_author("Alice")  # Should only MERGE one Alice

    # Create Notes
    note1_uuid = manager.create_note("Alice", "Initial Idea", "This is the core concept for the project.")
    note2_uuid = manager.create_note("Bob", "Tech Stack Review", "Suggesting Python/Neo4j for development.")
    # Note 3 references Note 1
    note3_uuid = manager.create_note("Alice", "Project Plan Outline", "Milestones for the next quarter.",
                                     ref_note_uuid=note1_uuid)
    # Note 4 references Note 2
    note4_uuid = manager.create_note("Bob", "Next Steps", "Reviewing Bob's tech stack notes.", ref_note_uuid=note2_uuid)

    # --- Repost Chain Example ---
    manager.create_author("Charlie")
    manager.create_author("Dave")
    manager.create_author("Eve")

    repost1_uuid = manager.create_note("Charlie", "Repost 1", "Charlie reposts Alice's initial idea.", ref_note_uuid=note1_uuid)
    repost2_uuid = manager.create_note("Dave", "Repost 2", "Dave reposts Charlie's repost.", ref_note_uuid=repost1_uuid)
    repost3_uuid = manager.create_note("Eve", "Repost 3", "Eve reposts Dave's repost.", ref_note_uuid=repost2_uuid)

    print("\n=============== CRUD Demonstration ===============")

    # READ Operation
    print("\n-- READ Note 3 (Project Plan Outline) --")
    note3_data = manager.read_note(note3_uuid)
    print(json.dumps(note3_data, indent=2))

    # UPDATE Operation
    print("\n-- UPDATE Note 2 (Tech Stack Review) --")
    manager.update_note_text(note2_uuid, "Suggesting Python/Neo4j is the way to go. We should document this decision.")

    # VERIFY Update
    print("\n-- READ Note 2 to Verify Update --")
    note2_data = manager.read_note(note2_uuid)
    print(f"New Text for Note 2: {note2_data['text']}")

    # DELETE Operation
    print("\n-- DELETE Note 4 (Next Steps) --")
    manager.delete_note(note4_uuid)

    # VERIFY Delete
    print("\n-- VERIFY Delete of Note 4 --")
    deleted_note = manager.read_note(note4_uuid)
    print(f"Note 4 exists? {'Yes' if deleted_note else 'No'}")

    # Visualization
    manager.get_notes_network_cypher()
    manager.get_repost_depth_cypher()


if __name__ == "__main__":
    manager = None
    try:
        manager = NoteManager(URI, AUTH, DATABASE)
        run_sample_data(manager)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        if manager:
            manager.close()