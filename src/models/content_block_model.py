"""
Content block data model with validation
"""
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from src.config import CONTENT_BLOCK_TYPES


class ContentBlock(BaseModel):
    """
    Represents a reusable content piece generated from product data
    """
    # Core identification
    block_id: str = Field(..., description="Unique identifier for this block")
    block_type: str = Field(..., description="Type of content block")
    
    # Content data (can be string or structured)
    content: Union[str, Dict[str, Any], List[Any]] = Field(
        ...,
        description="The actual content - can be text, dict, or list"
    )
    
    # Metadata
    source_fields: List[str] = Field(
        default_factory=list,
        description="ProductModel fields used to generate this block"
    )
    format: str = Field(
        default="plain_text",
        description="Output format: plain_text, structured_data, markdown, html"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="Other block_ids this block depends on"
    )
    reusable: bool = Field(
        default=True,
        description="Can this block be used across multiple pages?"
    )
    validation_status: str = Field(
        default="complete",
        description="Status: complete, partial, missing, error"
    )
    
    # System tracking
    generated_by: str = Field(
        default="content_logic_agent",
        description="Which agent/function created this block"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="When block was generated"
    )
    token_count: Optional[int] = Field(
        None,
        description="Approximate content length in tokens"
    )
    
    @field_validator('block_type')
    @classmethod
    def validate_block_type(cls, v):
        """Ensure block_type is valid"""
        if v not in CONTENT_BLOCK_TYPES:
            raise ValueError(
                f"Invalid block_type '{v}'. Must be one of: {CONTENT_BLOCK_TYPES}"
            )
        return v
    
    @field_validator('format')
    @classmethod
    def validate_format(cls, v):
        """Ensure format is valid"""
        valid_formats = ["plain_text", "structured_data", "markdown", "html"]
        if v not in valid_formats:
            raise ValueError(
                f"Invalid format '{v}'. Must be one of: {valid_formats}"
            )
        return v
    
    @field_validator('validation_status')
    @classmethod
    def validate_status(cls, v):
        """Ensure validation_status is valid"""
        valid_statuses = ["complete", "partial", "missing", "error"]
        if v not in valid_statuses:
            raise ValueError(
                f"Invalid validation_status '{v}'. Must be one of: {valid_statuses}"
            )
        return v
    
    def model_post_init(self, __context):
        """Calculate token count for text content"""
        if isinstance(self.content, str) and not self.token_count:
            # Rough approximation: 1 token ≈ 4 characters
            self.token_count = len(self.content) // 4
    
    class Config:
        json_schema_extra = {
            "example": {
                "block_id": "benefits_001",
                "block_type": "benefits",
                "content": "This serum provides powerful brightening effects and effectively fades dark spots.",
                "source_fields": ["benefits", "key_ingredients", "name"],
                "format": "plain_text",
                "dependencies": [],
                "reusable": True,
                "validation_status": "complete",
                "generated_by": "content_logic_agent"
            }
        }