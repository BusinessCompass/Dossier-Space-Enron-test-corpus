# S25 — existing dossier links and lexical retrieval

Exploratory known-answer test on 19 S24 derived records. No held-out test, model calls, embeddings, native-source re-verification, or independent assurance.

| Question | Baseline top 3 | Guided top 3 | Expected found A/B | Context words A/B |
|---|---|---|---|---|
| Q1 | B10, B05, N13 | B05, B10, N01 | 2/2 vs 2/2 | 846/770 |
| Q2 | B10, N01, B05 | B05, N01, B10 | 1/1 vs 1/1 | 770/770 |
| Q3 | N08, N02, B05 | N06, N07, N08 | 1/1 vs 1/1 | 853/784 |
| Q4 | B05, N06, N11 | B05, N06, N08 | 1/2 vs 1/2 | 981/1021 |
| Q5 | N04, N15 | N15, N04 | Not answerable; not scored | 258/258 |

## Interpretation boundaries
The questions were authored after inspecting S24 annotations. Existing links were frozen and no result tuning was performed. Expected sets are minimum controls, not exhaustive relevance judgments. Equal top-three counts do not imply equal token budgets. Whole-record context is retained in both arms; this does not reproduce S22 chunk retrieval. Relationship edges were not traversed. No causal or general performance inference is justified. Q5 can return relevant-looking documents without establishing a confirmed date; abstention requires evidence interpretation.

## Provenance
Source archive/member/native hash references remain in the existing S24 source-manifest.csv. Input hashes and all rankings are preserved here. No existing inputs were moved or rewritten. All 33 existing quotations matched their derived texts and input hashes were unchanged.

## Observed outcome
Both arms retrieved 5 of 6 expected record references across four answerable questions. This is pooled control coverage, not corpus recall. Q3 moved N08 from first to third under guidance; Q4 missed N07 in both top-three sets. Q1 substituted a more thematically related third candidate, but no extra expected evidence was found. Q5 ranked a forecast and training notice; neither establishes a confirmed bankruptcy date. The tested concept-label matching and equal-weight rank fusion provide no demonstrated coverage benefit on these controls. This does not rule out better concept resolution, explicit relationship traversal or a held-out test.
