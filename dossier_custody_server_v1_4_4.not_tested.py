#!/usr/bin/env python3
"""
Dossier Space MCP Custody Server v1.4.4
Persistent MCP Service for Evidence Operations with Raw JSON-RPC Protocol
Session: DS-202608xx-S12+ (JSON-RPC rebuild)
Purpose: Expose custody tools as persistent MCP service using raw JSON-RPC
Architecture: Claude Code (MCP client) ← JSON-RPC/stdio → Custody Server
             Each tool call independently logged to governance ledger
Version History:
- v1.3: Built without JSON-RPC protocol layer (blocker identified in Session 10)
- v1.4: Rebuild with FastMCP 1.29.0 (tool truncation bug identified)
- v1.4.3: FastMCP enum handling fix attempted (issue persisted)
- v1.4.4: Stripped FastMCP entirely; raw JSON-RPC 2.0 implementation on stdio
Key Features:
- NO external MCP dependencies (raw JSON-RPC 2.0)
- Full JSON-RPC protocol handler with explicit tool registry
- Stdio transport for Claude Code integration
- Full governance ledger integration (append-only, fail-closed)
- All 7 tools: search_messages, list_folder, read_file, get_headers, hash_document, verify_hash, emit_documentary_gap
- Complete audit logging of all JSON-RPC exchanges
Design Principle: "Watch is never the watched"
- Claude Code requests evidence operations via JSON-RPC
- Custody Server executes and independently records all actions
- Ledger is the canonical truth source
- All message exchanges logged for audit
- No external API calls (workstation-local only)
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
            flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
            fd = os.open(filepath, flags, 0o644)
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                if format == "txt":
                    f.write('\n'.join(result_set))
                elif format == "jsonl":
                    for item in result_set:
                        f.write(json.dumps(item) + '\n')
        except FileExistsError:
            logger.error(f"Result set file already exists: {filepath}")
            raise
        except Exception as e:
            logger.error(f"Failed to persist result set: {e}")
            raise
        # Compute hash
        sha256_hash = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256_hash.update(chunk)
        hash_hex = sha256_hash.hexdigest()
        return (f"results/{filename}", hash_hex)

# ============================================================================
# CUSTODY SERVER (CORPUS ACCESS LAYER)
# ============================================================================
class CustodyServer:
    """Provides read-verify access to corpus with governance ledger logging."""
    def __init__(self, corpus_root: str, ledger: LedgerWriter, task_id: str):
        self.corpus_root = corpus_root
        self.ledger = ledger
        self.task_id = task_id

    def _compute_document_hash(self, filepath: str) -> Optional[str]:
        """Compute SHA256 hash of a file."""
        try:
            with open(filepath, 'rb') as f:
                sha256_hash = hashlib.sha256()
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256_hash.update(chunk)
                return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Failed to compute hash for {filepath}: {e}")
            return None

    def search_messages(self, custodian: str, keyword: str, date_contains: Optional[str] = None) -> Dict[str, Any]:
        """Search for messages by custodian and keyword."""
        custodian_path = os.path.join(self.corpus_root, custodian)
        if not os.path.isdir(custodian_path):
            return {"error": f"Custodian folder not found: {custodian}"}
        results = []
        try:
            for root, dirs, files in os.walk(custodian_path):
                for file in files:
                    if file.endswith('.eml'):
                        filepath = os.path.join(root, file)
                        if not validate_path_containment(filepath, self.corpus_root):
                            logger.warning(f"Path containment check failed: {filepath}")
                            continue
                        try:
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if keyword.lower() in content.lower():
                                    if date_contains is None or date_contains in content:
                                        rel_path = os.path.relpath(filepath, self.corpus_root)
                                        results.append(rel_path)
                        except Exception as e:
                            logger.warning(f"Error reading {filepath}: {e}")
                            continue
        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}
        action_id = self.ledger.next_action_id()
        self.ledger.emit_entry(
            entry_type="tool_call",
            action_id=action_id,
            task_id=self.task_id,
            tool_name="search_messages",
            parameters={"custodian": custodian, "keyword": keyword, "date_contains": date_contains},
            description=f"Search messages in {custodian} for '{keyword}'",
            tool_output={"count": len(results), "results": results[:50]}
        )
        return {"keyword": keyword, "custodian": custodian, "count": len(results), "results": results}

    def list_folder(self, custodian: str) -> Dict[str, Any]:
        """List all EML files for a custodian."""
        custodian_path = os.path.join(self.corpus_root, custodian)
        if not os.path.isdir(custodian_path):
            return {"error": f"Custodian folder not found: {custodian}"}
        files = []
        try:
            for root, dirs, filenames in os.walk(custodian_path):
                for filename in filenames:
                    if filename.endswith('.eml'):
                        filepath = os.path.join(root, filename)
                        if validate_path_containment(filepath, self.corpus_root):
                            rel_path = os.path.relpath(filepath, self.corpus_root)
                            files.append(rel_path)
        except Exception as e:
            return {"error": f"Failed to list folder: {str(e)}"}
        action_id = self.ledger.next_action_id()
        self.ledger.emit_entry(
            entry_type="tool_call",
            action_id=action_id,
            task_id=self.task_id,
            tool_name="list_folder",
            parameters={"custodian": custodian},
            description=f"List folder for custodian {custodian}",
            tool_output={"count": len(files)}
        )
        return {"custodian": custodian, "count": len(files), "files": files}

    def read_file(self, filepath: str) -> Dict[str, Any]:
        """Read the full content of an EML file."""
        full_path = os.path.join(self.corpus_root, filepath)
        if not validate_path_containment(full_path, self.corpus_root):
            return {"error": "Path containment check failed"}
        if not os.path.isfile(full_path):
            return {"error": f"File not found: {filepath}"}
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            action_id = self.ledger.next_action_id()
            self.ledger.emit_entry(
                entry_type="tool_call",
                action_id=action_id,
                task_id=self.task_id,
                tool_name="read_file",
                parameters={"filepath": filepath},
                description=f"Read file: {filepath}",
                tool_output={"bytes": len(content)}
            )
            return {"filepath": filepath, "content": content}
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}

    def get_headers(self, filepath: str) -> Dict[str, Any]:
        """Extract email headers from an EML file."""
        full_path = os.path.join(self.corpus_root, filepath)
        if not validate_path_containment(full_path, self.corpus_root):
            return {"error": "Path containment check failed"}
        if not os.path.isfile(full_path):
            return {"error": f"File not found: {filepath}"}
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                headers = {}
                for line in f:
                    line = line.rstrip()
                    if not line:
                        break
                    if ':' in line:
                        key, value = line.split(':', 1)
                        headers[key.strip()] = value.strip()
            action_id = self.ledger.next_action_id()
            self.ledger.emit_entry(
                entry_type="tool_call",
                action_id=action_id,
                task_id=self.task_id,
                tool_name="get_headers",
                parameters={"filepath": filepath},
                description=f"Get headers: {filepath}",
                tool_output={"header_count": len(headers)}
            )
            return {"filepath": filepath, "headers": headers}
        except Exception as e:
            return {"error": f"Failed to get headers: {str(e)}"}

    def hash_document(self, filepath: str) -> Dict[str, Any]:
        """Compute SHA256 hash of an EML file."""
        full_path = os.path.join(self.corpus_root, filepath)
        if not validate_path_containment(full_path, self.corpus_root):
            return {"error": "Path containment check failed"}
        if not os.path.isfile(full_path):
            return {"error": f"File not found: {filepath}"}
        hash_hex = self._compute_document_hash(full_path)
        if hash_hex is None:
            return {"error": "Failed to compute hash"}
        action_id = self.ledger.next_action_id()
        self.ledger.emit_entry(
            entry_type="tool_call",
            action_id=action_id,
            task_id=self.task_id,
            tool_name="hash_document",
            parameters={"filepath": filepath},
            description=f"Hash document: {filepath}",
            tool_output={"hash": hash_hex}
        )
        return {"filepath": filepath, "sha256": hash_hex}

    def verify_hash(self, filepath: str, expected_hash: str) -> Dict[str, Any]:
        """Verify SHA256 hash of an EML file."""
        full_path = os.path.join(self.corpus_root, filepath)
        if not validate_path_containment(full_path, self.corpus_root):
            return {"error": "Path containment check failed"}
        if not os.path.isfile(full_path):
            return {"error": f"File not found: {filepath}"}
        hash_hex = self._compute_document_hash(full_path)
        if hash_hex is None:
            return {"error": "Failed to compute hash"}
        match = hash_hex.lower() == expected_hash.lower()
        action_id = self.ledger.next_action_id()
        self.ledger.emit_entry(
            entry_type="tool_call",
            action_id=action_id,
            task_id=self.task_id,
            tool_name="verify_hash",
            parameters={"filepath": filepath, "expected_hash": expected_hash},
            description=f"Verify hash: {filepath}",
            tool_output={"match": match, "computed": hash_hex}
        )
        return {"filepath": filepath, "match": match, "computed": hash_hex, "expected": expected_hash}

    def emit_documentary_gap(self, gap_identified: str, reason_identified: str, significance: str, status: str) -> Dict[str, Any]:
        """Record a documentary gap to the governance ledger."""
        if significance not in ["high", "medium", "low"]:
            return {"error": f"Significance must be high/medium/low, got {significance}"}
        if status not in ["open", "closed"]:
            return {"error": f"Status must be open/closed, got {status}"}
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
# TOOL REGISTRY (JSON SCHEMAS)
# ============================================================================
TOOLS_REGISTRY = [
    {
        "name": "search_messages",
        "description": "Search for messages by custodian and keyword",
        "inputSchema": {
            "type": "object",
            "properties": {
                "custodian": {"type": "string", "description": "Custodian folder name (e.g., 'farmer-d')"},
                "keyword": {"type": "string", "description": "Keyword to search for"},
                "date_contains": {"type": "string", "description": "Optional date string to filter results"}
            },
            "required": ["custodian", "keyword"]
        }
    },
    {
        "name": "list_folder",
        "description": "List all EML files for a custodian",
        "inputSchema": {
            "type": "object",
            "properties": {
                "custodian": {"type": "string", "description": "Custodian folder name"}
            },
            "required": ["custodian"]
        }
    },
    {
        "name": "read_file",
        "description": "Read the full content of an EML file",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Relative path to EML file"}
            },
            "required": ["filepath"]
        }
    },
    {
        "name": "get_headers",
        "description": "Extract email headers from an EML file",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Relative path to EML file"}
            },
            "required": ["filepath"]
        }
    },
    {
        "name": "hash_document",
        "description": "Compute SHA256 hash of an EML file",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Relative path to EML file"}
            },
            "required": ["filepath"]
        }
    },
    {
        "name": "verify_hash",
        "description": "Verify SHA256 hash of an EML file",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Relative path to EML file"},
                "expected_hash": {"type": "string", "description": "Expected SHA256 hash (hex)"}
            },
            "required": ["filepath", "expected_hash"]
        }
    },
    {
        "name": "emit_documentary_gap",
        "description": "Record a documentary gap (missing communication, document, or event) to the governance ledger",
        "inputSchema": {
            "type": "object",
            "properties": {
                "gap_identified": {"type": "string", "description": "What's missing (e.g., 'Aug 22 meeting content')"},
                "reason_identified": {"type": "string", "description": "Why it's missing or where it was referenced"},
                "significance": {"type": "string", "description": "Impact to investigation: high, medium, or low"},
                "status": {"type": "string", "description": "Status: open (not found) or closed (exhaustively searched)"}
            },
            "required": ["gap_identified", "reason_identified", "significance", "status"]
        }
    }
]

# ============================================================================
# JSON-RPC MESSAGE HANDLER
# ============================================================================
class JSONRPCServer:
    """Raw JSON-RPC 2.0 server over stdio."""
    def __init__(self, custody: CustodyServer):
        self.custody = custody
        self.initialized = False

    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process a JSON-RPC 2.0 request."""
        jsonrpc = message.get("jsonrpc", "2.0")
        method = message.get("method", "")
        params = message.get("params", {})
        msg_id = message.get("id")

        logger.info(f"JSON-RPC request: method={method}, id={msg_id}")

        try:
            if method == "initialize":
                response = self.handle_initialize(msg_id)
            elif method == "tools/list":
                response = self.handle_tools_list(msg_id)
            elif method == "tools/call":
                response = await self.handle_tool_call(params, msg_id)
            else:
                response = self.error_response(msg_id, -32601, f"Method not found: {method}")
        except Exception as e:
            logger.error(f"Exception in handle_message: {e}")
            response = self.error_response(msg_id, -32603, str(e))

        logger.info(f"JSON-RPC response: id={msg_id}, has_error={'error' in response}")
        return response

    def handle_initialize(self, msg_id: Optional[int]) -> Dict[str, Any]:
        """Handle initialize request."""
        self.initialized = True
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "serverInfo": {
                    "name": "Dossier Space MCP Custody Server",
                    "version": "1.4.4"
                }
            }
        }

    def handle_tools_list(self, msg_id: Optional[int]) -> Dict[str, Any]:
        """Handle tools/list request."""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": TOOLS_REGISTRY
            }
        }

    async def handle_tool_call(self, params: Dict[str, Any], msg_id: Optional[int]) -> Dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        logger.info(f"Tool call: name={tool_name}, args={arguments}")

        try:
            if tool_name == "search_messages":
                result = self.custody.search_messages(
                    custodian=arguments.get("custodian"),
                    keyword=arguments.get("keyword"),
                    date_contains=arguments.get("date_contains")
                )
            elif tool_name == "list_folder":
                result = self.custody.list_folder(custodian=arguments.get("custodian"))
            elif tool_name == "read_file":
                result = self.custody.read_file(filepath=arguments.get("filepath"))
            elif tool_name == "get_headers":
                result = self.custody.get_headers(filepath=arguments.get("filepath"))
            elif tool_name == "hash_document":
                result = self.custody.hash_document(filepath=arguments.get("filepath"))
            elif tool_name == "verify_hash":
                result = self.custody.verify_hash(
                    filepath=arguments.get("filepath"),
                    expected_hash=arguments.get("expected_hash")
                )
            elif tool_name == "emit_documentary_gap":
                result = self.custody.emit_documentary_gap(
                    gap_identified=arguments.get("gap_identified"),
                    reason_identified=arguments.get("reason_identified"),
                    significance=arguments.get("significance"),
                    status=arguments.get("status")
                )
            else:
                return self.error_response(msg_id, -32601, f"Unknown tool: {tool_name}")
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return self.error_response(msg_id, -32603, str(e))

        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": result
        }

    def error_response(self, msg_id: Optional[int], code: int, message: str) -> Dict[str, Any]:
        """Generate a JSON-RPC error response."""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": code,
                "message": message
            }
        }

# ============================================================================
# STDIO MESSAGE LOOP
# ============================================================================
async def message_loop(server: JSONRPCServer):
    """Read JSON-RPC messages from stdin, write responses to stdout."""
    loop = asyncio.get_event_loop()

    while True:
        try:
            # Read line from stdin
            line = await loop.run_in_executor(None, sys.stdin.readline)
            if not line:
                logger.info("EOF on stdin; shutting down")
                break

            line = line.strip()
            if not line:
                continue

            # Parse JSON-RPC message
            try:
                message = json.loads(line)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "Parse error"}
                }
                print(json.dumps(response), flush=True)
                continue

            # Handle message
            response = await server.handle_message(message)

            # Send response
            print(json.dumps(response), flush=True)

        except Exception as e:
            logger.error(f"Exception in message loop: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            }
            print(json.dumps(error_response), flush=True)

# ============================================================================
# MAIN
# ============================================================================
async def main():
    """Main entry point."""
    logger.info(f"Starting Dossier Space MCP Custody Server v1.4.4")
    logger.info(f"Session: {SESSION_ID}")
    logger.info(f"Ledger: {LEDGER_FILE}")
    logger.info(f"Corpus Root: {ENRON_CORPUS_ROOT}")
    logger.info(f"Mode: Raw JSON-RPC 2.0 on stdio (FastMCP removed)")

    # Initialize ledger
    ledger = LedgerWriter(
        session_id=SESSION_ID,
        ledger_path=LEDGER_FILE,
        fallback_path=LEDGER_FALLBACK_FILE,
        results_dir=RESULTS_DIR
    )

    # Initialize custody server
    custody = CustodyServer(
        corpus_root=ENRON_CORPUS_ROOT,
        ledger=ledger,
        task_id=f"{SESSION_ID}-T01"
    )

    # Log session start
    action_id = ledger.next_action_id()
    ledger.emit_entry(
        entry_type="session_start",
        action_id=action_id,
        task_id=f"{SESSION_ID}-T01",
        description=f"Session {SESSION_ID} initialized: MCP Custody Server v1.4.4 (raw JSON-RPC, FastMCP removed)",
        material_decision=True,
        severity="critical"
    )

    logger.info(f"MCP Custody Server v1.4.4 initialized and ready")
    logger.info(f"Available tools (7):")
    for tool in TOOLS_REGISTRY:
        logger.info(f"  - {tool['name']}")
    logger.info(f"JSON-RPC protocol: Active")
    logger.info(f"Governance ledger: {LEDGER_FILE}")
    logger.info(f"Server listening on stdio...")

    # Start message loop
    jsonrpc_server = JSONRPCServer(custody)
    await message_loop(jsonrpc_server)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info(f"Server shutdown requested by operator")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)
