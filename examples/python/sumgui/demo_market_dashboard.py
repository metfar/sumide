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

import json;
import math;
import random;
import time;
import urllib.request;

import pygame;
import sumgui.easy as sg;


SYMBOLS = [
    ("^NYA", "NYSE"),
    ("^GSPC", "S&P 500"),
    ("^DJI", "Dow Jones"),
    ("^IXIC", "Nasdaq"),
    ("^RUT", "Russell"),
    ("^VIX", "VIX"),
];

PALETTE = [
    (0, 0, 0),
    (0, 0, 205),
    (205, 0, 0),
    (205, 0, 205),
    (0, 205, 0),
    (0, 205, 205),
    (205, 205, 0),
    (205, 205, 205),
    (22, 22, 22),
    (0, 0, 255),
    (255, 0, 0),
    (255, 0, 255),
    (0, 255, 0),
    (0, 255, 255),
    (255, 255, 0),
    (255, 255, 255),
];

SERIE_COLORS = [
    PALETTE[13],
    PALETTE[11],
    PALETTE[14],
    PALETTE[12],
    PALETTE[10],
    PALETTE[9],
];


def fetch_symbol(symbol, data_range="1mo", interval="1d"):
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        + urllib.parse.quote(symbol)
        + "?range="
        + data_range
        + "&interval="
        + interval
    );

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    );

    with urllib.request.urlopen(req, timeout=12) as response:
        data = json.loads(response.read().decode("utf-8"));

    result = data["chart"]["result"][0];
    timestamps = result["timestamp"];
    closes = result["indicators"]["quote"][0]["close"];

    clean = [];
    for ts, close in zip(timestamps, closes):
        if close is not None:
            clean.append((ts, float(close)));

    return clean;


def fake_symbol(seed, points=30):
    random.seed(seed);
    value = 100.0 + random.random() * 20.0;
    rows = [];

    for i in range(points):
        value += random.uniform(-2.5, 2.8);
        value += math.sin(i / 3.0 + seed) * 0.8;
        rows.append((int(time.time()) - (points - i) * 86400, value));

    return rows;


def load_market_data():
    data = {};
    used_fake = False;

    for i, item in enumerate(SYMBOLS):
        symbol, name = item;

        try:
            rows = fetch_symbol(symbol);
        except Exception:
            rows = fake_symbol(i + 1);
            used_fake = True;

        data[name] = rows;

    return data, used_fake;


def normalize_series(rows):
    base = rows[0][1];

    if base == 0.0:
        base = 1.0;

    return [(v / base) * 100.0 for _, v in rows];


def draw_dashboard(canvas, surface, rect):
    data = canvas.data["data"];
    used_fake = canvas.data["used_fake"];
    font = canvas.data["font"];
    small = canvas.data["small"];

    pygame.draw.rect(surface, PALETTE[8], rect);

    cyan = PALETTE[13];
    magenta = PALETTE[11];
    yellow = PALETTE[14];
    white = PALETTE[15];
    gray = (120, 120, 120);

    pygame.draw.rect(surface, cyan, rect, 2);

    title = font.render("SumGUI Demo - NYSE Market Dashboard", True, cyan);
    surface.blit(title, (rect.x + 20, rect.y + 14));

    for i, color in enumerate(PALETTE):
        pygame.draw.rect(surface, color, (rect.right - 280 + i * 16, rect.y + 14, 14, 14));
        pygame.draw.rect(surface, white, (rect.right - 280 + i * 16, rect.y + 14, 14, 14), 1);

    chart = pygame.Rect(rect.x + 35, rect.y + 70, 680, 430);
    side = pygame.Rect(rect.x + 735, rect.y + 70, 330, 430);
    bottom = pygame.Rect(rect.x + 35, rect.y + 520, 1030, 150);

    pygame.draw.rect(surface, (5, 5, 5), chart);
    pygame.draw.rect(surface, cyan, chart, 1);
    pygame.draw.rect(surface, (10, 20, 20), side);
    pygame.draw.rect(surface, cyan, side, 1);
    pygame.draw.rect(surface, (10, 20, 20), bottom);
    pygame.draw.rect(surface, cyan, bottom, 1);

    plot = pygame.Rect(chart.x + 55, chart.y + 55, chart.width - 80, chart.height - 105);

    all_norm = [];
    normalized = {};

    for name, rows in data.items():
        values = normalize_series(rows);
        normalized[name] = values;
        all_norm.extend(values);

    min_y = min(all_norm) - 2.0;
    max_y = max(all_norm) + 2.0;

    pygame.draw.rect(surface, (0, 0, 0), plot);
    pygame.draw.rect(surface, white, plot, 1);

    for i in range(6):
        x = plot.x + int(plot.width * i / 5);
        pygame.draw.line(surface, gray, (x, plot.y), (x, plot.bottom), 1);

    for i in range(5):
        y = plot.y + int(plot.height * i / 4);
        pygame.draw.line(surface, gray, (plot.x, y), (plot.right, y), 1);

    heading = font.render("Market / Research Chart", True, yellow);
    surface.blit(heading, (chart.x + 25, chart.y + 18));

    def map_point(index, value, count):
        x = plot.x + int(index * plot.width / max(1, count - 1));
        y = plot.bottom - int((value - min_y) * plot.height / (max_y - min_y));
        return x, y;

    for s, name in enumerate(normalized.keys()):
        values = normalized[name];
        points = [map_point(i, values[i], len(values)) for i in range(len(values))];
        pygame.draw.lines(surface, SERIE_COLORS[s % len(SERIE_COLORS)], False, points, 2);

    legend_y = chart.bottom - 40;
    for s, name in enumerate(normalized.keys()):
        x = chart.x + 30 + (s % 3) * 200;
        y = legend_y + (s // 3) * 22;
        color = SERIE_COLORS[s % len(SERIE_COLORS)];
        pygame.draw.rect(surface, color, (x, y + 4, 12, 12));
        surface.blit(small.render(name, True, color), (x + 22, y));

    surface.blit(font.render("Latest Values", True, cyan), (side.x + 20, side.y + 18));
    surface.blit(small.render("Index", True, white), (side.x + 20, side.y + 60));
    surface.blit(small.render("Last", True, white), (side.x + 145, side.y + 60));
    surface.blit(small.render("Var%", True, white), (side.x + 245, side.y + 60));

    for i, name in enumerate(data.keys()):
        rows = data[name];
        first = rows[0][1];
        last = rows[-1][1];
        pct = ((last - first) / first) * 100.0;
        color = SERIE_COLORS[i % len(SERIE_COLORS)];
        y = side.y + 95 + i * 42;

        surface.blit(small.render(name, True, color), (side.x + 20, y));
        surface.blit(small.render("{:.2f}".format(last), True, white), (side.x + 145, y));
        surface.blit(small.render("{:+.2f}%".format(pct), True, color), (side.x + 245, y));

    bar_area = pygame.Rect(bottom.x + 25, bottom.y + 40, 520, 80);
    pygame.draw.rect(surface, (0, 0, 0), bar_area);
    pygame.draw.rect(surface, white, bar_area, 1);

    x = bar_area.x + 8;
    for s, name in enumerate(normalized.keys()):
        values = normalized[name][-8:];
        color = SERIE_COLORS[s % len(SERIE_COLORS)];

        for value in values:
            h = int((value - min_y) * bar_area.height / (max_y - min_y));
            pygame.draw.rect(surface, color, (x, bar_area.bottom - h, 6, h));
            x += 8;

        x += 8;

    surface.blit(font.render("Distribution", True, cyan), (bottom.x + 25, bottom.y + 12));

    info_x = bottom.x + 610;
    surface.blit(font.render("Info", True, cyan), (info_x, bottom.y + 12));

    source = "Simulated fallback" if used_fake else "Yahoo Finance";
    lines = [
        "Range: 1 month",
        "Interval: 1 day",
        "Series: {}".format(len(SYMBOLS)),
        "Source: {}".format(source),
        "Updated: {}".format(time.strftime("%H:%M:%S")),
    ];

    for i, line in enumerate(lines):
        surface.blit(small.render(line, True, white), (info_x, bottom.y + 48 + i * 20));

    status = "SumGUI + ZX Spectrum Palette | NYSE-style dashboard | normalized base=100";
    surface.blit(small.render(status, True, magenta), (rect.x + 25, rect.bottom - 35));


def main():
    data, used_fake = load_market_data();

    app = sg.window(
        "NYSE Dashboard",
        1080,
        720,
        base_width=1080,
        base_height=720,
        scale_mode="fit",
        font_size=20,
        theme="dark",
    );

    small = app.make_font(16);

    #small = pygame.font.SysFont("monospace", app.size(16));

    dash = sg.canvas(
        0,
        0,
        1080,
        720,
        interactive=False,
        auto_redraw=True,
        on_draw=draw_dashboard,
    );

    dash.data = {
        "data": data,
        "used_fake": used_fake,
        "font": app.font,
        "small": small,
    };

    sg.start();


if __name__ == "__main__":
    main();
