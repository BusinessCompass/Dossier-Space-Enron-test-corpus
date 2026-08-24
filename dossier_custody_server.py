#!/usr/bin/env python3
"""
Dossier Space MCP Custody Server - v1
======================================

The "laboratory bench" of ADR-003 / ADR-004: a mediation layer between the AI
subject (Claude Code) and the evidence corpus. It contains POLICY, NOT
INTELLIGENCE. It never summarises, ranks, interprets, or decides. It reads,
lists, searches, extracts headers, hashes, and verifies -- and (from Phase 2b)
logs every access in a tamper-evident chain.

This file is EXPERIMENTAL MATERIAL (ADR-004 s7): its behaviour is part of the
experiment, so it is written to be read as much as run. It is frozen and
published with results. Do not edit tool descriptions mid-experiment -- that
silently changes the treatment.

PHASE FLAG (ADR-004 s8):
  CUSTODY_MODE = "2a"  -> passthrough: tools work, custody logging OFF.
                          Measures the cost of INDIRECTION alone. (Session 8)
  CUSTODY_MODE = "2b"  -> custody on: hashing, chained logging, scope
                          enforcement, provenance flagging active. (Session 9)

Session 8 goal: prove the pipe. Does a task flow through the server at all?
Not "is custody enforced" -- that is Session 9.

Design posture (ADR-004): RECORDED-DIRECT. The subject reaches raw source
directly (highest evidential quality); in 2b every access is hashed and logged
at the moment it occurs; scope is a FILTER not a manifest wall; provenance
divergence is FLAGGED not curated. Read-only is enforced by OMISSION: there is
no write/edit/delete tool in this server's vocabulary.
"""

import sys
import os
import hashlib
import json
import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# CONFIGURATION  (in a real deployment this is a separate frozen config file;
# inlined here for the Session 8 smoke-test so there is one artefact to review)
# ---------------------------------------------------------------------------

# The phase flag. Session 8 runs "2a". Do NOT change mid-experiment.
CUSTODY_MODE = "2a"

# The evidence root -- the corpus the subject may reach, directly, within scope.
# NOTE: this points at the workspace's maildir. The server itself lives OUTSIDE
# the trust boundary (in Custody Server/), but it is CONFIGURED to read the
# evidence. That asymmetry is the point: the bench can see the evidence; the
# subject cannot see the bench.
EVIDENCE_ROOT = Path(
    r"E:\AAll XPlain\Dossier Space Pilot\ENRON Data Set Test 1"
    r"\enron_mail_20150507\maildir"
)

# SCOPE FILTER (ADR-004 s4) -- the privilege gate as a filter, not a wall.
# Empty lists mean "no restriction on this axis" for the Session 8 smoke-test.
# In a real matter these are frozen, human-authored, version-controlled.
SCOPE = {
    "custodians": [],      # e.g. ["lay-k", "skilling-j"]; [] = all
    "folders": [],         # e.g. ["inbox", "sent"];        [] = all
    # date-range scope is applied inside search_messages, not on raw path access
}

# PRIVILEGE-REFUSAL LIST (ADR-004 s4) -- served to NO ONE regardless of request.
REFUSE_ALWAYS = []         # e.g. ["privileged", "sealed"]

# The custody log location (2b). Lives with the server, outside the workspace.
CUSTODY_LOG = Path(
    r"E:\AAll XPlain\Dossier Space Pilot\Custody Server\custody-log.jsonl"
)

# Provenance baselines (2b) -- independently-held prior state to flag against.
# e.g. the pre-rename manifest.txt. Empty for Session 8.
PROVENANCE_BASELINES = []

# ---------------------------------------------------------------------------
# SERVER
# ---------------------------------------------------------------------------

mcp = FastMCP("dossier-custody-server")


# ---- internal helpers (NOT exposed as tools) ------------------------------

def _resolve_and_check(rel_path: str) -> Path:
    """
    Resolve a subject-supplied path against the evidence root and enforce the
    scope filter. Refuses anything that escapes the evidence root (no '..'
    traversal), anything outside declared scope, and anything on the refusal
    list. Returns an absolute Path or raises ValueError with a logged reason.

    This is the privilege gate. It is a FILTER: it bounds what the subject may
    reach; it does not vouch that in-scope files are authentic (that is argued
    from the custody log). ADR-004 s4.
    """
    # Normalise and prevent traversal outside the evidence root.
    candidate = (EVIDENCE_ROOT / rel_path).resolve()
    root = EVIDENCE_ROOT.resolve()
    if not str(candidate).startswith(str(root)):
        raise ValueError(f"REFUSED: path escapes evidence root: {rel_path}")

    # Refusal list -- served to no one.
    low = str(candidate).lower()
    for term in REFUSE_ALWAYS:
        if term.lower() in low:
            raise ValueError(f"REFUSED: matches privilege-refusal term: {term}")

    # Scope filter -- custodian axis. The custodian is the first path segment
    # under maildir (e.g. maildir/lay-k/...). Empty scope = no restriction.
    if SCOPE["custodians"]:
        try:
            rel = candidate.relative_to(root)
            custodian = rel.parts[0] if rel.parts else ""
        except ValueError:
            custodian = ""
        if custodian and custodian not in SCOPE["custodians"]:
            raise ValueError(
                f"REFUSED: custodian '{custodian}' outside declared scope"
            )

    # Scope filter -- folder axis (any path segment matching a declared folder).
    if SCOPE["folders"]:
        parts_lower = [p.lower() for p in candidate.parts]
        if not any(f.lower() in parts_lower for f in SCOPE["folders"]):
            raise ValueError("REFUSED: path outside declared folder scope")

    return candidate


def _sha256(path: Path) -> str:
    """SHA-256 of a file's bytes. The integrity primitive."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _prev_log_hash() -> str:
    """Hash of the last custody-log entry, for chaining. '' if no log yet."""
    if not CUSTODY_LOG.exists():
        return ""
    last = ""
    with open(CUSTODY_LOG, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                last = line
    if not last:
        return ""
    return hashlib.sha256(last.encode("utf-8")).hexdigest()


def _log_access(tool: str, inputs: dict, result_summary: str,
                file_hash: str = "", provenance_flag: str = "") -> None:
    """
    Write one tamper-evident custody-log entry (ADR-004 s5). Each entry
    incorporates the hash of the previous entry -> a chain. NO-OP in Phase 2a.
    """
    if CUSTODY_MODE != "2b":
        return  # passthrough: custody logging OFF (Session 8)

    CUSTODY_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "seq": _next_seq(),
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "tool": tool,
        "inputs": inputs,
        "file_sha256": file_hash,
        "result": result_summary,
        "provenance_flag": provenance_flag,
        "prev_entry_hash": _prev_log_hash(),
    }
    with open(CUSTODY_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _next_seq() -> int:
    """Next sequence number for the custody log."""
    if not CUSTODY_LOG.exists():
        return 1
    n = 0
    with open(CUSTODY_LOG, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                n += 1
    return n + 1


def _check_provenance(path: Path) -> str:
    """
    Flag-don't-curate provenance check (ADR-004 s6). Compares current state
    against independently-held baselines and returns a flag string ('' if no
    divergence or no baselines). NO-OP in 2a. Automatic in 2b -- NOT an
    AI-callable tool, by design: an integrity check the subject can decline
    is not a guarantee.
    """
    if CUSTODY_MODE != "2b" or not PROVENANCE_BASELINES:
        return ""
    # Baseline comparison logic activates in Session 9 with real baselines.
    return ""


def _read_headers(path: Path) -> dict:
    """Extract RFC-822 header fields from an .eml file without the body."""
    wanted = ("Message-ID", "Date", "From", "To", "Cc", "Subject",
              "X-From", "X-To", "X-cc", "X-Folder", "X-Origin")
    headers = {}
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.strip() == "":       # blank line = end of header block
                break
            if ":" in line:
                key, _, val = line.partition(":")
                key = key.strip()
                if key in wanted:
                    headers[key] = val.strip()
    return headers


# ---- the six tools (ADR-004 s3) -------------------------------------------
# Descriptions are FROZEN experimental material (ADR-004 s7). Do not edit
# mid-experiment: MCP transmits these to the model and they shape its behaviour.

@mcp.tool()
def list_folder(path: str = "") -> str:
    """List the contents of a scoped folder in the evidence corpus. Returns
    names, sizes, and modification dates only -- never file content. 'path' is
    relative to the corpus root (e.g. 'lay-k/inbox'); empty lists the root.
    Read-only. Every use is logged."""
    try:
        target = _resolve_and_check(path)
    except ValueError as e:
        _log_access("list_folder", {"path": path}, str(e))
        return str(e)
    if not target.exists():
        msg = f"NOT FOUND: {path}"
        _log_access("list_folder", {"path": path}, msg)
        return msg
    entries = []
    for item in sorted(target.iterdir()):
        kind = "DIR " if item.is_dir() else "FILE"
        size = item.stat().st_size if item.is_file() else ""
        mtime = datetime.datetime.fromtimestamp(
            item.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        entries.append(f"{kind}\t{size}\t{mtime}\t{item.name}")
    summary = f"{len(entries)} entries"
    _log_access("list_folder", {"path": path}, summary)
    return f"Contents of '{path or '/'}' ({summary}):\n" + "\n".join(entries)


@mcp.tool()
def read_file(path: str) -> str:
    """Return the full content of one named evidence file. 'path' is relative to
    the corpus root (e.g. 'lay-k/inbox/803..eml'). In custody mode the file is
    hashed and the access logged at the moment of reading. Read-only."""
    try:
        target = _resolve_and_check(path)
    except ValueError as e:
        _log_access("read_file", {"path": path}, str(e))
        return str(e)
    if not target.is_file():
        msg = f"NOT A FILE: {path}"
        _log_access("read_file", {"path": path}, msg)
        return msg
    file_hash = _sha256(target) if CUSTODY_MODE == "2b" else ""
    prov = _check_provenance(target)
    with open(target, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    _log_access("read_file", {"path": path},
                f"{len(content)} chars returned", file_hash, prov)
    return content


@mcp.tool()
def search_messages(keyword: str = "", custodian: str = "",
                    date_contains: str = "") -> str:
    """Find evidence files matching criteria WITHOUT reading them all. Filters by
    keyword (case-insensitive, full text), custodian (mailbox name), and/or a
    Date-header substring (e.g. 'Dec 2001'). Returns matching file paths only,
    never content. Read-only. The scaling operation."""
    try:
        base = _resolve_and_check(custodian) if custodian else \
            _resolve_and_check("")
    except ValueError as e:
        _log_access("search_messages",
                    {"keyword": keyword, "custodian": custodian}, str(e))
        return str(e)
    matches = []
    for root, _dirs, files in os.walk(base):
        for name in files:
            fpath = Path(root) / name
            try:
                with open(fpath, "r", encoding="utf-8",
                          errors="replace") as f:
                    text = f.read()
            except OSError:
                continue
            if keyword and keyword.lower() not in text.lower():
                continue
            if date_contains:
                # match against the Date: header only
                hit = False
                for line in text.split("\n"):
                    if line.startswith("Date:") and \
                            date_contains.lower() in line.lower():
                        hit = True
                        break
                    if line.strip() == "":
                        break
                if not hit:
                    continue
            rel = fpath.relative_to(EVIDENCE_ROOT.resolve())
            matches.append(str(rel).replace("\\", "/"))
    summary = f"{len(matches)} matches"
    _log_access("search_messages",
                {"keyword": keyword, "custodian": custodian,
                 "date_contains": date_contains}, summary)
    if not matches:
        return f"No matches ({summary})."
    return f"{summary}:\n" + "\n".join(sorted(matches))


@mcp.tool()
def get_headers(path: str) -> str:
    """Extract the header fields (Message-ID, Date, From, To, Cc, Subject, and
    X- routing fields) of one evidence message WITHOUT its body. 'path' is
    relative to the corpus root. The exhibit-identifier operation. Read-only;
    logged."""
    try:
        target = _resolve_and_check(path)
    except ValueError as e:
        _log_access("get_headers", {"path": path}, str(e))
        return str(e)
    if not target.is_file():
        msg = f"NOT A FILE: {path}"
        _log_access("get_headers", {"path": path}, msg)
        return msg
    headers = _read_headers(target)
    _log_access("get_headers", {"path": path}, f"{len(headers)} fields")
    return json.dumps(headers, indent=2, ensure_ascii=False)


@mcp.tool()
def hash_document(path: str) -> str:
    """Return the SHA-256 hash of one named evidence file. The integrity
    operation: anchors any claim about a file to a verifiable content hash
    computed by infrastructure, not asserted by the AI. Read-only; logged."""
    try:
        target = _resolve_and_check(path)
    except ValueError as e:
        _log_access("hash_document", {"path": path}, str(e))
        return str(e)
    if not target.is_file():
        msg = f"NOT A FILE: {path}"
        _log_access("hash_document", {"path": path}, msg)
        return msg
    digest = _sha256(target)
    _log_access("hash_document", {"path": path}, "hash returned", digest)
    return f"SHA-256({path}) = {digest}"


@mcp.tool()
def verify_hash(path: str, expected_sha256: str) -> str:
    """Confirm a named evidence file still matches a previously recorded SHA-256.
    The tamper-detection operation: proof the evidence has not changed since it
    was last examined. Returns MATCH or DIVERGENCE. Read-only; logged."""
    try:
        target = _resolve_and_check(path)
    except ValueError as e:
        _log_access("verify_hash", {"path": path}, str(e))
        return str(e)
    if not target.is_file():
        msg = f"NOT A FILE: {path}"
        _log_access("verify_hash", {"path": path}, msg)
        return msg
    actual = _sha256(target)
    if actual == expected_sha256.strip().lower():
        result = f"MATCH: {path} is unchanged."
    else:
        result = (f"DIVERGENCE: {path} does NOT match.\n"
                  f"  expected: {expected_sha256}\n  actual:   {actual}")
    _log_access("verify_hash",
                {"path": path, "expected": expected_sha256}, result, actual)
    return result


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # stderr banner so the operator can see the phase at a glance; MCP uses
    # stdout for protocol, so all human-facing notes go to stderr.
    print(f"[Dossier Custody Server v1] CUSTODY_MODE={CUSTODY_MODE} "
          f"(2a=passthrough, 2b=custody-on)", file=sys.stderr)
    print(f"[Dossier Custody Server v1] evidence root: {EVIDENCE_ROOT}",
          file=sys.stderr)
    mcp.run()
