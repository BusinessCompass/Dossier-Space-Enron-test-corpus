# Concept extraction pilot — DS-20260905-S23

Status: completed exploratory analysis; self-checked, not independently assured or operator-accepted.

Only the D: raw corpus was used. Source files were opened read-only; attachments were excluded from text analysis. This is a capability demonstration, not a corpus-wide finding.

## Sample and method

The small bailey-s archive was chosen for a bounded pilot. From 2,178 native .eml entries, 30 were selected by ranking SHA-256(seed + archive entry path), with seed DS-S23-concepts-v1|. The sample was fixed before reading it; there was no topic-based selection or replacement of sparse records. See ../00_PLAN/EXPECTED.yaml and ../01_ACTUAL/sample.py.

24 records had no usable plain-text body after the EDRM licence footer was removed; 13 of these were marked Calendar. S11 contained only an identifier-like string; S16 pointed to an excluded attachment. Four records (S02, S05, S10, S28) supported substantive body concepts. No empty-body finding establishes that other representations of the record contain no information.

S05 and S10 have important header-like text embedded in the body, while outer From/Subject fields are blank. Sender and subject interpretations for those records come from that embedded text and quoted-message structure, not populated outer headers. No XML or text sidecar was opened; no HTML fallback was needed for this sample.

## Concepts and evidence

### C01: Agreement execution and document availability

Tracking whether signed agreements or fully executed copies are available.

Support: [S05](../02_RESULTS/S05.txt): "Executed copy is not available."

Quoted earlier message by Susan Bailey; sender reports a document-availability gap, not proof that execution never occurred.

### C02: Document retrieval and follow-up

Asking another team to locate records and following up on unresolved requests.

Support: [S05](../02_RESULTS/S05.txt): "I sent a reminder to Tom Moran today and will follow up with him tomorrow."

Top-level reply attributed to Nony Flores in embedded headers; follow-up is stated, its later outcome is unknown.

### C03: Document-set completeness across delivery formats

Different coverage in hard-copy and electronic document sets.

Support: [S10](../02_RESULTS/S10.txt): "The only document not included was the Florida Power & Light Company ("FPL") agreement."

Quoted Bailey message says the hard-copy set omitted FPL while the electronic/PDF set included it; not an independently verified inventory.

### C04: Handover responsibility

Assigning responsibility for onward delivery of documents.

Support: [S10](../02_RESULTS/S10.txt): "If you want to present E&Y with the electronic/pdf versions, you will need to do that."

Quoted Bailey instruction to Hlopak; the reply promises action but does not prove delivery.

### C05: Recipient identity disambiguation

Correcting confusion between people sharing a name.

Support: [S10](../02_RESULTS/S10.txt): "was the Ed, Sr - my father."

Quoted Hlopak message reports earlier emails addressed to his father; no wider disclosure or harm finding is made.

### C06: Counterparty trade inventory and review

Circulating a stated inventory of financial trades for review.

Support: [S02](../02_RESULTS/S02.txt): "all financial trades"

Brant Reves describes a spreadsheet of ENA trades with the subject-named entity, Glencore Commodities Ltd.; spreadsheet contents and completeness were not examined.

### C07: Time-exception reporting

Reporting whether exceptions exist for a specified reporting period.

Support: [S28](../02_RESULTS/S28.txt): "I have NO exceptions for the time period covering February 1-15."

Explicit negative report; do not classify as an actual exception or infer a broader compliance result.

## Relationships and distinctions

- S05: Bailey asks Flores about unavailable/partly executed agreement copies; Flores reports a reminder to Moran. The document request and follow-up are observed statements; a general document-control weakness is only a hypothesis.
- S10: Bailey distinguishes hard-copy from electronic/PDF coverage and places onward electronic delivery with Hlopak. His promise does not establish completion.
- C01 and C03 fall under the analyst-created parent concept "agreement documentation management". That grouping is an interpretation, not a phrase or formal taxonomy asserted by the senders.
- S02 refers to an attached spreadsheet. It supports the communication of a trade inventory, not verification of the trades.
- S28 is a negative report: no exceptions. Negation is preserved.

## Sparse records and competing explanations

Repeated legal/credit and SWAP meeting subjects suggest topics only; they cannot establish what was discussed or decided. Calendar, organizer and personal scheduling records are mixed with email correspondence. Repeated subject labels are not independent evidence of repeated substantive events. The sample contains repeated 30 November 2002 calendar dates and three 31 December 1979 organizer dates; these must not be assumed to be reliable underlying event dates without further examination.

The narrow single-mailbox sample and four substantive bodies make frequencies unreliable outside this sample. S05 and S10 include quoted earlier correspondence: multiple quoted statements in one item are not independent corroboration. Attachments, other mailboxes, linked text/XML representations and F: were excluded. No legal conclusion, wrongdoing finding, or corpus-wide negative finding is warranted.

## Reproduction and validation

[Sample and decoded text](../02_RESULTS/sample.json), [source references](../02_RESULTS/source-manifest.csv), [concept table](../02_RESULTS/concepts.csv), and [self-checks](../04_ASSURANCE/self-checks.json) are preserved. Seven support strings were checked against the saved decoded bodies, and all 30 source-entry hashes were rechecked. Archive size and modification time matched the extraction record. A closure archive hash is recorded; it is not a newly established pre-analysis hash baseline.

Recommended next pilot: retain this sample as a record-quality test, then use a separately declared body-bearing correspondence sample across several mailboxes. Stratification and exclusion rules must be recorded before selection. Do not silently substitute it for this sample.

Dataset attribution: ZL Technologies, Inc. (http://www.zlti.com), as stated in the EDRM source footer.