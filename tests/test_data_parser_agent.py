"""Test Data Parser Agent"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.data_parser_agent import parse_product_data
from src.models.state_model import WorkflowState

# Test 1: Complete product data
print("=" * 60)
print("TEST 1: Complete Product Data")
print("=" * 60)

state: WorkflowState = {
    "raw_input": {
        "name": "GlowBoost Vitamin C Serum",
        "price": 699,
        "currency": "₹",
        "category": "Serum",
        "key_ingredients": [
            {"name": "Vitamin C", "concentration": "10%", "purpose": "Brightening"},
            "Hyaluronic Acid"  # Simple string format
        ],
        "benefits": ["Brightening", "Fades dark spots"],
        "usage_instructions": "Apply 2-3 drops in the morning before sunscreen",
        "side_effects": "Mild tingling for sensitive skin",
        "target_audience": ["Oily skin", "Combination skin"]
    },
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

# Run agent
result = parse_product_data(state)

# Check results
print("\n📊 Results:")
print(f"Status: {result['workflow_status']}")
print(f"Agent trace: {result['agent_trace']}")
if result.get('product_model'):
    print(f"Product ID: {result['product_model'].product_id}")
    print(f"Ingredients: {[ing.name for ing in result['product_model'].key_ingredients]}")

# Test 2: Minimal product data
print("\n" + "=" * 60)
print("TEST 2: Minimal Product Data (only required fields)")
print("=" * 60)

state2: WorkflowState = {
    "raw_input": {
        "name": "Basic Product",
        "price": 100
    },
    "input_mode": "form",
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

result2 = parse_product_data(state2)
print("\n📊 Results:")
print(f"Status: {result2['workflow_status']}")
print(f"Completeness: {result2.get('product_model').completeness_score if result2.get('product_model') else 'N/A'}%")

# Test 3: Invalid data (should fail gracefully)
print("\n" + "=" * 60)
print("TEST 3: Invalid Data (missing required fields)")
print("=" * 60)

state3: WorkflowState = {
    "raw_input": {
        "category": "Serum"
        # Missing name and price - should fail
    },
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

result3 = parse_product_data(state3)
print("\n📊 Results:")
print(f"Status: {result3['workflow_status']}")
print(f"Errors: {result3.get('errors', [])}")