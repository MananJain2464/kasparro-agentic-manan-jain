"""Quick test for ProductModel"""
print("Script started")

from src.models.product_models import ProductModel

# Test data
test_data = {
    "name": "GlowBoost Vitamin C Serum",
    "price": 699,
    "currency": "₹",
    "key_ingredients": [
        {"name": "Vitamin C", "concentration": "10%"},
        "Hyaluronic Acid"  # Simple string format
    ],
    "benefits": ["Brightening", "Fades dark spots"],
    "target_audience": ["Oily skin"]
}

product = ProductModel(**test_data)
print("✅ ProductModel created successfully!")
print(f"Product ID: {product.product_id}")
print(f"Completeness: {product.completeness_score}%")
print(f"Ingredients: {[ing.name for ing in product.key_ingredients]}")