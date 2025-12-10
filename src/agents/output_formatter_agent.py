"""
Output Formatter Agent
Writes final JSON files to disk
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import json
from typing import Dict, Any
from datetime import datetime
from src.models.state_model import WorkflowState
from src.config import OUTPUTS_DIR, FAQ_OUTPUT_FILE, PRODUCT_PAGE_OUTPUT_FILE, COMPARISON_OUTPUT_FILE


def write_output_files(state: WorkflowState) -> Dict[str, Any]:
    """
    Output Formatter Agent
    
    Reads: faq_page, product_page, comparison_page from state
    Writes: Files to disk, agent_trace
    
    Writes all generated pages as JSON files to the outputs directory
    """
    print("\n💾 Output Formatter Agent: Starting...")
    
    faq_page = state.get("faq_page")
    product_page = state.get("product_page")
    comparison_page = state.get("comparison_page")
    
    # Track which files were written
    written_files = []
    errors = []
    
    # Ensure outputs directory exists
    OUTPUTS_DIR.mkdir(exist_ok=True, parents=True)
    print(f"📁 Output directory: {OUTPUTS_DIR}")
    
    try:
        # Write FAQ page
        if faq_page:
            faq_path = OUTPUTS_DIR / FAQ_OUTPUT_FILE
            try:
                with open(faq_path, 'w', encoding='utf-8') as f:
                    json.dump(faq_page, f, indent=2, ensure_ascii=False)
                written_files.append(str(faq_path))
                print(f"  ✅ Written: {FAQ_OUTPUT_FILE}")
            except Exception as e:
                error_msg = f"Failed to write FAQ page: {str(e)}"
                errors.append(error_msg)
                print(f"  ❌ Error: {error_msg}")
        else:
            print(f"  ⚠️  Skipped: {FAQ_OUTPUT_FILE} (no data)")
        
        # Write Product page
        if product_page:
            product_path = OUTPUTS_DIR / PRODUCT_PAGE_OUTPUT_FILE
            try:
                with open(product_path, 'w', encoding='utf-8') as f:
                    json.dump(product_page, f, indent=2, ensure_ascii=False)
                written_files.append(str(product_path))
                print(f"  ✅ Written: {PRODUCT_PAGE_OUTPUT_FILE}")
            except Exception as e:
                error_msg = f"Failed to write product page: {str(e)}"
                errors.append(error_msg)
                print(f"  ❌ Error: {error_msg}")
        else:
            print(f"  ⚠️  Skipped: {PRODUCT_PAGE_OUTPUT_FILE} (no data)")
        
        # Write Comparison page
        if comparison_page:
            comparison_path = OUTPUTS_DIR / COMPARISON_OUTPUT_FILE
            try:
                with open(comparison_path, 'w', encoding='utf-8') as f:
                    json.dump(comparison_page, f, indent=2, ensure_ascii=False)
                written_files.append(str(comparison_path))
                print(f"  ✅ Written: {COMPARISON_OUTPUT_FILE}")
            except Exception as e:
                error_msg = f"Failed to write comparison page: {str(e)}"
                errors.append(error_msg)
                print(f"  ❌ Error: {error_msg}")
        else:
            print(f"  ⚠️  Skipped: {COMPARISON_OUTPUT_FILE} (no data)")
        
        # Summary
        if written_files:
            print(f"\n✅ Successfully wrote {len(written_files)} file(s)")
            print(f"📂 Location: {OUTPUTS_DIR}")
        else:
            print(f"\n⚠️  No files written (no page data available)")
        
        result = {
            "written_files": written_files,
            "output_directory": str(OUTPUTS_DIR),
            "files_written_count": len(written_files),
            "agent_trace": ["output_formatter_agent"],
            "timestamp": datetime.now().isoformat()
        }
        
        if errors:
            result["errors"] = errors
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to write output files: {str(e)}"
        print(f"❌ Error: {error_msg}")
        return {
            "errors": [error_msg],
            "written_files": written_files,
            "agent_trace": ["output_formatter_agent"],
            "timestamp": datetime.now().isoformat()
        }


# Agent metadata
AGENT_INFO = {
    "name": "Output Formatter Agent",
    "responsibility": "Write final JSON files to disk",
    "reads_from_state": ["faq_page", "product_page", "comparison_page"],
    "writes_to_state": ["written_files", "agent_trace"],
    "dependencies": ["faq_builder_agent", "product_page_builder_agent", "comparison_page_builder_agent"]
}