# -*- coding: utf-8 -*-

DEFAULT_PROBLEMS = [
    {
        "id": 1,
        "title": "LeetCode 1: Two Sum",
        "category": "LeetCode Python",
        "difficulty": "Easy",
        "summary": "Find two numbers in an array that add up to a specific target.",
        "problem_description": "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.\nYou can return the answer in any order.",
        "solution_code": """def twoSum(nums: list[int], target: int) -> list[int]:
    # Use a hash map to store value -> index mapping
    num_map = {}
    
    for index, value in enumerate(nums):
        complement = target - value
        # If the complement exists in the map, we found the pair
        if complement in num_map:
            return [num_map[complement], index]
        # Otherwise, store the index of the current value
        num_map[value] = index
        
    return []  # Fallback (though constraint guarantees a solution)""",
        "explanation": "### Algorithm Analysis\n\n- **Time Complexity:** $O(n)$ where $n$ is the number of elements in the array. We traverse the list containing $n$ elements exactly once. Each lookup in the hash table costs only $O(1)$ time.\n- **Space Complexity:** $O(n)$ to store the key-value pairs in the dictionary/hash map, which stores at most $n$ elements.\n\n### Explanation\nInstead of checking all pairs using a nested loop ($O(n^2)$), we can look for the 'complement' ($target - nums[i]$) of the current number. By storing visited elements in a dictionary, we can check if the complement exists in constant $O(1)$ time.",
        "tags": ["Array", "Hash Table", "Easy"]
    },
    {
        "id": 2,
        "title": "LeetCode 3: Longest Substring Without Repeating Characters",
        "category": "LeetCode Python",
        "difficulty": "Medium",
        "summary": "Find the length of the longest substring without repeating characters.",
        "problem_description": "Given a string `s`, find the length of the longest substring without repeating characters.\n\n**Example:**\nInput: `s = \"abcabcbb\"`\nOutput: `3` (The substring is `\"abc\"`)",
        "solution_code": """def lengthOfLongestSubstring(s: str) -> int:
    char_map = {}  # Stores char -> its last seen index
    max_length = 0
    start = 0      # Left boundary of the sliding window
    
    for end, char in enumerate(s):
        # If char was seen and is within our current window
        if char in char_map and char_map[char] >= start:
            # Shrink/slide window past the previous occurrence
            start = char_map[char] + 1
            
        char_map[char] = end
        max_length = max(max_length, end - start + 1)
        
    return max_length""",
        "explanation": "### Sliding Window Technique\n\n- **Time Complexity:** $O(n)$ where $n$ is the length of the string. The right pointer `end` scans through the string once.\n- **Space Complexity:** $O(min(a, m))$ where $a$ is the alphabet size and $m$ is string length. In the worst case, we store the position of all unique characters.\n\n### Detailed Breakdown\nWe maintain a sliding window `[start, end]`. As we move the `end` pointer to the right, we check if the current character has been seen. If it has been seen, and its index is greater than or equal to `start`, we slide `start` directly to `last_seen_index + 1`. This avoids redundant inner loops, completing the search in a single pass.",
        "tags": ["String", "Sliding Window", "Medium"]
    },
    {
        "id": 3,
        "title": "LeetCode 146: LRU Cache Design",
        "category": "LeetCode Python",
        "difficulty": "Medium",
        "summary": "Design a Least Recently Used (LRU) Cache using double linked lists.",
        "problem_description": "Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.\nImplement the `LRUCache` class:\n- `LRUCache(capacity)` Initialize the LRU cache with positive size capacity.\n- `get(key)` Return the value of the key if it exists, otherwise return -1.\n- `put(key, value)` Update the value of the key if it exists. Otherwise, add the key-value pair. If number of keys exceeds capacity, evict the least recently used key.",
        "solution_code": """class Node:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # Map: key -> Node
        
        # Dummy head and tail to simplify list manipulation
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node):
        # Remove node from double linked list
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add_to_head(self, node: Node):
        # Insert node immediately after dummy head (most recently used)
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            self._add_to_head(node)  # Mark as recently used
            return node.value
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_head(node)
        else:
            if len(self.cache) >= self.capacity:
                # Evict LRU from tail
                lru_node = self.tail.prev
                self._remove(lru_node)
                del self.cache[lru_node.key]
                
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)""",
        "explanation": "### Cache Mechanics\n\n- **Get / Put Time:** $O(1)$ constant time complexity.\n- **Space Complexity:** $O(c)$ where $c$ is the capacity of the cache, storing nodes and keys.\n\n### Implementation Insights\nTo achieve $O(1)$ lookup, we need a hash map. To achieve $O(1)$ eviction order adjustment, we need a doubly linked list. By linking them together, the hash map maps keys to nodes in the doubly linked list, enabling us to instantly jump to any node, remove it, and append it to the front (representing Most Recently Used) when accessed.",
        "tags": ["Design", "Hash Table", "Doubly Linked List", "Medium"]
    },
    {
        "id": 4,
        "title": "LeetCode 200: Number of Islands",
        "category": "LeetCode Python",
        "difficulty": "Medium",
        "summary": "Count the number of separate islands in a 2D binary grid.",
        "problem_description": "Given an `m x n` 2D binary grid `grid` which represents a map of `'1'`s (land) and `'0'`s (water), return the number of islands.\nAn island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically. You may assume all four edges of the grid are all surrounded by water.",
        "solution_code": """def numIslands(grid: list[list[str]]) -> int:
    if not grid:
        return 0
        
    rows, cols = len(grid), len(grid[0])
    island_count = 0
    
    def dfs(r, c):
        # Base case: boundary check or water cell
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] == '0':
            return
            
        # Mark cell as visited by sinking it to '0'
        grid[r][c] = '0'
        
        # Traverse in 4 directions
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                island_count += 1
                dfs(r, c)  # Visit all connected land
                
    return island_count""",
        "explanation": "### Graph Traversal (DFS/BFS)\n\n- **Time Complexity:** $O(M \\times N)$ where $M$ is the number of rows and $N$ is the number of columns. Every element in the grid is visited at most once.\n- **Space Complexity:** $O(M \\times N)$ worst case stack space if the entire grid is one island.\n\n### Explanation\nWe iterate through the grid. When we find a `'1'` (land), we increment our island counter and run a Depth First Search (DFS) to find all horizontally and vertically adjacent land cells, sinking them to `'0'` so they won't be counted again. The number of times we initiate a DFS is the total number of islands.",
        "tags": ["Graph", "DFS", "Matrix", "Medium"]
    },
    {
        "id": 5,
        "title": "LeetCode 23: Merge k Sorted Lists",
        "category": "LeetCode Python",
        "difficulty": "Hard",
        "summary": "Merge k sorted linked lists in O(N log k) time.",
        "problem_description": "You are given an array of `k` linked-lists `lists`, each linked-list is sorted in ascending order.\nMerge all the linked-lists into one sorted linked-list and return it.\n\n**Example:**\nInput: `lists = [[1,4,5],[1,3,4],[2,6]]`\nOutput: `[1,1,2,3,4,4,5,6]`",
        "solution_code": """import heapq

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
        
    # Python 3 compatibility for priority queue comparison
    def __lt__(self, other):
        return self.val < other.val

def mergeKLists(lists: list[ListNode]) -> ListNode:
    min_heap = []
    
    # Push the head node of each non-empty list into the heap
    for idx, lst_head in enumerate(lists):
        if lst_head:
            # Storing (node.val, index, node) to ensure uniqueness
            heapq.heappush(min_heap, (lst_head.val, idx, lst_head))
            
    dummy = ListNode(0)
    curr = dummy
    
    while min_heap:
        val, idx, node = heapq.heappop(min_heap)
        curr.next = node
        curr = curr.next
        
        # If there is a next node, push it to heap
        if node.next:
            heapq.heappush(min_heap, (node.next.val, idx, node.next))
            
    return dummy.next""",
        "explanation": "### Priority Queue (Min-Heap)\n\n- **Time Complexity:** $O(N \\log k)$ where $N$ is the total number of nodes in all lists, and $k$ is the number of linked lists. Inserting and extracting from the heap costs $O(\\log k)$.\n- **Space Complexity:** $O(k)$ auxiliary space for the min-heap containing at most one node from each of the $k$ lists.\n\n### Explanation\nInstead of checking every list head on each step (which would take $O(N \\cdot k)$), we use a min-heap to keep track of the smallest node values across the $k$ list heads. We pop the smallest node from the heap, append it to our merged list, and push its next sibling back into the heap.",
        "tags": ["Linked List", "Divide and Conquer", "Heap (Priority Queue)", "Hard"]
    },
    {
        "id": 6,
        "title": "LeetCode 42: Trapping Rain Water",
        "category": "LeetCode Python",
        "difficulty": "Hard",
        "summary": "Calculate total trapped rain water after rainfall over elevation map.",
        "problem_description": "Given `n` non-negative integers representing an elevation map where the width of each bar is `1`, compute how much water it can trap after raining.\n\n**Example:**\nInput: `height = [0,1,0,2,1,0,1,3,2,1,2,1]`\nOutput: `6`",
        "solution_code": """def trap(height: list[int]) -> int:
    if not height:
        return 0
        
    left, right = 0, len(height) - 1
    left_max, right_max = height[left], height[right]
    water_trapped = 0
    
    while left < right:
        if left_max < right_max:
            left += 1
            left_max = max(left_max, height[left])
            water_trapped += left_max - height[left]
        else:
            right -= 1
            right_max = max(right_max, height[right])
            water_trapped += right_max - height[right]
            
    return water_trapped""",
        "explanation": "### Two Pointer Technique\n\n- **Time Complexity:** $O(n)$ single pass over the array.\n- **Space Complexity:** $O(1)$ constant extra space.\n\n### Explanation\nThe volume of water trapped above any bar is determined by the minimum of the maximum height to its left and right, minus its own height: $Volume = \\min(\\text{left\\_max}, \\text{right\\_max}) - \\text{height}[i]$. By moving pointers from both ends towards the middle, we can greedily compute the boundaries. Since the lower boundary limits the water container's height, we update the pointer on the smaller max side.",
        "tags": ["Array", "Two Pointers", "Dynamic Programming", "Hard"]
    },
    {
        "id": 7,
        "title": "LeetCode 56: Merge Intervals",
        "category": "LeetCode Python",
        "difficulty": "Medium",
        "summary": "Merge overlapping intervals in a collection.",
        "problem_description": "Given an array of `intervals` where `intervals[i] = [start_i, end_i]`, merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.",
        "solution_code": """def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    if not intervals:
        return []
        
    # Sort intervals by their start time
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    
    for current in intervals[1:]:
        prev_start, prev_end = merged[-1]
        curr_start, curr_end = current
        
        # If current interval overlaps with previous merged interval
        if curr_start <= prev_end:
            # Merge them by expanding the end time of previous interval
            merged[-1][1] = max(prev_end, curr_end)
        else:
            # No overlap, append current interval
            merged.append(current)
            
    return merged""",
        "explanation": "### Greedy Algorithm with Sorting\n\n- **Time Complexity:** $O(n \\log n)$ due to sorting. The linear scan takes $O(n)$ time.\n- **Space Complexity:** $O(\\log n)$ or $O(n)$ space depending on the sorting implementation.\n\n### Explanation\nBy sorting intervals by their starting times, overlapping intervals are placed adjacent to each other. We can then iterate through the list, checking if the current interval starts before the last merged interval ends. If so, we merge them; otherwise, we start a new interval.",
        "tags": ["Array", "Sorting", "Medium"]
    },
    {
        "id": 8,
        "title": "LeetCode 121: Best Time to Buy and Sell Stock",
        "category": "LeetCode Python",
        "difficulty": "Easy",
        "summary": "Find maximum profit from buying and selling a stock once.",
        "problem_description": "You are given an array `prices` where `prices[i]` is the price of a given stock on the $i$-th day.\nYou want to maximize your profit by choosing a single day to buy one stock and choosing a different day in the future to sell that stock.\nReturn the maximum profit you can achieve. If you cannot achieve any profit, return `0`.",
        "solution_code": """def maxProfit(prices: list[int]) -> int:
    if not prices:
        return 0
        
    min_price = float('inf')
    max_profit = 0
    
    for price in prices:
        # Keep track of minimum buy price seen so far
        if price < min_price:
            min_price = price
        # Calculate profit if sold today and update max profit
        elif price - min_price > max_profit:
            max_profit = price - min_price
            
    return max_profit""",
        "explanation": "### One-pass Greedy Approach\n\n- **Time Complexity:** $O(n)$ single pass scan.\n- **Space Complexity:** $O(1)$ constant space.\n\n### Explanation\nInstead of a nested loop checking every day against every future day ($O(n^2)$), we maintain a running `min_price` of the stock. As we scan the list, we compute the hypothetical profit we would make if we sold today: $price - min\\_price$. We save the maximum value encountered.",
        "tags": ["Array", "Dynamic Programming", "Easy"]
    },
    {
        "id": 9,
        "title": "LeetCode 207: Course Schedule (Graph)",
        "category": "LeetCode Python",
        "difficulty": "Medium",
        "summary": "Check if a directed graph contains cycles (Topological Sort).",
        "problem_description": "There are a total of `numCourses` courses you have to take, labeled from `0` to `numCourses - 1`.\nYou are given an array `prerequisites` where `prerequisites[i] = [a_i, b_i]` indicates that you must take course `b_i` first if you want to take course `a_i`.\nReturn `True` if you can finish all courses. Otherwise, return `False`.",
        "solution_code": """def canFinish(numCourses: int, prerequisites: list[list[int]]) -> bool:
    # Build adjacency list representation of the graph
    adj_list = {i: [] for i in range(numCourses)}
    for dest, src in prerequisites:
        adj_list[src].append(dest)
        
    # State tracking: 0=unvisited, 1=visiting (on current path), 2=visited
    state = [0] * numCourses
    
    def has_cycle(node):
        if state[node] == 1:
            return True   # Cycle detected
        if state[node] == 2:
            return False  # Already verified cycle-free
            
        state[node] = 1   # Mark as visiting
        
        for neighbor in adj_list[node]:
            if has_cycle(neighbor):
                return True
                
        state[node] = 2   # Mark as fully visited
        return False

    for course in range(numCourses):
        if state[course] == 0:
            if has_cycle(course):
                return False
                
    return True""",
        "explanation": "### Cycle Detection in Directed Graphs\n\n- **Time Complexity:** $O(V + E)$ where $V = numCourses$ and $E = prerequisites$. We visit every vertex and traverse every edge.\n- **Space Complexity:** $O(V + E)$ for graph construction and recursion stack.\n\n### Topological Sorting via DFS\nThis problem is equivalent to determining if a topological ordering of courses exists. A topological order exists if and only if the directed graph contains no cycles. We use Depth First Search (DFS) with three states (tri-color coloring) to detect cycles. If we visit a node currently in the recursion stack (state = 1), a cycle exists.",
        "tags": ["Depth-First Search", "Breadth-First Search", "Graph", "Topological Sort", "Medium"]
    },
    {
        "id": 10,
        "title": "LeetCode 72: Edit Distance (Levenshtein)",
        "category": "LeetCode Python",
        "difficulty": "Hard",
        "summary": "Find minimum insertions, deletions, or substitutions to transform one string into another.",
        "problem_description": "Given two strings `word1` and `word2`, return the minimum number of operations required to convert `word1` to `word2`.\nYou have the following three operations permitted on a word:\n- Insert a character\n- Delete a character\n- Replace a character",
        "solution_code": """def minDistance(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    # DP Table: (m+1) x (n+1)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize base cases (converting empty string)
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
        
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                # If characters match, no new operation needed
                dp[i][j] = dp[i-1][j-1]
            else:
                # Minimum of (Delete, Insert, Replace) + 1
                dp[i][j] = min(
                    dp[i-1][j],    # Delete
                    dp[i][j-1],    # Insert
                    dp[i-1][j-1]   # Replace
                ) + 1
                
    return dp[m][n]""",
        "explanation": "### Dynamic Programming (Bottom-Up)\n\n- **Time Complexity:** $O(M \\times N)$ where $M$ and $N$ are the lengths of the two words. The nested loop fills out the grid.\n- **Space Complexity:** $O(M \\times N)$ to store the DP grid (can be optimized to $O(N)$).\n\n### Subproblem Recurrence Relation\nLet $dp[i][j]$ represent the edit distance of prefixes $word1[0..i-1]$ and $word2[0..j-1]$. If character $word1[i-1] == word2[j-1]$, no edit is needed, so $dp[i][j] = dp[i-1][j-1]$. Otherwise, we take the minimum cost of replacing ($dp[i-1][j-1]$), deleting ($dp[i-1][j]$), or inserting ($dp[i][j-1]$) and add 1.",
        "tags": ["String", "Dynamic Programming", "Hard"]
    },
    {
        "id": 11,
        "title": "PostgreSQL Connection Pool Exhaustion under Spikes",
        "category": "Production Scaling & Systems",
        "difficulty": "Medium",
        "summary": "Mitigate high latency and DB timeouts caused by connection pool exhaustion during traffic surges.",
        "problem_description": "An API service built with Django and PostgreSQL crashed during a flash sale. The database error logs showed `FATAL: remaining connection slots are reserved for non-replication superuser connections` and API latency spiked from 50ms to 30s before dropping requests with 504 gateway timeouts.",
        "solution_code": """# SQLAlchemy / Asyncpg Config Example for FastAPI/Flask
# Preventing connection pool exhaustion using PgBouncer and pool sizing.

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# 1. Use PgBouncer in transaction mode (port 6432) instead of direct PG port (5432)
DATABASE_URL = "postgresql://user:pass@pg-bouncer-host:6432/db_name?sslmode=require"

# 2. Configure robust pool settings
engine = create_engine(
    DATABASE_URL,
    pool_class=QueuePool,
    pool_size=20,          # Keep baseline connections low
    max_overflow=10,       # Allow burst connections under spikes
    pool_timeout=5,        # Wait at most 5 seconds for a connection from pool
    pool_recycle=1800,     # Recycle connection every 30 minutes
    pool_pre_ping=True     # Test connection health before using
)""",
        "explanation": "### Root Cause Analysis\n\nEach PostgreSQL connection spawns a separate backend process on the database server, consuming about 10MB of memory and overhead. Django's default behavior opens a connection per thread/request. Under a traffic spike of 5,000 requests/sec, the maximum connection limit (`max_connections = 100` by default in PG) is instantly reached. Subsequent requests block waiting for a connection, causing thread pool starvation in the API layer.\n\n### Mitigation Strategy\n1. **PgBouncer (Connection Pooler):** Place PgBouncer in front of PostgreSQL configured in **transaction pooling** mode. PgBouncer multiplexes thousands of incoming client connections over a tiny pool of physical DB connections (e.g. 50 client connections to 10 DB connections).\n2. **Shorten Connection Timeouts:** Configure `connect_timeout` and `pool_timeout` in the client application to fail fast rather than stalling threads for 30s.\n3. **Close Connections Early:** Ensure middle-tier middlewares close database connections immediately after query completion rather than holding them open until the HTTP response completes.",
        "tags": ["Database", "PostgreSQL", "PgBouncer", "System Design"]
    },
    {
        "id": 12,
        "title": "Redis Cache Stampede (Thundering Herd)",
        "category": "Production Scaling & Systems",
        "difficulty": "Hard",
        "summary": "Implement XFetch/Probabilistic Early Expiration to solve cache stampedes on hot keys.",
        "problem_description": "A high-traffic homepage cached a hot config key (`global_navigation_menu`) in Redis with a 1-hour TTL. When the key expired, 50,000 concurrent requests found a cache miss simultaneously. They all queried the primary SQL database to rebuild the cache, causing a CPU spike to 100% on the database, locking tables, and triggering a total system outage.",
        "solution_code": """import time
import math
import random

# Cache Client implementing Probabilistic Early Expiration (XFetch algorithm)
class CacheClient:
    def __init__(self, redis_client, db_client):
        self.redis = redis_client
        self.db = db_client

    def xfetch(self, key, ttl_seconds, beta=1.0):
        # Retrieve value and delta (computation time to fetch from DB)
        # Redis stores value as JSON containing: {"data": data, "delta": delta, "ttl": ttl}
        cached = self.redis.get_json(key)
        
        if not cached:
            return self._rebuild_and_cache(key, ttl_seconds)
            
        value = cached["data"]
        delta = cached["delta"]   # Time in seconds taken to read from DB last time
        expiration = cached["expiration"] # Epoch timestamp of expiration
        
        # Probabilistic Early Expiration calculation
        # formula: time() - (delta * beta * ln(rand())) > expiration
        # If true, one of the concurrent clients will proactively rebuild the cache BEFORE it expires.
        if (time.time() - (delta * beta * math.log(random.random()))) > expiration:
            # Rebuild cache asynchronously or inline (safely locks or replaces value)
            return self._rebuild_and_cache(key, ttl_seconds)
            
        return value

    def _rebuild_and_cache(self, key, ttl):
        start_time = time.time()
        # Fetch from SQL DB
        data = self.db.query_navigation_menu()
        delta = time.time() - start_time
        
        expiration = time.time() + ttl
        payload = {
            "data": data,
            "delta": delta,
            "expiration": expiration
        }
        self.redis.set_json(key, payload, ex=ttl + 300) # Keep in Redis slightly longer than logical expiration
        return data""",
        "explanation": "### Cache Stampede Mechanics\n\nWhen a high-traffic cache key expires, the cache goes from $100\\%$ hit rate to $0\\%$ for that key. If the rebuild time (fetching from SQL, formatting JSON) takes $200\\text{ms}$ and traffic is $10,000\\text{ req/sec}$, then $2,000$ database queries are triggered concurrently before the first query can write the value back to the cache.\n\n### The XFetch Solution\nInstead of waiting for the key to expire, we use a probabilistic algorithm (XFetch, developed by Vattani et al.) to expire the key early for a *single* random request as the expiration time approaches. The probability of early expiration increases as the key gets closer to its TTL and is proportional to the database query duration. Only one user experience incurs the database write, seamlessly rebuilding the cache in background.",
        "tags": ["Caching", "Redis", "High Traffic", "System Design"]
    },
    {
        "id": 13,
        "title": "Memory Leak in Python Asynchronous Event Loop",
        "category": "Production Bugs & Debugging",
        "difficulty": "Hard",
        "summary": "Fix unbounded memory growth in asyncio WebSockets caused by unawaited tasks and global references.",
        "problem_description": "A Python asyncio WebSocket server processing IoT sensor telemetry experienced linear memory leaks, growing from 150MB to 8GB over 48 hours and triggering Linux Out-Of-Memory (OOM) killer terminations. Heap analysis showed millions of uncollected `Task` and `Future` objects.",
        "solution_code": """# Buggy code vs Fixed code in asyncio Task creation
import asyncio

class TelemetryServer:
    def __init__(self):
        self.active_tasks = set() # Store strong references to running background tasks

    # --- BUGGY IMPLEMENTATION ---
    async def handle_client_buggy(self, websocket):
        async for message in websocket:
            # Memory Leak: Loop creates an unawaited task for each message.
            # Python's asyncio garbage collection fails to reclaim completed tasks
            # if they are not properly referenced and cleared, or if global events register them.
            asyncio.create_task(self.process_telemetry(message))

    # --- FIXED IMPLEMENTATION ---
    async def handle_client_fixed(self, websocket):
        async for message in websocket:
            task = asyncio.create_task(self.process_telemetry(message))
            
            # 1. Keep a strong reference to prevent garbage collection while running
            self.active_tasks.add(task)
            
            # 2. Add callback to remove task from set upon completion
            task.add_done_callback(self.active_tasks.discard)

    async def process_telemetry(self, data):
        # Simulate processing IO/DB write
        await asyncio.sleep(0.1)
        # Processed!""",
        "explanation": """### Root Cause Analysis

In Python's `asyncio`, tasks spawned via `asyncio.create_task` are scheduled on the event loop. If they are not awaited and no reference is kept, the loop retains a reference in its internal scheduling queue. Under high throughput, if tasks block on slow external I/O (like database writes), they stack up. Furthermore, if references to these tasks are kept in callback cycles or global event managers, they can never be garbage collected, resulting in a severe memory leak.

### Debugging & Resolution Steps
1. **Use `tracemalloc`:** Run `tracemalloc` to capture memory snapshots and identify which objects (specifically `asyncio.Task`) are growing.
2. **Task Reference Management:** Maintain a `set` of active tasks and use `task.add_done_callback(active_tasks.discard)` to remove them immediately upon completion.
3. **Structured Concurrency:** Use `asyncio.TaskGroup` (available in Python 3.11+) or `asyncio.gather` with limits to control execution scope.""",
        "tags": ["Python", "Asyncio", "Memory Leak", "WebSockets"]
    },
    {
        "id": 14,
        "title": "N+1 Query Latency in SQLAlchemy ORM",
        "category": "Production Bugs & Debugging",
        "difficulty": "Medium",
        "summary": "Identify and resolve SQL query explosion caused by lazy loading in ORM relationships.",
        "problem_description": "An API endpoint fetching a list of 100 blog posts along with their authors took 3.2 seconds to resolve, executing 101 separate SQL queries. The ORM was lazy-loading the `Author` relationship for each post in a loop.",
        "solution_code": """# SQLAlchemy Models and Eager Loading Fixes

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base, joinedload, selectinload
from sqlalchemy.future import select

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    author = relationship("User")

# --- BUGGY LAZY-LOADING CODE (Executes 1 + N queries) ---
# select(Post) -> fetches 100 posts
# For each post, accessing post.author.name executes: SELECT * FROM users WHERE id = ?
async def get_posts_buggy(session):
    result = await session.execute(select(Post))
    posts = result.scalars().all()
    return [{"title": p.title, "author": p.author.name} for p in posts]

# --- FIXED EAGER-LOADING CODE (Executes exactly 1 JOIN query) ---
# Using joinedload tells SQLAlchemy to fetch the related User table using a SQL JOIN.
async def get_posts_fixed(session):
    stmt = select(Post).options(joinedload(Post.author))
    result = await session.execute(stmt)
    posts = result.scalars().all()
    return [{"title": p.title, "author": p.author.name} for p in posts]""",
        "explanation": "### N+1 Query Dynamics\n\nThe N+1 query problem occurs when an application loads a collection of $N$ items from a database, and then loops through each item to load a related item (e.g., $N$ details). This results in $1$ query to fetch the list, followed by $N$ separate queries to fetch the child objects, leading to high database latency due to network roundtrips.\n\n### Eager Loading Types\n- **Joined Load (`joinedload`):** Performs a `LEFT OUTER JOIN` in the initial SQL statement. Best for Many-to-One relationships.\n- **Select In Load (`selectinload`):** Emits a second query using the `IN` operator (e.g. `SELECT * FROM users WHERE id IN (1, 2, 3...)`). Best for One-to-Many collections, preventing huge cartesian product tables.",
        "tags": ["Database", "SQLAlchemy", "Python", "ORM"]
    },
    {
        "id": 15,
        "title": "Kafka Consumer Lag & Rebalance Storm",
        "category": "Production Scaling & Systems",
        "difficulty": "Hard",
        "summary": "Resolve Kafka consumer group dropouts and rebalancing loops under heavy message payloads.",
        "problem_description": "During peak hours, an order processing system backed by Kafka began falling behind. As lag accumulated, consumers frequently disconnected from the group, triggering continuous partition rebalancing. During rebalancing, message processing stopped entirely, creating a cascading backlog.",
        "solution_code": """# Python Kafka Consumer (Confluent-Kafka) Optimization Settings
# Preventing rebalance storms by adjusting processing intervals and heartbeat limits.

from confluent_kafka import Consumer

conf = {
    'bootstrap.servers': "kafka-broker-1:9092",
    'group.id': "order-processors",
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,  # Manual commits to ensure processing completeness
    
    # --- OPTIMIZED REBALANCE CONFIG ---
    'session.timeout.ms': 45000,      # Max time to miss heartbeats before eviction (45s)
    'heartbeat.interval.ms': 15000,   # Send heartbeats every 15s (1/3 of session timeout)
    'max.poll.interval.ms': 300000,   # Allow up to 5 minutes to process a single batch
    'max.partition.fetch.bytes': 1048576, # Limit batch size in bytes (1MB) to process quickly
}

consumer = Consumer(conf)
consumer.subscribe(['orders'])""",
        "explanation": "### Rebalance Storm Anatomy\n\nKafka consumers send periodic heartbeats to the broker to prove they are alive. They also poll for new messages in a loop. If a consumer takes too long to process a fetched batch of messages (exceeding `max.poll.interval.ms`), the broker assumes the consumer has hung or died. The broker evicts the consumer and triggers a partition rebalance. The evicted consumer then finishes its batch, tries to rejoin, triggers *another* rebalance, and the group gets stuck in a perpetual 'rebalance storm' where no work is completed.\n\n### Optimization Guide\n1. **Increase Poll Interval:** Set `max.poll.interval.ms` to a value comfortably larger than the worst-case processing time for a single batch.\n2. **Limit Batch Sizes:** Lower the number of records returned in a single poll using settings like `max.poll.records` or `max.partition.fetch.bytes` so processing finishes quickly.\n3. **Decouple Fetch and Process:** Implement a queue-based consumer where the Kafka thread only polls and pushes to an in-memory thread pool for processing.",
        "tags": ["Kafka", "System Design", "Message Queues", "Scaling"]
    },
    {
        "id": 16,
        "title": "Distributed Lock Timeout (Redis Split-Brain)",
        "category": "Production Bugs & Debugging",
        "difficulty": "Medium",
        "summary": "Fix race conditions in distributed systems caused by expired Redis lock leases.",
        "problem_description": "An inventory system used Redis to lock items during checkout to prevent double-booking. Under high CPU load, checkout requests took longer than the 5-second Redis lock TTL. The lock expired, another worker acquired the lock, and the same inventory item was double-sold.",
        "solution_code": """# Secure Distributed Lock with Redlock and Auto-Renewal (Watchdog pattern)
import redis
import time
import uuid
import threading

class RedisDistributedLock:
    def __init__(self, redis_client, lock_key):
        self.r = redis_client
        self.key = lock_key
        self.value = str(uuid.uuid4())
        self.running = False

    def acquire(self, ttl_ms=5000):
        # Set lock only if it doesn't exist (NX) with expiry (PX)
        success = self.r.set(self.key, self.value, nx=True, px=ttl_ms)
        if success:
            self.running = True
            # Spawn a background watchdog thread to renew lock lease
            self.watchdog = threading.Thread(target=self._run_watchdog, args=(ttl_ms,))
            self.watchdog.daemon = True
            self.watchdog.start()
            return True
        return False

    def _run_watchdog(self, ttl_ms):
        renew_interval = (ttl_ms / 1000.0) / 3.0
        while self.running:
            time.sleep(renew_interval)
            # Lua Script: Atomically renew lock if value matches
            lua_renew = \"\"\"
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("pexpire", KEYS[1], ARGV[2])
            else:
                return 0
            end
            \"\"\"
            self.r.eval(lua_renew, 1, self.key, self.value, ttl_ms)

    def release(self):
        self.running = False
        # Lua Script: Atomically release lock only if value matches (prevents releasing others' locks)
        lua_release = \"\"\"
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else:
            return 0
        end
        \"\"\"
        self.r.eval(lua_release, 1, self.key, self.value)""",
        "explanation": "### The Split-Brain Race Condition\n\nIf Client A acquires a distributed lock with a lease time of $5$ seconds, but experiences a stop-the-world garbage collection pause or database stall for $6$ seconds, Redis automatically releases the lock. Client B acquires the lock. Client A resumes and completes its write, believing it still holds the lock. Both clients now execute in the critical section simultaneously, corrupting data.\n\n### The Fix: Watchdog and Atomic Releases\n1. **Lock Watchdog:** Spawn a background thread/task to periodically renew the lock lease (extend TTL) as long as the main processing thread is still actively working.\n2. **Atomic Releases:** Always release locks using a Lua script that checks if the lock value still matches the unique client ID. This prevents Client A from mistakenly releasing a lock currently held by Client B.",
        "tags": ["Redis", "Distributed Systems", "Concurrency", "Medium"]
    },
    {
        "id": 17,
        "title": "FastAPI ThreadPool Starvation",
        "category": "Production Bugs & Debugging",
        "difficulty": "Medium",
        "summary": "Resolve API stalling in async frameworks caused by blocking synchronous calls.",
        "problem_description": "A high-performance FastAPI service crashed when under load. One endpoint performed a heavy image analysis using a synchronous OpenCV library. During analysis, other lightweight endpoints (like health checks) stopped responding entirely, leading to health check failures and orchestrator restarts.",
        "solution_code": """# FastAPI Async vs Sync thread allocation fix
import asyncio
from fastapi import FastAPI
import time

app = FastAPI()

def heavy_blocking_cpu_bound_operation():
    # Simulated OpenCV image processing
    time.sleep(2)
    return "processed_image_metadata"

# --- BUGGY APPROACH (Blocks the single-threaded Event Loop) ---
@app.get("/process-buggy")
async def process_buggy():
    # Crucial Mistake: Running blocking synchronous code inside 'async def'.
    # This blocks the single asyncio thread, freezing the entire API server.
    data = heavy_blocking_cpu_bound_operation()
    return {"status": "done", "data": data}

# --- OPTION 1: Use normal 'def' (FastAPI automatically runs in ThreadPool) ---
@app.get("/process-option1")
def process_option1():
    # FastAPI runs normal 'def' endpoints in an external thread pool automatically.
    data = heavy_blocking_cpu_bound_operation()
    return {"status": "done", "data": data}

# --- OPTION 2: Run in asyncio executor (Explicit async control) ---
@app.get("/process-option2")
async def process_option2():
    loop = asyncio.get_running_loop()
    # Offload the blocking operation to a default thread pool executor
    data = await loop.run_in_executor(None, heavy_blocking_cpu_bound_operation)
    return {"status": "done", "data": data}""",
        "explanation": "### Event Loop Blockage\n\nFastAPI is built on `asyncio` which runs on a **single thread**. When you declare an endpoint with `async def`, the event loop expects the code inside to yield control using `await`. If you run blocking synchronous code (like file I/O, heavy computation, or blocking libraries like requests/OpenCV) inside an `async def`, the single thread of the event loop is entirely blocked. No other request can be handled during this time.\n\n### Threading Guidelines in FastAPI\n- If your endpoint uses blocking libraries: Declare it with regular `def`. FastAPI runs it in a separate thread pool so the async event loop stays free.\n- If your endpoint is fully asynchronous: Declare it with `async def` and use await on all I/O.",
        "tags": ["FastAPI", "Python", "Concurrency", "Medium"]
    },
    {
        "id": 18,
        "title": "Prompt Token Window Overflow in RAG Pipelines",
        "category": "Generative AI & LLMs",
        "difficulty": "Medium",
        "summary": "Manage chunk context sizes to avoid token limit overflow in Retrieval-Augmented Generation.",
        "problem_description": "A company RAG (Retrieval-Augmented Generation) chatbot crashed when answering queries about large financial PDFs. The vector database retrieved dozens of text chunks, creating a combined prompt that exceeded the LLM's context window limit (e.g. 8192 tokens), throwing API errors.",
        "solution_code": """# RAG Prompt Context Limiter with Token Counting (tiktoken)
import tiktoken

def build_safe_rag_prompt(query: str, retrieved_chunks: list[str], max_tokens: int = 6000) -> str:
    # Use the appropriate tokenizer for the target model (e.g. cl100k_base for gpt-4)
    encoding = tiktoken.get_encoding("cl100k_base")
    
    base_prompt_template = "Answer the query based on the context below.\\n\\nContext:\\n{context}\\n\\nQuery: {query}\\nAnswer:"
    
    # Calculate base tokens (template structure + query)
    empty_prompt = base_prompt_template.format(context="", query=query)
    base_tokens = len(encoding.encode(empty_prompt))
    
    available_tokens = max_tokens - base_tokens
    included_chunks = []
    current_tokens = 0
    
    # Sort chunks by relevance score if available
    for chunk in retrieved_chunks:
        chunk_tokens = len(encoding.encode(chunk))
        if current_tokens + chunk_tokens <= available_tokens:
            included_chunks.append(chunk)
            current_tokens += chunk_tokens
        else:
            # Stop adding chunks to prevent token overflow
            break
            
    context_str = "\\n---\\n".join(included_chunks)
    return base_prompt_template.format(context=context_str, query=query)""",
        "explanation": "### Token Management in LLMs\n\nLarge Language Models have a strict maximum context window representing the sum of prompt tokens and generated output tokens. In RAG pipelines, naive retrieval can fetch too many long chunks. If unchecked, sending this context to the LLM throws an API error, degrading system availability.\n\n### Resolution Mechanics\n1. **Eager Token Calculation:** Use model-specific tokenizers (like `tiktoken` for OpenAI or `sentencepiece` for Llama) to count exact token lengths of prompt templates and dynamic query structures.\n2. **Truncation & Rank Filtering:** Add retrieved document chunks to the prompt context one by one in order of retrieval relevance, checking the cumulative token count. Stop adding chunks once the safety threshold is reached.",
        "tags": ["RAG", "LLM", "Generative AI", "Python"]
    },
    {
        "id": 19,
        "title": "LLM Rate Limit (429) Handling w/ Redis Token Bucket",
        "category": "Generative AI & LLMs",
        "difficulty": "Hard",
        "summary": "Implement Redis-backed sliding window rate limiting for LLM API calls.",
        "problem_description": "An enterprise GenAI system hit OpenAI rate limit errors (`RateLimitError: 429 - Too Many Requests`) because multiple async workers sent batches of translation prompts simultaneously, exceeding the Model's Tokens-Per-Minute (TPM) limit.",
        "solution_code": """# Redis-based Token Bucket Rate Limiter for LLM API integration
import time
import redis

class RedisTokenBucketLimiter:
    def __init__(self, redis_client, rate_limit_tpm=10000):
        self.r = redis_client
        self.limit = rate_limit_tpm # Max tokens allowed per minute
        
    def acquire_token_allowance(self, client_id: str, tokens_needed: int) -> bool:
        # Lua script implementing token bucket rate limiting
        # KEYS[1]: client bucket key
        # ARGV[1]: max capacity (limit)
        # ARGV[2]: fill rate per second (limit / 60)
        # ARGV[3]: tokens requested
        # ARGV[4]: current timestamp
        lua_script = \"\"\"
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local fill_rate = tonumber(ARGV[2])
        local requested = tonumber(ARGV[3])
        local now = tonumber(ARGV[4])

        local bucket = redis.call('hgetall', key)
        local last_update = now
        local tokens = capacity

        if #bucket > 0 then
            for i = 1, #bucket, 2 do
                if bucket[i] == 'last_update' then
                    last_update = tonumber(bucket[i+1])
                elseif bucket[i] == 'tokens' then
                    tokens = tonumber(bucket[i+1])
                end
            end
            -- Calculate replenished tokens based on elapsed time
            local elapsed = now - last_update
            tokens = math.min(capacity, tokens + (elapsed * fill_rate))
        end

        if tokens >= requested then
            tokens = tokens - requested
            redis.call('hset', key, 'tokens', tokens, 'last_update', now)
            redis.call('expire', key, 120) -- Keep key active for 2 mins
            return 1 -- Allowed
        else
            return 0 -- Rejected (Rate limited)
        end
        \"\"\"
        fill_rate = self.limit / 60.0
        result = self.r.eval(
            lua_script, 
            1, 
            f"limiter:{client_id}", 
            self.limit, 
            fill_rate, 
            tokens_needed, 
            time.time()
        )
        return bool(result)""",
        "explanation": "### TPM / RPM Rate Limits in LLMs\n\nLLM APIs enforce strict limits on both Requests-Per-Minute (RPM) and Tokens-Per-Minute (TPM). If a user sends a large document containing $80,000$ tokens, they might hit the TPM ceiling immediately, causing subsequent API calls to fail.\n\n### Token Bucket Algorithm\nTo prevent hitting provider-side rate limits, applications should enforce client-side queues. The **Token Bucket** algorithm allows spikes of traffic up to the bucket capacity while throttling the long-term consumption rate to the bucket fill rate. Implementing this in a Redis Lua script ensures atomic check-and-set operations, enabling multiple distributed workers to coordinate rate limits.",
        "tags": ["Redis", "Rate Limiting", "Generative AI", "Infrastructure"]
    },
    {
        "id": 20,
        "title": "Vector DB Retrieval Recall Degradation under High Concurrency",
        "category": "Generative AI & LLMs",
        "difficulty": "Hard",
        "summary": "Fix search precision drops in vector databases by balancing index types and HNSW search configurations.",
        "problem_description": "During a load test of a retrieval system, vector search queries returned low-relevance results (semantic drift). Under high query load, the recall rate of top-K chunks dropped from 95% to 65%. The vector database (Pinecone/Milvus) index was configured for high throughput but poor precision.",
        "solution_code": """# Configuration optimizations for Vector DB search (Milvus/HNSW example)
# Adjusting HNSW parameters to balance QPS (queries per second) vs Recall/Accuracy.

# index_params configuration in Milvus
index_params = {
    "metric_type": "COSINE",
    "index_type": "HNSW",
    "params": {
        # 1. M: Max outgoing links in the graph. Range [4, 64]. Higher M = higher accuracy under load
        "M": 32,
        # 2. efConstruction: Size of dynamic candidate list for index building. Higher = better recall
        "efConstruction": 200
    }
}

# Search parameters override (Crucial for query-time precision tuning)
search_params = {
    "metric_type": "COSINE",
    "params": {
        # ef: Size of dynamic candidate list during query search.
        # Increasing 'ef' improves recall at the cost of slightly higher search latency.
        # Set higher during concurrency spikes to protect search quality.
        "ef": 64 
    }
}""",
        "explanation": "### Vector Index Recall & Concurrency\n\nApproximate Nearest Neighbor (ANN) indexes like HNSW (Hierarchical Navigable Small World) construct a multi-layered graph to quickly search high-dimensional embeddings. Under high concurrency, vector databases allocate resources to handle QPS. If HNSW search bounds (`ef`) are set too small, search paths abort early, missing the true closest neighbors. This leads to retrieval of lower-quality contexts and causes the LLM to write inaccurate or hallucinated answers.\n\n### Optimization Tactics\n1. **Index Parameters Adjustment:** Increase HNSW configuration parameters `M` (e.g. 16 to 32) and `efConstruction` to construct a denser graph with more alternative paths.\n2. **Query Tuning:** Increase query-time candidate list size `ef` parameter. A value of 64 or 128 balances precision and CPU usage.\n3. **Hybrid Search:** Combine sparse lexical search (BM25) with dense vector search (Reciprocal Rank Fusion - RRF) to offset vector search failures.",
        "tags": ["Vector Database", "HNSW", "System Design", "Generative AI"]
    }
]
