# 6 树 - 基础和 Overview

### 1. 概念名称

> **一句话核心概念总结:** 树是一种以层次关系组织数据的非线性结构，节点通过父子边连接，可高效表达“包含/从属/优先级/前缀”等关系。

### 2. 详细解释

- **基本术语与性质:** 节点（Node）、根（Root）、父/子、兄弟、叶子（无子节点）、度（子节点数量）、高度/深度/层次、子树、森林。高度常指“从节点到叶的最长路径边数”；树的高度是根的高度。
- **常见树型快速概览:** 一般树（任意度）；二叉树（每个节点度≤2）；满二叉树（除叶外度=2且叶在同层）；完全二叉树（按层紧凑排列，用数组存储友好）；二叉搜索树BST（左<根<右，中序有序）；平衡BST（如AVL、红黑树）在查找/插入/删除中保持高度约O(log n)；堆（完全二叉树满足堆序，用于优先队列）；B/B+树（多路平衡，磁盘/数据库索引用）；Trie（按字符前缀展开，适合前缀/词典）；线段树/区间树（支持区间查询与更新，常用于竞赛/区间统计）。
- **遍历方式:** 深度优先（先序/中序/后序，递归或栈迭代），层序遍历（BFS，队列）。BST 的中序遍历输出有序序列。
- **基本操作与复杂度（以平衡BST为例）:** 查找/插入/删除平均 O(log n)；在不平衡BST中最坏可退化为 O(n)。堆的插入/取顶/下沉为 O(log n)，取最值 O(1)。Trie 的查找/插入与键长相关 O(k)。
- **存储方式:** 链式节点（指针/引用字段，易表达稀疏结构）与顺序存储（完全二叉树用数组，利用索引计算父子位置，缓存友好）。

### 3. 代码示例

```java
// 简单双叉节点定义
class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;
    TreeNode(int val) { this.val = val; }
}

// 先序遍历（递归）：根 -> 左 -> 右
void preorder(TreeNode root, List<Integer> out) {
    if (root == null) return;
    out.add(root.val);
    preorder(root.left, out);
    preorder(root.right, out);
}

// 层序遍历（BFS）：按层访问
List<Integer> levelOrder(TreeNode root) {
    List<Integer> res = new ArrayList<>();
    if (root == null) return res;
    Queue<TreeNode> q = new LinkedList<>();
    q.offer(root);
    while (!q.isEmpty()) {
        TreeNode cur = q.poll();
        res.add(cur.val);
        if (cur.left != null) q.offer(cur.left);
        if (cur.right != null) q.offer(cur.right);
    }
    return res;
}

// 二叉搜索树插入（递归），保持左<根<右
TreeNode insertBST(TreeNode root, int val) {
    if (root == null) return new TreeNode(val);
    if (val < root.val) root.left = insertBST(root.left, val);
    else if (val > root.val) root.right = insertBST(root.right, val);
    // 若等于，通常选择忽略或记录计数，这里忽略
    return root;
}

// 二叉搜索树查找
TreeNode searchBST(TreeNode root, int val) {
    if (root == null || root.val == val) return root;
    if (val < root.val) return searchBST(root.left, val);
    return searchBST(root.right, val);
}
```

### 4. 常见应用场景

- **层级数据建模:** 组织结构、文件系统、DOM 树等自然层次关系。
- **高效索引与搜索:** BST/红黑树/AVL、B/B+树用于内存/磁盘索引；中序有序特性支持范围查询。
- **优先级调度:** 堆实现优先队列，用于任务调度、Dijkstra、TopK 等。
- **前缀匹配与自动补全:** Trie 支持前缀查找、词频统计、敏感词过滤。
- **区间/统计查询:** 线段树、区间树、Fenwick 树（BIT）用于区间求和、最值、差分更新。

### 5. 优缺点/注意事项

- **优势:** 能直接表达层次；平衡树/堆/Trie 等可在约束下提供接近 O(log n) 或按键长的操作复杂度；灵活支持多种查询模式（前缀、范围、优先级）。
- **注意事项:** 不平衡会退化（如BST变链表）；指针结构可能缓存不友好；递归遍历需注意栈深（可改迭代/尾递归）；选择合适的树型以匹配读写比例、存储介质与操作模式（内存 vs 磁盘）。

### 6. 深入思考

- 为什么对 BST 做中序遍历能得到有序序列？在插入和删除时如何保证这一性质不被破坏？
- 平衡策略（AVL 与红黑树）在“查询快”与“插入/旋转成本”之间如何权衡？在什么场景下更偏好哪一种？
- 对磁盘索引为何选择多路 B/B+ 树而非二叉树？这与磁盘页和缓存命中有什么关系？

