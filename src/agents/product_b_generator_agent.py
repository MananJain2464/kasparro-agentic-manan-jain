"""
Product B Generator Agent (LLM-Powered)
Generates fictional competitor product for comparison
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import json
from typing import Dict, Any
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.models.product_model import ProductModel
from src.models.state_model import WorkflowState
from src.config import OPENAI_MODEL, OPENAI_TEMPERATURE


def generate_product_b(state: WorkflowState) -> Dict[str, Any]:
    """
    Product B Generator Agent (LLM-Powered)
    
    Reads: product_model from state
    Writes: product_b_model, agent_trace
    
    Generates a fictional competitor product for comparison
    """
    print("\n🏭 Product B Generator Agent: Starting...")
    
    product_model = state.get("product_model")
    
    if not product_model:
        error_msg = "No product model found in state"
        print(f"❌ Error: {error_msg}")
        return {
            "errors": [error_msg],
            "agent_trace": ["product_b_generator_agent"],
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # Initialize LLM
        llm = ChatOpenAI(
            model=OPENAI_MODEL,
            temperature=OPENAI_TEMPERATURE
        )
        
        # Build Product A context
        product_a_context = _build_product_context(product_model)
        
        # Create prompt for Product B generation
        system_prompt = """You are a product development expert creating a fictional competitor product.

Your task: Generate a realistic competitor product (Product B) that can be compared with Product A.

REQUIREMENTS:
1. Product B must be in the SAME category as Product A
2. Product B must have DIFFERENT key ingredients (no exact matches)
3. Product B price should be within 20-40% range of Product A (can be higher or lower)
4. Product B should offer DIFFERENT but comparable benefits
5. Product B must be realistic and believable
6. Include all standard fields (name, price, ingredients, benefits, usage, etc.)

OUTPUT FORMAT (strict JSON matching ProductModel schema):
{
  "name": "Product B name (creative, realistic)",
  "price": numeric_value,
  "currency": "same as Product A",
  "category": "same as Product A",
  "key_ingredients": [
    {"name": "Ingredient name", "concentration": "optional", "purpose": "optional"}
  ],
  "benefits": ["benefit1", "benefit2", "benefit3"],
  "usage_instructions": "How to use Product B",
  "side_effects": "Any warnings or side effects",
  "target_audience": ["audience1", "audience2"]
}

IMPORTANT:
- Make Product B different enough to be interesting for comparison
- Ensure ingredients DON'T overlap with Product A
- Keep the same product domain (skincare, food, supplement, etc.)
- Make it realistic - could be an actual product

Return ONLY the JSON object, no other text."""

        user_prompt = f"""Product A (for reference):
{product_a_context}

Generate Product B - a realistic competitor product that:
1. Targets the same market but with different ingredients
2. Has a price within 20-40% of Product A's price
3. Offers comparable but distinct benefits
4. Is believable as a real competitor product"""

        # Call LLM
        print("🤖 Calling LLM to generate competitor product...")
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        # Parse response
        response_text = response.content.strip()
        
        # Extract JSON (handle markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        product_b_data = json.loads(response_text)
        
        # Validate by creating ProductModel
        product_b_model = ProductModel(**product_b_data)
        
        # Add comparison metadata
        price_diff_percent = abs(product_b_model.price - product_model.price) / product_model.price * 100
        
        print(f"✅ Generated competitor: {product_b_model.name}")
        print(f"   Category: {product_b_model.category}")
        print(f"   Price: {product_b_model.currency}{product_b_model.price} ({price_diff_percent:.1f}% difference)")
        print(f"   Ingredients: {len(product_b_model.key_ingredients)} items")
        print(f"   Benefits: {len(product_b_model.benefits)} items")
        
        # Check for ingredient overlap (should be minimal)
        if product_model.key_ingredients and product_b_model.key_ingredients:
            a_ingredients = {ing.name.lower() for ing in product_model.key_ingredients}
            b_ingredients = {ing.name.lower() for ing in product_b_model.key_ingredients}
            overlap = a_ingredients.intersection(b_ingredients)
            
            if overlap:
                print(f"   ⚠️  Ingredient overlap detected: {overlap}")
            else:
                print(f"   ✅ No ingredient overlap - good differentiation")
        
        return {
            "product_b_model": product_b_model,
            "agent_trace": ["product_b_generator_agent"],
            "timestamp": datetime.now().isoformat()
        }
        
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse LLM response as JSON: {str(e)}"
        print(f"❌ Error: {error_msg}")
        print(f"Raw response: {response_text[:500]}")
        return {
            "errors": [error_msg],
            "agent_trace": ["product_b_generator_agent"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        error_msg = f"Failed to generate Product B: {str(e)}"
        print(f"❌ Error: {error_msg}")
        return {
            "errors": [error_msg],
            "agent_trace": ["product_b_generator_agent"],
            "timestamp": datetime.now().isoformat()
        }


def _build_product_context(product: ProductModel) -> str:
    """Build product context for LLM prompt"""
    context_parts = [
        f"Name: {product.name}",
        f"Price: {product.currency}{product.price}",
        f"Category: {product.category or 'General'}"
    ]
    
    if product.key_ingredients:
        ingredients = [ing.name for ing in product.key_ingredients]
        context_parts.append(f"Key Ingredients: {', '.join(ingredients)}")
    
    if product.benefits:
        context_parts.append(f"Benefits: {', '.join(product.benefits)}")
    
    if product.target_audience:
        context_parts.append(f"Target Audience: {', '.join(product.target_audience)}")
    
    return "\n".join(context_parts)


# Agent metadata
AGENT_INFO = {
    "name": "Product B Generator Agent (LLM-Powered)",
    "responsibility": "Generate fictional competitor product for comparison",
    "reads_from_state": ["product_model"],
    "writes_to_state": ["product_b_model", "agent_trace"],
    "dependencies": ["data_parser_agent"]
}