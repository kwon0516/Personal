#include <iostream>

int main()
{
    int arr[3] = {1, 2, 3};
    int (&arr_ref)[3] = arr;

    for (int i = 0; i != 3; i++)
    {
        std::cout << arr_ref[i] << std::endl;
    }
    
    return 0;
}

// 래퍼런스와 포인터의 차이
// -> 래퍼런스는 선언과 동시에 초기화를 해야 함(대상을 지정)
// -> 포인터는 선언 후 나중에 초기화가 가능
// -> 래퍼런스는 한 번 지정하면 값을 변경하는 것이 불가능
// -> 래퍼런스는 메모리 상에 존재하지 않을 수 있다(포인터는 8바이트 할당)
// -> 래퍼런스의 래퍼런스, 래펴런스의 배열, 래퍼런스의 포인터는 존재할 수 없다.

// #include <iostream>

// int main()
// {

    
//     return 0;
// }