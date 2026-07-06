"""CLAIRO shared library.

Provides domain models, repositories, audit logging, configuration access, and
authentication/authorization helpers shared across all CLAIRO units.

Error handling convention: fallible functions return a ``(value, error)`` tuple.
See ``clairo_shared.result`` and ``clairo_shared.errors``.
"""

__version__ = "0.1.0"
