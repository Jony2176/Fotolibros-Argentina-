# FDF Stagehand Toolkit
# Implementación híbrida: Playwright (DOM) + Gemini Vision (diseño inteligente)
# + Pattern Cache (SQLite) + Stagehand v3 (self-healing)

from .fdf_stagehand_driver import FDFStagehandToolkit, get_fdf_stagehand_tools
from .vision_designer import VisionDesigner
from .design_intelligence import DesignIntelligence
from .pattern_cache import FDFPatternCache, get_pattern_cache
from .stagehand_wrapper import (
    FDFStagehandWrapper, 
    FDFStagehandActions, 
    stagehand_session, 
    STAGEHAND_AVAILABLE
)
from .error_handling import (
    # Logger
    FDFLogger,
    logger,
    # Exceptions
    FDFError,
    LoginError,
    NavigationError,
    UploadError,
    TemplateError,
    EditorError,
    VisionError,
    DragDropError,
    CheckoutError,
    TimeoutError,
    # Retry utilities
    retry_async,
    retry_sync,
    with_retry,
    # Fallbacks
    VisionFallback,
    # Recovery
    RecoveryStrategy,
    SafeOperation,
    # Utils
    health_check
)

__all__ = [
    # Main toolkit
    "FDFStagehandToolkit", 
    "get_fdf_stagehand_tools",
    "VisionDesigner",
    "DesignIntelligence",
    # Pattern Cache (SQLite)
    "FDFPatternCache",
    "get_pattern_cache",
    # Stagehand v3 (self-healing)
    "FDFStagehandWrapper",
    "FDFStagehandActions",
    "stagehand_session",
    "STAGEHAND_AVAILABLE",
    # Error handling
    "FDFLogger",
    "logger",
    "FDFError",
    "LoginError",
    "NavigationError",
    "UploadError",
    "TemplateError",
    "EditorError",
    "VisionError",
    "DragDropError",
    "CheckoutError",
    "TimeoutError",
    "retry_async",
    "retry_sync",
    "with_retry",
    "VisionFallback",
    "RecoveryStrategy",
    "SafeOperation",
    "health_check"
]
