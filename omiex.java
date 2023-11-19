

ロジックは置いといてネスト深さの話で言うと、読みやすくするなら関数化するのが一番いいと思う

// example
ケース1
```
// switch文は使うな！！！
String color = "red";
int colorCode;
switch(color)
{
    // 白が200色あったらどうすんねん！！！
    case "red":
        colorCode = 1;
        break;
    case "blue":
        colorCode = 2;
        break;
    default:
        colorCode = 0;
        break;
}
System.out.println(colorCode);
```
↓ 改善

```
// 関数とreturnとifで代用できる、しろ！！！
int GetColorCode(String color)
{
    // returnは関数を抜けるので、elseすらいらない！！！
    // その後の処理をしなくていい場合は、if文の中でreturnする！！！
    if(color == "red") return 1;
    if(color == "blue") return 2;
    return 0;
}
int colorCode = GetColorCode("red");
System.out.println(colorCode);
```

ケース2
```
// これがクソネストだ！！！
int[][] image = new int[100][100];
int[][] output = new int[100][100];

if(image != null)
{
    for(int y = 0; y < image.length; y++)
    {
        /// こんなところでnullチェックすな！！！
        if(image[y] != null)
        {
            for(int x = 0; x < image[0].length; x++)
            {
                if(image[y][x] < 127)
                {
                    output[y][x] = 0;
                }
                else
                {
                    output[y][x] = 255;
                }
            }
        }
    }
}
```
↓ 改善

```
int[][] ConvertImage2BinaryArray(int[][] image)
{
    int[][] output = new int[100][100];
    for(int y = 0; y < image.length; y++)
        for(int x = 0; x < image[0].length; x++)
            output[y][x] = ConvertPixel2Binary(image[y][x]);
}

int ConvertPixel2Binary(int pixel)
{
    // ちなみに3項演算子は複雑にすると可読性がゴミだ！！！
    return pixel < 127 ? 0 : 255;
}


void main()
{
    int[][] image = new int[100][100];
    if(image != null)
    {
        int[][] output = ConvertImage2BinaryArray(image);
    }
}

```
```

```

```
        

