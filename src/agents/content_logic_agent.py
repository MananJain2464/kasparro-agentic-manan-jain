"""
Content Logic Agent
Generates reusable content blocks from product data
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.models.product_model import ProductModel
from src.models.question_model import QuestionModel
from src.models.content_block_model import ContentBlock
from src.models.state_model import WorkflowState
from src.config import OPENAI_MODEL, OPENAI_TEMPERATURE


class ContentBlockGenerator:
    """Generates various types of content blocks"""
    
    def __init__(self, use_llm_enhancement: bool = True):
        self.use_llm_enhancement = use_llm_enhancement
        if use_llm_enhancement:
            self.llm = ChatOpenAI(model=OPENAI_MODEL, temperature=OPENAI_TEMPERATURE)
    
    def generate_overview_block(self, product: ProductModel) -> ContentBlock:
        """Generate product overview block"""
        # Rule-based generation
        parts = [f"{product.name}"]
        
        if product.category:
            parts.append(f"is a {product.category}")
        
        if product.key_ingredients and len(product.key_ingredients) > 0:
            key_ing = product.key_ingredients[0].name
            parts.append(f"featuring {key_ing}")
        
        if product.benefits and len(product.benefits) > 0:
            parts.append(f"designed to provide {product.benefits[0].lower()}")
        
        content = " ".join(parts) + "."
        
        # Optional LLM enhancement for more natural flow
        if self.use_llm_enhancement and product.completeness_score > 50:
            content = self._enhance_overview(product, content)
        
        return ContentBlock(
            block_id="overview_block",
            block_type="overview",
            content=content,
            source_fields=["name", "category", "key_ingredients", "benefits"],
            format="plain_text",
            reusable=True,
            validation_status="complete"
        )
    
    def generate_benefits_block(self, product: ProductModel) -> ContentBlock:
        """Generate benefits content block"""
        if not product.benefits or len(product.benefits) == 0:
            content = "Benefit information is currently unavailable for this product."
            status = "missing"
        else:
            # Structured format
            content = {
                "summary": f"{product.name} offers multiple benefits for users.",
                "benefits_list": product.benefits,
                "formatted_text": f"{product.name} provides {', '.join(product.benefits).lower()}."
            }
            status = "complete"
        
        return ContentBlock(
            block_id="benefits_block",
            block_type="benefits",
            content=content,
            source_fields=["benefits", "name"],
            format="structured_data" if isinstance(content, dict) else "plain_text",
            reusable=True,
            validation_status=status
        )
    
    def generate_ingredients_block(self, product: ProductModel) -> ContentBlock:
        """Generate ingredients content block"""
        if not product.key_ingredients or len(product.key_ingredients) == 0:
            content = "Ingredient information is currently unavailable for this product."
            status = "missing"
        else:
            # Structured format with details
            ingredients_data = []
            for ing in product.key_ingredients:
                ing_info = {
                    "name": ing.name,
                    "concentration": ing.concentration,
                    "purpose": ing.purpose
                }
                ingredients_data.append(ing_info)
            
            # Create formatted text
            ing_details = []
            for ing in product.key_ingredients:
                detail = ing.name
                if ing.concentration:
                    detail += f" ({ing.concentration})"
                if ing.purpose:
                    detail += f" for {ing.purpose.lower()}"
                ing_details.append(detail)
            
            content = {
                "ingredients_list": ingredients_data,
                "formatted_text": f"Key ingredients include: {', '.join(ing_details)}.",
                "count": len(product.key_ingredients)
            }
            status = "complete"
        
        return ContentBlock(
            block_id="ingredients_block",
            block_type="ingredients",
            content=content,
            source_fields=["key_ingredients"],
            format="structured_data" if isinstance(content, dict) else "plain_text",
            reusable=True,
            validation_status=status
        )
    
    def generate_usage_block(self, product: ProductModel) -> ContentBlock:
        """Generate usage instructions block"""
        if not product.usage_instructions:
            content = "Usage instructions are not available. Please refer to product packaging or consult a professional."
            status = "partial"
        else:
            content = {
                "instructions": product.usage_instructions,
                "formatted_text": f"How to use: {product.usage_instructions}"
            }
            status = "complete"
        
        return ContentBlock(
            block_id="usage_block",
            block_type="usage",
            content=content,
            source_fields=["usage_instructions"],
            format="structured_data" if isinstance(content, dict) else "plain_text",
            reusable=True,
            validation_status=status
        )
    
    def generate_safety_block(self, product: ProductModel) -> ContentBlock:
        """Generate safety/side effects block"""
        if not product.side_effects:
            content = {
                "warnings": "No known side effects reported.",
                "recommendation": "As with any product, discontinue use if irritation occurs.",
                "formatted_text": "This product is generally considered safe. Discontinue use if any adverse reactions occur."
            }
            status = "partial"
        else:
            content = {
                "warnings": product.side_effects,
                "recommendation": "Consult a healthcare professional if you have concerns.",
                "formatted_text": f"Safety information: {product.side_effects}"
            }
            status = "complete"
        
        return ContentBlock(
            block_id="safety_block",
            block_type="safety",
            content=content,
            source_fields=["side_effects"],
            format="structured_data",
            reusable=True,
            validation_status=status
        )
    
    def generate_price_block(self, product: ProductModel) -> ContentBlock:
        """Generate pricing block"""
        # Determine value proposition
        if product.price < 300:
            value_prop = "an affordable"
        elif product.price < 800:
            value_prop = "a reasonably priced"
        else:
            value_prop = "a premium"
        
        content = {
            "price": product.price,
            "currency": product.currency,
            "formatted_price": f"{product.currency}{product.price}",
            "value_proposition": f"{product.name} is {value_prop} option at {product.currency}{product.price}."
        }
        
        return ContentBlock(
            block_id="price_block",
            block_type="price",
            content=content,
            source_fields=["price", "currency", "name"],
            format="structured_data",
            reusable=True,
            validation_status="complete"
        )
    
    def generate_comparison_block(
        self, 
        product_a: ProductModel, 
        product_b: ProductModel
    ) -> ContentBlock:
        """Generate product comparison block"""
        
        # Ingredient comparison
        a_ingredients = {ing.name for ing in product_a.key_ingredients} if product_a.key_ingredients else set()
        b_ingredients = {ing.name for ing in product_b.key_ingredients} if product_b.key_ingredients else set()
        
        ingredient_overlap = a_ingredients.intersection(b_ingredients)
        a_unique = a_ingredients - b_ingredients
        b_unique = b_ingredients - a_ingredients
        
        # Price comparison
        price_diff = product_b.price - product_a.price
        price_diff_percent = (price_diff / product_a.price) * 100
        
        cheaper_product = product_a.name if price_diff > 0 else product_b.name
        
        # Benefits comparison
        a_benefits = set(product_a.benefits) if product_a.benefits else set()
        b_benefits = set(product_b.benefits) if product_b.benefits else set()
        
        benefit_overlap = a_benefits.intersection(b_benefits)
        a_unique_benefits = a_benefits - b_benefits
        b_unique_benefits = b_benefits - a_benefits
        
        content = {
            "products": {
                "product_a": product_a.name,
                "product_b": product_b.name
            },
            "price_comparison": {
                "product_a_price": f"{product_a.currency}{product_a.price}",
                "product_b_price": f"{product_b.currency}{product_b.price}",
                "difference": f"{product_b.currency}{abs(price_diff)}",
                "percentage_difference": f"{abs(price_diff_percent):.1f}%",
                "cheaper_product": cheaper_product
            },
            "ingredient_comparison": {
                "common_ingredients": list(ingredient_overlap),
                f"{product_a.name}_unique": list(a_unique),
                f"{product_b.name}_unique": list(b_unique),
                "similarity_score": len(ingredient_overlap) / max(len(a_ingredients), len(b_ingredients), 1)
            },
            "benefit_comparison": {
                "common_benefits": list(benefit_overlap),
                f"{product_a.name}_unique": list(a_unique_benefits),
                f"{product_b.name}_unique": list(b_unique_benefits)
            },
            "summary": self._generate_comparison_summary(
                product_a, product_b, cheaper_product, price_diff_percent
            )
        }
        
        return ContentBlock(
            block_id="comparison_block",
            block_type="comparison",
            content=content,
            source_fields=["product_a", "product_b"],
            format="structured_data",
            reusable=True,
            validation_status="complete"
        )
    
    def generate_faq_answers_blocks(
        self, 
        questions: List[QuestionModel]
    ) -> List[ContentBlock]:
        """Generate content blocks for FAQ answers"""
        faq_blocks = []
        
        for i, question in enumerate(questions):
            block = ContentBlock(
                block_id=f"faq_answer_{i+1}",
                block_type="faq_answer",
                content={
                    "question": question.question_text,
                    "answer": question.answer,
                    "category": question.category,
                    "priority": question.priority
                },
                source_fields=question.related_fields,
                format="structured_data",
                reusable=False,  # FAQ-specific
                validation_status="complete"
            )
            faq_blocks.append(block)
        
        return faq_blocks
    
    def _enhance_overview(self, product: ProductModel, base_content: str) -> str:
        """Use LLM to enhance overview for more natural flow"""
        try:
            prompt = f"""Rewrite this product overview to be more engaging and natural, keep it concise (2-3 sentences max):

Current: {base_content}

Product details:
- Name: {product.name}
- Category: {product.category}
- Key benefits: {', '.join(product.benefits[:3]) if product.benefits else 'N/A'}

Return only the enhanced overview text, nothing else."""

            response = self.llm.invoke([HumanMessage(content=prompt)])
            enhanced = response.content.strip()
            return enhanced if len(enhanced) > 10 else base_content
        except:
            return base_content
    
    def _generate_comparison_summary(
        self, 
        product_a: ProductModel, 
        product_b: ProductModel,
        cheaper: str,
        price_diff: float
    ) -> str:
        """Generate comparison summary text"""
        summary = f"{product_a.name} and {product_b.name} are both {product_a.category or 'products'} options. "
        summary += f"{cheaper} is more affordable with a {abs(price_diff):.1f}% price difference. "
        
        if product_a.key_ingredients and product_b.key_ingredients:
            summary += f"{product_a.name} features {product_a.key_ingredients[0].name}, "
            summary += f"while {product_b.name} uses {product_b.key_ingredients[0].name}. "
        
        return summary


def generate_content_blocks(state: WorkflowState) -> Dict[str, Any]:
    """
    Content Logic Agent
    
    Reads: product_model, product_b_model, questions from state
    Writes: content_blocks, agent_trace
    
    Generates all reusable content blocks from product data
    """
    print("\n📝 Content Logic Agent: Starting...")
    
    product_model = state.get("product_model")
    product_b_model = state.get("product_b_model")
    questions = state.get("questions", [])
    
    if not product_model:
        error_msg = "No product model found in state"
        print(f"❌ Error: {error_msg}")
        return {
            "errors": [error_msg],
            "agent_trace": ["content_logic_agent"],
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        generator = ContentBlockGenerator(use_llm_enhancement=True)
        
        print("🔨 Generating content blocks...")
        
        # Generate core product blocks
        blocks = {}
        
        blocks["overview"] = generator.generate_overview_block(product_model)
        print(f"  ✅ Overview block")
        
        blocks["benefits"] = generator.generate_benefits_block(product_model)
        print(f"  ✅ Benefits block")
        
        blocks["ingredients"] = generator.generate_ingredients_block(product_model)
        print(f"  ✅ Ingredients block")
        
        blocks["usage"] = generator.generate_usage_block(product_model)
        print(f"  ✅ Usage block")
        
        blocks["safety"] = generator.generate_safety_block(product_model)
        print(f"  ✅ Safety block")
        
        blocks["price"] = generator.generate_price_block(product_model)
        print(f"  ✅ Price block")
        
        # Generate comparison block if Product B exists
        if product_b_model:
            blocks["comparison"] = generator.generate_comparison_block(
                product_model, 
                product_b_model
            )
            print(f"  ✅ Comparison block")
        
        # Generate FAQ answer blocks
        if questions:
            faq_blocks = generator.generate_faq_answers_blocks(questions)
            blocks["faq_answers"] = faq_blocks
            print(f"  ✅ FAQ answers blocks ({len(faq_blocks)} questions)")
        
        print(f"\n✅ Generated {len(blocks)} content block types")
        
        return {
            "content_blocks": blocks,
            "agent_trace": ["content_logic_agent"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"Failed to generate content blocks: {str(e)}"
        print(f"❌ Error: {error_msg}")
        return {
            "errors": [error_msg],
            "agent_trace": ["content_logic_agent"],
            "timestamp": datetime.now().isoformat()
        }


# Agent metadata
AGENT_INFO = {
    "name": "Content Logic Agent",
    "responsibility": "Generate reusable content blocks from product data",
    "reads_from_state": ["product_model", "product_b_model", "questions"],
    "writes_to_state": ["content_blocks", "agent_trace"],
    "dependencies": ["data_parser_agent", "product_b_generator_agent", "question_generator_agent"]
}