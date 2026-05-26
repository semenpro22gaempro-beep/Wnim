#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""".
Start: wnim <file>
"""

import sys
import os

# Добавляем папку скрипта в путь для импорта editor
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from editor import Editor, main

if __name__ == "__main__":
    main()
