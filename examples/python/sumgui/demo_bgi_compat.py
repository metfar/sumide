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

from sumui.bgi import *;


def main():
    initgraph(DETECT, 12, "");
    setbkcolor(BLUE);
    cleardevice();
    setcolor(LIGHTCYAN);
    setfillstyle(SOLID_FILL, CYAN);
    circle(320, 210, 90);
    floodfill(320, 210, LIGHTCYAN);
    setcolor(WHITE);
    setfillstyle(SOLID_FILL, WHITE);
    circle(285, 185, 12);
    circle(355, 185, 12);
    floodfill(285, 185, WHITE);
    floodfill(355, 185, WHITE);
    setcolor(LIGHTMAGENTA);
    arc(320, 220, 220, 320, 55);
    setcolor(WHITE);
    settextstyle(DEFAULT_FONT, HORIZ_DIR, 2);
    outtextxy(185, 345, "Sum BGI-compatible demo");
    backend = globals().get("_backend", None);
    # The default sumGUI window stays open until ESC/window close.
    try:
        import sumui.bgi as bgi;
        if getattr(bgi, "_backend", None) is not None and hasattr(bgi._backend, "wait_for_close"):
            bgi._backend.wait_for_close();
    finally:
        closegraph();


if __name__ == "__main__":
    main();
