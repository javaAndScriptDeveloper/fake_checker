"""Pydantic schemas for Note-related data validation."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class EvaluationScores(BaseModel):
    """Schema for evaluation scores with raw values and coefficients."""

    # Sentiment analysis
    sentimental_score: float = Field(default=0.0, ge=0.0, le=1.0)
    sentimental_score_raw: Optional[float] = None
    sentimental_score_coeff: float = Field(default=1.0, ge=0.0)

    # Trigger keywords
    triggered_keywords: float = Field(default=0.0, ge=0.0)
    triggered_keywords_raw: Optional[float] = None
    triggered_keywords_coeff: float = Field(default=1.0, ge=0.0)

    # Trigger topics
    triggered_topics: float = Field(default=0.0, ge=0.0)
    triggered_topics_raw: Optional[float] = None
    triggered_topics_coeff: float = Field(default=1.0, ge=0.0)

    # Text simplicity
    text_simplicity_deviation: float = Field(default=0.0)
    text_simplicity_deviation_raw: Optional[float] = None
    text_simplicity_deviation_coeff: float = Field(default=1.0, ge=0.0)

    # Confidence factor
    confidence_factor: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence_factor_raw: Optional[float] = None
    confidence_factor_coeff: float = Field(default=1.0, ge=0.0)

    # Clickbait
    clickbait: float = Field(default=0.0, ge=0.0, le=1.0)
    clickbait_raw: Optional[float] = None
    clickbait_coeff: float = Field(default=1.0, ge=0.0)

    # Subjective
    subjective: float = Field(default=0.0, ge=0.0, le=1.0)
    subjective_raw: Optional[float] = None
    subjective_coeff: float = Field(default=1.0, ge=0.0)

    # Call to action
    call_to_action: float = Field(default=0.0, ge=0.0, le=1.0)
    call_to_action_raw: Optional[float] = None
    call_to_action_coeff: float = Field(default=1.0, ge=0.0)

    # Repeated take
    repeated_take: float = Field(default=0.0, ge=0.0, le=1.0)
    repeated_take_raw: Optional[float] = None
    repeated_take_coeff: float = Field(default=1.0, ge=0.0)

    # Repeated note
    repeated_note: float = Field(default=0.0, ge=0.0, le=1.0)
    repeated_note_raw: Optional[float] = None
    repeated_note_coeff: float = Field(default=1.0, ge=0.0)

    # Messianism
    messianism: float = Field(default=0.0, ge=0.0, le=1.0)
    messianism_raw: Optional[float] = None
    messianism_coeff: float = Field(default=1.0, ge=0.0)

    # Opposition to opponents
    opposition_to_opponents: float = Field(default=0.0, ge=0.0, le=1.0)
    opposition_to_opponents_raw: Optional[float] = None
    opposition_to_opponents_coeff: float = Field(default=1.0, ge=0.0)

    # Generalization of opponents
    generalization_of_opponents: float = Field(default=0.0, ge=0.0, le=1.0)
    generalization_of_opponents_raw: Optional[float] = None
    generalization_of_opponents_coeff: float = Field(default=1.0, ge=0.0)

    # Total score
    total_score: float = Field(default=0.0, ge=0.0, le=1.0)
    total_score_raw: Optional[float] = None
    total_score_coeff: float = Field(default=1.0, ge=0.0)

    # Cosine similarity (for comparison metrics)
    cosine_similarity: float = Field(default=0.0, ge=0.0, le=1.0)
    cosine_similarity_raw: Optional[float] = None
    cosine_similarity_coeff: float = Field(default=1.0, ge=0.0)

    model_config = {"from_attributes": True}


class NoteInput(BaseModel):
    """Schema for input when processing a new note."""

    title: Optional[str] = Field(default=None, max_length=500)
    content: str = Field(..., min_length=1, max_length=50000)
    source_id: int = Field(..., gt=0)
    language: str = Field(default="english", min_length=2, max_length=50)
    reposted_from_source_id: Optional[int] = Field(default=None, gt=0)

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Content cannot be empty or whitespace only")
        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        return v.lower().strip()


class NoteOutput(BaseModel):
    """Schema for note output with all evaluation results."""

    id: int
    content: str
    hash: str
    source_id: int
    reposted_from_source_id: Optional[int] = None

    # Evaluation scores
    scores: EvaluationScores

    # Final classification
    is_propaganda: bool = False
    fehner_type: Optional[str] = None
    reason: Optional[str] = None
    amount_of_propaganda_scores: Optional[float] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_note(cls, note) -> "NoteOutput":
        """Create NoteOutput from a Note ORM model."""
        scores = EvaluationScores(
            sentimental_score=float(note.sentimental_score or 0),
            sentimental_score_raw=float(note.sentimental_score_raw) if note.sentimental_score_raw else None,
            sentimental_score_coeff=float(note.sentimental_score_coeff or 1.0),
            triggered_keywords=float(note.triggered_keywords or 0),
            triggered_keywords_raw=float(note.triggered_keywords_raw) if note.triggered_keywords_raw else None,
            triggered_keywords_coeff=float(note.triggered_keywords_coeff or 1.0),
            triggered_topics=float(note.triggered_topics or 0),
            triggered_topics_raw=float(note.triggered_topics_raw) if note.triggered_topics_raw else None,
            triggered_topics_coeff=float(note.triggered_topics_coeff or 1.0),
            text_simplicity_deviation=float(note.text_simplicity_deviation or 0),
            text_simplicity_deviation_raw=float(note.text_simplicity_deviation_raw) if note.text_simplicity_deviation_raw else None,
            text_simplicity_deviation_coeff=float(note.text_simplicity_deviation_coeff or 1.0),
            confidence_factor=float(note.confidence_factor or 0),
            confidence_factor_raw=float(note.confidence_factor_raw) if note.confidence_factor_raw else None,
            confidence_factor_coeff=float(note.confidence_factor_coeff or 1.0),
            clickbait=float(note.clickbait or 0),
            clickbait_raw=float(note.clickbait_raw) if note.clickbait_raw else None,
            clickbait_coeff=float(note.clickbait_coeff or 1.0),
            subjective=float(note.subjective or 0),
            subjective_raw=float(note.subjective_raw) if note.subjective_raw else None,
            subjective_coeff=float(note.subjective_coeff or 1.0),
            call_to_action=float(note.call_to_action or 0),
            call_to_action_raw=float(note.call_to_action_raw) if note.call_to_action_raw else None,
            call_to_action_coeff=float(note.call_to_action_coeff or 1.0),
            repeated_take=float(note.repeated_take or 0),
            repeated_take_raw=float(note.repeated_take_raw) if note.repeated_take_raw else None,
            repeated_take_coeff=float(note.repeated_take_coeff or 1.0),
            repeated_note=float(note.repeated_note or 0),
            repeated_note_raw=float(note.repeated_note_raw) if note.repeated_note_raw else None,
            repeated_note_coeff=float(note.repeated_note_coeff or 1.0),
            messianism=float(note.messianism or 0),
            messianism_raw=float(note.messianism_raw) if note.messianism_raw else None,
            messianism_coeff=float(note.messianism_coeff or 1.0),
            opposition_to_opponents=float(note.opposition_to_opponents or 0),
            opposition_to_opponents_raw=float(note.opposition_to_opponents_raw) if note.opposition_to_opponents_raw else None,
            opposition_to_opponents_coeff=float(note.opposition_to_opponents_coeff or 1.0),
            generalization_of_opponents=float(note.generalization_of_opponents or 0),
            generalization_of_opponents_raw=float(note.generalization_of_opponents_raw) if note.generalization_of_opponents_raw else None,
            generalization_of_opponents_coeff=float(note.generalization_of_opponents_coeff or 1.0),
            total_score=float(note.total_score or 0),
            total_score_raw=float(note.total_score_raw) if note.total_score_raw else None,
            total_score_coeff=float(note.total_score_coeff or 1.0),
            cosine_similarity=float(note.cosine_similarity or 0),
            cosine_similarity_raw=float(note.cosine_similarity_raw) if note.cosine_similarity_raw else None,
            cosine_similarity_coeff=float(note.cosine_similarity_coeff or 1.0),
        )

        return cls(
            id=note.id,
            content=note.content,
            hash=note.hash,
            source_id=note.source_id,
            reposted_from_source_id=note.reposted_from_source_id,
            scores=scores,
            is_propaganda=bool(note.is_propaganda),
            fehner_type=note.fehner_type,
            reason=note.reason,
            amount_of_propaganda_scores=float(note.amount_of_propaganda_scores) if note.amount_of_propaganda_scores else None,
            created_at=note.created_at,
            updated_at=note.updated_at,
        )
