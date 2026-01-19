# Propaganda Detection System

A comprehensive system for analyzing text content to detect propaganda, bias, and manipulation techniques. The system uses machine learning models, natural language processing, and graph database technology to track information flow and identify patterns in content distribution.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Repost Analysis Feature](#repost-analysis-feature)
- [Neo4j Queries](#neo4j-queries)
- [Configuration](#configuration)

## Overview

This system analyzes text content across multiple dimensions to detect propaganda:

- **Sentiment Analysis**: Detects emotional manipulation
- **Keyword Detection**: Identifies trigger keywords and topics
- **Text Complexity**: Analyzes simplicity deviation (propaganda often uses simpler language)
- **Clickbait Detection**: Identifies attention-grabbing headlines
- **Subjectivity Analysis**: Measures objective vs. subjective content
- **Call-to-Action Detection**: Identifies persuasive language
- **Repetition Analysis**: Detects repeated takes and notes
- **Messianism Detection**: Identifies messianic language patterns
- **Opposition Analysis**: Detects generalization and opposition to opponents
- **ChatGPT Integration**: Optional AI-powered analysis for high-scoring content

## Features

### Core Analysis Features

1. **Multi-dimensional Scoring**: Each note receives scores across 12+ dimensions
2. **Propaganda Score**: Aggregated total score indicating propaganda likelihood
3. **Source Rating**: Tracks average propaganda scores per source
4. **Fehner Analysis**: Categorizes content using Fehner classification
5. **Translation Support**: Processes content in multiple languages
6. **Graph Database Integration**: Stores relationships in Neo4j for network analysis

### Repost Analysis Feature

The system tracks when notes repost content from other sources, enabling:

- **Information Flow Tracking**: See which sources repost from which other sources
- **Network Analysis**: Visualize repost networks in Neo4j
- **Source Attribution**: Track original sources of reposted content
- **Propagation Patterns**: Identify how information spreads through the network

#### How Reposts Work

When a note reposts content from another source:

1. **Database**: The note stores `reposted_from_source_id` linking to the original source
2. **Neo4j**: Creates a `REPOSTS_FROM` relationship: `(Note)-[:REPOSTS_FROM]->(Source)`
3. **Graph Structure**: 
   ```
   Source A ──[:PUBLISHED]──> Note X ──[:REPOSTS_FROM]──> Source B
   ```
   Where:
   - Source A = The source that published Note X
   - Note X = The note containing reposted content
   - Source B = The original source that Note X reposted from

#### Input Format

Add `repostedFrom` field to your JSON input files:

```json
{
  "language": "english",
  "title": "Breaking News",
  "content": "Content here...",
  "source_id": 5,
  "repostedFrom": 14
}
```

- `repostedFrom: null` = Original content (not a repost)
- `repostedFrom: <source_id>` = Reposts content from that source

## Architecture

### Technology Stack

- **Backend**: Python 3.12
- **Database**: PostgreSQL (primary data storage)
- **Graph Database**: Neo4j (relationship tracking)
- **UI**: PyQt5 (desktop application)
- **ML/NLP**: 
  - Transformers (Hugging Face)
  - spaCy
  - Sentence Transformers
  - TextBlob
  - TextStat

### System Components

```
┌─────────────┐
│   UI Layer  │  PyQt5 Desktop Application
└──────┬──────┘
       │
┌──────▼──────┐
│   Manager   │  Core orchestration
└──────┬──────┘
       │
   ┌───┴───┬──────────────┬──────────────┐
   │       │              │              │
┌──▼──┐ ┌──▼──┐    ┌──────▼──────┐  ┌────▼────┐
│ DAL │ │Proc │    │ Evaluation │  │  Neo4j  │
└──┬──┘ └──┬──┘    │  Processor │  │ Service │
   │       │       └────────────┘  └─────────┘
┌──▼───────▼──┐
│ PostgreSQL  │
└─────────────┘
```

### Data Flow

1. **Input**: JSON files or UI input with text content
2. **Processing**: 
   - Translation (if needed)
   - Evaluation across all dimensions
   - Fehner classification
   - Hash generation (deduplication)
3. **Storage**: 
   - PostgreSQL: Note data, scores, metadata
   - Neo4j: Relationships (PUBLISHED, REPOSTS_FROM)
4. **Output**: Propaganda scores, source ratings, graph visualizations

## Installation

### Prerequisites

- Python 3.12+
- PostgreSQL
- Neo4j (optional, for graph features)
- Virtual environment

### Setup

1. **Clone the repository**:
   ```bash
   cd /path/to/project
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy model**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Configure databases**:
   - Update PostgreSQL connection in `dal/dal.py`
   - Update Neo4j connection in `services/neo4j_service.py`
   - Configure settings in `config/config.yaml`

6. **Run migrations**:
   ```bash
   python -c "from singletons import migration; migration.execute()"
   ```

## Usage

### Running the UI

Launch the desktop application:

```bash
python main.py
```

The UI provides:
- **Text Processor Tab**: Analyze new content
- **Result Table Tab**: View all analyzed notes
- **Ratings Tab**: See source ratings and statistics
- **System Info Tab**: System configuration and status

### Running Examples

You can run the examples script to see the system in action, including the new repost depth feature:

```bash
python examples.py
```

This script will:
1. Process several historical and modern speeches.
2. Demonstrate the **Repost Depth** feature by creating a multi-level chain of reposts.
3. Output processing metadata (time, speed, etc.).

## Repost Analysis Feature

### Understanding Repost Relationships

The repost feature creates two types of relationships in Neo4j:

1. **PUBLISHED**: `(Source)-[:PUBLISHED]->(Note)`
   - Shows which source published/created the note
   - Created for every note

2. **REPOSTS_FROM**: `(Note)-[:REPOSTS_FROM]->(Source)`
   - Shows which source the note reposted from
   - Only created when `repostedFrom` is set in input

### Example Graph Structure

```
Source A (CNN) ──[:PUBLISHED]──> Note 1 "Breaking News"
                                      │
                                      │ [:REPOSTS_FROM]
                                      │
                                      ▼
                              Source B (Reuters)
```

This means:
- Source A (CNN) published Note 1
- Note 1 reposts content from Source B (Reuters)

## Neo4j Queries

### Basic Repost Query

Show all reposts with full context:

```cypher
// Visualize the repost network
MATCH (reposting_note:Note)-[r:REPOSTS_FROM]->(reposted_source:Source)
MATCH (reposting_note)<-[:PUBLISHED]-(reposting_source:Source)
RETURN reposting_note, reposting_source, reposted_source, r
```

### Detailed Repost Information

```cypher
// Show reposts with all details
MATCH (reposting_note:Note)-[r:REPOSTS_FROM]->(reposted_source:Source)
MATCH (reposting_note)<-[:PUBLISHED]-(reposting_source:Source)
RETURN 
    reposting_source.name AS published_by,
    reposting_note.title AS reposting_note_title,
    reposting_note.postgres_id AS reposting_note_id,
    reposted_source.name AS reposted_from_source,
    reposted_source.postgres_id AS reposted_from_source_id,
    r.created_at AS repost_timestamp
ORDER BY r.created_at DESC
```

### Repost Statistics

```cypher
// Count reposts per source
MATCH (note:Note)-[:REPOSTS_FROM]->(source:Source)
RETURN 
    source.name AS source_name,
    source.postgres_id AS source_id,
    count(*) AS repost_count
ORDER BY repost_count DESC
```

### Most Reposted Sources

```cypher
// Find sources that are reposted from most often
MATCH (note:Note)-[:REPOSTS_FROM]->(source:Source)
WITH source, count(*) AS repost_count
RETURN 
    source.name AS source_name,
    source.postgres_id AS source_id,
    repost_count,
    collect(DISTINCT note.postgres_id)[0..10] AS reposting_note_ids
ORDER BY repost_count DESC
LIMIT 10
```

### Complete Repost Context

```cypher
// Show complete repost context with original notes from reposted source
MATCH (reposting_note:Note)-[r:REPOSTS_FROM]->(reposted_source:Source)
MATCH (reposting_note)<-[:PUBLISHED]-(reposting_source:Source)
OPTIONAL MATCH (reposted_source)<-[:PUBLISHED]-(original_notes:Note)
RETURN 
    reposting_source.name + " (ID: " + toString(reposting_source.postgres_id) + ")" AS publisher,
    reposting_note.title AS reposting_note_title,
    reposting_note.postgres_id AS reposting_note_id,
    reposted_source.name + " (ID: " + toString(reposted_source.postgres_id) + ")" AS reposted_from_source,
    count(original_notes) AS original_notes_count
ORDER BY reposting_note.postgres_id DESC
```

### Repost Network Visualization

```cypher
// Visualize the complete repost network
MATCH path = (reposting_source:Source)-[:PUBLISHED]->(reposting_note:Note)-[:REPOSTS_FROM]->(reposted_source:Source)
RETURN path
LIMIT 100
```

### Find Reposts by Specific Source

```cypher
// Find all notes that repost from a specific source
MATCH (note:Note)-[:REPOSTS_FROM]->(source:Source {postgres_id: 14})
MATCH (note)<-[:PUBLISHED]-(publisher:Source)
RETURN 
    publisher.name AS published_by,
    note.title AS note_title,
    note.postgres_id AS note_id
ORDER BY note.postgres_id DESC
```

### Repost Chains and Depth

Find if there are any chains of reposts:
```cypher
MATCH path = (note1:Note)-[:REPOSTS_FROM]->(source1:Source)<-[:PUBLISHED]-(note2:Note)-[:REPOSTS_FROM]->(source2:Source)
RETURN path
LIMIT 50
```

### Depth of Reposts (Note-to-Note)

If using a note-to-note reference model (as in `neo4j_poc.py`), you can calculate the depth of a repost chain from the original post:

```cypher
// Calculate the depth of reposts (chains of REFERENCES)
MATCH path = (n:Note)-[:REFERENCES*]->(root:Note)
WHERE NOT (root)-[:REFERENCES]->()
RETURN n.name AS Note, root.name AS OriginalPost, length(path) AS Depth
ORDER BY Depth DESC
```

## Configuration

### Config File

Edit `config/config.yaml`:

```yaml
average_news_simplicity: 1.0
similarity_threshold: 0.85
openai_api_key: "your-key-here"  # Optional, for ChatGPT analysis
is_chatgpt_processor_enabled: false  # Set to true to enable ChatGPT
```

### Database Configuration

**PostgreSQL** (`dal/dal.py`):
```python
engine = create_engine('postgresql://postgres:password@localhost:5432/fake_checker')
```

**Neo4j** (`services/neo4j_service.py`):
```python
Neo4jService(uri="bolt://localhost:7687", 
             auth=("neo4j", "your_strong_password"),
             database="neo4j")
```

## Logging

The system uses centralized logging. Logs are written to:
- **File**: `logs/app.log`
- **Console**: Standard output

Log levels:
- `INFO`: General information
- `WARNING`: Warnings (e.g., missing sources)
- `ERROR`: Errors with stack traces
- `DEBUG`: Debug information

## Data Structure

### Note Fields

- Content analysis scores (sentiment, keywords, topics, etc.)
- Propaganda indicators (clickbait, subjectivity, call-to-action)
- Fehner classification
- Source attribution
- Repost information (`reposted_from_source_id`)
- Hash for deduplication

### Source Fields

- Name, platform, external ID
- Rating (average propaganda score)
- Visibility settings

## Contributing

When adding new features:
1. Follow the existing logging pattern using `utils.logger`
2. Update database schema if needed
3. Add Neo4j relationships if tracking new connections
4. Update this README with new queries or features

## License

[Add your license here]

## Support

For issues or questions, please [add contact information or issue tracker link]
