# logutils

A Python library for creating and managing advanced logging configurations with support for multiple handlers, custom filters, and flexible configuration options.

## Features

- Built ontop of Python standard `logging` module
- Create loggers from configuration dictionaries
- Support for multiple logging handlers (File, Stream, Rotating, Timed, Socket, Syslog, etc.)
- Custom OR filter for selective logging based on logger names
- Automatic handler cleanup and logger management
- Flexible configuration with sensible defaults

## Installation

You can install directly from source:

```bash
pip install git+https://github.com/Ekerim/logutils.git
```

## Usage

### Basic Example

```python
from logutils import create_logger, close_logger

# Basic logger configuration
config = {
    "name": "my_app",
    "level": "INFO",
    "handlers": [
        {
            "type": "StreamHandler",
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    ]
}

# Create the logger
logger = create_logger(config)
logger.info("Hello, world!")

# Clean up when done
close_logger(logger)
```

### File Logging with Rotation

```python
import tempfile
import os

config = {
    "name": "file_logger",
    "level": "DEBUG",
    "handlers": [
        {
            "type": "RotatingFileHandler",
            "path": "/tmp",
            "filename": "app.log",
            "level": "DEBUG",
            "handler_kwargs": {
                "maxBytes": 1024*1024,  # 1MB
                "backupCount": 5
            },
            "format": "%(asctime)s - %(name)s - %(funcName)s [%(levelname)s]: %(message)s"
        }
    ]
}

logger = create_logger(config)
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
```

### Multiple Handlers with Filters

```python
config = {
    "name": "multi_handler_logger",
    "level": "DEBUG",
    "propagate": False,
    "handlers": [
        {
            "type": "StreamHandler",
            "level": "INFO",
            "format": "%(levelname)s: %(message)s"
        },
        {
            "type": "FileHandler",
            "path": "/tmp",
            "filename": "debug.log",
            "level": "DEBUG",
            "filters": ["my_app", "my_module"],  # Only log messages from these modules
            "format": "%(asctime)s - %(name)s - %(funcName)s [%(levelname)s]: %(message)s"
        }
    ]
}

logger = create_logger(config)
```

## Configuration Reference

### Logger Configuration

- `name` (str): Logger name (default: random UUID)
- `level` (str): Logging level (default: "DEBUG")
- `enabled` (bool): Whether logger is enabled (default: True)
- `propagate` (bool): Whether to propagate to parent loggers (default: False)
- `format` (str): Default message format
- `handlers` (list): List of handler configurations

### Handler Configuration

- `type` (str): Handler type (required)
- `level` (str): Handler logging level (default: "DEBUG")
- `enabled` (bool): Whether handler is enabled (default: True)
- `format` (str): Message format for this handler
- `filters` (list): List of logger name prefixes to filter
- `path` (str): File path (for file-based handlers)
- `filename` (str): Log filename (default: random UUID + .log)
- `args` (list): Positional arguments for handler constructor
- `handler_kwargs` (dict): Keyword arguments for handler constructor
- `proto` (str): Protocol for SysLogHandler ("TCP" or "UDP")

### Supported Handler Types

- `StreamHandler`: Console output
- `FileHandler`: Basic file logging
- `WatchedFileHandler`: File logging with external rotation support
- `RotatingFileHandler`: Size-based log rotation
- `TimedRotatingFileHandler`: Time-based log rotation
- `SocketHandler`: TCP socket logging
- `DatagramHandler`: UDP socket logging
- `SysLogHandler`: Syslog server logging
- `NTEventLogHandler`: Windows Event Log (Windows only)
- `SMTPHandler`: Email notifications

## API Reference

### Functions

- `create_logger(linfo, logger_object=None)`: Create a logger from configuration
- `close_logger(logger_object)`: Clean up logger and close all handlers

### Constants

- `LOG_LEVELS`: Dictionary mapping level names to numeric values

### Custom Filters

The library includes an `OrFilter` class that allows filtering based on logger name prefixes. When specified in the `filters` list of a handler configuration, only log messages from loggers whose names start with any of the specified prefixes will be processed.

## License

This project is licensed under the GNU Lesser General Public License v3 (LGPLv3). See the [LICENSE](./LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## Contact

For questions or support, please contact [ekerim@gmail.com](mailto:ekerim@gmail.com).
