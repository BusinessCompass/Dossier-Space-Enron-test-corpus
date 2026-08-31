# Dossier Space Corpus Onboarding Primer

**Document ID:** DS-PRIMER-CORPUS-ONBOARDING  
**Version:** 0.2  
**Version date:** 2026-08-31  
**Status:** Draft for operational use  
**Purpose:** Formal onboarding of a corpus into a Dossier Space  
**Initial application:** Full raw Enron corpus on sovereign local workstation  
**Applies to:** Human Operator, Design/Leader AI, execution tools, Dossier Space analytical AI, and Assurance reviewer  
**Change control:** v0.2 adds explicit post-onboarding Dossier Space axis activation while preserving the onboarding pipeline as the infrastructure layer.

---

## 1. Directive

A corpus must not become analytically active within Dossier Space until its identity, location, integrity, structure, provenance, accessibility, limitations, and working controls have been established and recorded.

Every onboarding must follow the sequence:

> **EXPECTED → EXECUTION → OBSERVED → ROMER → ASSURANCE → ACCEPTANCE**

The purpose is not merely to confirm that files exist.

The purpose is to establish a **defensible baseline state** against which every subsequent analytical action can be understood, reproduced, challenged, or assured.

Original source evidence must remain unchanged.

Analysis takes place around the corpus, not inside it.

---

# 2. Governing Principles

The onboarding process shall follow these principles.

### 2.1 Evidence remains native

The original corpus should be preserved in its native form and directory structure wherever practicable.

No transformation, chunking, embedding, indexing, conversion, deduplication, renaming, or restructuring is required merely to make the corpus acceptable to Dossier Space.

Such techniques may later be used where analytically justified, but they must remain distinguishable from the source corpus.

### 2.2 Direct access is the default

The initial working assumption is that the AI and its authorised tools may interrogate the corpus directly at machine level.

RAG, embeddings, vector databases, indexing, classification, Diplomatics, AHP/ANP, statistical analysis, and other techniques are **selectable methods**, not architectural prerequisites.

### 2.3 Method follows need

No analytical technique should be used simply because it is available.

The reason for selecting a method must be capable of being stated and recorded.

### 2.4 Source and working material remain separated

The raw corpus must be distinguishable from:

- working files;
- temporary artefacts;
- indexes;
- scripts;
- search results;
- extracted evidence;
- findings;
- ROMER records;
- reports; and
- assurance records.

### 2.5 Significant actions must be visible

Material actions affecting the corpus, its interpretation, or subsequent analytical results should leave a reconstructible record.

### 2.6 Failure is part of the record

Errors, timeouts, incomplete searches, unavailable files, access problems, deviations, interventions, and unexpected results must not be silently removed from the analytical history.

### 2.7 Absence is not proof

Failure to locate material must not automatically be represented as proof that the material does not exist.

The method and extent of the search must support any statement concerning absence.

### 2.8 Portability

The Dossier Space should remain understandable and usable if:

- the AI model changes;
- the software tools change;
- the workstation changes;
- the original operator is unavailable; or
- another competent reviewer takes over.

---

# 3. Purpose of Corpus Onboarding

The onboarding session shall establish:

1. what corpus has been received;
2. where it came from;
3. where it is physically located;
4. what its apparent structure and scale are;
5. whether the source copy is complete relative to the available acquisition information;
6. what integrity records can reasonably be established;
7. what file types and structures are present;
8. what the AI and authorised tools can actually access;
9. what technical or evidential limitations exist;
10. what transformations, if any, have already occurred before receipt;
11. what controls will govern future interaction with the corpus; and
12. whether the corpus is suitable to be declared analytically active.

---

# 4. Roles

The onboarding record should identify the actual participants.

### Human Operator

Controls the workstation and physical corpus, authorises material actions, and retains ultimate human oversight.

### Design / Leader AI

Interprets this Primer, directs the planned onboarding process, identifies required checks, and reconciles expected and actual execution.

The Leader AI does not silently assume authority beyond the role granted to it.

### Execution Tools

May include operating-system functions, PowerShell, Python, database tools, hashing utilities, search tools, or other authorised software.

Execution tools perform actions but do not independently redefine the method.

### Dossier Space Analytical AI

May interrogate the corpus once permitted by the onboarding state and subsequent session authority.

### Assurance

Reviews whether the onboarding record supports the claimed corpus baseline and analytical readiness.

Where independent assurance is used, it should remain distinguishable from execution.

---

# 5. CIPDA Onboarding Cycle

## C — Context

Before action, establish the known circumstances surrounding the corpus.

Record:

- corpus name;
- corpus description;
- source;
- acquisition route;
- acquisition or copy date where known;
- physical location;
- storage device;
- filesystem;
- approximate size;
- approximate file count if known;
- original directory structure;
- known provenance;
- previous processing or transformations;
- known versions or copies;
- expected corpus characteristics;
- relevant prior custody records;
- available technical documentation;
- operator identity;
- AI/tool roles;
- workstation environment;
- permissions and access constraints;
- known uncertainties; and
- relevant limitations.

For the initial implementation, the corpus is expected to be the **full raw Enron corpus** residing on the dedicated Dossier Space drive.

No assumption of completeness should be made merely because the corpus is described as “full”.

---

## I — Intent

The intended result of onboarding is to:

> **Establish and preserve a reliable baseline description of the corpus and confirm whether it can safely enter analytical use within Dossier Space.**

The onboarding is not intended to:

- perform substantive evidential analysis;
- reach case findings;
- optimise the corpus prematurely;
- create RAG solely because it is available;
- transform the raw source unnecessarily;
- alter native evidence;
- conceal technical problems;
- infer completeness without evidence; or
- treat a successful technical copy as equivalent to evidential acceptance.

---

## P — Plan

Before execution begins, create an **EXPECTED record**.

The EXPECTED record shall state what is intended to happen.

At minimum it should contain:

### Corpus checks

- confirm physical source location;
- confirm destination location;
- identify corpus root;
- inspect directory structure;
- establish approximate size;
- establish file count or another practical inventory measure;
- identify principal file formats;
- identify inaccessible or anomalous material;
- preserve native structure.

### Custody checks

Determine an appropriate custody baseline proportionate to the corpus.

This may include:

- acquisition record;
- source and destination identification;
- volume size;
- directory inventory;
- file counts;
- manifest creation;
- selected or complete hashing;
- filesystem metadata;
- copy records;
- timestamps;
- duplicate/version information; and
- verification records.

The method chosen must be recorded.

For a corpus of approximately 120 GB, custody should be technically realistic and should not create disproportionate processing merely for appearance of completeness.

### Access checks

Confirm what the working AI/tool environment can actually:

- list;
- open;
- search;
- parse;
- hash;
- query;
- extract; and
- preserve.

### Logging checks

Confirm that material execution can be captured in appropriate logs.

### Separation checks

Confirm that:

- raw evidence is read-only or operationally protected;
- working outputs go elsewhere;
- evidence artefacts have their own location;
- findings remain separate from raw results;
- logs are preserved;
- ROMER records have a defined location; and
- assurance records remain identifiable.

### Validation action

Define one or more **small, bounded, non-substantive direct-access tests** sufficient to demonstrate that the corpus can be interrogated without modifying it.

The purpose is to validate the environment, not to reduce the corpus.

The small test must not become a substitute corpus or architectural dependency.

---

# 6. EXPECTED Record — Mandatory Before Action

No formal corpus onboarding execution should begin until the EXPECTED record exists.

The record should answer:

### What are we about to do?

Describe the planned onboarding actions.

### Why are we doing them?

State their purpose.

### What evidence or system will be touched?

Identify the corpus areas and tools involved.

### What should remain untouched?

Explicitly identify protected source material.

### What methods will be used?

List intended commands, tools, scripts or procedures at an appropriate level of detail.

### What do we expect to obtain?

Identify expected manifests, logs, counts, hashes, inventories or validation results.

### What would constitute success?

Define the acceptance criteria.

### What could go wrong?

Identify known risks and uncertainties.

### What requires human intervention or approval?

Define checkpoints where applicable.

---

# 7. Execution

Execution shall follow the EXPECTED record unless a justified change becomes necessary.

Material actions should be logged with sufficient detail to reconstruct:

- action;
- date/time where material;
- actor or tool;
- target;
- command or method;
- parameters where relevant;
- output location;
- success/failure;
- error information;
- human intervention; and
- deviation from plan.

Routine machine noise need not be preserved merely because it exists.

The requirement is **material reconstructibility**, not indiscriminate logging.

---

# 8. OBSERVED Record — Mandatory After Action

Following execution, create an **OBSERVED record**.

This must describe what actually happened rather than what was supposed to happen.

Record:

- corpus actually found;
- actual location;
- actual size;
- actual inventory characteristics;
- actual file structures;
- formats encountered;
- access limitations;
- corrupt or anomalous material;
- custody results;
- hashes or manifests created;
- logging successfully captured;
- validation results;
- failures;
- timeouts;
- deviations;
- interventions;
- unexpected artefacts;
- missing expected material;
- unresolved issues; and
- any change required to the intended Dossier Space configuration.

The OBSERVED record should explicitly reconcile itself against EXPECTED.

For each material expected activity, record:

**Occurred as expected / Occurred differently / Did not occur / Unable to determine**

---

# 9. ROMER

The onboarding ROMER shall be compiled from the captured onboarding record.

It must not be written purely from recollection.

## R — Reasoning

Record:

- why the onboarding design was appropriate;
- why particular custody and validation methods were selected;
- why any technique was included or excluded;
- why deviations occurred; and
- the reasoning supporting analytical acceptance or refusal.

## O — Observations

Record the significant observed facts about:

- corpus structure;
- scale;
- access;
- anomalies;
- technical environment;
- custody;
- limitations;
- failures;
- missing information; and
- differences between expected and actual state.

Observation must be distinguishable from inference.

## M — Methods

Record:

- planned methods;
- actual methods;
- tools used;
- parameters where material;
- searches or validation operations;
- custody methods;
- transformations, if any;
- deviations from plan; and
- limitations of the methods used.

## E — Evidence

Reference the artefacts supporting the onboarding assessment, including as appropriate:

- acquisition records;
- manifests;
- hashes;
- directory inventories;
- file counts;
- logs;
- scripts;
- command outputs;
- validation results;
- screenshots where justified;
- machine/environment records;
- EXPECTED record;
- OBSERVED record; and
- other relevant custody material.

Evidence should be referenced rather than unnecessarily duplicated.

## R — Results

State clearly:

- whether the corpus is accepted;
- whether it is accepted with limitations;
- whether further action is required;
- whether substantive analysis may begin;
- what baseline has been established;
- what uncertainties remain;
- what restrictions apply; and
- what should be carried forward into future analytical sessions.

---

# 10. Assurance

The onboarding must receive an explicit assurance outcome before the corpus becomes analytically active.

Assurance should test at least:

### Identity

Is there sufficient evidence that this is the corpus claimed?

### Integrity

Has a reasonable integrity/custody baseline been established?

### Separation

Is raw evidence adequately separated from working material?

### Accessibility

Can authorised tools reliably access the corpus?

### Visibility

Are material actions capable of being recorded?

### Reconstructibility

Could another competent person or AI understand what was done?

### Expected versus actual

Have material differences between planned and actual execution been identified?

### Limitations

Are limitations and uncertainties visible rather than buried?

### Method neutrality

Has the environment avoided unnecessarily committing future work to one retrieval or analytical technique?

### Analytical readiness

Is there sufficient basis to permit substantive analysis?

---

# 11. Acceptance States

The assurance outcome should use one of four states.

### ACCEPTED

The corpus baseline is sufficiently established for substantive Dossier Space analysis.

### ACCEPTED WITH LIMITATIONS

Analysis may begin, but specified limitations must remain visible and be carried into relevant sessions and ROMER records.

### REMEDIATION REQUIRED

The corpus is present but one or more onboarding conditions require correction before analytical activation.

### NOT ACCEPTED

The available evidence is insufficient to establish a reliable corpus baseline.

---

# 12. Activation Gate

The governing rule is:

> **No corpus becomes analytically active until EXPECTED, EXECUTION, OBSERVED, ROMER and ASSURANCE are complete to a level proportionate to the corpus and intended use.**

Analytical tools may be used during onboarding only where required to validate the environment.

Their use does not itself constitute acceptance.

---

# 13. Post-Onboarding Analytical Rule

Once accepted, the corpus becomes the **native evidential substrate** of the Dossier Space.

Future analytical sessions may select appropriate techniques including:

- direct machine interrogation;
- full-text search;
- metadata search;
- regex;
- timeline reconstruction;
- relationship analysis;
- Diplomatics;
- RAG;
- semantic retrieval;
- AHP/ANP;
- statistics;
- anomaly detection;
- classification;
- clustering;
- or other justified methods.

Each method remains subordinate to the question being asked.

Where material, its selection and application should be visible through the session Primer, EXPECTED record, OBSERVED record and ROMER.

## 13.1 Analytical Space / Axis Activation

Completion of corpus onboarding establishes the reliable analytical pipeline. It does **not** by itself define how a substantive evidential question will be explored.

For each substantive analytical session, the session Primer should explicitly declare the Dossier Space dimensions that are active for that question. This is the point at which the multidimensional analytical structure is turned on.

At minimum, record:

### Anchor

Define the evidential reference point from which the analysis begins. This may be a document, event, person, communication, transaction, issue, or other justified point of reference.

Where the original three-axis model is being used, this reference point should be treated as the **0,0,0 anchor** for that analytical session.

### Active axes

Identify the evidential dimensions that will be traversed for the question. The Primer should state which axes are active rather than allowing them to remain implicit in search commands or workflow steps.

The axes may include the established Dossier Space dimensions and, where justified, additional or refined dimensions developed through later analytical use.

### Traversal intent

State what is being followed away from the anchor and why. Examples may include chronology, relationships, provenance, communication sequence, evidential dependency, contradiction, or another relevant analytical movement.

### Cross-axis checks

State what corroboration, contradiction, absence, divergence, dependency, or other relationship should be tested across the active dimensions.

A finding on one axis should not automatically be treated as complete where another active axis could materially support, qualify, or undermine it.

### Inactive axes

Where material, identify dimensions deliberately not activated for the session. This makes analytical omission explicit rather than accidental.

### Axis record in ROMER

The ROMER for the session should preserve:

- the anchor selected;
- the axes activated;
- the reason for their selection;
- the traversal actually performed;
- material cross-axis observations;
- limitations or axes not examined; and
- whether the analytical path changed during execution.

The governing distinction is:

> **The onboarding pipeline establishes how Dossier Space operates reliably. Axis activation establishes how the evidence is examined for a particular analytical purpose.**

The pipeline should therefore remain method-neutral. The axes become explicit when substantive analysis begins.

---

# 14. Model Dossier Space Requirement

This onboarding process should be designed so that it can be repeated on another suitable workstation by another competent operator or AI.

Machine-specific configuration may differ.

The governing structure should not.

A successful implementation should pass this test:

> **If the current AI, operator, software or machine were replaced, could a competent successor identify the corpus, understand its custody, determine what was done, recognise its limitations, and continue the work without relying on the originating conversation?**

If not, the onboarding record is incomplete.

---

## Revision History

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-08-31 | Initial corpus onboarding Primer. |
| 0.2 | 2026-08-31 | Added explicit Analytical Space / Axis Activation after onboarding; defined anchor, active and inactive axes, traversal intent, cross-axis checks, and ROMER capture. Clarified separation between infrastructure pipeline and multidimensional analytical reasoning. |

---

# 15. Working Principle

> **Preserve the source.  
> Define what should happen.  
> Record what actually happens.  
> Reconcile the difference.  
> Preserve the evidence of the work.  
> Assure the result before relying upon it.**

This is the baseline from which the Dossier Space becomes operational.