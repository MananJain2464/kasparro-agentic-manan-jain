"""
Question Generator Agent (LLM-Powered)
Generates categorized questions with answers using AI
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import json
from typing import Dict, Any, List
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.models.product_model import ProductModel
from src.models.question_model import QuestionModel
from src.models.state_model import WorkflowState
from src.config import MIN_QUESTIONS, QUESTION_CATEGORIES, OPENAI_MODEL, OPENAI_TEMPERATURE


def generate_questions(state: WorkflowState) -> Dict[str, Any]:
    """
    Question Generator Agent (LLM-Powered)
    
    Reads: product_model from state
    Writes: questions, questions_by_category, agent_trace
    
    Uses LLM to generate contextual questions based on product data
    """
    print("\n❓ Question Generator Agent: Starting...")
    
    product_model = state.get("product_model")
    
    if not product_model:
        error_msg = "No product model found in state"
        print(f"❌ Error: {error_msg}")
        return {
            "errors": [error_msg],
            "agent_trace": ["question_generator_agent"],
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # Initialize LLM
        llm = ChatOpenAI(
            model=OPENAI_MODEL,
            temperature=OPENAI_TEMPERATURE
        )
        
        # Build product context for prompt
        product_context = _build_product_context(product_model)
        
        # Create prompt
        system_prompt = f"""You are an expert question generator for product information.

Your task: Generate {MIN_QUESTIONS} diverse, user-focused questions about the given product with accurate answers.

REQUIREMENTS:
1. Generate EXACTLY {MIN_QUESTIONS} or more questions
2. Each question must have a clear, accurate answer based ONLY on the provided product data
3. Distribute questions across these categories: {', '.join(QUESTION_CATEGORIES)}
4. Questions should be natural and user-focused (what real customers would ask)
5. Answers must be factual, concise, and derived from product information
6. If data is missing for a question, provide a generic but helpful answer

OUTPUT FORMAT (strict JSON):
{{
  "questions": [
    {{
      "question_text": "Question here?",
      "answer": "Answer here based on product data.",
      "category": "One of the valid categories",
      "related_fields": ["field1", "field2"],
      "priority": "high/medium/low"
    }}
  ]
}}

VALID CATEGORIES: {', '.join(QUESTION_CATEGORIES)}

Return ONLY the JSON object, no other text."""

        user_prompt = f"""Product Information:
{product_context}

Generate {MIN_QUESTIONS} comprehensive questions with answers for this product."""

        # Call LLM
        print("🤖 Calling LLM to generate questions...")
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
        
        questions_data = json.loads(response_text)
        
        # Convert to QuestionModel objects
        questions = []
        for q_data in questions_data.get("questions", []):
            try:
                question = QuestionModel(
                    question_text=q_data["question_text"],
                    answer=q_data["answer"],
                    category=q_data["category"],
                    related_fields=q_data.get("related_fields", []),
                    priority=q_data.get("priority", "medium"),
                    generated_from="llm"
                )
                questions.append(question)
            except Exception as e:
                print(f"⚠️  Skipping invalid question: {e}")
                continue
        
        if len(questions) < MIN_QUESTIONS:
            warning_msg = f"Generated {len(questions)} questions, expected {MIN_QUESTIONS}"
            print(f"⚠️  Warning: {warning_msg}")
            # Don't fail, just warn
        
        # Organize by category
        questions_by_category = {}
        for question in questions:
            category = question.category
            if category not in questions_by_category:
                questions_by_category[category] = []
            questions_by_category[category].append(question)
        
        print(f"✅ Generated {len(questions)} questions across {len(questions_by_category)} categories")
        for category, cat_questions in questions_by_category.items():
            print(f"   {category}: {len(cat_questions)} questions")
        
        return {
            "questions": questions,
            "questions_by_category": questions_by_category,
            "agent_trace": ["question_generator_agent"],
            "timestamp": datetime.now().isoformat()
        }
        
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse LLM response as JSON: {str(e)}"
        print(f"❌ Error: {error_msg}")
        print(f"Raw response: {response_text[:500]}")
        return {
            "errors": [error_msg],
            "agent_trace": ["question_generator_agent"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        error_msg = f"Failed to generate questions: {str(e)}"
        print(f"❌ Error: {error_msg}")
        return {
            "errors": [error_msg],
            "agent_trace": ["question_generator_agent"],
            "timestamp": datetime.now().isoformat()
        }


def _build_product_context(product: ProductModel) -> str:
    """Build comprehensive product context for LLM prompt"""
    context_parts = [
        f"Product Name: {product.name}",
        f"Price: {product.currency}{product.price}"
    ]
    
    if product.category:
        context_parts.append(f"Category: {product.category}")
    
    if product.key_ingredients:
        ingredients_list = []
        for ing in product.key_ingredients:
            ing_str = ing.name
            if ing.concentration:
                ing_str += f" ({ing.concentration})"
            if ing.purpose:
                ing_str += f" - {ing.purpose}"
            ingredients_list.append(ing_str)
        context_parts.append(f"Key Ingredients:\n  - " + "\n  - ".join(ingredients_list))
    
    if product.benefits:
        context_parts.append(f"Benefits:\n  - " + "\n  - ".join(product.benefits))
    
    if product.usage_instructions:
        context_parts.append(f"Usage Instructions: {product.usage_instructions}")
    
    if product.side_effects:
        context_parts.append(f"Side Effects/Warnings: {product.side_effects}")
    
    if product.target_audience:
        context_parts.append(f"Target Audience: {', '.join(product.target_audience)}")
    
    if product.custom_fields:
        custom = "\n  - ".join([f"{k}: {v}" for k, v in product.custom_fields.items()])
        context_parts.append(f"Additional Info:\n  - {custom}")
    
    return "\n".join(context_parts)


# Agent metadata
AGENT_INFO = {
    "name": "Question Generator Agent (LLM-Powered)",
    "responsibility": "Generate contextual questions with answers using AI",
    "reads_from_state": ["product_model"],
    "writes_to_state": ["questions", "questions_by_category", "agent_trace"],
    "dependencies": ["data_parser_agent"]
}