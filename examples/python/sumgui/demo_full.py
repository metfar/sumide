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

from sumgui.display import fit_window_size;
from sumgui import BarChart, Button, CanvasArea, DEFAULT_THEME, GridWidget, Label, LineChart, PaletteWidget, Panel, Scale, ScatterChart, Slider, StatusBar, TextArea, ToolBar, enable_key_repeat, get_events, message_box;

BASE_WIDTH = 720;
BASE_HEIGHT = 1280;
HEIGHT = 720;
WIDTH = int(BASE_WIDTH * (HEIGHT / BASE_HEIGHT));


def main():
    pygame.init();
    enable_key_repeat(250, 31);
    screen = pygame.display.set_mode(fit_window_size(WIDTH, HEIGHT));
    physical_width, physical_height = screen.get_size();
    pygame.display.set_caption("SumGUI Alpha Demo");
    clock = pygame.time.Clock();
    scale = Scale(physical_width, physical_height, base_width=BASE_WIDTH, base_height=BASE_HEIGHT);
    theme = DEFAULT_THEME;
    font_big = scale.font(30, bold=True);
    font = scale.font(18, bold=True);
    status = StatusBar(scale.rect(0, 1220, 720, 60), font, theme=theme, zones=[{"text":"READY", "width":-1}, {"text":"ROW 0", "width":130}, {"text":"COL 0", "width":130}, {"text":"SUMGUI 0.2.0a8", "width":230, "align":"right"}]);

    def set_status(text):
        status.set_zone(0, text);

    panel = Panel(scale.rect(20, 20, 680, 1180), theme);
    panel.add(Label(scale.rect(40, 45, 500, 40), "SumGUI / ΣGUI alpha", font_big, theme));
    panel.add(Label(scale.rect(40, 92, 620, 30), "Canvas, editable charts, Unicode, focus, repeat 250/31.", font, theme));

    grid = GridWidget(scale.rect(40, 145, 300, 300), rows=8, cols=8, palette=theme.palette, font=font, theme=theme);
    panel.add(grid);

    def select_color(index):
        grid.paint_value = index;
        set_status("COLOR " + str(index));

    palette = PaletteWidget(scale.rect(370, 145, 280, 80), theme.palette, scale.v(34), select_color, theme);
    panel.add(palette);

    def say_hello(button):
        set_status("HELLO FROM " + button.text);
        message_box(screen, clock, "SumGUI", "Simple widgets, spicy pixels.", theme);

    toolbar = ToolBar(scale.rect(370, 240, 280, 55), font, [("MSG", say_hello), ("CLR", lambda b: clear_grid(grid, set_status)), ("OK", lambda b: set_status("OK"))], theme);
    panel.add(toolbar);

    canvas_points = [(20, 30), (50, 40), (80, 20), (120, 70), (160, 50)];

    def draw_canvas(canvas, surface, rect):
        center = rect.center;
        pygame.draw.line(surface, theme.line, (rect.x + 8, center[1]), (rect.right - 8, center[1]), 1);
        pygame.draw.line(surface, theme.line, (center[0], rect.y + 8), (center[0], rect.bottom - 8), 1);
        for i in range(0, rect.width, max(8, scale.v(24))):
            pygame.draw.line(surface, theme.line, (rect.x + i, rect.y), (rect.x + i, rect.bottom), 1);
        for i in range(0, rect.height, max(8, scale.v(24))):
            pygame.draw.line(surface, theme.line, (rect.x, rect.y + i), (rect.right, rect.y + i), 1);
        prev = None;
        for x, y in canvas_points:
            sx = rect.x + int(x * rect.width / 180);
            sy = rect.bottom - int(y * rect.height / 90);
            if prev is not None:
                pygame.draw.line(surface, theme.cursor, prev, (sx, sy), 2);
            pygame.draw.circle(surface, theme.button, (sx, sy), 4);
            prev = (sx, sy);

    def canvas_event(canvas, event):
        if event.type == pygame.MOUSEBUTTONDOWN and canvas.get_rect().collidepoint(event.pos):
            local = canvas.local_pos(event.pos);
            r = canvas.get_rect().inflate(-8, -8);
            x = int((local[0] - 8) * 180 / max(1, r.width));
            y = int((r.height - (local[1] - 8)) * 90 / max(1, r.height));
            canvas_points.append((max(0, min(180, x)), max(0, min(90, y))));
            set_status("CANVAS POINT ADDED");
            return True;
        return False;

    panel.add(CanvasArea(scale.rect(40, 465, 285, 185), theme=theme, on_draw=draw_canvas, on_event=canvas_event, tab_index=3));
    panel.add(Label(scale.rect(52, 472, 250, 24), "CanvasArea", font, theme));

    def line_changed(chart, index, point):
        set_status("POINT " + str(index) + " = " + str((round(point[0], 2), round(point[1], 2))));

    panel.add(LineChart(scale.rect(350, 465, 300, 225), [(0, 1), (1, 4), (2, 3), (3, 8), (4, 6)], font, "Editable LineChart", theme, x_label="Time", y_label="Value", editable=True, on_change=line_changed, tab_index=4));
    panel.add(BarChart(scale.rect(40, 675, 285, 185), [("A", 5), ("B", 9), ("C", 2), ("D", 7)], font, "BarChart", theme, x_label="Category", y_label="Qty"));
    panel.add(ScatterChart(scale.rect(350, 710, 300, 185), [(1, 2), (2, 3), (3, 7), (4, 4), (5, 9)], font, "Scatter", theme, x_label="X", y_label="Y"));

    panel.add(Button(scale.rect(350, 900, 300, 58), "BUTTON WIDGET", font, say_hello, theme));

    def slider_changed(slider, value):
        set_status(slider.label + " = " + str(round(value, 2)));

    panel.add(Slider(scale.rect(350, 975, 300, 68), 0, 100, 42, "horizontal", 1, slider_changed, font, "Horizontal Slider", theme));
    panel.add(Slider(scale.rect(610, 1060, 40, 105), 0, 10, 5, "vertical", 1, slider_changed, font, "V", theme));
    panel.add(TextArea(scale.rect(350, 1060, 245, 105), font, "Tildes: áéíóú ñ Ñ ü Ü àèìòù âêîôû äëïöü ç Ç œ æ.", True, True, True, -1, -1, theme, show_v_scrollbar=True, show_h_scrollbar=True, accepts_tab=True));
    panel.add(TextArea(scale.rect(40, 885, 285, 70), font, "single line", False, False, True, 1, -1, theme, show_v_scrollbar=False, show_h_scrollbar=False, accepts_tab=False));

    running = True;
    while running:
        dt = clock.tick(60);
        for event in get_events():
            if event.type == pygame.QUIT:
                running = False;
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False;
            elif panel.handle_event(event):
                pass;
        panel.update(dt);
        screen.fill(theme.bg);
        panel.draw(screen);
        status.draw(screen);
        pygame.display.flip();
    pygame.quit();


def clear_grid(grid, set_status):
    for row in range(grid.rows):
        for col in range(grid.cols):
            grid.cells[row][col].color = -1;
            grid.cells[row][col].text = "";
            grid.cells[row][col].image = None;
    set_status("GRID CLEARED");


if __name__ == "__main__":
    main();
