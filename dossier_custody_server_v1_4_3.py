#!/usr/bin/env python3
"""
Dossier Space MCP Custody Server v1.4.3
Persistent MCP Service for Evidence Operations with Full JSON-RPC Protocol

Session: DS-202608xx-S12+ (Intermediate build)
Purpose: Expose custody tools as persistent MCP service with proper protocol layer
Architecture: Claude Code (MCP client) → Custody Server (JSON-RPC MCP server)
             Each tool call independently logged to governance ledger

Version History:
- v1.3: Built without JSON-RPC protocol layer (blocker identified in Session 10)
- v1.4: Complete rebuild with JSON-RPC protocol, FastMCP 1.29.0 compatible
- v1.4.1: Added documentary_gap entry_type for Session 12 gap logging discipline
- v1.4.2: Added emit_documentary_gap() tool (MCP serialization issue with optional fields)
- v1.4.3: Simplified emit_documentary_gap() to required fields only (FastMCP compatibility)

Key Features:
- FastMCP 1.29.0 (pinned for stability)
- Full JSON-RPC protocol handler with proper tool registration
- Stdio transport via stdio_server for Claude Code integration
- Full governance ledger integration
- Fail-closed semantics maintained
- Six read-verify tools: search_messages, list_folder, read_file, get_headers, hash_document, verify_hash

Design Principle: "Watch is never the watched"
- Claude Code requests evidence operations via MCP JSON-RPC
- Custody Server executes and independently records all actions
- Ledger is the canonical truth source
- No direct imports of custody logic into Claude Code
"""

import os
import sys
import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging
import asyncio

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent, CallToolResult
    from mcp import stdio_server
except ImportError:
    print("ERROR: FastMCP 1.29.0 not installed. Install with: pip install mcp==1.29.0")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================

SESSION_ID = "DS-202608xx-S12"
OPERATOR = "Ken Tombs"
DESIGN_LEAD = "Claude"

# Paths
ENRON_CORPUS_ROOT = r"E:\AAll XPlain\Dossier Space Pilot\ENRON Data Set Test 1\enron_mail_20150507\maildir"
GOVERNANCE_LEDGER_DIR = r"E:\AAll XPlain\Dossier Space Pilot\Governance Ledger"
RESULTS_DIR = os.path.join(GOVERNANCE_LEDGER_DIR, "results")
LEDGER_FILE = os.path.join(GOVERNANCE_LEDGER_DIR, "session-ledger.jsonl")
LEDGER_FALLBACK_FILE = os.path.join(GOVERNANCE_LEDGER_DIR, "session-ledger-DEGRADED.jsonl")

# Controlled value enums
ENTRY_TYPES = {
    "session_start", "decision", "tool_call", "mcp_call", "result_set",
    "candidate_set", "candidate_cluster", "operator_intervention", "finding",
    "assurance", "exception", "correction", "documentary_gap", "session_close"
}

SEVERITY_LEVELS = {"critical", "major", "minor", "informational"}
STATUS_VALUES = {"active", "superseded"}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# PATH VALIDATION UTILITY
# ============================================================================

def validate_path_containment(resolved_path: str, corpus_root: str) -> bool:
    """Ensure resolved_path is within corpus_root (prevent directory traversal)."""
    resolved = os.path.normpath(os.path.abspath(resolved_path))
    root = os.path.normpath(os.path.abspath(corpus_root))
    return resolved.startswith(root + os.sep) or resolved == root


# ============================================================================
# LEDGER WRITER WITH FAIL-CLOSED BEHAVIOR
# ============================================================================

class LedgerWriter:
    """Handles all ledger entry creation and persistence with fail-closed semantics."""
    
    def __init__(self, session_id: str, ledger_path: str, fallback_path: str, results_dir: str):
        self.session_id = session_id
        self.ledger_path = ledger_path
        self.fallback_path = fallback_path
        self.results_dir = results_dir
        self.action_counter = 0
        
        # Ensure directories exist
        Path(self.ledger_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.results_dir).mkdir(parents=True, exist_ok=True)
        
        # Recover action counter from existing ledger
        self._recover_action_counter()
    
    def _recover_action_counter(self):
        """Scan existing ledger for highest action number in this session."""
        if not os.path.exists(self.ledger_path):
            self.action_counter = 0
            logger.info(f"No existing ledger found; starting action counter at 0")
            return
        
        max_action_num = 0
        try:
            with open(self.ledger_path, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = json.loads(line)
                    if entry.get('session_id') != self.session_id:
                        continue
                    
                    action_id = entry.get('action_id', '')
                    if f"-A" in action_id:
                        num_str = action_id.split('-A')[-1]
                        try:
                            num = int(num_str)
                            max_action_num = max(max_action_num, num)
                        except ValueError:
                            continue
        
        except Exception as e:
            logger.warning(f"Failed to recover action counter: {e}; starting at 0")
            return
        
        self.action_counter = max_action_num
        logger.info(f"Action counter recovered: highest action was A{self.action_counter:02d}, continuing from A{self.action_counter + 1:02d}")
    
    def next_action_id(self) -> str:
        """Generate next sequential action ID."""
        self.action_counter += 1
        return f"{self.session_id}-A{self.action_counter:02d}"
    
    def _validate_entry(self, entry: Dict[str, Any]):
        """Validate entry structure and controlled values."""
        if not isinstance(entry.get('entry_type'), str) or entry['entry_type'] not in ENTRY_TYPES:
            raise ValueError(f"Invalid entry_type: {entry.get('entry_type')}")
        
        if not isinstance(entry.get('severity'), str) or entry['severity'] not in SEVERITY_LEVELS:
            raise ValueError(f"Invalid severity: {entry.get('severity')}")
        
        if not isinstance(entry.get('status'), str) or entry['status'] not in STATUS_VALUES:
            raise ValueError(f"Invalid status: {entry.get('status')}")
    
    def _write_ledger(self, entry: Dict[str, Any], use_fallback: bool = False) -> bool:
        """Write entry to ledger (primary or fallback)."""
        target_file = self.fallback_path if use_fallback else self.ledger_path
        
        try:
            with open(target_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
            return True
        except Exception as e:
            logger.error(f"Failed to write to {'fallback ' if use_fallback else ''}ledger: {e}")
            return False
    
    def emit_entry(
        self,
        entry_type: str,
        action_id: str,
        task_id: str,
        tool_name: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        result_set: Optional[List[str]] = None,
        result_set_reference: Optional[str] = None,
        result_set_sha256: Optional[str] = None,
        candidate_paths: Optional[List[str]] = None,
        description: str = "",
        decision_rationale: str = "",
        dedup_rule: Optional[str] = None,
        linked_action_ids: Optional[List[str]] = None,
        tool_output: Optional[Dict[str, Any]] = None,
        material_decision: bool = False,
        severity: str = "informational",
        reconciliation_notes: str = "",
        status: str = "active"
    ) -> Dict[str, Any]:
        """Emit a ledger entry with fail-closed semantics."""
        
        ledger_entry_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        entry = {
            "ledger_entry_id": ledger_entry_id,
            "session_id": self.session_id,
            "task_id": task_id,
            "action_id": action_id,
            "entry_type": entry_type,
            "timestamp": timestamp,
            "operator": OPERATOR,
            "description": description,
            "material_decision": material_decision,
            "severity": severity,
            "payload": {
                "tool_name": tool_name,
                "parameters": parameters or {},
                "result_set_count": len(result_set) if result_set is not None else None,
                "result_set_reference": result_set_reference,
                "result_set_sha256": result_set_sha256,
                "candidate_paths": candidate_paths or [],
                "dedup_rule": dedup_rule,
                "decision_rationale": decision_rationale,
                "linked_action_ids": linked_action_ids or [],
                "tool_output": tool_output or {}
            },
            "status": status,
            "superseded_by": None,
            "reconciliation_notes": reconciliation_notes
        }
        
        # Validate before writing
        try:
            self._validate_entry(entry)
        except ValueError as e:
            logger.error(f"Entry validation failed: {e}")
            raise
        
        # Attempt primary write
        if self._write_ledger(entry, use_fallback=False):
            logger.info(f"{action_id}: Ledger entry emitted (primary)")
            return entry
        
        # Fallback write
        logger.warning(f"{action_id}: Primary ledger write failed; attempting fallback")
        if self._write_ledger(entry, use_fallback=True):
            logger.info(f"{action_id}: Ledger entry emitted (fallback)")
            return entry
        
        # Both failed: fail-closed
        logger.critical(f"{action_id}: Both primary and fallback ledger writes failed. FAIL-CLOSED.")
        raise RuntimeError("Ledger write failed (both primary and fallback)")
    
    def persist_result_set(self, action_id: str, result_set: List[str], format: str = "txt") -> tuple:
        """
        Persist result set to disk with SHA256 hash.
        Returns (file_reference, sha256_hash)
        """
        filename = f"{action_id}_result_set.{format}"
        filepath = os.path.join(self.results_dir, filename)
        
        # Exclusive create (fail if exists)
        try:
            with open(filepath, 'x', encoding='utf-8') as f:
                for item in result_set:
                    f.write(item + '\n')
        except FileExistsError:
            logger.warning(f"Result file already exists: {filepath}")
            return filepath, None
        except Exception as e:
            logger.error(f"Failed to persist result set: {e}")
            return None, None
        
        # Compute SHA256
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
        except Exception as e:
            logger.error(f"Failed to hash result file: {e}")
            return filepath, None
        
        return filepath, sha256_hash.hexdigest()


# ============================================================================
# CUSTODY SERVER (Evidence Operations)
# ============================================================================

class CustodyServer:
    """Provides access to evidence corpus with full governance logging."""
    
    def __init__(self, corpus_root: str, ledger: LedgerWriter, task_id: str):
        self.corpus_root = corpus_root
        self.ledger = ledger
        self.task_id = task_id
        logger.info(f"CustodyServer initialized: corpus_root={corpus_root}, task_id={task_id}")
    
    def _compute_document_hash(self, filepath: str) -> Optional[str]:
        """Private hash computation (no ledger entry)."""
        full_filepath = os.path.join(self.corpus_root, filepath)
        resolved_path = os.path.normpath(os.path.abspath(full_filepath))
        
        if not validate_path_containment(resolved_path, self.corpus_root):
            return None
        
        sha256_hash = hashlib.sha256()
        try:
            with open(resolved_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash {resolved_path}: {e}")
            return None
    
    def search_messages(self, custodian: str, keyword: str, date_contains: Optional[str] = None) -> Dict[str, Any]:
        """Search for messages by custodian and keyword."""
        
        action_id = self.ledger.next_action_id()
        parameters = {
            "custodian": custodian,
            "keyword": keyword,
            "date_contains": date_contains
        }
        
        # Validate custodian path
        custodian_path = os.path.join(self.corpus_root, custodian)
        resolved_path = os.path.normpath(os.path.abspath(custodian_path))
        
        if not validate_path_containment(resolved_path, self.corpus_root):
            self.ledger.emit_entry(
                entry_type="exception",
                action_id=action_id,
                task_id=self.task_id,
                tool_name="search_messages",
                parameters=parameters,
                description=f"Path containment violation: {custodian}",
                material_decision=True,
                severity="critical"
            )
            return {"results": [], "count": 0, "error": "Path containment violation", "action_id": action_id}
        
        if not os.path.isdir(resolved_path):
            self.ledger.emit_entry(
                entry_type="exception",
                action_id=action_id,
                task_id=self.task_id,
                tool_name="search_messages",
                parameters=parameters,
                description=f"Custodian path not found: {custodian}",
                material_decision=False,
                severity="major"
            )
            return {"results": [], "count": 0, "error": "Custodian path not found", "action_id": action_id}
        
        results = []
        try:
            for root, dirs, files in os.walk(resolved_path):
                for file in files:
                    if file.endswith('.eml'):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().lower()
                                if keyword.lower() in content:
                                    if date_contains is None or date_contains in content:
                                        rel_path = os.path.relpath(filepath, self.corpus_root)
                                        results.append(rel_path)
                        except Exception as e:
                            logger.warning(f"Failed to read {filepath}: {e}")
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
            self.ledger.emit_entry(
                entry_type="exception",
                action_id=action_id,
                task_id=self.task_id,
                tool_name="search_messages",
                parameters=parameters,
                description=f"Search failed: {e}",
                material_decision=False,
                severity="critical"
            )
            return {"results": [], "count": 0, "error": str(e), "action_id": action_id}
        
        result_set_reference, result_set_sha256 = self.ledger.persist_result_set(action_id, results, format="txt")
        
        self.ledger.emit_entry(
            entry_type="mcp_call",
            action_id=action_id,
            task_id=self.task_id,
            tool_name="search_messages",
            parameters=parameters,
            result_set=results,
            result_set_reference=result_set_reference,
            result_set_sha256=result_set_sha256,
            candidate_paths=results,
            description=f"Searched for '{keyword}' in custodian '{custodian}' (date_contains={date_contains})",
            material_decision=False,
            severity="informational"
        )
        
        return {"results": results, "count": len(results), "action_id": action_id}
    
    def list_folder(self, custodian: str) -> Dict[str, Any]:
        """List all EML files for a custodian."""
        
        action_id = self.ledger.next_action_id()
        parameters = {"custodian": custodian}
        results = []
        
        custodian_path = os.path.join(self.corpus_root, custodian)
        resolved_path = os.path.normpath(os.path.abspath(custodian_path))
        
        if not validate_path_containment(resolved_path, self.corpus_root):
            self.ledger.emit_entry(
                entry_type="exception",
                action_id=action_id,
                task_id=self.task_id,
                tool_name="list_folder",
                parameters=parameters,
                description=f"Path containment violation: {custodian}",
                material_decision=True,
                severity="critical"
            )
            return {"files": [], "error": "Path containment violation", "action_id": action_id}
        
        if not os.path.isdir(resolved_path):
            self.ledger.emit_entry(
                entry_type="exception",
                action_id=action_id,
                task_id=self.task_id,
                tool_name="list_folder",
                parameters=parameters,
                description=f"Custodian path not found: {custodian}",
                material_decision=False,
                severity="major"
            )
            return {"files": [], "error": "Custodian path not found", "action_id": action_id}
        
        try:
            for root, dirs, files in os.walk(resolved_path):
                for file in files:
                    if file.endswith('.eml'):
                        filepath = os.path.join(root, file)
                        rel_path = os.path.relpath(filepath, self.corpus_root)
                        results.append(rel_path)
        
        except Exception as e:
            logger.error(f"Failed to list folder: {e}")
            self.ledger.emit_entry(
                entry_type="exception",
                action_id=action_id,
                task_id=self.task_id,
                tool_name="list_folder",
                parameters=parameters,
                description=f"Folder listing failed: {e}",
                material_decision=False,
                severity="critical"
            )
            return {"files": [], "error": str(e), "action_id": action_id}
        
        result_set_reference, result_set_sha256 = self.ledger.persist_result_set(action_id, results, format="txt")
        
        self.ledger.emit_entry(
            entry_type="mcp_call",
            action_id=action_id,
            task_id=self.task_id,
            tool_name="list_folder",
            parameters=parameters,
            result_set=results,
            result_set_reference=result_set_reference,
            result_set_sha256=result_set_sha256,
            candidate_paths=results,
            description=f"Listed all EML files for custodian '{custodian}'",
            material_decision=False,
            severity="informational"
        )
        
        return {"files": results, "count": len(results), "action_id": action_id}
    
    def read_file(self, filepath: str) -> Dict[str, Any]:
        """Read content of an EML file."""
        
        action_id = self.ledger.next_action_id()
        parameters = {"filepath": filepath}
        
        full_filepath = os.path.join(self.corpus_root, filepath)
        resolved_path = os.path.normpath(os.path.abspath(full_filepath))
        
        if not validate_path_containment(resolved_path, self.corpus_root):
            self.ledger.emit_entry(
                entry_type="exception",
                action_id=action_id,
                task_id=self.task_id,
                tool_name="read_file",
                parameters=parameters,
                description=f"Path containment violation: {filepath}",
                material_decision=True,
                severity="critical"
            )
            return {"content": None, "error": "Path containment violation", "action_id": action_id}
        
        if not os.path.isfile(resolved_path):
            self.ledger.emit_entry(
                entry_type="exception",
                action_id=action_id,
                task_id=self.task_id,
                tool_name="read_file",
                parameters=parameters,
                description=f"File not found: {filepath}",
                material_decision=False,
                severity="major"
            )
            return {"content": None, "error": "File not found", "action_id": action_id}
        
        try:
            with open(resolved_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read {filepath}: {e}")
            self.ledger.emit_entry(
                entry_type="exception",
                action_id=action_id,
                task_id=self.task_id,
                tool_name="read_file",
                parameters=parameters,
                description=f"Read failed: {e}",
                material_decision=False,
                severity="major"
            )
            return {"content": None, "error": str(e), "action_id": action_id}
        
        self.ledger.emit_entry(
            entry_type="tool_call",
            action_id=action_id,
            task_id=self.task_id,
            tool_name="read_file",
            parameters=parameters,
            description=f"Read file: {filepath} ({len(content)} bytes)",
            tool_output={"file_size": len(content)},
            material_decision=False,
            severity="informational"
        )
        
        return {"content": content, "action_id": action_id}
    
    def get_headers(self, filepath: str) -> Dict[str, Any]:
        """Extract email headers from an EML file."""
        
        action_id = self.ledger.next_action_id()
        parameters = {"filepath": filepath}
        
        full_filepath = os.path.join(self.corpus_root, filepath)
        resolved_path = os.path.normpath(os.path.abspath(full_filepath))
        
        if not validate_path_containment(resolved_path, self.corpus_root):
            self.ledger.emit_entry(
                entry_type="exception",
                action_id=action_id,
                task_id=self.task_id,
                tool_name="get_headers",
                parameters=parameters,
                description=f"Path containment violation: {filepath}",
                material_decision=True,
                severity="critical"
            )
            return {"headers": {}, "error": "Path containment violation", "action_id": action_id}
        
        if not os.path.isfile(resolved_path):
            self.ledger.emit_entry(
                entry_type="exception",
                action_id=action_id,
                task_id=self.task_id,
                tool_name="get_headers",
                parameters=parameters,
                description=f"File not found: {filepath}",
                material_decision=False,
                severity="major"
            )
            return {"headers": {}, "error": "File not found", "action_id": action_id}
        
        headers = {}
        try:
            with open(resolved_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.rstrip()
                    if not line:  # End of headers
                        break
                    if ': ' in line:
                        key, value = line.split(': ', 1)
                        headers[key] = value
        except Exception as e:
            logger.error(f"Failed to extract headers from {filepath}: {e}")
            self.ledger.emit_entry(
                entry_type="exception",
                action_id=action_id,
                task_id=self.task_id,
                tool_name="get_headers",
                parameters=parameters,
                description=f"Header extraction failed: {e}",
                material_decision=False,
                severity="major"
            )
            return {"headers": {}, "error": str(e), "action_id": action_id}
        
        self.ledger.emit_entry(
            entry_type="tool_call",
            action_id=action_id,
            task_id=self.task_id,
            tool_name="get_headers",
            parameters=parameters,
            description=f"Extracted {len(headers)} headers from {filepath}",
            tool_output={"header_count": len(headers)},
            material_decision=False,
            severity="informational"
        )
        
        return {"headers": headers, "action_id": action_id}
    
    def hash_document(self, filepath: str) -> Dict[str, Any]:
        """Compute SHA256 hash of an EML file."""
        
        action_id = self.ledger.next_action_id()
        parameters = {"filepath": filepath}
        
        file_hash = self._compute_document_hash(filepath)
        
        if not file_hash:
            self.ledger.emit_entry(
                entry_type="exception",
                action_id=action_id,
                task_id=self.task_id,
                tool_name="hash_document",
                parameters=parameters,
                description=f"Hash computation failed: {filepath}",
                material_decision=False,
                severity="major"
            )
            return {"hash": None, "error": "Hash computation failed", "action_id": action_id}
        
        self.ledger.emit_entry(
            entry_type="tool_call",
            action_id=action_id,
            task_id=self.task_id,
            tool_name="hash_document",
            parameters=parameters,
            description=f"Computed SHA256 for {filepath}",
            tool_output={"file_hash": file_hash},
            material_decision=False,
            severity="informational"
        )
        
        return {"hash": file_hash, "action_id": action_id}
    
    def verify_hash(self, filepath: str, expected_hash: str) -> Dict[str, Any]:
        """Verify SHA256 hash of an EML file."""
        
        action_id = self.ledger.next_action_id()
        parameters = {"filepath": filepath, "expected_hash": expected_hash}
        
        actual_hash = self._compute_document_hash(filepath)
        match = actual_hash == expected_hash if actual_hash else False
        
        self.ledger.emit_entry(
            entry_type="tool_call",
            action_id=action_id,
            task_id=self.task_id,
            tool_name="verify_hash",
            parameters=parameters,
            description=f"Hash verification for {filepath}: {'MATCH' if match else 'MISMATCH'}",
            tool_output={"actual_hash": actual_hash, "expected_hash": expected_hash, "match": match},
            material_decision=not match,
            severity="major" if not match else "informational"
        )
        
        return {"match": match, "actual_hash": actual_hash, "action_id": action_id}
    
    def emit_documentary_gap(self, gap_identified: str, reason_identified: str, significance: str, 
                           status: str) -> Dict[str, Any]:
        """Record a documentary gap to the governance ledger.
        
        A documentary gap is an indicated communication, document, or event that 
        cannot presently be located or examined in the corpus.
        
        Args:
            gap_identified: Concise description of what's missing
            reason_identified: Why this gap was identified
            significance: "high", "medium", or "low"
            status: "open" (not found) or "closed" (exhaustively searched, not found)
        
        Returns:
            dict with gap_id, action_id, timestamp, status
        """
        if significance not in ["high", "medium", "low"]:
            raise ValueError(f"Significance must be high/medium/low, got {significance}")
        if status not in ["open", "closed"]:
            raise ValueError(f"Status must be open/closed, got {status}")
        
        action_id = self.ledger.next_action_id()
        
        gap_payload = {
            "gap_identified": gap_identified,
            "reason_identified": reason_identified,
            "significance": significance,
            "status": status
        }
        
        self.ledger.emit_entry(
            entry_type="documentary_gap",
            action_id=action_id,
            task_id=self.task_id,
            description=f"Documentary gap: {gap_identified}",
            material_decision=False,
            severity="informational",
            tool_output=gap_payload
        )
        
        return {
            "gap_id": str(uuid.uuid4()),
            "action_id": action_id,
            "gap_identified": gap_identified,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "recorded",
            "significance": significance
        }


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Initialize and start the custody server."""
    
    logger.info(f"Starting Dossier Space MCP Custody Server v1.4")
    logger.info(f"Session: {SESSION_ID}")
    logger.info(f"Ledger: {LEDGER_FILE}")
    logger.info(f"Corpus Root: {ENRON_CORPUS_ROOT}")
    logger.info(f"Mode: Persistent MCP Service with JSON-RPC Protocol (v1.4 clean rebuild)")
    
    # Initialize ledger writer
    ledger = LedgerWriter(SESSION_ID, LEDGER_FILE, LEDGER_FALLBACK_FILE, RESULTS_DIR)
    
    task_id = "DS-202608xx-S12-T01"
    
    # Emit session_start
    action_id = ledger.next_action_id()
    ledger.emit_entry(
        entry_type="session_start",
        action_id=action_id,
        task_id=task_id,
        description=f"Session {SESSION_ID} initialized: MCP Custody Server v1.4 (clean rebuild with JSON-RPC protocol)",
        material_decision=True,
        severity="critical"
    )
    logger.info(f"Session {SESSION_ID} started")
    
    # Initialize custody server
    custody = CustodyServer(ENRON_CORPUS_ROOT, ledger, task_id)
    
    # Create MCP server
    server = Server("dossier-custody")
    
    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="search_messages",
                description="Search for messages by custodian and keyword",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "custodian": {"type": "string", "description": "Custodian folder name (e.g., 'farmer-d')"},
                        "keyword": {"type": "string", "description": "Keyword to search for"},
                        "date_contains": {"type": "string", "description": "Optional date string to filter results"}
                    },
                    "required": ["custodian", "keyword"]
                }
            ),
            Tool(
                name="list_folder",
                description="List all EML files for a custodian",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "custodian": {"type": "string", "description": "Custodian folder name"}
                    },
                    "required": ["custodian"]
                }
            ),
            Tool(
                name="read_file",
                description="Read the full content of an EML file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "Relative path to EML file"}
                    },
                    "required": ["filepath"]
                }
            ),
            Tool(
                name="get_headers",
                description="Extract email headers from an EML file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "Relative path to EML file"}
                    },
                    "required": ["filepath"]
                }
            ),
            Tool(
                name="hash_document",
                description="Compute SHA256 hash of an EML file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "Relative path to EML file"}
                    },
                    "required": ["filepath"]
                }
            ),
            Tool(
                name="verify_hash",
                description="Verify SHA256 hash of an EML file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "Relative path to EML file"},
                        "expected_hash": {"type": "string", "description": "Expected SHA256 hash (hex)"}
                    },
                    "required": ["filepath", "expected_hash"]
                }
            ),
            Tool(
                name="emit_documentary_gap",
                description="Record a documentary gap (missing communication, document, or event) to the governance ledger",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "gap_identified": {"type": "string", "description": "What's missing (e.g., 'Aug 22 meeting content')"},
                        "reason_identified": {"type": "string", "description": "Why it's missing or where it was referenced"},
                        "significance": {"type": "string", "enum": ["high", "medium", "low"], "description": "Impact to investigation"},
                        "status": {"type": "string", "enum": ["open", "closed"], "description": "Has it been exhaustively searched?"}
                    },
                    "required": ["gap_identified", "reason_identified", "significance", "status"]
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        """Route tool calls to custody server."""
        logger.info(f"MCP tool call: {name} with arguments {arguments}")
        
        try:
            if name == "search_messages":
                result = custody.search_messages(
                    custodian=arguments.get("custodian"),
                    keyword=arguments.get("keyword"),
                    date_contains=arguments.get("date_contains")
                )
            elif name == "list_folder":
                result = custody.list_folder(custodian=arguments.get("custodian"))
            elif name == "read_file":
                result = custody.read_file(filepath=arguments.get("filepath"))
            elif name == "get_headers":
                result = custody.get_headers(filepath=arguments.get("filepath"))
            elif name == "hash_document":
                result = custody.hash_document(filepath=arguments.get("filepath"))
            elif name == "verify_hash":
                result = custody.verify_hash(
                    filepath=arguments.get("filepath"),
                    expected_hash=arguments.get("expected_hash")
                )
            elif name == "emit_documentary_gap":
                result = custody.emit_documentary_gap(
                    gap_identified=arguments.get("gap_identified"),
                    reason_identified=arguments.get("reason_identified"),
                    significance=arguments.get("significance"),
                    status=arguments.get("status")
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                    isError=True
                )
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result))],
                isError=False
            )
        
        except Exception as e:
            logger.error(f"Tool call error: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")],
                isError=True
            )
    
    logger.info(f"MCP Custody Server v1.4.3 initialized and ready")
    logger.info(f"Available tools:")
    logger.info(f"  - search_messages(custodian, keyword, date_contains)")
    logger.info(f"  - list_folder(custodian)")
    logger.info(f"  - read_file(filepath)")
    logger.info(f"  - get_headers(filepath)")
    logger.info(f"  - hash_document(filepath)")
    logger.info(f"  - verify_hash(filepath, expected_hash)")
    logger.info(f"  - emit_documentary_gap(gap_identified, reason_identified, significance, status)")
    logger.info(f"")
    logger.info(f"Server ready for MCP client connections (JSON-RPC protocol active)")
    logger.info(f"Starting MCP server on stdio...")
    
    # Start server on stdio using the correct FastMCP 1.29.0 API
    async with stdio_server() as (read_stream, write_stream):
        logger.info("MCP server listening on stdio")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info(f"Server shutdown requested by operator")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Server startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
