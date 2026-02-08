"""Service module for parsing Ansible logs using ansible-output-parser."""

import json
import re
import tempfile
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ansible_parser.logs import Logs
from ansible_parser.play import Play


@dataclass
class ParsedHost:
    """Represents parsed host data from Ansible output."""

    hostname: str
    ok: int = 0
    changed: int = 0
    failed: int = 0
    unreachable: int = 0
    skipped: int = 0
    rescued: int = 0
    ignored: int = 0


@dataclass
class ParsedPlay:
    """Represents parsed play data from Ansible output."""

    name: str
    order: int
    line_number: Optional[int] = None


@dataclass
class ParsedTaskResult:
    """Represents a single task execution result on a host."""

    hostname: str
    status: str  # ok, changed, failed, fatal, skipping, unreachable, ignored, rescued
    message: Optional[str] = None


@dataclass
class ParsedTask:
    """Represents a parsed task from Ansible output."""

    name: str
    order: int
    play_name: str
    line_number: Optional[int] = None
    results: list[ParsedTaskResult] = field(default_factory=list)


@dataclass
class ParseResult:
    """Result of parsing an Ansible log."""

    success: bool
    hosts: list[ParsedHost] = field(default_factory=list)
    plays: list[ParsedPlay] = field(default_factory=list)
    tasks: list[ParsedTask] = field(default_factory=list)
    timestamp: Optional[datetime] = None
    error: Optional[str] = None
    detail: Optional[str] = None
    parser_type: Optional[str] = None
    traceback_str: Optional[str] = None

    @property
    def play_names(self) -> list[str]:
        """Return list of play names for backwards compatibility."""
        return [p.name for p in self.plays]


class LogParserService:
    """Service to parse Ansible logs using ansible-output-parser."""

    # Pattern to detect timestamped log format: "YYYY-MM-DD HH:MM:SS,mmm | "
    TIMESTAMP_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \|")
    # Pattern to match PLAY lines and extract play name
    PLAY_PATTERN = re.compile(r"PLAY \[([^\]]+)\]")
    # Pattern to match TASK lines and extract task name
    TASK_PATTERN = re.compile(r"TASK \[([^\]]+)\]")

    def parse(self, raw_content: str) -> ParseResult:
        """
        Auto-detect format and parse log content.

        Args:
            raw_content: Raw Ansible log content (stdout or timestamped log)

        Returns:
            ParseResult with hosts/plays data or error details
        """
        if not raw_content or not raw_content.strip():
            return ParseResult(
                success=False,
                error="Empty log content",
                detail="The provided log content is empty or contains only whitespace",
            )

        # Normalize line endings (CRLF -> LF) for consistent parsing
        # Browser textareas may submit with Windows-style line endings
        raw_content = raw_content.replace("\r\n", "\n").replace("\r", "\n")

        parser_type = self._detect_format(raw_content)

        try:
            if parser_type == "logs":
                return self._parse_log_file(raw_content)
            else:
                return self._parse_play_output(raw_content)
        except Exception as e:
            return ParseResult(
                success=False,
                error="Log parsing failed",
                detail=str(e),
                parser_type=parser_type,
                traceback_str=traceback.format_exc(),
            )

    def _detect_format(self, content: str) -> str:
        """
        Detect if content is raw stdout or timestamped log format.

        Args:
            content: Raw log content

        Returns:
            'logs' for timestamped format, 'play' for raw stdout
        """
        first_line = content.strip().split("\n")[0] if content.strip() else ""
        if self.TIMESTAMP_PATTERN.match(first_line):
            return "logs"
        return "play"

    def _parse_play_output(self, content: str) -> ParseResult:
        """
        Parse using ansible_parser.play.Play class for raw stdout format.

        Args:
            content: Raw Ansible playbook stdout output

        Returns:
            ParseResult with extracted hosts, plays, and tasks
        """
        parser = Play(play_output=content)

        # Extract play names from parser
        play_names = list(parser.plays().keys())

        # Find line numbers for each play
        plays = self._extract_plays_with_line_numbers(content, play_names)

        # Extract hosts from recap
        hosts = self._extract_hosts_from_recap(parser)

        # Extract tasks directly from raw content (handles serial execution)
        tasks = self._extract_tasks_from_content(content, play_names)

        if not hosts:
            return ParseResult(
                success=False,
                error="No hosts found in log",
                detail="The parser could not find any PLAY RECAP section",
                parser_type="play",
            )

        return ParseResult(
            success=True,
            hosts=hosts,
            plays=plays,
            tasks=tasks,
            timestamp=None,  # Raw stdout doesn't have timestamps
            parser_type="play",
        )

    def _parse_log_file(self, content: str) -> ParseResult:
        """
        Parse using ansible_parser.logs.Logs class for timestamped log format.

        Args:
            content: Timestamped log file content

        Returns:
            ParseResult with extracted hosts, plays, and tasks
        """
        # Logs class requires a file path, so we write to a temp file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".log", delete=False
        ) as tmp_file:
            tmp_file.write(content)
            tmp_file.flush()
            tmp_path = tmp_file.name

        try:
            log_parser = Logs(log_file=tmp_path)

            # Collect all hosts and plays from all parsed plays
            all_hosts: dict[str, ParsedHost] = {}
            all_play_names: list[str] = []

            for play in log_parser.plays:
                # Get play names
                play_names = list(play.plays().keys())
                for name in play_names:
                    if name not in all_play_names:
                        all_play_names.append(name)

                # Get hosts from recap
                hosts = self._extract_hosts_from_recap(play)
                for host in hosts:
                    if host.hostname in all_hosts:
                        # Aggregate counts
                        existing = all_hosts[host.hostname]
                        existing.ok += host.ok
                        existing.changed += host.changed
                        existing.failed += host.failed
                        existing.unreachable += host.unreachable
                        existing.skipped += host.skipped
                        existing.rescued += host.rescued
                        existing.ignored += host.ignored
                    else:
                        all_hosts[host.hostname] = host

            # Strip timestamps from content for task extraction
            stripped_content = self._strip_timestamps(content)

            # Extract tasks directly from raw content (handles serial execution)
            all_tasks = self._extract_tasks_from_content(
                stripped_content, all_play_names
            )

            if not all_hosts:
                return ParseResult(
                    success=False,
                    error="No hosts found in log",
                    detail="The parser could not find any PLAY RECAP section",
                    parser_type="logs",
                )

            # Find line numbers for each play
            plays = self._extract_plays_with_line_numbers(content, all_play_names)

            return ParseResult(
                success=True,
                hosts=list(all_hosts.values()),
                plays=plays,
                tasks=all_tasks,
                timestamp=log_parser.last_processed_time,
                parser_type="logs",
            )

        finally:
            # Clean up temp file
            import os

            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def _strip_timestamps(self, content: str) -> str:
        """
        Strip timestamp prefixes from log lines.

        Converts lines like "2024-01-15 10:30:00,000 | TASK [name]"
        to "TASK [name]" for consistent parsing.

        Args:
            content: Raw timestamped log content

        Returns:
            Content with timestamp prefixes removed
        """
        lines = content.split("\n")
        stripped = []
        for line in lines:
            match = self.TIMESTAMP_PATTERN.match(line)
            if match:
                # Remove the timestamp prefix (everything up to and including " | ")
                pipe_idx = line.find(" | ")
                if pipe_idx != -1:
                    stripped.append(line[pipe_idx + 3 :])
                else:
                    stripped.append(line)
            else:
                stripped.append(line)
        return "\n".join(stripped)

    def _extract_plays_with_line_numbers(
        self, content: str, play_names: list[str]
    ) -> list[ParsedPlay]:
        """
        Extract plays with their line numbers from raw content.

        Args:
            content: Raw log content
            play_names: List of play names to find

        Returns:
            List of ParsedPlay objects with name, order, and line_number
        """
        plays: list[ParsedPlay] = []
        lines = content.split("\n")

        # Track which plays we've found to maintain order
        order = 0
        found_plays: set[str] = set()

        for line_num, line in enumerate(lines, start=1):
            match = self.PLAY_PATTERN.search(line)
            if match:
                play_name = match.group(1)
                # Only add if this play name is in our expected list
                if play_name in play_names and play_name not in found_plays:
                    plays.append(
                        ParsedPlay(name=play_name, order=order, line_number=line_num)
                    )
                    found_plays.add(play_name)
                    order += 1

        # Add any plays that weren't found in the content (shouldn't happen normally)
        for name in play_names:
            if name not in found_plays:
                plays.append(ParsedPlay(name=name, order=order, line_number=None))
                order += 1

        return plays

    def _extract_hosts_from_recap(self, parser: Play) -> list[ParsedHost]:
        """
        Extract host data from parser._recap attribute.

        Args:
            parser: Play parser instance

        Returns:
            List of ParsedHost objects with task counts
        """
        hosts = []

        # Access the internal _recap dict
        recap = getattr(parser, "_recap", {})

        for hostname, counts in recap.items():
            host = ParsedHost(
                hostname=hostname,
                ok=counts.get("ok", 0),
                changed=counts.get("changed", 0),
                failed=counts.get("failed", 0),
                unreachable=counts.get("unreachable", 0),
                skipped=counts.get("skipped", 0),
                rescued=counts.get("rescued", 0),
                ignored=counts.get("ignored", 0),
            )
            hosts.append(host)

        return hosts

    # Pattern to match task status lines
    # e.g., "ok: [hostname]", "failed: [host] (item=x)"
    STATUS_PATTERN = re.compile(
        r"(ok|changed|failed|fatal|skipping|unreachable|ignored|rescued)"
        r":\s+\[([^\]]+)\]",
        re.IGNORECASE,
    )

    def _extract_tasks_from_content(
        self, content: str, play_names: list[str]
    ) -> list[ParsedTask]:
        """
        Parse tasks directly from raw content, handling serial execution.

        When Ansible uses `serial`, the same PLAY header appears multiple times
        (once per batch). The ansible-output-parser library loses earlier batches.
        This method parses the raw content directly and merges results across
        serial batches using (play_name, task_name, order_within_play) as key.

        Args:
            content: Raw log content (with timestamps already stripped if needed)
            play_names: List of known play names (used for validation)

        Returns:
            List of ParsedTask objects with per-host results merged across batches
        """
        lines = content.split("\n")

        current_play: Optional[str] = None
        # Track task order per play; resets to 0 on each PLAY header (for merging)
        play_task_order: dict[str, int] = {}
        # Key: (play_name, task_name, order) -> ParsedTask
        task_map: dict[tuple[str, str, int], ParsedTask] = {}

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Check for PLAY header
            if stripped.startswith("PLAY ["):
                play_match = self.PLAY_PATTERN.search(stripped)
                if play_match:
                    current_play = play_match.group(1)
                    # Reset order to 0 for each PLAY section (serial batches
                    # repeat the same play, so resetting allows merging by order)
                    play_task_order[current_play] = 0
                i += 1
                continue

            # Check for TASK header
            if stripped.startswith("TASK [") and current_play is not None:
                task_match = self.TASK_PATTERN.search(stripped)
                if task_match:
                    task_name = task_match.group(1)
                    task_line_number = i + 1  # 1-indexed
                    order = play_task_order.get(current_play, 0)
                    play_task_order[current_play] = order + 1

                    key = (current_play, task_name, order)

                    # Parse following lines for host results until next section
                    i += 1
                    while i < len(lines):
                        result_line = lines[i]
                        result_stripped = result_line.strip()

                        # Stop at next section boundary
                        if (
                            result_stripped.startswith("TASK [")
                            or result_stripped.startswith("PLAY [")
                            or result_stripped.startswith("PLAY RECAP")
                        ):
                            break

                        # Try to match status line
                        status_match = self.STATUS_PATTERN.match(result_stripped)
                        if status_match:
                            task_status = status_match.group(1).lower()
                            hostname = status_match.group(2)
                            failure_msg = None

                            # Extract failure message from JSON block
                            if task_status in ("failed", "fatal"):
                                failure_msg = self._extract_failure_message(lines, i)

                            # Get or create ParsedTask
                            if key not in task_map:
                                task_map[key] = ParsedTask(
                                    name=task_name,
                                    order=order,
                                    play_name=current_play,
                                    line_number=task_line_number,
                                    results=[],
                                )

                            # Merge: add result, replacing any existing result
                            # for this host (later batch wins)
                            existing_task = task_map[key]
                            # Remove previous result for this host if any
                            existing_task.results = [
                                r
                                for r in existing_task.results
                                if r.hostname != hostname
                            ]
                            existing_task.results.append(
                                ParsedTaskResult(
                                    hostname=hostname,
                                    status=task_status,
                                    message=failure_msg,
                                )
                            )

                        i += 1
                    continue

                i += 1
                continue

            i += 1

        return list(task_map.values())

    def _extract_failure_message(
        self, lines: list[str], status_line_idx: int
    ) -> Optional[str]:
        """
        Extract failure message from a failed/fatal task result line.

        Handles two formats:
        1. Inline JSON: `failed: [host] => {"msg": "error message"}`
        2. Multiline JSON block following the status line

        Args:
            lines: All log lines
            status_line_idx: Index of the failed/fatal status line

        Returns:
            The failure message string, or None if not found
        """
        status_line = lines[status_line_idx]

        # Check for inline JSON: "=> { ... }" on the same line
        arrow_idx = status_line.find("=> {")
        if arrow_idx != -1:
            json_str = status_line[arrow_idx + 3 :].strip()
            msg = self._parse_msg_from_json(json_str)
            if msg:
                return msg

            # If single-line JSON didn't work, try multiline from this line
            json_lines = [status_line[arrow_idx + 3 :].strip()]
            for j in range(status_line_idx + 1, min(status_line_idx + 100, len(lines))):
                json_lines.append(lines[j].strip())
                if lines[j].strip() == "}":
                    break
            json_text = "\n".join(json_lines)
            msg = self._parse_msg_from_json(json_text)
            if msg:
                return msg

        # Check next line for "=> {" pattern (some formats put it on the next line)
        if status_line_idx + 1 < len(lines):
            next_line = lines[status_line_idx + 1].strip()
            if next_line.startswith("=> {"):
                json_lines = [next_line[3:].strip()]
                for j in range(
                    status_line_idx + 2, min(status_line_idx + 100, len(lines))
                ):
                    json_lines.append(lines[j].strip())
                    if lines[j].strip() == "}":
                        break
                json_text = "\n".join(json_lines)
                msg = self._parse_msg_from_json(json_text)
                if msg:
                    return msg

        # Fallback: try regex on nearby lines for "msg" field
        for j in range(status_line_idx, min(status_line_idx + 50, len(lines))):
            line = lines[j].strip()
            # Stop if we hit another task/play section
            if line.startswith("TASK [") or line.startswith("PLAY ["):
                break
            msg_match = re.search(r'"msg":\s*"((?:[^"\\]|\\.)*)"', line)
            if msg_match:
                return msg_match.group(1)

        return None

    def _parse_msg_from_json(self, json_str: str) -> Optional[str]:
        """
        Try to parse a JSON string and extract the 'msg' field.

        Args:
            json_str: JSON string (potentially malformed)

        Returns:
            The 'msg' value or None
        """
        try:
            data = json.loads(json_str)
            if isinstance(data, dict) and "msg" in data:
                msg = data["msg"]
                if isinstance(msg, list):
                    return "\n".join(str(item) for item in msg)
                return str(msg)
        except (json.JSONDecodeError, ValueError):
            pass
        return None


def determine_status(host: ParsedHost) -> str:
    """
    Determine the overall status for a host based on task counts.

    Args:
        host: ParsedHost with task counts

    Returns:
        'failed' if any failed/unreachable, 'changed' if any changed, else 'ok'
    """
    if host.failed > 0 or host.unreachable > 0:
        return "failed"
    if host.changed > 0:
        return "changed"
    return "ok"
