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

from sumgui.easy import label, slider, start, window;

window("SumGUI Slider", width=640, height=380, base_width=640, base_height=380);
label("Slider component", 24, 24, 420, 42, font_size=26, bold=True);
slider("Volume", 24, 96, 560, 60, minimum=0, maximum=100, value=50, step=5);
start();
