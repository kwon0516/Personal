// #include <iostream>

// class Animal
// {
//     private:
//     int food;
//     int weight;

//     public:
//     void set_animal(int _food, int _weight)
//     {
//         food = _food;
//         weight = _weight;
//     }

//     void increase_food(int inc)
//     {
//         food += inc;
//         weight += (inc / 3);
//     }

//     void view_stat()
//     {
//         std::cout << "food : " << food << std::endl;
//         std::cout << "weight : " << weight << std::endl;
//     }
// };

// int main()
// {
//     Animal animal;

//     animal.set_animal(100, 50);
//     animal.increase_food(30);

//     animal.view_stat();

//     return 0;
// }
// ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ //
#include <iostream>

class Date
{
    private:
    int year_;
    int month_;
    int day_;

    public:
    void SetData(int year, int month, int day)
    {
        year_ = year;
        month_ = month;
        day_ = day;
    }
    
    void AddDay(int inc)
    {
        int result_day = day_ + inc;

        if (result_day > 31)
        {
            month_++;
            day_ = result_day - 31;
            return;
        }
        day_ += inc;
    }

    void AddMonth(int inc)
    {
        int result_month = month_ + inc;
        
        if (result_month > 12)
        {
            year_++;
            month_ = result_month - 12;
            return;
        }
        month_ += inc;
    }

    void AddYear(int inc)
    {
        year_ += inc;
    }

    void ShowDate()
    {
        std::cout << year_ << '/' << month_ << '/' << day_ << std::endl;
    }
};

int main()
{
    Date date;

    date.SetData(2017, 11, 22);
    date.ShowDate();

    date.AddDay(9);
    date.ShowDate();
    
    return 0;
}