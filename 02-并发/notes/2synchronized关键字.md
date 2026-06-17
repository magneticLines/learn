
# `synchronized` 关键字详解

`synchronized` 是 Java 提供的一个关键字，用于实现线程之间的同步。它是 Java 并发编程中最基本、最常用的同步机制之一，通过确保在同一时刻，只有一个线程可以执行被 `synchronized` 保护的代码块或方法，来解决多线程环境下的数据竞争和一致性问题。

---

### 1. `synchronized` 是什么？

`synchronized` 本质上是一种**内置锁**（Intrinsic Lock）或**监视器锁**（Monitor Lock）。在 Java 中，每个对象都有一个与之关联的内置锁。当一个线程想要执行一个 `synchronized` 方法或代码块时，它必须先获取该方法或代码块所对应的对象的内置锁。一旦获取成功，其他任何试图获取同一个锁的线程都将被阻塞，直到持有锁的线程释放它。

它主要解决了三个核心的并发问题：
- **原子性 (Atomicity)**：确保一个操作（可能包含多条指令）不被中断，要么全部执行成功，要么都不执行。被 `synchronized` 包裹的代码块是原子的。
- **可见性 (Visibility)**：当一个线程修改了共享变量的值，`synchronized` 确保其修改能立即被其他线程看到。它通过在释放锁时将本地内存中的修改刷新到主内存，并在获取锁时从主内存重新加载共享变量来实现。
- **有序性 (Ordering)**：`synchronized` 会禁止指令重排序，确保代码块内的指令执行顺序与代码顺序一致，避免了因重排序导致的意外结果。

---

### 2. `synchronized` 的使用方式

`synchronized` 主要有三种使用方式：

#### a. 修饰实例方法

当 `synchronized` 修饰一个普通的实例方法时，它锁定的对象是**当前实例对象 (`this`)**。

```java
public class MyClass {
    public synchronized void instanceMethod() {
        // 同步代码
    }
}
```
当一个线程进入 `instanceMethod` 时，它会获取 `MyClass` 当前实例的锁。其他线程无法同时访问该实例的**任何** `synchronized` 实例方法。

#### b. 修饰静态方法

当 `synchronized` 修饰一个静态方法时，它锁定的对象是**当前类的 `Class` 对象**。

```java
public class MyClass {
    public static synchronized void staticMethod() {
        // 同步代码
    }
}
```
由于锁是作用于 `Class` 对象，因此无论有多少个类的实例，静态同步方法在同一时间只允许一个线程进入。这会影响到该类的所有实例。

#### c. 修饰代码块

`synchronized` 还可以用来修饰一个代码块，这种方式更加灵活，可以精确控制同步的范围，减小锁的粒度。

```java
public class MyClass {
    private final Object lock = new Object();

    public void blockMethod() {
        // 同步特定对象
        synchronized(lock) {
            // 同步代码
        }

        // 同步当前实例
        synchronized(this) {
            // 同步代码
        }

        // 同步Class对象
        synchronized(MyClass.class) {
            // 同步代码
        }
    }
}
```
- `synchronized(this)`: 锁住当前实例对象，与修饰实例方法效果相同。
- `synchronized(object)`: 锁住指定的 `object` 对象。
- `synchronized(MyClass.class)`: 锁住 `Class` 对象，与修饰静态方法效果相同。

---

### 3. `synchronized` 的核心特性

- **可重入性 (Reentrancy)**: 也称递归锁。一个已经持有锁的线程，可以再次获取同一个锁而不会被阻塞。这是为了防止死锁，例如，一个 `synchronized` 方法调用了同一个对象的另一个 `synchronized` 方法。
- **非公平性 (Non-fair)**: `synchronized` 在默认情况下是非公平的。当锁被释放时，任何等待的线程都有机会获取锁，而不是严格按照先来后到的顺序，这可能导致某些线程“饿死”。
- **不可中断性**: 一个线程在尝试获取 `synchronized` 锁时，如果锁被其他线程持有，那么该线程会进入阻塞状态，并且这个过程是不可被 `Thread.interrupt()` 中断的。

---

### 4. `synchronized` 的工作原理（锁升级）

`synchronized` 是由 JVM 实现的。它的性能在 JDK 1.6 之后得到了极大的优化，引入了“锁升级”的概念，目的是为了在不同竞争情况下使用最合适的锁状态，减少锁的开销。

锁的状态总共有四种：**无锁状态**、**偏向锁状态**、**轻量级锁状态**和**重量级锁状态**。升级路径是单向的，只能从低到高升级。

#### a. 偏向锁 (Biased Locking)

- **场景**: 在大多数情况下，锁不仅不存在多线程竞争，而且总是由同一个线程多次获得。
- **原理**: 当一个线程第一次获取锁时，JVM 会将对象头中的标志位设为“偏向模式”，并记录下持有该锁的线程ID。当这个线程再次进入同步块时，无需再进行任何同步操作，直接就可以获取锁，极大地提高了性能。
- **升级**: 如果有另一个线程尝试获取这个偏向锁，偏向模式会立即撤销，锁会升级为轻量级锁。

#### b. 轻量级锁 (Lightweight Locking)

- **场景**: 线程交替执行同步块，但竞争不激烈。
- **原理**: 当锁升级为轻量级锁后，线程不会立即阻塞，而是通过**自旋（Spinning）**的方式尝试获取锁。它会执行一个忙循环，不断检查锁是否被释放。自旋避免了线程上下文切换的开- 销（挂起和唤醒线程）。
- **升级**: 如果自旋一定次数后（或有其他线程同时在自旋），锁仍未被释放，轻量级锁就会膨胀为重量级锁。

#### c. 重量级锁 (Heavyweight Locking)

- **场景**: 多个线程同时竞争锁，锁竞争激烈。
- **原理**: 这是最传统的锁实现。当锁膨胀为重量级锁后，所有未能获取锁的线程都会被阻塞，并交由操作系统内核来进行调度。这种方式涉及到用户态和内核态的切换，开销最大。

---

### 5. `synchronized` vs. `ReentrantLock`

| 特性 | `synchronized` | `ReentrantLock` |
| :--- | :--- | :--- |
| **来源** | Java 关键字，JVM 实现 | `java.util.concurrent.locks` 包下的 API 类 |
| **锁管理** | JVM 自动获取和释放锁，不易出错 | 需手动调用 `lock()` 和 `unlock()`，必须在 `finally` 中释放 |
| **公平性** | 非公平锁 | 可通过构造函数选择公平或非公平（默认） |
| **中断** | 不可中断 | 可通过 `lockInterruptibly()` 实现可中断的锁获取 |
| **超时** | 不支持 | 可通过 `tryLock(long, TimeUnit)` 实现超时获取 |
| **条件变量**| 只能与一个 `wait/notify` 队列关联 | 可通过 `newCondition()` 绑定多个 `Condition` 对象 |

**如何选择？**
- **简单性**: 如果同步需求简单，没有特殊要求（如公平性、中断等），优先使用 `synchronized`，因为代码更简洁，由 JVM 管理不易出错。
- **功能性**: 如果需要更高级的功能，如公平锁、可中断锁、超时等待或多个条件变量，则必须使用 `Re- entrantLock`。
- **性能**: JDK 1.6 之后，`synchronized` 性能已经与 `ReentrantLock` 不相上下，甚至在低竞争下由于JVM的优化可能表现更好。因此，性能不再是选择的主要依据。
