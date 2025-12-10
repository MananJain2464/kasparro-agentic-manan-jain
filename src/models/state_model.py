"""
State model for LangGraph workflow
This is the central data structure that flows through all agents
"""
from typing import TypedDict, Optional, List, Dict, Any, Annotated
from operator import add
from src.models.product_model import ProductModel
from src.models.question_model import QuestionModel
from src.models.content_block_model import ContentBlock


class WorkflowState(TypedDict):
    """
    Master state object that flows through the agent workflow
    Each agent reads from and writes to specific keys
    """
    
    # ==================== INPUT SECTION ====================
    # Populated at workflow start
    raw_input: Optional[Dict[str, Any]]  # Original product JSON from user
    input_mode: Optional[str]  # "form" or "json"
    
    # ==================== PARSED DATA SECTION ====================
    # Populated by Data Parser Agent
    product_model: Optional[ProductModel]  # Main product (validated)
    
    # Populated by Product B Generator Agent
    product_b_model: Optional[ProductModel]  # Competitor product (generated)
    
    # ==================== GENERATED CONTENT SECTION ====================
    # Populated by Question Generator Agent
    questions: Annotated[List[QuestionModel], add]  # All questions (append-only)
    questions_by_category: Optional[Dict[str, List[QuestionModel]]]  # Organized questions
    
    # Populated by Content Logic Agent
    content_blocks: Optional[Dict[str, ContentBlock]]  # All generated content blocks
    
    # ==================== PAGE OUTPUTS SECTION ====================
    # Populated by Page Builder Agents
    faq_page: Optional[Dict[str, Any]]  # FAQ page JSON structure
    product_page: Optional[Dict[str, Any]]  # Product page JSON structure
    comparison_page: Optional[Dict[str, Any]]  # Comparison page JSON structure
    
    # ==================== METADATA SECTION ====================
    # System tracking
    workflow_status: str  # Current stage: initialized, parsed, generating, building, complete, error
    errors: Annotated[List[str], add]  # Error messages (append-only)
    warnings: Annotated[List[str], add]  # Warning messages (append-only)
    agent_trace: Annotated[List[str], add]  # Which agents have run (append-only)
    # Allow multiple agents in the same step to write timestamp without conflict
    timestamp: Annotated[str, add]  # ISO timestamps concatenated per step