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

from .main import create_logger, close_logger, LOG_LEVELS

__all__ = ['create_logger', 'close_logger', 'LOG_LEVELS']
