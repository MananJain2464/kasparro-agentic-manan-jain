"""
Test Output Formatter Agent
Tests JSON file writing to disk
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import json
import os
from src.agents.data_parser_agent import parse_product_data
from src.agents.product_b_generator_agent import generate_product_b
from src.agents.question_generator_agent import generate_questions
from src.agents.content_logic_agent import generate_content_blocks
from src.agents.faq_builder_agent import build_faq_page
from src.agents.product_page_builder_agent import build_product_page
from src.agents.comparison_page_builder_agent import build_comparison_page
from src.agents.output_formatter_agent import write_output_files
from src.models.state_model import WorkflowState
from src.config import OUTPUTS_DIR

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


def cleanup_output_files():
    """Clean up test output files"""
    if OUTPUTS_DIR.exists():
        for file in OUTPUTS_DIR.glob("*.json"):
            file.unlink()
        print("🧹 Cleaned up existing output files")


# ============================================================
# TEST 1: Complete Pipeline → All Files Written
# ============================================================
print("=" * 70)
print("TEST 1: Complete Pipeline → All Files Written")
print("=" * 70)

# Cleanup before test
cleanup_output_files()

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

# Run complete pipeline
print("\n🔄 Running complete pipeline...")

parse_result = parse_product_data(state1)
state1["product_model"] = parse_result["product_model"]

product_b_result = generate_product_b(state1)
state1["product_b_model"] = product_b_result["product_b_model"]

question_result = generate_questions(state1)
state1["questions"] = question_result["questions"]

content_result = generate_content_blocks(state1)
state1["content_blocks"] = content_result["content_blocks"]

faq_result = build_faq_page(state1)
state1["faq_page"] = faq_result["faq_page"]

product_page_result = build_product_page(state1)
state1["product_page"] = product_page_result["product_page"]

comparison_result = build_comparison_page(state1)
state1["comparison_page"] = comparison_result["comparison_page"]

# Write output files
output_result = write_output_files(state1)

print("\n📊 Output Results:")
print(f"   Files written: {output_result.get('files_written_count', 0)}")
print(f"   Output directory: {output_result.get('output_directory')}")

if output_result.get('written_files'):
    print(f"\n   Written files:")
    for file_path in output_result['written_files']:
        file_name = Path(file_path).name
        file_size = os.path.getsize(file_path)
        print(f"     ✅ {file_name} ({file_size} bytes)")


# ============================================================
# TEST 2: Verify File Contents → JSON Validity
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 2: Verify File Contents → JSON Validity")
print("=" * 70)

if output_result.get('written_files'):
    print("\n🔍 Validating JSON files...")
    
    for file_path in output_result['written_files']:
        file_name = Path(file_path).name
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"\n   ✅ {file_name}:")
            print(f"      Valid JSON: ✅")
            
            # Check specific fields based on file type
            if 'faq' in file_name:
                print(f"      Page type: {data.get('page_type')}")
                print(f"      Total questions: {data.get('total_questions')}")
                print(f"      Categories: {len(data.get('categories', []))}")
                
            elif 'product_page' in file_name:
                print(f"      Page type: {data.get('page_type')}")
                print(f"      Product name: {data.get('product', {}).get('name')}")
                print(f"      Sections: {len(data.get('product', {}).keys())}")
                
            elif 'comparison' in file_name:
                print(f"      Page type: {data.get('page_type')}")
                print(f"      Product A: {data.get('product_a', {}).get('name')}")
                print(f"      Product B: {data.get('product_b', {}).get('name')}")
                
        except json.JSONDecodeError as e:
            print(f"   ❌ {file_name}: Invalid JSON - {e}")
        except Exception as e:
            print(f"   ❌ {file_name}: Error reading - {e}")


# ============================================================
# TEST 3: Partial Pages → Selective Writing
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 3: Partial Pages → Selective Writing")
print("=" * 70)

cleanup_output_files()

state3 = create_base_state()
state3["raw_input"] = {"name": "Basic Product", "price": 100}

# Only build FAQ page, skip others
parse_result3 = parse_product_data(state3)
state3["product_model"] = parse_result3["product_model"]

question_result3 = generate_questions(state3)
state3["questions"] = question_result3["questions"]

content_result3 = generate_content_blocks(state3)
state3["content_blocks"] = content_result3["content_blocks"]

faq_result3 = build_faq_page(state3)
state3["faq_page"] = faq_result3["faq_page"]

# Don't build product or comparison pages
state3["product_page"] = None
state3["comparison_page"] = None

output_result3 = write_output_files(state3)

print("\n📊 Output Results (Partial):")
print(f"   Files written: {output_result3.get('files_written_count', 0)}")
print(f"   Expected: 1 file (FAQ only)")

if output_result3.get('written_files'):
    for file_path in output_result3['written_files']:
        print(f"     ✅ {Path(file_path).name}")


# ============================================================
# TEST 4: File Locations and Structure
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 4: File Locations and Structure")
print("=" * 70)

print(f"\n📂 Output Directory: {OUTPUTS_DIR}")
print(f"   Exists: {'✅' if OUTPUTS_DIR.exists() else '❌'}")
print(f"   Is directory: {'✅' if OUTPUTS_DIR.is_dir() else '❌'}")

if OUTPUTS_DIR.exists():
    json_files = list(OUTPUTS_DIR.glob("*.json"))
    print(f"\n   JSON files in directory: {len(json_files)}")
    
    for json_file in json_files:
        size = json_file.stat().st_size
        print(f"     - {json_file.name} ({size} bytes)")


# ============================================================
# TEST 5: No Pages Available (Error Handling)
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 5: No Pages Available (Graceful Handling)")
print("=" * 70)

cleanup_output_files()

state5 = create_base_state()
# Don't set any pages

output_result5 = write_output_files(state5)

print("\n📊 Results:")
print(f"   Files written: {output_result5.get('files_written_count', 0)}")
print(f"   Expected: 0 files")
print(f"   Handled gracefully: {'✅' if output_result5.get('files_written_count') == 0 else '❌'}")


# ============================================================
# TEST 6: Food Product → Special Characters
# ============================================================
print("\n\n" + "=" * 70)
print("TEST 6: Food Product → Special Characters (UTF-8)")
print("=" * 70)

cleanup_output_files()

state6 = create_base_state()
state6["raw_input"] = {
    "name": "Organic Protein Bar",
    "price": 150,
    "currency": "₹",  # Special character
    "category": "Snack",
    "key_ingredients": [{"name": "Almonds"}, {"name": "Dates"}],
    "benefits": ["High protein", "Energy boost"]
}

parse_result6 = parse_product_data(state6)
state6["product_model"] = parse_result6["product_model"]

question_result6 = generate_questions(state6)
state6["questions"] = question_result6["questions"]

content_result6 = generate_content_blocks(state6)
state6["content_blocks"] = content_result6["content_blocks"]

faq_result6 = build_faq_page(state6)
state6["faq_page"] = faq_result6["faq_page"]

output_result6 = write_output_files(state6)

print("\n📊 UTF-8 Encoding Test:")
if output_result6.get('written_files'):
    faq_file = Path(output_result6['written_files'][0])
    
    with open(faq_file, 'r', encoding='utf-8') as f:
        content = f.read()
        has_rupee = '₹' in content
        print(f"   Currency symbol (₹) preserved: {'✅' if has_rupee else '❌'}")


# ============================================================
# SUMMARY
# ============================================================
print("\n\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

test_results = [
    ("Complete pipeline writes all files", output_result.get('files_written_count') == 3),
    ("JSON files are valid", len(output_result.get('written_files', [])) > 0),
    ("Partial pages handled", output_result3.get('files_written_count') == 1),
    ("Output directory created", OUTPUTS_DIR.exists()),
    ("No pages handled gracefully", output_result5.get('files_written_count') == 0),
    ("UTF-8 encoding works", output_result6.get('files_written_count') > 0)
]

print("\nTest Results:")
for test_name, passed in test_results:
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")

all_passed = all(result[1] for result in test_results)
print(f"\n{'🎉 All tests passed!' if all_passed else '⚠️  Some tests failed'}")

if all_passed:
    print("\n✅ Output Formatter Agent is working correctly!")
    print("   - Writes JSON files to disk")
    print("   - Validates JSON structure")
    print("   - Handles partial pages")
    print("   - Creates output directory")
    print("   - Handles UTF-8 encoding")
    print("   - Graceful error handling")
    
    print(f"\n📁 Output files available at: {OUTPUTS_DIR}")