"""
Backward-compatibility wrapper.

FalGenerator is now Generator in lib.generator.
This module re-exports it under the old name so existing scripts
and agentic workflows continue to work unchanged.
"""

from .generator import Generator as FalGenerator
from .ffmpeg import extract_last_frame, concatenate_clips

__all__ = ["FalGenerator", "extract_last_frame", "concatenate_clips"]
