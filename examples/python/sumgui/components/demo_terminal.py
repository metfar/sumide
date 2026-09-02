#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  

import os;
import sys;

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."));
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT);

from sumgui.easy import label, start, terminal, window;

window("SumGUI TerminalArea", width=700, height=500, base_width=700, base_height=500);
label("TerminalArea component", 20, 16, 440, 40, font_size=24, bold=True);
terminal(20, 70, 660, 400, text="sum> help\nShared Sum ecosystem terminal area\nsum> _");
start();
