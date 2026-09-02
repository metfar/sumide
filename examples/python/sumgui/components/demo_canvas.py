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

from sumgui.easy import canvas, label, start, window;

window("SumGUI Canvas", width=700, height=520, base_width=700, base_height=520);
label("Canvas component", 20, 16, 400, 38, font_size=24, bold=True);
area = canvas(20, 70, 660, 420, interactive=False);
area.line(20, 30, 620, 30, color=(0, 255, 255), width=2);
area.rect(60, 90, 180, 100, color=(255, 255, 0), width=3);
area.circle(430, 150, 70, color=(255, 0, 255), width=3);
area.text(70, 240, "Shared graphical primitives", color=(255, 255, 255));
start();
