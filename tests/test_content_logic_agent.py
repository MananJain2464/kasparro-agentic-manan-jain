"""
Test Content Logic Agent
Tests content block generation with various scenarios
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.data_parser_agent import parse_product_data
from src.agents.product_b_generator_agent import generate_product_b
from src.agents.question_generator_agent import generate_questions
from src.agents.content_logic_agent import generate_content_blocks
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
# TEST 1: Complete Product → All Content Blocks
# ============================================================
print("=" * 70)
print("TEST 1: Complete Product → All Content Blocks")
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

# Parse product
parse_result = parse_product_data(state1)
state1["product_model"] = parse_result["product_model"]

# Generate content blocks
content_result = generate_content_blocks(state1)

print("\n📊 Content Blocks Generated:")
if content_result.get('content_blocks'):
    blocks = content_result['content_blocks']
    print(f"Total block types: {len(blocks)}")
    
    for block_name, block_data in blocks.items():
        if block_name == "faq_answers":
            continue
        print(f"\n  📦 {block_name.upper()} BLOCK:")
        print(f"     ID: {block_data.block_id}")
        print(f"     Type: {block_data.block_type}")
        print(f"     Format: {block_data.format}")
        print(f"     Status: {block_data.validation_status}")
        
        # Show content preview
        if isinstance(block_data.content, dict):
            print(f"     Content keys: {list(block_data.content.keys())}")
        else:
            preview = str(block_data.content)[:100]
            print(f"     Content preview: {preview}...")


# ============================================================
# TEST 2: Minimal Product → Fallback Handling
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 2: Minimal Product → Fallback Handling")
print("=" * 70)

state2 = create_base_state()
state2["raw_input"] = {
    "name": "Basic Moisturizer",
    "price": 299,
    "currency": "₹"
}

parse_result2 = parse_product_data(state2)
state2["product_model"] = parse_result2["product_model"]

content_result2 = generate_content_blocks(state2)

print("\n📊 Content Blocks Generated (Minimal Data):")
if content_result2.get('content_blocks'):
    blocks2 = content_result2['content_blocks']
    
    # Check how blocks handled missing data
    print(f"\n  Benefits Block Status: {blocks2['benefits'].validation_status}")
    print(f"  Ingredients Block Status: {blocks2['ingredients'].validation_status}")
    print(f"  Usage Block Status: {blocks2['usage'].validation_status}")
    print(f"  Safety Block Status: {blocks2['safety'].validation_status}")
    
    # Show fallback content
    print(f"\n  Sample fallback content (Benefits):")
    print(f"  {blocks2['benefits'].content}")


# ============================================================
# TEST 3: Full Pipeline → Product A + B + Questions + Blocks
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 3: Full Pipeline → Product A + B + Questions + Blocks")
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

# Step 1: Parse Product A
parse_result3 = parse_product_data(state3)
state3["product_model"] = parse_result3["product_model"]

# Step 2: Generate Product B
product_b_result3 = generate_product_b(state3)
state3["product_b_model"] = product_b_result3["product_b_model"]

# Step 3: Generate Questions
question_result3 = generate_questions(state3)
state3["questions"] = question_result3["questions"]

# Step 4: Generate Content Blocks
content_result3 = generate_content_blocks(state3)

print("\n📊 Full Pipeline Content Blocks:")
if content_result3.get('content_blocks'):
    blocks3 = content_result3['content_blocks']
    
    print(f"\nTotal block types: {len(blocks3)}")
    
    # Show comparison block details
    if "comparison" in blocks3:
        comp_block = blocks3["comparison"]
        print(f"\n  🔍 COMPARISON BLOCK:")
        comp_content = comp_block.content
        print(f"     Products: {comp_content['products']}")
        print(f"     Price comparison: {comp_content['price_comparison']['cheaper_product']} is cheaper")
        print(f"     Price difference: {comp_content['price_comparison']['percentage_difference']}")
        print(f"     Common ingredients: {comp_content['ingredient_comparison']['common_ingredients']}")
        print(f"     Similarity score: {comp_content['ingredient_comparison']['similarity_score']:.2f}")
        print(f"     Summary: {comp_content['summary'][:150]}...")
    
    # Show FAQ blocks
    if "faq_answers" in blocks3:
        faq_blocks = blocks3["faq_answers"]
        print(f"\n  💬 FAQ ANSWER BLOCKS:")
        print(f"     Total questions: {len(faq_blocks)}")
        print(f"     Sample FAQ entries:")
        for i, faq in enumerate(faq_blocks[:3], 1):
            faq_content = faq.content
            print(f"\n     {i}. [{faq_content['category']}] {faq_content['question']}")
            print(f"        Answer: {faq_content['answer'][:80]}...")


# ============================================================
# TEST 4: Food Product → Domain Adaptability
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 4: Food Product → Domain Adaptability")
print("=" * 70)

state4 = create_base_state()
state4["raw_input"] = {
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
    "usage_instructions": "Consume 1 bar as a snack or after workout.",
    "target_audience": ["Athletes"]
}

parse_result4 = parse_product_data(state4)
state4["product_model"] = parse_result4["product_model"]

content_result4 = generate_content_blocks(state4)

print("\n📊 Food Product Content Blocks:")
if content_result4.get('content_blocks'):
    blocks4 = content_result4['content_blocks']
    
    # Show overview
    overview = blocks4["overview"].content
    print(f"\n  Overview: {overview}")
    
    # Show ingredients structure
    ing_block = blocks4["ingredients"]
    if isinstance(ing_block.content, dict):
        print(f"\n  Ingredients format: {ing_block.content['formatted_text']}")
        print(f"  Ingredient count: {ing_block.content['count']}")


# ============================================================
# TEST 5: Missing Product Model (Error Handling)
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 5: Missing Product Model (Error Handling)")
print("=" * 70)

state5 = create_base_state()
# Don't set product_model

content_result5 = generate_content_blocks(state5)

print("\n📊 Results:")
print(f"Error handled gracefully: {'errors' in content_result5}")
if content_result5.get('errors'):
    print(f"Error message: {content_result5['errors'][0]}")


# ============================================================
# SUMMARY
# ============================================================
print("\n\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

test_results = [
    ("Complete product blocks generated", content_result.get('content_blocks') is not None),
    ("Minimal product fallbacks work", content_result2.get('content_blocks') is not None),
    ("Full pipeline with comparison", content_result3.get('content_blocks', {}).get('comparison') is not None),
    ("FAQ blocks generated", content_result3.get('content_blocks', {}).get('faq_answers') is not None),
    ("Food product adaptability", content_result4.get('content_blocks') is not None),
    ("Error handling works", 'errors' in content_result5)
]

print("\nTest Results:")
for test_name, passed in test_results:
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")

all_passed = all(result[1] for result in test_results)
print(f"\n{'🎉 All tests passed!' if all_passed else '⚠️  Some tests failed'}")

if all_passed:
    print("\n✅ Content Logic Agent is working correctly!")
    print("   - Generates all content block types")
    print("   - Handles missing data with fallbacks")
    print("   - Creates structured content")
    print("   - Generates comparison blocks")
    print("   - Creates FAQ answer blocks")
    print("   - Domain-agnostic content generation")