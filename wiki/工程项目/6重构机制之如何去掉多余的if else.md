# 6重构机制之如何去掉多余的if else

## 1. 🎯 问题与背景 (The Problem & Context)

> **工程视角:** *"圈复杂度 (Cyclomatic Complexity) 是代码腐烂的开始。"*

*   **痛点分析:** 
    *   **可读性差:** 当一个方法里包含 10 个 `if-else` 或一个巨大的 `switch-case`，阅读者需要在这个迷宫里脑补所有的分支状态，心智负担极重。
    *   **违反开闭原则 (OCP):** 每次新增一种业务类型（如新增一种支付方式），都需要修改原来的 `if-else` 代码块，容易不小心改坏旧逻辑。
    *   **测试困难:** 必须覆盖所有分支路径，单元测试极其繁琐。

*   **核心定义:** 
    *   **多态与策略:** 利用面向对象的多态特性，将“分支判断”转换为“对象查找”。
    *   **重构目标:** 将 `if (type == A) { doA() } else if (type == B) { doB() }` 转化为 `Map.get(type).execute()`。

## 2. 🧩 抽象与心智模型 (The Mental Model)

> **设计视角:** *"把‘判断’变成‘查表’。"*

*   **生活类比 (自动售货机 vs 柜台服务员):**
    *   **If-Else (新手柜员):** 客户来了，柜员大脑飞速运转：“如果是要可乐，我就去A货架拿；如果是要雪碧，我就去B货架拿；如果是...” —— 柜员累死。
    *   **策略模式 (自动售货机):** 所有的饮料（策略）都整齐地摆在各自的格子里。客户按下 "可乐" 按钮（Key），售货机直接弹出对应的商品（Value）。售货机不需要思考，它只需要**路由**。

*   **抽象设计:**
    *   **Input:** 业务类型标识 (Type/Key)。
    *   **Router (Context):** 一个 Map 容器，存储 `Key -> Handler` 的映射。
    *   **Output:** 对应的处理器对象 (Handler)。

## 3. 🏗️ 系统架构与设计 (System & Architecture)

> **架构视角:** *"扁平化逻辑结构。"*

*   **在系统中的位置:** 通常位于**Service 层**的入口处，用于分发业务逻辑。

*   **关键组件:**
    1.  **Strategy Interface:** 定义统一的行为标准 (e.g., `PaymentService`).
    2.  **Concrete Strategy:** 具体的实现类 (e.g., `AliPayService`, `WeChatPayService`).
    3.  **Strategy Factory / Map:** 负责在启动时注册所有策略，并提供查找方法。

*   **设计模式:**
    *   **策略模式 (Strategy Pattern):** 核心。
    *   **工厂模式 (Factory Pattern):** 用于构建策略 Map。
    *   **模板方法模式 (Template Method):** 如果各个策略有公共逻辑，可以抽成抽象父类。

## 4. 💻 核心实现 (Implementation)

> **落地视角:** *"Spring 让策略模式变得无比简单。"*

假设我们要处理不同类型的订单通知 (SMS, Email, AppPush)。

### 方式一：经典的 Map 查表法 (Java 基础版)

```java
public interface NotifyStrategy {
    void send(String msg);
}

// 实现类 A
public class SmsStrategy implements NotifyStrategy {
    public void send(String msg) { /* 发短信 */ }
}

// 策略工厂
public class NotifyFactory {
    private static final Map<String, NotifyStrategy> map = new HashMap<>();

    static {
        map.put("sms", new SmsStrategy());
        map.put("email", new EmailStrategy());
    }

    public static NotifyStrategy get(String type) {
        return map.get(type);
    }
}

// 客户端调用：消灭了 if-else
NotifyFactory.get("sms").send("Hello");
```

### 方式二：Spring 自动注入法 (进阶版 - 推荐)
利用 Spring 强大的依赖注入，自动将所有实现类注入到一个 Map 中。

```java
// 1. 定义接口
public interface PaymentHandler {
    void pay(double amount);
    // 核心：策略自报家门，自己说自己是处理哪种类型的
    String getType(); 
}

// 2. 实现类 (加上 @Component 交给 Spring 管理)
@Component
public class AliPayHandler implements PaymentHandler {
    @Override
    public void pay(double amount) { System.out.println("支付宝支付"); }
    
    @Override
    public String getType() { return "ALI_PAY"; }
}

@Component
public class WechatPayHandler implements PaymentHandler {
    @Override
    public void pay(double amount) { System.out.println("微信支付"); }
    
    @Override
    public String getType() { return "WECHAT_PAY"; }
}

// 3. 策略路由中心 (核心)
@Service
public class PaymentService {
    
    // Spring 的魔法：自动把所有实现 PaymentHandler 的 Bean 注入这个 Map
    // Key 默认是 beanName (类名首字母小写)，但我们通常自己维护一个 Map
    private Map<String, PaymentHandler> handlerMap = new ConcurrentHashMap<>();

    // 构造函数注入所有 Handler (Spring 会自动收集所有实现类放入 List)
    public PaymentService(List<PaymentHandler> handlers) {
        for (PaymentHandler handler : handlers) {
            handlerMap.put(handler.getType(), handler);
        }
    }

    public void doPay(String type, double amount) {
        // 一行代码代替所有 if-else
        PaymentHandler handler = handlerMap.get(type);
        
        if (handler == null) {
            throw new IllegalArgumentException("不支持的支付类型: " + type);
        }
        handler.pay(amount);
    }
}
```

## 5. ⚖️ 工程权衡与局限 (Trade-offs & Constraints)

> **工程视角:** *"不要为了设计模式而强行套用。"*

*   **优点 (Pros):**
    *   **扩展性极强:** 新增一种类型，只需要加一个类，完全不用动 `PaymentService` 的代码。
    *   **逻辑清晰:** 每个类只负责一种逻辑，符合单一职责原则 (SRP)。

*   **代价 (Cons):**
    *   **类爆炸:** 如果逻辑很简单（比如只是返回不同的字符串），搞出几十个类来反而增加了维护成本。
    *   **逻辑割裂:** 业务逻辑分散在不同的文件里，无法像 `if-else` 那样一眼看到全貌（虽然 `if-else` 太多也看不懂）。

*   **何时不该用:**
    *   如果 `if-else` 只有 2-3 个，且未来大概率不会增加，直接写 `if-else` 其实更清晰、更高效。**过度设计是万恶之源。**

## 6. 🌐 深度联想与扩展 (Deep Dive & Connections)

> **通识视角:** *"表驱动法 (Table-Driven Methods)。"*

*   **底层原理:** 
    *   **指令跳转:** 在汇编层面，`switch` 语句（如果 case 紧凑）会被编译器优化成**跳转表 (Jump Table)**，直接根据索引跳转到内存地址，这和我们用 Map 存对象的思想是一致的。

### 思考题解答: Lambda 简化策略模式

**问题:** 如果我们的策略逻辑非常轻量，不想创建几十个类，Java 8 的 `Map<String, Consumer<T>>` 或 `Map<String, Function<T, R>>` Lambda 表达式能如何简化这个模式？

**解答:**
当每个策略的逻辑只有几行代码时，为每个策略创建一个 Class 确实显得笨重（“类爆炸”）。我们可以直接在 Map 里存储**函数（Lambda）**，而不是对象。

```java
@Service
public class LightweightStrategyService {
    
    // Map 的 Value 不再是具体的 Service 类，而是函数接口 Consumer<Double>
    // 意思：给你一个 Double (金额)，你去消费它，不需要返回值
    private final Map<String, Consumer<Double>> payStrategies = new HashMap<>();

    @PostConstruct
    public void init() {
        // 1. 支付宝逻辑：直接写 Lambda
        payStrategies.put("ALI_PAY", amount -> {
            System.out.println("调用支付宝SDK扣款: " + amount);
            // 这里可以写 5-10 行的简单逻辑
        });

        // 2. 微信逻辑
        payStrategies.put("WECHAT_PAY", amount -> {
            System.out.println("调用微信API扣款: " + amount);
        });
        
        // 3. 银行卡逻辑 (如果稍微复杂点，可以引用私有方法)
        payStrategies.put("BANK_CARD", this::handleBankCardPay);
    }

    public void doPay(String type, double amount) {
        Consumer<Double> strategy = payStrategies.get(type);
        if (strategy == null) throw new IllegalArgumentException("Unknown type");
        
        // 执行函数
        strategy.accept(amount);
    }
    
    private void handleBankCardPay(double amount) {
        // ... 较复杂的逻辑 ...
    }
}
```

*   **优点:** 所有的策略逻辑都内聚在一个类文件里，代码量极少，一目了然。
*   **适用场景:** 策略逻辑非常简单（Micro-Strategies），且不需要复杂的依赖注入。
