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
from sumgui.display import fit_window_size;

from sumgui import ChartSpec, ChartView, DEFAULT_THEME;


pygame.init();
screen = pygame.display.set_mode(fit_window_size(800, 480), pygame.RESIZABLE);
font = pygame.font.SysFont("monospace", 16);
spec = ChartSpec.bar(["A", "B", "C"], [25, 50, 35], title="Shared ChartSpec", y_label="Value");
chart = ChartView(pygame.Rect(20, 20, 760, 420), spec, font, DEFAULT_THEME);
clock = pygame.time.Clock();
running = True;
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False;
    screen.fill(DEFAULT_THEME.bg);
    chart.rect = pygame.Rect(20, 20, max(40, screen.get_width() - 40), max(40, screen.get_height() - 40));
    chart.draw(screen);
    pygame.display.flip();
    clock.tick(60);
pygame.quit();
