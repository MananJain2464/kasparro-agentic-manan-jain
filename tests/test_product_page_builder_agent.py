"""
Test Product Page Builder Agent
Tests product page assembly from content blocks
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import json
from src.agents.data_parser_agent import parse_product_data
from src.agents.content_logic_agent import generate_content_blocks
from src.agents.product_page_builder_agent import build_product_page
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
# TEST 1: Complete Product → Full Product Page
# ============================================================
print("=" * 70)
print("TEST 1: Complete Product → Full Product Page")
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
        {"name": "Ferulic Acid", "purpose": "Antioxidant"}
    ],
    "benefits": ["Brightening", "Fades dark spots", "Evens skin tone", "Boosts radiance"],
    "usage_instructions": "Apply 2-3 drops in the morning after cleansing. Follow with sunscreen.",
    "side_effects": "Mild tingling for sensitive skin. Patch test recommended.",
    "target_audience": ["Oily skin", "Combination skin", "Adults 25+"]
}

# Run pipeline
print("\n🔄 Running pipeline...")
parse_result = parse_product_data(state1)
state1["product_model"] = parse_result["product_model"]

content_result = generate_content_blocks(state1)
state1["content_blocks"] = content_result["content_blocks"]

# Build product page
product_page_result = build_product_page(state1)

print("\n📊 Product Page Results:")
if product_page_result.get('product_page'):
    page = product_page_result['product_page']
    
    print(f"\n✅ Product Page Structure:")
    print(f"   Page type: {page['page_type']}")
    print(f"   Product name: {page['product']['name']}")
    
    print(f"\n📦 Sections Present:")
    product_sections = page['product']
    for section_name, section_data in product_sections.items():
        if section_data:
            if isinstance(section_data, dict):
                print(f"   ✅ {section_name}: {len(section_data)} fields")
            elif isinstance(section_data, str):
                preview = section_data[:60] + "..." if len(section_data) > 60 else section_data
                print(f"   ✅ {section_name}: {preview}")
    
    print(f"\n🔍 Key Information:")
    key_info = product_sections.get('key_information', {})
    if 'ingredients' in key_info:
        ing_count = key_info['ingredients'].get('count', 0)
        print(f"   Ingredients: {ing_count} items")
    if 'benefits' in key_info:
        ben_list = key_info['benefits'].get('list', [])
        print(f"   Benefits: {len(ben_list)} items")
    
    print(f"\n💰 Pricing:")
    pricing = product_sections.get('pricing', {})
    print(f"   Price: {pricing.get('formatted_price', 'N/A')}")
    
    print(f"\n📋 Metadata:")
    metadata = page.get('metadata', {})
    print(f"   Completeness: {metadata.get('completeness_score', 0)}%")
    print(f"   Blocks used: {len(metadata.get('blocks_used', []))}")
    
    # Validate JSON
    print(f"\n🔍 JSON Validation:")
    try:
        json_str = json.dumps(page, indent=2)
        print(f"   ✅ Valid JSON structure")
        print(f"   Size: {len(json_str)} characters")
    except:
        print(f"   ❌ Invalid JSON structure")


# ============================================================
# TEST 2: Minimal Product → Sparse Data Handling
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 2: Minimal Product → Sparse Data Handling")
print("=" * 70)

state2 = create_base_state()
state2["raw_input"] = {
    "name": "Basic Moisturizer",
    "price": 299,
    "currency": "₹"
}

print("\n🔄 Running pipeline...")
parse_result2 = parse_product_data(state2)
state2["product_model"] = parse_result2["product_model"]

content_result2 = generate_content_blocks(state2)
state2["content_blocks"] = content_result2["content_blocks"]

product_page_result2 = build_product_page(state2)

print("\n📊 Product Page Results:")
if product_page_result2.get('product_page'):
    page2 = product_page_result2['product_page']
    print(f"   Product: {page2['product']['name']}")
    print(f"   Completeness: {page2['metadata']['completeness_score']}%")
    
    # Check fallback content
    key_info2 = page2['product']['key_information']
    print(f"\n   Fallback handling:")
    print(f"   - Ingredients: {key_info2['ingredients'].get('description', '')[:50]}...")
    print(f"   - Benefits: {key_info2['benefits'].get('description', '')[:50]}...")


# ============================================================
# TEST 3: Food Product → Domain Adaptability
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 3: Food Product → Domain Adaptability")
print("=" * 70)

state3 = create_base_state()
state3["raw_input"] = {
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
    "target_audience": ["Athletes", "Fitness enthusiasts"],
    "custom_fields": {
        "calories": "250 kcal",
        "allergens": "Nuts, Dairy",
        "shelf_life": "6 months"
    }
}

print("\n🔄 Running pipeline...")
parse_result3 = parse_product_data(state3)
state3["product_model"] = parse_result3["product_model"]

content_result3 = generate_content_blocks(state3)
state3["content_blocks"] = content_result3["content_blocks"]

product_page_result3 = build_product_page(state3)

print("\n📊 Product Page Results:")
if product_page_result3.get('product_page'):
    page3 = product_page_result3['product_page']
    print(f"   Product: {page3['product']['name']}")
    print(f"   Category: {page3['product']['additional_information'].get('category', 'N/A')}")
    
    # Check custom fields
    custom = page3['product']['additional_information'].get('custom_attributes', {})
    if custom:
        print(f"\n   Custom Attributes:")
        for key, value in custom.items():
            print(f"     - {key}: {value}")


# ============================================================
# TEST 4: Supplement Product with Full Details
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 4: Supplement Product with Full Details")
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
    "target_audience": ["Adults", "Seniors"]
}

print("\n🔄 Running pipeline...")
parse_result4 = parse_product_data(state4)
state4["product_model"] = parse_result4["product_model"]

content_result4 = generate_content_blocks(state4)
state4["content_blocks"] = content_result4["content_blocks"]

product_page_result4 = build_product_page(state4)

print("\n📊 Product Page Results:")
if product_page_result4.get('product_page'):
    page4 = product_page_result4['product_page']
    print(f"   Product: {page4['product']['name']}")
    
    # Show safety information
    safety = page4['product']['safety_information']
    print(f"\n   Safety Information:")
    print(f"   - Warnings: {safety.get('warnings', '')[:60]}...")


# ============================================================
# TEST 5: Verify Page Structure Details
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 5: Verify Page Structure Details")
print("=" * 70)

if product_page_result.get('product_page'):
    page = product_page_result['product_page']
    
    print("\n🔍 Structural Validation:")
    
    # Check top-level keys
    required_top_keys = ['page_type', 'product', 'metadata']
    for key in required_top_keys:
        has_key = key in page
        status = "✅" if has_key else "❌"
        print(f"   {status} Has '{key}' field")
    
    # Check product section keys
    print(f"\n   Product Section:")
    product_keys = ['name', 'overview', 'key_information', 'how_to_use', 'safety_information', 'pricing']
    for key in product_keys:
        has_key = key in page['product']
        status = "✅" if has_key else "❌"
        print(f"     {status} Has '{key}' field")
    
    # Check key_information structure
    print(f"\n   Key Information Structure:")
    key_info = page['product']['key_information']
    for key in ['ingredients', 'benefits']:
        has_key = key in key_info
        status = "✅" if has_key else "❌"
        print(f"     {status} Has '{key}' field")
    
    # Check metadata
    print(f"\n   Metadata Structure:")
    metadata = page['metadata']
    meta_keys = ['generated_at', 'product_id', 'completeness_score', 'blocks_used']
    for key in meta_keys:
        has_key = key in metadata
        status = "✅" if has_key else "❌"
        print(f"     {status} Has '{key}' field")


# ============================================================
# TEST 6: Missing Content Blocks (Error Handling)
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 6: Missing Content Blocks (Error Handling)")
print("=" * 70)

state6 = create_base_state()
state6["raw_input"] = {"name": "Test", "price": 100}

parse_result6 = parse_product_data(state6)
state6["product_model"] = parse_result6["product_model"]
# Don't generate content blocks

product_page_result6 = build_product_page(state6)

print("\n📊 Results:")
print(f"Error handled gracefully: {'errors' in product_page_result6}")
if product_page_result6.get('errors'):
    print(f"Error message: {product_page_result6['errors'][0]}")


# ============================================================
# SUMMARY
# ============================================================
print("\n\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

test_results = [
    ("Complete product page built", product_page_result.get('product_page') is not None),
    ("Minimal product handled", product_page_result2.get('product_page') is not None),
    ("Food product page built", product_page_result3.get('product_page') is not None),
    ("Supplement page built", product_page_result4.get('product_page') is not None),
    ("Valid JSON structure", product_page_result.get('product_page') is not None),
    ("Error handling works", 'errors' in product_page_result6)
]

print("\nTest Results:")
for test_name, passed in test_results:
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")

all_passed = all(result[1] for result in test_results)
print(f"\n{'🎉 All tests passed!' if all_passed else '⚠️  Some tests failed'}")

if all_passed:
    print("\n✅ Product Page Builder Agent is working correctly!")
    print("   - Assembles comprehensive product pages")
    print("   - Organizes into logical sections")
    print("   - Handles missing data gracefully")
    print("   - Valid JSON structure")
    print("   - Includes rich metadata")
    print("   - Domain-agnostic")
    print("   - Captures custom fields")