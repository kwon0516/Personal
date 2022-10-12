#include <iostream>
#include <windows.h>

int main()
{
    for (int i = 0; i != 3; i++)
    {
        std::cout << "테스트" << std::endl;
        Sleep(500);
    }

    return 0;
}
