# C++ 面试题：实现图的 BFS 和 DFS

## 1. 图遍历与树遍历有什么不同

图可能存在：

- 环；
- 一个节点被多条边指向；
- 多个互不连通的分量。

因此图遍历必须维护 `visited`。没有访问标记，遇到环会重复遍历甚至无限循环。

下面使用邻接表保存图，顶点编号为 `[0, n)`。

## 2. 邻接表与 BFS

```cpp
#include <algorithm>
#include <cstddef>
#include <queue>
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

    std::vector<std::size_t> bfs(std::size_t start) const {
        check(start);
        std::vector<std::size_t> order;
        std::vector<bool> visited(adjacency_.size(), false);
        std::queue<std::size_t> pending;

        visited[start] = true;
        pending.push(start);

        while (!pending.empty()) {
            const std::size_t current = pending.front();
            pending.pop();
            order.push_back(current);

            for (std::size_t next : adjacency_[current]) {
                if (!visited[next]) {
                    visited[next] = true;
                    pending.push(next);
                }
            }
        }
        return order;
    }

    std::vector<std::size_t> dfs(std::size_t start) const {
        check(start);
        std::vector<std::size_t> order;
        std::vector<bool> visited(adjacency_.size(), false);
        std::vector<std::size_t> stack{start};

        while (!stack.empty()) {
            const std::size_t current = stack.back();
            stack.pop_back();
            if (visited[current]) {
                continue;
            }

            visited[current] = true;
            order.push_back(current);

            const auto& neighbors = adjacency_[current];
            for (auto it = neighbors.rbegin();
                 it != neighbors.rend();
                 ++it) {
                if (!visited[*it]) {
                    stack.push_back(*it);
                }
            }
        }
        return order;
    }

private:
    void check(std::size_t vertex) const {
        if (vertex >= adjacency_.size()) {
            throw std::out_of_range("Graph vertex");
        }
    }

    std::vector<std::vector<std::size_t>> adjacency_;
};
```

BFS 在入队时标记访问，防止同一节点被多个前驱重复加入队列。DFS 示例在出栈时标记，因此可能重复入栈，但不会重复处理。

## 3. 非连通图怎么遍历

从一个起点只能访问它所在的连通分量。遍历整个图需要在外层扫描所有顶点：

```text
for each vertex:
    if not visited:
        从该顶点启动一次 BFS 或 DFS
        连通分量数量加一
```

如果需要统计连通分量，应让多次搜索共享同一份 `visited`，而不是每次重新创建。

## 4. BFS 和 DFS 的选择

| 需求 | 更常用的遍历 |
|---|---|
| 无权图最短边数 | BFS |
| 分层处理 | BFS |
| 连通性和路径探索 | DFS 或 BFS |
| 拓扑排序 | DFS 或基于入度的 BFS |
| 回溯、检测递归结构 | DFS |

邻接表下，BFS 和 DFS 的时间复杂度都是 `O(V + E)`，额外空间复杂度都是 `O(V)`。

## 5. 常见错误

1. 忘记 `visited`，在有环图中无限循环。
2. BFS 出队时才标记，导致一个节点重复入队。
3. 把无向边只加入一个方向。
4. 默认一次起点遍历可以覆盖非连通图。
5. 把 BFS 当成任意带权图最短路；它只直接适用于无权或等权边。

## 6. 面试口述版

图遍历与树遍历最大的区别是必须记录 visited，因为图可能有环和多条入边。BFS 用队列按层扩展，适合无权最短路；DFS 用递归或栈深入路径。使用邻接表时二者复杂度都是 `O(V+E)`。要覆盖非连通图，还要在外层对每个未访问顶点重新启动一次遍历。
