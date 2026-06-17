
/**
 * 手动实现一个简单的单向链表来理解其工作原理
 */
public class SimpleLinkedList {

    // 内部节点类
    private static class Node {
        int data;   // 数据域
        Node next;  // 指针域

        Node(int data) {
            this.data = data;
            this.next = null;
        }
    }

    private Node head; // 头节点

    // 构造函数
    public SimpleLinkedList() {
        this.head = null;
    }

    // 1. 在链表头部插入节点
    public void addFirst(int data) {
        Node newNode = new Node(data);
        newNode.next = head; // 新节点的 next 指向旧的 head
        head = newNode;      // head 更新为新节点
    }

    // 2. 在链表尾部插入节点
    public void addLast(int data) {
        Node newNode = new Node(data);
        if (head == null) {
            head = newNode;
            return;
        }
        Node current = head;
        while (current.next != null) { // 遍历直到找到最后一个节点
            current = current.next;
        }
        current.next = newNode; // 将原尾节点的 next 指向新节点
    }

    // 3. 删除头部节点
    public void removeFirst() {
        if (head != null) {
            head = head.next;
        }
    }

    // 4. 打印链表
    public void printList() {
        Node current = head;
        while (current != null) {
            System.out.print(current.data + " -> ");
            current = current.next;
        }
        System.out.println("null");
    }

    public static void main(String[] args) {
        SimpleLinkedList list = new SimpleLinkedList();

        System.out.println("在头部添加元素 10, 20:");
        list.addFirst(10);
        list.addFirst(20);
        list.printList(); // 输出: 20 -> 10 -> null

        System.out.println("在尾部添加元素 5:");
        list.addLast(5);
        list.printList(); // 输出: 20 -> 10 -> 5 -> null

        System.out.println("删除头部元素:");
        list.removeFirst();
        list.printList(); // 输出: 10 -> 5 -> null
    }
}