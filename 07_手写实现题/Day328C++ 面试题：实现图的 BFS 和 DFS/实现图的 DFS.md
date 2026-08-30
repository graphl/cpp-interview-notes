# C++ 面试题：实现图的 DFS

## 1. DFS 是什么

DFS（Depth-First Search，深度优先搜索）从起点沿一条路径不断深入，无法继续时再回退并尝试其他分支。

它可以使用：

- 递归，由函数调用栈保存搜索路径；
- 显式栈，手动保存等待处理的节点。

图可能存在环和多条入边，因此递归版和迭代版都必须维护 `visited`。

## 2. 递归实现

下面使用邻接表保存图，顶点编号范围为 `[0, vertex_count)`：

```cpp
#include <cstddef>
#include <stdexcept>
#include <vector>

class Graph {
public:
    explicit Graph(std::size_t vertex_count)
        : adjacency_(vertex_count) {}

    void add_edge(std::size_t from,
                  std::size_t to,
                  bool undirected = false) {
        check(from);
        check(to);

        adjacency_[from].push_back(to);
        if (undirected) {
            adjacency_[to].push_back(from);
        }
    }

    std::vector<std::size_t> dfs_recursive(std::size_t start) const {
        check(start);

        std::vector<std::size_t> order;
        std::vector<bool> visited(adjacency_.size(), false);
        dfs_visit(start, visited, order);
        return order;
    }

private:
    void dfs_visit(std::size_t current,
                   std::vector<bool>& visited,
                   std::vector<std::size_t>& order) const {
        visited[current] = true;
        order.push_back(current);

        for (std::size_t next : adjacency_[current]) {
            if (!visited[next]) {
                dfs_visit(next, visited, order);
            }
        }
    }

    void check(std::size_t vertex) const {
        if (vertex >= adjacency_.size()) {
            throw std::out_of_range("Graph vertex");
        }
    }

    std::vector<std::vector<std::size_t>> adjacency_;
};
```

递归函数一进入节点就标记 `visited`，然后依次递归访问尚未访问的邻接点。

## 3. 显式栈实现

图的路径可能很深，递归实现可能耗尽线程栈。可以使用 `std::vector` 模拟栈：

```cpp
std::vector<std::size_t> dfs_iterative(std::size_t start) const {
    check(start);

    std::vector<std::size_t> order;
    std::vector<bool> visited(adjacency_.size(), false);
    std::vector<std::size_t> pending;

    visited[start] = true;
    pending.push_back(start);

    while (!pending.empty()) {
        const std::size_t current = pending.back();
        pending.pop_back();
        order.push_back(current);

        const auto& neighbors = adjacency_[current];
        for (auto it = neighbors.rbegin();
             it != neighbors.rend();
             ++it) {
            if (!visited[*it]) {
                visited[*it] = true;
                pending.push_back(*it);
            }
        }
    }

    return order;
}
```

邻接点使用逆序入栈，是为了让较前面的邻接点先出栈，使结果更接近递归版的访问顺序。如果不要求固定顺序，可以直接正序入栈。

在入栈时标记能够避免节点重复入栈。也可以在出栈时检查并标记，但同一节点可能被多个前驱重复压栈，空间和操作次数会增加。

## 4. 遍历非连通图

遍历整个图需要在外层扫描所有顶点：

```cpp
std::vector<std::size_t> dfs_all() const {
    std::vector<std::size_t> order;
    std::vector<bool> visited(adjacency_.size(), false);

    for (std::size_t start = 0; start < adjacency_.size(); ++start) {
        if (!visited[start]) {
            dfs_visit(start, visited, order);
        }
    }

    return order;
}
```

多次搜索必须共享同一份 `visited`。对无向图而言，每次重新启动 DFS 就发现一个新的连通分量。

## 5. DFS 的典型用途

DFS 常用于：

- 判断节点是否可达；
- 遍历连通分量；
- 检测环；
- 拓扑排序；
- 回溯和路径枚举；
- 构造 DFS 树或森林。

不同任务需要额外状态。例如，有向图环检测通常使用未访问、正在访问、已经完成三种状态，仅有一个 `visited` 布尔值无法区分回边。

## 6. 复杂度

使用邻接表时：

- 时间复杂度：`O(V + E)`；
- `visited`、结果和递归栈或显式栈的额外空间：`O(V)`。

最坏情况下递归深度可以达到 `O(V)`。顶点数量很大或图可能形成长链时，显式栈版本通常更稳妥。

如果使用邻接矩阵，时间复杂度为 `O(V²)`。

## 7. 常见错误

1. 忘记 `visited`，在有环图中无限递归或反复入栈。
2. 递归调用前后维护状态的时机不正确。
3. 图很深时仍无条件使用递归，导致栈溢出。
4. 认为一次起点搜索可以覆盖非连通图。
5. 无向边只加入一个方向。
6. 认为 DFS 一定能得到无权图最短路径。
7. 依赖某个固定遍历顺序，却没有固定邻接表顺序和入栈顺序。

## 8. 面试口述版

DFS 沿一条路径尽量深入，再回溯处理其他分支，可以使用递归或显式栈实现。图可能有环，因此进入或压入节点时要维护 `visited`。邻接表实现的时间复杂度是 `O(V+E)`，额外空间复杂度是 `O(V)`。递归版代码简洁，但深图存在栈溢出风险；非连通图需要在外层扫描所有未访问顶点。

返回 [图的 BFS 和 DFS 导航](实现图的%20BFS%20和%20DFS.md)。
