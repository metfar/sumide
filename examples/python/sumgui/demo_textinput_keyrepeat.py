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

from sumgui.easy import *;


def main():
    window("SumGUI TextInput keyrepeat demo", width=720, height=420, font_size=18, theme="zx");
    say("Hold a letter, Backspace, Delete, Home/End. Field scrolls with cursor.", 20, 20, 680, 35);
    inputline(20, 75, 460, 50, text="graphic", placeholder="filename", max_length=-1, show_h_scrollbar=False);
    button("ASK", 500, 75, 160, 50, do=lambda: alert("Result: " + str(ask("InputBox", "This modal uses TextInput too.", "graphicaaaaa", max_length=-1))));
    textarea(20, 150, 640, 210, text="TextArea already scrolls horizontally and repeats Backspace/Delete.\nTry áéíóú äëïöü ñ ç and dead keys.", accepts_tab=True, tab_size=4, syntax=None);
    start();


if __name__ == "__main__":
    main();
