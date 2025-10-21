package main

import (
	"bufio"
	"fmt"
	"math"
	"os"
)

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func main() {
	in := bufio.NewReader(os.Stdin)
	out := bufio.NewWriter(os.Stdout)
	defer out.Flush()

	var n int
	if _, err := fmt.Fscan(in, &n); err != nil {
		return
	}

	g := make([][]int, n+1)
	deg := make([]int, n+1)
	for i := 0; i < n-1; i++ {
		var a, b int
		fmt.Fscan(in, &a, &b)
		g[a] = append(g[a], b)
		g[b] = append(g[b], a)
		deg[a]++
		deg[b]++
	}

	// соберём листья (degree == 1)
	owner := make([]int, n+1) // какой лист "владеет" вершиной
	dist := make([]int, n+1)  // расстояние до владельца
	q := make([]int, 0, n)

	for v := 1; v <= n; v++ {
		if deg[v] == 1 { // лист
			owner[v] = v
			dist[v] = 0
			q = append(q, v)
		}
	}

	ans := math.MaxInt32
	head := 0
	for head < len(q) {
		u := q[head]
		head++
		for _, v := range g[u] {
			if owner[v] == 0 {
				owner[v] = owner[u]
				dist[v] = dist[u] + 1
				q = append(q, v)
			} else if owner[v] != owner[u] {
				// волны от разных листьев встретились по ребру u-v
				cand := dist[u] + dist[v] + 1
				ans = min(ans, cand)
			}
		}
	}

	// ans обязательно установлен (в дереве >=2 листа), но на всякий случай:
	if ans == math.MaxInt32 {
		ans = 0
	}
	fmt.Fprintln(out, ans)
}
