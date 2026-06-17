
import java.util.Arrays;

/**
 * 用链地址法实现的简易整型键 -> 字符串值哈希表
 */
public class SimpleHashTable {
    private static class Node {
        final int key;
        String value;
        Node next;
        Node(int key, String value) {
            this.key = key;
            this.value = value;
        }
    }

    private Node[] buckets;
    private int size;
    private static final double LOAD_FACTOR = 0.75;

    public SimpleHashTable(int capacity) {
        buckets = new Node[Math.max(4, capacity)];
    }

    private int index(int key) {
        return Math.floorMod(key, buckets.length);
    }

    public String get(int key) {
        Node cur = buckets[index(key)];
        while (cur != null) {
            if (cur.key == key) return cur.value;
            cur = cur.next;
        }
        return null;
    }

    public void put(int key, String value) {
        if ((size + 1.0) / buckets.length > LOAD_FACTOR) {
            resize();
        }
        int idx = index(key);
        Node cur = buckets[idx];
        while (cur != null) {          // 已存在则覆盖
            if (cur.key == key) {
                cur.value = value;
                return;
            }
            cur = cur.next;
        }
        Node newNode = new Node(key, value);
        newNode.next = buckets[idx];   // 头插法挂到链表
        buckets[idx] = newNode;
        size++;
    }

    public boolean remove(int key) {
        int idx = index(key);
        Node cur = buckets[idx], prev = null;
        while (cur != null) {
            if (cur.key == key) {
                if (prev == null) buckets[idx] = cur.next;
                else prev.next = cur.next;
                size--;
                return true;
            }
            prev = cur;
            cur = cur.next;
        }
        return false;
    }

    private void resize() {
        Node[] old = buckets;
        buckets = new Node[old.length << 1];
        size = 0;
        for (Node head : old) {
            Node cur = head;
            while (cur != null) {      // 重新分布到新桶
                put(cur.key, cur.value);
                cur = cur.next;
            }
        }
    }

    public static void main(String[] args) {
        SimpleHashTable table = new SimpleHashTable(4);
        table.put(1, "Alice");
        table.put(5, "Bob");   // 与 1 可能同槽，考验链表
        table.put(9, "Cindy"); // 触发扩容

        System.out.println(table.get(5)); // 输出 Bob
        table.remove(1);
        System.out.println(table.get(1)); // 输出 null
    }
}