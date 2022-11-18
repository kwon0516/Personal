#include <iostream>
#include <stdio.h>

int main()
{
    std::string str;
    long num = 123456789;
    long n = 10;

    std::cout << num << std::endl;
    std::cout << n << std::endl;
    printf("%d \n", num);
    printf("%ld \n", num);
    printf("%d \n", n);
    printf("%ld \n", n);
    
    return 0;
}