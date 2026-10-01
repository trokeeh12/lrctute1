"""LabVIEW CLI Wrapper.

Executes operations using National Instruments LabVIEWCLI.exe.
Useful for CI/CD, headless batch execution, and command-line automation.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("LabVIEWCLI")

LABVIEW_CLI_PATH = r"C:\Program Files (x86)\National Instruments\Shared\LabVIEW CLI\LabVIEWCLI.exe"
LABVIEW_EXE_PATH = r"C:\Program Files (x86)\National Instruments\LabVIEW 2025\LabVIEW.exe"


class LabVIEWCLI:
    """Wrapper around LabVIEWCLI.exe."""

    def __init__(
        self,
        cli_path: str = LABVIEW_CLI_PATH,
        labview_path: str = LABVIEW_EXE_PATH,
    ) -> None:
        self.cli_path = cli_path
        self.labview_path = labview_path

    def run_vi(
        self,
        vi_path: str | Path,
        additional_args: Optional[List[str]] = None,
        timeout_seconds: int = 60,
    ) -> Dict[str, str | int]:
        """Run a VI via LabVIEWCLI -OperationName RunVI."""
        resolved_vi = Path(vi_path).resolve()
        if not resolved_vi.exists():
            raise FileNotFoundError(f"VI not found: {resolved_vi}")

        cmd = [
            self.cli_path,
            "-OperationName", "RunVI",
            "-LabVIEWPath", self.labview_path,
            "-VIPath", str(resolved_vi),
        ]
        if additional_args:
            cmd.extend(additional_args)

        logger.info(f"Running LabVIEW CLI command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )

        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    def close_labview(self) -> int:
        """Close running LabVIEW instance gracefully via CLI."""
        cmd = [
            self.cli_path,
            "-OperationName", "CloseLabVIEW",
            "-LabVIEWPath", self.labview_path,
        ]
        logger.info("Closing LabVIEW via CLI...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode
