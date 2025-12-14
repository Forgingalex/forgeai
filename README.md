# ForgeAI

ForgeAI explores how AI systems can act as external cognitive layers for human learning. The core question: can we build persistent memory and retrieval-augmented reasoning without cloud APIs?

## The Problem

Human learning faces three constraints: working memory limits, retrieval failures, and reasoning gaps. Traditional study tools don't address these. Cloud-based AI systems introduce latency, cost, and privacy trade-offs. ForgeAI asks what happens when you keep everything local and build a system that remembers.

## Cognitive Constraints

**Memory**: Working memory holds about 7±2 items. Long-term knowledge exists but isn't always accessible when needed. ForgeAI maintains a persistent knowledge base that survives sessions.

**Retrieval**: Finding relevant information from documents is harder than storing it. The system uses TF-IDF vectorization to retrieve context before reasoning, not after.

**Reasoning**: LLMs reason in context windows. Without external memory, they forget between sessions. ForgeAI uses retrieval-augmented generation to ground responses in persistent knowledge.

## Why Local-First

Local-first means no cloud API dependencies. Ollama runs models locally. PostgreSQL stores knowledge. Redis caches queries. Everything stays on your machine. This enables offline operation, unlimited usage, and privacy by default.

The trade-off: you need local compute. A GPU helps but isn't required. The system falls back to CPU inference when needed.

## Design Decisions

**TF-IDF over embeddings**: Simpler, no vector database, good enough for <10k documents. Semantic search can be added later if needed.

**Dual-model architecture**: Google AI Studio (Gemini) as primary, Ollama as fallback. Automatic failover when rate limits hit or network fails.

**PostgreSQL for knowledge**: Relational storage for structured data, file system for documents. No specialized vector DB required.

**WebSocket streaming**: Real-time responses, not batch processing. The interface shows reasoning as it happens.

## Scope Boundaries

This is not a general-purpose chatbot. It's optimized for learning workflows: document ingestion, summarization, question generation, and retrieval-augmented conversation. It doesn't do image generation, code execution, or multi-modal reasoning beyond text.

The system assumes single-user operation. Multi-user support exists but isn't the focus. Authentication exists for API security, not social features.

## Relationship to AEROS

AEROS handles perception: what the robot sees. ForgeAI handles cognition: what the human learns. Both systems operate locally, process streams in real-time, and maintain persistent state. The difference is domain: AEROS processes sensor data, ForgeAI processes knowledge.

The architectural similarity is intentional. Both systems explore how to build reliable AI systems without cloud dependencies.

## What This Is Not

This is not a SaaS product. There's no hosted version, no subscription model, no marketing funnel. It's a research prototype exploring cognitive architectures.

This is not production-ready for enterprise use. Error handling exists but isn't comprehensive. The system works for single users with moderate document volumes. Scale beyond that requires architectural changes.

## Getting Started

See [TECHNICAL.md](TECHNICAL.md) for installation, API documentation, and deployment details.

## License

MIT
