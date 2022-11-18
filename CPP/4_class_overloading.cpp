#include <iostream>

// 오버로딩 : 같은 이름의 함수를 여러 개 선언(매개변수가 다른)
// 오버로딩 함수는 호출 시 인자를 기준으로 구분을 한다
// 호출 시 인자와 일치하는 함수가 없는 경우 가장 근접한 함수를 호출한다.

void print(int x) {std::cout << "int : " << x << std::endl;}
// void print(char x) {std::cout << "char : " << x << std::endl;}
void print(double x) {std::cout << "double : " << x << std::endl;}

int main()
{
    int a = 1;
    char b = 'c';
    double c = 3.2f;

    print(a);
    print(b);
    print(c);
    
    return 0;
}