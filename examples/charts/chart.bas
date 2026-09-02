# sumBASIC emits the backend-neutral sum.chart/1 interchange format.
Q$ = CHR$(34)
PRINT "{"
PRINT Q$; "schema"; Q$; ":"; Q$; "sum.chart/1"; Q$; ","
PRINT Q$; "kind"; Q$; ":"; Q$; "bar"; Q$; ","
PRINT Q$; "title"; Q$; ":"; Q$; "Shared chart from sumBASIC"; Q$; ","
PRINT Q$; "categories"; Q$; ":["; Q$; "A"; Q$; ","; Q$; "B"; Q$; ","; Q$; "C"; Q$; "],"
PRINT Q$; "series"; Q$; ":[{"
PRINT Q$; "name"; Q$; ":"; Q$; "value"; Q$; ","
PRINT Q$; "values"; Q$; ":[25,50,35],"
PRINT Q$; "x_values"; Q$; ":[]}]}"
