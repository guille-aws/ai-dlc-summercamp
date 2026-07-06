"""Config Provider: runtime configuration from SSM Parameter Store.

No caching (NFR requirements Q3:B) — reads SSM on every call, always fresh.
Injectable SSM client. Returns result tuples.
"""

from __future__ import annotations

import os
from typing import Optional

import boto3

from .errors import StorageError, ValidationError
from .result import Result, err, ok

_DEFAULT_THRESHOLD_PARAM = "/clairo/dev/confidence_threshold"
_DEFAULT_GDPR_PARAM = "/clairo/dev/gdpr_rules_ref"


class ConfigProvider:
    def __init__(
        self,
        threshold_param: Optional[str] = None,
        gdpr_rules_param: Optional[str] = None,
        ssm_client=None,
    ):
        self._threshold_param = threshold_param or os.environ.get(
            "THRESHOLD_PARAM", _DEFAULT_THRESHOLD_PARAM
        )
        self._gdpr_param = gdpr_rules_param or os.environ.get(
            "GDPR_RULES_PARAM", _DEFAULT_GDPR_PARAM
        )
        self._ssm = ssm_client or boto3.client("ssm")

    def get_threshold(self) -> Result:
        """Return the global confidence threshold as a float (US-10)."""
        value, error = self._get_param(self._threshold_param)
        if error:
            return err(error)
        try:
            return ok(float(value))
        except (TypeError, ValueError):
            return err(ValidationError(f"Invalid threshold value: {value!r}"))

    def get_gdpr_rules_ref(self) -> Result:
        """Return the pointer to the externalized GDPR rules."""
        return self._get_param(self._gdpr_param)

    def set_threshold(self, value: float) -> Result:
        """Update the confidence threshold (Supervisor only, enforced by caller)."""
        if not 0.0 <= value <= 1.0:
            return err(ValidationError("Threshold must be between 0.0 and 1.0"))
        try:
            self._ssm.put_parameter(
                Name=self._threshold_param,
                Value=str(value),
                Type="String",
                Overwrite=True,
            )
        except Exception as exc:
            return err(StorageError(f"Failed to set threshold: {exc}"))
        return ok(value)

    def _get_param(self, name: str) -> Result:
        try:
            response = self._ssm.get_parameter(Name=name)
            return ok(response["Parameter"]["Value"])
        except Exception as exc:
            return err(StorageError(f"Failed to read parameter {name}: {exc}"))
