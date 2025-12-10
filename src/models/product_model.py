"""
Product data model with validation
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class IngredientModel(BaseModel):
    """
    Represents a single ingredient with optional details
    """
    name: str = Field(..., description="Ingredient name (required)")
    concentration: Optional[str] = Field(None, description="Amount or percentage (e.g., '10%', '500mg')")
    purpose: Optional[str] = Field(None, description="Why this ingredient is included")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Vitamin C",
                "concentration": "10%",
                "purpose": "Brightening"
            }
        }


class ProductModel(BaseModel):
    """
    Validated product data model
    Domain-agnostic structure that works for skincare, food, supplements, etc.
    """
    # Required fields
    name: str = Field(..., description="Product name")
    price: float = Field(..., gt=0, description="Product price (must be positive)")
    currency: str = Field(default="₹", description="Currency symbol or code")
    
    # Standard optional fields (domain-agnostic)
    category: Optional[str] = Field(None, description="Product category/type")
    key_ingredients: Optional[List[IngredientModel]] = Field(
        default_factory=list,
        description="List of ingredients with optional details"
    )
    benefits: Optional[List[str]] = Field(
        default_factory=list,
        description="Product benefits"
    )
    usage_instructions: Optional[str] = Field(
        None,
        description="How to use the product (multi-line text)"
    )
    side_effects: Optional[str] = Field(
        None,
        description="Warnings and side effects (multi-line text)"
    )
    target_audience: Optional[List[str]] = Field(
        default_factory=list,
        description="Target users (e.g., skin types, age groups, dietary preferences)"
    )
    
    # Dynamic fields for domain-specific attributes
    custom_fields: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional domain-specific attributes"
    )
    
    # Metadata (system-generated)
    product_id: Optional[str] = Field(None, description="Unique identifier")
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="When this model was created"
    )
    field_count: Optional[int] = Field(None, description="Number of populated fields")
    completeness_score: Optional[float] = Field(None, description="Percentage of standard fields filled")
    
    @field_validator('key_ingredients', mode='before')
    @classmethod
    def parse_ingredients(cls, v):
        """Convert simple string list to IngredientModel objects if needed"""
        if not v:
            return []
        
        result = []
        for item in v:
            if isinstance(item, dict):
                result.append(IngredientModel(**item))
            elif isinstance(item, str):
                # Simple string - convert to ingredient object
                result.append(IngredientModel(name=item))
            else:
                result.append(item)
        return result
    
    def model_post_init(self, __context):
        """Calculate metadata after initialization"""
        # Generate product ID if not provided
        if not self.product_id:
            self.product_id = f"prod_{self.name.lower().replace(' ', '_')[:20]}"
        
        # Calculate completeness score
        standard_fields = [
            self.category, self.key_ingredients, self.benefits,
            self.usage_instructions, self.side_effects, self.target_audience
        ]
        filled = sum(1 for field in standard_fields if field)
        self.completeness_score = round((filled / len(standard_fields)) * 100, 2)
        
        # Field count
        self.field_count = filled + len(self.custom_fields) + 3  # +3 for required fields
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "GlowBoost Vitamin C Serum",
                "price": 699,
                "currency": "₹",
                "category": "Serum",
                "key_ingredients": [
                    {"name": "Vitamin C", "concentration": "10%", "purpose": "Brightening"},
                    {"name": "Hyaluronic Acid", "purpose": "Hydration"}
                ],
                "benefits": ["Brightening", "Fades dark spots"],
                "usage_instructions": "Apply 2-3 drops in the morning before sunscreen",
                "side_effects": "Mild tingling for sensitive skin",
                "target_audience": ["Oily skin", "Combination skin"]
            }
        }