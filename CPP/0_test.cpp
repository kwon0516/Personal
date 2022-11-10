#include <iostream>

void print(int *arr, int length)
{
    for (int i = 0; i != length; i++)
    {
        std::cout << arr[i] << std::endl;
    }
}

int main()
{
    int arr[3] = {1, 3, 5};

    print(arr, 3);
    
    return 0;
}