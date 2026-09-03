# Modern DISPLAY with active/visible pages and manual refresh.
DISPLAY 640,480,65536,MANUAL,2,1,0
COLOR 15,1,1
CLS
RECTANGLE 60,60,520,340,11
CIRCLE 320,230,110,13
OUTTEXTXY 185,390,"Prepared off-screen on page 1",15,16,"monospace"

# Page 0 remains visible while page 1 is drawn. Flip when complete.
DISPLAY VISIBLE 1
DISPLAY UPDATE
PAUSE 3

# Copy page 1 back to page 0 and display it.
COPY SCREEN FROM 1 TO 0
DISPLAY VISIBLE 0
DISPLAY UPDATE
PAUSE 3
SCREEN 0
