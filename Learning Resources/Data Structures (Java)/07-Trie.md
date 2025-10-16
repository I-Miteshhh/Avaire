# Trie (Prefix Tree)

**Difficulty:** Intermediate  
**Learning Time:** 1-2 weeks  
**Interview Frequency:** ⭐⭐⭐⭐ (High - Google, Amazon favorite)

---

## 📚 Table of Contents

1. [Trie Fundamentals](#trie-fundamentals)
2. [Implementation](#implementation)
3. [Interview Problems](#interview-problems)
4. [Advanced Techniques](#advanced-techniques)
5. [Real-World Use Cases](#real-world-use-cases)

---

## Trie Fundamentals

### What is a Trie?

```
Tree-like data structure for storing strings
Each node represents a character
Path from root to node forms a word/prefix

Example Trie for ["cat", "cap", "dog", "do"]:

         root
        /    \
       c      d
       |      |
       a      o
      / \     |
     t   p    g

✅ Fast prefix search: O(m) where m = word length
✅ Space-efficient for common prefixes
✅ Great for autocomplete, spell check
❌ More memory than hash table (lots of nodes)
```

### Time Complexity

| Operation | Time Complexity | Space |
|-----------|-----------------|-------|
| **Insert** | O(m) | O(m) worst |
| **Search** | O(m) | O(1) |
| **StartsWith** | O(m) | O(1) |
| **Delete** | O(m) | O(1) |

**Note:** m = length of word

---

## Implementation

### Basic Trie

```java
/**
 * Standard Trie implementation
 */
class Trie {
    
    private static class TrieNode {
        Map<Character, TrieNode> children;
        boolean isEndOfWord;
        
        TrieNode() {
            children = new HashMap<>();
            isEndOfWord = false;
        }
    }
    
    private TrieNode root;
    
    public Trie() {
        root = new TrieNode();
    }
    
    /**
     * Insert word: O(m) where m = word length
     */
    public void insert(String word) {
        TrieNode current = root;
        
        for (char c : word.toCharArray()) {
            current.children.putIfAbsent(c, new TrieNode());
            current = current.children.get(c);
        }
        
        current.isEndOfWord = true;
    }
    
    /**
     * Search exact word: O(m)
     */
    public boolean search(String word) {
        TrieNode node = searchPrefix(word);
        return node != null && node.isEndOfWord;
    }
    
    /**
     * Check if any word starts with prefix: O(m)
     */
    public boolean startsWith(String prefix) {
        return searchPrefix(prefix) != null;
    }
    
    /**
     * Helper: Search prefix node
     */
    private TrieNode searchPrefix(String prefix) {
        TrieNode current = root;
        
        for (char c : prefix.toCharArray()) {
            if (!current.children.containsKey(c)) {
                return null;
            }
            current = current.children.get(c);
        }
        
        return current;
    }
    
    /**
     * Delete word: O(m)
     */
    public boolean delete(String word) {
        return deleteHelper(root, word, 0);
    }
    
    private boolean deleteHelper(TrieNode current, String word, int index) {
        if (index == word.length()) {
            if (!current.isEndOfWord) {
                return false;  // Word doesn't exist
            }
            
            current.isEndOfWord = false;
            return current.children.isEmpty();  // Can delete if no children
        }
        
        char c = word.charAt(index);
        TrieNode node = current.children.get(c);
        
        if (node == null) {
            return false;  // Word doesn't exist
        }
        
        boolean shouldDeleteChild = deleteHelper(node, word, index + 1);
        
        if (shouldDeleteChild) {
            current.children.remove(c);
            return current.children.isEmpty() && !current.isEndOfWord;
        }
        
        return false;
    }
}
```

### Array-Based Trie (Lowercase Letters Only)

```java
/**
 * Optimized Trie for lowercase letters
 * Faster access with array instead of HashMap
 */
class ArrayTrie {
    
    private static class TrieNode {
        TrieNode[] children;
        boolean isEndOfWord;
        
        TrieNode() {
            children = new TrieNode[26];  // a-z
            isEndOfWord = false;
        }
    }
    
    private TrieNode root;
    
    public ArrayTrie() {
        root = new TrieNode();
    }
    
    /**
     * Insert: O(m)
     */
    public void insert(String word) {
        TrieNode current = root;
        
        for (char c : word.toCharArray()) {
            int index = c - 'a';
            
            if (current.children[index] == null) {
                current.children[index] = new TrieNode();
            }
            
            current = current.children[index];
        }
        
        current.isEndOfWord = true;
    }
    
    /**
     * Search: O(m)
     */
    public boolean search(String word) {
        TrieNode node = searchPrefix(word);
        return node != null && node.isEndOfWord;
    }
    
    /**
     * Starts with: O(m)
     */
    public boolean startsWith(String prefix) {
        return searchPrefix(prefix) != null;
    }
    
    private TrieNode searchPrefix(String prefix) {
        TrieNode current = root;
        
        for (char c : prefix.toCharArray()) {
            int index = c - 'a';
            
            if (current.children[index] == null) {
                return null;
            }
            
            current = current.children[index];
        }
        
        return current;
    }
}
```

### Trie with Word Count

```java
/**
 * Trie that tracks word frequency
 */
class TrieWithCount {
    
    private static class TrieNode {
        Map<Character, TrieNode> children;
        int wordCount;  // Number of times word inserted
        
        TrieNode() {
            children = new HashMap<>();
            wordCount = 0;
        }
    }
    
    private TrieNode root;
    
    public TrieWithCount() {
        root = new TrieNode();
    }
    
    public void insert(String word) {
        TrieNode current = root;
        
        for (char c : word.toCharArray()) {
            current.children.putIfAbsent(c, new TrieNode());
            current = current.children.get(c);
        }
        
        current.wordCount++;
    }
    
    public int count(String word) {
        TrieNode node = searchPrefix(word);
        return node != null ? node.wordCount : 0;
    }
    
    private TrieNode searchPrefix(String prefix) {
        TrieNode current = root;
        
        for (char c : prefix.toCharArray()) {
            if (!current.children.containsKey(c)) {
                return null;
            }
            current = current.children.get(c);
        }
        
        return current;
    }
}
```

---

## Interview Problems

### Problem 1: Implement Trie (LeetCode 208)

```java
/**
 * Basic Trie with insert, search, startsWith
 * Already implemented above
 */
```

### Problem 2: Add and Search Word (LeetCode 211)

```java
/**
 * Support wildcard '.' that matches any character
 * 
 * Time: O(m) insert, O(26^m) search (worst case with all dots)
 */
class WordDictionary {
    
    private static class TrieNode {
        Map<Character, TrieNode> children;
        boolean isEndOfWord;
        
        TrieNode() {
            children = new HashMap<>();
            isEndOfWord = false;
        }
    }
    
    private TrieNode root;
    
    public WordDictionary() {
        root = new TrieNode();
    }
    
    public void addWord(String word) {
        TrieNode current = root;
        
        for (char c : word.toCharArray()) {
            current.children.putIfAbsent(c, new TrieNode());
            current = current.children.get(c);
        }
        
        current.isEndOfWord = true;
    }
    
    /**
     * Search with wildcard support
     */
    public boolean search(String word) {
        return searchHelper(word, 0, root);
    }
    
    private boolean searchHelper(String word, int index, TrieNode node) {
        if (index == word.length()) {
            return node.isEndOfWord;
        }
        
        char c = word.charAt(index);
        
        if (c == '.') {
            // Try all children
            for (TrieNode child : node.children.values()) {
                if (searchHelper(word, index + 1, child)) {
                    return true;
                }
            }
            return false;
        } else {
            TrieNode child = node.children.get(c);
            if (child == null) {
                return false;
            }
            return searchHelper(word, index + 1, child);
        }
    }
}
```

### Problem 3: Word Search II (LeetCode 212)

```java
/**
 * Find all words from dictionary in 2D board
 * 
 * Time: O(m * n * 4^L) where L = max word length
 * Space: O(total characters in all words)
 */
public List<String> findWords(char[][] board, String[] words) {
    // Build Trie
    TrieNode root = new TrieNode();
    for (String word : words) {
        insert(root, word);
    }
    
    Set<String> result = new HashSet<>();
    int m = board.length;
    int n = board[0].length;
    
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            dfs(board, i, j, root, result);
        }
    }
    
    return new ArrayList<>(result);
}

private static class TrieNode {
    Map<Character, TrieNode> children = new HashMap<>();
    String word;  // Store complete word at end
}

private void insert(TrieNode root, String word) {
    TrieNode current = root;
    
    for (char c : word.toCharArray()) {
        current.children.putIfAbsent(c, new TrieNode());
        current = current.children.get(c);
    }
    
    current.word = word;
}

private void dfs(char[][] board, int i, int j, TrieNode node, Set<String> result) {
    if (i < 0 || i >= board.length || j < 0 || j >= board[0].length) {
        return;
    }
    
    char c = board[i][j];
    
    if (c == '#' || !node.children.containsKey(c)) {
        return;
    }
    
    TrieNode next = node.children.get(c);
    
    if (next.word != null) {
        result.add(next.word);
        next.word = null;  // Avoid duplicates
    }
    
    board[i][j] = '#';  // Mark visited
    
    dfs(board, i + 1, j, next, result);
    dfs(board, i - 1, j, next, result);
    dfs(board, i, j + 1, next, result);
    dfs(board, i, j - 1, next, result);
    
    board[i][j] = c;  // Restore
}
```

### Problem 4: Autocomplete System (LeetCode 642)

```java
/**
 * Design search autocomplete system
 * 
 * Time: O(m + n log n) where m = prefix length, n = matching sentences
 */
class AutocompleteSystem {
    
    private static class TrieNode {
        Map<Character, TrieNode> children;
        Map<String, Integer> sentences;  // sentence -> frequency
        
        TrieNode() {
            children = new HashMap<>();
            sentences = new HashMap<>();
        }
    }
    
    private TrieNode root;
    private StringBuilder currentInput;
    private TrieNode currentNode;
    
    public AutocompleteSystem(String[] sentences, int[] times) {
        root = new TrieNode();
        currentInput = new StringBuilder();
        currentNode = root;
        
        // Build Trie
        for (int i = 0; i < sentences.length; i++) {
            insert(sentences[i], times[i]);
        }
    }
    
    private void insert(String sentence, int frequency) {
        TrieNode current = root;
        
        for (char c : sentence.toCharArray()) {
            current.children.putIfAbsent(c, new TrieNode());
            current = current.children.get(c);
            current.sentences.put(sentence, current.sentences.getOrDefault(sentence, 0) + frequency);
        }
    }
    
    public List<String> input(char c) {
        if (c == '#') {
            // End of input, save sentence
            String sentence = currentInput.toString();
            insert(sentence, 1);
            
            currentInput = new StringBuilder();
            currentNode = root;
            
            return new ArrayList<>();
        }
        
        currentInput.append(c);
        
        if (currentNode != null && currentNode.children.containsKey(c)) {
            currentNode = currentNode.children.get(c);
            
            // Get top 3 sentences
            return getTop3(currentNode.sentences);
        } else {
            currentNode = null;
            return new ArrayList<>();
        }
    }
    
    private List<String> getTop3(Map<String, Integer> sentences) {
        PriorityQueue<Map.Entry<String, Integer>> pq = new PriorityQueue<>(
            (a, b) -> a.getValue().equals(b.getValue()) ? 
                      b.getKey().compareTo(a.getKey()) :  // Lexicographically smaller
                      a.getValue() - b.getValue()          // Lower frequency
        );
        
        for (Map.Entry<String, Integer> entry : sentences.entrySet()) {
            pq.offer(entry);
            
            if (pq.size() > 3) {
                pq.poll();
            }
        }
        
        List<String> result = new ArrayList<>();
        while (!pq.isEmpty()) {
            result.add(0, pq.poll().getKey());
        }
        
        return result;
    }
}
```

### Problem 5: Replace Words (LeetCode 648)

```java
/**
 * Replace words with their shortest root from dictionary
 * 
 * Example: dict=["cat","bat","rat"], sentence="the cattle was rattled by the battery"
 *       → "the cat was rat by the bat"
 * 
 * Time: O(total characters in dict + sentence)
 */
public String replaceWords(List<String> dictionary, String sentence) {
    // Build Trie
    TrieNode root = new TrieNode();
    for (String word : dictionary) {
        insertRoot(root, word);
    }
    
    String[] words = sentence.split(" ");
    StringBuilder result = new StringBuilder();
    
    for (String word : words) {
        if (result.length() > 0) {
            result.append(" ");
        }
        
        String replacement = findShortest Root(root, word);
        result.append(replacement != null ? replacement : word);
    }
    
    return result.toString();
}

private static class TrieNode {
    Map<Character, TrieNode> children = new HashMap<>();
    boolean isRoot;
}

private void insertRoot(TrieNode root, String word) {
    TrieNode current = root;
    
    for (char c : word.toCharArray()) {
        current.children.putIfAbsent(c, new TrieNode());
        current = current.children.get(c);
    }
    
    current.isRoot = true;
}

private String findShortestRoot(TrieNode root, String word) {
    TrieNode current = root;
    StringBuilder prefix = new StringBuilder();
    
    for (char c : word.toCharArray()) {
        if (!current.children.containsKey(c)) {
            return null;  // No root found
        }
        
        prefix.append(c);
        current = current.children.get(c);
        
        if (current.isRoot) {
            return prefix.toString();  // Found shortest root
        }
    }
    
    return null;
}
```

### Problem 6: Longest Word in Dictionary (LeetCode 720)

```java
/**
 * Find longest word that can be built one character at a time
 * 
 * Time: O(sum of word lengths)
 */
public String longestWord(String[] words) {
    TrieNode root = new TrieNode();
    
    // Build Trie
    for (String word : words) {
        insert(root, word);
    }
    
    return dfs(root);
}

private static class TrieNode {
    Map<Character, TrieNode> children = new HashMap<>();
    String word;
}

private void insert(TrieNode root, String word) {
    TrieNode current = root;
    
    for (char c : word.toCharArray()) {
        current.children.putIfAbsent(c, new TrieNode());
        current = current.children.get(c);
    }
    
    current.word = word;
}

private String dfs(TrieNode node) {
    String longest = node.word != null ? node.word : "";
    
    for (TrieNode child : node.children.values()) {
        if (child.word != null) {  // Can be built
            String candidate = dfs(child);
            
            if (candidate.length() > longest.length() ||
                (candidate.length() == longest.length() && candidate.compareTo(longest) < 0)) {
                longest = candidate;
            }
        }
    }
    
    return longest;
}
```

---

## Advanced Techniques

### 1. Compressed Trie (Radix Tree)

```java
/**
 * Compress paths with only one child
 * Saves space for long unique suffixes
 */
class CompressedTrie {
    
    private static class RadixNode {
        Map<String, RadixNode> children;
        boolean isEndOfWord;
        
        RadixNode() {
            children = new HashMap<>();
            isEndOfWord = false;
        }
    }
    
    private RadixNode root;
    
    public CompressedTrie() {
        root = new RadixNode();
    }
    
    public void insert(String word) {
        RadixNode current = root;
        int i = 0;
        
        while (i < word.length()) {
            boolean found = false;
            
            for (Map.Entry<String, RadixNode> entry : current.children.entrySet()) {
                String edge = entry.getKey();
                RadixNode child = entry.getValue();
                
                int j = 0;
                while (j < edge.length() && i + j < word.length() && 
                       edge.charAt(j) == word.charAt(i + j)) {
                    j++;
                }
                
                if (j > 0) {
                    found = true;
                    
                    if (j < edge.length()) {
                        // Split edge
                        String commonPrefix = edge.substring(0, j);
                        String edgeRemainder = edge.substring(j);
                        
                        RadixNode newChild = new RadixNode();
                        newChild.children.put(edgeRemainder, child);
                        
                        current.children.remove(edge);
                        current.children.put(commonPrefix, newChild);
                        
                        current = newChild;
                    } else {
                        current = child;
                    }
                    
                    i += j;
                    break;
                }
            }
            
            if (!found) {
                RadixNode newChild = new RadixNode();
                current.children.put(word.substring(i), newChild);
                current = newChild;
                break;
            }
        }
        
        current.isEndOfWord = true;
    }
}
```

### 2. Suffix Trie

```java
/**
 * Store all suffixes of a string
 * Useful for substring search
 */
class SuffixTrie {
    
    private Trie trie;
    
    public SuffixTrie(String text) {
        trie = new Trie();
        
        // Insert all suffixes
        for (int i = 0; i < text.length(); i++) {
            trie.insert(text.substring(i));
        }
    }
    
    /**
     * Check if pattern exists as substring
     */
    public boolean contains(String pattern) {
        return trie.startsWith(pattern);
    }
}
```

---

## Real-World Use Cases

### 1. Autocomplete/Type-Ahead

```java
/**
 * Search suggestions for user input
 */
class Autocomplete {
    
    private Trie trie;
    
    public Autocomplete(List<String> dictionary) {
        trie = new Trie();
        for (String word : dictionary) {
            trie.insert(word.toLowerCase());
        }
    }
    
    public List<String> getSuggestions(String prefix, int limit) {
        List<String> suggestions = new ArrayList<>();
        TrieNode node = trie.searchPrefix(prefix.toLowerCase());
        
        if (node == null) {
            return suggestions;
        }
        
        collectWords(node, prefix, suggestions, limit);
        return suggestions;
    }
    
    private void collectWords(TrieNode node, String currentWord, 
                             List<String> suggestions, int limit) {
        if (suggestions.size() >= limit) {
            return;
        }
        
        if (node.isEndOfWord) {
            suggestions.add(currentWord);
        }
        
        for (Map.Entry<Character, TrieNode> entry : node.children.entrySet()) {
            collectWords(entry.getValue(), currentWord + entry.getKey(), suggestions, limit);
        }
    }
}
```

### 2. IP Routing Table

```java
/**
 * Longest prefix matching for IP routing
 */
class IPRoutingTable {
    
    private static class TrieNode {
        TrieNode[] children;  // 0 or 1 for binary
        String gateway;
        
        TrieNode() {
            children = new TrieNode[2];
        }
    }
    
    private TrieNode root;
    
    public IPRoutingTable() {
        root = new TrieNode();
    }
    
    /**
     * Add route with CIDR notation
     */
    public void addRoute(String cidr, String gateway) {
        String[] parts = cidr.split("/");
        String ip = parts[0];
        int prefixLength = Integer.parseInt(parts[1]);
        
        String binary = ipToBinary(ip);
        TrieNode current = root;
        
        for (int i = 0; i < prefixLength; i++) {
            int bit = binary.charAt(i) - '0';
            
            if (current.children[bit] == null) {
                current.children[bit] = new TrieNode();
            }
            
            current = current.children[bit];
        }
        
        current.gateway = gateway;
    }
    
    /**
     * Find longest prefix match
     */
    public String findGateway(String ip) {
        String binary = ipToBinary(ip);
        TrieNode current = root;
        String lastGateway = null;
        
        for (char c : binary.toCharArray()) {
            int bit = c - '0';
            
            if (current.children[bit] == null) {
                break;
            }
            
            current = current.children[bit];
            
            if (current.gateway != null) {
                lastGateway = current.gateway;
            }
        }
        
        return lastGateway;
    }
    
    private String ipToBinary(String ip) {
        String[] octets = ip.split("\\.");
        StringBuilder binary = new StringBuilder();
        
        for (String octet : octets) {
            binary.append(String.format("%8s", 
                Integer.toBinaryString(Integer.parseInt(octet))).replace(' ', '0'));
        }
        
        return binary.toString();
    }
}
```

### 3. Spell Checker

```java
/**
 * Spell checking with edit distance
 */
class SpellChecker {
    
    private Trie dictionary;
    
    public SpellChecker(List<String> words) {
        dictionary = new Trie();
        for (String word : words) {
            dictionary.insert(word.toLowerCase());
        }
    }
    
    public boolean isCorrect(String word) {
        return dictionary.search(word.toLowerCase());
    }
    
    /**
     * Find suggestions within edit distance 1
     */
    public List<String> getSuggestions(String word) {
        List<String> suggestions = new ArrayList<>();
        String lower = word.toLowerCase();
        
        // Delete one character
        for (int i = 0; i < lower.length(); i++) {
            String candidate = lower.substring(0, i) + lower.substring(i + 1);
            if (dictionary.search(candidate)) {
                suggestions.add(candidate);
            }
        }
        
        // Replace one character
        for (int i = 0; i < lower.length(); i++) {
            for (char c = 'a'; c <= 'z'; c++) {
                String candidate = lower.substring(0, i) + c + lower.substring(i + 1);
                if (dictionary.search(candidate)) {
                    suggestions.add(candidate);
                }
            }
        }
        
        // Insert one character
        for (int i = 0; i <= lower.length(); i++) {
            for (char c = 'a'; c <= 'z'; c++) {
                String candidate = lower.substring(0, i) + c + lower.substring(i);
                if (dictionary.search(candidate)) {
                    suggestions.add(candidate);
                }
            }
        }
        
        return new ArrayList<>(new HashSet<>(suggestions));
    }
}
```

---

## 🎯 Interview Tips

### Trie Patterns

1. **Prefix Search**: Autocomplete, type-ahead
2. **Word Game**: Boggle, Scrabble, word search
3. **Routing**: IP routing, URL matching
4. **Spell Check**: Dictionary lookups
5. **String Matching**: Multiple pattern search

### When to Use Trie

**Use Trie when:**
- ✅ Many prefix queries
- ✅ Autocomplete functionality
- ✅ Dictionary with common prefixes
- ✅ Pattern matching in strings
- ✅ Routing tables

**Avoid Trie when:**
- ❌ Single word lookups → use HashSet
- ❌ Memory constrained → use compressed trie
- ❌ No prefix queries → use HashMap

### Common Mistakes

```java
// ❌ BAD: Using HashMap for each character (slow)
Map<Character, TrieNode> children = new HashMap<>();

// ✅ GOOD: Use array for lowercase letters
TrieNode[] children = new TrieNode[26];

// ❌ BAD: Not handling case sensitivity
trie.insert("Apple");
trie.search("apple");  // Returns false!

// ✅ GOOD: Normalize case
trie.insert(word.toLowerCase());
```

---

**Next:** [Segment Tree and Fenwick Tree](./08-Advanced-Trees.md) — Range query data structures
