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
import pygame;
from sumgui import CalendarView, DateTimeView, DEFAULT_THEME, Panel, TimeView, set_default_icon;
from sumgui.display import fit_window_size;


def main():
    pygame.init();
    set_default_icon();
    screen = pygame.display.set_mode(fit_window_size(720, 520));
    pygame.display.set_caption("Σ SumGUI date/time widgets");
    font = pygame.font.SysFont("monospace", 20, bold=True);
    panel = Panel(pygame.Rect(20, 20, 680, 480), DEFAULT_THEME);
    panel.add(CalendarView(pygame.Rect(30, 30, 410, 360), font, theme=DEFAULT_THEME, tab_index=1));
    panel.add(TimeView(pygame.Rect(460, 60, 190, 70), font, live=True, theme=DEFAULT_THEME, tab_index=2));
    panel.add(DateTimeView(pygame.Rect(450, 160, 210, 90), font, live=True, theme=DEFAULT_THEME, tab_index=3));
    clock = pygame.time.Clock();
    running = True;
    while running:
        dt = clock.tick(30);
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False;
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False;
            else: panel.handle_event(event);
        panel.update(dt);
        screen.fill(DEFAULT_THEME.bg);
        panel.draw(screen);
        pygame.display.flip();
    pygame.quit();


if __name__ == "__main__":
    main();
