#include <iostream>

class C
{
	public:
	C();
	~C();
	void DefaultFunction(bool b = false);
};

C::C()
{
	std::cout << "Create!" << std::endl;
}

C::~C()
{
	std::cout << "Destroy!" << std::endl;
}

void C::DefaultFunction(bool b)
{
	if (b) std::cout << "True" << std::endl;
	else std::cout << "False" << std::endl;
}

int main()
{
	C c;
	
	c.DefaultFunction();
	c.DefaultFunction(true);
	
	std::cout << '1' << std::endl;
	return 0;
	std::cout << '2' << std::endl;
}