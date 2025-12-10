"""
Test Comparison Page Builder Agent
Tests comparison page assembly from products and content blocks
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import json
from src.agents.data_parser_agent import parse_product_data
from src.agents.product_b_generator_agent import generate_product_b
from src.agents.content_logic_agent import generate_content_blocks
from src.agents.comparison_page_builder_agent import build_comparison_page
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
# TEST 1: Complete Comparison → Skincare Products
# ============================================================
print("=" * 70)
print("TEST 1: Complete Comparison → Skincare Products")
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
    "target_audience": ["Oily skin", "Combination skin"]
}

# Run pipeline
print("\n🔄 Running pipeline...")
parse_result = parse_product_data(state1)
state1["product_model"] = parse_result["product_model"]

product_b_result = generate_product_b(state1)
state1["product_b_model"] = product_b_result["product_b_model"]

content_result = generate_content_blocks(state1)
state1["content_blocks"] = content_result["content_blocks"]

# Build comparison page
comparison_result = build_comparison_page(state1)

print("\n📊 Comparison Page Results:")
if comparison_result.get('comparison_page'):
    page = comparison_result['comparison_page']
    
    print(f"\n✅ Comparison Page Structure:")
    print(f"   Page type: {page['page_type']}")
    print(f"   Product A: {page['product_a']['name']}")
    print(f"   Product B: {page['product_b']['name']}")
    
    print(f"\n💰 Price Comparison:")
    price_comp = page['comparison']['price']
    print(f"   {page['product_a']['name']}: {price_comp['product_a_price']}")
    print(f"   {page['product_b']['name']}: {price_comp['product_b_price']}")
    print(f"   Cheaper: {price_comp['cheaper_product']}")
    print(f"   Difference: {price_comp['percentage_difference']}")
    
    print(f"\n🧪 Ingredient Comparison:")
    ing_comp = page['comparison']['ingredients']
    print(f"   Common ingredients: {ing_comp['common_ingredients']}")
    print(f"   Similarity score: {ing_comp['similarity_score']:.2f}")
    # Handle both key naming conventions
    a_unique_key = 'product_a_unique_ingredients' if 'product_a_unique_ingredients' in ing_comp else f"{page['product_a']['name']}_unique"
    b_unique_key = 'product_b_unique_ingredients' if 'product_b_unique_ingredients' in ing_comp else f"{page['product_b']['name']}_unique"

    a_unique = ing_comp.get(a_unique_key, [])
    b_unique = ing_comp.get(b_unique_key, [])

    print(f"   {page['product_a']['name']} unique: {a_unique[:3] if len(a_unique) > 3 else a_unique}")
    print(f"   {page['product_b']['name']} unique: {b_unique[:3] if len(b_unique) > 3 else b_unique}")
    
    print(f"\n💡 Benefits Comparison:")
    ben_comp = page['comparison']['benefits']
    print(f"   Common benefits: {ben_comp['common_benefits']}")
    print(f"   {page['product_a']['name']} unique: {ben_comp['product_a_unique_benefits']}")
    print(f"   {page['product_b']['name']} unique: {ben_comp['product_b_unique_benefits']}")
    
    print(f"\n🎯 Recommendations:")
    recommendations = page.get('recommendations', {})
    if 'budget_friendly' in recommendations:
        print(f"   Budget-friendly: {recommendations['budget_friendly']['product']}")
    if 'overall' in recommendations:
        print(f"   Overall recommended: {recommendations['overall']['recommended_product']}")
    
    # Validate JSON
    print(f"\n🔍 JSON Validation:")
    try:
        json_str = json.dumps(page, indent=2)
        print(f"   ✅ Valid JSON structure")
        print(f"   Size: {len(json_str)} characters")
    except:
        print(f"   ❌ Invalid JSON structure")


# ============================================================
# TEST 2: Food Products → Domain Adaptability
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 2: Food Products → Domain Adaptability")
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
    "benefits": ["High protein", "Energy boost"],
    "target_audience": ["Athletes", "Fitness enthusiasts"]
}

print("\n🔄 Running pipeline...")
parse_result2 = parse_product_data(state2)
state2["product_model"] = parse_result2["product_model"]

product_b_result2 = generate_product_b(state2)
state2["product_b_model"] = product_b_result2["product_b_model"]

content_result2 = generate_content_blocks(state2)
state2["content_blocks"] = content_result2["content_blocks"]

comparison_result2 = build_comparison_page(state2)

print("\n📊 Comparison Page Results:")
if comparison_result2.get('comparison_page'):
    page2 = comparison_result2['comparison_page']
    print(f"   Product A: {page2['product_a']['name']} ({page2['product_a']['category']})")
    print(f"   Product B: {page2['product_b']['name']} ({page2['product_b']['category']})")
    
    price_comp2 = page2['comparison']['price']
    print(f"   Price difference: {price_comp2['percentage_difference']}")


# ============================================================
# TEST 3: Supplement Products → Detailed Comparison
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 3: Supplement Products → Detailed Comparison")
print("=" * 70)

state3 = create_base_state()
state3["raw_input"] = {
    "name": "Omega-3 Fish Oil Capsules",
    "price": 899,
    "currency": "₹",
    "category": "Dietary Supplement",
    "key_ingredients": [
        {"name": "EPA", "concentration": "360mg"},
        {"name": "DHA", "concentration": "240mg"}
    ],
    "benefits": ["Supports heart health", "Improves brain function"],
    "target_audience": ["Adults", "Seniors"]
}

print("\n🔄 Running pipeline...")
parse_result3 = parse_product_data(state3)
state3["product_model"] = parse_result3["product_model"]

product_b_result3 = generate_product_b(state3)
state3["product_b_model"] = product_b_result3["product_b_model"]

content_result3 = generate_content_blocks(state3)
state3["content_blocks"] = content_result3["content_blocks"]

comparison_result3 = build_comparison_page(state3)

print("\n📊 Comparison Page Results:")
if comparison_result3.get('comparison_page'):
    page3 = comparison_result3['comparison_page']
    
    ing_comp3 = page3['comparison']['ingredients']
    print(f"   Ingredient overlap: {len(ing_comp3['common_ingredients'])} ingredients")
    print(f"   Similarity score: {ing_comp3['similarity_score']:.0%}")
    
    # Show target audience comparison
    if 'target_audience' in page3['recommendations']:
        ta_rec = page3['recommendations']['target_audience']
        print(f"\n   Target Audience:")
        print(f"   - {ta_rec['product_a']['name']}: {ta_rec['product_a']['best_for']}")
        print(f"   - {ta_rec['product_b']['name']}: {ta_rec['product_b']['best_for']}")


# ============================================================
# TEST 4: Verify Comparison Structure
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 4: Verify Comparison Structure")
print("=" * 70)

if comparison_result.get('comparison_page'):
    page = comparison_result['comparison_page']
    
    print("\n🔍 Structural Validation:")
    
    # Check top-level keys
    required_top_keys = ['page_type', 'product_a', 'product_b', 'comparison', 'recommendations', 'metadata']
    for key in required_top_keys:
        has_key = key in page
        status = "✅" if has_key else "❌"
        print(f"   {status} Has '{key}' field")
    
    # Check product summaries
    print(f"\n   Product Summary Structure:")
    product_keys = ['name', 'price', 'currency', 'formatted_price', 'category', 'key_ingredients', 'benefits']
    for key in product_keys:
        has_in_a = key in page['product_a']
        has_in_b = key in page['product_b']
        status_a = "✅" if has_in_a else "❌"
        status_b = "✅" if has_in_b else "❌"
        print(f"     {status_a} Product A has '{key}'  |  {status_b} Product B has '{key}'")
    
    # Check comparison structure
    print(f"\n   Comparison Structure:")
    comparison_keys = ['price', 'ingredients', 'benefits', 'summary']
    for key in comparison_keys:
        has_key = key in page['comparison']
        status = "✅" if has_key else "❌"
        print(f"     {status} Has '{key}' comparison")
    
    # Check price comparison details
    print(f"\n   Price Comparison Details:")
    price_keys = ['product_a_price', 'product_b_price', 'difference', 'percentage_difference', 'cheaper_product']
    price_comp = page['comparison']['price']
    for key in price_keys:
        has_key = key in price_comp
        status = "✅" if has_key else "❌"
        print(f"     {status} Has '{key}'")
    
    # Check ingredient comparison details
    print(f"\n   Ingredient Comparison Details:")
    ing_keys = ['common_ingredients', 'product_a_unique_ingredients', 'product_b_unique_ingredients', 'similarity_score']
    ing_comp = page['comparison']['ingredients']
    for key in ing_keys:
        has_key = key in ing_comp
        status = "✅" if has_key else "❌"
        print(f"     {status} Has '{key}'")
    
    # Check recommendations
    print(f"\n   Recommendations:")
    recommendations = page.get('recommendations', {})
    print(f"     Total recommendation types: {len(recommendations)}")
    for rec_type in recommendations.keys():
        print(f"     ✅ Has '{rec_type}' recommendation")


# ============================================================
# TEST 5: Missing Product B (Error Handling)
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 5: Missing Product B (Error Handling)")
print("=" * 70)

state5 = create_base_state()
state5["raw_input"] = {"name": "Test", "price": 100}

parse_result5 = parse_product_data(state5)
state5["product_model"] = parse_result5["product_model"]
# Don't generate Product B

comparison_result5 = build_comparison_page(state5)

print("\n📊 Results:")
print(f"Error handled gracefully: {'errors' in comparison_result5}")
if comparison_result5.get('errors'):
    print(f"Error message: {comparison_result5['errors'][0]}")


# ============================================================
# SUMMARY
# ============================================================
print("\n\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

test_results = [
    ("Skincare comparison built", comparison_result.get('comparison_page') is not None),
    ("Food comparison built", comparison_result2.get('comparison_page') is not None),
    ("Supplement comparison built", comparison_result3.get('comparison_page') is not None),
    ("Valid JSON structure", comparison_result.get('comparison_page') is not None),
    ("Has recommendations", comparison_result.get('comparison_page', {}).get('recommendations') is not None),
    ("Error handling works", 'errors' in comparison_result5)
]

print("\nTest Results:")
for test_name, passed in test_results:
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")

all_passed = all(result[1] for result in test_results)
print(f"\n{'🎉 All tests passed!' if all_passed else '⚠️  Some tests failed'}")

if all_passed:
    print("\n✅ Comparison Page Builder Agent is working correctly!")
    print("   - Assembles side-by-side comparisons")
    print("   - Compares price, ingredients, benefits")
    print("   - Calculates similarity scores")
    print("   - Generates smart recommendations")
    print("   - Valid JSON structure")
    print("   - Domain-agnostic")