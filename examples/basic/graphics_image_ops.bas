# sumBASIC graphics image operations.
# Demonstrates COLOR, PAINT/FILL, GET/PUT and BSAVE.
# Run with: sumbasic --gui --run examples/graphics_image_ops.bas

DISPLAY 640,480,65536,AUTO
COLOR 15,1,1
CLS

# Draw and fill two boxes.
RECTANGLE 40, 40, 180, 120, 11
PAINT (50, 50), 3, 11
RECTANGLE 260, 60, 160, 100, 13
FILL (270, 70), 5, 13

# Copy regions directly, without an intermediate variable.
PUT (80, 240), GET(40, 40, 180, 120)
PUT (50,50), GET(150,150,10,10)

# Capture to a reusable image variable and draw it elsewhere.
Tile = GET(260, 60, 160, 100)
PUT (330, 250), Tile

# Both GET forms can be saved directly.
BSAVE "graphics_full.png", SCREEN
BSAVE "graphics_part.png", GET (40,40)-(219,159)
BSAVE "graphics_tile.png", Tile

PRINT "Saved graphics_full.png, graphics_part.png and graphics_tile.png"
PAUSE 250
SCREEN 0
