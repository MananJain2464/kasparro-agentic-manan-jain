"""Quick test for WorkflowState"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Then your imports
from src.models.state_model import WorkflowState
from src.models.state_model import WorkflowState
from src.models.product_model import ProductModel
from src.models.question_model import QuestionModel

# Initialize empty state
state: WorkflowState = {
    "raw_input": {"name": "Test Product", "price": 100},
    "input_mode": "json",
    "product_model": None,
    "product_b_model": None,
    "questions": [],
    "questions_by_category": None,
    "content_blocks": None,
    "faq_page": None,
    "product_page": None,
    "comparison_page": None,
    "workflow_status": "initialized",
    "errors": [],
    "warnings": [],
    "agent_trace": [],
    "timestamp": None
}

print("✅ WorkflowState initialized!")
print(f"Status: {state['workflow_status']}")
print(f"Questions list: {state['questions']}")

# Simulate agent update
state["product_model"] = ProductModel(name="Test", price=100, currency="$")
state["agent_trace"].append("data_parser_agent")
state["workflow_status"] = "parsed"

print("\n✅ State updated by agent!")
print(f"Product: {state['product_model'].name}")
print(f"Agent trace: {state['agent_trace']}")
print(f"New status: {state['workflow_status']}")