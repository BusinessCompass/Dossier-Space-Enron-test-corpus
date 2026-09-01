# Dossier Space

**A sovereign, method-neutral environment for governed AI-assisted evidence analysis**

Dossier Space is an experimental working architecture for using AI directly with large evidential or documentary collections while preserving visibility, provenance, method, and assurance.

Periodic articles were published by the UK Society for Computers and Law   https://www.scl.org/ai-assisted-evidence-and-the-dossier-space-experiment/

It was developed through practical testing against the public Enron email corpus and is intended to explore a simple question:

**Can AI work directly over a substantial body of evidence while leaving a record sufficiently clear, complete and reconstructible for another human or AI to understand what was intended, what actually happened, what evidence was used, and how the resulting conclusions were reached?**

**How far coud we go with common-day equipment and a technically literate but non-coder opeator**

It was pursued using most contemporary AI models which demonstrated the analytical capabiities necessary. while lacking in a desktop interface.

More specifically used Anthropic Claude and ChatGPT chat panels, wth Claude Code and GPT Codex desk top interfaces to woring purposes.

Dossier Space is not a particular AI model, retrieval technology, database, or software product.

Dossier Space was tested on a vanilla Windows 11 workstation, using out-of-the-box software and AI. AI took the lead in designing and operating.

## Dossier Space Pilot — Session Purpose Summary

The Dossier Space Pilot developed progressively from basic platform validation through evidential analysis, governance testing, reproducibility, and transportability. Each session was intended to test a distinct part of the overall method.

**Session 1 — Establish the Dossier Space**
Create the initial working environment, define the pilot boundaries, establish roles, custody expectations, governance records, and the basic Dossier Space operating model.

**Session 2 — Establish the Evidence Baseline**
Load and inspect the Enron corpus, confirm that the dataset could be accessed reliably, and establish a known evidential baseline against which later analytical work could be tested.

**Session 3 — Introduce Primers**
Test whether explicit Primers could guide AI analysis consistently by defining purpose, scope, constraints, evidential expectations, and the reasoning approach before analysis began.

**Session 4 — Test More Complex Analysis**
Move beyond straightforward retrieval into questions requiring interpretation, linkage between records, chronology, contextual reasoning, and identification of uncertainty.

**Session 5 — Test Structured Analytical Methods**
Explore whether established methods and analytical techniques could be invoked within the Dossier Space where relevant rather than relying on unconstrained AI reasoning alone.

**Session 6 — Test Evidential Traceability**
Examine whether findings could be traced back through the analytical process to the underlying source material, search steps, decisions, and supporting evidence.

**Session 7 — Test Governance and Assurance**
Strengthen the distinction between analysis, operator oversight, and independent assurance, and examine whether the analytical process itself could be reviewed rather than merely its final output.

**Session 8 — Test the Dossier as a Reconstructible Record**
Assess whether another reviewer could understand what had been asked, what had been done, what evidence had been considered, and why the resulting conclusions had been reached.

**Session 9 — Divergence / “Hanging Thread” Smoke Test**
Test whether the Dossier Space could identify references to communications or events that appeared in the documentary record but for which no corresponding documentary trace could be found. This introduced missing evidence and evidential divergence as analytical findings in their own right.

**Session 9.5 — Reconciliation and Governance Repair**
Investigate discrepancies exposed by the Session 9 rerun, reconcile competing result sets, improve logging and custody controls, and preserve rather than conceal differences between analytical runs.

**Session 10 — Architecture Validation**
Test whether the improved Dossier Space architecture could reproduce the earlier smoke test with stronger custody, instrumentation, hashing, logging, result persistence, and fail-closed controls.

**Session 11 — Independent Smoke-Test Validation**
Re-run the divergence analysis as a formal validation exercise to determine whether the principal finding survived independent reconstruction and whether the supporting counts and evidence remained defensible.

**Session 12 — Documentary Sequence Reconstruction**
Test a more realistic evidential task: reconstructing the documentary sequence surrounding Vince Kaminski's analysis or concerns relating to LJM/Raptor valuations, including participants, chronology, information exchanged, responses, off-email activity, and evidential gaps.

**Session 13 — Transportability and Role Separation**
Test whether a fresh AI environment could reconstruct the Dossier Space from its repository and documentation alone. The session also examined separation between the AI leading the analytical process, the coding tools executing technical work, the human operator, and external assurance.

**Session 14 — Replication and Error Detection**
Re-run the earlier smoke test independently to determine whether the principal conclusion could be replicated and whether discrepancies in supporting counts or earlier assertions could be detected. The conclusion survived, while several supporting measurements were corrected.

** Session 15 - Onboarding Raw Enron corpus workin.g**

** Session 16 - Planning for a simulated investigation of the corpus.**

### Overall Progression

Taken together, the sessions moved the pilot through a deliberate sequence:

**environment → evidence → guided reasoning → complex analysis → traceability → governance → reproducibility → divergence detection → reconciliation → architecture validation → independent validation → realistic case analysis → transportability → replication.**

The purpose of the pilot was therefore not simply to test whether AI could analyse a large evidence corpus. It was to determine whether AI-assisted analysis could become **visible, governed, reproducible, challengeable, and evidentially defensible**.

It is a **working method and evidential architecture** within which different technologies and analytical techniques can be used where appropriate.

---

## Core principle

**Evidence remains native. Methods are selectable. Actions are visible. Material artefacts are captured. ROMER reconciles intent with execution. Assurance tests the record.**

**Organise the information → Work with the information → Govern and assure the reasoning**

The architecture deliberately separates the enduring method from the technologies used to implement it.

AI platforms, retrieval methods and computational techniques will change. The requirement for work to remain visible, reviewable and reproducible should not.

---

## Why Dossier Space?

Much current AI architecture concentrates on getting information into a model through techniques such as:

* chunking;
* embeddings;
* vector databases;
* Retrieval-Augmented Generation (RAG);
* summarisation; and
* context management.

These remain useful techniques, but Dossier Space does not assume that any one of them is necessary.

As AI systems gain increasingly capable access to filesystems, databases, code execution and local machine resources, the problem changes.

The important question becomes less:

> **How do we feed the information to the AI?**

and increasingly:

> **How do we govern, observe and evidence what the AI does with the information?**

Dossier Space therefore treats direct access to native evidence as the default substrate and makes additional analytical methods available when justified by the task.

---

## Method-neutral by design

A Dossier Space may use, among other techniques:

* direct filesystem and database interrogation;
* conventional full-text, metadata and regular-expression search;
* timeline and sequence reconstruction;
* entity and relationship analysis;
* statistical and anomaly analysis;
* classification and clustering;
* Retrieval-Augmented Generation;
* embeddings and semantic retrieval;
* Diplomatics and documentary analysis;
* AHP, ANP and other structured decision methods; and
* purpose-built scripts and analytical tools.

No technique is automatically preferred.

**The evidential question should determine the method, not the availability or fashion of the technology.**

Where a method is used, the Dossier Space should record why it was selected, how it was applied, what parameters or constraints were used, and what effect it had on the resulting analysis.

---

## Expected versus actual

A central Dossier Space principle is that important work is recorded twice.

### Before execution

Record what is expected to happen:

* question or task;
* scope;
* permitted evidence;
* intended method;
* constraints;
* expected searches or actions;
* success criteria;
* known uncertainties; and
* assurance requirements.

### After execution

Record what actually happened:

* evidence accessed;
* searches and actions performed;
* parameters used;
* results obtained;
* errors and failures;
* deviations from the intended method;
* human interventions;
* missing evidence;
* unresolved uncertainty; and
* consequential changes to the analysis.

The difference between expected and actual execution is itself evidence.

---

## ROMER

Dossier Space uses **ROMER** to structure the analytical record:

**R — Reasoning**
Why the analytical approach was chosen and how conclusions were developed.

**O — Observations**
What was encountered during the work, including unexpected findings and absences.

**M — Methods**
What methods were intended, what methods were actually used, and any material deviations.

**E — Evidence**
The documents, records, searches, result sets, hashes, logs and other material supporting the work.

**R — Results**
What can properly be concluded from the analysis, including limitations and uncertainty.

ROMER should be produced from the captured working record rather than reconstructed afterwards from memory.

---

## Primers and CIPDA

A Dossier Space can use a **Primer** to establish the governing context for a task or session.

For more complex work, the **CIPDA** cycle may be used:

**Context → Intent → Plan → Deliver → Assure**

Together these provide a structured way to define the task before execution and evaluate the resulting work afterwards.

They are intended to support disciplined human–AI working rather than replace professional judgement.

---

## Typical Dossier Space structure

A model implementation may use a structure similar to:

```text
DOSSIER_SPACE_ROOT/
│
├── 00_CONTROL/
├── 01_RAW_CORPUS/
├── 02_CUSTODY/
├── 03_PRIMERS_METHODS/
├── 04_SESSIONS/
├── 05_WORKING/
├── 06_LOGS/
├── 07_EVIDENCE/
├── 08_FINDINGS/
├── 09_ROMER/
├── 10_OUTPUTS/
├── 11_ASSURANCE/
├── 12_TOOLS/
├── 13_METHOD_LIBRARY/
└── 99_ARCHIVE/
```

The important distinction is between:

**Source evidence** — preserved and unchanged.

**Working material** — disposable or reproducible intermediate activity.

**Evidential artefacts** — preserved searches, extracts, results and supporting records.

**Findings and outputs** — conclusions produced from that evidence.

**Assurance** — independent or subsequent examination of whether the recorded process and conclusions are supported.

---

## Raw evidence

Original source material should ordinarily remain untouched.

Analysis takes place **around the evidence rather than inside it**.

Where practical, custody information, manifests, hashes or equivalent integrity records should establish what corpus was available when the analysis was performed.

Dossier Space is therefore compatible with conventional evidential and digital-preservation principles rather than attempting to replace them.

---

## Human in the loop

Dossier Space does not assume autonomous AI decision-making.

The pilot has deliberately explored separation between roles including:

* Human Operator;
* Design or Leader AI;
* execution tools or code;
* analytical AI;
* and independent assurance.

The exact roles may vary between implementations.

What matters is that authority, execution and review are identifiable rather than silently merged.

---

## Findings

A finding should be capable of being traced back through the analytical record to the evidence supporting it.

Where appropriate, findings should retain:

* stable identifiers;
* source references;
* relevant searches or analytical steps;
* supporting and conflicting evidence;
* uncertainty;
* status;
* and subsequent review or correction.

A coherent narrative is not itself proof.

Missing evidence, failed searches and contradictory results may be analytically important and should not disappear simply because they make the final explanation less tidy.

---

## Assurance

Dossier Space treats assurance as part of the working architecture rather than an activity added only after a report is complete.

Assurance may ask:

* Did the planned work actually happen?
* Were the intended sources available?
* Were search parameters recorded?
* Were result sets preserved?
* Can important claims be reconstructed?
* Were failures and deviations recorded?
* Does the evidence support the finding?
* Are inference and observation distinguishable?
* Could another competent person or AI reproduce or challenge the work?

The objective is not to prove that an AI cannot make mistakes.

It is to make mistakes, omissions and analytical choices **discoverable**.

---

## The Enron pilot

The initial Dossier Space pilot uses the publicly available Enron email corpus as a substantial, realistic documentary environment.

Formal sessions have tested issues including:

* evidence discovery;
* sequence reconstruction;
* absence of corroborating records;
* search reproducibility;
* discrepancies between different search mechanisms;
* custody;
* logging;
* method changes;
* role separation;
* independent assurance; and
* reconstruction of earlier analytical work by a different AI.

These tests have repeatedly shown that the difficult problem is not simply obtaining an answer.

The more important problem is preserving sufficient evidence of the analytical process to determine **why that answer should — or should not — be trusted**.

---

## Current direction

The next stage is to test transporting the Dossier Space agent (Anthropic Code to to GPTCODEX) against the complete raw Enron corpus on a sovereign local workstation.

The intention is to begin with direct machine-level access to the native corpus rather than assuming that it must first be transformed into a RAG or vector architecture.

Additional methods can then be introduced selectively where the evidential task demonstrates that they add value.

The resulting workstation is intended to help explore whether a Dossier Space can become **portable rather than case-specific**.

A useful design test is:

> **If the AI technology were replaced tomorrow, would the Dossier Space still make sense, preserve the evidential record, and allow another capable system to continue the work?**

If the answer is yes, the enduring asset is not the model.

It is the **governed evidential workspace and the method surrounding it**.

---

## Repository status

This repository records experimental research and evolving working methods.

It should not presently be treated as:

* production legal software;
* an evidential standard;
* an autonomous decision system;
* or a substitute for professional judgement.

Structures, terminology and procedures may continue to change as further pilot sessions expose weaknesses or better approaches.

That change is intentional and should itself be recorded.

---

## Intended users

Although initially explored in a legal and evidential context, the architecture is potentially applicable wherever humans and AI need to work over substantial bodies of information under conditions requiring accountability and reconstruction.

Possible contexts include:

* litigation and investigations;
* regulatory work;
* compliance and GRC;
* audit;
* research;
* corporate investigations;
* due diligence;
* historical and archival analysis;
* public-sector decision support; and
* other evidence-intensive professional work.

---

## Design objective

Dossier Space is ultimately an experiment in making AI-assisted professional work **inspectable**.

Its proposition is straightforward:

> **The value of powerful AI increases when we can see and preserve what it actually did.**

The technology may change.

The record should remain.

