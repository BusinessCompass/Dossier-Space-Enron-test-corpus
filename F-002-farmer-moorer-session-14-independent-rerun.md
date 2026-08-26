# F-002 — Farmer/Moorer: Session 14 independent rerun of the 8 May 2000 divergence case

**Stage:** Analysis  
**Primer:** `CIPDA-Analysis-v1.0.md`  
**Custodian(s):** Daren Farmer (`farmer-d`); Torrey Moorer (referenced party, no mailbox in corpus)  
**Candidate message:** `maildir/farmer-d/all_documents/1914..eml`, with folder copies at `maildir/farmer-d/discussion_threads/1096..eml` and `maildir/farmer-d/logistics/1093..eml`  
**Prior finding compared:** `findings/F-001-farmer-moorer-unrecorded-call-8may2000.md`  
**Session transcript:** `transcripts/2026-08-26-analysis-farmer-moorer-session-14.md`  
**Drafted:** 2026-08-26  
**Status:** final

---

## R — Reasoning

- This finding records an independently numbered rerun of F-001 so that the original finding remains historically intact and the new results cannot be confused with the earlier analysis.
- The same proposition, target message, approved phrase variants, ±7-day window, and available-mailbox scope were retained.
- Hypothesis tested: whether the admitted corpus contains an independent contemporaneous record of the phone call, fax, six failed trades, or requested SITARA booking described by Moorer.
- The 26 routine Farmer-only candidates remained outside Session 14 scope.

## O — Observations

**1. Evidence the event occurred**

The target states:

> “As per our phone conversation I sent you a fax, but I also wanted to let you have an electronic copy of the failed deals which need to be booked into SITARA.”

**2. Evidence about its subject**

The communication concerned failed deals that Moorer said needed to be booked into SITARA.

**3. Evidence about its detailed content**

The target adds:

> “Attached is the detail on the six trades in question.”

The corpus copy remains `text/plain` and contains no MIME attachment. It supplies no trade identifiers, counterparties, volumes, or booking results.

The three target files are unchanged from the Session 10 integrity anchors:

| File | SHA-256 |
|---|---|
| `farmer-d/all_documents/1914..eml` | `ba1497804fd68e5007e2f8ba7aadef0c325ad5c915588073f17018a98fb52df9` |
| `farmer-d/discussion_threads/1096..eml` | `761959523634df909bd402daf2e5025dd1eaac11fed8b17d5868c4b5a0233dbd` |
| `farmer-d/logistics/1093..eml` | `e73a94a7e0149585348443d8ad3675c98f7a27f2c49e1f0c647561c1a3365416` |

## M — Methods

**6. Searches performed to locate corroboration**

All operations were read-only. The custody MCP used during the previous smoke test was unavailable in Session 14; local `rg`, PowerShell header parsing, `Get-Content`, and `Get-FileHash` were used instead. This is a tool-path deviation, not a silent scope change.

| # | Search/read | Scope | Date window | Result |
|---|---|---|---|---|
| 1 | Approved seven-variant alternation | `maildir` | none | 2,119 files |
| 2 | Same alternation | `maildir/farmer-d` | none | 85 files; 27 unique Date+From+To+Subject signatures |
| 3 | `as per our phone conversation` | `maildir` | none | 38 files; 3 in Farmer, all F-001/F-002 target copies |
| 4 | Date-header census | all `farmer-d` folders | 1–15 May 2000 | 208 files |
| 5 | `moorer|fax|failed deal|SITARA|six trades` | those 208 files | 1–15 May 2000 | 40 raw files; 12 unique header signatures |
| 6 | `moorer` | `farmer-d` | 1–15 May 2000 | 3 files, all target copies |
| 7 | `torrey.moorer` | `farmer-d` | 1–15 May 2000 | 3 files, all target copies |
| 8 | `fax` | `farmer-d` | 1–15 May 2000 | 3 files, all target copies |
| 9 | `failed deal` | `farmer-d` | 1–15 May 2000 | 3 files, all target copies |
| 10 | `six trades` | `farmer-d` | 1–15 May 2000 | 3 files, all target copies |
| 11 | `SITARA` | `farmer-d` | 1–15 May 2000 | 40 files, including unrelated system references |
| 12 | `six trades` | entire `farmer-d` mailbox | none | 3 files, all target copies |
| 13 | `torrey.moorer` | entire `farmer-d` mailbox | none | 71 files; only the 3 target copies fall within the window |
| 14 | `27199744` | entire `farmer-d` mailbox | none | 1 file; no reply/reference found |
| 15 | `moorer`, Date header containing `May 2000` | `farmer-d` | May 2000 | 12 files, reproducing Session 10 |
| 16 | `fax`, Date header containing `May 2000` | `farmer-d` | May 2000 | 16 files, reproducing Session 10 |
| 17 | `sitara`, Date header containing `May 2000` | `farmer-d` | May 2000 | 97 files, reproducing Session 10 |
| 18 | `failed deal` | `farmer-d` | none | 6 files, reproducing Session 10 |
| 19 | `Moorer` | corpus-wide | none | 2,325 files |
| 20 | mailbox directory check / `moorer` in manifest | corpus root / `manifest.txt` | none | 151 top-level directories locally; no Moorer, Denny, or Frayre mailbox; 0 manifest hits for `moorer` |

## E — Evidence

Full target citation:

- **File:** `maildir/farmer-d/all_documents/1914..eml`
- **Message-ID:** `<27199744.1075854011833.JavaMail.evans@thyme>`
- **Date:** Mon, 8 May 2000 01:42:00 -0700 (PDT)
- **From:** `torrey.moorer@enron.com`
- **To:** `daren.farmer@enron.com`
- **Cc/Bcc:** `jennifer.denny@enron.com`, `imelda.frayre@enron.com`
- **Subject:** `Failed Deals`

**4. Corroborating or conflicting records**

None found. Within the 1–15 May window, every specific event-term hit resolves to the same three folder copies of the target. No reply references the target Message-ID.

**5. Missing expected artefacts**

- The referenced fax.
- The referenced electronic attachment detailing six trades.
- Any Farmer reply or acknowledgement.
- Any independent identification of the six trades.
- Any SITARA booking confirmation tied to those trades.
- Records from Moorer, Denny, or Frayre mailboxes, which are structurally unavailable in this corpus.

**Comparison with F-001 and the prior smoke test**

Reproduced:

- Target content and all three SHA-256 hashes.
- 2,119 corpus-wide variant hits, 85 Farmer hits, and 27 Farmer signatures.
- 208 Farmer files in the ±7-day window.
- Session 10 counts of 12 (`moorer` + May 2000), 16 (`fax` + May 2000), 97 (`sitara` + May 2000), 6 (`failed deal`, all dates), 3 (`six trades`), and 1 target Message-ID hit.
- The absence of an independent contemporaneous record.

Not reproduced:

- The earlier claim that F-001 was the only literal corpus-wide seed-phrase match. Session 14 finds 38 files. The narrower supportable statement is that the three Farmer literal hits are the three target copies.
- The earlier corpus-wide `Moorer` count of 16. Session 14 finds 2,325 files. The cause of the earlier undercount is not established.
- The earlier combined date-window count of 39 raw files. Session 14 finds 40 raw files and 12 unique header signatures; none adds corroboration.
- The earlier top-level count of 150 directories. Session 14 locally sees 151; none is an in-scope missing mailbox. The discrepancy remains unresolved.

## R — Results

**7. Resulting hanging thread**

F-002 independently classifies the case as **no independent contemporaneous record found (hanging thread)**. The call’s detailed content, fax, attachment, identities of the six trades, and booking outcome remain supported only by the target email, repeated through folder mirroring rather than independent evidence.

- **Confidence:** High that no independent record exists within the searched Farmer mailbox and 1–15 May window; no confidence about the contents of the off-corpus call or fax. Confidence in F-001’s global count descriptions is reduced by the Session 14 discrepancies.
- **Open questions:** The six trades and booking outcome could potentially be resolved only through records outside the searched corpus or through later correspondence using vocabulary not tied to this event.
- **Corpus-gap note:** Moorer, Denny, and Frayre have no admitted mailboxes. Their absence limits the available corroboration and is not evidence about the underlying event.

---
*— end of F-002 —*
