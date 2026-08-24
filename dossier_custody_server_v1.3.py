#!/usr/bin/env python3
"""
Dossier Space MCP Custody Server v1.3
Persistent MCP Service for Evidence Operations

Session: DS-20260806-S10
Purpose: Expose custody tools as persistent MCP service
Architecture: Claude Code (MCP client) → Custody Server (persistent service)
             Each tool call independently logged to governance ledger

Key Changes from v1.2:
- No smoke test on startup
- Persistent service (does not exit after initialization)
- MCP tool endpoints registered and ready to accept calls
- Each tool execution: action ID generated, parameters logged, results persisted, ledger entry emitted
- Separation principle: analyst and custody mechanism remain independent

Design: "Watch is never the watched"
- Claude Code requests evidence operations
- Custody Server executes and independently records
- No direct class imports; MCP tool calls only
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

# ============================================================================
# CONFIGURATION
# ============================================================================

SESSION_ID = "DS-20260806-S10"
OPERATOR = "Ken Tombs"
DESIGN_LEAD = "Claude"

# Paths
ENRON_CORPUS_ROOT = r"E:\AAll XPlain\Dossier Space Pilot\ENRON Data Set Test 1\enron_mail_20150507\maildir"
GOVERNANCE_LEDGER_DIR = r"E:\AAll XPlain\Dossier Space Pilot\Governance Ledger"
RESULTS_DIR = os.path.join(GOVERNANCE_LEDGER_DIR, "results")
LEDGER_FILE = os.path.join(GOVERNANCE_LEDGER_DIR, "session-ledger.jsonl")
LEDGER_FALLBACK_FILE = os.path.join(GOVERNANCE_LEDGER_DIR, "session-ledger-DEGRADED.jsonl")

# Controlled value enums (validation)
ENTRY_TYPES = {
    "session_start", "decision", "tool_call", "mcp_call", "result_set",
    "candidate_set", "candidate_cluster", "operator_intervention", "finding",
    "assurance", "exception", "correction", "session_close"
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
        
        # Try primary ledger
        if self._write_ledger(entry, use_fallback=False):
            logger.info(f"Ledger entry {action_id} emitted: {entry_type}")
            return entry
        
        # Primary failed, try fallback
        logger.warning(f"Primary ledger write failed; attempting fallback")
        entry['reconciliation_notes'] = f"DEGRADED: {entry.get('reconciliation_notes', '')}".strip()
        
        if self._write_ledger(entry, use_fallback=True):
            logger.warning(f"Ledger entry {action_id} written to FALLBACK ledger (degraded mode)")
            return entry
        
        # Both failed: fail-closed exception
        error_msg = f"CRITICAL: Ledger write failed (primary and fallback). Evidence operation cannot proceed."
        logger.critical(error_msg)
        raise RuntimeError(error_msg)
    
    def persist_result_set(
        self,
        action_id: str,
        result_set: List[str],
        format: str = "txt"
    ) -> tuple:
        """Persist raw result set to disk with exclusive creation and SHA256 hash."""
        
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{action_id}-{unique_id}-results.{format}"
        filepath = os.path.join(self.results_dir, filename)
        
        if os.path.exists(filepath):
            logger.warning(f"Result file already exists (unexpected): {filepath}")
            return None, None
        
        try:
            if format == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(result_set, f, indent=2)
            else:  # txt
                with open(filepath, 'w', encoding='utf-8') as f:
                    for item in result_set:
                        f.write(item + '\n')
            
            sha256_hash = self._compute_file_hash(filepath)
            
            logger.info(f"Result set persisted: {filepath} ({len(result_set)} items, SHA256: {sha256_hash[:8]}...)")
            return filepath, sha256_hash
        
        except Exception as e:
            logger.error(f"Failed to persist result set {action_id}: {e}")
            return None, None
    
    def _compute_file_hash(self, filepath: str) -> str:
        """Compute SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash file {filepath}: {e}")
            return None


# ============================================================================
# PATH CONTAINMENT VALIDATION
# ============================================================================

def validate_path_containment(resolved_path: str, corpus_root: str) -> bool:
    """Validate that resolved_path is contained within corpus_root."""
    norm_resolved = os.path.normpath(os.path.abspath(resolved_path))
    norm_root = os.path.normpath(os.path.abspath(corpus_root))
    
    if not norm_root.endswith(os.sep):
        norm_root += os.sep
    
    if not norm_resolved.startswith(norm_root) and norm_resolved != norm_root.rstrip(os.sep):
        logger.error(f"Path containment violation: {norm_resolved} not under {norm_root}")
        return False
    
    return True


# ============================================================================
# CUSTODY SERVER TOOLS
# ============================================================================

class CustodyServer:
    """Enron corpus access with governance ledger integration."""
    
    def __init__(self, corpus_root: str, ledger_writer: LedgerWriter, task_id: str):
        self.corpus_root = corpus_root
        self.ledger = ledger_writer
        self.task_id = task_id
    
    def search_messages(
        self,
        custodian: str,
        keyword: str,
        date_contains: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for messages by custodian, keyword, and optional date filter.
        Returns structured result with candidate paths and metadata.
        """
        
        action_id = self.ledger.next_action_id()
        
        parameters = {
            "custodian": custodian,
            "keyword": keyword,
            "date_contains": date_contains
        }
        
        logger.info(f"{action_id}: Searching custodian={custodian}, keyword={keyword}, date_contains={date_contains}")
        
        custodian_path = os.path.join(self.corpus_root, custodian, "all_documents")
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
            return {"candidates": [], "error": "Path containment violation", "action_id": action_id}
        
        results = []
        
        if not os.path.isdir(resolved_path):
            logger.warning(f"Custodian path not found: {resolved_path}")
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
            return {"candidates": [], "error": "Custodian path not found", "action_id": action_id}
        
        # Walk custodian folder
        try:
            for root, dirs, files in os.walk(resolved_path):
                for file in files:
                    if not file.endswith('.eml'):
                        continue
                    
                    filepath = os.path.join(root, file)
                    
                    if not validate_path_containment(filepath, self.corpus_root):
                        logger.warning(f"Skipping file outside corpus: {filepath}")
                        continue
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            if keyword.lower() not in content.lower():
                                continue
                            
                            if date_contains:
                                if date_contains not in content:
                                    continue
                            
                            rel_path = os.path.relpath(filepath, self.corpus_root)
                            results.append(rel_path)
                    
                    except Exception as e:
                        logger.warning(f"Error reading {filepath}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
            self.ledger.emit_entry(
                entry_type="exception",
                action_id=action_id,
                task_id=self.task_id,
                tool_name="search_messages",
                parameters=parameters,
                description=f"Search execution failed: {e}",
                material_decision=False,
                severity="critical"
            )
            return {"candidates": [], "error": str(e), "action_id": action_id}
        
        # Persist result set with hash
        result_set_reference, result_set_sha256 = self.ledger.persist_result_set(action_id, results, format="txt")
        
        # Emit ledger entry
        self.ledger.emit_entry(
            entry_type="mcp_call",
            action_id=action_id,
            task_id=self.task_id,
            tool_name="search_messages",
            parameters=parameters,
            result_set=results,
            result_set_reference=result_set_sha256 and result_set_reference,
            result_set_sha256=result_set_sha256,
            candidate_paths=results,
            description=f"Searched custodian '{custodian}' for keyword '{keyword}'",
            material_decision=False,
            severity="informational"
        )
        
        logger.info(f"{action_id}: Found {len(results)} results")
        
        return {
            "candidates": results,
            "count": len(results),
            "action_id": action_id,
            "result_file": result_set_reference,
            "result_sha256": result_set_sha256
        }
    
    def get_headers(self, filepath: str) -> Dict[str, Any]:
        """Extract email headers from an EML file."""
        
        action_id = self.ledger.next_action_id()
        parameters = {"filepath": filepath}
        headers = {}
        
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
        
        try:
            with open(resolved_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.strip() == '':
                        break
                    if ':' in line:
                        key, value = line.split(':', 1)
                        headers[key.strip()] = value.strip()
        
        except Exception as e:
            logger.error(f"Failed to read headers from {resolved_path}: {e}")
            self.ledger.emit_entry(
                entry_type="exception",
                action_id=action_id,
                task_id=self.task_id,
                tool_name="get_headers",
                parameters=parameters,
                description=f"Failed to read headers: {e}",
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
            description=f"Retrieved {len(headers)} headers from {filepath}",
            tool_output={"headers": headers},
            material_decision=False,
            severity="informational"
        )
        
        return {"headers": headers, "action_id": action_id}
    
    def list_folder(self, custodian: str) -> Dict[str, Any]:
        """List all EML files in a custodian folder."""
        
        action_id = self.ledger.next_action_id()
        parameters = {"custodian": custodian}
        results = []
        
        custodian_path = os.path.join(self.corpus_root, custodian, "all_documents")
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
            result_set_reference=result_set_sha256 and result_set_reference,
            result_set_sha256=result_set_sha256,
            candidate_paths=results,
            description=f"Listed all EML files for custodian '{custodian}'",
            material_decision=False,
            severity="informational"
        )
        
        return {"files": results, "count": len(results), "action_id": action_id}
    
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


# ============================================================================
# MCP SERVICE INITIALIZATION
# ============================================================================

def initialize_session(ledger_writer: LedgerWriter, task_id: str):
    """Emit session_start entry."""
    action_id = ledger_writer.next_action_id()
    ledger_writer.emit_entry(
        entry_type="session_start",
        action_id=action_id,
        task_id=task_id,
        description=f"Session {SESSION_ID} initialized: MCP Custody Server v1.3 (persistent service)",
        material_decision=True,
        severity="critical"
    )
    logger.info(f"Session {SESSION_ID} started - Service ready for MCP tool calls")


# ============================================================================
# MAIN SERVICE ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    
    logger.info(f"Starting Dossier Space MCP Custody Server v1.3")
    logger.info(f"Session: {SESSION_ID}")
    logger.info(f"Ledger: {LEDGER_FILE}")
    logger.info(f"Corpus Root: {ENRON_CORPUS_ROOT}")
    logger.info(f"Mode: Persistent MCP Service")
    
    # Initialize ledger writer (with counter recovery)
    ledger = LedgerWriter(SESSION_ID, LEDGER_FILE, LEDGER_FALLBACK_FILE, RESULTS_DIR)
    
    task_id = "DS-20260806-S10-T02"
    
    # Emit session_start
    initialize_session(ledger, task_id)
    
    # Initialize custody server
    custody = CustodyServer(ENRON_CORPUS_ROOT, ledger, task_id)
    
    logger.info(f"MCP Custody Server v1.3 initialized and ready")
    logger.info(f"Available tools:")
    logger.info(f"  - search_messages(custodian, keyword, date_contains)")
    logger.info(f"  - get_headers(filepath)")
    logger.info(f"  - list_folder(custodian)")
    logger.info(f"  - hash_document(filepath)")
    logger.info(f"  - verify_hash(filepath, expected_hash)")
    logger.info(f"")
    logger.info(f"Waiting for Claude Code MCP client connections...")
    logger.info(f"Server is persistent - does not auto-exit")
    
    # Keep server running
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info(f"Server shutdown requested")
        logger.info(f"Session {SESSION_ID} closed by operator")
        sys.exit(0)
