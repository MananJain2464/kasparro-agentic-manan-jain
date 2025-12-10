"""
Main entry point for the Agentic Content Generation System

This system uses 8 specialized AI agents orchestrated by LangGraph to:
1. Parse product data
2. Generate questions and competitor products
3. Create reusable content blocks
4. Build FAQ, Product, and Comparison pages
5. Output machine-readable JSON files

Usage:
    python main.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from src.orchestrator import run_workflow
from src.config import OUTPUTS_DIR

# Load environment variables
load_dotenv()


def main():
    """
    Main entry point - demonstrates the complete workflow
    """
    
    print("=" * 80)
    print("🤖 AGENTIC CONTENT GENERATION SYSTEM")
    print("=" * 80)
    print("\nA modular multi-agent system that automatically generates:")
    print("  📄 FAQ Pages")
    print("  📄 Product Pages")
    print("  📄 Comparison Pages")
    print("\n" + "=" * 80)
    
    # Example product data (as per assignment)
    example_product = {
        "name": "GlowBoost Vitamin C Serum",
        "price": 699,
        "currency": "₹",
        "concentration": "10% Vitamin C",
        "category": "Serum",
        "key_ingredients": [
            {"name": "Vitamin C", "concentration": "10%", "purpose": "Brightening"},
            {"name": "Hyaluronic Acid", "purpose": "Hydration"}
        ],
        "benefits": ["Brightening", "Fades dark spots"],
        "usage_instructions": "Apply 2–3 drops in the morning before sunscreen",
        "side_effects": "Mild tingling for sensitive skin",
        "target_audience": ["Oily skin", "Combination skin"]
    }
    
    print("\n📦 Running example with provided product data...")
    print("=" * 80)
    
    try:
        # Run the complete workflow
        final_state = run_workflow(example_product, input_mode="json")
        
        # Success summary
        print("\n" + "=" * 80)
        print("✅ SYSTEM EXECUTION COMPLETE")
        print("=" * 80)
        
        print(f"\n📊 Execution Summary:")
        print(f"   Agents executed: {len(final_state.get('agent_trace', []))}")
        print(f"   Pages generated: 3 (FAQ, Product, Comparison)")
        
        print(f"\n📁 Output Location: {OUTPUTS_DIR}")
        print(f"\n   Generated files:")
        for file_name in ["faq.json", "product_page.json", "comparison_page.json"]:
            file_path = OUTPUTS_DIR / file_name
            if file_path.exists():
                size_kb = file_path.stat().st_size / 1024
                print(f"   ✅ {file_name} ({size_kb:.1f} KB)")
        
        print("\n" + "=" * 80)
        print("🎉 All outputs generated successfully!")
        print("=" * 80)
        
        print("\n💡 Next Steps:")
        print("   1. Check the outputs/ directory for generated JSON files")
        print("   2. Modify the product data in main.py to test different products")
        print("   3. See docs/projectdocumentation.md for system architecture")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nPlease ensure:")
        print("  1. OPENAI_API_KEY is set in .env file")
        print("  2. All dependencies are installed (pip install -r requirements.txt)")
        raise


if __name__ == "__main__":
    main()