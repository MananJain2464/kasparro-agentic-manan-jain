"""
LangGraph Orchestrator
Coordinates all agents in the content generation workflow
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from src.models.state_model import WorkflowState
from src.agents.data_parser_agent import parse_product_data
from src.agents.question_generator_agent import generate_questions
from src.agents.product_b_generator_agent import generate_product_b
from src.agents.content_logic_agent import generate_content_blocks
from src.agents.faq_builder_agent import build_faq_page
from src.agents.product_page_builder_agent import build_product_page
from src.agents.comparison_page_builder_agent import build_comparison_page
from src.agents.output_formatter_agent import write_output_files


def create_workflow() -> StateGraph:
    """
    Creates the LangGraph workflow with all agents
    
    Workflow Structure:
    1. Data Parser Agent (parse product)
    2. Question Generator + Product B Generator (parallel)
    3. Content Logic Agent (generate blocks)
    4. FAQ Builder + Product Page Builder + Comparison Page Builder (parallel)
    5. Output Formatter (write files)
    """
    
    # Initialize workflow
    workflow = StateGraph(WorkflowState)
    
    # Add nodes (agents)
    workflow.add_node("data_parser", parse_product_data)
    workflow.add_node("question_generator", generate_questions)
    workflow.add_node("product_b_generator", generate_product_b)
    workflow.add_node("content_logic", generate_content_blocks)
    workflow.add_node("faq_builder", build_faq_page)
    workflow.add_node("product_page_builder", build_product_page)
    workflow.add_node("comparison_page_builder", build_comparison_page)
    workflow.add_node("output_formatter", write_output_files)
    
    # Define edges (execution flow)
    
    # Step 1: Start with Data Parser
    workflow.set_entry_point("data_parser")
    
    # Step 2: After parsing, run Question Generator and Product B Generator in parallel
    workflow.add_edge("data_parser", "question_generator")
    workflow.add_edge("data_parser", "product_b_generator")
    
    # Step 3: Both must complete before Content Logic
    workflow.add_edge("question_generator", "content_logic")
    workflow.add_edge("product_b_generator", "content_logic")
    
    # Step 4: After content blocks, run all page builders in parallel
    workflow.add_edge("content_logic", "faq_builder")
    workflow.add_edge("content_logic", "product_page_builder")
    workflow.add_edge("content_logic", "comparison_page_builder")
    
    # Step 5: All builders must complete before output formatter
    workflow.add_edge("faq_builder", "output_formatter")
    workflow.add_edge("product_page_builder", "output_formatter")
    workflow.add_edge("comparison_page_builder", "output_formatter")
    
    # Step 6: End after output
    workflow.add_edge("output_formatter", END)
    
    # Compile workflow
    app = workflow.compile()
    
    return app


def run_workflow(product_data: Dict[str, Any], input_mode: str = "json") -> Dict[str, Any]:
    """
    Run the complete content generation workflow
    
    Args:
        product_data: Product information as dictionary
        input_mode: "json" or "form"
    
    Returns:
        Final state with all generated content and file paths
    """
    
    print("=" * 70)
    print("🚀 AGENTIC CONTENT GENERATION SYSTEM")
    print("=" * 70)
    print(f"\n📦 Input Product: {product_data.get('name', 'Unknown')}")
    print(f"💰 Price: {product_data.get('currency', '₹')}{product_data.get('price', 0)}")
    print(f"📝 Input Mode: {input_mode}")
    print("\n" + "=" * 70)
    
    # Initialize state
    initial_state: WorkflowState = {
        "raw_input": product_data,
        "input_mode": input_mode,
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
        "timestamp": ""
    }
    
    # Create and run workflow
    app = create_workflow()
    
    print("\n🔄 Starting workflow execution...\n")
    
    try:
        # Execute workflow
        final_state = app.invoke(initial_state)
        
        # Check for errors
        if final_state.get("errors"):
            print("\n⚠️  Workflow completed with errors:")
            for error in final_state["errors"]:
                print(f"   ❌ {error}")
        else:
            print("\n✅ Workflow completed successfully!")
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 WORKFLOW SUMMARY")
        print("=" * 70)
        
        print(f"\n🔧 Agents Executed: {len(final_state.get('agent_trace', []))}")
        for i, agent in enumerate(final_state.get('agent_trace', []), 1):
            print(f"   {i}. {agent}")
        
        if final_state.get('written_files'):
            print(f"\n📄 Output Files Generated: {len(final_state.get('written_files', []))}")
            for file_path in final_state['written_files']:
                print(f"   ✅ {Path(file_path).name}")
            print(f"\n📁 Location: {final_state.get('output_directory')}")
        
        print("\n" + "=" * 70)
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ Workflow execution failed: {str(e)}")
        raise


def run_workflow_from_json_file(json_file_path: str) -> Dict[str, Any]:
    """
    Run workflow from a JSON file containing product data
    
    Args:
        json_file_path: Path to JSON file with product data
    
    Returns:
        Final state with all generated content
    """
    import json
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        product_data = json.load(f)
    
    return run_workflow(product_data, input_mode="json")


# For visualization (optional)
def visualize_workflow():
    """
    Generate a visual representation of the workflow
    Requires: pip install grandalf
    """
    try:
        app = create_workflow()
        
        # Get Mermaid diagram
        print("\n📊 Workflow Visualization (Mermaid):")
        print("=" * 70)
        print(app.get_graph().draw_mermaid())
        print("=" * 70)
        
    except Exception as e:
        print(f"Visualization requires additional dependencies: {e}")


if __name__ == "__main__":
    # Example usage
    sample_product = {
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
    
    # Run workflow
    final_state = run_workflow(sample_product)
    
    # Optional: Visualize workflow
    # visualize_workflow()