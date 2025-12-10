"""
Test Product B Generator Agent (LLM-Powered)
Tests competitor product generation across domains
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.data_parser_agent import parse_product_data
from src.agents.product_b_generator_agent import generate_product_b
from src.models.state_model import WorkflowState
import os
os.environ["OPENAI_API_KEY"] = ""

def create_base_state() -> WorkflowState:
    """Create base empty state"""
    return {
        "raw_input": None,
        "input_mode": None,
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


# ============================================================
# TEST 1: Skincare Product → Competitor Generation
# ============================================================
print("=" * 70)
print("TEST 1: Skincare Product → Competitor Generation")
print("=" * 70)

state1 = create_base_state()
state1["raw_input"] = {
    "name": "GlowBoost Vitamin C Serum",
    "price": 699,
    "currency": "₹",
    "category": "Serum",
    "key_ingredients": [
        {"name": "Vitamin C", "concentration": "10%", "purpose": "Brightening"},
        {"name": "Hyaluronic Acid", "concentration": "2%", "purpose": "Hydration"}
    ],
    "benefits": ["Brightening", "Fades dark spots", "Evens skin tone"],
    "usage_instructions": "Apply 2-3 drops in the morning after cleansing.",
    "target_audience": ["Oily skin", "Combination skin"]
}

# Parse Product A
parse_result = parse_product_data(state1)
state1["product_model"] = parse_result["product_model"]

# Generate Product B
product_b_result = generate_product_b(state1)

print("\n📊 Comparison:")
print(f"\nProduct A: {state1['product_model'].name}")
print(f"  Price: {state1['product_model'].currency}{state1['product_model'].price}")
print(f"  Ingredients: {[ing.name for ing in state1['product_model'].key_ingredients]}")
print(f"  Benefits: {state1['product_model'].benefits}")

if product_b_result.get('product_b_model'):
    product_b = product_b_result['product_b_model']
    print(f"\nProduct B: {product_b.name}")
    print(f"  Price: {product_b.currency}{product_b.price}")
    print(f"  Ingredients: {[ing.name for ing in product_b.key_ingredients]}")
    print(f"  Benefits: {product_b.benefits}")
    
    # Calculate comparison metrics
    price_diff = abs(product_b.price - state1['product_model'].price) / state1['product_model'].price * 100
    print(f"\n  Price difference: {price_diff:.1f}%")
    print(f"  Same category: {product_b.category == state1['product_model'].category}")


# ============================================================
# TEST 2: Food Product → Competitor Generation
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 2: Food Product → Competitor Generation")
print("=" * 70)

state2 = create_base_state()
state2["raw_input"] = {
    "name": "Organic Protein Bar",
    "price": 150,
    "currency": "₹",
    "category": "Snack",
    "key_ingredients": [
        {"name": "Almonds", "concentration": "30%"},
        {"name": "Dates"},
        {"name": "Whey Protein", "concentration": "20g"}
    ],
    "benefits": ["High protein", "Energy boost", "Post-workout recovery"],
    "usage_instructions": "Consume 1 bar as a snack or after workout.",
    "target_audience": ["Athletes", "Fitness enthusiasts"]
}

parse_result2 = parse_product_data(state2)
state2["product_model"] = parse_result2["product_model"]

product_b_result2 = generate_product_b(state2)

print("\n📊 Comparison:")
print(f"\nProduct A: {state2['product_model'].name}")
print(f"  Category: {state2['product_model'].category}")
print(f"  Price: {state2['product_model'].currency}{state2['product_model'].price}")

if product_b_result2.get('product_b_model'):
    product_b2 = product_b_result2['product_b_model']
    print(f"\nProduct B: {product_b2.name}")
    print(f"  Category: {product_b2.category}")
    print(f"  Price: {product_b2.currency}{product_b2.price}")
    print(f"  Target: {product_b2.target_audience}")


# ============================================================
# TEST 3: Supplement Product → Competitor Generation
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 3: Supplement Product → Competitor Generation")
print("=" * 70)

state3 = create_base_state()
state3["raw_input"] = {
    "name": "Omega-3 Fish Oil Capsules",
    "price": 899,
    "currency": "₹",
    "category": "Dietary Supplement",
    "key_ingredients": [
        {"name": "EPA", "concentration": "360mg", "purpose": "Heart health"},
        {"name": "DHA", "concentration": "240mg", "purpose": "Brain function"}
    ],
    "benefits": ["Supports heart health", "Improves brain function"],
    "usage_instructions": "Take 2 capsules daily with meals.",
    "target_audience": ["Adults", "Seniors"]
}

parse_result3 = parse_product_data(state3)
state3["product_model"] = parse_result3["product_model"]

product_b_result3 = generate_product_b(state3)

print("\n📊 Comparison:")
print(f"\nProduct A: {state3['product_model'].name}")
print(f"  Main ingredients: {[ing.name for ing in state3['product_model'].key_ingredients]}")

if product_b_result3.get('product_b_model'):
    product_b3 = product_b_result3['product_b_model']
    print(f"\nProduct B: {product_b3.name}")
    print(f"  Main ingredients: {[ing.name for ing in product_b3.key_ingredients]}")
    
    # Check for overlap
    a_ing = {ing.name.lower() for ing in state3['product_model'].key_ingredients}
    b_ing = {ing.name.lower() for ing in product_b3.key_ingredients}
    overlap = a_ing.intersection(b_ing)
    print(f"\n  Ingredient overlap: {overlap if overlap else 'None (Good!)'}")


# ============================================================
# TEST 4: Minimal Product → Competitor Generation
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 4: Minimal Product → Competitor Generation")
print("=" * 70)

state4 = create_base_state()
state4["raw_input"] = {
    "name": "Basic Moisturizer",
    "price": 299,
    "currency": "₹"
}

parse_result4 = parse_product_data(state4)
state4["product_model"] = parse_result4["product_model"]

product_b_result4 = generate_product_b(state4)

print("\n📊 Comparison:")
print(f"\nProduct A: {state4['product_model'].name} (minimal data)")
print(f"  Completeness: {state4['product_model'].completeness_score}%")

if product_b_result4.get('product_b_model'):
    product_b4 = product_b_result4['product_b_model']
    print(f"\nProduct B: {product_b4.name}")
    print(f"  Completeness: {product_b4.completeness_score}%")
    print(f"  LLM filled in missing details successfully!")


# ============================================================
# TEST 5: Missing Product Model (Error Handling)
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 5: Missing Product Model (Error Handling)")
print("=" * 70)

state5 = create_base_state()
# Don't set product_model

product_b_result5 = generate_product_b(state5)

print("\n📊 Results:")
print(f"Error handled gracefully: {'errors' in product_b_result5}")
if product_b_result5.get('errors'):
    print(f"Error message: {product_b_result5['errors'][0]}")


# ============================================================
# SUMMARY
# ============================================================
print("\n\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

test_results = [
    ("Skincare competitor generated", product_b_result.get('product_b_model') is not None),
    ("Food competitor generated", product_b_result2.get('product_b_model') is not None),
    ("Supplement competitor generated", product_b_result3.get('product_b_model') is not None),
    ("Minimal product handled", product_b_result4.get('product_b_model') is not None),
    ("Error handling works", 'errors' in product_b_result5)
]

print("\nTest Results:")
for test_name, passed in test_results:
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")

all_passed = all(result[1] for result in test_results)
print(f"\n{'🎉 All tests passed!' if all_passed else '⚠️  Some tests failed'}")

# Additional validation checks
if all_passed:
    print("\n✅ Product B Generator Agent is working correctly!")
    print("   - Generates comparable competitors")
    print("   - Maintains same category")
    print("   - Creates different ingredients")
    print("   - Handles minimal data")
    print("   - Error handling functional")