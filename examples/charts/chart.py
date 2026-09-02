#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json;

chart = {
    "schema": "sum.chart/1",
    "kind": "bar",
    "title": "Shared chart from Python",
    "categories": ["A", "B", "C"],
    "series": [{"name": "value", "values": [25, 50, 35], "x_values": []}],
};
print(json.dumps(chart, ensure_ascii=False));
