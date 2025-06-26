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

class OrFilter(logging.Filter):
    def __init__(self):
        self.names = []

    def addName(self, name):
        if isinstance(name, str) and name not in self.names:
            self.names.append(name)

    def removeName(self, name):
        if isinstance(name, str) and name in self.names:
            self.names.remove(name)

    def filter(self, record):
        # if [name for name in self.names if record.name.startswith(name)]:
        #     return True

        # return False
        matches = [name for name in self.names if record.name.startswith(name)]
        # print(f"Filter check: {record.name} against {self.names} -> matches: {matches}")
        return bool(matches)
