# Agentic Content Generation System - Project Documentation

## Problem Statement

Traditional content generation systems are monolithic and inflexible. When businesses need to create product documentation (FAQs, product pages, comparison pages) at scale, they face challenges:

- Manual content creation is time-consuming and inconsistent
- Monolithic systems are hard to maintain and extend
- Domain-specific logic is tightly coupled
- Difficult to reuse content across different page types
- No systematic way to generate competitor comparisons

This project solves these challenges by building a **modular, multi-agent system** that automatically generates structured, machine-readable content pages from minimal product data.

---

## Solution Overview

We've built an **8-agent orchestration system** using LangGraph that transforms raw product data into three comprehensive, structured JSON pages:

1. **FAQ Page**: 15+ categorized questions with AI-generated answers
2. **Product Page**: Complete product information organized into logical sections
3. **Comparison Page**: Side-by-side comparison with a generated competitor product

### Key Innovations

- **Agent-Based Architecture**: Each agent has a single, well-defined responsibility
- **LLM-Powered Intelligence**: Uses OpenAI GPT-4o-mini for contextual question generation, competitor creation, and content enhancement
- **Domain-Agnostic**: Works seamlessly across product categories (skincare, food, supplements, etc.)
- **Parallel Execution**: LangGraph orchestrates agents to run in parallel where possible, optimizing performance
- **Reusable Content Blocks**: Content is generated once and reused across multiple page types

---

## Scopes & Assumptions

### In Scope

✅ Parse and validate product data from JSON input  
✅ Generate 15+ questions across 15 predefined categories  
✅ Create fictional but realistic competitor products  
✅ Generate reusable content blocks (benefits, ingredients, usage, safety, pricing, comparison)  
✅ Build three page types: FAQ, Product, Comparison  
✅ Output as clean, machine-readable JSON files  
✅ Support custom product fields (domain-specific attributes)  
✅ Handle minimal product data with graceful fallbacks  
✅ Domain-agnostic design (works for any product type)  

### Out of Scope

❌ Multi-product batch processing (system processes one product at a time)  
❌ Real-time collaboration or concurrent user access  
❌ External data enrichment (web scraping, API calls for additional product info)  
❌ Non-JSON output formats (HTML, PDF, Markdown)  
❌ User authentication or access control  
❌ Product data validation beyond basic schema requirements  

### Assumptions

- **Input Quality**: User provides valid product data (minimum: name, price, currency)
- **API Access**: System has access to OpenAI API with valid API key
- **Competitor Relevance**: Generated Product B should be in the same category as Product A
- **Content Length**: All generated content fits within LLM token limits
- **Execution Environment**: System runs in a single-user, local environment

---

## System Design

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                              │
│                    (Product Data JSON)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LANGGRAPH ORCHESTRATOR                      │
│                    (State Management & Flow)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   1. Data Parser Agent       │
              │   Parse & Validate Input     │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   PARALLEL EXECUTION         │
              ├──────────────┬───────────────┤
              │ 2. Question  │ 3. Product B  │
              │  Generator   │   Generator   │
              └──────────────┴───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  4. Content Logic Agent      │
              │  Generate Reusable Blocks    │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   PARALLEL EXECUTION         │
              ├──────────┬─────────┬─────────┤
              │ 5. FAQ   │ 6. Prod │ 7. Comp │
              │  Builder │  Builder│ Builder │
              └──────────┴─────────┴─────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  8. Output Formatter Agent   │
              │  Write JSON Files to Disk    │
              └──────────────┬───────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         OUTPUTS                                 │
│        faq.json | product_page.json | comparison_page.json     │
└─────────────────────────────────────────────────────────────────┘
```

---

### Agent Specifications

#### 1. Data Parser Agent
**Responsibility**: Parse and validate raw product input into structured ProductModel

- **Input**: Raw product JSON
- **Output**: Validated ProductModel with metadata
- **Processing**: 
  - Validates required fields (name, price, currency)
  - Structures ingredients as objects
  - Calculates completeness score
  - Generates product ID
- **Dependencies**: None (entry point)

#### 2. Question Generator Agent (LLM-Powered)
**Responsibility**: Generate 15+ contextual questions with answers

- **Input**: ProductModel
- **Output**: List of QuestionModel objects organized by category
- **Processing**:
  - Calls OpenAI GPT-4o-mini with structured prompt
  - Requests questions across 15 categories
  - Validates categories match predefined list
  - Ensures answers use only available product data
- **Dependencies**: Data Parser Agent

#### 3. Product B Generator Agent (LLM-Powered)
**Responsibility**: Create fictional competitor product for comparison

- **Input**: ProductModel (Product A)
- **Output**: ProductBModel (fictional competitor)
- **Processing**:
  - Calls OpenAI with constraints (same category, 20-40% price difference, different ingredients)
  - Validates output as ProductModel
  - Ensures no ingredient overlap with Product A
- **Dependencies**: Data Parser Agent

#### 4. Content Logic Agent
**Responsibility**: Transform product data into reusable content blocks

- **Input**: ProductModel, ProductBModel, Questions
- **Output**: Dictionary of ContentBlock objects
- **Processing**:
  - Generates 7 block types: overview, benefits, ingredients, usage, safety, price, comparison
  - Optionally enhances content with LLM for natural flow
  - Handles missing data with fallback content
  - Creates FAQ answer blocks from questions
- **Dependencies**: Question Generator, Product B Generator

#### 5. FAQ Builder Agent
**Responsibility**: Assemble FAQ page from questions and content blocks

- **Input**: Questions, ContentBlocks
- **Output**: FAQ page JSON
- **Processing**:
  - Organizes questions by category
  - Sorts by priority within categories
  - Adds product overview as introduction
  - Includes metadata (timestamps, product info)
- **Dependencies**: Content Logic Agent

#### 6. Product Page Builder Agent
**Responsibility**: Assemble comprehensive product page

- **Input**: ProductModel, ContentBlocks
- **Output**: Product page JSON
- **Processing**:
  - Organizes into sections: overview, key info, usage, safety, pricing
  - Extracts structured data from content blocks
  - Handles missing blocks gracefully
  - Includes completeness metadata
- **Dependencies**: Content Logic Agent

#### 7. Comparison Page Builder Agent
**Responsibility**: Assemble side-by-side product comparison

- **Input**: ProductModel A & B, ContentBlocks
- **Output**: Comparison page JSON
- **Processing**:
  - Calculates price differences and percentages
  - Compares ingredients (overlap, unique, similarity score)
  - Compares benefits (common, unique)
  - Generates smart recommendations
- **Dependencies**: Content Logic Agent

#### 8. Output Formatter Agent
**Responsibility**: Write all JSON files to disk

- **Input**: FAQ page, Product page, Comparison page
- **Output**: 3 JSON files in /outputs directory
- **Processing**:
  - Creates output directory if not exists
  - Writes JSON with UTF-8 encoding and pretty formatting
  - Handles file write errors gracefully
  - Returns file paths for verification
- **Dependencies**: All page builder agents

---

### Data Flow Diagram
```
Raw Input (JSON)
      │
      ▼
ProductModel (validated, typed)
      │
      ├──────────────┬────────────────┐
      ▼              ▼                ▼
  Questions     Product B        (stored)
      │              │                │
      └──────────────┴────────────────┘
                     │
                     ▼
            Content Blocks (reusable)
                     │
      ├──────────────┼────────────────┐
      ▼              ▼                ▼
  FAQ Page     Product Page    Comparison Page
      │              │                │
      └──────────────┴────────────────┘
                     │
                     ▼
          JSON Files (outputs/)
```

---

### State Management Strategy

**Central State Object (WorkflowState)**:
- Flows through all agents via LangGraph
- Each agent reads required fields and writes updates
- Uses TypedDict for type safety
- Annotated fields with `add` operator for append-only lists (questions, errors, warnings, agent_trace)
- Non-annotated fields use last-write-wins semantics

**Key State Fields**:
- `raw_input`: Original product JSON
- `product_model`: Parsed and validated product
- `product_b_model`: Generated competitor
- `questions`: All generated questions
- `content_blocks`: Reusable content blocks dictionary
- `faq_page`, `product_page`, `comparison_page`: Final page structures
- `agent_trace`: Execution order tracking
- `errors`, `warnings`: Error tracking

**Benefits**:
- ✅ No hidden global state
- ✅ Clear data provenance
- ✅ Easy to debug and test
- ✅ Supports parallel execution safely

---

### Design Decisions & Rationale

#### Why LangGraph?

**Decision**: Use LangGraph for orchestration instead of custom orchestrator or other frameworks (CrewAI, AutoGen)

**Rationale**:
- **Explicit Flow Control**: LangGraph makes agent dependencies and execution order explicit through graph edges
- **Built-in State Management**: StateGraph pattern naturally handles state passing and merging
- **Parallel Execution**: Framework handles concurrent agent execution automatically
- **Type Safety**: Works seamlessly with Pydantic models (our data schemas)
- **Production-Ready**: Battle-tested framework from LangChain team

#### Why Shared State Communication?

**Decision**: Agents communicate via shared state object (not message passing or queues)

**Rationale**:
- **Data Provenance**: Clear tracking of what each agent contributed
- **No Hidden Dependencies**: Agents declare what they read/write
- **Immutability**: State updates are explicit, preventing accidental mutations
- **Debuggability**: Can inspect state at any point in workflow
- **Simplicity**: Easier to reason about than event-driven message passing

#### Why LLM-Assisted Product B Generation?

**Decision**: Use GPT-4o-mini to generate competitor product (not rule-based or template-based)

**Rationale**:
- **Contextual Relevance**: LLM understands product category and creates realistic competitors
- **Variety**: Each generation is unique, avoiding repetitive outputs
- **Flexibility**: Works across all product domains without domain-specific rules
- **Quality**: Generates structured output that passes ProductModel validation
- **Constraint Satisfaction**: Can enforce rules (price range, no ingredient overlap) via prompt

#### Why Separate Content Logic Agent?

**Decision**: Centralize content block generation in one agent instead of embedding in page builders

**Rationale**:
- **Reusability**: Same content blocks used across multiple pages (FAQ, Product, Comparison)
- **Single Source of Truth**: Content generated once, formatted differently per page
- **Separation of Concerns**: Content generation logic separate from page assembly logic
- **Easier Testing**: Can test content generation independently
- **Extensibility**: Easy to add new block types without touching page builders

#### Why JSON Output Only?

**Decision**: Output only JSON format (not HTML, PDF, or other formats)

**Rationale**:
- **Machine-Readable**: JSON is easily consumed by other systems, APIs, or UIs
- **Flexibility**: Frontend can render JSON however needed (web, mobile, desktop)
- **Structured Data**: Preserves data types, nesting, and relationships
- **Validation**: Easy to validate against JSON schemas
- **Assignment Requirement**: Explicitly specified in assignment requirements

---

### Extensibility Examples

#### Adding a New Page Type (e.g., "Ingredient Deep Dive")

**Required Changes**:
1. Create new template definition in `src/templates/`
2. Create new builder agent: `ingredient_deepdive_builder_agent.py`
3. Add agent as node in `src/orchestrator.py`
4. Add edge from Content Logic Agent to new builder
5. Add edge from new builder to Output Formatter
6. Update config with new output filename

**Unchanged**:
- All existing agents (Data Parser, Question Generator, Product B Generator, Content Logic)
- Existing page builders (FAQ, Product, Comparison)
- State model (or add one optional field)

**Time Estimate**: ~2-3 hours

#### Adding Multi-Product Batch Processing

**Required Changes**:
1. Modify `main.py` to accept list of products
2. Wrap orchestrator call in loop
3. Update Output Formatter to namespace files by product ID
4. (Optional) Add batch progress tracking

**Unchanged**:
- All 8 agents remain identical
- Orchestration flow unchanged
- State model unchanged

**Time Estimate**: ~1-2 hours

---

## Technology Stack

- **Python 3.11+**
- **LangGraph 0.2.45**: Multi-agent orchestration
- **LangChain 0.3.15**: LLM integration
- **OpenAI GPT-4o-mini**: AI-powered content generation
- **Pydantic 2.10**: Data validation and schemas
- **Python-dotenv 1.0**: Environment variable management

---

## Project Structure
```
kasparro-ai-agentic-content-generation-system-manan/
│
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── data_parser_agent.py
│   │   ├── question_generator_agent.py
│   │   ├── product_b_generator_agent.py
│   │   ├── content_logic_agent.py
│   │   ├── faq_builder_agent.py
│   │   ├── product_page_builder_agent.py
│   │   ├── comparison_page_builder_agent.py
│   │   └── output_formatter_agent.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── product_model.py           # ProductModel, IngredientModel
│   │   ├── question_model.py          # QuestionModel
│   │   ├── content_block_model.py     # ContentBlock
│   │   └── state_model.py             # WorkflowState
│   │
│   ├── config.py                      # Configuration constants
│   └── orchestrator.py                # LangGraph workflow
│
├── outputs/                           # Generated JSON files
│   ├── faq.json
│   ├── product_page.json
│   └── comparison_page.json
│
├── docs/
│   └── projectdocumentation.md        # This file
│
├── tests/                             # Test files (not required but provided)
├── main.py                            # Entry point
├── requirements.txt                   # Dependencies
├── .env                               # API keys (not committed)
├── .gitignore
└── README.md
```

---

## Performance Characteristics

**Execution Time** (for single product):
- Data Parsing: <1 second
- Question Generation: ~5-10 seconds (LLM call)
- Product B Generation: ~5-10 seconds (LLM call)
- Content Logic: ~2-5 seconds (with optional LLM enhancement)
- Page Building: <1 second each
- File Writing: <1 second

**Total Time**: ~15-30 seconds per product

**Parallel Execution Optimization**:
- Question Generator + Product B Generator run simultaneously (saves ~5-10 seconds)
- All 3 page builders run simultaneously (saves ~2 seconds)

**Approximate Cost** (OpenAI API):
- Input tokens: ~2,000-3,000 per product
- Output tokens: ~1,500-2,500 per product
- Cost with GPT-4o-mini: ~$0.01-0.02 per product

---

## Conclusion

This system demonstrates **production-grade agentic architecture** principles:

1. **Modularity**: Each agent is independently testable and replaceable
2. **Orchestration**: LangGraph manages complex multi-agent workflows
3. **Reusability**: Content blocks generated once, used across pages
4. **Extensibility**: New pages, agents, or features can be added without breaking existing functionality
5. **Domain-Agnostic**: Works across product categories without modification
6. **Type Safety**: Pydantic models ensure data integrity throughout workflow
7. **Error Handling**: Graceful degradation when data is incomplete
8. **Production-Ready**: Clean code, comprehensive testing, proper documentation

The system successfully transforms minimal product data into comprehensive, structured content suitable for web applications, mobile apps, or any system requiring machine-readable product information.