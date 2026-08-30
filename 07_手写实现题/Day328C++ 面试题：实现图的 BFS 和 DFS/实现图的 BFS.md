# C++ 面试题：实现图的 BFS

## 1. BFS 是什么

BFS（Breadth-First Search，广度优先搜索）从起点开始，按照距离起点的层次逐层访问节点。

它的核心数据结构是队列：

```text
起点入队
   ↓
取出队首节点
   ↓
访问所有尚未访问的邻接点并入队
   ↓
队列为空时结束
```

图与树不同，可能存在环和多条入边，因此必须维护 `visited`。

## 2. 邻接表实现

下面使用邻接表保存图，顶点编号范围为 `[0, vertex_count)`：

```cpp
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

private:
    void check(std::size_t vertex) const {
        if (vertex >= adjacency_.size()) {
            throw std::out_of_range("Graph vertex");
        }
    }

    std::vector<std::vector<std::size_t>> adjacency_;
};
```

## 3. 为什么要在入队时标记 visited

正确顺序是：

```cpp
visited[next] = true;
pending.push(next);
```

如果等到出队时才标记，同一个节点可能被多个前驱重复加入队列。

例如：

```text
0 -> 1
0 -> 2
1 -> 3
2 -> 3
```

处理节点 `1` 和 `2` 时，它们都可能把尚未出队的节点 `3` 加入队列。入队即标记可以保证每个节点最多入队一次。

## 4. 遍历非连通图

从单个起点出发，只能访问该起点所在的连通分量。要遍历整个图，需要扫描所有顶点，并让多次 BFS 共享同一份 `visited`：

```cpp
std::vector<std::size_t> bfs_all() const {
    std::vector<std::size_t> order;
    std::vector<bool> visited(adjacency_.size(), false);
    std::queue<std::size_t> pending;

    for (std::size_t start = 0; start < adjacency_.size(); ++start) {
        if (visited[start]) {
            continue;
        }

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
    }

    return order;
}
```

每次从未访问节点启动 BFS，就发现了一个新的连通分量。对有向图而言，这种扫描得到的是遍历森林，不能直接当作强连通分量算法。

## 5. BFS 与无权最短路

BFS 按层扩展，因此第一次到达某个节点时，使用的边数最少。可以增加 `distance` 和 `parent` 数组记录距离及路径：

```cpp
std::vector<int> distance(adjacency_.size(), -1);
std::vector<std::size_t> parent(adjacency_.size(), adjacency_.size());

distance[start] = 0;
visited[start] = true;
pending.push(start);

while (!pending.empty()) {
    const std::size_t current = pending.front();
    pending.pop();

    for (std::size_t next : adjacency_[current]) {
        if (!visited[next]) {
            visited[next] = true;
            distance[next] = distance[current] + 1;
            parent[next] = current;
            pending.push(next);
        }
    }
}
```

BFS 只直接适用于无权图或所有边权相同的图。一般非负权图应使用 Dijkstra，存在负权边时需要选择其他算法。

## 6. 复杂度

使用邻接表时：

- 时间复杂度：`O(V + E)`；
- `visited`、结果和队列的额外空间：`O(V)`。

无向图中的一条边会在邻接表中保存两次，但渐进复杂度仍然是 `O(V + E)`。

如果使用邻接矩阵，为每个节点扫描全部可能邻居，时间复杂度会变成 `O(V²)`。

## 7. 常见错误

1. 忘记 `visited`，在有环图中无限循环。
2. 出队时才标记，导致节点重复入队。
3. 无向边只加入一个方向。
4. 认为从一个起点可以覆盖非连通图。
5. 把 BFS 当作任意带权图的最短路算法。
6. 没有检查起点和边端点是否越界。

## 8. 面试口述版

BFS 使用队列按层遍历图。节点应该在入队时标记为已访问，避免它被多个前驱重复入队。邻接表实现的时间复杂度是 `O(V+E)`，额外空间复杂度是 `O(V)`。BFS 适合无权图最短边数和分层处理；要覆盖非连通图，需要在外层扫描所有未访问顶点，并共享同一份 `visited`。

