import contextvars

from .agent import (
    LM,gen, step, agent,
    AssistantResponse, ToolCall, StepResult, ToolResult
)
from .eval import (
    eval_example, eval_stream, eval_batch,
    EvalResult
)

# Exports
__all__ = [
    'LM',
    'gen', 'step', 'agent',
    'AssistantResponse', 'ToolCall', 'StepResult', 'ToolResult',
    'eval_example', 'eval_stream', 'eval_batch',
    'EvalResult',
    'configure', 'get_lm'
]

# Global LM context
_current_lm = contextvars.ContextVar('lm', default=None)

def configure(lm=None, **kwargs):
    """Configure the framework with default LM and other settings."""
    if lm:
        _current_lm.set(lm)

def get_lm():
    """Get the current LM from context."""
    return _current_lm.get()

# Keep set_lm internal/private
def _set_lm(lm):
    """Internal: Set the default LM for all modules in this context."""
    _current_lm.set(lm)
