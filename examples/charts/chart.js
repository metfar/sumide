#!/usr/bin/env node
const chart = {
    schema: "sum.chart/1",
    kind: "bar",
    title: "Shared chart from JavaScript",
    categories: ["A", "B", "C"],
    series: [{name: "value", values: [25, 50, 35], x_values: []}],
};
console.log(JSON.stringify(chart));
