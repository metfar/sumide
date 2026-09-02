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

import numpy as np;
import pygame;
import sumgui.easy as sg;


def euler_equations(omega, inertia):
    w1, w2, w3 = omega;
    return np.array([
        ((inertia[1] - inertia[2]) / inertia[0]) * w2 * w3,
        ((inertia[2] - inertia[0]) / inertia[1]) * w3 * w1,
        ((inertia[0] - inertia[1]) / inertia[2]) * w1 * w2,
    ], dtype=float);


def rk4_step(func, y, dt, inertia):
    k1 = func(y, inertia);
    k2 = func(y + 0.5 * dt * k1, inertia);
    k3 = func(y + 0.5 * dt * k2, inertia);
    k4 = func(y + dt * k3, inertia);
    return y + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4);


def simulate(inertia, omega0, tmax=50.0, steps=800):
    t = np.linspace(0.0, tmax, steps);
    dt = t[1] - t[0];
    sol = np.zeros((len(t), 3), dtype=float);
    sol[0] = np.array(omega0, dtype=float);

    for n in range(1, len(t)):
        sol[n] = rk4_step(euler_equations, sol[n - 1], dt, inertia);

    return t, sol;


def draw_plot(canvas, surface, rect):
    t = canvas.data["t"];
    sol = canvas.data["sol"];
    font = canvas.data["font"];

    pygame.draw.rect(surface, (28, 28, 28), rect);

    plot = pygame.Rect(rect.x + 55, rect.y + 40, rect.width - 75, rect.height - 105);

    min_x = float(t[0]);
    max_x = float(t[-1]);
    min_y = -1.15;
    max_y = 1.15;

    pygame.draw.rect(surface, (175, 175, 175), plot, 1);

    for i in range(6):
        x = plot.x + int(i * plot.width / 5);
        pygame.draw.line(surface, (80, 80, 80), (x, plot.y), (x, plot.bottom), 1);

    for i in range(5):
        y = plot.y + int(i * plot.height / 4);
        pygame.draw.line(surface, (80, 80, 80), (plot.x, y), (plot.right, y), 1);

    def map_point(x, y):
        sx = plot.x + int((x - min_x) * plot.width / (max_x - min_x));
        sy = plot.bottom - int((y - min_y) * plot.height / (max_y - min_y));
        return sx, sy;

    colors = [
        (80, 170, 255),
        (255, 170, 60),
        (90, 220, 90),
    ];

    labels = [
        "omega 1 - eje mayor",
        "omega 2 - eje intermedio",
        "omega 3 - eje menor",
    ];

    for serie in range(3):
        points = [map_point(float(t[i]), float(sol[i, serie])) for i in range(len(t))];
        pygame.draw.lines(surface, colors[serie], False, points, 2);

    title = font.render("Teorema del Eje Intermedio", True, (235, 235, 235));
    surface.blit(title, (rect.x + 20, rect.y + 10));

    xlabel = font.render("Tiempo", True, (235, 235, 235));
    surface.blit(xlabel, (plot.centerx - xlabel.get_width() // 2, plot.bottom + 12));

    for i, label in enumerate(labels):
        y = rect.bottom - 62 + i * 20;
        pygame.draw.line(surface, colors[i], (rect.x + 70, y + 8), (rect.x + 115, y + 8), 3);
        text = font.render(label, True, (235, 235, 235));
        surface.blit(text, (rect.x + 125, y));


def main():
    t, sol = simulate([3.0, 2.0, 1.0], [0.01, 1.0, 0.0]);

    app = sg.window(
        "Dzhanibekov - SumGUI",
        780,
        720,
        base_width=720,
        base_height=720,
        scale_mode="fit",
        fullscreen=False,
        font_size=18,
        theme="dark",
    );

    chart = sg.canvas(10, 10, 700, 660, interactive=False, auto_redraw=True, on_draw=draw_plot);
    chart.data = {
        "t": t,
        "sol": sol,
        "font": app.font,
    };

    sg.start();


if __name__ == "__main__":
    main();

