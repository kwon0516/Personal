#include <iostream>

struct Animal
{
    std::string name;
    int age;
    int health = 100;
    int food = 100;
    int clean = 100;

    void Play()
    {
        health += 10;
        food -= 20;
        clean -= 10;
    }

    void ShowState()
    {
        std::cout << "name : " << name << std::endl;
        std::cout << "age : " << age << std::endl;
        std::cout << "health : " << health << std::endl;
        std::cout << "food : " << food << std::endl;
        std::cout << "clean : " << clean << std::endl;
    }
};


int main()
{
    Animal poppy;

    Animal *ptr_arr[10];

    poppy.name = "poppy";
    poppy.age = 10;

    poppy.Play();

    poppy.ShowState();

    

    return 0;
}