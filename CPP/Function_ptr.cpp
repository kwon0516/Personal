#include <iostream>

void Add(int n1, int n2) {std::cout << n1 + n2 << std::endl;}
void Min(int n1, int n2) {std::cout << n1 - n2 << std::endl;}

int main()
{
    int user_select = 0;
    int n1 = 7;
    int n2 = 5;
    void (*fp[2])(int, int);

    fp[0] = Add;
    fp[1] = Min;

    std::cout << "1 : Add \n2 : Min" << std::endl;
    std::cout << "select number : ";
    std::cin >> user_select;

    if (user_select * 4 > sizeof(fp)) {std::cout << "wrong number!" << std::endl;}
    else {fp[user_select - 1](n1, n2);}
    
    return 0;
}

// https://coding-factory.tistory.com/638