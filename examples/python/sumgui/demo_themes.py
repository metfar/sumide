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
from sumgui.display import fit_window_size;


import os;
import sys;

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."));
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT);

from sumgui import Button, Label, Panel, Scale, THEMES, enable_key_repeat, get_events;


def main():
    pygame.init();
    screen = pygame.display.set_mode(fit_window_size(720, 720));
    physical_width, physical_height = screen.get_size();
    pygame.display.set_caption("SumGUI themes");
    clock = pygame.time.Clock();
    scale = Scale(physical_width, physical_height, base_width=720, base_height=720);
    font = scale.font(20, bold=True);
    big = scale.font(28, bold=True);
    names = list(THEMES.keys());
    current = [0];

    def build_panel():
        theme = THEMES[names[current[0]]];
        panel = Panel(pygame.Rect(0, 0, physical_width, physical_height), theme);
        panel.add(Label(pygame.Rect(30, 30, 600, 40), "Theme: " + names[current[0]], big, theme));
        def next_theme(widget):
            current[0] = (current[0] + 1) % len(names);
        panel.add(Button(pygame.Rect(30, 100, 240, 70), "NEXT THEME", font, next_theme, theme));
        panel.add(Label(pygame.Rect(30, 200, 620, 120), "ZX, DOS, C64, MSX, Dark, Light\nPress button, Enter or Space.", font, theme));
        return panel;

    panel = build_panel();
    running = True;
    enable_key_repeat(250, 31);
    while running:
        dt = clock.tick(60);
        old = current[0];
        for event in get_events():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False;
            else:
                panel.handle_event(event);
        if old != current[0]:
            panel = build_panel();
        panel.update(dt);
        screen.fill(THEMES[names[current[0]]].bg);
        panel.draw(screen);
        pygame.display.flip();
    pygame.quit();


if __name__ == "__main__":
    main();
