"""
Question data model with validation
"""
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from src.config import QUESTION_CATEGORIES


class QuestionModel(BaseModel):
    """
    Represents a generated question with answer and metadata
    """
    # Core content
    question_text: str = Field(..., description="The actual question")
    answer: str = Field(..., description="Generated answer text")
    category: str = Field(..., description="Question category/type")
    
    # Metadata
    related_fields: List[str] = Field(
        default_factory=list,
        description="ProductModel fields this question relates to"
    )
    priority: str = Field(
        default="medium",
        description="Importance level: high, medium, low"
    )
    complexity: str = Field(
        default="simple",
        description="Answer depth needed: simple, detailed"
    )
    
    # System tracking
    question_id: Optional[str] = Field(None, description="Unique identifier")
    generated_from: str = Field(
        default="template",
        description="Generation method: template, llm, rule-based"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="When question was generated"
    )
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        """Ensure category is valid"""
        if v not in QUESTION_CATEGORIES:
            raise ValueError(
                f"Invalid category '{v}'. Must be one of: {QUESTION_CATEGORIES}"
            )
        return v
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        """Ensure priority is valid"""
        valid_priorities = ["high", "medium", "low"]
        if v not in valid_priorities:
            raise ValueError(
                f"Invalid priority '{v}'. Must be one of: {valid_priorities}"
            )
        return v
    
    def model_post_init(self, __context):
        """Generate question ID if not provided"""
        if not self.question_id:
            # Create ID from first few words of question
            words = self.question_text.lower().split()[:3]
            self.question_id = f"q_{'_'.join(words)}"
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_text": "What are the main benefits of this product?",
                "answer": "This product provides brightening effects and helps fade dark spots.",
                "category": "Benefits",
                "related_fields": ["benefits", "key_ingredients"],
                "priority": "high",
                "complexity": "detailed",
                "generated_from": "template"
            }
        }