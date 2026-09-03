# College Assistant — Engineering Guidelines

## Project Overview

This project is a college assistant chatbot.

The existing CLI implementation is the behavioral reference for the new application. The goal is to transform the existing prototype into a maintainable, modular, production-oriented application with:

* FastAPI backend
* Next.js frontend
* LangGraph orchestration
* RAG-based knowledge retrieval
* Conversation/session memory
* Streaming assistant responses
* Clean API boundaries
* Proper testing
* Clear separation of concerns

The existing CLI implementation must be treated as legacy/reference code.

Do NOT blindly copy its structure into the new application.

Preserve its intended behavior while improving the architecture.

---

# Core Engineering Principles

Follow these principles throughout the project:

1. Separation of concerns
2. Single responsibility
3. Dependency inversion where appropriate
4. Explicit interfaces between layers
5. Reusable components and services
6. Strong typing
7. Clear naming
8. Minimal duplication
9. Testability
10. Security by default
11. Performance awareness
12. Maintainability over cleverness
13. Avoid unnecessary abstraction
14. Prefer simple solutions when they are sufficient

Do not over-engineer the application.

Every abstraction should have a clear purpose.

---

# Architecture

The application must maintain a clear separation between:

* API layer
* Business/service layer
* RAG/retrieval layer
* LangGraph/orchestration layer
* Data/repository layer
* Schemas/types
* Configuration
* Infrastructure
* UI components

API routes/controllers must not contain business logic.

Business logic must not be tightly coupled to FastAPI.

LangGraph logic must remain isolated from HTTP-specific concerns.

Frontend components must not directly contain API implementation details.

---

# Backend — FastAPI

Use FastAPI with a modular architecture.

Recommended responsibilities:

### API Layer

Responsible for:

* HTTP endpoints
* Request validation
* Response serialization
* Authentication/authorization when required
* HTTP-specific error handling

Do not place business logic inside route handlers.

### Services

Responsible for application/business logic.

Services should coordinate:

* Chat operations
* Conversation management
* RAG operations
* Graph execution
* Streaming
* Other application-level workflows

### RAG Layer

Keep retrieval functionality separate from the API and graph orchestration.

RAG responsibilities include:

* Document loading
* Chunking
* Embedding
* Vector store management
* Retriever creation
* Retrieval
* Context preparation

Avoid rebuilding expensive resources unnecessarily.

Prefer persistent/cached vector indexes where appropriate.

### Graph Layer

LangGraph should be responsible for:

* State definition
* Classification
* Routing
* Retrieval nodes
* Response generation
* Conversation flow

Do not put FastAPI request/response logic inside LangGraph nodes.

### Schemas

Use typed Pydantic models for API boundaries.

Avoid passing unstructured dictionaries throughout the application when a typed schema is appropriate.

### Configuration

Centralize configuration.

Use environment variables for:

* API keys
* Model configuration
* Application configuration
* Database configuration
* External service configuration

Never hardcode secrets.

Never commit `.env`.

Provide `.env.example`.

---

# Frontend — Next.js

Use a clean component-based architecture.

Separate:

* Pages/routes
* UI components
* Feature components
* API/service functions
* Hooks
* Types
* Utilities

Components should focus on presentation and UI behavior.

API communication should be isolated inside service/client modules.

Avoid putting large amounts of business logic inside React components.

Use TypeScript strictly.

Avoid `any` unless there is a documented reason.

Prefer reusable components over duplicated UI code.

---

# Type Safety

TypeScript must use strict typing.

Python code should use type hints consistently.

Avoid:

* unnecessary `Any`
* unnecessary type assertions
* untyped dictionaries
* duplicated type definitions
* implicit contracts

Types should represent actual domain concepts where useful.

---

# Error Handling

Handle errors intentionally.

Do not silently swallow exceptions.

Do not expose internal stack traces, API keys, prompts, or sensitive implementation details to clients.

Use consistent API error responses.

Log useful diagnostic information server-side.

---

# Security

Treat all external input as untrusted.

Validate API input.

Never trust client-side authorization.

Never expose secrets to the frontend.

Never hardcode API keys.

Avoid leaking retrieved documents or internal prompts unnecessarily.

Review authentication, authorization, CORS, input validation, and sensitive data handling before production.

---

# Performance

Consider performance when implementing features.

Pay particular attention to:

* repeated LLM initialization
* repeated embedding generation
* repeated PDF processing
* vector store rebuilding
* unnecessary database queries
* unnecessary API requests
* unnecessary React renders
* large payloads
* streaming behavior
* memory usage

Do not optimize prematurely.

First ensure correctness and architecture.

Then optimize actual bottlenecks.

---

# Testing

Important business logic must be testable.

Add tests for:

* API endpoints
* request validation
* classification/routing
* RAG retrieval behavior
* graph behavior
* services
* important edge cases

Do not rely only on manual testing.

After significant changes, run:

1. Type checks
2. Linting
3. Relevant tests
4. Build validation where applicable

Never declare a feature complete solely because the application starts successfully.

---

# Legacy Code

The legacy CLI implementation exists as a reference.

Before replacing behavior:

1. Understand what the existing implementation does.
2. Identify its inputs and outputs.
3. Identify business rules.
4. Identify existing limitations.
5. Preserve intended behavior.
6. Improve the architecture.

Do not modify legacy/reference code unless explicitly instructed.

Do not introduce breaking behavioral changes without explaining them.

---

# Development Workflow

For every significant feature:

1. Understand
2. Explore existing code
3. Identify dependencies
4. Plan
5. Discuss architectural concerns
6. Implement
7. Test
8. Review
9. Simplify
10. Verify
11. Document when necessary

Do not immediately start coding after receiving a complex requirement.

For complex tasks, first create an implementation plan.

---

# Self Review

Before considering a significant task complete, review the implementation like a senior staff engineer.

Check:

1. Correctness
2. Security
3. Performance
4. Scalability
5. Maintainability
6. Type safety
7. Error handling
8. Edge cases
9. Database efficiency
10. API design
11. Code duplication
12. Unnecessary complexity
13. Test coverage
14. Compliance with this CLAUDE.md

If issues are discovered:

* Explain them.
* Rank them by severity.
* Fix them where appropriate.
* Run relevant tests again.

Do not assume the implementation is correct simply because it compiles or builds.

---

# Communication Rules

When working on this project:

* Explain important architectural decisions.
* Ask before making major architectural changes that were not requested.
* Do not silently introduce new dependencies unless justified.
* Before installing a dependency, check whether the existing stack can solve the problem.
* Prefer established libraries over custom implementations when appropriate.
* Keep changes focused on the requested task.
* Do not modify unrelated files unnecessarily.
* Do not rewrite working code without a clear reason.

When uncertain, inspect the repository and existing documentation before making assumptions.

---

# Definition of Done

A feature is not complete until:

* Implementation is finished.
* Relevant tests pass.
* Type checks pass.
* Linting passes where configured.
* Error handling has been considered.
* Security implications have been considered.
* The implementation follows project architecture.
* No unnecessary duplication or complexity was introduced.
* The final changes have been reviewed.
