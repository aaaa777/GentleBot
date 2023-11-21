#include <iostream>
#include <string>

using namespace std;

// mainをスッキリさせたいプログラム

class Neko
{
private:
    string name;
    int age;
public:
    Neko(string n, int a) : name(n), age(a) {}

    void naku()
    {
        cout << name << "(" << age << ") : んんんにゃおん！" << endl;
    }
};

// ユーザー入力部分を分けた
static string UserInput(string caption)
{
    string input;
    cout << caption << endl;
    cin >> input;
    return input;
}

static string AskName()
{
    return UserInput("猫に名前をつけてください。");
}

static int AskAge()
{
    return UserInput("猫の年齢を入力してください。");
}

int main()
{
    string name = AskName();
    int age = AskAge();
    Neko neko(name, age);
    
    neko.naku();
}