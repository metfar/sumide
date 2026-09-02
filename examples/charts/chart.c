#include <stdio.h>

int main(void)
{
    puts("{\"schema\":\"sum.chart/1\",\"kind\":\"bar\",\"title\":\"Shared chart from C\",\"categories\":[\"A\",\"B\",\"C\"],\"series\":[{\"name\":\"value\",\"values\":[25,50,35],\"x_values\":[]}]}");
    return 0;
}
