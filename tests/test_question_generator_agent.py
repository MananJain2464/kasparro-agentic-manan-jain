"""
Test Question Generator Agent (LLM-Powered)
Tests multiple product scenarios
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.agents.question_generator_agent import generate_questions
from src.agents.data_parser_agent import parse_product_data
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
# TEST 1: Complete Skincare Product (All Fields)
# ============================================================
print("=" * 70)
print("TEST 1: Complete Skincare Product (All Fields)")
print("=" * 70)

state1 = create_base_state()
state1["raw_input"] = {
    "name": "GlowBoost Vitamin C Serum",
    "price": 699,
    "currency": "₹",
    "category": "Serum",
    "key_ingredients": [
        {"name": "Vitamin C", "concentration": "10%", "purpose": "Brightening"},
        {"name": "Hyaluronic Acid", "concentration": "2%", "purpose": "Hydration"},
        {"name": "Ferulic Acid", "purpose": "Antioxidant protection"}
    ],
    "benefits": ["Brightening", "Fades dark spots", "Evens skin tone", "Boosts radiance"],
    "usage_instructions": "Apply 2-3 drops in the morning after cleansing. Follow with sunscreen. Can be used daily.",
    "side_effects": "Mild tingling may occur for sensitive skin. Patch test recommended.",
    "target_audience": ["Oily skin", "Combination skin", "Adults 25+"]
}

# Parse product first
parse_result = parse_product_data(state1)
state1["product_model"] = parse_result["product_model"]

# Generate questions
question_result = generate_questions(state1)

print("\n📊 Results:")
print(f"Total questions: {len(question_result.get('questions', []))}")
print(f"Categories covered: {len(question_result.get('questions_by_category', {}))}")
print("\nSample questions:")
for i, q in enumerate(question_result.get('questions', [])[:5], 1):
    print(f"\n{i}. [{q.category}] {q.question_text}")
    print(f"   Answer: {q.answer[:100]}...")


# ============================================================
# TEST 2: Minimal Product (Only Required Fields)
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 2: Minimal Product (Only Required Fields)")
print("=" * 70)

state2 = create_base_state()
state2["raw_input"] = {
    "name": "Basic Moisturizer",
    "price": 299,
    "currency": "₹"
}

parse_result2 = parse_product_data(state2)
state2["product_model"] = parse_result2["product_model"]

question_result2 = generate_questions(state2)

print("\n📊 Results:")
print(f"Total questions: {len(question_result2.get('questions', []))}")
print(f"Categories covered: {len(question_result2.get('questions_by_category', {}))}")
print("\nSample questions:")
for i, q in enumerate(question_result2.get('questions', [])[:5], 1):
    print(f"\n{i}. [{q.category}] {q.question_text}")
    print(f"   Answer: {q.answer[:100]}...")


# ============================================================
# TEST 3: Food Product (Domain Adaptability)
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 3: Food Product (Domain Adaptability)")
print("=" * 70)

state3 = create_base_state()
state3["raw_input"] = {
    "name": "Organic Protein Bar",
    "price": 150,
    "currency": "₹",
    "category": "Snack",
    "key_ingredients": [
        {"name": "Almonds", "concentration": "30%", "purpose": "Protein source"},
        {"name": "Dates", "purpose": "Natural sweetener"},
        {"name": "Whey Protein", "concentration": "20g", "purpose": "Muscle recovery"}
    ],
    "benefits": ["High protein", "Energy boost", "Post-workout recovery"],
    "usage_instructions": "Consume 1 bar as a snack or after workout. Best consumed within 30 minutes of exercise.",
    "side_effects": "Contains nuts and dairy. May cause allergic reactions in sensitive individuals.",
    "target_audience": ["Athletes", "Fitness enthusiasts", "Adults"],
    "custom_fields": {
        "calories": "250 kcal",
        "allergens": "Nuts, Dairy",
        "shelf_life": "6 months"
    }
}

parse_result3 = parse_product_data(state3)
state3["product_model"] = parse_result3["product_model"]

question_result3 = generate_questions(state3)

print("\n📊 Results:")
print(f"Total questions: {len(question_result3.get('questions', []))}")
print(f"Categories covered: {len(question_result3.get('questions_by_category', {}))}")
print("\nCategory distribution:")
for category, questions in question_result3.get('questions_by_category', {}).items():
    print(f"  {category}: {len(questions)} questions")

print("\nSample questions:")
for i, q in enumerate(question_result3.get('questions', [])[:5], 1):
    print(f"\n{i}. [{q.category}] {q.question_text}")
    print(f"   Answer: {q.answer[:100]}...")


# ============================================================
# TEST 4: Supplement Product with Custom Fields
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 4: Supplement Product with Custom Fields")
print("=" * 70)

state4 = create_base_state()
state4["raw_input"] = {
    "name": "Omega-3 Fish Oil Capsules",
    "price": 899,
    "currency": "₹",
    "category": "Dietary Supplement",
    "key_ingredients": [
        {"name": "EPA", "concentration": "360mg", "purpose": "Heart health"},
        {"name": "DHA", "concentration": "240mg", "purpose": "Brain function"}
    ],
    "benefits": ["Supports heart health", "Improves brain function", "Reduces inflammation"],
    "usage_instructions": "Take 2 capsules daily with meals.",
    "side_effects": "May cause fishy aftertaste. Consult doctor if on blood thinners.",
    "target_audience": ["Adults", "Seniors"],
    "custom_fields": {
        "dosage": "1000mg per serving",
        "capsules_per_bottle": "60",
        "form": "Softgel capsules",
        "certifications": "GMP Certified"
    }
}

parse_result4 = parse_product_data(state4)
state4["product_model"] = parse_result4["product_model"]

question_result4 = generate_questions(state4)

print("\n📊 Results:")
print(f"Total questions: {len(question_result4.get('questions', []))}")
print(f"Categories covered: {len(question_result4.get('questions_by_category', {}))}")
print("\nSample questions:")
for i, q in enumerate(question_result4.get('questions', [])[:5], 1):
    print(f"\n{i}. [{q.category}] {q.question_text}")
    print(f"   Answer: {q.answer[:100]}...")


# ============================================================
# TEST 5: Missing Product Model (Error Handling)
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 5: Missing Product Model (Error Handling)")
print("=" * 70)

state5 = create_base_state()
# Don't set product_model - should fail gracefully

question_result5 = generate_questions(state5)

print("\n📊 Results:")
print(f"Workflow handled error: {'errors' in question_result5}")
if question_result5.get('errors'):
    print(f"Error message: {question_result5['errors'][0]}")


# ============================================================
# SUMMARY
# ============================================================
print("\n\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

test_results = [
    ("Complete skincare product", len(question_result.get('questions', [])) >= 15),
    ("Minimal product", len(question_result2.get('questions', [])) >= 15),
    ("Food product (domain adaptability)", len(question_result3.get('questions', [])) >= 15),
    ("Supplement with custom fields", len(question_result4.get('questions', [])) >= 15),
    ("Error handling", 'errors' in question_result5)
]

print("\nTest Results:")
for test_name, passed in test_results:
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")

all_passed = all(result[1] for result in test_results)
print(f"\n{'🎉 All tests passed!' if all_passed else '⚠️  Some tests failed'}")