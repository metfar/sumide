#!/bin/bash
cat <<'JSON'
{"schema":"sum.chart/1","kind":"bar","title":"Shared chart from Bash","categories":["A","B","C"],"series":[{"name":"value","values":[25,50,35],"x_values":[]}]}
JSON
