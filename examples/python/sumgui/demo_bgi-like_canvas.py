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

from sumgui.easy import alert, button, canvas, label, start, window;

STATE = {"shape": "RECT", "color": (255, 255, 0), "last": None, "status": "Choose a shape and click the canvas."};
DRAW_CANVAS = None;
STATUS_LABEL = None;


def set_shape(name):
    STATE["shape"] = name;
    STATE["status"] = "Shape: " + name;
    if STATUS_LABEL is not None:
        STATUS_LABEL.text = STATE["status"];


def clear_canvas():
    if DRAW_CANVAS is not None:
        DRAW_CANVAS.clear();
        DRAW_CANVAS.line(10, 10, 420, 10, color=(0, 255, 255), width=1);
        DRAW_CANVAS.text(14, 16, "SumGUI CanvasArea - BGI style demo", color=(255, 255, 255));
    STATE["last"] = None;
    STATE["status"] = "Canvas cleared.";
    if STATUS_LABEL is not None:
        STATUS_LABEL.text = STATE["status"];


def choose_color(color, name):
    STATE["color"] = color;
    STATE["status"] = "Color: " + name;
    if STATUS_LABEL is not None:
        STATUS_LABEL.text = STATE["status"];


def canvas_event(widget, event):
    if event.type != pygame.MOUSEBUTTONDOWN:
        return False;
    if event.button != 1:
        return False;

    x, y = widget.canvas_pos(event.pos);
    x = int(x);
    y = int(y);
    shape = STATE["shape"];
    color = STATE["color"];

    if shape == "POINT":
        widget.fill_circle(x, y, 4, color=color);
    elif shape == "LINE":
        if STATE["last"] is None:
            STATE["last"] = (x, y);
            STATE["status"] = "Line start: " + str((x, y));
            if STATUS_LABEL is not None:
                STATUS_LABEL.text = STATE["status"];
            return True;
        x0, y0 = STATE["last"];
        widget.line(x0, y0, x, y, color=color, width=3);
        STATE["last"] = None;
    elif shape == "RECT":
        widget.rect(x - 35, y - 25, 70, 50, color=color, width=3);
    elif shape == "FILLRECT":
        widget.fill_rect(x - 35, y - 25, 70, 50, color=color);
    elif shape == "CIRCLE":
        widget.circle(x, y, 28, color=color, width=3);
    elif shape == "FILLCIRCLE":
        widget.fill_circle(x, y, 28, color=color);
    elif shape == "ELLIPSE":
        widget.ellipse(x - 40, y - 25, 80, 50, color=color, width=3);
    elif shape == "TEXT":
        widget.text(x, y, "READY.", color=color);

    STATE["status"] = shape + " at " + str((x, y));
    if STATUS_LABEL is not None:
        STATUS_LABEL.text = STATE["status"];
    return True;


def main():
    global DRAW_CANVAS;
    global STATUS_LABEL;

    window("SumGUI Canvas BGI demo", width=720, height=700, base_width=720, base_height=700, font_size=18);
    label("SumGUI / CanvasArea demo", 20, 16, 420, 34, font_size=24, bold=True);
    label("Pick a figure. Click the canvas to draw. LINE uses two clicks.", 20, 52, 650, 28);

    button("POINT", 20, 90, 100, 42, do=lambda: set_shape("POINT"));
    button("LINE", 130, 90, 100, 42, do=lambda: set_shape("LINE"));
    button("RECT", 240, 90, 100, 42, do=lambda: set_shape("RECT"));
    button("FRECT", 350, 90, 100, 42, do=lambda: set_shape("FILLRECT"));
    button("CIRCLE", 460, 90, 110, 42, do=lambda: set_shape("CIRCLE"));
    button("FCIRC", 580, 90, 110, 42, do=lambda: set_shape("FILLCIRCLE"));
    button("ELLIP", 20, 140, 100, 42, do=lambda: set_shape("ELLIPSE"));
    button("TEXT", 130, 140, 100, 42, do=lambda: set_shape("TEXT"));
    button("CLEAR", 240, 140, 110, 42, do=clear_canvas);
    button("ABOUT", 360, 140, 110, 42, do=lambda: alert("Canvas primitives: line, rect, fill_rect, circle, fill_circle, ellipse, polygon, text, image.", "CanvasArea"));

    button("YELLOW", 490, 140, 95, 42, do=lambda: choose_color((255, 255, 0), "YELLOW"));
    button("CYAN", 595, 140, 95, 42, do=lambda: choose_color((0, 255, 255), "CYAN"));

    DRAW_CANVAS = canvas(20, 200, 680, 430, interactive=True, on_event=canvas_event);
    clear_canvas();
    STATUS_LABEL = label(STATE["status"], 20, 650, 680, 30);

    start();


if __name__ == "__main__":
    main();
