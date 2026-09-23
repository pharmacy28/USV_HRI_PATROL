# Scientific Writing Guide

This guide defines the house style for this IEEE ICRA paper. It governs
technical meaning and evidence discipline, not generic grammar correction.

## Definitions, equations, and notation

1. Introduce a new object with **“Let \(X\) denote ...”** or **“We define
   ... as ...”**. Use the latter only for a genuine definition.
2. State a quantity derived from already defined objects with **“is given by
   ...”**, rather than repeatedly writing “is defined as.”
3. Use an after-equation **“where”** clause only for symbols that have not
   already been introduced.
4. Use **“Here,”** for local semantic clarification, such as explaining what
   a probability means or what an evaluation variable records.
5. Use **“denotes”** for notation and **“represents”** for conceptual
   interpretation.
6. Do not repeat an immediate list of symbol definitions in a second
   sentence. Introduce only the information needed at that location.
7. Use **“respectively”** only for two ordered, matched lists.

## Logical and methodological prose

1. Reserve **“Thus,” “Therefore,”** and **“Hence,”** for an actual logical
   consequence. Do not use “Thus” merely to begin a paragraph.
2. Use **“Accordingly,”** for a methodological consequence of a stated
   premise.
3. Do not use colloquial labels such as “where to search” in place of formal
   scientific definitions.
4. Distinguish what is **estimated from data**, **selected on held-out
   validation**, **derived from map or physics**, **specified from mission
   risk**, and **chosen as a baseline design decision**.
5. Do not present a design choice, calibration decision, or experimental
   setting as if it were a mathematical fact.
6. Prefer compact IEEE prose. Explain a symbol once, and do not narrate every
   standard implementation step.
7. Audit and remove weak recurring phrases unless they add precise meaning:
   “The resulting question is ...,” “Thus, ...,” “In this way ...,” “It can
   be seen that ...,” “Obviously,” and “Clearly.”

## Evidence and novelty discipline

1. Every literature claim requires a verified source before it enters the
   manuscript. A metadata-verified paper may support bibliographic facts and
   an abstract-level description only.
2. A strong novelty comparison requires a locally read or otherwise
   PDF-verified primary paper. Do not infer methods, assumptions, or results
   from a title.
3. Describe Bayesian filtering, A*, Hungarian assignment, Lloyd/K-means, and
   Random Forest only as implementation components when applicable; do not
   present any of them alone as this paper's contribution.
4. State hypotheses and evaluation plans as hypotheses and plans. Do not
   convert anticipated benefits into reported findings.

## Paper-specific preferred terminology

Use the following terms consistently:

- predictive spatial responsibility redistribution;
- future position at horizon \(H\);
- future spatial responsibility;
- fixed responsibility anchor;
- belief-aware responsibility generation;
- path-dependent vehicle--center assignment;
- effective correct detection;
- residual missed-detection risk.

Do not replace “future position at horizon \(H\)” with “destination” unless
the text specifically concerns an explicit \(g_{\mathrm{cmd}}\). Keep
interaction modalities separate from planner-level command semantics.
