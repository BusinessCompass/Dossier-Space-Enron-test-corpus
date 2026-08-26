# Transcript — Session 14 — 2026-08-26 — Analysis — Farmer/Moorer

**Stage:** Analysis  
**Primer:** `CIPDA-Analysis-v1.0.md` (approved; re-read in full)  
**Template:** `ROMER-Finding-v1.0.md`  
**Authority:** Operator expressly authorized rerunning the previous F-001 smoke-test analysis and comparing it with the new results.  
**Custodians:** Daren Farmer (`farmer-d`); Torrey Moorer (referenced party; no mailbox in corpus)  
**Proposition:** Same as F-001: identify a message referring to a call, meeting, or other communication for which no independent contemporaneous record exists.  
**Target:** `maildir/farmer-d/all_documents/1914..eml` and its two folder copies.  
**Corroboration window:** 1–15 May 2000 (±7 calendar days around 8 May).  
**Session start:** `2026-08-26T15:24:18Z`
**Finding produced:** `findings/F-002-farmer-moorer-session-14-independent-rerun.md`

---

## R — Reasoning

The purpose was reproducibility, not discovery of the 26 routine Farmer-only candidates. The same target, proposition, search vocabulary, date window, and available mailbox scope were retained. Numerical and methodological differences were compared explicitly with the original F-001 analysis and the Session 10 custody-server smoke test.

## O — Observations

1. The three target files are unchanged by SHA-256 from Session 10.
2. The target body and headers are unchanged. It remains a plain-text message from Torrey Moorer to Daren Farmer dated 8 May 2000, subject `Failed Deals`, referring to a phone conversation, fax, electronic copy, six trades, and SITARA booking.
3. The attachment described in the body is still absent from the corpus copy.
4. No `moorer-t`, `denny-j`, or `frayre-i` mailbox exists at the corpus top level; `manifest.txt` contains no occurrence of `moorer`.

## M — Methods and access log

All corpus operations were read-only local filesystem searches. The `dossier-custody` MCP tools used in Session 10 were not exposed in Session 14. This is a logged methodological deviation: local `rg`, PowerShell header parsing, `Get-Content`, and `Get-FileHash` replaced custody-server calls. The standalone Session 10 custody log contains only server startup information, so Session 14 does not claim continuity of custody logging.

| # | Search/read | Scope | Result |
|---|---|---|---|
| 1 | SHA-256 and full read of target; SHA-256 of two copies | Three F-001 files | Hashes exactly match Session 10; content unchanged |
| 2 | Approved seven-variant alternation, case-insensitive | `maildir` | 2,119 files |
| 3 | Same alternation | `maildir/farmer-d` | 85 files; 27 unique Date+From+To+Subject signatures |
| 4 | `as per our phone conversation` | `maildir` | 38 files; 3 in Farmer, all three F-001 copies |
| 5 | Farmer Date headers, 1–15 May 2000 | all `farmer-d` folders | 208 files |
| 6 | `moorer|fax|failed deal|SITARA|six trades` in those 208 files | `farmer-d`, 1–15 May | 40 raw files; 12 unique header signatures |
| 7 | Specific terms in window | `farmer-d`, 1–15 May | `moorer` 3; `torrey.moorer` 3; `fax` 3; `failed deal` 3; `six trades` 3; each is the same three F-001 copies. `SITARA` 40, including unrelated system references |
| 8 | `six trades` | entire `farmer-d` mailbox | 3 files, all F-001 copies |
| 9 | `torrey.moorer` | entire `farmer-d` mailbox | 71 files; only 3 in the window, all F-001 copies |
| 10 | target Message-ID token `27199744` | entire `farmer-d` mailbox | 1 file; no reply/reference located |
| 11 | Session 10 query semantics: Date header contains `May 2000` | `farmer-d` | 591 May files; `moorer` 12, `fax` 16, `sitara` 97; all reproduce Session 10 counts |
| 12 | `failed deal`, `six trades`, `27199744` | `farmer-d`, all dates | 6, 3, and 1 respectively; reproduce Session 10 |
| 13 | literal `Moorer` | corpus-wide | 2,325 files |
| 14 | top-level mailbox folders / `moorer` in manifest | corpus root / `manifest.txt` | Local filesystem shows 151 top-level directories; none named Moorer, Denny, or Frayre; manifest has 0 `moorer` hits |

Approved variants were also counted separately:

| Variant | Corpus | Farmer |
|---|---:|---:|
| `as per our phone conversation` | 38 | 3 |
| `per our phone conversation` | 212 | 13 |
| `as we discussed on the phone` | 94 | 0 |
| `per our conversation` | 1,535 | 69 |
| `as per our discussion` | 234 | 3 |
| `further to our call` | 4 | 0 |
| `following our meeting` | 44 | 0 |

## E — Evidence and comparison

Target integrity anchors:

| File | SHA-256 |
|---|---|
| `farmer-d/all_documents/1914..eml` | `ba1497804fd68e5007e2f8ba7aadef0c325ad5c915588073f17018a98fb52df9` |
| `farmer-d/discussion_threads/1096..eml` | `761959523634df909bd402daf2e5025dd1eaac11fed8b17d5868c4b5a0233dbd` |
| `farmer-d/logistics/1093..eml` | `e73a94a7e0149585348443d8ad3675c98f7a27f2c49e1f0c647561c1a3365416` |

Reproduced results:

- 2,119 corpus-wide variant hits, 85 Farmer hits, and 27 Farmer signatures.
- 208 Farmer files in the ±7-day window.
- Three `six trades` files and one target Message-ID hit.
- Session 10 counts of 12 (`moorer` + May 2000), 16 (`fax` + May 2000), 97 (`sitara` + May 2000), and 6 (`failed deal`, all dates).
- No independent record of the F-001 call, fax, six trades, attachment, reply, or booking confirmation.

Corrections/divergences:

- F-001's statement that the target was the only literal corpus-wide seed-phrase match is incorrect. Session 14 finds 38 files. The defensible narrower statement is that the three Farmer literal hits are the three copies of F-001, and F-001 is the sole relevant Farmer/Moorer underlying message among them.
- The earlier corpus-wide `Moorer` count of 16 does not reproduce. Session 14 finds 2,325 files. The earlier value likely reflected incomplete/truncated search reporting, but cause is not established.
- The combined date-window term sweep yields 40 raw files rather than 39, and 12 unique header signatures. This numerical discrepancy does not add a relevant corroborating message.
- Session 14 sees 151 top-level corpus directories rather than the earlier reported 150. No in-scope mailbox appears; the count difference remains unexplained and should not be treated as resolved.

## R — Results

**Classification:** No independent contemporaneous record found. Recorded independently as F-002; F-001 remains historically unchanged.

The substantive result reproduces. Within the 1–15 May 2000 window, every specific event term (`moorer`, `torrey.moorer`, `fax`, `failed deal`, `six trades`) resolves only to the same three folder copies of the target message. No reply references its Message-ID. The phone-call content, fax, attachment, six-trade details, and booking outcome remain uncorroborated in the searched Farmer mailbox. Moorer, Denny, and Frayre have no admitted mailboxes, structurally limiting corroboration.

**Confidence:** High that no independent record exists within the searched Farmer mailbox and window; no confidence about the off-corpus call or fax contents. Confidence in some prior global count/completeness statements is reduced because Session 14 disproves the earlier literal-phrase and corpus-wide Moorer counts.

## A — Assure

- Claims are tied to paths, hashes, headers, search strings, scopes, and counts.
- Absence is limited to the searched corpus and is not treated as evidence about conduct or intent.
- The missing-mailbox gap is restated.
- Tool substitution and all observed numerical divergences are explicit.
- Scope remained on F-001; the 26 routine candidates were not analyzed.

---
*— end of Session 14 transcript —*
