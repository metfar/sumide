#include <iostream>

int main()
{
    std::cout << R"({"schema":"sum.chart/1","kind":"bar","title":"Shared chart from C++","categories":["A","B","C"],"series":[{"name":"value","values":[25,50,35],"x_values":[]}]})" << '\n';
    return 0;
}
