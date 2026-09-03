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

from sumui import ChartSeries, ChartSpec, FontSpec, TableSpec, modern_mode;
from sumgui.display import set_default_icon;
from sumgui.graphics import GraphicsSurface;
from sumgui.theme import Theme;


REPORT_PALETTE = [
    (38, 110, 190),
    (0, 145, 135),
    (142, 88, 180),
    (220, 105, 45),
    (70, 145, 85),
];

REPORT_THEME = Theme(
    "Sum Report",
    bg=(238, 242, 247),
    panel=(255, 255, 255),
    line=(185, 198, 214),
    text=(30, 42, 56),
    muted=(82, 98, 116),
    button=(215, 229, 246),
    button_alt=(226, 235, 244),
    button_text=(24, 48, 76),
    error=(190, 55, 55),
    cursor=(38, 110, 190),
    palette=REPORT_PALETTE,
    title=(24, 74, 130),
);


def _chart(kind, title, categories, values, renderer, body_font, title_font, tick_font, **options):
    chart_options = [("renderer", renderer), ("series_colors", tuple(REPORT_PALETTE))];
    chart_options.extend(options.items());
    return ChartSpec(
        kind,
        title=title,
        categories=categories,
        series=(ChartSeries("Users", values),),
        options=tuple(chart_options),
        font=body_font,
        title_font=title_font,
        tick_font=tick_font,
        legend_font=tick_font,
    );


def build_dashboard(renderer="native"):
    surface = GraphicsSurface(modern_mode(960, 600));
    surface.clear(REPORT_THEME.bg);
    categories = ("Android", "Linux", "Windows");
    values = (500, 800, 600);
    rows = (("Android", 500), ("Linux", 800), ("Windows", 600));
    body_font = FontSpec(size=10);
    title_font = FontSpec(size=12, bold=True);
    tick_font = FontSpec(size=9);
    surface.draw_table(
        20, 20, 260, 150,
        TableSpec(rows, ("OS", "Users"), "Users by OS", font=body_font, title_font=title_font, header_font=body_font),
        theme=REPORT_THEME,
    );
    line = _chart("line", "Line", categories, values, renderer, body_font, title_font, tick_font);
    bars = _chart("bar", "Bars", categories, values, renderer, body_font, title_font, tick_font);
    hbars = _chart("bar", "Horizontal bars", categories, values, renderer, body_font, title_font, tick_font, orientation="horizontal");
    pie = _chart("pie", "Pie", categories, values, renderer, body_font, title_font, tick_font);
    radar = _chart("radar", "Radar", categories, values, renderer, body_font, title_font, tick_font);
    surface.draw_chart(300, 20, 300, 250, line, theme=REPORT_THEME);
    surface.draw_chart(620, 20, 300, 250, bars, theme=REPORT_THEME);
    surface.draw_chart(20, 300, 280, 250, hbars, theme=REPORT_THEME);
    surface.draw_chart(320, 300, 280, 250, pie, theme=REPORT_THEME);
    surface.draw_chart(620, 300, 300, 250, radar, theme=REPORT_THEME);
    return surface;


def main(renderer="native"):
    pygame.init();
    surface = build_dashboard(renderer=renderer);
    surface.save_image("sumgui_report_dashboard_{}.png".format(renderer));
    set_default_icon();
    screen = pygame.display.set_mode(surface.size, pygame.RESIZABLE);
    pygame.display.set_caption("Σ SumGUI report dashboard - {}".format(renderer));
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
