# String Algorithms

**Difficulty:** Medium-Hard  
**Learning Time:** 5-7 days  
**Interview Frequency:** ⭐⭐⭐⭐ (High)  
**Common In:** Google, Amazon, Microsoft, Pattern Matching Problems

---

## 📚 Table of Contents

1. [KMP Pattern Matching](#kmp-pattern-matching)
2. [Rabin-Karp Algorithm](#rabin-karp-algorithm)
3. [Z-Algorithm](#z-algorithm)
4. [Manacher's Algorithm](#manachers-algorithm)
5. [Trie Applications](#trie-applications)
6. [Real-World Applications](#real-world-applications)

---

## KMP Pattern Matching

**Knuth-Morris-Pratt Algorithm:** Efficient pattern matching using **LPS (Longest Prefix Suffix)** array.

### Time Complexity: O(n + m)
- **n:** text length
- **m:** pattern length

### Key Insight

Don't re-compare characters we know match. Use LPS array to skip redundant comparisons.

### LPS Array

**LPS[i]:** Length of longest proper prefix of pattern[0..i] that is also suffix.

**Example:** pattern = "ABABC"
- LPS = [0, 0, 1, 2, 0]

### Implementation

```java
/**
 * KMP Pattern Matching
 * Time: O(n + m), Space: O(m)
 */
class KMP {
    
    /**
     * Find all occurrences of pattern in text
     */
    public List<Integer> kmpSearch(String text, String pattern) {
        List<Integer> result = new ArrayList<>();
        
        if (pattern.isEmpty()) return result;
        
        // Build LPS array
        int[] lps = computeLPS(pattern);
        
        int i = 0;  // Index for text
        int j = 0;  // Index for pattern
        
        while (i < text.length()) {
            if (text.charAt(i) == pattern.charAt(j)) {
                i++;
                j++;
                
                if (j == pattern.length()) {
                    // Pattern found at index i - j
                    result.add(i - j);
                    j = lps[j - 1];  // Continue searching for overlapping patterns
                }
            } else {
                if (j != 0) {
                    j = lps[j - 1];  // Skip using LPS
                } else {
                    i++;
                }
            }
        }
        
        return result;
    }
    
    /**
     * Compute LPS (Longest Prefix Suffix) array
     */
    private int[] computeLPS(String pattern) {
        int m = pattern.length();
        int[] lps = new int[m];
        int len = 0;  // Length of previous longest prefix suffix
        int i = 1;
        
        lps[0] = 0;  // LPS of first character is always 0
        
        while (i < m) {
            if (pattern.charAt(i) == pattern.charAt(len)) {
                len++;
                lps[i] = len;
                i++;
            } else {
                if (len != 0) {
                    len = lps[len - 1];  // Try smaller prefix
                } else {
                    lps[i] = 0;
                    i++;
                }
            }
        }
        
        return lps;
    }
}

/**
 * LeetCode 28: Find the Index of First Occurrence
 */
class Solution {
    public int strStr(String haystack, String needle) {
        if (needle.isEmpty()) return 0;
        
        int[] lps = computeLPS(needle);
        
        int i = 0;
        int j = 0;
        
        while (i < haystack.length()) {
            if (haystack.charAt(i) == needle.charAt(j)) {
                i++;
                j++;
                
                if (j == needle.length()) {
                    return i - j;
                }
            } else {
                if (j != 0) {
                    j = lps[j - 1];
                } else {
                    i++;
                }
            }
        }
        
        return -1;
    }
    
    private int[] computeLPS(String pattern) {
        int m = pattern.length();
        int[] lps = new int[m];
        int len = 0;
        int i = 1;
        
        while (i < m) {
            if (pattern.charAt(i) == pattern.charAt(len)) {
                lps[i++] = ++len;
            } else {
                if (len != 0) {
                    len = lps[len - 1];
                } else {
                    lps[i++] = 0;
                }
            }
        }
        
        return lps;
    }
}
```

---

## Rabin-Karp Algorithm

**Rolling hash** for pattern matching.

### Time Complexity
- **Average:** O(n + m)
- **Worst:** O(nm) with many hash collisions

### Key Insight

Use hash to quickly compare substrings. Only verify character-by-character on hash match.

### Implementation

```java
/**
 * Rabin-Karp Pattern Matching with Rolling Hash
 * Time: O(n + m) average, Space: O(1)
 */
class RabinKarp {
    private static final int PRIME = 101;  // Prime for hashing
    private static final int BASE = 256;   // Number of characters
    
    /**
     * Find all occurrences of pattern in text
     */
    public List<Integer> search(String text, String pattern) {
        List<Integer> result = new ArrayList<>();
        
        int n = text.length();
        int m = pattern.length();
        
        if (m > n) return result;
        
        // Calculate hash of pattern and first window of text
        long patternHash = 0;
        long textHash = 0;
        long h = 1;  // BASE^(m-1) % PRIME
        
        // Calculate h = BASE^(m-1) % PRIME
        for (int i = 0; i < m - 1; i++) {
            h = (h * BASE) % PRIME;
        }
        
        // Calculate initial hashes
        for (int i = 0; i < m; i++) {
            patternHash = (BASE * patternHash + pattern.charAt(i)) % PRIME;
            textHash = (BASE * textHash + text.charAt(i)) % PRIME;
        }
        
        // Slide pattern over text
        for (int i = 0; i <= n - m; i++) {
            // Check if hashes match
            if (patternHash == textHash) {
                // Verify character by character (handle collisions)
                boolean match = true;
                for (int j = 0; j < m; j++) {
                    if (text.charAt(i + j) != pattern.charAt(j)) {
                        match = false;
                        break;
                    }
                }
                
                if (match) {
                    result.add(i);
                }
            }
            
            // Calculate hash for next window
            if (i < n - m) {
                textHash = (BASE * (textHash - text.charAt(i) * h) + 
                           text.charAt(i + m)) % PRIME;
                
                // Handle negative hash
                if (textHash < 0) {
                    textHash += PRIME;
                }
            }
        }
        
        return result;
    }
}

/**
 * LeetCode 1392: Longest Happy Prefix
 * (Find longest prefix that is also suffix)
 */
class Solution {
    private static final int MOD = 1_000_000_007;
    private static final int BASE = 26;
    
    public String longestPrefix(String s) {
        int n = s.length();
        long prefixHash = 0;
        long suffixHash = 0;
        long power = 1;
        int maxLen = 0;
        
        for (int i = 0; i < n - 1; i++) {
            // Add to prefix hash
            prefixHash = (prefixHash * BASE + (s.charAt(i) - 'a')) % MOD;
            
            // Add to suffix hash (from right)
            suffixHash = (suffixHash + (s.charAt(n - 1 - i) - 'a') * power) % MOD;
            power = (power * BASE) % MOD;
            
            if (prefixHash == suffixHash) {
                maxLen = i + 1;
            }
        }
        
        return s.substring(0, maxLen);
    }
}
```

---

## Z-Algorithm

**Z[i]:** Length of longest substring starting from i that matches prefix.

### Time Complexity: O(n)

### Implementation

```java
/**
 * Z-Algorithm for Pattern Matching
 * Time: O(n + m), Space: O(n + m)
 */
class ZAlgorithm {
    
    /**
     * Calculate Z array
     * Z[i] = length of longest substring starting at i matching prefix
     */
    public int[] calculateZ(String s) {
        int n = s.length();
        int[] z = new int[n];
        
        int left = 0;
        int right = 0;
        
        for (int i = 1; i < n; i++) {
            if (i > right) {
                // Outside current Z-box, calculate from scratch
                left = right = i;
                
                while (right < n && s.charAt(right - left) == s.charAt(right)) {
                    right++;
                }
                
                z[i] = right - left;
                right--;
            } else {
                // Inside Z-box, use previously computed values
                int k = i - left;
                
                if (z[k] < right - i + 1) {
                    z[i] = z[k];
                } else {
                    left = i;
                    
                    while (right < n && s.charAt(right - left) == s.charAt(right)) {
                        right++;
                    }
                    
                    z[i] = right - left;
                    right--;
                }
            }
        }
        
        return z;
    }
    
    /**
     * Pattern matching using Z-algorithm
     */
    public List<Integer> search(String text, String pattern) {
        List<Integer> result = new ArrayList<>();
        
        // Concatenate pattern and text with separator
        String combined = pattern + "$" + text;
        int[] z = calculateZ(combined);
        
        int m = pattern.length();
        
        for (int i = 0; i < z.length; i++) {
            if (z[i] == m) {
                result.add(i - m - 1);  // Pattern found
            }
        }
        
        return result;
    }
}
```

---

## Manacher's Algorithm

**Find longest palindromic substring in O(n) time.**

### Key Insight

Use previously computed palindrome information to avoid redundant checks.

### Implementation

```java
/**
 * Manacher's Algorithm for Longest Palindrome
 * Time: O(n), Space: O(n)
 */
class Manacher {
    
    /**
     * Find longest palindromic substring
     */
    public String longestPalindrome(String s) {
        if (s == null || s.isEmpty()) return "";
        
        // Transform string to avoid even/odd length handling
        String transformed = preprocess(s);
        int n = transformed.length();
        
        int[] p = new int[n];  // p[i] = radius of palindrome centered at i
        int center = 0;
        int right = 0;
        
        int maxLen = 0;
        int maxCenter = 0;
        
        for (int i = 0; i < n; i++) {
            // Mirror of i with respect to center
            int mirror = 2 * center - i;
            
            if (i < right) {
                p[i] = Math.min(right - i, p[mirror]);
            }
            
            // Expand palindrome centered at i
            int a = i + (1 + p[i]);
            int b = i - (1 + p[i]);
            
            while (a < n && b >= 0 && transformed.charAt(a) == transformed.charAt(b)) {
                p[i]++;
                a++;
                b--;
            }
            
            // Update center and right boundary
            if (i + p[i] > right) {
                center = i;
                right = i + p[i];
            }
            
            // Track maximum palindrome
            if (p[i] > maxLen) {
                maxLen = p[i];
                maxCenter = i;
            }
        }
        
        // Extract palindrome from original string
        int start = (maxCenter - maxLen) / 2;
        return s.substring(start, start + maxLen);
    }
    
    /**
     * Transform "abc" to "^#a#b#c#$"
     * ^ and $ are sentinels to avoid boundary checks
     */
    private String preprocess(String s) {
        StringBuilder sb = new StringBuilder("^");
        for (char c : s.toCharArray()) {
            sb.append("#").append(c);
        }
        sb.append("#$");
        return sb.toString();
    }
}

/**
 * LeetCode 5: Longest Palindromic Substring
 */
class Solution {
    public String longestPalindrome(String s) {
        if (s == null || s.isEmpty()) return "";
        
        String transformed = "#";
        for (char c : s.toCharArray()) {
            transformed += c + "#";
        }
        
        int n = transformed.length();
        int[] p = new int[n];
        int center = 0;
        int right = 0;
        
        int maxLen = 0;
        int maxCenter = 0;
        
        for (int i = 1; i < n - 1; i++) {
            int mirror = 2 * center - i;
            
            if (i < right) {
                p[i] = Math.min(right - i, p[mirror]);
            }
            
            while (i + p[i] + 1 < n && i - p[i] - 1 >= 0 &&
                   transformed.charAt(i + p[i] + 1) == transformed.charAt(i - p[i] - 1)) {
                p[i]++;
            }
            
            if (i + p[i] > right) {
                center = i;
                right = i + p[i];
            }
            
            if (p[i] > maxLen) {
                maxLen = p[i];
                maxCenter = i;
            }
        }
        
        int start = (maxCenter - maxLen) / 2;
        return s.substring(start, start + maxLen);
    }
}

/**
 * Alternative: Expand around center (O(n²) but simpler)
 */
class SolutionExpand {
    public String longestPalindrome(String s) {
        if (s == null || s.isEmpty()) return "";
        
        int start = 0;
        int maxLen = 0;
        
        for (int i = 0; i < s.length(); i++) {
            // Odd length palindrome
            int len1 = expandAroundCenter(s, i, i);
            
            // Even length palindrome
            int len2 = expandAroundCenter(s, i, i + 1);
            
            int len = Math.max(len1, len2);
            
            if (len > maxLen) {
                maxLen = len;
                start = i - (len - 1) / 2;
            }
        }
        
        return s.substring(start, start + maxLen);
    }
    
    private int expandAroundCenter(String s, int left, int right) {
        while (left >= 0 && right < s.length() && s.charAt(left) == s.charAt(right)) {
            left--;
            right++;
        }
        return right - left - 1;
    }
}
```

---

## Trie Applications

### 1. Word Search II

**LeetCode 212**

```java
/**
 * Find all words from dictionary in board
 * Time: O(m*n*4^L) where L = max word length
 */
class Solution {
    
    class TrieNode {
        Map<Character, TrieNode> children = new HashMap<>();
        String word = null;
    }
    
    public List<String> findWords(char[][] board, String[] words) {
        // Build trie
        TrieNode root = new TrieNode();
        for (String word : words) {
            TrieNode node = root;
            for (char c : word.toCharArray()) {
                node.children.putIfAbsent(c, new TrieNode());
                node = node.children.get(c);
            }
            node.word = word;
        }
        
        List<String> result = new ArrayList<>();
        
        for (int i = 0; i < board.length; i++) {
            for (int j = 0; j < board[0].length; j++) {
                dfs(board, i, j, root, result);
            }
        }
        
        return result;
    }
    
    private void dfs(char[][] board, int i, int j, TrieNode node, List<String> result) {
        if (i < 0 || i >= board.length || j < 0 || j >= board[0].length) {
            return;
        }
        
        char c = board[i][j];
        if (c == '#' || !node.children.containsKey(c)) {
            return;
        }
        
        node = node.children.get(c);
        
        if (node.word != null) {
            result.add(node.word);
            node.word = null;  // Avoid duplicates
        }
        
        board[i][j] = '#';  // Mark visited
        
        dfs(board, i + 1, j, node, result);
        dfs(board, i - 1, j, node, result);
        dfs(board, i, j + 1, node, result);
        dfs(board, i, j - 1, node, result);
        
        board[i][j] = c;  // Restore
    }
}
```

---

## Real-World Data Engineering Applications

### 1. Log Parsing with KMP

```java
/**
 * Find patterns in log files efficiently
 */
class LogParser {
    
    /**
     * Find all occurrences of error pattern in logs
     */
    public List<LogMatch> findErrorPatterns(List<String> logs, String pattern) {
        List<LogMatch> matches = new ArrayList<>();
        
        int[] lps = computeLPS(pattern);
        
        for (int lineNum = 0; lineNum < logs.size(); lineNum++) {
            String line = logs.get(lineNum);
            
            int i = 0;
            int j = 0;
            
            while (i < line.length()) {
                if (line.charAt(i) == pattern.charAt(j)) {
                    i++;
                    j++;
                    
                    if (j == pattern.length()) {
                        matches.add(new LogMatch(lineNum, i - j, line));
                        j = lps[j - 1];
                    }
                } else {
                    if (j != 0) {
                        j = lps[j - 1];
                    } else {
                        i++;
                    }
                }
            }
        }
        
        return matches;
    }
    
    private int[] computeLPS(String pattern) {
        int m = pattern.length();
        int[] lps = new int[m];
        int len = 0;
        int i = 1;
        
        while (i < m) {
            if (pattern.charAt(i) == pattern.charAt(len)) {
                lps[i++] = ++len;
            } else {
                if (len != 0) {
                    len = lps[len - 1];
                } else {
                    lps[i++] = 0;
                }
            }
        }
        
        return lps;
    }
    
    static class LogMatch {
        int lineNumber;
        int position;
        String line;
        
        LogMatch(int lineNumber, int position, String line) {
            this.lineNumber = lineNumber;
            this.position = position;
            this.line = line;
        }
    }
}
```

### 2. DNA Sequence Matching

```java
/**
 * Find DNA patterns in genome sequences
 */
class DNAMatcher {
    
    /**
     * Find all occurrences of DNA pattern
     */
    public List<Integer> findDNAPattern(String genome, String pattern) {
        // Use Rabin-Karp for fast matching
        return rabinKarp(genome, pattern);
    }
    
    private List<Integer> rabinKarp(String text, String pattern) {
        List<Integer> result = new ArrayList<>();
        
        int n = text.length();
        int m = pattern.length();
        
        if (m > n) return result;
        
        // DNA has 4 bases: A, C, G, T
        int BASE = 4;
        int PRIME = 101;
        
        // Map bases to numbers
        Map<Character, Integer> baseMap = new HashMap<>();
        baseMap.put('A', 0);
        baseMap.put('C', 1);
        baseMap.put('G', 2);
        baseMap.put('T', 3);
        
        long patternHash = 0;
        long textHash = 0;
        long h = 1;
        
        for (int i = 0; i < m - 1; i++) {
            h = (h * BASE) % PRIME;
        }
        
        for (int i = 0; i < m; i++) {
            patternHash = (BASE * patternHash + baseMap.get(pattern.charAt(i))) % PRIME;
            textHash = (BASE * textHash + baseMap.get(text.charAt(i))) % PRIME;
        }
        
        for (int i = 0; i <= n - m; i++) {
            if (patternHash == textHash) {
                boolean match = true;
                for (int j = 0; j < m; j++) {
                    if (text.charAt(i + j) != pattern.charAt(j)) {
                        match = false;
                        break;
                    }
                }
                
                if (match) {
                    result.add(i);
                }
            }
            
            if (i < n - m) {
                textHash = (BASE * (textHash - baseMap.get(text.charAt(i)) * h) +
                           baseMap.get(text.charAt(i + m))) % PRIME;
                
                if (textHash < 0) {
                    textHash += PRIME;
                }
            }
        }
        
        return result;
    }
}
```

### 3. Plagiarism Detection

```java
/**
 * Detect similar text using rolling hash
 */
class PlagiarismDetector {
    
    /**
     * Find common substrings of given length
     */
    public List<String> findCommonSubstrings(String text1, String text2, int k) {
        Set<Long> hashes1 = computeHashes(text1, k);
        Set<Long> hashes2 = computeHashes(text2, k);
        
        // Find intersection
        hashes1.retainAll(hashes2);
        
        // Convert back to strings (would need to store hash -> string mapping)
        List<String> result = new ArrayList<>();
        
        // For simplicity, re-scan text1
        for (int i = 0; i <= text1.length() - k; i++) {
            String substring = text1.substring(i, i + k);
            long hash = computeHash(substring);
            
            if (hashes1.contains(hash) && !result.contains(substring)) {
                result.add(substring);
            }
        }
        
        return result;
    }
    
    private Set<Long> computeHashes(String text, int k) {
        Set<Long> hashes = new HashSet<>();
        
        if (text.length() < k) return hashes;
        
        int BASE = 256;
        long MOD = 1_000_000_007;
        
        long hash = 0;
        long h = 1;
        
        for (int i = 0; i < k - 1; i++) {
            h = (h * BASE) % MOD;
        }
        
        for (int i = 0; i < k; i++) {
            hash = (BASE * hash + text.charAt(i)) % MOD;
        }
        hashes.add(hash);
        
        for (int i = k; i < text.length(); i++) {
            hash = (BASE * (hash - text.charAt(i - k) * h) + text.charAt(i)) % MOD;
            if (hash < 0) hash += MOD;
            hashes.add(hash);
        }
        
        return hashes;
    }
    
    private long computeHash(String s) {
        int BASE = 256;
        long MOD = 1_000_000_007;
        long hash = 0;
        
        for (char c : s.toCharArray()) {
            hash = (BASE * hash + c) % MOD;
        }
        
        return hash;
    }
}
```

---

## 🎯 Interview Tips

### Algorithm Selection

**Use KMP when:**
- Need to find all occurrences
- Pattern is reused multiple times
- Need deterministic O(n+m) time

**Use Rabin-Karp when:**
- Multiple patterns to search
- Need average-case performance
- Can tolerate occasional hash collisions

**Use Z-Algorithm when:**
- Need prefix matching information
- Pattern matching with preprocessing

**Use Manacher when:**
- Finding longest palindrome
- Need O(n) solution

### Common Mistakes

1. **KMP: Not handling overlapping patterns**
   ```java
   // After match, continue from lps[j-1], not from 0
   j = lps[j - 1];
   ```

2. **Rabin-Karp: Forgetting modulo**
   ```java
   // Always take modulo to avoid overflow
   hash = (hash * BASE + c) % PRIME;
   ```

3. **Manacher: Wrong transformation**
   ```java
   // Must add sentinels to avoid boundary checks
   String transformed = "^#a#b#c#$";
   ```

---

## 📊 Complexity Summary

| Algorithm | Time | Space | Best For |
|-----------|------|-------|----------|
| KMP | O(n + m) | O(m) | Exact pattern match |
| Rabin-Karp | O(n + m) avg | O(1) | Multiple patterns |
| Z-Algorithm | O(n + m) | O(n + m) | Prefix matching |
| Manacher | O(n) | O(n) | Longest palindrome |

---

**Next:** [Bit Manipulation](./13-Bit-Manipulation.md)
