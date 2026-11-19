"""
vCon ElevenLabs Adapter

Convert ElevenLabs agent interactions to standardized vCon format
and export to multiple backends (file, S3, webhook).
"""

__version__ = "1.0.0"
__author__ = "Thomas Howe"

from .adapter import ElevenLabsVconAdapter

__all__ = ["ElevenLabsVconAdapter"]
