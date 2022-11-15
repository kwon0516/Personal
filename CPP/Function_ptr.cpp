#include <iostream>

void func1(int n1, int n2)
{
    std::cout << n1 + n2 << std::endl;
}

void func2(int n1, int n2)
{
    std::cout << n1 * n2 << std::endl;
}

int main()
{
    void (*ptr[2])(int, int) = {&func1, &func2};
    
    (*ptr[0])(2, 5);
    ptr[0](2, 5);
    
    return 0;
}