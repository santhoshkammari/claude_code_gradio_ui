"""
Universal Logger - The Ultimate Logging Solution

A complete logging system that handles all data types, rich formatting,
rotatory files, AI conversations, and smart environment detection.
"""

import os
import sys
import json
import logging
import logging.handlers
from pathlib import Path
from typing import Union, List, Dict, Any, Optional
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.markdown import Markdown
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class UniversalLogger:
    """
    Universal Logger that handles all data types with rich formatting and smart rotation.
    
    Features:
    - Handles 4 data types: str, dict, List[str], List[dict]
    - Rich console formatting with panels and tables
    - Rotatory file logging with subdirectory support
    - AI conversation logging
    - Smart environment detection
    - Multiple log levels including custom ones
    """
    
    # Log levels with custom additions
    LEVELS = {
        'DEV': 5,        # Development-only
        'DEBUG': 10,     # Detailed diagnostic info
        'INFO': 20,      # General information
        'PROD': 25,      # Production-safe info
        'WARNING': 30,   # Something unexpected
        'ERROR': 40,     # Serious problem
        'AUDIT': 45,     # Security/compliance logs
        'CRITICAL': 50,  # Very serious error
    }
    
    def __init__(
        self,
        name: str = "universal",
        level: Optional[Union[str, int]] = None,
        enable_rich: bool = True,
        enable_files: bool = True,
        log_dir: str = "logs",
        subdir: Optional[str] = None,
        max_bytes: int = 10*1024*1024,  # 10MB
        backup_count: int = 5
    ):
        """
        Initialize Universal Logger
        
        Args:
            name: Logger name
            level: Log level (auto-detected if None)
            enable_rich: Enable rich console formatting
            enable_files: Enable file logging
            log_dir: Base log directory
            subdir: Subdirectory for this logger
            max_bytes: Max file size before rotation
            backup_count: Number of backup files to keep
        """
        self.name = name
        self.enable_rich = enable_rich and RICH_AVAILABLE
        self.enable_files = enable_files
        
        # Setup rich console if available
        if self.enable_rich:
            self.console = Console()
        
        # Determine log level
        if level is None:
            level = self._detect_environment_level()
        self.level = self._parse_level(level)
        
        # Setup file logging
        if self.enable_files:
            self._setup_file_logging(log_dir, subdir, max_bytes, backup_count)
        else:
            self.file_logger = None
    
    def _detect_environment_level(self) -> str:
        """Smart environment detection for log level"""
        if os.getenv('DEBUG') or os.getenv('DEV'):
            return "DEV"
        elif os.getenv('PRODUCTION') or os.getenv('PROD'):
            return "PROD"
        elif sys.stdout.isatty():
            return "DEBUG"
        else:
            return "INFO"
    
    def _parse_level(self, level: Union[str, int]) -> int:
        """Parse level string/int to numeric level"""
        if isinstance(level, str):
            return self.LEVELS.get(level.upper(), 20)
        return level
    
    def _setup_file_logging(self, log_dir: str, subdir: Optional[str], max_bytes: int, backup_count: int):
        """Setup file logging with rotation"""
        # Determine log path
        base_path = Path(log_dir)
        if subdir:
            log_path = base_path / subdir
        else:
            log_path = base_path
        
        # Create directories
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Setup file logger
        log_file = log_path / f"{self.name}.log"
        self.file_logger = logging.getLogger(f"file_{self.name}")
        self.file_logger.setLevel(logging.DEBUG)  # File gets everything
        self.file_logger.propagate = False  # Don't propagate to root logger (prevents console output)

        # Remove existing handlers
        self.file_logger.handlers.clear()

        # Add rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )

        # JSON formatter for structured logging
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": %(message)s}'
        )
        file_handler.setFormatter(formatter)
        self.file_logger.addHandler(file_handler)
    
    def set_level(self, level: Union[str, int]):
        """Change log level dynamically"""
        self.level = self._parse_level(level)
    
    def _should_log(self, level: str) -> bool:
        """Check if message should be logged based on level"""
        return self.LEVELS.get(level.upper(), 20) >= self.level
    
    def _format_data(self, data: Any, method_type: str = "standard") -> tuple:
        """
        Universal data formatter that handles all 4 types
        Returns (console_output, file_output)
        """
        if isinstance(data, str):
            return self._format_string(data, method_type)
        elif isinstance(data, dict):
            return self._format_dict(data, method_type)
        elif isinstance(data, list):
            if all(isinstance(item, str) for item in data):
                return self._format_list_of_strings(data, method_type)
            elif all(isinstance(item, dict) for item in data):
                return self._format_list_of_dicts(data, method_type)
            else:
                return self._format_mixed_list(data, method_type)
        else:
            # Fallback for other types
            str_data = str(data)
            return str_data, str_data
    
    def _format_string(self, data: str, method_type: str) -> tuple:
        """Format string data"""
        if method_type == "rich" and self.enable_rich:
            # Check if markdown
            if any(char in data for char in ['*', '_', '`', '#']):
                rich_content = Markdown(data)
            else:
                rich_content = Text(data)
            return rich_content, data
        return data, data
    
    def _format_dict(self, data: dict, method_type: str) -> tuple:
        """Format dictionary data"""
        # File output - JSON
        file_output = json.dumps(data, ensure_ascii=False, indent=None)
        
        if method_type == "rich" and self.enable_rich:
            # Rich panel for console
            content = ""
            for key, value in data.items():
                content += f"[bold]{key}[/bold] : {value}\n"
            rich_content = content.strip()
            return rich_content, file_output
        else:
            # Simple key=value format for console
            console_output = " ".join([f"{k}={v}" for k, v in data.items()])
            return console_output, file_output
    
    def _format_list_of_strings(self, data: List[str], method_type: str) -> tuple:
        """Format list of strings"""
        if method_type == "rich" and self.enable_rich:
            content = "\n".join([f"• {item}" for item in data])
            return content, json.dumps(data)
        else:
            content = "\n  ".join([f"• {item}" for item in data])
            return content, json.dumps(data)
    
    def _format_list_of_dicts(self, data: List[dict], method_type: str) -> tuple:
        """Format list of dictionaries"""
        file_output = json.dumps(data, ensure_ascii=False, indent=None)
        
        if not data:
            return "Empty data", file_output
        
        if method_type == "rich" and self.enable_rich:
            # Will be handled by rich table in output
            return data, file_output
        else:
            # Simple table format
            headers = list(data[0].keys())
            console_output = " | ".join(headers) + "\n"
            console_output += "-" * len(console_output) + "\n"
            for row in data:
                console_output += " | ".join([str(row.get(h, "")) for h in headers]) + "\n"
            return console_output.strip(), file_output
    
    def _format_mixed_list(self, data: list, method_type: str) -> tuple:
        """Handle mixed type lists"""
        items = []
        for item in data:
            if isinstance(item, dict):
                items.append(json.dumps(item))
            else:
                items.append(str(item))
        return self._format_list_of_strings(items, method_type)
    
    def _get_level_color(self, level: str) -> str:
        """Get rich color for level"""
        colors = {
            'DEV': 'dim white',
            'DEBUG': 'blue',
            'INFO': 'green',
            'PROD': 'bright_green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bright_red',
            'AUDIT': 'magenta'
        }
        return colors.get(level.upper(), 'white')
    
    def _get_level_style(self, level: str) -> str:
        """Get rich text style for level"""
        styles = {
            'DEV': 'dim',
            'DEBUG': 'blue',
            'INFO': 'green',
            'PROD': 'bright_green',
            'ERROR': 'bold red',
            'CRITICAL': 'bold bright_red'
        }
        return styles.get(level.upper(), 'white')
    
    def _log(self, data: Any, level: str, method_type: str = "standard"):
        """Internal logging method"""
        if not self._should_log(level):
            return
        
        console_output, file_output = self._format_data(data, method_type)
        
        # Console output
        if method_type == "rich" and self.enable_rich:
            self._rich_console_output(console_output, level, data)
        else:
            self._standard_console_output(console_output, level)
        
        # File output
        if self.file_logger:
            self._file_output(file_output, level)
    
    def _standard_console_output(self, output: str, level: str):
        """Standard console output"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {output}")
    
    def _rich_console_output(self, output: Any, level: str, original_data: Any):
        """Rich console output with panels and tables"""
        if not self.enable_rich:
            return self._standard_console_output(str(output), level)
        
        title = f"[{level}]"
        
        if isinstance(original_data, list) and original_data and isinstance(original_data[0], dict):
            # Create rich table for list of dicts
            table = Table(title=f"{title} Data")
            
            # Add columns
            headers = list(original_data[0].keys())
            for header in headers:
                table.add_column(str(header), style="cyan")
            
            # Add rows
            for row_dict in original_data:
                row_values = [str(row_dict.get(key, "")) for key in headers]
                table.add_row(*row_values)
            
            self.console.print(table)
        else:
            # Create panel for other types
            panel = Panel(
                output,
                title=title,
                border_style=self._get_level_color(level)
            )
            self.console.print(panel)
    
    def _file_output(self, output: str, level: str):
        """Output to file"""
        # Escape quotes for JSON logging
        escaped_output = output.replace('"', '\\"').replace('\n', '\\n')
        self.file_logger.log(
            getattr(logging, level.upper(), logging.INFO),
            f'"{escaped_output}"'
        )
    
    # Standard logging methods
    def dev(self, data: Any):
        """Development-only logging"""
        self._log(data, "DEV")
    
    def debug(self, data: Any):
        """Debug level logging"""
        self._log(data, "DEBUG")
    
    def info(self, data: Any):
        """Info level logging"""
        self._log(data, "INFO")
    
    def prod(self, data: Any):
        """Production-safe logging"""
        self._log(data, "PROD")
    
    def warning(self, data: Any):
        """Warning level logging"""
        self._log(data, "WARNING")
    
    def error(self, data: Any):
        """Error level logging"""
        self._log(data, "ERROR")
    
    def audit(self, data: Any):
        """Audit level logging"""
        self._log(data, "AUDIT")
    
    def critical(self, data: Any):
        """Critical level logging"""
        self._log(data, "CRITICAL")
    
    # Special methods
    def rich(self, data: Any, level: str = "INFO"):
        """Rich formatted output with panels and tables"""
        if self._should_log(level):
            self._log(data, level, "rich")
    
    def ai(self, data: Union[List[dict], dict, str], role: str = "user", level: str = "INFO"):
        """
        AI conversation logging with rich panels
        
        Handles:
        - List[dict] with role/content format
        - Single dict message
        - String message with optional role (defaults to "user")
        
        Args:
            data: Message data (string, dict, or list of dicts)
            role: Default role for string messages ("user", "assistant", "system")
            level: Log level
        """
        if not self._should_log(level):
            return
        
        if isinstance(data, str):
            # Simple string message with specified role
            messages = [{"role": role, "content": data}]
        elif isinstance(data, dict):
            # Single message dict
            messages = [data]
        elif isinstance(data, list):
            # List of messages
            messages = data
        else:
            # Fallback
            self._log(data, level, "rich")
            return
        
        # Rich conversation output
        if self.enable_rich:
            for msg in messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", str(msg))
                
                # Role-based styling
                if role == "user":
                    style = "blue"
                    icon = "👤"
                elif role == "assistant":
                    style = "green" 
                    icon = "🤖"
                elif role == "system":
                    style = "yellow"
                    icon = "⚙️"
                else:
                    style = "white"
                    icon = "💬"
                
                panel = Panel(
                    content,
                    title=f"{role.title()}",
                    border_style=style
                )
                self.console.print(panel)
        else:
            # Standard output for AI conversations
            for msg in messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", str(msg))
                self._standard_console_output(f"[{role.upper()}] {content}", level)
        
        # File output
        if self.file_logger:
            self._file_output(json.dumps(messages), level)


# Convenience function for quick setup
def get_logger(
    name: str = "logs",
    level: Optional[str] = None,
    enable_rich: bool = True,
    enable_files: bool = True,
    subdir: Optional[str] = None
) -> UniversalLogger:
    """
    Quick logger setup function
    
    Usage:
        log = get_logger("my_app", enable_rich=True, subdir="ai_logs")
    """
    return UniversalLogger(
        name=name,
        level=level,
        enable_rich=enable_rich,
        enable_files=enable_files,
        subdir=subdir
    )


# Example usage and testing
if __name__ == "__main__":
    # Test the logger
    log = UniversalLogger("test", level="DEBUG")
    
    print("=== Testing Universal Logger ===\n")
    
    # Test all data types with different levels
    log.info("Simple string message")
    log.info({"user": "alice", "action": "login", "ip": "192.168.1.1"})
    log.info(["Starting pipeline", "Loading model", "Processing data"])
    log.info([
        {"step": 1, "action": "validate", "status": "✅"},
        {"step": 2, "action": "process", "status": "⏳"},
        {"step": 3, "action": "save", "status": "⏳"}
    ])
    
    # Test rich formatting
    print("\n=== Rich Formatting ===")
    log.rich("**Bold** and *italic* markdown text")
    log.rich({"model": "gpt-4", "tokens": 150, "cost": 0.03})
    log.rich(["Task 1", "Task 2", "Task 3"])
    log.rich([{"name": "Alice", "score": 95}, {"name": "Bob", "score": 87}])
    
    # Test AI conversations
    print("\n=== AI Conversations ===")
    log.ai([
        {"role": "user", "content": "What's the weather like?"},
        {"role": "assistant", "content": "I'll check the current weather for you."},
        {"role": "system", "content": "Weather API called successfully"}
    ])
    
    # Test different levels
    print("\n=== Different Levels ===")
    log.dev("Development debug info")
    log.debug("Debug information")
    log.prod("Production-safe message")
    log.warning("Warning message")
    log.error("Error occurred")
    
    print("\n=== Logger test complete ===")
