#include <iostream>

enum Enu
{
    ONE,
    TWO,
    THREE,
    FOUR,
    FIVE
};

int main()
{
    int n1 = 1;
    switch (n1)
    {
    case ONE:
        std::cout << "one" << std::endl;
        break;
    
    default:
        std::cout << "false" << std::endl;
        break;
    }    
    return 0;
}