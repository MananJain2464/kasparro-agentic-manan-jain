"""
Product Page Builder Agent
Assembles comprehensive product page from content blocks
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import Dict, Any
from datetime import datetime
from src.models.state_model import WorkflowState


def build_product_page(state: WorkflowState) -> Dict[str, Any]:
    """
    Product Page Builder Agent
    
    Reads: content_blocks, product_model from state
    Writes: product_page, agent_trace
    
    Assembles comprehensive product page JSON from content blocks
    """
    print("\n📄 Product Page Builder Agent: Starting...")
    
    content_blocks = state.get("content_blocks", {})
    product_model = state.get("product_model")
    
    if not product_model:
        error_msg = "No product model found in state"
        print(f"❌ Error: {error_msg}")
        return {
            "errors": [error_msg],
            "agent_trace": ["product_page_builder_agent"],
            "timestamp": datetime.now().isoformat()
        }
    
    if not content_blocks:
        error_msg = "No content blocks found in state"
        print(f"❌ Error: {error_msg}")
        return {
            "errors": [error_msg],
            "agent_trace": ["product_page_builder_agent"],
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        print("🔨 Assembling product page sections...")
        
        # Extract content from blocks
        overview_block = content_blocks.get("overview")
        benefits_block = content_blocks.get("benefits")
        ingredients_block = content_blocks.get("ingredients")
        usage_block = content_blocks.get("usage")
        safety_block = content_blocks.get("safety")
        price_block = content_blocks.get("price")
        
        # Build overview section
        overview_content = ""
        if overview_block:
            overview_content = overview_block.content if isinstance(overview_block.content, str) else ""
        print("  ✅ Overview section")
        
        # Build key information section
        key_info = {}
        
        # Ingredients
        if ingredients_block and ingredients_block.validation_status != "missing":
            ing_content = ingredients_block.content
            if isinstance(ing_content, dict):
                key_info["ingredients"] = {
                    "list": ing_content.get("ingredients_list", []),
                    "count": ing_content.get("count", 0),
                    "description": ing_content.get("formatted_text", "")
                }
            else:
                key_info["ingredients"] = {
                    "description": str(ing_content)
                }
        else:
            key_info["ingredients"] = {
                "description": "Ingredient information not available"
            }
        print("  ✅ Ingredients section")
        
        # Benefits
        if benefits_block and benefits_block.validation_status != "missing":
            ben_content = benefits_block.content
            if isinstance(ben_content, dict):
                key_info["benefits"] = {
                    "list": ben_content.get("benefits_list", []),
                    "summary": ben_content.get("summary", ""),
                    "description": ben_content.get("formatted_text", "")
                }
            else:
                key_info["benefits"] = {
                    "description": str(ben_content)
                }
        else:
            key_info["benefits"] = {
                "description": "Benefit information not available"
            }
        print("  ✅ Benefits section")
        
        # Build usage section
        usage_info = {}
        if usage_block and usage_block.validation_status != "missing":
            usage_content = usage_block.content
            if isinstance(usage_content, dict):
                usage_info = {
                    "instructions": usage_content.get("instructions", ""),
                    "formatted": usage_content.get("formatted_text", "")
                }
            else:
                usage_info = {
                    "instructions": str(usage_content)
                }
        else:
            usage_info = {
                "instructions": "Usage instructions not available. Please refer to product packaging."
            }
        print("  ✅ Usage section")
        
        # Build safety section
        safety_info = {}
        if safety_block:
            safety_content = safety_block.content
            if isinstance(safety_content, dict):
                safety_info = {
                    "warnings": safety_content.get("warnings", "No known warnings"),
                    "recommendation": safety_content.get("recommendation", ""),
                    "formatted": safety_content.get("formatted_text", "")
                }
            else:
                safety_info = {
                    "warnings": str(safety_content)
                }
        else:
            safety_info = {
                "warnings": "No safety information available"
            }
        print("  ✅ Safety section")
        
        # Build pricing section
        pricing_info = {}
        if price_block:
            price_content = price_block.content
            if isinstance(price_content, dict):
                pricing_info = {
                    "price": price_content.get("price"),
                    "currency": price_content.get("currency"),
                    "formatted_price": price_content.get("formatted_price"),
                    "value_proposition": price_content.get("value_proposition", "")
                }
            else:
                pricing_info = {
                    "price": product_model.price,
                    "currency": product_model.currency,
                    "formatted_price": f"{product_model.currency}{product_model.price}"
                }
        else:
            pricing_info = {
                "price": product_model.price,
                "currency": product_model.currency,
                "formatted_price": f"{product_model.currency}{product_model.price}"
            }
        print("  ✅ Pricing section")
        
        # Build additional info section
        additional_info = {}
        
        if product_model.target_audience:
            additional_info["target_audience"] = product_model.target_audience
        
        if product_model.category:
            additional_info["category"] = product_model.category
        
        if product_model.custom_fields:
            additional_info["custom_attributes"] = product_model.custom_fields
        
        if additional_info:
            print("  ✅ Additional info section")
        
        # Build final product page structure
        product_page = {
            "page_type": "product_page",
            "product": {
                "name": product_model.name,
                "overview": overview_content,
                "key_information": key_info,
                "how_to_use": usage_info,
                "safety_information": safety_info,
                "pricing": pricing_info,
                "additional_information": additional_info
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "product_id": product_model.product_id,
                "completeness_score": product_model.completeness_score,
                "field_count": product_model.field_count,
                "blocks_used": list(content_blocks.keys())
            }
        }
        
        print(f"\n✅ Product page built successfully")
        print(f"   Product: {product_model.name}")
        print(f"   Completeness: {product_model.completeness_score}%")
        print(f"   Sections: {len([k for k in product_page['product'].keys() if product_page['product'][k]])}")
        
        return {
            "product_page": product_page,
            "agent_trace": ["product_page_builder_agent"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"Failed to build product page: {str(e)}"
        print(f"❌ Error: {error_msg}")
        return {
            "errors": [error_msg],
            "agent_trace": ["product_page_builder_agent"],
            "timestamp": datetime.now().isoformat()
        }


# Agent metadata
AGENT_INFO = {
    "name": "Product Page Builder Agent",
    "responsibility": "Assemble comprehensive product page from content blocks",
    "reads_from_state": ["content_blocks", "product_model"],
    "writes_to_state": ["product_page", "agent_trace"],
    "dependencies": ["content_logic_agent"]
}