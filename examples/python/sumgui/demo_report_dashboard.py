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

from sumui import ChartSeries, ChartSpec, TableSpec, modern_mode;
from sumgui.graphics import GraphicsSurface;
from sumgui.theme import DEFAULT_THEME;


def main():
    pygame.init();
    surface = GraphicsSurface(modern_mode(960, 600));
    surface.clear((245, 245, 245));
    categories = ("Android", "Linux", "Windows");
    values = (500, 800, 600);
    rows = (("Android", 500), ("Linux", 800), ("Windows", 600));
    surface.draw_table(20, 20, 260, 150, TableSpec(rows, ("OS", "Users"), "Users by OS"), theme=DEFAULT_THEME);
    line = ChartSpec("line", title="Line", categories=categories, series=(ChartSeries("Users", values),));
    bars = ChartSpec.bar(categories, values, title="Bars", name="Users");
    hbars = ChartSpec("bar", title="Horizontal bars", categories=categories, series=(ChartSeries("Users", values),), options=(("orientation", "horizontal"),));
    pie = ChartSpec.pie(categories, values, title="Pie", name="Users");
    radar = ChartSpec.radar(categories, values, title="Radar", name="Users");
    surface.draw_chart(300, 20, 300, 250, line, theme=DEFAULT_THEME);
    surface.draw_chart(620, 20, 300, 250, bars, theme=DEFAULT_THEME);
    surface.draw_chart(20, 300, 280, 250, hbars, theme=DEFAULT_THEME);
    surface.draw_chart(320, 300, 280, 250, pie, theme=DEFAULT_THEME);
    surface.draw_chart(620, 300, 300, 250, radar, theme=DEFAULT_THEME);
    surface.save_image("sumgui_report_dashboard.png");
    screen = pygame.display.set_mode(surface.size, pygame.RESIZABLE);
    pygame.display.set_caption("Σ SumGUI report dashboard");
    running = True;
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False;
        screen.blit(surface.surface, (0, 0));
        pygame.display.flip();
    pygame.quit();


if __name__ == "__main__":
    main();
