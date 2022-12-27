#include <iostream>

class Marine
{
	int hp_;
	int coord_x_, coord_y_;
	int damage_;
	bool is_dead_;

public:
	Marine();
	Marine(int x, int y);

	int attack();
	void be_attacked(int damage_earn);
	void move(int x, int y);

	void show_status();
};

Marine::Marine()
{
	hp_ = 50;
	coord_x_ = coord_y_ = 0;
	damage_ = 5;
	is_dead_ = false;
	show_status();
}

Marine::Marine(int x, int y)
{
	coord_x_ = x;
	coord_y_ = y;
	hp_ = 50;
	damage_ = 5;
	is_dead_ = false;
	show_status();
}

void Marine::move(int x, int y)
{
	coord_x_ = x;
	coord_y_ = y;
}

int Marine::attack() { return damage_; }

void Marine::be_attacked(int damage_earn)
{
	hp_ -= damage_earn;
	
	if (!hp_) is_dead_ = true;
}

void Marine::show_status()
{
	std::cout << " *** Marine *** " << std::endl;
	std::cout << " Location : ( " << coord_x_ << " , " << coord_y_ << " ) " << std::endl;
	std::cout << " HP : " << hp_ << std::endl;
}



int main()
{
	Marine* marines[100];

    marines[0] = new Marine(2, 3);
    marines[1] = new Marine(3, 5);

    // marines[0]->show_status();
    // marines[1]->show_status();

    int arr[10] = {0, };

    for (int i : arr)
    {
        std::cout << i << " ";
    }

    std::cout << std::endl;
	
	return 0;
}