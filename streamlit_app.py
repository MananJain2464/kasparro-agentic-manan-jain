"""
Streamlit UI for Agentic Content Generation System

Provides two input modes:
1. Form Mode: Guided form with predefined fields + ability to add custom fields
2. JSON Mode: Direct JSON paste for advanced users
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import json
from datetime import datetime
from dotenv import load_dotenv
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestrator import run_workflow
from src.config import OUTPUTS_DIR

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Agentic Content Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'custom_fields' not in st.session_state:
        st.session_state.custom_fields = []
    if 'workflow_complete' not in st.session_state:
        st.session_state.workflow_complete = False
    if 'generated_files' not in st.session_state:
        st.session_state.generated_files = []


def add_custom_field():
    """Add a new custom field to the form"""
    st.session_state.custom_fields.append({
        'name': '',
        'value': '',
        'id': len(st.session_state.custom_fields)
    })


def remove_custom_field(field_id):
    """Remove a custom field"""
    st.session_state.custom_fields = [
        f for f in st.session_state.custom_fields if f['id'] != field_id
    ]


def validate_json_input(json_str):
    """Validate JSON input"""
    try:
        data = json.loads(json_str)
        
        # Check required fields
        if 'name' not in data:
            return False, "Missing required field: 'name'"
        if 'price' not in data:
            return False, "Missing required field: 'price'"
        
        # Validate price is numeric
        if not isinstance(data['price'], (int, float)):
            return False, "'price' must be a number"
        
        return True, data
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}"


def render_form_mode():
    """Render form-based input mode"""
    st.markdown("### 📝 Product Information Form")
    st.markdown("Fill in the product details below. Fields marked with * are required.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Basic Information")
        name = st.text_input("Product Name *", placeholder="e.g., GlowBoost Vitamin C Serum")
        price = st.number_input("Price *", min_value=0.0, step=1.0, value=0.0)
        currency = st.text_input("Currency", value="₹", placeholder="e.g., ₹, $, €")
        category = st.text_input("Category", placeholder="e.g., Serum, Snack, Supplement")
        concentration = st.text_input("Concentration/Strength (optional)", placeholder="e.g., 10% Vitamin C")
        
    with col2:
        st.markdown("#### Target & Usage")
        target_audience = st.text_area(
            "Target Audience (one per line, optional)",
            placeholder="Oily skin\nCombination skin\nAdults 25+",
            height=100
        )
        usage_instructions = st.text_area(
            "Usage Instructions (optional)",
            placeholder="Apply 2-3 drops in the morning after cleansing...",
            height=100
        )
        side_effects = st.text_area(
            "Side Effects/Warnings (optional)",
            placeholder="Mild tingling for sensitive skin...",
            height=100
        )
    
    # Ingredients section
    st.markdown("#### 🧪 Ingredients")
    st.markdown("Add product ingredients with optional concentration and purpose.")
    
    num_ingredients = st.number_input("Number of ingredients", min_value=0, max_value=20, value=2, step=1)
    
    ingredients = []
    if num_ingredients > 0:
        for i in range(int(num_ingredients)):
            with st.expander(f"Ingredient {i+1}", expanded=(i < 2)):
                ing_col1, ing_col2, ing_col3 = st.columns([2, 1, 2])
                with ing_col1:
                    ing_name = st.text_input(f"Name *", key=f"ing_name_{i}", placeholder="e.g., Vitamin C")
                with ing_col2:
                    ing_conc = st.text_input(f"Concentration", key=f"ing_conc_{i}", placeholder="e.g., 10%")
                with ing_col3:
                    ing_purpose = st.text_input(f"Purpose", key=f"ing_purpose_{i}", placeholder="e.g., Brightening")
                
                if ing_name:
                    ing_data = {"name": ing_name}
                    if ing_conc:
                        ing_data["concentration"] = ing_conc
                    if ing_purpose:
                        ing_data["purpose"] = ing_purpose
                    ingredients.append(ing_data)
    
    # Benefits section
    st.markdown("#### ✨ Benefits")
    benefits = st.text_area(
        "Product Benefits (one per line)",
        placeholder="Brightening\nFades dark spots\nEvens skin tone",
        height=100
    )
    
    # Custom fields section
    st.markdown("#### ➕ Custom Fields")
    st.markdown("Add any additional product-specific attributes (e.g., calories, allergens, certifications).")
    
    col_add, col_spacer = st.columns([1, 3])
    with col_add:
        if st.button("➕ Add Custom Field", use_container_width=True):
            add_custom_field()
    
    custom_fields_data = {}
    for field in st.session_state.custom_fields:
        col_name, col_value, col_remove = st.columns([2, 3, 1])
        with col_name:
            field_name = st.text_input(
                "Field Name",
                key=f"custom_name_{field['id']}",
                placeholder="e.g., calories, allergens"
            )
        with col_value:
            field_value = st.text_input(
                "Value",
                key=f"custom_value_{field['id']}",
                placeholder="e.g., 250 kcal, Nuts"
            )
        with col_remove:
            if st.button("🗑️", key=f"remove_{field['id']}", use_container_width=True):
                remove_custom_field(field['id'])
                st.rerun()
        
        if field_name and field_value:
            custom_fields_data[field_name] = field_value
    
    # Submit button
    st.markdown("---")
    col_submit, col_clear = st.columns([1, 1])
    
    with col_submit:
        submit = st.button("🚀 Generate Content", type="primary", use_container_width=True)
    
    with col_clear:
        if st.button("🔄 Clear Form", use_container_width=True):
            st.session_state.custom_fields = []
            st.rerun()
    
    if submit:
        # Validate required fields
        if not name or price <= 0:
            st.error("❌ Please fill in all required fields (Name and Price)")
            return None
        
        # Build product data
        product_data = {
            "name": name,
            "price": float(price),
            "currency": currency if currency else "₹"
        }
        
        if category:
            product_data["category"] = category
        
        if concentration:
            product_data["concentration"] = concentration
        
        if ingredients:
            product_data["key_ingredients"] = ingredients
        
        if benefits:
            product_data["benefits"] = [b.strip() for b in benefits.split('\n') if b.strip()]
        
        if usage_instructions:
            product_data["usage_instructions"] = usage_instructions
        
        if side_effects:
            product_data["side_effects"] = side_effects
        
        if target_audience:
            product_data["target_audience"] = [t.strip() for t in target_audience.split('\n') if t.strip()]
        
        if custom_fields_data:
            product_data["custom_fields"] = custom_fields_data
        
        return product_data
    
    return None


def render_json_mode():
    """Render JSON input mode"""
    st.markdown("### 📋 JSON Input")
    st.markdown("Paste your product data as JSON. Must include `name` and `price` fields.")
    
    # Example JSON
    example_json = {
        "name": "GlowBoost Vitamin C Serum",
        "price": 699,
        "currency": "₹",
        "category": "Serum",
        "key_ingredients": [
            {"name": "Vitamin C", "concentration": "10%", "purpose": "Brightening"},
            {"name": "Hyaluronic Acid", "purpose": "Hydration"}
        ],
        "benefits": ["Brightening", "Fades dark spots"],
        "usage_instructions": "Apply 2-3 drops in the morning",
        "side_effects": "Mild tingling for sensitive skin",
        "target_audience": ["Oily skin", "Combination skin"]
    }
    
    with st.expander("📖 View Example JSON Format"):
        st.json(example_json)
    
    json_input = st.text_area(
        "Product JSON",
        height=300,
        placeholder=json.dumps(example_json, indent=2)
    )
    
    col_submit, col_validate = st.columns([1, 1])
    
    with col_validate:
        if st.button("✅ Validate JSON", use_container_width=True):
            if json_input:
                is_valid, result = validate_json_input(json_input)
                if is_valid:
                    st.success("✅ JSON is valid!")
                    with st.expander("View Parsed Data"):
                        st.json(result)
                else:
                    st.error(f"❌ {result}")
            else:
                st.warning("⚠️ Please enter JSON data")
    
    with col_submit:
        submit = st.button("🚀 Generate Content", type="primary", use_container_width=True)
    
    if submit:
        if not json_input:
            st.error("❌ Please enter product data in JSON format")
            return None
        
        is_valid, result = validate_json_input(json_input)
        if not is_valid:
            st.error(f"❌ {result}")
            return None
        
        return result
    
    return None


def run_content_generation(product_data, input_mode):
    """Run the workflow and display results"""
    st.markdown("---")
    st.markdown("## 🔄 Workflow Execution")
    
    # Create placeholder for live updates
    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    
    try:
        with st.spinner("Running agentic workflow..."):
            # Show initial status
            status_placeholder.info("🔍 Starting workflow execution...")
            progress_bar.progress(10)
            
            # Run workflow
            final_state = run_workflow(product_data, input_mode=input_mode)
            
            progress_bar.progress(100)
            status_placeholder.success("✅ Workflow completed successfully!")
        
        # Display results
        st.markdown("---")
        st.markdown("## 📊 Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Agents Executed", len(final_state.get('agent_trace', [])))
        
        with col2:
            st.metric("Questions Generated", len(final_state.get('questions', [])))
        
        with col3:
            completeness = final_state.get('product_model').completeness_score if final_state.get('product_model') else 0
            st.metric("Data Completeness", f"{completeness}%")
        
        # Agent trace
        with st.expander("🔧 Agent Execution Trace"):
            for i, agent in enumerate(final_state.get('agent_trace', []), 1):
                st.write(f"{i}. {agent}")
        
        # Display generated files
        st.markdown("### 📁 Generated Files")
        
        output_files = list(OUTPUTS_DIR.glob("*.json"))
        
        if output_files:
            tabs = st.tabs([f.stem.replace('_', ' ').title() for f in output_files])
            
            for tab, file_path in zip(tabs, output_files):
                with tab:
                    # Read and display JSON
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        file_data = json.loads(file_content)
                    
                    col_preview, col_download = st.columns([3, 1])
                    
                    with col_preview:
                        st.json(file_data)
                    
                    with col_download:
                        st.download_button(
                            label=f"⬇️ Download {file_path.name}",
                            data=file_content,
                            file_name=file_path.name,
                            mime="application/json",
                            use_container_width=True
                        )
                        
                        file_size = file_path.stat().st_size / 1024
                        st.caption(f"Size: {file_size:.1f} KB")
            
            st.success(f"✅ Successfully generated {len(output_files)} files!")
            st.info(f"📂 Files saved to: `{OUTPUTS_DIR}`")
        else:
            st.warning("⚠️ No output files found")
        
        # Store in session state
        st.session_state.workflow_complete = True
        st.session_state.generated_files = output_files
        
    except Exception as e:
        st.error(f"❌ Error during workflow execution: {str(e)}")
        st.exception(e)


def main():
    """Main Streamlit app"""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🤖 Agentic Content Generation System</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Automatically generate FAQ, Product Pages, and Comparisons using AI agents</div>',
        unsafe_allow_html=True
    )
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ℹ️ About")
        st.markdown("""
        This system uses **8 AI agents** to automatically generate structured content:
        
        - 📄 **FAQ Page** (15+ questions)
        - 📄 **Product Page** (comprehensive info)
        - 📄 **Comparison Page** (vs competitor)
        
        **How it works:**
        1. Enter product data
        2. AI agents process in parallel
        3. Download generated JSON files
        """)
        
        st.markdown("---")
        st.markdown("## ⚙️ Settings")
        
        api_key_status = "✅ Configured" if Path(".env").exists() else "❌ Missing"
        st.info(f"OpenAI API Key: {api_key_status}")
        
        st.markdown("---")
        st.markdown("## 📊 Statistics")
        if st.session_state.workflow_complete:
            st.success(f"✅ Last run: Success")
            st.metric("Files Generated", len(st.session_state.generated_files))
        else:
            st.info("No workflow executed yet")
    
    # Main content - Input mode selection
    input_mode = st.radio(
        "Choose Input Mode:",
        options=["📝 Form Mode (Guided)", "📋 JSON Mode (Direct)"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Render appropriate input mode
    product_data = None
    
    if "Form Mode" in input_mode:
        product_data = render_form_mode()
        mode = "form"
    else:
        product_data = render_json_mode()
        mode = "json"
    
    # Run workflow if data submitted
    if product_data:
        run_content_generation(product_data, mode)


if __name__ == "__main__":
    main()