# AXIS Project Status and Architecture Report

## 1. Executive summary
AXIS is a trading intelligence and execution-assistance project organized as a Python-based pipeline with a strong emphasis on market analysis, knowledge ingestion, optional LLM reasoning, and later-stage automation. The repository already contains a substantial scaffold for a multi-phase system, including folders for agents, graph orchestration, market data handling, memory/knowledge retrieval, services, backtesting, and tests.

At the current stage, the project is best described as an architecture-heavy scaffold rather than a fully wired production pipeline. Most of the core modules exist as empty or placeholder files, while the repository also includes environment configuration, a large dependency stack, and knowledge/data folders that suggest a much more complete intended design.

## 2. Current condition of the repository
### What is present
- A top-level Python project structure with:
  - [main.py](main.py)
  - [requirements.txt](requirements.txt)
  - [README.md](README.md)
  - [data/](data)
  - [src/](src)
  - [tests/](tests)
  - [migrations/](migrations)
  - [netlify/](netlify)
  - [.github/workflows/](.github/workflows)
- A populated environment file at [.env](.env) containing API keys and service configuration.
- A large dependency list in [requirements.txt](requirements.txt), including:
  - LangGraph
  - LiteLLM
  - Pydantic 2
  - Supabase
  - Cognee
  - Dhan SDK
  - HTTPX
  - Python-dotenv
  - Pandas
  - Pytest
- Knowledge content under [data/knowledge](data/knowledge) and examples under [data/examples](data/examples).
- A dedicated folder structure for future runtime modules under [src](src).

### What is still incomplete
- The main pipeline entry point [main.py](main.py) is a basic Cognee bootstrap script rather than a full trading workflow.
- Several core modules are empty files, including:
  - [src/graph/graph.py](src/graph/graph.py)
  - [src/graph/nodes.py](src/graph/nodes.py)
  - [src/graph/router.py](src/graph/router.py)
  - [src/graph/state.py](src/graph/state.py)
  - [src/memory/ingest.py](src/memory/ingest.py)
  - [src/memory/recall.py](src/memory/recall.py)
  - [src/memory/loader.py](src/memory/loader.py)
  - [src/memory/datasets.py](src/memory/datasets.py)
  - [src/agents/decision_engine.py](src/agents/decision_engine.py)
  - [src/agents/market_analyst.py](src/agents/market_analyst.py)
  - [src/agents/risk_manager.py](src/agents/risk_manager.py)
  - [src/llm/providers.py](src/llm/providers.py)
  - [src/llm/prompts.py](src/llm/prompts.py)
  - [src/llm/models.py](src/llm/models.py)
  - [src/config/settings.py](src/config/settings.py)
  - [src/config/constants.py](src/config/constants.py)
  - [src/config/models.py](src/config/models.py)
  - [src/database/dhan.py](src/database/dhan.py)
  - [src/database/supabase.py](src/database/supabase.py)
  - [src/market/downloader.py](src/market/downloader.py)
  - [src/services/telegram.py](src/services/telegram.py)
- The repository contains many smoke tests under [tests/smoke](tests/smoke), which suggests a previous or ongoing exploration phase, but the main runtime path is not yet fully implemented.
- The environment file contains real-looking credentials and tokens. That should be treated as sensitive and not shared broadly.

## 3. Folder-by-folder architecture overview
### Root level
- [main.py](main.py): currently acts as a simple Cognee startup and recall demo.
- [README.md](README.md): currently empty, so the project lacks a proper landing documentation page.
- [requirements.txt](requirements.txt): holds the current dependency set for the intended stack.
- [.env](.env): holds runtime secrets and provider configuration.
- [.env.example](.env.example): present but empty.
- [.gitignore](.gitignore): present but empty.
- [.github/workflows](.github/workflows): intended for CI automation, but the workflow file is empty.

### data/
This folder appears to be the knowledge and example corpus for the system.
- [data/knowledge](data/knowledge): contains domain knowledge files such as:
  - [data/knowledge/market_profile.txt](data/knowledge/market_profile.txt)
  - [data/knowledge/option_chain.txt](data/knowledge/option_chain.txt)
  - [data/knowledge/orderflow.txt](data/knowledge/orderflow.txt)
  - [data/knowledge/psychology.txt](data/knowledge/psychology.txt)
  - [data/knowledge/trap_mechanism.txt](data/knowledge/trap_mechanism.txt)
  - [data/knowledge/vsa.txt](data/knowledge/vsa.txt)
  - [data/knowledge/wyckoff.txt](data/knowledge/wyckoff.txt)
- [data/examples](data/examples): contains date-stamped example inputs such as:
  - [data/examples/june01.txt](data/examples/june01.txt)
  - [data/examples/june02.txt](data/examples/june02.txt)
  - [data/examples/june03.txt](data/examples/june03.txt)
  - [data/examples/june04.txt](data/examples/june04.txt)
  - [data/examples/june05.txt](data/examples/june05.txt)

This strongly suggests that the project is intended to use structured market reasoning examples and knowledge files as training or retrieval context for later analysis stages.

### src/
The core application code is split into modules by responsibility.

#### src/agents/
Contains agent-oriented analysis modules:
- [src/agents/decision_engine.py](src/agents/decision_engine.py)
- [src/agents/market_analyst.py](src/agents/market_analyst.py)
- [src/agents/oi_analyst.py](src/agents/oi_analyst.py)
- [src/agents/price_action.py](src/agents/price_action.py)
- [src/agents/risk_manager.py](src/agents/risk_manager.py)
- [src/agents/sentiment.py](src/agents/sentiment.py)
- [src/agents/trade_verifier.py](src/agents/trade_verifier.py)
- [src/agents/volume_analyst.py](src/agents/volume_analyst.py)

These files are likely intended to encapsulate specialist analysis roles such as price action, sentiment, open interest, volume, and risk assessment.

#### src/graph/
Hosts the orchestration layer for workflow and decision routing:
- [src/graph/graph.py](src/graph/graph.py)
- [src/graph/nodes.py](src/graph/nodes.py)
- [src/graph/router.py](src/graph/router.py)
- [src/graph/state.py](src/graph/state.py)

This is the most likely place where LangGraph-style stateful execution would be defined.

#### src/memory/
Contains the knowledge layer components:
- [src/memory/ingest.py](src/memory/ingest.py)
- [src/memory/loader.py](src/memory/loader.py)
- [src/memory/recall.py](src/memory/recall.py)
- [src/memory/datasets.py](src/memory/datasets.py)

These modules appear intended to ingest flat files from [data/knowledge](data/knowledge) and later retrieve relevant knowledge for agent reasoning.

#### src/llm/
Contains language-model integration pieces:
- [src/llm/models.py](src/llm/models.py)
- [src/llm/prompts.py](src/llm/prompts.py)
- [src/llm/providers.py](src/llm/providers.py)
- [src/llm/test_litellm.py](src/llm/test_litellm.py)

This is the layer that would manage provider routing, prompt templates, and model wrappers.

#### src/config/
Expected to hold configuration and settings management:
- [src/config/constants.py](src/config/constants.py)
- [src/config/models.py](src/config/models.py)
- [src/config/prompts.py](src/config/prompts.py)
- [src/config/settings.py](src/config/settings.py)

The current repository state shows these files as placeholders or empty scaffolds.

#### src/database/
Likely intended for persistence and external service wrappers:
- [src/database/dhan.py](src/database/dhan.py)
- [src/database/models.py](src/database/models.py)
- [src/database/supabase.py](src/database/supabase.py)

#### src/market/
Contains data pipeline and market data parsing modules:
- [src/market/cleaner.py](src/market/cleaner.py)
- [src/market/downloader.py](src/market/downloader.py)
- [src/market/indicators.py](src/market/indicators.py)
- [src/market/oi_analysis.py](src/market/oi_analysis.py)
- [src/market/option_chain.py](src/market/option_chain.py)
- [src/market/parser.py](src/market/parser.py)
- [src/market/validator.py](src/market/validator.py)

These suggest an intended pipeline for raw market data ingestion, cleaning, parsing, and validation.

#### src/services/
Contains operational integrations:
- [src/services/notifications.py](src/services/notifications.py)
- [src/services/scheduler.py](src/services/scheduler.py)
- [src/services/telegram.py](src/services/telegram.py)

This indicates a future direction toward automation, notifications, and scheduled execution.

### tests/
The test suite is organized as a mix of direct tests and smoke tests:
- [tests/test_cognee.py](tests/test_cognee.py)
- [tests/test_dhan.py](tests/test_dhan.py)
- [tests/test_gemini.py](tests/test_gemini.py)
- [tests/test_groq.py](tests/test_groq.py)
- [tests/test_langgraph.py](tests/test_litellm.py)
- [tests/test_openrouter.py](tests/test_openrouter.py)
- [tests/test_supabase.py](tests/test_supabase.py)
- [tests/smoke](tests/smoke)

The presence of smoke tests suggests that the project has already been used experimentally for provider validation and integration checks.

## 4. Likely intended architecture
The repository structure points to the following intended architecture:

1. Data ingestion layer
   - Market data and instrument metadata would be pulled from external sources, especially Dhan-related endpoints.
   - Parsed data would be normalized into structured objects for downstream analysis.

2. Knowledge layer
   - Domain knowledge files from [data/knowledge](data/knowledge) are intended to be ingested into a memory or retrieval system.
   - The memory layer would likely support retrieval-augmented reasoning for the agents.

3. Agent analysis layer
   - Specialist agents under [src/agents](src/agents) would assess market structure, volume, sentiment, open interest, price action, and risk.
   - These agents would likely produce intermediate signals and structured observations.

4. Graph orchestration layer
   - The graph modules under [src/graph](src/graph) likely define a stateful workflow that routes decisions between analysis, validation, and execution.
   - LangGraph is a strong fit for this part of the architecture.

5. LLM/provider layer
   - The LLM modules suggest an abstraction over providers such as Gemini, Groq, Z.ai, OpenRouter, and Anthropic.
   - The project appears designed to allow provider fallback and optional narration.

6. Persistence and automation layer
   - Supabase and database modules suggest storage for signals, memory, and operational state.
   - Telegram and scheduling modules suggest alerting and possibly autonomous operation.

## 5. Current gaps and risks
- The system is not yet a complete end-to-end trading pipeline.
- Important modules are empty, so the architecture is only partially implemented.
- The project currently appears to depend on external services and API keys for full functionality, but the runtime wiring is not yet mature.
- The repository contains sensitive-looking environment values; this should be handled carefully.
- The absence of meaningful content in [README.md](README.md), [.gitignore](.gitignore), [.env.example](.env.example), and [.github/workflows/ci.yml](.github/workflows/ci.yml) suggests documentation and project hygiene are incomplete.

## 6. Practical interpretation
The project is currently in a “blueprint with implementation beginnings” stage. It has the right components and the right ambition, but the execution layer still needs to be filled in. The repository is structured as though the team intended to build a modular trading copilot or autonomous analysis system, but the actual decision graph, data connectors, settings harness, and memory retrieval modules still need to be implemented.

## 7. Recommended next steps
1. Implement a minimal configuration layer using [src/config/settings.py](src/config/settings.py).
2. Create a concrete graph workflow in [src/graph/graph.py](src/graph/graph.py) and related modules.
3. Implement the memory ingestion and retrieval path in [src/memory](src/memory).
4. Add one concrete data connector for Dhan and one for Supabase to establish a real end-to-end path.
5. Replace empty placeholder modules with real logic and add tests for each one.
6. Add proper documentation, CI configuration, and safer secret handling.
