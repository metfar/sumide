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

from sumui import ChartSpec;
from sumgui.easy import alert, button, chart, label, slider, start, textinput, window;

window("SumGUI components", width=720, height=680, base_width=720, base_height=680);
label("SumGUI component sampler", 20, 14, 520, 40, font_size=24, bold=True);
label("The layout is logical; the physical window is fitted before startup.", 20, 55, 670, 30);
button("ABOUT", 20, 100, 150, 52, do=lambda: alert("Label, Button, TextInput, Slider and ChartView", "Components"));
textinput(190, 100, 240, 52, text="N", max_length=1, valid_values=("S", "N"), confirm_at_limit=True);
slider("Value", 450, 96, 240, 64, minimum=0, maximum=100, value=55);
spec = ChartSpec.bar(["A", "B", "C"], [25, 50, 35], title="Shared chart");
chart(spec, 20, 190, 670, 450);
start();
