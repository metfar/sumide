# sumBASIC charts + table dashboard.
# Run with: sumbasic --gui --run examples/charts_tables.bas
# Produces charts_tables.png in the current directory.

SCREEN 960, 600
COLOR 15, 0, 0
CLS

Cats = ["Android", "Linux", "Windows"]
Vals = [500, 800, 600]
Rows = [["Android", 500], ["Linux", 800], ["Windows", 600]]

TABLE 20, 20, 260, 150, ["OS", "Users"], Rows, "Users by OS"
CHART "LINE", 300, 20, 300, 250, Cats, Vals, "Line", "Users"
CHART "BAR", 620, 20, 300, 250, Cats, Vals, "Bars", "Users"
CHART "HBAR", 20, 300, 280, 250, Cats, Vals, "Horizontal bars", "Users"
CHART "PIE", 320, 300, 280, 250, Cats, Vals, "Pie", "Users"
CHART "RADAR", 620, 300, 300, 250, Cats, Vals, "Radar", "Users"

BSAVE "charts_tables.png", SCREEN
PRINT "Saved charts_tables.png"
PAUSE 300
SCREEN 0
