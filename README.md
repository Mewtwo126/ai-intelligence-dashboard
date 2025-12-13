# AI Tool Database - Frontier Model Tracker

A structured database for tracking frontier AI models, their features, costs, and trends.

## Project Overview

This project helps you stay up-to-date with the latest frontier AI models from leading providers:
- **Anthropic** (Claude family)
- **OpenAI** (GPT, o1 families)
- **Google** (Gemini family)
- **xAI** (Grok family)
- **DeepSeek** and other emerging providers

## Directory Structure

```
ai_tool_database/
├── data/
│   ├── models.json              # Main model database
│   ├── changelog.json           # Track all changes over time
│   └── snapshots/              # Historical snapshots
│       └── 2025-12/
├── scripts/
│   ├── ai_tool_parser.py       # Parse AI tool info with Ollama
│   ├── add_model.py            # Add/update models
│   └── compare.py              # Compare models side-by-side
└── reports/                     # Generated comparison reports
```

## Database Schema

Each model tracks the following (prioritized by your needs):

### 1. Modalities (Highest Priority)
- Text, images, audio, video, documents
- Determines what types of input/output the model supports

### 2. Context Window
- Input token limit
- Output token limit
- Critical for understanding model capacity

### 3. Pricing
- Input cost per 1M tokens
- Output cost per 1M tokens
- Currency and last update date
- Optional pricing notes

### 4. Performance/Speed
- Speed tier: very_fast, fast, medium, slow, adaptive
- Performance notes and special capabilities

## Scripts

### 1. add_model.py
Interactive tool to add new models or update existing ones.

```bash
python scripts/add_model.py
```

**Features:**
- Add new frontier models to database
- Update pricing, features, or modalities of existing models
- Automatically updates changelog
- Validates data before saving

### 2. compare.py
Compare models side-by-side with multiple view options.

```bash
python scripts/compare.py
```

**Options:**
- Compare all models
- Compare by provider (e.g., all Anthropic models)
- Custom selection (pick specific models)
- Cost efficiency analysis (ranked by price)
- List all available models

### 3. ai_tool_parser.py
Use local LLM (Ollama) to extract structured data from AI tool descriptions.

```bash
python scripts/ai_tool_parser.py
```

**Requirements:**
- Ollama installed and running
- Model downloaded (default: llama3.2)

## Current Models (as of 2025-12-06)

| Provider | Model | Context Window | Cost (in/out per 1M) |
|----------|-------|----------------|----------------------|
| Anthropic | Claude Opus 4.5 | 200K | $15.00 / $75.00 |
| Anthropic | Claude Sonnet 4.5 | 200K | $3.00 / $15.00 |
| Anthropic | Claude Haiku 4 | 200K | $1.00 / $5.00 |
| OpenAI | GPT-5.1 | 400K | $1.25 / $10.00 |
| OpenAI | o1 | 200K | $15.00 / $60.00 |
| Google | Gemini 3 Pro | 1M | $2.00 / $12.00 |
| xAI | Grok 4.1 | 2M | $0.20 / $0.50 |
| DeepSeek | DeepSeek-V3 | 65K | $0.27 / $1.10 |

## Getting Started

1. **View existing models:**
   ```bash
   python scripts/compare.py
   ```

2. **Add a new model:**
   ```bash
   python scripts/add_model.py
   ```

3. **Compare specific models:**
   ```bash
   python scripts/compare.py
   # Select option 3 for custom selection
   ```

## Tracking Trends

The `changelog.json` file tracks:
- When models are added
- When features/pricing are updated
- Historical changes for trend analysis

**Future enhancements:**
- Monthly snapshots for historical comparison
- Automated trend detection (e.g., "context windows growing 50% YoY")
- Feature adoption tracking (e.g., "multimodal becoming standard")

## Dependencies

Core scripts use Python standard library only. Optional dependencies:

- **tabulate** (for compare.py): `pip install tabulate`
- **requests** (for ai_tool_parser.py): `pip install requests`

## Use Cases

- **Cost comparison** - Find the most cost-effective model for your workload
- **Feature tracking** - Identify which models support specific modalities
- **Trend analysis** - Spot patterns in model releases and capabilities
- **Decision making** - Data-driven model selection for projects

## Next Steps

- [ ] Add more frontier models (Meta Llama, Mistral, etc.)
- [ ] Build trend analyzer script
- [ ] Create monthly snapshot automation
- [ ] Add visualization tools (charts for pricing trends)
- [ ] Expand to include fine-tuning and API features
