"""
FAQ Builder Agent
Assembles FAQ page from content blocks
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import Dict, Any, List
from datetime import datetime
from src.models.content_block_model import ContentBlock
from src.models.state_model import WorkflowState


def build_faq_page(state: WorkflowState) -> Dict[str, Any]:
    """
    FAQ Builder Agent
    
    Reads: content_blocks (specifically faq_answers), product_model from state
    Writes: faq_page, agent_trace
    
    Assembles FAQ page JSON from FAQ answer blocks
    """
    print("\n❓ FAQ Builder Agent: Starting...")
    
    content_blocks = state.get("content_blocks", {})
    product_model = state.get("product_model")
    
    if not product_model:
        error_msg = "No product model found in state"
        print(f"❌ Error: {error_msg}")
        return {
            "errors": [error_msg],
            "agent_trace": ["faq_builder_agent"],
            "timestamp": datetime.now().isoformat()
        }
    
    if not content_blocks:
        error_msg = "No content blocks found in state"
        print(f"❌ Error: {error_msg}")
        return {
            "errors": [error_msg],
            "agent_trace": ["faq_builder_agent"],
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # Get FAQ answer blocks
        faq_blocks = content_blocks.get("faq_answers", [])
        
        if not faq_blocks or len(faq_blocks) == 0:
            error_msg = "No FAQ answer blocks found in content blocks"
            print(f"❌ Error: {error_msg}")
            return {
                "errors": [error_msg],
                "agent_trace": ["faq_builder_agent"],
                "timestamp": datetime.now().isoformat()
            }
        
        print(f"📋 Processing {len(faq_blocks)} FAQ blocks...")
        
        # Get overview block for page introduction
        overview_block = content_blocks.get("overview")
        overview_text = ""
        if overview_block:
            if isinstance(overview_block.content, str):
                overview_text = overview_block.content
            elif isinstance(overview_block.content, dict):
                overview_text = overview_block.content.get("formatted_text", "")
        
        # Organize FAQs by category
        faqs_by_category = {}
        all_faqs = []
        
        for faq_block in faq_blocks:
            faq_content = faq_block.content
            
            category = faq_content.get("category", "General")
            
            # Create FAQ entry
            faq_entry = {
                "question": faq_content["question"],
                "answer": faq_content["answer"],
                "category": category,
                "priority": faq_content.get("priority", "medium")
            }
            
            all_faqs.append(faq_entry)
            
            # Organize by category
            if category not in faqs_by_category:
                faqs_by_category[category] = []
            faqs_by_category[category].append(faq_entry)
        
        # Sort FAQs within each category by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        
        for category in faqs_by_category:
            faqs_by_category[category].sort(
                key=lambda x: priority_order.get(x["priority"], 1)
            )
        
        # Build final FAQ page structure
        faq_page = {
            "page_type": "faq",
            "product_name": product_model.name,
            "product_overview": overview_text,
            "total_questions": len(all_faqs),
            "categories": list(faqs_by_category.keys()),
            "faqs": all_faqs,
            "faqs_by_category": faqs_by_category,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "product_id": product_model.product_id,
                "currency": product_model.currency,
                "price": product_model.price
            }
        }
        
        print(f"✅ FAQ page built successfully")
        print(f"   Total questions: {len(all_faqs)}")
        print(f"   Categories: {len(faqs_by_category)}")
        print(f"   Category breakdown:")
        for category, faqs in faqs_by_category.items():
            print(f"     - {category}: {len(faqs)} questions")
        
        return {
            "faq_page": faq_page,
            "agent_trace": ["faq_builder_agent"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"Failed to build FAQ page: {str(e)}"
        print(f"❌ Error: {error_msg}")
        return {
            "errors": [error_msg],
            "agent_trace": ["faq_builder_agent"],
            "timestamp": datetime.now().isoformat()
        }


# Agent metadata
AGENT_INFO = {
    "name": "FAQ Builder Agent",
    "responsibility": "Assemble FAQ page from content blocks",
    "reads_from_state": ["content_blocks", "product_model"],
    "writes_to_state": ["faq_page", "agent_trace"],
    "dependencies": ["content_logic_agent"]
}