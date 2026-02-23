-- Migration: Add audio_metadata table
-- Created: 2026-02-20
-- Description: Adds audio_metadata table for storing transcription metadata

-- Create audio_metadata table
CREATE TABLE IF NOT EXISTS audio_metadata (
    id SERIAL PRIMARY KEY,
    note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    original_filename VARCHAR(255) NOT NULL,
    duration_seconds NUMERIC NOT NULL,
    detected_language VARCHAR(50),
    whisper_model_version VARCHAR(50),
    audio_format VARCHAR(10),
    file_size_bytes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on note_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_audio_metadata_note_id ON audio_metadata(note_id);

-- Verify table was created
SELECT 'audio_metadata table created successfully' AS status;
