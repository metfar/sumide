# sumBASIC charts + table dashboard.
# Run with: sumbasic --gui --run examples/charts_tables.bas
# Produces charts_tables.png in the current directory.

DISPLAY 960,600,65536,AUTO
COLOR 15,1,1
CLS

Cats = ["Android", "Linux", "Windows"]
Vals = [500, 800, 600]
Rows = [["Android", 500], ["Linux", 800], ["Windows", 600]]

TABLE 20, 20, 260, 150, ["OS", "Users"], Rows, "Users by OS", 10, 12, 10, "monospace"
CHART "LINE", 300, 20, 300, 250, Cats, Vals, "Line", "Users", 10, 12, "monospace"
CHART "BAR", 620, 20, 300, 250, Cats, Vals, "Bars", "Users", 10, 12, "monospace"
CHART "HBAR", 20, 300, 280, 250, Cats, Vals, "Horizontal bars", "Users", 9, 11, "monospace"
CHART "PIE", 320, 300, 280, 250, Cats, Vals, "Pie", "Users", 9, 11, "monospace"
CHART "RADAR", 620, 300, 300, 250, Cats, Vals, "Radar", "Users", 9, 11, "monospace"

BSAVE "charts_tables.png", SCREEN
PRINT "Saved charts_tables.png"
PAUSE .60
SCREEN 0
