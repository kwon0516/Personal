#include <iostream>

void Func(std::string *arr, int length)
{
    for (int i = 0; i < length; i++)
    {
        std::cout << *(arr + i);
    }
    std::cout << std::endl;
}

int main()
{
    std::string str_arr[] = {"hello", ", ", "World", "!"};
    int length = sizeof(str_arr) / sizeof(std::string);

    Func(str_arr, length);
    
    return 0;
}