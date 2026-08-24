#!/usr/bin/env python3
"""
Dossier Space MCP Custody Server v1.1
Governance Ledger Implementation & Metadata Capture

Session: DS-20260806-S09.5
Purpose: Preserve material execution metadata with complete audit trail
Author: Ken Tombs (Operator), Claude (Design Lead)

Features:
- Sequential action ID generation (DS-20260806-S09.5-A01, A02, ...)
- Full parameter and result set capture for all MCP calls
- Candidate path persistence with traceable references
- JSONL ledger emission with immutable GUIDs
- Deduplication rule freezing
- Exception handling with ledger fallback
"""

import os
import sys
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

SESSION_ID = "DS-20260806-S09.5"
OPERATOR = "Ken Tombs"
DESIGN_LEAD = "Claude"

# Paths
ENRON_CORPUS_ROOT = r"E:\AAll XPlain\Dossier Space Pilot\ENRON Data Set Test 1\enron_mail_20150507"
GOVERNANCE_LEDGER_DIR = r"E:\AAll XPlain\Dossier Space Pilot\Governance Ledger"
RESULTS_DIR = os.path.join(GOVERNANCE_LEDGER_DIR, "results")
LEDGER_FILE = os.path.join(GOVERNANCE_LEDGER_DIR, "session-ledger.jsonl")

# ============================================================================
# LEDGER WRITER
# ============================================================================

class LedgerWriter:
    """Handles all ledger entry creation and persistence."""
    
    def __init__(self, session_id: str, ledger_path: str, results_dir: str):
        self.session_id = session_id
        self.ledger_path = ledger_path
        self.results_dir = results_dir
        self.action_counter = 0
        
        # Ensure directories exist
        Path(self.ledger_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.results_dir).mkdir(parents=True, exist_ok=True)
        
    def next_action_id(self) -> str:
        """Generate next sequential action ID."""
        self.action_counter += 1
        return f"{self.session_id}-A{self.action_counter:02d}"
    
    def emit_entry(
        self,
        entry_type: str,
        action_id: str,
        task_id: str,
        tool_name: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        result_set: Optional[List[str]] = None,
        result_set_reference: Optional[str] = None,
        candidate_paths: Optional[List[str]] = None,
        description: str = "",
        decision_rationale: str = "",
        dedup_rule: Optional[str] = None,
        linked_action_ids: Optional[List[str]] = None,
        material_decision: bool = False,
        severity: str = "informational",
        reconciliation_notes: str = "",
        status: str = "active"
    ) -> Dict[str, Any]:
        """
        Emit a ledger entry to the governance ledger.
        
        Args:
            entry_type: One of controlled values (decision, mcp_call, result_set, etc.)
            action_id: Unique action identifier
            task_id: Associated task ID
            tool_name: MCP tool name (if applicable)
            parameters: Exact parameters passed to tool
            result_set: Raw result list (file paths, etc.)
            result_set_reference: Path to persisted result file
            candidate_paths: List of candidate EML paths
            description: Human-readable description
            decision_rationale: Why this action was taken
            dedup_rule: Frozen deduplication logic
            linked_action_ids: List of related action IDs
            material_decision: Boolean flag
            severity: critical | major | minor | informational
            reconciliation_notes: MCP/Claude/PowerShell alignment notes
            status: active | superseded
        
        Returns:
            Entry dict (for reference)
        """
        
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
                "result_set_count": len(result_set) if result_set else None,
                "result_set_reference": result_set_reference,
                "candidate_paths": candidate_paths or [],
                "dedup_rule": dedup_rule,
                "decision_rationale": decision_rationale,
                "linked_action_ids": linked_action_ids or []
            },
            "status": status,
            "superseded_by": None,
            "reconciliation_notes": reconciliation_notes
        }
        
        # Persist to ledger file
        try:
            with open(self.ledger_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
            logger.info(f"Ledger entry {action_id} emitted: {entry_type}")
        except Exception as e:
            logger.error(f"Failed to write ledger entry {action_id}: {e}")
            # Still return entry; don't crash
        
        return entry
    
    def persist_result_set(
        self,
        action_id: str,
        result_set: List[str],
        format: str = "txt"
    ) -> str:
        """
        Persist raw result set to disk.
        
        Args:
            action_id: Action ID for naming
            result_set: List of paths/results
            format: "txt" or "json"
        
        Returns:
            Path to persisted result file
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{action_id}-results.{format}"
        filepath = os.path.join(self.results_dir, filename)
        
        try:
            if format == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(result_set, f, indent=2)
            else:  # txt
                with open(filepath, 'w', encoding='utf-8') as f:
                    for item in result_set:
                        f.write(item + '\n')
            logger.info(f"Result set persisted: {filepath} ({len(result_set)} items)")
        except Exception as e:
            logger.error(f"Failed to persist result set {action_id}: {e}")
            return None
        
        return filepath


# ============================================================================
# CUSTODY SERVER TOOLS
# ============================================================================

class CustodyServer:
    """Enron corpus access with governance ledger integration."""
    
    def __init__(self, corpus_root: str, ledger_writer: LedgerWriter):
        self.corpus_root = corpus_root
        self.ledger = ledger_writer
        self.task_id = "DS-20260806-S09.5-T04"  # Smoke test task
    
    def search_messages(
        self,
        custodian: str,
        keyword: str,
        date_contains: Optional[str] = None
    ) -> List[str]:
        """
        Search for messages by custodian, keyword, and optional date filter.
        Logs full execution to governance ledger.
        
        Args:
            custodian: Mailbox name (e.g., 'farmer-d')
            keyword: Case-insensitive keyword to match
            date_contains: Substring to match in Date header (e.g., 'May 2000')
        
        Returns:
            List of matching EML file paths
        """
        
        action_id = self.ledger.next_action_id()
        
        # Capture exact parameters
        parameters = {
            "custodian": custodian,
            "keyword": keyword,
            "date_contains": date_contains
        }
        
        logger.info(f"{action_id}: Searching custodian={custodian}, keyword={keyword}, date_contains={date_contains}")
        
        custodian_path = os.path.join(self.corpus_root, custodian, "all_documents")
        results = []
        
        if not os.path.isdir(custodian_path):
            logger.warning(f"Custodian path not found: {custodian_path}")
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
            return results
        
        # Walk custodian folder
        try:
            for root, dirs, files in os.walk(custodian_path):
                for file in files:
                    if not file.endswith('.eml'):
                        continue
                    
                    filepath = os.path.join(root, file)
                    
                    # Read file and check keyword + date
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            # Case-insensitive keyword search
                            if keyword.lower() not in content.lower():
                                continue
                            
                            # Optional date filter
                            if date_contains:
                                if date_contains not in content:
                                    continue
                            
                            # Match: capture relative path
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
            return results
        
        # Persist result set
        result_set_reference = self.ledger.persist_result_set(action_id, results, format="txt")
        
        # Emit ledger entry
        self.ledger.emit_entry(
            entry_type="mcp_call",
            action_id=action_id,
            task_id=self.task_id,
            tool_name="search_messages",
            parameters=parameters,
            result_set=results,
            result_set_reference=result_set_reference,
            candidate_paths=results,
            description=f"Searched custodian '{custodian}' for keyword '{keyword}' (date_contains={date_contains})",
            material_decision=False,
            severity="informational"
        )
        
        logger.info(f"{action_id}: Found {len(results)} results")
        return results
    
    def get_headers(self, filepath: str) -> Dict[str, str]:
        """
        Extract email headers from an EML file.
        Logs execution to governance ledger.
        
        Args:
            filepath: Relative path to EML file (e.g., 'farmer-d/all_documents/1914.eml')
        
        Returns:
            Dict of headers {Date, From, Subject, Message-ID, ...}
        """
        
        action_id = self.ledger.next_action_id()
        
        parameters = {
            "filepath": filepath
        }
        
        headers = {}
        full_filepath = os.path.join(self.corpus_root, filepath)
        
        logger.info(f"{action_id}: Reading headers from {filepath}")
        
        try:
            with open(full_filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.strip() == '':
                        break  # End of headers
                    
                    if ':' in line:
                        key, value = line.split(':', 1)
                        headers[key.strip()] = value.strip()
        
        except Exception as e:
            logger.error(f"Failed to read headers from {full_filepath}: {e}")
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
            return headers
        
        # Emit ledger entry
        self.ledger.emit_entry(
            entry_type="tool_call",
            action_id=action_id,
            task_id=self.task_id,
            tool_name="get_headers",
            parameters=parameters,
            description=f"Retrieved headers from {filepath}",
            material_decision=False,
            severity="informational"
        )
        
        return headers
    
    def list_folder(self, custodian: str) -> List[str]:
        """
        List all EML files in a custodian folder.
        Logs execution to governance ledger.
        
        Args:
            custodian: Mailbox name
        
        Returns:
            List of EML file paths
        """
        
        action_id = self.ledger.next_action_id()
        
        parameters = {
            "custodian": custodian
        }
        
        logger.info(f"{action_id}: Listing folder for custodian {custodian}")
        
        custodian_path = os.path.join(self.corpus_root, custodian, "all_documents")
        results = []
        
        if not os.path.isdir(custodian_path):
            logger.warning(f"Custodian path not found: {custodian_path}")
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
            return results
        
        try:
            for root, dirs, files in os.walk(custodian_path):
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
            return results
        
        # Persist result set
        result_set_reference = self.ledger.persist_result_set(action_id, results, format="txt")
        
        # Emit ledger entry
        self.ledger.emit_entry(
            entry_type="mcp_call",
            action_id=action_id,
            task_id=self.task_id,
            tool_name="list_folder",
            parameters=parameters,
            result_set=results,
            result_set_reference=result_set_reference,
            candidate_paths=results,
            description=f"Listed all EML files for custodian '{custodian}'",
            material_decision=False,
            severity="informational"
        )
        
        logger.info(f"{action_id}: Found {len(results)} files")
        return results
    
    def hash_document(self, filepath: str) -> str:
        """
        Generate SHA256 hash of an EML file.
        Logs execution to governance ledger.
        
        Args:
            filepath: Relative path to EML file
        
        Returns:
            SHA256 hash (hex)
        """
        
        import hashlib
        
        action_id = self.ledger.next_action_id()
        
        parameters = {
            "filepath": filepath
        }
        
        full_filepath = os.path.join(self.corpus_root, filepath)
        file_hash = None
        
        logger.info(f"{action_id}: Hashing {filepath}")
        
        try:
            sha256_hash = hashlib.sha256()
            with open(full_filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            file_hash = sha256_hash.hexdigest()
        
        except Exception as e:
            logger.error(f"Failed to hash {full_filepath}: {e}")
            self.ledger.emit_entry(
                entry_type="exception",
                action_id=action_id,
                task_id=self.task_id,
                tool_name="hash_document",
                parameters=parameters,
                description=f"Hash computation failed: {e}",
                material_decision=False,
                severity="major"
            )
            return None
        
        # Emit ledger entry
        self.ledger.emit_entry(
            entry_type="tool_call",
            action_id=action_id,
            task_id=self.task_id,
            tool_name="hash_document",
            parameters=parameters,
            description=f"Hashed {filepath}: {file_hash}",
            material_decision=False,
            severity="informational"
        )
        
        return file_hash
    
    def verify_hash(self, filepath: str, expected_hash: str) -> bool:
        """
        Verify SHA256 hash of an EML file.
        Logs execution to governance ledger.
        
        Args:
            filepath: Relative path to EML file
            expected_hash: Expected SHA256 hash (hex)
        
        Returns:
            True if hash matches, False otherwise
        """
        
        action_id = self.ledger.next_action_id()
        
        parameters = {
            "filepath": filepath,
            "expected_hash": expected_hash
        }
        
        actual_hash = self.hash_document(filepath)
        match = actual_hash == expected_hash if actual_hash else False
        
        logger.info(f"{action_id}: Hash verification for {filepath}: {match}")
        
        # Emit ledger entry
        self.ledger.emit_entry(
            entry_type="tool_call",
            action_id=action_id,
            task_id=self.task_id,
            tool_name="verify_hash",
            parameters=parameters,
            description=f"Hash verification for {filepath}: {'MATCH' if match else 'MISMATCH'}",
            material_decision=False,
            severity="major" if not match else "informational"
        )
        
        return match


# ============================================================================
# INITIALIZATION & SESSION MANAGEMENT
# ============================================================================

def initialize_session(ledger_writer: LedgerWriter):
    """Emit session_start entry."""
    action_id = ledger_writer.next_action_id()
    ledger_writer.emit_entry(
        entry_type="session_start",
        action_id=action_id,
        task_id="DS-20260806-S09.5-T02",
        description=f"Session {SESSION_ID} initialized: MCP Custody Server v1.1",
        material_decision=True,
        severity="critical"
    )
    logger.info(f"Session {SESSION_ID} started")


def smoke_test(custody_server: CustodyServer, ledger_writer: LedgerWriter):
    """
    Smoke test: Execute one search and validate ledger chain.
    """
    logger.info("=" * 70)
    logger.info("SMOKE TEST: Single keyword search with full ledger validation")
    logger.info("=" * 70)
    
    # Test parameters
    test_custodian = "farmer-d"
    test_keyword = "deal"
    test_date = None
    
    logger.info(f"\nExecuting: search_messages(custodian='{test_custodian}', keyword='{test_keyword}', date_contains={test_date})")
    
    results = custody_server.search_messages(
        custodian=test_custodian,
        keyword=test_keyword,
        date_contains=test_date
    )
    
    logger.info(f"\nResults: {len(results)} candidates found")
    if results:
        logger.info("Sample results (first 5):")
        for i, result in enumerate(results[:5]):
            logger.info(f"  {i+1}. {result}")
    
    # Validate ledger
    logger.info("\nValidating ledger entries...")
    with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
        entries = [json.loads(line) for line in f]
    
    logger.info(f"Total ledger entries: {len(entries)}")
    
    # Find the search_messages mcp_call entry
    search_entry = None
    for entry in entries:
        if entry.get('entry_type') == 'mcp_call' and entry.get('payload', {}).get('tool_name') == 'search_messages':
            search_entry = entry
            break
    
    if search_entry:
        logger.info(f"\nMCP Call Entry Found:")
        logger.info(f"  Action ID: {search_entry['action_id']}")
        logger.info(f"  Timestamp: {search_entry['timestamp']}")
        logger.info(f"  Result Count: {search_entry['payload']['result_set_count']}")
        logger.info(f"  Result File: {search_entry['payload']['result_set_reference']}")
        logger.info(f"  Candidate Paths: {len(search_entry['payload']['candidate_paths'])} items")
    else:
        logger.warning("MCP Call entry not found in ledger")
    
    logger.info("\n" + "=" * 70)
    logger.info("SMOKE TEST COMPLETE")
    logger.info("=" * 70)


if __name__ == "__main__":
    
    logger.info(f"Starting Dossier Space MCP Custody Server v1.1")
    logger.info(f"Session: {SESSION_ID}")
    logger.info(f"Ledger: {LEDGER_FILE}")
    
    # Initialize ledger writer
    ledger = LedgerWriter(SESSION_ID, LEDGER_FILE, RESULTS_DIR)
    
    # Emit session_start
    initialize_session(ledger)
    
    # Initialize custody server
    custody = CustodyServer(ENRON_CORPUS_ROOT, ledger)
    
    # Run smoke test
    smoke_test(custody, ledger)
    
    # Emit session_close (will be done after all work completes)
    # For now, server is ready for interactive use
    logger.info("\nServer initialized and ready for MCP integration.")
    logger.info(f"Governance Ledger: {LEDGER_FILE}")
    logger.info(f"Results Directory: {RESULTS_DIR}")
