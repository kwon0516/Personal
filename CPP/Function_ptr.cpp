#include <iostream>

void Func()
{
    std::cout << "Function pointer test!" << std::endl;
}

int main()
{
    void (*ptr_func)() = Func;

    (*ptr_func)();
    
    return 0;
}