# Java Spring 笔记

Tags: 学习笔记

-----
[TOC]

-----
> SpringCloud 教程：https://github.com/macrozheng/springcloud-learning

TODO：
AOP：https://www.bilibili.com/video/BV1Lo4y1c7hR/

## Spring

**容器**

容器是为某种组件的运行提供必要支持的一个软件环境。
使用容器运行组件，容器除了提供一个运行环境之外，还提供了许多底层服务。

例如：Tomcat就是一个Servlet容器，它可以为Servlet的运行提供运行环境。类似Docker这样的软件也是一个容器，它提供了必要的Linux环境以便运行一个特定的Linux进程。



**IOC**

> （不确定）传参数进去能改变类的行为，这就叫让类的行为被外部确定了，所以是一种控制反转。对象的依赖作为对象的成员而存在，从而影响对象的行为。

IOC (Inversion of Control，控制反转)。
对于 spring 框架来说，就是由 spring 的 IoC 容器来负责控制对象的生命周期和对象间的调用关系。组件不再由应用程序自己决定何时创建与销毁、如何配置，而是由 IoC 容器负责。这样应用就只需要使用。
IoC 也叫依赖注入 (DI, Dependency Injection)？将组件的创建与配置，和组件的使用分离。

Spring 的 IoC 容器中，把所有组件统称为 JavaBean，配置一个组件就是配置一个Bean。

IoC 容器是无侵入的，组件不知道自己在 Spring 的容器中运行，也不是必须依赖于容器运行。

IoC 容器要实例化所有的组件，因此需要告诉容器如何创建组件，以及各组件的依赖关系。
一种方法是通过 xml 配置文件，告诉 IoC 创建哪些 Bean 组件：

```xml
<beans>
    <bean id="dataSource" class="HikariDataSource" />
    <bean id="bookService" class="BookService">
        <property name="dataSource" ref="dataSource" />
    </bean>
    <bean id="userService" class="UserService">
        <property name="dataSource" ref="dataSource" />
    </bean>
</beans>
```

但这种配置太麻烦了，每创建一个 Bean 就要更改 xml。

另一种方法就是使用注解，如：在类前加`@Component`就会定义一个该类型的 Bean 单例，其名称默认为类名（但首字母小写）。
使用`@Autowired`修饰字段，可以将指定类型的 Bean 注入到字段中。

**Bean**

通过 getBean(Class) 可以获取一个类型的 Bean。
Bean 有两种，一种就是最常用的单例，在容器结束前才销毁。
另一种 Bean 在每次调用 getBean 时，都会返回一个新的实例，这种 Bean 称为 Prototype（原型），它的生命周期与 Singleton 不同。
在声明原型 Bean 时，除了`@Component`外，还要加`@Scope`注解。

某个基类的 Bean 对象可能有很多个（每个子类一个），通过 @autowired 可以绑定到一个 List 上。List 中 Bean 的顺序与扫描 classpath 有关。在 @Component 后可以加`@Order(...)`来指定 List 中的顺序。

**@Bean**

如果一个 Bean 不在当前包中，或者需要自己创建一个对象作为 Bean，可以在一个方法上标注`@Bean`，方法的返回值将被创建为 Bean 单例（该方法只会被调用一次）。

对于单例的 Bean，是通过注入字段的类型来决定使用哪个 Bean 的。但同一种类型的 Bean 可能存在多个实例（如有多个同类型的 @Bean 方法），就必须为这些 Bean 指定不同的名字。
Bean 的名称默认为类名（但首字母小写）。
可以用`@Bean("name")`指定新的名字，也可以用`@Bean`+`@Qualifier("name")`指定名字。
使用 Bean 时，也需要指定 Bean 的名称：`@Autowired`+`@Qualifier("name")`。
不过，如果一个 Bean 指定为`@Primary`，注入时可以不指定名字，将默认使用 @Primary 的 Bean。

@Bean 注解所在的类一般都会标注 @Configuration，一是为了启用完全模式，二是显式标记这个类是配置类，而非一个普通的 JavaBean。
默认的精简模式下的 @Bean 方法，调用另一个 @Bean 方法得到的实例并不是容器中唯一的 Bean 对象，而完全模式得到的是唯一的，一般更正确。

**FactoryBean**

可以使用工厂模式去创建 Bean。该工厂类需要实现`FactoryBean`接口，并标注`@Component`（它也是 Bean）。
当一个 Bean 实现了`FactoryBean`接口后，Spring 会先实例化这个工厂，然后通过调用它的`getObject()`创建真正的Bean（该工厂类的方法返回值才是真正用到的 Bean）。`class<?> getObjectType()`可以指定创建的 Bean 的类型，因为指定类型不一定与实际类型一致，可以是接口或抽象类。
虽然它是一个 Bean，但实际是用来创建 Bean 的，并不会使用它作为 Bean。为了和普通 Bean 区分，通常都以`XxxFactoryBean`命名。

**Resource**

Spring 提供了`Resource`类便于注入资源文件。
最常用的注入是通过 classpath 以`@Value("classpath:/path/to/file")`的形式注入。

**条件装配**

对于某个标注 Bean 的对象，Spring 容器可以根据注解`@Profile`或`@Conditional`来决定是否真的创建该 Bean。这样可以区分不同的运行环境。

**@Profile**

如：`@Bean @Profile("!test")`，只有在 Profile 中没有设置 test 的时，才会创建该 Bean。
profile 是在运行程序时通过参数（或环境变量位置）指定的，如`-Dspring.profiles.active=v1,v2`表示 v1, v2 被设置。

**AOP (Aspect Oriented Programming)**

https://www.liaoxuefeng.com/wiki/1252599548343744/1266265125480448

面向切面编程





**EndPoint**

SpringBoot 的 Endpoint 主要用来监控应用服务的运行状况，并集成在 MVC 中提供查看接口。





---

## 注解

**@Configuration**

表明当前类是 spring 的一个配置类，可以替代或减少 spring 的 applicationContext.xml。但其本质就是 @Component。
用 @Configuration 注解的类，等价于 XML 中配置 beans；用 @Bean 标注配置类的方法，等价于 XML 中配置的 bean。

**@Value(...)**

> 例子见：https://blog.csdn.net/qq_31960623/article/details/116902786

用于将指定的值注入到标注的属性。用法有三类：

- `@Value(str)`：直接注入字符串值。
- `@Value("${...}")`：获取配置文件中的对应属性值。
  例：`@Value("${a.b.c: x}")`表示读取 key 为 a.b.c 的 value，如果没有使用默认值 x。
- `@Value("#{...}")`：通过 SpEl 表达式，获取某个属性值；或调用某个 bean 的方法。
  例：`@Value("#{A.f}")`表示读取一个 Bean A 中的 f 属性（对于 private 属性将调用相应的 get 方法）。

**SpEl (Spring Expression Language)**

SpEl 是 Spring 表达式语言，可以在运行时查询和操作数据。使用`＃{…}`作为操作符号，大括号中的所有字符均视为 SpEl。







---

## Maven

`setting.xml`是全局级别的配置文件，配置 maven 的运行环境。
`pom.xml`是项目级别的配置文件。pom (project object model，项目对象模型) 是 Maven 对一个项目的描述，包含：项目的 maven 坐标、依赖关系、开发者需要遵循的规则、缺陷管理系统、组织和 licenses、项目的 url、项目的依赖性，以及其他所有的项目相关因素。



在`<build>`标签中写入构建相关的配置。

聚合 POM 与继承关系中的父 POM 的 packaging 都需要是 pom。
聚合模块与继承关系中的父模块除了 POM 之外都没有实际的内容。
对于聚合模块来说，它知道有哪些被聚合的模块，但那些被聚合的模块不知道这个聚合模块的存在；而继承关系中的子模块都必须知道父模块是什么。

`<dependencyManagement>`用来管理项目的依赖配置。
在`<dependencyManagement>`标签下的依赖声明不会将依赖直接引入到父工程和子工程中，不过它能约束 dependencies 下的依赖配置；子模块中只有在`<dependenices>`标签中声明的依赖才会被继承并引入到子工程中。



---

## 杂

**项目目录规范**

https://www.cnblogs.com/shoshana-kong/p/11419937.html

**配置文件**

配置文件里通过类似 JSON 的 key: value 形式定义配置，通过一个或多个 key 可查询某个值。
value 可以用逗号分隔多个值。

`application.yml`是默认的配置文件。
如果要定义其它配置文件，需要起名为`application-name.yml`，并在 application.yml 中用`profiles: include: name`注册（或`profiles: active: name`？）。

同一目录下可以有 bootstrap 和 application 两个配置文件，前者优先级更高。
bootstrap 是系统级别的配置，application 是应用级别的配置。

配置文件优先级与位置有关：根目录/config > 根目录 > 根目录/src/main/resources/config > 根目录/src/main/resources。

**slf4j**

> https://blog.csdn.net/Damon_zqt/article/details/106241767
> https://baijiahao.baidu.com/s?id=1741578840871626015&wfr=spider&for=pc
> https://www.cnblogs.com/xrq730/p/8619156.html

简单日志门面 (Simple Logging Facade for Java)。

SLF4J所提供的核心API是一些接口以及一个LoggerFactory的工厂类。在使用SLF4J的时候，不需要在代码中或配置文件中指定你打算使用哪个具体的日志系统。SLF4J提供了统一的记录日志的接口，只要按照其提供的方法记录即可，最终日志的格式、记录级别、输出方式等通过具体日志系统的配置来实现，因此可以在应用中灵活切换日志系统。

**Lombok**

> https://blog.csdn.net/zzhongcy/article/details/122948536

**@componet**

> https://blog.csdn.net/qq_36908872/article/details/126975626

**VO DTO DO PO DAO**

VO (视图对象, view object) 用于展示层，一般与 DTO 一致，但会根据页面的需求转换数据格式。
DTO (数据传输对象, data transfer object) 用于展示层和逻辑层之间的数据传输，即前端与后端之间的数据传输。
DO (domain object) 是业务实体，服务层会将 DO 根据需要，转换成返回给展示层的 DTO。
PO (持久化对象, persistent object) 与持久层的数据结构对应，一般与 DO 一致，但 DO 有时不需要持久化。如果持久层是关系数据库，则属性与数据库的字段一一对应。
DAO (数据访问对象, data access object) 是一个面向对象的数据库接口，在持久化层用于操作数据库。

**版本号**

2.1、例如：Spring Boot的版本号是2.1.5

（1）其中2: 表示的主版本号，表示是我们的SpringBoot第二代产品。

（2）其中1: 表示的是次版本号，增加了一些新的功能但是主体的架构是没有变化的，是兼容的。

（3）其中5: 表示的是bug修复版。

（4）所以2.1.5合起来就是springboot的第二代版本的第1个小版本的第5次bug修复版本。

结论：版本格式 -> 主版本号.子版本号.修正版本号。

snapshot 快照

alpha 内测

beta 公测

release 稳定版本

GA 最稳定版本

Final 正式版

Pro(professional) 专业版

Plus 加强版

Retail 零售版

DEMO 演示版

Build 内部标号

Delux 豪华版 （deluxe：豪华的，华丽的）

Corporation或Enterpraise 企业版

M1 M2 M3 M是milestone的简写 里程碑的意思

RC 版本RC:(Release Candidate)，几乎就不会加入新的功能了，而主要着重于除错

SR 修正版

Trial 试用版

Shareware 共享版

Full 完全版

 

这个名词是多的不得了，这里我们讲几个常见的。

build-snapshot：开发版本，也叫快照版本。当前版本处于开发中，开发完成之后，自己进行测试，另外让团队其它人也进行测试使用下;  

M1...M2（Milestone）：里程碑版本，在版发布之前 会出几个里程碑的版本。使用snapshot版本开发了一个时间，觉得最近写代码杠杠的，那么就整几个里程碑版本记录下吧，记录我们这个重大的时刻，是你我未来的回忆。

RC1…RC2（Release Candidates）：发布候选。内部开发到一定阶段了，各个模块集成后，经过细心的测试整个开发团队觉得软件已经稳定没有问题了，可以对外发行了。

release：正式版本。发布候选差不多之后，那么说明整个框架到了一定的阶段了，可投入市场大面积使用了，那么发布出去，让广大用户来吃吃香吧。

SR1…SR2（Service Release）：修正版。这是啥意思呐，这不release版本发布之后，让广大群体使用了嘛，再牛逼的架构师，也无法写出零bug的代码，那么这时候，就优先对于release版本的问题进行修复，这时候每次迭代的版本就是SR1,SR2,SR3。

那么上面的一个顺序是这样子的：

snapshot –>M1…MX  –> RC1…RCX  –> release –> SR1…SRX

对应的文字理解：

开发版本(BS) --(开发到一个小阶段，就要标记下)--> 里程碑版本(MX) --(版本到了一个相对稳定的阶段，可以对外发行了，但是可能还存在修复的问题，此时只做修复，不做新功能的增加)--> 发布候选(RC1) --(BUG修复完成，发布)-->正式版本(release)  --(外界反馈存在一些问题，进行内部在修复)--> 修正版本(SRX)

结论：版本格式-> 主版本号.子版本号.修正版本号.软件版本阶段

CURRENT：当前推荐的版本

GA：稳定版，可用于生产

PRE   ：里程碑版/预览版本

SNAPSHOT : 快照





