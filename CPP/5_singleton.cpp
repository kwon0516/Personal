#include <iostream>

class Singleton
{
private:
    Singleton(){}; // 임의로 인스턴스 생성하는 것을 방지하기 위해 생성자를 private로 지정
    static Singleton *instance;
    int num;

public:
    static Singleton &GetInstance()
    {
        if (instance == NULL)
        {
            std::cout << "create new instance" << std::endl;
            instance = new Singleton();
        }
        return *instance;
    }

    void ChangeNum(int n) {num = n;};

    void PrintNUm() {std::cout << num << std::endl;};
};

Singleton *Singleton::instance = nullptr;

int main()
{
    Singleton &ref1 = Singleton::GetInstance();
    Singleton &ref2 = Singleton::GetInstance();

    ref1.ChangeNum(5);
    ref1.PrintNUm();
    ref2.PrintNUm();

    std::cout << std::endl;

    // Singleton s; // 생성자를 private로 지정해 놓았기 때문에 임의로 생성 불가
    
    return 0;
}