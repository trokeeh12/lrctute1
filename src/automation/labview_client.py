"""LabVIEW Automation Client via COM/ActiveX interface.

Provides programmatic control over NI LabVIEW for:
- Starting/Attaching to LabVIEW
- Opening, inspecting, and closing VIs (.vi)
- Setting Front Panel control values (inputs)
- Running VIs with timeout and completion monitoring
- Reading Front Panel indicator values (outputs)
- Exporting Front Panel images for agent visual verification
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

# Ensure win32com is available
try:
    import win32com.client
    import pythoncom
except ImportError:
    win32com = None  # type: ignore
    pythoncom = None  # type: ignore

# Setup logging
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "labview_automation.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("LabVIEWClient")

DEFAULT_LABVIEW_EXE = r"C:\Program Files (x86)\National Instruments\LabVIEW 2025\LabVIEW.exe"
DEFAULT_LABVIEW_CLI = r"C:\Program Files (x86)\National Instruments\Shared\LabVIEW CLI\LabVIEWCLI.exe"


class LabVIEWError(Exception):
    """Custom exception for LabVIEW automation errors."""
    pass


class LabVIEWClient:
    """Automates NI LabVIEW via Windows ActiveX/COM."""

    def __init__(self, labview_exe: str = DEFAULT_LABVIEW_EXE) -> None:
        self.labview_exe = labview_exe
        self._app: Optional[Any] = None

    @staticmethod
    def is_process_running() -> bool:
        """Check if LabVIEW.exe is currently running in Windows."""
        try:
            output = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", "Get-Process -Name 'LabVIEW' -ErrorAction SilentlyContinue"],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            return "LabVIEW" in output
        except Exception:
            return False

    def connect(self, start_if_not_running: bool = True) -> Any:
        """Connect to running LabVIEW instance or launch it."""
        if win32com is None:
            raise LabVIEWError("pywin32 is not installed. Run 'pip install pywin32' in .venv.")

        is_running = self.is_process_running()
        logger.info(f"Checking LabVIEW process: {'Running' if is_running else 'Not Running'}")

        if not is_running and not start_if_not_running:
            raise LabVIEWError("LabVIEW is not running and start_if_not_running is False.")

        try:
            logger.info("Connecting to LabVIEW.Application via COM...")
            self._app = win32com.client.Dispatch("LabVIEW.Application")
            version = getattr(self._app, "Version", "Unknown")
            app_dir = getattr(self._app, "ApplicationDirectory", "Unknown")
            logger.info(f"Connected successfully to LabVIEW version: {version} at {app_dir}")
            return self._app
        except Exception as e:
            logger.error(f"Failed to connect to LabVIEW: {e}")
            raise LabVIEWError(f"COM connection error: {e}") from e

    @property
    def app(self) -> Any:
        """Get the active LabVIEW COM Application object."""
        if self._app is None:
            return self.connect()
        return self._app

    def open_vi(self, vi_path: str | Path) -> Any:
        """Open a Virtual Instrument (.vi) file and return its VI COM reference."""
        resolved_path = Path(vi_path).resolve()
        if not resolved_path.exists():
            raise FileNotFoundError(f"VI file not found: {resolved_path}")

        app = self.app
        try:
            logger.info(f"Loading VI: {resolved_path}")
            # GetVIReference(VIPath, Password="", Reserving=False)
            vi = app.GetVIReference(str(resolved_path), "", False)
            return vi
        except Exception as e:
            logger.error(f"Error opening VI {resolved_path}: {e}")
            raise LabVIEWError(f"Failed to open VI: {e}") from e

    def run_vi(
        self,
        vi_path: str | Path,
        inputs: Optional[Dict[str, Any]] = None,
        output_indicators: Optional[list[str]] = None,
        timeout_seconds: float = 30.0,
        show_front_panel: bool = False,
    ) -> Dict[str, Any]:
        """Run a VI with provided control inputs and retrieve indicator outputs.

        Args:
            vi_path: Absolute or relative path to the .vi file.
            inputs: Dictionary mapping control names to values to set before running.
            output_indicators: List of indicator names to retrieve after execution.
            timeout_seconds: Maximum execution time in seconds.
            show_front_panel: Whether to display the front panel window during run.

        Returns:
            Dictionary containing execution status, elapsed time, and output values.
        """
        vi = self.open_vi(vi_path)
        start_time = time.time()
        results: Dict[str, Any] = {
            "status": "pending",
            "vi_path": str(Path(vi_path).resolve()),
            "inputs": inputs or {},
            "outputs": {},
            "elapsed_seconds": 0.0,
        }

        try:
            if show_front_panel:
                try:
                    vi.OpenFrontPanel()
                except Exception as e:
                    logger.warning(f"Could not open Front Panel: {e}")

            # 1. Set input controls
            if inputs:
                for name, value in inputs.items():
                    logger.info(f"Setting control '{name}' = {value}")
                    try:
                        vi.SetControlValue(name, value)
                    except Exception as e:
                        logger.warning(f"Failed to set control '{name}': {e}")

            # 2. Run the VI
            logger.info("Executing VI (WaitUntilDone=True)...")
            # vi.Run(WaitUntilDone=True)
            vi.Run(True)

            elapsed = time.time() - start_time
            results["elapsed_seconds"] = round(elapsed, 3)
            logger.info(f"VI execution finished in {results['elapsed_seconds']}s")

            # 3. Read output indicators
            if output_indicators:
                for ind_name in output_indicators:
                    try:
                        val = vi.GetControlValue(ind_name)
                        results["outputs"][ind_name] = val
                        logger.info(f"Read indicator '{ind_name}' = {val}")
                    except Exception as e:
                        logger.warning(f"Failed to read indicator '{ind_name}': {e}")
                        results["outputs"][ind_name] = None

            results["status"] = "success"
            return results

        except Exception as e:
            elapsed = time.time() - start_time
            results["elapsed_seconds"] = round(elapsed, 3)
            results["status"] = "error"
            results["error_message"] = str(e)
            logger.error(f"VI execution failed: {e}")
            raise LabVIEWError(f"Execution error on {vi_path}: {e}") from e

        finally:
            try:
                # Close VI reference to free memory
                vi.Close()
            except Exception:
                pass

    def export_vi_image(self, vi_path: str | Path, output_image_path: str | Path) -> str:
        """Export an image of the VI's Front Panel for visual inspection."""
        vi = self.open_vi(vi_path)
        out_path = Path(output_image_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # LabVIEW COM method: ExportImage(FileName, ImageFormat, Quality)
            # ImageFormat: 1=BMP, 2=PICT, 3=JPEG, 4=PNG
            logger.info(f"Exporting VI Front Panel image to {out_path}...")
            vi.ExportImage(str(out_path), 4, 100)
            return str(out_path)
        except Exception as e:
            logger.warning(f"ExportImage not supported directly: {e}")
            raise
        finally:
            try:
                vi.Close()
            except Exception:
                pass


def main() -> None:
    """CLI entrypoint for testing LabVIEW connection."""
    import argparse

    parser = argparse.ArgumentParser(description="Antigravity LabVIEW Automation Bridge")
    parser.add_argument("--status", action="store_true", help="Check LabVIEW status and version")
    parser.add_argument("--run-vi", type=str, help="Path to .vi file to execute")
    args = parser.parse_args()

    client = LabVIEWClient()

    if args.status or len(sys.argv) == 1:
        is_running = client.is_process_running()
        print(f"[LabVIEW Status] Process running: {is_running}")
        print(f"[LabVIEW Executable] {DEFAULT_LABVIEW_EXE}")
        print(f"[LabVIEW CLI] {DEFAULT_LABVIEW_CLI}")
        if is_running:
            try:
                app = client.connect(start_if_not_running=False)
                print(f"[LabVIEW COM] Version: {app.Version}")
            except Exception as e:
                print(f"[LabVIEW COM] Error: {e}")
        else:
            print("[LabVIEW COM] Not attached (process is currently idle)")

    if args.run_vi:
        res = client.run_vi(args.run_vi)
        print(f"[Run Result] {res}")


if __name__ == "__main__":
    main()
