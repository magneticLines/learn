# SOLID 设计原则

> SOLID 是面向对象设计的五个基本原则，由 Robert C. Martin (Uncle Bob) 提出。它们是编写可维护、可扩展和易于理解的代码的基础。

---

## 1. 单一职责原则 (Single Responsibility Principle - SRP)

### 1.1 定义
**"一个类应该只有一个引起它变化的原因。"**

简单来说，一个类只负责一项职责。如果一个类承担了太多的职责，就相当于把这些职责耦合在一起了。

### 1.2 为什么需要 SRP
- **降低复杂度**：每个类逻辑简单，易于阅读。
- **提高可维护性**：修改一个功能不影响其他功能。
- **提高复用性**：功能单一的类更容易被其他模块引用。

### 1.3 代码示例

**❌ 违反 SRP（一个类负责了逻辑处理和文件保存）**

```java
public class UserSettings {
    private User user;

    public UserSettings(User user) {
        this.user = user;
    }

    // 更新设置
    public void changeSettings(String newSettings) {
        if (checkAccess()) {
            // 处理逻辑
        }
    }

    // 检查权限（职责2）
    private boolean checkAccess() {
        return true;
    }

    // 保存到数据库（职责3）
    public void save() {
        System.out.println("Saving user to database...");
    }
}
```

**✅ 遵循 SRP（拆分为职责专一的类）**

```java
// 核心业务逻辑
public class UserSettings {
    private User user;
    public void changeSettings(String newSettings) { /* ... */ }
}

// 权限检查
public class SecurityService {
    public static boolean checkAccess(User user) { /* ... */ }
}

// 数据持久化
public class UserRepository {
    public void save(User user) { /* ... */ }
}
```

---

## 2. 开闭原则 (Open-Closed Principle - OCP)

### 2.1 定义
**"对扩展开放，对修改关闭。"**

当需求发生变化时，我们应该通过**添加新代码**来扩展功能，而不是**修改现有的代码**。

### 2.2 为什么需要 OCP
- **稳定性**：不修改已有代码，就不会引入新的 Bug。
- **扩展性**：通过增加新类来增加新功能，非常灵活。

### 2.3 代码示例

**❌ 违反 OCP（增加一种形状需要修改 area 方法）**

```java
public class AreaCalculator {
    public double calculateArea(Object shape) {
        if (shape instanceof Rectangle) {
            Rectangle rect = (Rectangle) shape;
            return rect.width * rect.height;
        } else if (shape instanceof Circle) {
            Circle circle = (Circle) shape;
            return Math.PI * circle.radius * circle.radius;
        }
        return 0;
    }
}
```

**✅ 遵循 OCP（通过继承或接口扩展）**

```java
public interface Shape {
    double area();
}

public class AreaCalculator {
    public double calculateArea(Shape shape) {
        return shape.area(); // 无论增加多少种形状，这里都不需要改动
    }
}
```

---

## 3. 里氏替换原则 (Liskov Substitution Principle - LSP)

### 3.1 定义
**"子类对象应该能够替换其父类对象，而程序的逻辑行为不发生改变。"**

继承必须确保父类所拥有的性质在子类中同样成立。

### 3.2 为什么需要 LSP
- **保证规范性**：确保继承关系的正确性。
- **多态的基础**：多态必须建立在 LSP 之上才能安全工作。

### 3.3 经典案例：正方形不是长方形

**❌ 违反 LSP**

```java
public class Rectangle {
    protected int width;
    protected int height;
    public void setWidth(int w) { this.width = w; }
    public void setHeight(int h) { this.height = h; }
}

public class Square extends Rectangle {
    @Override
    public void setWidth(int w) {
        super.setWidth(w);
        super.setHeight(w); // 强制宽高一致
    }
}

// 测试代码
void test(Rectangle r) {
    r.setWidth(10);
    r.setHeight(20);
    // 对于长方形，面积应该是 200
    // 如果传入的是正方形，面积会变成 400（因为 setHeight 时宽也被改成了 20）
    // 逻辑发生变化，违反 LSP
}
```

---

## 4. 接口隔离原则 (Interface Segregation Principle - ISP)

### 4.1 定义
**"客户端不应该强迫依赖它不需要的接口。"**

建立单一接口，不要建立庞大臃肿的接口。尽量细化接口，接口中的方法尽量少。

### 4.2 为什么需要 ISP
- **避免副作用**：修改一个无关的方法不会影响只依赖相关方法的客户端。
- **提高灵活性**：实现类可以根据需要组合多个细粒度接口。

### 4.3 代码示例

**❌ 违反 ISP（臃肿的接口）**

```java
public interface Worker {
    void work();
    void eat();
}

public class Robot implements Worker {
    public void work() { /* 机器人工作 */ }
    public void eat() { /* 机器人不需要吃饭，但被迫实现空方法 */ }
}
```

**✅ 遵循 ISP（细颗粒度接口）**

```java
public interface Workable { void work(); }
public interface Feedable { void eat(); }

public class Human implements Workable, Feedable { ... }
public class Robot implements Workable { ... }
```

---

## 5. 依赖倒置原则 (Dependency Inversion Principle - DIP)

### 5.1 定义
**"高层模块不应该依赖低层模块，两者都应该依赖其抽象；抽象不应该依赖细节，细节应该依赖抽象。"**

核心思想：**要面向接口编程，不要面向实现编程。**

### 5.2 为什么需要 DIP
- **降低耦合**：高层模块不直接依赖具体实现，更换实现变得轻而易举。
- **提高可测试性**：可以方便地使用 Mock 对象替换真实依赖。

### 5.3 代码示例

**❌ 违反 DIP（高层直接依赖低层）**

```java
public class Driver {
    public void drive(Benz car) { // 强依赖于奔驰类
        car.run();
    }
}
```

**✅ 遵循 DIP（高层依赖接口）**

```java
public interface ICar { void run(); }

public class Driver {
    public void drive(ICar car) { // 依赖抽象接口
        car.run();
    }
}

// 这样司机可以开 Benz, BMW, 或者任何实现了 ICar 的车
```

---

## ⭐ 总结：如何记住 SOLID

- **S (SRP)**: 每个类只负责一件事。
- **O (OCP)**: 增加功能不改旧代码。
- **L (LSP)**: 子类完全可以当父类用。
- **I (ISP)**: 接口要小巧精干。
- **D (DIP)**: 依赖接口，不依赖具体类。

---

📖 下一步：[设计模式大纲](./设计模式大纲.md) | [面向对象基础](./0面向对象基础.md)
