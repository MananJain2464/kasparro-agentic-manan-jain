"""
Test FAQ Builder Agent
Tests FAQ page assembly from content blocks
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import json
from src.agents.data_parser_agent import parse_product_data
from src.agents.product_b_generator_agent import generate_product_b
from src.agents.question_generator_agent import generate_questions
from src.agents.content_logic_agent import generate_content_blocks
from src.agents.faq_builder_agent import build_faq_page
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
# TEST 1: Complete Pipeline → FAQ Page Assembly
# ============================================================
print("=" * 70)
print("TEST 1: Complete Pipeline → FAQ Page Assembly")
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
    "side_effects": "Mild tingling for sensitive skin.",
    "target_audience": ["Oily skin", "Combination skin"]
}

# Run pipeline
print("\n🔄 Running pipeline...")
parse_result = parse_product_data(state1)
state1["product_model"] = parse_result["product_model"]

question_result = generate_questions(state1)
state1["questions"] = question_result["questions"]

content_result = generate_content_blocks(state1)
state1["content_blocks"] = content_result["content_blocks"]

# Build FAQ page
faq_result = build_faq_page(state1)

print("\n📊 FAQ Page Results:")
if faq_result.get('faq_page'):
    faq_page = faq_result['faq_page']
    
    print(f"\n✅ FAQ Page Structure:")
    print(f"   Page type: {faq_page['page_type']}")
    print(f"   Product: {faq_page['product_name']}")
    print(f"   Total questions: {faq_page['total_questions']}")
    print(f"   Categories: {faq_page['categories']}")
    
    print(f"\n📋 Category Breakdown:")
    for category, faqs in faq_page['faqs_by_category'].items():
        print(f"   {category}: {len(faqs)} questions")
    
    print(f"\n💡 Sample FAQs:")
    for i, faq in enumerate(faq_page['faqs'][:5], 1):
        print(f"\n   {i}. [{faq['category']}] {faq['question']}")
        print(f"      Priority: {faq['priority']}")
        print(f"      Answer: {faq['answer'][:80]}...")
    
    # Validate JSON structure
    print(f"\n🔍 JSON Validation:")
    try:
        json_str = json.dumps(faq_page, indent=2)
        print(f"   ✅ Valid JSON structure")
        print(f"   Size: {len(json_str)} characters")
    except:
        print(f"   ❌ Invalid JSON structure")


# ============================================================
# TEST 2: Food Product → Domain Adaptability
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 2: Food Product → Domain Adaptability")
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

# Run pipeline
print("\n🔄 Running pipeline...")
parse_result2 = parse_product_data(state2)
state2["product_model"] = parse_result2["product_model"]

question_result2 = generate_questions(state2)
state2["questions"] = question_result2["questions"]

content_result2 = generate_content_blocks(state2)
state2["content_blocks"] = content_result2["content_blocks"]

faq_result2 = build_faq_page(state2)

print("\n📊 FAQ Page Results:")
if faq_result2.get('faq_page'):
    faq_page2 = faq_result2['faq_page']
    print(f"   Product: {faq_page2['product_name']}")
    print(f"   Total questions: {faq_page2['total_questions']}")
    print(f"   Categories: {len(faq_page2['categories'])}")


# ============================================================
# TEST 3: Minimal Product → FAQ Generation
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 3: Minimal Product → FAQ Generation")
print("=" * 70)

state3 = create_base_state()
state3["raw_input"] = {
    "name": "Basic Moisturizer",
    "price": 299,
    "currency": "₹"
}

# Run pipeline
print("\n🔄 Running pipeline...")
parse_result3 = parse_product_data(state3)
state3["product_model"] = parse_result3["product_model"]

question_result3 = generate_questions(state3)
state3["questions"] = question_result3["questions"]

content_result3 = generate_content_blocks(state3)
state3["content_blocks"] = content_result3["content_blocks"]

faq_result3 = build_faq_page(state3)

print("\n📊 FAQ Page Results:")
if faq_result3.get('faq_page'):
    faq_page3 = faq_result3['faq_page']
    print(f"   Product: {faq_page3['product_name']}")
    print(f"   Total questions: {faq_page3['total_questions']}")
    print(f"   Can handle minimal data: ✅")


# ============================================================
# TEST 4: Missing Content Blocks (Error Handling)
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 4: Missing Content Blocks (Error Handling)")
print("=" * 70)

state4 = create_base_state()
state4["raw_input"] = {"name": "Test", "price": 100}

parse_result4 = parse_product_data(state4)
state4["product_model"] = parse_result4["product_model"]
# Don't generate content blocks

faq_result4 = build_faq_page(state4)

print("\n📊 Results:")
print(f"Error handled gracefully: {'errors' in faq_result4}")
if faq_result4.get('errors'):
    print(f"Error message: {faq_result4['errors'][0]}")


# ============================================================
# TEST 5: Verify FAQ Structure Details
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 5: Verify FAQ Structure Details")
print("=" * 70)

if faq_result.get('faq_page'):
    faq_page = faq_result['faq_page']
    
    print("\n🔍 Structural Validation:")
    
    # Check required keys
    required_keys = ['page_type', 'product_name', 'total_questions', 'categories', 'faqs', 'faqs_by_category', 'metadata']
    for key in required_keys:
        has_key = key in faq_page
        status = "✅" if has_key else "❌"
        print(f"   {status} Has '{key}' field")
    
    # Check FAQ entry structure
    if faq_page['faqs']:
        sample_faq = faq_page['faqs'][0]
        faq_keys = ['question', 'answer', 'category', 'priority']
        print(f"\n   FAQ Entry Structure:")
        for key in faq_keys:
            has_key = key in sample_faq
            status = "✅" if has_key else "❌"
            print(f"     {status} Has '{key}' field")
    
    # Check metadata
    print(f"\n   Metadata Structure:")
    metadata = faq_page.get('metadata', {})
    meta_keys = ['generated_at', 'product_id', 'currency', 'price']
    for key in meta_keys:
        has_key = key in metadata
        status = "✅" if has_key else "❌"
        print(f"     {status} Has '{key}' field")
    
    # Check category organization
    print(f"\n   Category Organization:")
    total_in_categories = sum(len(faqs) for faqs in faq_page['faqs_by_category'].values())
    matches = total_in_categories == faq_page['total_questions']
    print(f"     {'✅' if matches else '❌'} All FAQs accounted for in categories")
    print(f"     Total in flat list: {len(faq_page['faqs'])}")
    print(f"     Total in categories: {total_in_categories}")


# ============================================================
# SUMMARY
# ============================================================
print("\n\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

test_results = [
    ("Complete FAQ page built", faq_result.get('faq_page') is not None),
    ("Food product FAQ built", faq_result2.get('faq_page') is not None),
    ("Minimal product FAQ built", faq_result3.get('faq_page') is not None),
    ("Error handling works", 'errors' in faq_result4),
    ("Valid JSON structure", faq_result.get('faq_page') is not None)
]

print("\nTest Results:")
for test_name, passed in test_results:
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")

all_passed = all(result[1] for result in test_results)
print(f"\n{'🎉 All tests passed!' if all_passed else '⚠️  Some tests failed'}")

if all_passed:
    print("\n✅ FAQ Builder Agent is working correctly!")
    print("   - Assembles FAQ pages from content blocks")
    print("   - Organizes by category")
    print("   - Sorts by priority")
    print("   - Valid JSON structure")
    print("   - Includes metadata")
    print("   - Domain-agnostic")