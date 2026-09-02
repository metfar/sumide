<?php
$chart = [
    "schema" => "sum.chart/1",
    "kind" => "bar",
    "title" => "Shared chart from PHP",
    "categories" => ["A", "B", "C"],
    "series" => [["name" => "value", "values" => [25, 50, 35], "x_values" => []]],
];
echo json_encode($chart, JSON_UNESCAPED_UNICODE), PHP_EOL;
?>
