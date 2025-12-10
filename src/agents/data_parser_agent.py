"""
Data Parser Agent
Converts raw product input into validated ProductModel
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import Dict, Any
from datetime import datetime
from src.models.product_model import ProductModel, IngredientModel
from src.models.state_model import WorkflowState


def parse_product_data(state: WorkflowState) -> Dict[str, Any]:
    """
    Data Parser Agent
    
    Reads: raw_input from state
    Writes: product_model, workflow_status, agent_trace, errors/warnings
    
    Converts raw JSON input into validated ProductModel with proper structure
    """
    print("\n🔍 Data Parser Agent: Starting...")
    
    raw_input = state.get("raw_input", {})
    
    if not raw_input:
        error_msg = "No raw input provided"
        print(f"❌ Error: {error_msg}")
        return {
            "errors": [error_msg],
            "workflow_status": "error",
            "agent_trace": ["data_parser_agent"],
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # Parse ingredients if they exist
        if "key_ingredients" in raw_input and raw_input["key_ingredients"]:
            parsed_ingredients = []
            for ing in raw_input["key_ingredients"]:
                if isinstance(ing, str):
                    # Simple string format
                    parsed_ingredients.append({"name": ing})
                elif isinstance(ing, dict):
                    # Already structured
                    parsed_ingredients.append(ing)
            raw_input["key_ingredients"] = parsed_ingredients
        
        # Create validated ProductModel
        product_model = ProductModel(**raw_input)
        
        print(f"✅ Parsed product: {product_model.name}")
        print(f"   Price: {product_model.currency}{product_model.price}")
        print(f"   Completeness: {product_model.completeness_score}%")
        print(f"   Fields populated: {product_model.field_count}")
        
        # Return state updates
        return {
            "product_model": product_model,
            "workflow_status": "parsed",
            "agent_trace": ["data_parser_agent"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"Failed to parse product data: {str(e)}"
        print(f"❌ Error: {error_msg}")
        return {
            "errors": [error_msg],
            "workflow_status": "error",
            "agent_trace": ["data_parser_agent"],
            "timestamp": datetime.now().isoformat()
        }


# Agent metadata for documentation
AGENT_INFO = {
    "name": "Data Parser Agent",
    "responsibility": "Parse and validate raw product input",
    "reads_from_state": ["raw_input"],
    "writes_to_state": ["product_model", "workflow_status", "agent_trace", "errors", "timestamp"],
    "dependencies": []
}