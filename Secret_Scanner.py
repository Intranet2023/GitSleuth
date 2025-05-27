"""Utility functions for secret detection."""

import json
import logging
import os
import subprocess
import tempfile
from typing import Optional


def snippet_has_secret(snippet: str, baseline_file: Optional[str] = None) -> bool:
    """Return True if detect-secrets finds a secret in the snippet.

    The function uses the ``detect-secrets`` CLI so that the optional
    dependency is only required when secret scanning is enabled.

    Parameters
    ----------
    snippet : str
        The text snippet to scan.
    baseline_file : str, optional
        Path to a ``detect-secrets`` baseline file to apply allowlisting.
    """
    try:
        with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
            tmp.write(snippet)
            tmp_path = tmp.name

        cmd = ["detect-secrets", "scan", tmp_path, "--json"]
        if baseline_file:
            cmd.extend(["--baseline", baseline_file])
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logging.debug("detect-secrets exited with code %s", result.returncode)
            return True
        data = json.loads(result.stdout or "{}")
        findings = data.get("results", {}).get(tmp_path, [])
        return bool(findings)
    except FileNotFoundError:
        logging.debug("detect-secrets command not available")
        return True
    except Exception as exc:
        logging.debug("detect-secrets scanning failed: %s", exc)
        return True
    finally:
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
