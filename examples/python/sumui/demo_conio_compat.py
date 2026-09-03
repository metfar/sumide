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

from sumgui.conio import install;
from sumui.conio import *;


def main():
    install(cols=80, rows=25, title="Σ Sum conio-compatible demo");
    textbackground(BLUE);
    textcolor(WHITE);
    clrscr();
    gotoxy(10, 5);
    cputs("conio.h-compatible text over sumGUI");
    gotoxy(10, 7);
    textcolor(LIGHTCYAN);
    cputs("Press any key to close...");
    getch();


if __name__ == "__main__":
    main();
