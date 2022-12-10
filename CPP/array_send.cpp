#include <iostream>

void Display(std::string *arr, int length)
{
    arr[0] = "asd";
    arr[1] = "3f2";
    for (int i = 0; i != length; i++)
    {
        std::cout << arr[i];
    }
    std::cout << std::endl;
}

int main()
{
    std::string arr[] = {"Hello", ", ", "World", "!"};
    int length = sizeof(arr) / sizeof(std::string);

    Display(arr, length);
    
    return 0;
}