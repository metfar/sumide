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

import sumgui.easy as sg;


sg.window("Mi programa", 960,720);

sg.label("Nombre:", 20, 20, 120, 60);
nombre = sg.textinput(150, 20, 300, 40, placeholder="Nombre");
print(type(nombre.text()));
sg.button(
    "Saludar",
    20,
    80,
    140,
    40,
    do=lambda: sg.alert("Hola " + nombre.text()),
);

sg.start();
