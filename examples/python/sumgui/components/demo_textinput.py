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

from sumgui.easy import label, start, textinput, window;

window("SumGUI TextInput", width=640, height=380, base_width=640, base_height=380);
label("TextInput + CONFIRM", 24, 24, 460, 42, font_size=26, bold=True);
label("One-character S/N field. CONFIRM stays ON.", 24, 78, 560, 30);
textinput(24, 122, 220, 52, text="N", max_length=1, valid_values=("S", "N"), validation_error="Only S or N", confirm_at_limit=True);
start();
