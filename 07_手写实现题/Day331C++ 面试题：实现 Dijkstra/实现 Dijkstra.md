# C++ 面试题：实现 Dijkstra 最短路

## 1. 适用条件

Dijkstra 求单源最短路，要求所有边权非负。它每次确定当前距离最小的未确定节点，再用该节点松弛出边。

存在负权边时，“最短节点已经确定”的贪心前提不再成立，应改用 Bellman-Ford 等算法。

## 2. 邻接表加小根堆实现

```cpp
#include <cstddef>
#include <functional>
#include <limits>
#include <queue>
#include <stdexcept>
#include <utility>
#include <vector>

struct Edge {
    int to;
    long long weight;
};

std::vector<long long> dijkstra(
    const std::vector<std::vector<Edge>>& graph,
    int source) {
    const std::size_t vertex_count = graph.size();
    if (source < 0 ||
        static_cast<std::size_t>(source) >= vertex_count) {
        throw std::out_of_range("source out of range");
    }

    for (const auto& edges : graph) {
        for (const Edge& edge : edges) {
            if (edge.to < 0 ||
                static_cast<std::size_t>(edge.to) >= vertex_count) {
                throw std::out_of_range("edge endpoint out of range");
            }
            if (edge.weight < 0) {
                throw std::invalid_argument(
                    "Dijkstra requires non-negative weights");
            }
        }
    }

    const long long infinity =
        std::numeric_limits<long long>::max();
    std::vector<long long> distance(vertex_count, infinity);

    using State = std::pair<long long, int>;
    std::priority_queue<
        State, std::vector<State>, std::greater<State>> heap;

    distance[source] = 0;
    heap.push({0, source});

    while (!heap.empty()) {
        const long long current_distance = heap.top().first;
        const int current = heap.top().second;
        heap.pop();

        if (current_distance != distance[current]) {
            continue;
        }

        for (const Edge& edge : graph[current]) {
            if (current_distance >
                infinity - edge.weight) {
                continue;
            }

            const long long candidate =
                current_distance + edge.weight;
            if (candidate < distance[edge.to]) {
                distance[edge.to] = candidate;
                heap.push({candidate, edge.to});
            }
        }
    }

    return distance;
}
```

## 3. 为什么允许堆里出现重复节点

C++ 的 `priority_queue` 不支持高效的 decrease-key。距离变小时直接压入新状态；旧状态弹出时，如果它记录的距离不等于当前最短距离，就说明已经过期，直接跳过。

这种“允许重复、弹出时判旧”的写法简单且常用于面试。

## 4. 复杂度和边界

1. 使用邻接表和二叉堆时，时间复杂度为 `O((V + E) log V)`，常写作 `O(E log V)`。
2. 空间复杂度为 `O(V + E)`，堆中可能存在过期状态。
3. 不可达节点的距离保持为 `LLONG_MAX`。
4. 零权边可以正常处理。
5. 加法前必须避免有符号整数溢出。

## 5. 面试口述版

把源点距离设为零并加入小根堆。每次弹出当前距离最小的状态，如果它已经过期就跳过，否则用它松弛所有出边。距离变小时更新数组并压入新状态。算法依赖非负边权，否则已经确定的最短距离可能再次被负权边缩短。
