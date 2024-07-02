# Java 笔记

Tags: 学习笔记

-----
[TOC]

-----
> 作业部落链接：https://www.zybuluo.com/SovietPower/note/2200494
> 参考：
> https://www.runoob.com/java/java-tutorial.html


## 安装
下载：https://www.oracle.com/java/technologies/downloads/#jdk17-windows
可以直接用exe安装，否则还要添加环境变量。
cmd中测试`java -version, javac`命令。

### 使用vscode
安装插件 Extension Pack for Java。
在`setting.json`里添加插件设置：
```
"java.import.gradle.java.home": "F:\\Programs\\Java\\jdk-17.0.2",
"java.configuration.runtimes": [
	{
		"name": "JavaSE-17",
		"path": "F:\\Programs\\Java\\jdk-17.0.2"
	},
	{
		"name": "JavaSE-1.8",
		"path": "F:\\Programs\\Java\\jdk1.8.0_321"
	}
]
```

**测试**
Ctrl+Shift+P，输入`java:create java Project`，选择`No build tools`，输入路径、项目名，可创建项目。
点击项目`src`下的`App.java`，在主类处可Run运行该项目的`main`。
使用`Code Runner`也可以运行单个Java。

### 使用 IDEA

**使用 IDEA 前**

要修改 Maven 的本地仓库目录，不然会占 C 盘。
在 设置 - 构建 - 构建工具 - Maven 下设置，顺序改一下配置目录。

在 idea 安装目录的 bin 下，修改`idea.properties`，修改`idea.config.path=H:/JetBrains/.IntelliJ/config`以及`system, plugins, log`，否则会在 C 盘（注意路径用斜杠）。
config 要么早改，要么还是不改了，配置会清空，记得备份。

在 file - manage ide settings 下可同步、导入导出配置。




### Maven环境
> http://blog.hotsun168.com/index.php/archives/16/



-----
## 简介
https://www.runoob.com/java/java-intro.html

Java为半解释半编译型语言。通过`javac`将`.java`编译为字节代码的`.class`文件，通过`java`运行`.java`文件。

> JDK（Java Development Kit ）：编写Java程序的程序员使用的软件，为程序员提供一些已经封装好的 java 类库。
> JRE（Java Runtime Environment）：运行Java程序的用户使用的软件。
> Server JRE （Java SE Runtime Environment）：服务端使用的 Java 运行环境。
> SDK（Software Development Kit）：软件开发工具包，在Java中用于描述1998年~2006年之间的JDK。
> DAO（Data Access Object）：数据访问接口，数据访问，顾名思义就是与数据库打交道。
> MVC（Model View Controller）：模型(model)－视图(view)－控制器(controller)的缩写，一种软件设计典范，用于组织代码用一种业务逻辑和数据显示分离的方法。


-----
## 语法
### 基础语法及规范
https://www.runoob.com/java/java-basic-syntax.html

文档注释/说明注释：https://www.runoob.com/java/java-documentation.html


### 类、对象、文件规则
https://www.runoob.com/java/java-object-classes.html

- 一个源文件中只能有一个或没有 public 类
- 一个源文件可以有多个非 public 类
- 源文件的名称应该和 public 类的类名保持一致


### 基本数据类型、常量、字面量
https://www.runoob.com/java/java-basic-datatypes.html

String不是基本数据类型。使用时首字母也应大写。
`"str"`表示字符串，`'c'`表示字符。

通过`obj instanceof CLASS_NAME`判断一个对象是否属于某个类。

使用字面量时，前缀`0`表示 8 进制，而前缀`0x`表示 16 进制, 如：
```java
int decimal = 100;
int octal = 0144;
int hexa =  0x64;
```

boolean 类型为逻辑类型，值为逻辑值；其它类型为数值类型，值为数值。逻辑类型和数值类型间**不可转换**，逻辑值和数值间**无法比较**（会CE）。
所以**不可用**：`while(1)`等，如果`x`不是`boolean`，也不能用`if(x), if(!x)`，应`if(x!=0), if(x==0)`。

注意对于对象来说**`==`是比较地址**，字符串应使用**`equals`**比较。
但基本类型直接用`==`，如`charA==charB`。

数据类型转换规则：
1. 不能对 boolean 类型进行类型转换（同样不能给 boolean 赋值其它类型的值）。
2. 不能把对象类型转换成不相关类的对象。
3. 在把容量大的类型转换为容量小的类型时必须使用强制类型转换；反之不用，会自动转换。
4. 转换过程中可能导致溢出或损失精度。
5. 浮点数到整数的转换是通过截断（舍弃小数）得到，而不是四舍五入。

比int类型小的数值类型做运算时，java在编译时会将它们统一转换成int，即结果也为int。当比int类型大的数值类型做运算时，会将它们转换成它们中最大的类型。


### 泛型
> 泛型是假的，实际上全部都是Object，所以java容器里只能是装箱后的引用类型如Integer/Boolean等，不能是值类型如int/boolean之类的，C#就没这个问题，值类型可以直接放进容器。


### 变量
Java的变量类型：

**类变量**：独立于方法之外的变量，与类绑定，用 static 修饰。
有默认值（`0, false 或 null`)。可在类中任意一个位置声明。
是属于某个对象的属性，创建实例对象后，其中的实例变量才会被分配空间。
`final`修饰的类变量可在静态方法中赋值（声明时不赋值）。

**实例变量**：独立于方法之外的变量，与对象实例绑定，没有 static 修饰。
有默认值（`0, false 或 null`)。可在类中任意一个位置声明。
不属于某个实例对象，属于类。只要程序加载了类的字节码，静态变量就会被分配空间，无需创建实例对象。

**局部变量**：类的方法中的变量。
访问修饰符不能用于局部变量；在栈上分配；没有默认值，所以局部变量被声明后，**必须初始化**，否则不可使用（会CE）。


### 修饰符
https://www.runoob.com/java/java-modifier-types.html


### switch

- case 语句中的值的数据类型必须与变量的数据类型相同，而且只能是常量或者字面常量。
- 当变量的值与 case 语句的值相等时，那么 case 语句之后的语句开始执行，**直到** break 语句出现**才会**跳出 switch 语句（一旦成功匹配，则之后的 case 无须进行匹配，都认为已匹配成功，会依次执行所有 case 中的内容会全部执行直到 break）。
- `default`的位置任意。因为是哈希表直接跳转，所以能不能匹配到元素与`default`的位置无关。


### Number, Character
一般使用的 byte、int、long、double 等，是内置数据类型。
因为有时需将内置数据类型作为对象来使用，所以 Java 为每一个内置数据类型提供了对应的包装类：Integer、Long、Byte、Double、Float、Short，它们都是 Number 的子类。Number 类属于 java.lang 包（会自动导入`java.lang.*`）。
Character 是 char 的包装类。
包装类对象为该数据类型提供了许多方法。但是不包装也可使用，如`char c; Character.isDigit(c)`。
这种由编译器特别支持的包装称为装箱。当内置数据类型被当作对象使用时，编译器**将内置类型装箱为包装类**。当使用对象的数值时，编译器把**对象拆箱为内置数据类型**。

非 new 生成的 Integer 变量（直接赋值）与`new Integer()`生成的变量地址不同。非 new 生成的 Integer 变量指向的是 java 常量池中的对象，而`new Integer()`生成的变量指向堆中新建的对象（String 同理）。
使用`obj = Number/Character.valueOf(x)`（`x`为数值）新建对象，与直接赋值的非 new 生成对象相同（规则也相同，$[–128,127]$内会重用，否则不会）。

对于在$[–128,127]$（默认）内的值，被装箱后，该对象会被放在内存里进行**重用**（即使有多个相同数值的对象，它们的实际地址也是相同的），即已经预定义了这些数值的对象。
但是如果超出了这个区间，系统会重新`new`一个对象，此时多个相同数值的对象存在不同的位置。
当对象和数值进行比较时，会进行拆箱比较其数值。

```java
public class A {
	public static void main(String[] args)
	{
		Integer i = new Integer(1);
        Integer j = 1;
        Integer k = Integer.valueOf(1);
        System.out.printf("%b %b %b\n", i == j, i == k, j == k);
	
		Integer a = 128, b = 128;
		Integer c = 127, d = 127;
	    int x = 1, y = 1;
	
	    System.out.printf("%d %d %d %d\n", a, b, c, d);
	    System.out.println(a == b);
	    System.out.println(a.equals(b));
	    System.out.println(c == d);
	    System.out.println(x == y);
	    
	    System.out.println(a == 128);
	}
}
/*
输出：
false false true
128 128 127 127
false
true
true
true
true
*/
```


### String
Java 的 String 为一个类，而不是基本数据类型。

String 创建的字符串存储在公共池中，而 new 创建的字符串对象在堆上：
```java
public class A {
	public static void main(String[] args)
	{
		String s1 = "abc";				// String 直接创建
		String s2 = s1;					// 相同引用
		String s3 = new String("abc");	// String 对象创建
        System.out.printf("%b %b %b\n", s1 == s2, s1 == s3, s2 == s3);
        System.out.printf("%b %b %b\n", s1.equals(s2), s1.equals(s3), s2.equals(s3));
	}
}
/*
输出：
true false false
true true true
*/
```

与基本数据类型不同，String 对象保存的值不可修改，只能新建一个对象。
如需修改，使用[StringBuffer 和 StringBuilder 类](https://www.runoob.com/java/java-stringbuffer.html)。

使用`String.concat()`或`+`连接字符串（包括字符粗常量）。
`String.format()`可创建**格式化字符串**（用法与`printf`相同，但返回字符串）

字符串常量之间进行`+`，会直接计算得出常量结果。值相同的常量只会创建一次，所以它们地址相同。
但对字符串常量使用`concat`，或对字符串变量使用`+`（即使是与常量），不会直接进行计算，而是会创建 StringBuilder 或 StringBuffer 对象，使用`append`连接。这些对象中的每个都有自己的地址。
这两种方式得到的相同字符串，地址也是不同的。

```java
public class HelloWorldA {

	public static void main(String[] args)
	{
		String t1="a"+"b"+"c";
		String t2="abc";
		System.out.printf("t: %b %b\n", t1==t2, t1.equals(t2));
		
		String s1 = "ab";
		String s2 = "abc";
		String s3 = s1 + "c";
        System.out.printf("s: %b %b %b\n", s1 == s2, s1 == s3, s2 == s3);
        System.out.printf("s: %b\n", s2.equals(s3));

		String q1 = "a".concat("b").concat("c");
		String q2 = "a"+"b"+"c";
		String q3 = "abc";
        System.out.printf("q: %b %b %b\n", q1 == q2, q1 == q3, q2 == q3);
        System.out.printf("q: %b %b %b\n", q1.equals(q2), q1.equals(q3), q2.equals(q3));
    }
}
/*
输出：
t: true true
s: false false false
s: true
q: false false true
q: true true true
*/
```

**常用函数**
![](https://img.jbzj.com/file_images/article/201909/201994150649242.jpg)
若要获取单个字符，不能用`[]`，需用`charAt`或`substring`。
String不可迭代（for遍历），所以遍历只能枚举`charAt(i)`。


### StringBuffer 和 StringBuilder todo
> https://www.runoob.com/java/java-stringbuffer.html

字符串要修改时使用，不产生新的未使用对象。




### 数组
> https://www.runoob.com/java/java-array.html

使用`某个类型[]`创建定长数组。


### List
> https://www.runoob.com/java/java-arraylist.html
> https://www.liaoxuefeng.com/wiki/1252599548343744/1265112034799552

动态数组。
有两个子类：`ArrayList`和`LinkedList`。
前者类似`vector`，用数组实现；后者用链表实现。
所以前者可以随机读取，但插入删除复杂度高；后者随机读取的复杂度高，但插入删除可以O(1)。

创建list时不指定类型，则为`Object`，可存任意类型。使用时需自己转换类型。
`List list = new ArrayList();`
如果显式指定类型，则程序运行时会进行类型检查。

map同理：`Map map = new HashMap();`。


### HashMap
> https://www.runoob.com/java/java-hashmap.html
> LinkedHashMap：
> https://baike.baidu.com/item/LinkedHashMap/2576927?fr=aladdin

无序哈希列表。

`HashMap`有一个子类`LinkedHashMap`，其中的元素顺序在遍历时依旧保持插入顺序，


### Iterator
> https://www.runoob.com/java/java-iterator.html

数组用`ListIterator`。


### 方法
参数传递：https://www.zhihu.com/question/31203609
Java **只有值传递**（因为没有指针的概念），基本类型传递值本身，其它对象（包括String）传递指向对象的地址（类似引用传递）。
String未提供setter或改变自身的方法（如`append`），在赋值时会创建新的String对象赋给参数，所以即使是传递了地址，原有对象也不会因参数改变而改变。
注意，很多对象参数使用`=`赋值，并不会改变原有对象，除非用改变自身（而不是返回新的）的相应方法。


### 错误 异常
> https://www.runoob.com/java/java-exceptions.html

**检查型异常（Checked Exception）**
在Java中所有不是RuntimeException派生的Exception都是检查型异常。当函数中存在**可能(?)**抛出检查型异常的操作时（如打开文件），该函数的函数声明中必须包含`throws`，或必须捕获该异常，否则程序终止。如是前者，则调用该函数的函数必须对该异常进行处理，否则也应在函数后声明`throws`。
编译器会检查这类异常，如果在编译时没有处理这些异常（没有`throws`也没`catch`），则无法通过编译。可以强制开发者在运行前就处理。
处理异常的方式就是两种：`throws`或`try catch`。
如果异常用`catch`没匹配到相应类型的错误，则该异常算作没被捕获，程序终止。
`catch`内可以为空，也算捕获并处理了该类型错误（即忽略）。

**非检查型异常/运行时异常（Unchecked Exception/Runtime Exception）**
编译器不会检查这类异常。这类异常一般可以避免，如除0、数组越界、访问null，所以不强制`catch`。
而且一般无法恢复或不可捕获，所以一般让程序直接终止。

使用`throw new Exception()`主动抛出任意异常。

**try-with-resources**
JDK7 之后，Java 新增的 try-with-resource 语法糖来打开资源，并且可以在语句执行完毕后确保每个资源都被自动关闭 。
JDK7 之前所有被打开的系统资源，比如流、文件或者 Socket 连接等，都需要被开发者手动关闭，否则会造成资源泄露将。
```
try (resource declaration) {
  // 使用的资源
} catch (ExceptionType e1) {
  // 异常块
}
```
以上的语法中 try 用于声明和实例化资源，catch 用于处理关闭资源时可能引发的所有异常。
declaration中就要给变量赋值，且之后不能更改。





-----
## 面向对象
### 继承
类不能继承多个类（不能多继承），但可以链式继承（可以多重继承）。
类可以继承多个接口`interface`。
使用`extends [class]`继承一个类，使用`implements [interface1, interface2, ...]`继承多个接口。
`super`表示当前对象的父类，可用来访问父类成员。`this`表示当前对象。

子类拥有父类的非私有属性和方法。

子类不继承父类的构造器（构造方法或构造函数），但它会调用（隐式或显式）父类的构造器。如果父类的构造器带有参数，则必须在子类构造器中显式地通过`super`调用父类的构造器，并传递适当的参数。
如果父类构造器没有参数，则在子类构造器中不需要使用`super`调用父类构造器，系统会自动调用父类的无参构造器。

继承提高了类之间的耦合性。耦合度高会造成代码之间的联系紧密，代码独立性差。
所有的类都继承于`java.lang.Object`。


### final
`final`可修饰变量（类属性、对象属性、局部变量、形参）、方法（类方法、对象方法）和类。
`final`声明的类为最终类，不能被继承（但其属性、方法并不一定是`final`的）。
`final`修饰的方法不能被子类重写。


### override todo
https://www.runoob.com/java/java-override-overload.html


### 抽象
> https://www.runoob.com/java/java-abstraction.html

**抽象类**`abstract class`不能被实例化成对象，其他与一般类相同。抽象类只用来被继承。一个类只能继承一个抽象类。
**抽象方法**不能被直接调用，是一个必须被子类实现的方法的占位符。抽象方法只有声明，没有函数体，具体需由子类实现。

如果一个类包含抽象方法，那么该类必须是抽象类。但抽象类可以有非抽象方法（与一般类相同）。
任何子类必须重写父类的抽象方法，或声明自身为抽象类。
构造方法，类方法（静态方法）不能声明为抽象方法。


-----
## 使用错误
**java.util.ConcurrentModificationException**
定义迭代器后，就不能直接对 Set 或 List 进行修改（直接使用相应函数），否则会有该错误。
但是可以通过迭代器对该 Set 或 List 进行修改。
注意这样的修改有局限性，如即使是 ArrayList 的迭代器，也是 ListIterator，是一个链表，并不能在 List 末尾加元素，只能在当前位置（下次next()的前面）插入。如果要，只能不用迭代器。

**java.util.regex.PatternSyntaxException: Unexpected internal error near index 1**
`replaceAll，split`等方法中的参数都是正则表达式，如果是`\`的话都需要写`\\\\`。




-----
## 注意
**(char)-1 != -1**
必须是`(char)-1 == (char)-1`。但是还是有`(char)48 == 48`。


-----
## 代码规范
https://blog.csdn.net/qq_42988868/article/details/121633508
包名规则：https://blog.csdn.net/weixin_39915721/article/details/110723780


-----
## 数据库 mysql
下载驱动包：https://dev.mysql.com/downloads/windows/installer/8.0.html
选择 Platform Independent 的zip，解压后得到 jar 库文件。
> 下面这个方法并没有成功：
> 新建系统变量`CLASSPATH`，添加解压后的路径（如果之前已有路径，则需用`;`与前面隔开）

在工作目录（或者任意目录，或者项目本身的libs目录），新建一个文件夹`libs`（名字任意），把解压后文件夹里的`jar`文件放进去。
vscode左边，有`JAVA PROJECTS`，在`Referenced Libraries`中添加保存的`jar`文件，即可导入。

**测试代码**
（可以用`try-with-resources`）
```java
import java.sql.*;

public class Exercise
{
	static final String JDBC_DRIVER = "com.mysql.cj.jdbc.Driver"; // 驱动名
	static final String DB_URL = "jdbc:mysql://localhost:3306/db_name?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC"; // 数据库 URL

	public static void main(String... args)
	{
		String username = "root";
		String password = "111";

		Connection conn = null;
		Statement stmt = null;
		try
		{
			// 注册 JDBC 驱动
			Class.forName(JDBC_DRIVER);

			// 打开链接
			System.out.println("Connecting");
			conn = DriverManager.getConnection(DB_URL, username, password);

			// 执行查询
			System.out.println("Instancing Statement");
			stmt = conn.createStatement();
			String sql;
			sql = "SELECT id, name FROM test";
			ResultSet rs = stmt.executeQuery(sql);

			while(rs.next())
			{
				int id  = rs.getInt("id");
				String name = rs.getString("name");

				System.out.print("ID: " + id);
				System.out.println(", name: " + name);
			}
			// 关闭
			rs.close();
			stmt.close();
			conn.close();
		}
		catch(SQLException se)
		{
			// 处理 JDBC 错误
			se.printStackTrace();
		}
		catch(Exception e)
		{
			// 处理 Class.forName 错误
			e.printStackTrace();
		}
		finally
		{
			// 关闭资源
			try {
				if(stmt!=null) stmt.close();
			}
			catch(SQLException se2) {
				// do nothing
			}
			try {
				if(conn!=null) conn.close();
			}
			catch(SQLException se) {
				se.printStackTrace();
			}
		}
		System.out.println("finish!");
	}
}
```

`allowPublicKeyRetrieval=true`：允许客户端从服务器获取公钥。
默认建立 SSL 连接，如果不需要可显示关闭。
新版的mysql需要指定时区`serverTimezone`。

**运行**
使用插件给的代码里的Run。
如果自己输命令，或用Code Runner，需要像Run给的指令一样去写。
如：`java -cp 'C:\Users\LENOVO\AppData\Local\Temp\cp_ee1zqjoxovyu9bi9ynkr1649l.jar' Exercise`。
需要用`-classpath`或`-cp`指定驱动jar包的路径，但这个路径需要是vscode生成的，不能自己指定实际的路径比如`F:\Codes\Java\DB\libs\mysql-connector-java-8.0.28.jar`，否则会`java.lang.ClassNotFoundException: com.mysql.cj.jdbc.Driver`，或`错误: 找不到或无法加载主类`，不知道为什么。


### 其它
**错误码**
见mysql驱动包下的：`mysql-connector-java-8.0.28\src\main\core-api\java\com\mysql\cj\exceptions\MysqlErrorNumbers.java`，里面定义了`SQLException.getErrorCode()`常数。
`import com.mysql.cj.exceptions.MysqlErrorNumbers;`后，也可使用如`MysqlErrorNumbers.ER_ACCESS_DENIED_ERROR`访问。


-----
## 连接postgresql
驱动下载：https://jdbc.postgresql.org/download.html





-----
## AWT
> API文档：https://www.apiref.com/java11-zh/java.desktop/java/awt/package-summary.html
> Container文档：https://www.apiref.com/java11-zh/java.desktop/java/awt/Container.html

AWT(Abstract Windowing Toolkit，抽象窗口工具包)，是Java提供的用来建立和设置Java图形用户界面的基本工具。
AWT由Java中的`java.awt`包提供，里面包含了许多可用来建立与平台无关的图形用户界面(GUI)的类，这些类又被称为组件(components)。
由于Java是一种独立于平台的程序设计语言，但GUI却往往是依赖于特定平台的，Java采用了相应的技术使得AWT能提供给应用程序独立于机器平台的接口，这保证了同一程序的GUI在不同机器上运行具有类似的外观（不一定完全一致）。
Swing是Sun公司后期推出的图形用户界面包。它基于AWT，并做出了更多改进。


### Container
Container 类是 Component 的子类，其有两个子类：Panel，Window。
Window 可独立于其他 Container 而存在。主要有两个子类：Frame，Dialog。

Container 中组件的位置和大小默认由布局管理器 layout manager 决定。Java主要包含以下几种布局管理器：
> Flow Layout：Panel, Applet 的默认布局管理器。
> Border Layout：Window, Frame, Dialog 的默认布局管理器。
> Grid Layout
> Card Layout
> GridBag Layout

使用`setLayout()`改变使用的布局管理器。
使用`setLayout(null)`可不用管理器，以便使用`setLocation(), setSize(), setBounds()`自定义数据，但不推荐？可能会使程序变得与平台相关。（然而不自定义根本做不出合适的）

Panel 对象创建后，必须加到 Window 或 Frame 对象中才能成为可见的。


### Event
事件类的层次结构：
```
java.lang.Object
  |
  +...java.util.EventObject
        |
        +...java.awt.AWTEvent
              |
              +...java.awt.event.ActionEvent(鼠标在按钮或文本框键击)
              +...
                  |
                  +...java.awt.event.WindowEvent(窗口事件)
                  +...
                      |
                      +...java.awt.event.MouseEvent(鼠标事件)
```

JDK使用委托代理模型(Delegation model)处理事件。
如果一个对象$obj$想要响应并处理某个事件`Ev`，则需先使用`addEvListener()`注册该事件的Listener。该函数的参数为一个类的实例，该类需继承该事件Listener的接口，即`implements EvListener`，并实现了处理该事件的方法（方法名取决于事件类型）。
这样当$obj$收到/产生一个事件时，会自动提交给响应的Listener进行处理。


-----
## 常用函数
**int到String**
```java
int num=100;
String s1=""+num;
String s2 =String.valueOf(num);
String s3 =(new Integer(num)).toString();
String s4 =Integer.toString(i);
```

**int到String**
```java
String s="100";

Integer ii =new Integer(s);
int x=ii.intValue();

int y = Integer.parseInt(s);
```



-----
## 其它
### 输入输出
**读入**
https://www.runoob.com/java/java-scanner-class..html

**输出**
使用：`import static java.lang.System.out;`，用`static import`导入class的静态方法。
然后`System.out.println`可写为`out.println`。


### 读取文件
> https://www.cnblogs.com/hkgov/p/14707726.html

`System.getProperty("user.dir")` 获取当前项目的根目录。



