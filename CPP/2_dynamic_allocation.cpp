#include <iostream>

struct Animal
{
    std::string name;
    int age;
    int health;
    int food;
    int clean;
};

void Add_animal(Animal *animal)
{
    std::cout << "Enter animal's name : ";
    std::cin >> animal->name;
    std::cout << "Enter animal's age : ";
    std::cin >> animal->age;

    animal->health = 100;
    animal->food = 100;
    animal->clean = 100;

    std::cout << "Animal add complete!" << std::endl;
}

void Show_animal_list(Animal *(*list), int animal_count)
{
    for (int i = 0; i != animal_count; i++)
    {
        std::cout << i << " : " << (*list[i]).name << std::endl;
    }
}

void Show_state(Animal *animal)
{
    std::cout << "Animal's name : " << animal->name << std::endl;
    std::cout << "Animal's age : " << animal->age << std::endl;
    std::cout << "Animal's health : " << animal->health << std::endl;
    std::cout << "Animal's food : " << animal->food << std::endl;
    std::cout << "Animal's clean : " << animal->clean << std::endl;
}

void Play(Animal *animal)
{
    animal->health += 20;
    animal->food -= 20;
    animal->clean -= 10;
    std::cout << "Play complete!" << std::endl;
}

void Food(Animal *animal)
{
    animal->health += 20;
    animal->food += 20;
    std::cout << "Food complete!" << std::endl;
}

void Shower(Animal *animal)
{
    animal->health += 10;
    animal->food -= 10;
    animal->clean -= 20;
    std::cout << "Shower complete!" << std::endl;
}

bool Check_animal_count(int animal_count)
{
    if (animal_count == 0)
    {
        return false;
    }
    return true;
}


int main()
{
    Animal *list[10];
    int animal_count = 0;

    for (;;)
    {
        int select_menu = 0;
        int select_animal_num = 0;

        std::cout << '\n';
        std::cout << "1. Add new animal" << std::endl;
        std::cout << "2. Animal's state show" << std::endl;
        std::cout << "3. Play" << std::endl;
        std::cout << "4. Food" << std::endl;
        std::cout << "5. Shower" << std::endl;
        std::cout << "Select menu : ";
        std::cin >> select_menu;
        std::cout << '\n';

        if (!Check_animal_count(animal_count) && select_menu != 1)
        {
            std::cout << "No" << std::endl;
            continue;
        }

        switch (select_menu)
        {
        case 1:
            list[animal_count] = new Animal;
            Add_animal(list[animal_count]);
            animal_count += 1;
            break;
        case 2:
            Show_animal_list(list, animal_count);
            std::cout << "Select animal's number : ";
            std::cin >> select_animal_num;
            Show_state(list[select_animal_num]);
            break;
        case 3:
            Show_animal_list(list, animal_count);
            std::cout << "Select animal's number : ";
            std::cin >> select_animal_num;
            Play(list[select_animal_num]);
            break;
        case 4:
            Show_animal_list(list, animal_count);
            std::cout << "Select animal's number : ";
            std::cin >> select_animal_num;
            Food(list[select_animal_num]);
            break;
        case 5:
            Show_animal_list(list, animal_count);
            std::cout << "Select animal's number : ";
            std::cin >> select_animal_num;
            Shower(list[select_animal_num]);
            break;
        // test code
        case 6:
            for(int i = 0; i != animal_count; i++)
            {
                std::cout << list[i]->name << std::endl;
            }
            break;
        
        default:
            break;
        }
    }
    
    return 0;
}