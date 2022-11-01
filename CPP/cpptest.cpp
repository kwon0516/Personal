#include <iostream>
#include <vector>

void Add(int n1 = 0, int n2 = 0)
{
    std::cout << "↓Add result↓" << std::endl;
    std::cout << n1 * n2 << std::endl;
}

void Min(int n1 = 0, int n2 = 0)
{
    std::cout << "↓Min result↓" << std::endl;
    std::cout << n1 * n2 << std::endl;
}

int main()
{
    int n1 = 5;
    int n2 = 8;

    void (*arr)[2] = {Add, Min};

    return 0;
}