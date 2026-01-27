from pydantic import BaseModel, Field
from typing import List, Literal


class LineEdit(BaseModel):
    """Represents a single line-level edit suggestion."""
    original_text: str = Field(..., description="The exact text snippet from the thesis.")
    suggested_revision: str = Field(..., description="The corrected version.")
    category: Literal['Grammar', 'Clarity', 'Tone', 'Citation'] = Field(
        ..., description="Type of edit needed."
    )
    reasoning: str = Field(..., description="Explanation for the suggested change.")


class SectionReview(BaseModel):
    """Complete review of a single thesis section."""
    section_name: str = Field(..., description="Name of the section (e.g., 'Introduction').")
    
    # Scoring (0-10) for quick quantitative assessment
    clarity_score: int = Field(
        ..., ge=0, le=10, description="Rating of language clarity."
    )
    logic_score: int = Field(
        ..., ge=0, le=10, description="Rating of logical flow."
    )
    rigor_score: int = Field(
        ..., ge=0, le=10, description="Rating of scientific evidence/methodology."
    )
    
    summary: str = Field(..., description="Executive summary of this section's quality.")
    critical_issues: List[str] = Field(
        default_factory=list, description="High-level structural or logical flaws."
    )
    line_by_line_edits: List[LineEdit] = Field(
        default_factory=list, description="Specific text corrections."
    )


class ThesisReviewResult(BaseModel):
    """Complete review result for an entire thesis."""
    filename: str = Field(..., description="Name of the PDF file reviewed.")
    reviews: List[SectionReview] = Field(..., description="Reviews for each section.")
