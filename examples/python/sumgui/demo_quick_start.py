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
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#


import math;
import os;
import sys;

import pygame;

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")));


import os;
import sys;

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."));
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT);

from sumgui.easy import *;


window("SumGUI quick start", width=720, height=580, base_width=720, base_height=580, font_size=22, theme="ZX");
say("READY.", 20, 20, 300, 40, font_size=28, bold=True);
say("This is the beginner-friendly API.", 20, 70, 520, 34);
button("ALERT", 20, 130, 180, 70, do=lambda: alert("Hello from SumGUI!"));
textarea(20, 230, 660, 280, "Try accents: áéíóú àèìòù äëïöü ñ ç\nClipboard: Ctrl+C/X/V", font_size=20, accepts_tab=True);
start();
