"""Quick test for ContentBlock model"""
from src.models.content_block_model import ContentBlock

# Test 1: Text content block
text_block = ContentBlock(
    block_id="benefits_001",
    block_type="benefits",
    content="This product brightens skin and fades dark spots effectively.",
    source_fields=["benefits", "key_ingredients"]
)

print("✅ Text ContentBlock created!")
print(f"Block ID: {text_block.block_id}")
print(f"Token count: {text_block.token_count}")
print(f"Status: {text_block.validation_status}")

# Test 2: Structured content block
structured_block = ContentBlock(
    block_id="ingredients_001",
    block_type="ingredients",
    content={
        "primary": ["Vitamin C", "Hyaluronic Acid"],
        "concentration": "10% Vitamin C"
    },
    format="structured_data",
    source_fields=["key_ingredients"]
)

print("\n✅ Structured ContentBlock created!")
print(f"Content type: {type(structured_block.content)}")
print(f"Format: {structured_block.format}")

# Test 3: Invalid block type (should raise error)
try:
    invalid_block = ContentBlock(
        block_id="test_001",
        block_type="invalid_type",  # Should fail
        content="Test"
    )
except ValueError as e:
    print(f"\n✅ Validation works! Caught error: {e}")