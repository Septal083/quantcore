"""Polar.sh license validation for QuantCore Pro features."""

from __future__ import annotations

import json
import os
import uuid
from functools import lru_cache
from typing import Optional
from urllib import request, error as urllib_error

POLAR_VALIDATE_URL = "https://api.polar.sh/v1/licenses/validate"
POLAR_ORG_ID = "1f3ada33-0e12-48b8-8efe-79e00d29e5e0"
PRO_UNLOCK_MESSAGE = "\U0001f512 Pro feature \u2014 unlock at https://buy.polar.sh/polar_cl_rA97pLblKd1pRhwXezgssGgCp1NaKlDV0CeG74fP4q4"


@lru_cache(maxsize=1)
def validate_license(license_key: Optional[str] = None) -> bool:
    """Validate a Polar.sh license key.

    Checks the ``QUANTCORE_LICENSE_KEY`` environment variable if no key is
    provided directly.

    Returns
    -------
    bool
        True if the license is valid, False otherwise.
    """
    key = license_key or os.environ.get("QUANTCORE_LICENSE_KEY", "")
    if not key:
        return False

    machine_id = str(uuid.getnode())
    payload = json.dumps({
        "key": key,
        "organization_id": POLAR_ORG_ID,
        "benefit_id": "quantcore-pro",
        "machine_id": machine_id,
    }).encode("utf-8")

    req = request.Request(
        POLAR_VALIDATE_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("valid", False)
    except (urllib_error.URLError, json.JSONDecodeError, OSError):
        return False


def require_pro(license_key: Optional[str] = None) -> bool:
    """Check for a valid Pro license. Prints unlock message if invalid.

    Returns
    -------
    bool
        True if licensed, False otherwise.
    """
    if validate_license(license_key):
        return True
    print(PRO_UNLOCK_MESSAGE)
    return False
