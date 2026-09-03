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
from sumui import conio, stdio;


def main():
    install(cols=80, rows=25, title="Σ Sum stdio/conio demo");
    conio.textbackground(conio.BLUE);
    conio.textcolor(conio.WHITE);
    conio.clrscr();
    stdio.use_conio();
    stdio.printf("stdio-compatible printf routed through the active Sum console.\n");
    stdio.printf("Same call works with the TUI or GUI conio backend.\n\n");
    stdio.printf("Press any key...");
    conio.getch();


if __name__ == "__main__":
    main();
