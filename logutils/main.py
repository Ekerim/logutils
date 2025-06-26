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

import logging
import logging.handlers
import socket
import uuid
import os

from .filters.OrFilter import OrFilter

logger = logging.getLogger(__name__)
show_stacktrace = False

LOG_LEVELS = {
    "CRITICAL": 50,
    "ERROR":    40,
    "WARNING":  30,
    "INFO":     20,
    "DEBUG":    10,
    "NOTSET":    0
}


def create_logger(linfo, logger_object=None):
    # If the logger is not enabled return None.
    if not linfo.get('enabled', True):
        # If a logger object was supplied, return that ...
        if logger_object:
            return logger_object

        # ... else return None
        return None

    # Create a random UUID that we can use if the user doesn't supply a name or filename.
    tUUID = uuid.UUID(str(uuid.uuid4()))

    logger_name = linfo.get('name', tUUID.hex)
    llevel = linfo.get('level', 'DEBUG')
    lformatter = logging.Formatter(
        linfo.get('format', '%(asctime)s %(name)s - %(funcName)s [%(levelname)s]: %(message)s')
    )

    tlogger = None

    # Create new logger object.
    if logger_object:
        tlogger = logger_object
    else:
        logging.Logger.manager.loggerDict.pop(logger_name, None)
        tlogger = logging.getLogger(logger_name)

    tlogger.setLevel(llevel)
    tlogger.propagate = linfo.get('propagate', False)

    for handler in linfo.get("handlers", {}):
        # If the handler is not enabled, skip it
        if not handler.get('enabled', True):
            continue

        hpath = handler.get('path', None)
        hfilename = handler.get('filename', tUUID.hex + '.log')
        htype = handler.get('type', 'FileHandler')
        hargs = handler.get('args', [])
        hkwargs = handler.get('handler_kwargs', {})
        hfilters = handler.get('filters', None)
        hlevel = handler.get('level', 'DEBUG')
        hformatter = logging.Formatter(
            handler.get('format', '%(asctime)s %(name)s - %(funcName)s [%(levelname)s]: %(message)s')
        )

        # If the log path doesn't exist, raise a RuntimeError()
        if (not hpath or not os.path.exists(hpath)) and htype in (
                'FileHandler', 'WatchedFileHandler', 'RotatingFileHandler', 'TimedRotatingFileHandler'
        ):
            raise RuntimeError(f"Logger path '{hpath}' doesn't exist")

        # Create a log handler of the right type ...

        # V class logging.StreamHandler(stream=None)
        # V class logging.FileHandler(filename, mode='a', encoding=None, delay=False, errors=None)
        # V class logging.handlers.WatchedFileHandler(filename, mode='a', encoding=None, delay=False, errors=None)
        # V class logging.handlers.RotatingFileHandler(filename, mode='a', maxBytes=0, backupCount=0,
        #         encoding=None, delay=False, errors=None)
        # V class logging.handlers.TimedRotatingFileHandler(filename, when='h', interval=1, backupCount=0,
        #         encoding=None, delay=False, utc=False, atTime=None, errors=None)
        # V class logging.handlers.SocketHandler(host, port)
        # V class logging.handlers.DatagramHandler(host, port)
        # V class logging.handlers.SysLogHandler(address=('localhost', SYSLOG_UDP_PORT), facility=LOG_USER,
        #         socktype=socket.SOCK_DGRAM)
        # V class logging.handlers.NTEventLogHandler(appname, dllname=None, logtype='Application')
        # V class logging.handlers.SMTPHandler(mailhost, fromaddr, toaddrs, subject, credentials=None, secure=None,
        #         timeout=1.0)

        thandler = None
        if htype == 'StreamHandler':
            # Output to stdout or stderr
            thandler = logging.StreamHandler(**hkwargs)
        elif htype == 'FileHandler':
            # Standard output to file, no frills
            thandler = logging.FileHandler(hpath + '/' + hfilename, **hkwargs)
        elif htype == 'WatchedFileHandler':
            # Standard output to file, but the file is reopened if it has changed on disk
            thandler = logging.handlers.WatchedFileHandler(hpath + '/' + hfilename, **hkwargs)
        elif htype == 'RotatingFileHandler':
            # Output to file that is rotated based on size
            thandler = logging.handlers.RotatingFileHandler(hpath + '/' + hfilename, **hkwargs)
        elif htype == 'TimedRotatingFileHandler':
            # Output to file that is rotated based on a schedule
            thandler = logging.handlers.TimedRotatingFileHandler(hpath + '/' + hfilename, **hkwargs)
        elif htype == 'SocketHandler':
            # Output to a TCP socket
            thandler = logging.handlers.SocketHandler(*hargs)
        elif htype == 'DatagramHandler':
            # Output to an UDP socket
            thandler = logging.handlers.DatagramHandler(*hargs)
        elif htype == 'SysLogHandler':
            # Output to a log-facility of a syslog server, defaults to TCP transport.
            proto = handler.get('proto', 'TCP')
            haddress = hkwargs.get('address', None)

            if haddress and isinstance(haddress, list):
                hkwargs['address'] = tuple(haddress)

            if proto == 'TCP':
                thandler = logging.handlers.SysLogHandler(**hkwargs, socktype=socket.SOCK_STREAM)
            elif proto == 'UDP':
                thandler = logging.handlers.SysLogHandler(**hkwargs, socktype=socket.SOCK_DGRAM)
            else:
                logger.warning(f"Handling of transport protocol {proto} is not implemented")
                continue
        elif htype == 'NTEventLogHandler':
            # Output to a Windows eventlog server
            thandler = logging.handlers.NTEventLogHandler(*hargs, **hkwargs)
        elif htype == 'SMTPHandler':
            # Output to email
            thandler = logging.handlers.SMTPHandler(*hargs, **hkwargs)
        else:
            logger.warning(f"Bogus log handler '{htype}'. Skipping")
            continue

        thandler.setLevel(hlevel)
        thandler.setFormatter(hformatter)

        if hfilters:
            hfilter = OrFilter()
            for fltr in hfilters:
                hfilter.addName(fltr)

            thandler.addFilter(hfilter)

        tlogger.addHandler(thandler)

    # Return the new logger
    return tlogger


def close_logger(logger_object):
    if logger_object:
        # Is the logger object has handlers attached to it ...
        if logger_object.hasHandlers():
            # ... iterate over all the handlers and remove them from the logger and then close them.
            # Make a copy of the handlers list to avoid modifying while iterating
            handlers = logger_object.handlers.copy()
            for handler in handlers:
                logger_object.removeHandler(handler)
                handler.close()

        # Delete the logger object
        del logger_object
