# C++ 面试题：实现红黑树和简化版 map

## 1. map 为什么通常使用平衡搜索树

有序 `map/set` 需要同时提供：

1. 按 key 有序遍历。
2. 查找、插入、删除的对数复杂度保证。
3. 插入其他节点时，已有节点地址通常保持稳定。

普通二叉搜索树遇到有序输入会退化成链表。红黑树通过颜色约束把最长根叶路径限制在最短路径的两倍以内，因此树高保持 `O(log n)`。

## 2. 红黑树不变量

1. 节点是红色或黑色。
2. 根节点是黑色。
3. 空叶子视为黑色。
4. 红节点不能有红孩子。
5. 任一节点到后代空叶子的所有路径包含相同数量的黑节点。

插入新节点通常先染红色，因为染红不会立即改变路径上的黑节点数量；随后修复可能出现的“红父—红子”冲突。

## 3. 节点和旋转

```cpp
enum class Color { Red, Black };

template <typename Key, typename Value>
struct RBNode {
    Key key;
    Value value;
    Color color = Color::Red;
    RBNode* parent = nullptr;
    RBNode* left = nullptr;
    RBNode* right = nullptr;
};

template <typename Node>
void rotate_left(Node*& root, Node* x) {
    Node* y = x->right;
    x->right = y->left;

    if (y->left) {
        y->left->parent = x;
    }

    y->parent = x->parent;
    if (!x->parent) {
        root = y;
    } else if (x == x->parent->left) {
        x->parent->left = y;
    } else {
        x->parent->right = y;
    }

    y->left = x;
    x->parent = y;
}
```

右旋与左旋完全对称。旋转只改变局部父子关系，不改变中序遍历顺序，因此不会破坏二叉搜索树的 key 顺序。

## 4. 插入修复的三类情况

设新节点为 `z`，父节点为红色，祖父节点存在：

```text
情况 1：叔叔是红色
父、叔染黑，祖父染红，z 上移到祖父继续检查。

情况 2：叔叔是黑色，z 与父形成“折线”
先围绕父节点旋转，把折线变成直线。

情况 3：叔叔是黑色，z 与父形成“直线”
父染黑、祖父染红，再围绕祖父反向旋转。
```

左侧和右侧情况镜像处理。循环结束后把根染黑。

```cpp
template <typename Node>
void fix_after_insert(Node*& root, Node* z) {
    while (z->parent && z->parent->color == Color::Red) {
        Node* parent = z->parent;
        Node* grand = parent->parent;

        if (parent == grand->left) {
            Node* uncle = grand->right;
            if (uncle && uncle->color == Color::Red) {
                parent->color = Color::Black;
                uncle->color = Color::Black;
                grand->color = Color::Red;
                z = grand;
            } else {
                if (z == parent->right) {
                    z = parent;
                    rotate_left(root, z);
                    parent = z->parent;
                    grand = parent->parent;
                }
                parent->color = Color::Black;
                grand->color = Color::Red;
                // rotate_right(root, grand);
            }
        } else {
            // 与上面完全镜像：交换 left/right 和左旋/右旋。
        }
    }
    root->color = Color::Black;
}
```

代码刻意省略镜像分支和删除修复，面试时应先把三种状态变化画对，再补完整实现。

## 5. map 和 set 如何复用树

```text
set 节点保存 Key，比较 Key
map 节点保存 pair<const Key, Value>，仍只比较 Key
```

迭代器做中序遍历。求后继时：有右子树就取右子树最左节点；否则沿父指针向上，直到当前节点来自某个父节点的左侧。

## 6. 面试口述版

map 通常建立在红黑树上。节点按 key 满足二叉搜索树顺序，颜色规则保证树高为 O(log n)。插入节点先染红，通过叔叔变色和局部旋转修复红红冲突；旋转保持中序顺序不变。map 与 set 可以复用同一棵树，差别主要在节点保存的数据以及迭代器暴露的值类型。
