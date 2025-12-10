"""
Comparison Page Builder Agent
Assembles product comparison page from content blocks
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import Dict, Any
from datetime import datetime
from src.models.state_model import WorkflowState


def build_comparison_page(state: WorkflowState) -> Dict[str, Any]:
    """
    Comparison Page Builder Agent
    
    Reads: product_model, product_b_model, content_blocks from state
    Writes: comparison_page, agent_trace
    
    Assembles comparison page JSON showing Product A vs Product B
    """
    print("\n🔍 Comparison Page Builder Agent: Starting...")
    
    product_a = state.get("product_model")
    product_b = state.get("product_b_model")
    content_blocks = state.get("content_blocks", {})
    
    if not product_a:
        error_msg = "No product A model found in state"
        print(f"❌ Error: {error_msg}")
        return {
            "errors": [error_msg],
            "agent_trace": ["comparison_page_builder_agent"],
            "timestamp": datetime.now().isoformat()
        }
    
    if not product_b:
        error_msg = "No product B model found in state"
        print(f"❌ Error: {error_msg}")
        return {
            "errors": [error_msg],
            "agent_trace": ["comparison_page_builder_agent"],
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        print("🔨 Assembling comparison page...")
        
        # Get comparison block
        comparison_block = content_blocks.get("comparison")
        
        if not comparison_block:
            # Generate basic comparison if block missing
            comparison_data = _generate_basic_comparison(product_a, product_b)
        else:
            comparison_data = comparison_block.content
        
        # Build product A summary
        product_a_summary = {
            "name": product_a.name,
            "price": product_a.price,
            "currency": product_a.currency,
            "formatted_price": f"{product_a.currency}{product_a.price}",
            "category": product_a.category,
            "key_ingredients": [
                {
                    "name": ing.name,
                    "concentration": ing.concentration,
                    "purpose": ing.purpose
                } for ing in product_a.key_ingredients
            ] if product_a.key_ingredients else [],
            "benefits": product_a.benefits if product_a.benefits else [],
            "target_audience": product_a.target_audience if product_a.target_audience else [],
            "product_id": product_a.product_id
        }
        print("  ✅ Product A summary")
        
        # Build product B summary
        product_b_summary = {
            "name": product_b.name,
            "price": product_b.price,
            "currency": product_b.currency,
            "formatted_price": f"{product_b.currency}{product_b.price}",
            "category": product_b.category,
            "key_ingredients": [
                {
                    "name": ing.name,
                    "concentration": ing.concentration,
                    "purpose": ing.purpose
                } for ing in product_b.key_ingredients
            ] if product_b.key_ingredients else [],
            "benefits": product_b.benefits if product_b.benefits else [],
            "target_audience": product_b.target_audience if product_b.target_audience else [],
            "product_id": product_b.product_id
        }
        print("  ✅ Product B summary")
        
        # Extract comparison data
        if isinstance(comparison_data, dict):
            price_comparison = comparison_data.get("price_comparison", {})
            ingredient_comparison = _normalize_ingredient_comparison(
                comparison_data.get("ingredient_comparison", {}),
                product_a,
                product_b,
            )
            benefit_comparison = _normalize_benefit_comparison(
                comparison_data.get("benefit_comparison", {}),
                product_a,
                product_b,
            )
            summary_text = comparison_data.get("summary", "")
        else:
            # Fallback if comparison data is not structured
            price_comparison = _compare_prices(product_a, product_b)
            ingredient_comparison = _compare_ingredients(product_a, product_b)
            benefit_comparison = _compare_benefits(product_a, product_b)
            summary_text = f"Comparing {product_a.name} and {product_b.name}."
        
        print("  ✅ Comparison analysis")
        
        # Generate recommendations
        recommendations = _generate_recommendations(
            product_a, product_b, price_comparison, ingredient_comparison
        )
        print("  ✅ Recommendations")
        
        # Build final comparison page
        comparison_page = {
            "page_type": "comparison",
            "product_a": product_a_summary,
            "product_b": product_b_summary,
            "comparison": {
                "price": price_comparison,
                "ingredients": ingredient_comparison,
                "benefits": benefit_comparison,
                "summary": summary_text
            },
            "recommendations": recommendations,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "comparison_id": f"comp_{product_a.product_id}_{product_b.product_id}",
                "product_a_completeness": product_a.completeness_score,
                "product_b_completeness": product_b.completeness_score
            }
        }
        
        print(f"\n✅ Comparison page built successfully")
        print(f"   Product A: {product_a.name} ({product_a.currency}{product_a.price})")
        print(f"   Product B: {product_b.name} ({product_b.currency}{product_b.price})")
        
        if isinstance(price_comparison, dict):
            print(f"   Price difference: {price_comparison.get('percentage_difference', 'N/A')}")
        if isinstance(ingredient_comparison, dict):
            print(f"   Ingredient similarity: {ingredient_comparison.get('similarity_score', 0):.2f}")
        
        return {
            "comparison_page": comparison_page,
            "agent_trace": ["comparison_page_builder_agent"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"Failed to build comparison page: {str(e)}"
        print(f"❌ Error: {error_msg}")
        return {
            "errors": [error_msg],
            "agent_trace": ["comparison_page_builder_agent"],
            "timestamp": datetime.now().isoformat()
        }


def _generate_basic_comparison(product_a, product_b) -> Dict[str, Any]:
    """Generate basic comparison if comparison block is missing"""
    return {
        "price_comparison": _compare_prices(product_a, product_b),
        "ingredient_comparison": _compare_ingredients(product_a, product_b),
        "benefit_comparison": _compare_benefits(product_a, product_b),
        "summary": f"Basic comparison between {product_a.name} and {product_b.name}."
    }


def _compare_prices(product_a, product_b) -> Dict[str, Any]:
    """Compare prices between two products"""
    price_diff = product_b.price - product_a.price
    price_diff_percent = (price_diff / product_a.price) * 100
    
    cheaper_product = product_a.name if price_diff > 0 else product_b.name
    more_expensive = product_b.name if price_diff > 0 else product_a.name
    
    return {
        "product_a_price": f"{product_a.currency}{product_a.price}",
        "product_b_price": f"{product_b.currency}{product_b.price}",
        "difference": f"{product_a.currency}{abs(price_diff)}",
        "percentage_difference": f"{abs(price_diff_percent):.1f}%",
        "cheaper_product": cheaper_product,
        "more_expensive_product": more_expensive,
        "analysis": f"{cheaper_product} is {abs(price_diff_percent):.1f}% cheaper than {more_expensive}."
    }


def _compare_ingredients(product_a, product_b) -> Dict[str, Any]:
    """Compare ingredients between two products"""
    a_ingredients = {ing.name.lower() for ing in product_a.key_ingredients} if product_a.key_ingredients else set()
    b_ingredients = {ing.name.lower() for ing in product_b.key_ingredients} if product_b.key_ingredients else set()
    
    common = a_ingredients.intersection(b_ingredients)
    a_unique = a_ingredients - b_ingredients
    b_unique = b_ingredients - a_ingredients
    
    similarity_score = len(common) / max(len(a_ingredients), len(b_ingredients), 1)
    
    return {
        "common_ingredients": list(common),
        "product_a_unique_ingredients": list(a_unique),
        "product_b_unique_ingredients": list(b_unique),
        "similarity_score": similarity_score,
        "analysis": f"Products share {len(common)} common ingredients. Similarity: {similarity_score:.0%}."
    }


def _compare_benefits(product_a, product_b) -> Dict[str, Any]:
    """Compare benefits between two products"""
    a_benefits = set(product_a.benefits) if product_a.benefits else set()
    b_benefits = set(product_b.benefits) if product_b.benefits else set()
    
    common = a_benefits.intersection(b_benefits)
    a_unique = a_benefits - b_benefits
    b_unique = b_benefits - a_benefits
    
    return {
        "common_benefits": list(common),
        "product_a_unique_benefits": list(a_unique),
        "product_b_unique_benefits": list(b_unique),
        "analysis": f"Both products offer {len(common)} shared benefits."
    }


def _normalize_ingredient_comparison(data: Dict[str, Any], product_a, product_b) -> Dict[str, Any]:
    """
    Ensure ingredient comparison uses canonical keys even if the content block
    used product-name-specific keys (e.g., '{product_a.name}_unique').
    """
    if not isinstance(data, dict):
        return _compare_ingredients(product_a, product_b)
    
    normalized = dict(data)
    
    # Standard keys
    a_key = "product_a_unique_ingredients"
    b_key = "product_b_unique_ingredients"
    
    # If standard keys missing, try to map from name-based keys
    if a_key not in normalized:
        name_key = f"{product_a.name}_unique"
        normalized[a_key] = normalized.get(name_key, [])
    if b_key not in normalized:
        name_key = f"{product_b.name}_unique"
        normalized[b_key] = normalized.get(name_key, [])
    
    return normalized


def _normalize_benefit_comparison(data: Dict[str, Any], product_a, product_b) -> Dict[str, Any]:
    """
    Ensure benefit comparison uses canonical keys even if the content block
    used product-name-specific keys (e.g., '{product_a.name}_unique').
    """
    if not isinstance(data, dict):
        return _compare_benefits(product_a, product_b)
    
    normalized = dict(data)
    
    # Standard keys
    a_key = "product_a_unique_benefits"
    b_key = "product_b_unique_benefits"
    
    if a_key not in normalized:
        name_key = f"{product_a.name}_unique"
        normalized[a_key] = normalized.get(name_key, [])
    if b_key not in normalized:
        name_key = f"{product_b.name}_unique"
        normalized[b_key] = normalized.get(name_key, [])
    
    return normalized


def _generate_recommendations(product_a, product_b, price_comp, ingredient_comp) -> Dict[str, Any]:
    """Generate product recommendations based on comparison"""
    recommendations = {}
    
    # Budget-conscious recommendation
    if isinstance(price_comp, dict):
        cheaper = price_comp.get("cheaper_product")
        recommendations["budget_friendly"] = {
            "product": cheaper,
            "reason": f"{cheaper} offers better value at a lower price point."
        }
    
    # Ingredient-based recommendation
    if isinstance(ingredient_comp, dict):
        similarity = ingredient_comp.get("similarity_score", 0)
        
        if similarity < 0.3:
            recommendations["unique_formulation"] = {
                "note": "These products have significantly different formulations.",
                "suggestion": "Choose based on your specific ingredient preferences."
            }
        else:
            recommendations["similar_products"] = {
                "note": "These products have similar formulations.",
                "suggestion": "Price may be the deciding factor."
            }
    
    # Target audience recommendation
    if product_a.target_audience and product_b.target_audience:
        recommendations["target_audience"] = {
            "product_a": {
                "name": product_a.name,
                "best_for": product_a.target_audience
            },
            "product_b": {
                "name": product_b.name,
                "best_for": product_b.target_audience
            }
        }
    
    # Overall recommendation
    price_factor = 0.4
    ingredient_factor = 0.6
    
    # Simple scoring (lower price is better, higher ingredient variety is better)
    if isinstance(price_comp, dict) and isinstance(ingredient_comp, dict):
        a_price_score = 1 if price_comp.get("cheaper_product") == product_a.name else 0
        a_ing_score = len(ingredient_comp.get("product_a_unique_ingredients", [])) / 10
        
        b_price_score = 1 if price_comp.get("cheaper_product") == product_b.name else 0
        b_ing_score = len(ingredient_comp.get("product_b_unique_ingredients", [])) / 10
        
        a_total = (a_price_score * price_factor) + (a_ing_score * ingredient_factor)
        b_total = (b_price_score * price_factor) + (b_ing_score * ingredient_factor)
        
        if a_total > b_total:
            recommendations["overall"] = {
                "recommended_product": product_a.name,
                "reason": "Better overall value considering price and formulation."
            }
        else:
            recommendations["overall"] = {
                "recommended_product": product_b.name,
                "reason": "Better overall value considering price and formulation."
            }
    
    return recommendations


# Agent metadata
AGENT_INFO = {
    "name": "Comparison Page Builder Agent",
    "responsibility": "Assemble product comparison page",
    "reads_from_state": ["product_model", "product_b_model", "content_blocks"],
    "writes_to_state": ["comparison_page", "agent_trace"],
    "dependencies": ["data_parser_agent", "product_b_generator_agent", "content_logic_agent"]
}