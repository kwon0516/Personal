#include <iostream>

class Singleton
{
private:
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

    
    
    return 0;
}