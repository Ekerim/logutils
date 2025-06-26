# Copyright (c) 2025 Fredrik Larsson
# 
# This file is part of the logutils library.
# 
# The logutils library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# The logutils library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this library. If not, see <https://www.gnu.org/licenses/>.

import unittest
import tempfile
import os
import logging
import io
import sys

# Import the functions we want to test
from logutils import create_logger, close_logger, LOG_LEVELS
from logutils.filters.OrFilter import OrFilter


class TestLogUtils(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.created_loggers = []

    def tearDown(self):
        """Clean up any loggers created during tests."""
        # Clean up any loggers created during tests
        for logger in self.created_loggers:
            if logger:
                close_logger(logger)

    def track_logger(self, logger):
        """Helper to track loggers for cleanup."""
        if logger:
            self.created_loggers.append(logger)
        return logger

    def test_log_levels_constant(self):
        """Test that LOG_LEVELS constant is properly defined."""
        expected_levels = {
            "CRITICAL": 50,
            "ERROR": 40,
            "WARNING": 30,
            "INFO": 20,
            "DEBUG": 10,
            "NOTSET": 0
        }
        self.assertEqual(LOG_LEVELS, expected_levels)

    def test_create_logger_basic(self):
        """Test basic logger creation with minimal configuration."""
        config = {
            "name": "test_logger",
            "level": "INFO",
            "handlers": [
                {
                    "type": "StreamHandler",
                    "level": "INFO"
                }
            ]
        }
        
        logger = self.track_logger(create_logger(config))
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "test_logger")
        self.assertEqual(logger.level, logging.INFO)
        self.assertEqual(len(logger.handlers), 1)
        self.assertIsInstance(logger.handlers[0], logging.StreamHandler)

    def test_create_logger_disabled(self):
        """Test that disabled logger returns None."""
        config = {
            "enabled": False,
            "name": "disabled_logger"
        }
        
        logger = create_logger(config)
        self.assertIsNone(logger)

    def test_create_logger_disabled_with_existing_logger(self):
        """Test that disabled logger returns existing logger if provided."""
        existing_logger = logging.getLogger("existing")
        config = {
            "enabled": False,
            "name": "disabled_logger"
        }
        
        logger = create_logger(config, existing_logger)
        self.assertEqual(logger, existing_logger)

    def test_create_logger_with_existing_logger_object(self):
        """Test creating logger with existing logger object."""
        existing_logger = logging.getLogger("existing")
        config = {
            "name": "test_logger",
            "level": "DEBUG"
        }
        
        logger = self.track_logger(create_logger(config, existing_logger))
        self.assertEqual(logger, existing_logger)
        self.assertEqual(logger.level, logging.DEBUG)

    def test_create_logger_uuid_fallback_name(self):
        """Test that logger gets UUID name when no name provided."""
        config = {
            "level": "INFO",
            "handlers": [{"type": "StreamHandler"}]
        }
        
        logger = self.track_logger(create_logger(config))
        self.assertIsNotNone(logger)
        # UUID names are 32 character hex strings
        self.assertEqual(len(logger.name), 32)
        self.assertTrue(all(c in '0123456789abcdef' for c in logger.name))

    def test_create_logger_file_handler(self):
        """Test FileHandler creation with valid path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "name": "file_logger",
                "handlers": [
                    {
                        "type": "FileHandler",
                        "path": temp_dir,
                        "filename": "test.log",
                        "level": "DEBUG"
                    }
                ]
            }
            
            logger = self.track_logger(create_logger(config))
            self.assertIsNotNone(logger)
            self.assertEqual(len(logger.handlers), 1)
            self.assertIsInstance(logger.handlers[0], logging.FileHandler)
            
            # Test that file is created
            log_file = os.path.join(temp_dir, "test.log")
            logger.info("Test message")
            self.assertTrue(os.path.exists(log_file))

    def test_create_logger_file_handler_invalid_path(self):
        """Test FileHandler with invalid path raises RuntimeError."""
        config = {
            "name": "file_logger",
            "handlers": [
                {
                    "type": "FileHandler",
                    "path": "/nonexistent/path",
                    "filename": "test.log"
                }
            ]
        }
        
        with self.assertRaises(RuntimeError) as context:
            create_logger(config)
        
        self.assertIn("doesn't exist", str(context.exception))

    def test_create_logger_rotating_file_handler(self):
        """Test RotatingFileHandler creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "name": "rotating_logger",
                "handlers": [
                    {
                        "type": "RotatingFileHandler",
                        "path": temp_dir,
                        "filename": "rotating.log",
                        "handler_kwargs": {
                            "maxBytes": 1024,
                            "backupCount": 3
                        }
                    }
                ]
            }
            
            logger = self.track_logger(create_logger(config))
            self.assertIsNotNone(logger)
            self.assertEqual(len(logger.handlers), 1)
            # Check it's a RotatingFileHandler
            handler = logger.handlers[0]
            self.assertEqual(handler.__class__.__name__, "RotatingFileHandler")

    def test_create_logger_with_filters(self):
        """Test logger creation with OrFilter."""
        config = {
            "name": "filtered_logger",
            "handlers": [
                {
                    "type": "StreamHandler",
                    "filters": ["myapp", "mymodule"]
                }
            ]
        }
        
        logger = self.track_logger(create_logger(config))
        self.assertIsNotNone(logger)
        handler = logger.handlers[0]
        self.assertEqual(len(handler.filters), 1)
        self.assertIsInstance(handler.filters[0], OrFilter)

    def test_create_logger_disabled_handler(self):
        """Test that disabled handlers are skipped."""
        config = {
            "name": "test_logger",
            "handlers": [
                {
                    "type": "StreamHandler",
                    "enabled": False
                },
                {
                    "type": "StreamHandler",
                    "enabled": True
                }
            ]
        }
        
        logger = self.track_logger(create_logger(config))
        self.assertEqual(len(logger.handlers), 1)

    def test_create_logger_invalid_handler_type(self):
        """Test that invalid handler types are skipped."""
        config = {
            "name": "test_logger",
            "handlers": [
                {
                    "type": "InvalidHandler"
                },
                {
                    "type": "StreamHandler"
                }
            ]
        }
        
        logger = self.track_logger(create_logger(config))
        
        # Should still create the valid handler and skip the invalid one
        self.assertEqual(len(logger.handlers), 1)
        self.assertIsInstance(logger.handlers[0], logging.StreamHandler)

    def test_create_logger_propagate_setting(self):
        """Test logger propagate setting."""
        config = {
            "name": "test_logger",
            "propagate": True,
            "handlers": [{"type": "StreamHandler"}]
        }
        
        logger = self.track_logger(create_logger(config))
        self.assertTrue(logger.propagate)
        
        config["propagate"] = False
        logger2 = self.track_logger(create_logger(config))
        self.assertFalse(logger2.propagate)

    def test_close_logger(self):
        """Test logger cleanup functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "name": "closable_logger_test",
                "handlers": [
                    {
                        "type": "StreamHandler"
                    },
                    {
                        "type": "FileHandler",
                        "path": temp_dir,
                        "filename": "closable.log"
                    }
                ]
            }
            
            logger = create_logger(config)
            initial_handler_count = len(logger.handlers)
            self.assertEqual(initial_handler_count, 2)
            
            # Store references to handlers to verify they get closed
            handlers = logger.handlers.copy()
            
            # Close the logger
            close_logger(logger)
            
            # Handlers should be removed from logger
            self.assertEqual(len(logger.handlers), 0)
            
            # Verify handlers were actually closed
            for handler in handlers:
                # Closed file handlers should have their stream closed
                if hasattr(handler, 'stream') and hasattr(handler.stream, 'closed'):
                    # Only check for file handlers, not stdout/stderr
                    if handler.stream.name != '<stdout>' and handler.stream.name != '<stderr>':
                        self.assertTrue(handler.stream.closed)

    def test_close_logger_none(self):
        """Test that closing None logger doesn't raise error."""
        # Should not raise any exception
        close_logger(None)

    def test_multiple_handlers_different_levels(self):
        """Test logger with multiple handlers at different levels."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Capture stdout for StreamHandler
            stdout_capture = io.StringIO()
            
            config = {
                "name": "multi_handler_logger",
                "level": "DEBUG",
                "handlers": [
                    {
                        "type": "StreamHandler",
                        "level": "WARNING",
                        "handler_kwargs": {"stream": stdout_capture}
                    },
                    {
                        "type": "FileHandler",
                        "path": temp_dir,
                        "filename": "debug.log",
                        "level": "DEBUG"
                    }
                ]
            }
            
            logger = self.track_logger(create_logger(config))
            
            # Log messages at different levels
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            
            # StreamHandler should only have WARNING and ERROR
            stdout_output = stdout_capture.getvalue()
            self.assertNotIn("Debug message", stdout_output)
            self.assertNotIn("Info message", stdout_output)
            self.assertIn("Warning message", stdout_output)
            self.assertIn("Error message", stdout_output)
            
            # File should have all messages (DEBUG level)
            log_file = os.path.join(temp_dir, "debug.log")
            with open(log_file, 'r') as f:
                file_content = f.read()
            
            self.assertIn("Debug message", file_content)
            self.assertIn("Info message", file_content)
            self.assertIn("Warning message", file_content)
            self.assertIn("Error message", file_content)


class TestOrFilter(unittest.TestCase):
    """Test cases for the OrFilter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.filter = OrFilter()

    def test_or_filter_creation(self):
        """Test OrFilter creation."""
        self.assertIsInstance(self.filter, OrFilter)
        self.assertEqual(self.filter.names, [])

    def test_add_name(self):
        """Test adding names to filter."""
        self.filter.addName("myapp")
        self.assertEqual(self.filter.names, ["myapp"])
        
        self.filter.addName("mymodule")
        self.assertEqual(set(self.filter.names), {"myapp", "mymodule"})

    def test_add_duplicate_name(self):
        """Test that duplicate names are not added."""
        self.filter.addName("myapp")
        self.filter.addName("myapp")
        self.assertEqual(self.filter.names, ["myapp"])

    def test_add_non_string_name(self):
        """Test that non-string names are not added."""
        self.filter.addName(123)
        self.filter.addName(None)
        self.assertEqual(self.filter.names, [])

    def test_remove_name(self):
        """Test removing names from filter."""
        self.filter.addName("myapp")
        self.filter.addName("mymodule")
        
        self.filter.removeName("myapp")
        self.assertEqual(self.filter.names, ["mymodule"])

    def test_remove_nonexistent_name(self):
        """Test removing name that doesn't exist."""
        self.filter.addName("myapp")
        self.filter.removeName("nonexistent")
        self.assertEqual(self.filter.names, ["myapp"])

    def test_filter_matching_record(self):
        """Test filtering with real logging records."""
        self.filter.addName("myapp")
        self.filter.addName("mymodule")
        
        # Create real log records like logging would
        record1 = logging.LogRecord("myapp", logging.INFO, "", 0, "test message", (), None)
        record2 = logging.LogRecord("mymodule", logging.INFO, "", 0, "test message", (), None)
        record3 = logging.LogRecord("myapp.submodule", logging.INFO, "", 0, "test message", (), None)
        record4 = logging.LogRecord("otherapp", logging.INFO, "", 0, "test message", (), None)
        
        # Should match exact names and prefixes
        self.assertTrue(self.filter.filter(record1))
        self.assertTrue(self.filter.filter(record2))
        self.assertTrue(self.filter.filter(record3))
        
        # Should not match unrelated names
        self.assertFalse(self.filter.filter(record4))

    def test_filter_empty_names(self):
        """Test filter behavior with no names added."""
        # Create a real log record
        record = logging.LogRecord("anyname", logging.INFO, "", 0, "test message", (), None)
        
        # Should not match anything when no names are added
        self.assertFalse(self.filter.filter(record))


if __name__ == "__main__":
    unittest.main()
