# ROMER — Session 18 Final

Session: `DS-20260902-S18`  
Closed: `2026-09-02T15:04:16.8089389+02:00`  
Decision: **Completed — accepted with limitations**

The original Kingston drive, serial `50026B7683336CE4`, was baselined before migration and is retained as `Z:`. The replacement P3-1TB SSD, serial `9Y60803411111`, was initialized as GPT/NTFS, populated, verified, and cut over to `D:`.

The pre-cutover comparison matched all 314 copied files and all 164 accessible `Zone.Identifier` streams. The final seal reported zero copied files, mismatches, failures, or extras. After cutover, the active `D:` corpus was rehashed against the accepted Session 16 baseline: 164 of 164 files matched, totaling 79,087,637,104 bytes, with no missing files, hash mismatches, or size mismatches.

Security-metadata transfer was constrained by unavailable backup, restore, and auditing privileges. The successful transfer preserved data, attributes, and timestamps. The restrictive raw-corpus access policy was then reapplied and checked, with no non-administrative write-capable allow rules found.

Protected Windows locations were inaccessible, SACL rules were not copied, some general ownership/DACL identities differ, and BitLocker status could not be established. These limitations constrain any claim of complete device-level identity but do not alter the content-hash result.

The active corpus on `D:` is accepted for use. The original `Z:` is retained unchanged for rollback and evidential comparison until separately authorized disposition. Assurance is a primary-agent review of preserved records, not an independent review.
