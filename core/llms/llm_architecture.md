# SARATHI LLM Orchestration Engine

**Version:** Phase 7 Complete  
**Status:** Stable  
**Author:** Karthik

---

# Overview

The LLM Orchestration Engine is responsible for managing all Large Language Model interactions within SARATHI.

Instead of directly calling an AI provider, every request passes through a standardized execution pipeline that determines the best provider, executes the request, records analytics, and returns a unified response.

The system is provider-agnostic, allowing new LLM providers to be integrated without modifying the rest of the application.

---

# Goals

- Support multiple LLM providers.
- Enable offline AI using Ollama.
- Automatically select the best provider.
- Handle provider failures gracefully.
- Collect performance analytics.
- Track usage and estimated cost.
- Support adaptive provider selection.
- Keep providers isolated from orchestration logic.

---

# High-Level Architecture

```
User Request
      │
      ▼
LLM Context
      │
      ▼
Router
      │
      ▼
LLM Decision
      │
      ▼
Executor
      │
      ▼
Provider
      │
      ▼
LLM Response
      │
      ▼
Analytics
```

---

# Folder Structure

```
core/
└── llms/
    ├── analytics.py
    ├── base.py
    ├── config.py
    ├── connectivity.py
    ├── context.py
    ├── decision.py
    ├── executor.py
    ├── manager.py
    ├── pricing.py
    ├── registry.py
    ├── response.py
    ├── router.py
    ├── usage.py
    │
    └── providers/
        ├── gemini.py
        ├── groq.py
        ├── ollama.py
        └── claude.py
```

---

# Core Components

## Provider

Responsible only for communicating with the external AI API.

Responsibilities:

- Build request payload
- Send request
- Parse response
- Return an LLMResponse

Providers DO NOT:

- Route requests
- Measure latency
- Retry failures
- Log analytics
- Calculate costs

---

## Registry

Maintains a list of all registered providers.

Responsibilities:

- Register providers
- List providers
- Retrieve provider classes

---

## Manager

Acts as the interface between the application and the registry.

Responsibilities:

- Instantiate providers
- Retrieve provider instances
- List available providers

---

## Router

Responsible for deciding which provider should handle a request.

Uses:

- Provider priority
- Context
- Offline preference
- Adaptive scoring
- Provider capabilities

Returns:

```
LLMDecision
```

---

## Executor

Executes requests using the provider selected by the Router.

Responsibilities:

- Execute provider
- Handle fallback
- Record analytics
- Track latency
- Track usage
- Track cost

The Executor is the central runtime component of the LLM layer.

---

## Analytics

Stores execution history.

Tracks:

- Timestamp
- Provider
- Model
- Success
- Latency
- Cost
- Feedback

Provides helper methods such as:

- average_latency()
- success_rate()
- feedback_score()

---

## Pricing

Responsible for estimating request costs.

Current implementation:

- Ollama → Free
- Groq → Free Tier
- Gemini → Free Tier

Future versions will include real pricing models.

---

## Connectivity

Determines internet availability.

Allows SARATHI to automatically switch into offline mode.

---

# Request Lifecycle

```
User

↓

LLMContext

↓

Router

↓

LLMDecision

↓

Executor

↓

Provider.generate()

↓

LLMResponse

↓

Analytics
```

---

# Fallback Flow

If a provider fails:

```
Primary Provider

↓

Failure

↓

Fallback Provider

↓

Failure

↓

Next Fallback

↓

Return First Successful Response
```

---

# Offline Flow

```
Internet Available?

        │
        ├── Yes
        │
        │
        ▼
    Router Chooses Best Provider

        │
        ▼
    Cloud Provider

        │

        └──────────────

        No

        │

        ▼

    Offline Mode Enabled

        │

        ▼

    Ollama
```

---

# Adaptive Routing

Providers are ranked using an adaptive score based on:

- Base priority
- Success rate
- User feedback
- Average latency
- (Future) Cost

This allows routing decisions to improve over time based on historical performance.

---

# Standard Objects

## LLMContext

Contains request metadata used during routing.

---

## LLMDecision

Represents the Router's decision.

Contains:

- Provider
- Model
- Fallback chain

---

## LLMResponse

Standardized response returned by every provider.

Contains:

- Success
- Content
- Provider
- Model
- Usage
- Error

---

## LLMUsage

Standardized token usage information.

Contains:

- Prompt tokens
- Completion tokens
- Total tokens

---

# Supported Providers

| Provider | Status |
|----------|--------|
| Ollama | ✅ |
| Gemini | ✅ |
| Groq | ✅ |
| Claude | Implemented (Requires Credits) |
| OpenAI | Planned |

---

# Design Principles

The LLM subsystem follows several architectural principles:

### Single Responsibility

Each component performs one task only.

Examples:

- Router → Makes decisions
- Executor → Executes requests
- Provider → Talks to APIs
- Analytics → Stores metrics

---

### Provider Independence

The rest of SARATHI never communicates directly with provider APIs.

All providers expose the same interface.

---

### Standardized Responses

Every provider returns the same response object.

No provider-specific response handling exists outside the provider implementation.

---

### Extensibility

Adding a new provider requires:

1. Create provider class
2. Implement generate()
3. Register provider

No other subsystem requires modification.

---

### Offline First

Whenever internet connectivity is unavailable, SARATHI automatically falls back to local execution using Ollama.

---

# Future Improvements

- Persistent analytics database
- Real token pricing
- Dynamic provider benchmarking
- Streaming execution
- Tool calling
- Vision routing
- Automatic model benchmarking
- Learning-based routing
- Provider health monitoring
- Multi-provider consensus
- Parallel execution

---

# Phase Status

Phase 7 – LLM Orchestration Engine

Completed:

- Provider Framework
- Multi-provider Support
- Intelligent Router
- Offline Intelligence
- Execution Engine
- Analytics
- Latency Tracking
- Usage Tracking
- Cost Tracking
- Feedback System
- Adaptive Routing

Status:

**Stable**

---