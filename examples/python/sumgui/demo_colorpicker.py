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


import os;
import sys;

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")));

import pygame;
from sumgui.display import fit_window_size, set_default_icon;


import os;
import sys;

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."));
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT);

from sumgui import ColorPicker, Label, Panel, Scale, Slider, THEMES, enable_key_repeat, get_events;


def main():
    pygame.init();
    set_default_icon();
    screen = pygame.display.set_mode(fit_window_size(720, 720));
    physical_width, physical_height = screen.get_size();
    pygame.display.set_caption("SumGUI ColorPicker");
    clock = pygame.time.Clock();
    theme = THEMES["Dark"];
    scale = Scale(physical_width, physical_height, base_width=720, base_height=720);
    font = scale.font(18, bold=True);
    big = scale.font(26, bold=True);
    selected = {"rgb": (0, 0, 0)};

    panel = Panel(pygame.Rect(0, 0, physical_width, physical_height), theme);
    label = panel.add(Label(pygame.Rect(30, 30, 620, 40), "Color: (0, 0, 0)", big, theme));

    def changed(widget, rgb):
        selected["rgb"] = rgb;
        label.text = "Color: " + repr(rgb);

    picker = panel.add(ColorPicker(pygame.Rect(30, 90, 340, 230), font, colors=theme.palette, on_change=changed, theme=theme));
    r = panel.add(Slider(pygame.Rect(400, 100, 260, 70), 0, 255, 0, step=1, font=font, label="R", theme=theme));
    g = panel.add(Slider(pygame.Rect(400, 190, 260, 70), 0, 255, 0, step=1, font=font, label="G", theme=theme));
    b = panel.add(Slider(pygame.Rect(400, 280, 260, 70), 0, 255, 0, step=1, font=font, label="B", theme=theme));

    def sync(widget, value):
        picker.set_rgb(r.value, g.value, b.value);

    r.on_change = sync;
    g.on_change = sync;
    b.on_change = sync;

    running = True;
    enable_key_repeat(250, 31);
    while running:
        dt = clock.tick(60);
        for event in get_events():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False;
            else:
                panel.handle_event(event);
        panel.update(dt);
        screen.fill(theme.bg);
        panel.draw(screen);
        pygame.draw.rect(screen, selected["rgb"], pygame.Rect(30, 370, 630, 120));
        pygame.draw.rect(screen, theme.line, pygame.Rect(30, 370, 630, 120), 2);
        pygame.display.flip();
    pygame.quit();


if __name__ == "__main__":
    main();
