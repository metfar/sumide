#!/usr/bin/env ruby
require "json"
chart = {
  schema: "sum.chart/1",
  kind: "bar",
  title: "Shared chart from Ruby",
  categories: ["A", "B", "C"],
  series: [{name: "value", values: [25, 50, 35], x_values: []}],
}
puts JSON.generate(chart)
