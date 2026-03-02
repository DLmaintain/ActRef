
# Developer Guide: Adding a New Refactoring Type to ActRef

This document describes how to extend **ActRef** with a new refactoring type.
The guide is aligned with ActRef’s current architecture, which is based on:

* AST-level differencing (GumTree-based edit actions)
* Action-pattern composition
* Rule-based structural guards
* Structured refactoring records
* Instance-level evaluation against ground truth

This guide does **not** implement the detection logic itself. Instead, it explains how to correctly integrate a new refactoring type into the existing pipeline while preserving consistency, reproducibility, and evaluation comparability.

---

# 1. Overview of ActRef Detection Pipeline

Before adding a new type, it is important to understand the current detection flow:

1. **Commit Input**

   * Each commit consists of pre- and post-change source files.

2. **AST Differencing**

   * GumTree generates atomic edit actions:

     * `Insert`
     * `Delete`
     * `Move`
     * `Update`

3. **Action Normalization**

   * Actions are filtered and grouped by entity (function, class, module, etc.).

4. **Pattern Matching**

   * Refactoring rules are triggered by specific combinations of actions.

5. **Structural Guards**

   * Additional constraints prevent false positives.

6. **Structured Refactoring Record Generation**

   * Each detected refactoring is emitted in a unified schema.

7. **Evaluation Layer**

   * Structured records are matched against ground truth for TP/FP/FN calculation.

A new refactoring type must integrate into **Steps 4–6**, without breaking Steps 1–3 or evaluation logic.

---

# 2. Step 1 — Define the Refactoring Semantics

Before writing any detection rule, formally define the new refactoring in the project codebook.

Update:

```
dataset/codebook.md
```

Include:

* **Refactoring Name**
* **Location**
* **Src(Source Parent)**	
* **Dst(Destinition Parent)**
* **Example**
* **Heuristic**


Do not implement detection logic before the definition is stable.

---

# 3. Step 2 — Identify AST Granularity

Determine the structural level of the new refactoring:

* Function-level
* Class-level
* Module-level
* Cross-file


ActRef’s matching logic depends on consistent entity granularity.

You must specify:

* The primary AST node type (e.g., `FunctionDef`, `ClassDef`)
* Whether detection requires subtree comparison
* Whether file path changes are involved

If the refactoring involves file-level operations, ensure it is handled consistently with existing module-level logic (e.g., `Move Module`, `Rename Module`).

---

# 4. Step 3 — Define Required Action Patterns

ActRef relies on **combinations of edit actions** rather than textual heuristics.

For the new refactoring, specify:

## 4.1 Required Actions

Examples:

* Insert Node
* Delete Node
* Move Subtree
* Update Identifier

Clearly describe:

* Minimum action set
* Action ordering (if required)
* Whether actions must refer to the same entity

Example:

```
Required:
- Update (identifier)
- No structural changes inside body subtree
```

---

## 4.2 Forbidden Actions

Define guard conditions to reduce false positives.

Examples:

* Body modification exceeding threshold
* Additional Insert/Delete inside subtree
* Mixed semantic edits

Every new refactoring rule must explicitly list:

* What is allowed
* What invalidates detection

---

# 5. Step 4 — Implement Rule Integration

Integrate the new rule into the existing pattern-matching layer.

This typically involves:

* Adding a new rule handler
* Registering it in the detection pipeline
* Ensuring ordering does not conflict with existing rules

Important considerations:

* Avoid overlapping rule triggers.
* If the new rule conflicts with an existing one, define priority resolution.
* Ensure no duplicate emission of structured records.

Detection must remain deterministic.

---

# 6. Step 5 — Structured Refactoring Record Schema

All detected refactorings must conform to ActRef’s unified structured schema.

Each record should include:

```json/csv
{
  "type": "...",
  "source_entity": "...",
  "target_entity": "...",
  "entity_type": "...",
  "source_location": "...",
  "target_location": "...",
  "signature": "...",
  "additional_metadata": {...}
}
```

Guidelines:

* Use consistent naming conventions.
* Use file paths for module-level refactorings.
* Do not omit entity type.
* Ensure compatibility with evaluation matching logic.

If new metadata fields are introduced, update:

* Evaluation matching logic
* Documentation

---

# 7. Step 6 — Preventing False Positives

New refactoring rules must include defensive checks.

Common sources of false positives:

* Mixed edits (refactoring + feature change)
* Partial renames with semantic change
* File relocation with internal modifications
* Rename + Extract combined cases

Add structural guard conditions such as:

* Body equivalence checks
* AST subtree similarity threshold
* Entity consistency validation

False positives degrade evaluation credibility. Conservative detection is preferred over aggressive matching.

---

# 7. Design Principles to Follow

When extending ActRef:

* Prefer structural consistency over heuristic shortcuts.
* Avoid string-based matching.
* Ensure deterministic output.
* Maintain strict entity-level granularity.
* Preserve compatibility with evaluation scripts.

ActRef is designed as a structured, action-driven refactoring detector.
All extensions must respect this design philosophy.

---

# 8. Checklist Before Merging a New Refactoring Type

* [ ] Codebook updated
* [ ] Action pattern defined
* [ ] Structural guards added
* [ ] Structured schema validated
* [ ] Evaluation re-run
* [ ] Documentation updated
* [ ] Replication package synchronized

