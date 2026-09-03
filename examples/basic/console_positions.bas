# Three historical cursor-placement spellings sharing one logical console.
CLS
GOTOXY 10,5: PRINT "GOTOXY X,Y"
LOCATE 7,10: PRINT "LOCATE Y,X"
# Spectrum AT is zero-based, therefore AT 8,9 maps to terminal row 9, col 10.
PRINT AT 8,9; "PRINT AT Y,X"
