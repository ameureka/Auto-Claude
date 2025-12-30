# Gemini Agent Protocol: Kiro Specs Standard

This document defines the operational standards for Gemini agents working within the **Kiro Specs** framework. You must adhere to these protocols to ensure formal correctness, traceability, and high-quality software delivery.

## Core Methodology: Spec-Driven Development

You operate in three distinct, iterative phases. You must not proceed to the next phase without explicit user approval.

1.  **Requirements**: Define *what* to build using formal EARS syntax.
2.  **Design**: Define *how* to build it, proving correctness via formal properties.
3.  **Tasks**: Define *steps* to execute, linking back to requirements.

All artifacts are stored in `.kiro/specs/{feature-name}/`.

---

## Phase 1: Requirements (`requirements.md`)

**Goal**: Convert vague user intent into precise, testable specifications.

### 1. Syntax: EARS Patterns
Every requirement **MUST** use one of these patterns:

*   **Ubiquitous**: `THE <system> SHALL <response>` (Always true)
*   **Event-driven**: `WHEN <trigger>, THE <system> SHALL <response>` (On event)
*   **State-driven**: `WHILE <condition>, THE <system> SHALL <response>` (In state)
*   **Unwanted**: `IF <condition>, THEN THE <system> SHALL <response>` (Error handling)
*   **Optional**: `WHERE <option>, THE <system> SHALL <response>` (Config/Feature flag)
*   **Complex**: `[WHERE] [WHILE] [WHEN/IF] THE <system> SHALL <response>`

### 2. Quality Rules (INCOSE)
*   **Active Voice**: "THE system SHALL..." (Not "It should be...")
*   **Single Thought**: One requirement, one logic. Split complex ideas.
*   **No Ambiguity**: Ban words like "quickly", "user-friendly", "adequate".
*   **No Escapes**: Ban "where possible", "if feasible".

### 3. Special Handling
*   **Parsers/Serializers**: MUST include a "Round-trip" requirement (Parse -> Serialize -> Compare).

---

## Phase 2: Design (`design.md`)

**Goal**: Create a technical blueprint with machine-verifiable correctness guarantees.

### 1. Structure
*   **Architecture**: Mermaid diagrams showing flow/components.
*   **Interfaces**: TypeScript/Python interfaces defining data shapes.
*   **Correctness Properties**: The core of this phase.

### 2. Correctness Properties
You must define properties that hold true for **all valid inputs**, not just examples.

*   **Format**:
    ```markdown
    **Property N: [Name]**
    *For any* [input description], [invariant statement].
    **Validates: Requirements X.Y**
    ```
*   **Common Patterns**:
    *   **Invariant**: Size/shape remains constant.
    *   **Round-trip**: `decode(encode(x)) === x`.
    *   **Idempotence**: `f(f(x)) === f(x)`.
    *   **Metamorphic**: `len(filter(x)) <= len(x)`.

### 3. Prework
Before writing properties, analyze every Requirement:
*   `Testable: yes - property` -> Write a PBT.
*   `Testable: yes - example` -> Write a standard unit test.
*   `Testable: no` -> Mark as manual/visual only.

---

## Phase 3: Tasks (`tasks.md`)

**Goal**: An executable checklist for a coding agent.

### 1. Format
*   Use a nested checklist (max 2 levels).
*   **Traceability**: Every task must link to a Requirement ID.

### 2. Structure
```markdown
- [ ] 1. Implement Core Logic
  - Define interfaces and types
  - _Requirements: 1.1, 1.2_
- [ ]* 1.1 Write Property Tests: Round-trip
  - **Property 1: JSON Round-trip**
  - **Validates: Requirements 1.1**
```

### 3. Rules
*   **Optional (`*`)**: Only sub-tasks (like writing tests) can be optional. Top-level tasks are mandatory.
*   **PBT First**: Property test tasks should generally precede or immediately follow implementation tasks.
*   **Checkpoints**: Insert checkpoints to pause and verify tests pass.

---

## Coding Standard: Property-Based Testing (PBT)

When executing tasks, you prioritize PBT over simple example tests.

*   **Frameworks**:
    *   **TypeScript**: `fast-check`
    *   **Python**: `Hypothesis`
*   **Generator Rules**:
    *   Constrain inputs meaningfully (e.g., `fc.emailAddress()` not just `fc.string()`).
    *   Always test boundaries (empty lists, 0, negative numbers).
    *   Run >= 100 iterations.

---

## Quick Reference Checklist

Before submitting any artifact, ask:
1.  **Reqs**: Are all sentences EARS compliant? Is there a Glossary?
2.  **Design**: Do properties start with "For any"? Do they link to Reqs?
3.  **Tasks**: Are PBTs included as tasks? Is every task traced to a Req?

**You are the guardian of correctness. Do not compromise on rigor.**
