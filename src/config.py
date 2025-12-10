"""
Configuration settings for the content generation system
"""
import os
from pathlib import Path
import tempfile

# For local development
if Path("outputs").exists() or not Path("/tmp").exists():
    OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"
else:
    # For Streamlit Cloud - use temp directory
    OUTPUTS_DIR = Path(tempfile.gettempdir()) / "outputs"

OUTPUTS_DIR.mkdir(exist_ok=True, parents=True)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
# OUTPUTS_DIR = PROJECT_ROOT / "outputs"
TEMPLATES_DIR = PROJECT_ROOT / "src" / "templates"

# Ensure outputs directory exists
# OUTPUTS_DIR.mkdir(exist_ok=True)

# OpenAI settings
OPENAI_MODEL = "gpt-4o-mini"  # Model for all LLM calls
OPENAI_TEMPERATURE = 0.7  # Balance between creativity and consistency
OPENAI_MAX_TOKENS = 2000  # Maximum response length

# Question generation settings
MIN_QUESTIONS = 15  # Minimum questions to generate
QUESTION_CATEGORIES = [
    "Informational",
    "Safety", 
    "Usage",
    "Benefits",
    "Purchase",
    "Comparison",
    "Ingredients",
    "Compatibility",
    "Storage",
    "Results",
    "Alternatives",
    "Suitability",
    "Application",
    "Value",
    "Concerns"
]

# Product B generation settings
PRODUCT_B_SIMILARITY_THRESHOLD = 0.6  # How similar Product B should be (0-1)

# Content block types
CONTENT_BLOCK_TYPES = [
    "overview",
    "benefits",
    "usage",
    "ingredients",
    "safety",
    "price",
    "comparison",
    "faq_answer" 
]

# Output file names
FAQ_OUTPUT_FILE = "faq.json"
PRODUCT_PAGE_OUTPUT_FILE = "product_page.json"
COMPARISON_OUTPUT_FILE = "comparison_page.json"