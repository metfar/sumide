# sumBASIC simplified ChartSpec demo - Seaborn renderer
DISPLAY 640,480,65536,AUTO
CHART BAR \
    TITLE "Users by OS" \
    X "Android","Linux","Windows" \
    Y 500,800,600 \
    FONT SIZE 10 \
    RENDERER "seaborn"
PAUSE 0
