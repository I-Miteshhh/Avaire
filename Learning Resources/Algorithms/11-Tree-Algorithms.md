# Tree Algorithms

**Difficulty:** Medium-Hard  
**Learning Time:** 5-7 days  
**Interview Frequency:** ⭐⭐⭐⭐⭐ (Very High)  
**Common In:** All FAANG companies

---

## 📚 Table of Contents

1. [Tree Traversals](#tree-traversals)
2. [Binary Search Tree Operations](#binary-search-tree-operations)
3. [Tree Properties](#tree-properties)
4. [Lowest Common Ancestor](#lowest-common-ancestor)
5. [Serialization/Deserialization](#serializationdeserialization)
6. [Advanced Tree Algorithms](#advanced-tree-algorithms)
7. [Real-World Applications](#real-world-applications)

---

## Tree Traversals

### Binary Tree Definition

```java
class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;
    
    TreeNode(int val) {
        this.val = val;
    }
    
    TreeNode(int val, TreeNode left, TreeNode right) {
        this.val = val;
        this.left = left;
        this.right = right;
    }
}
```

---

### 1. Inorder Traversal (Left-Root-Right)

```java
/**
 * Inorder: Left → Root → Right
 * For BST: gives sorted order
 */
class InorderTraversal {
    
    // Recursive - Time: O(n), Space: O(h) where h = height
    public List<Integer> inorderRecursive(TreeNode root) {
        List<Integer> result = new ArrayList<>();
        inorderHelper(root, result);
        return result;
    }
    
    private void inorderHelper(TreeNode node, List<Integer> result) {
        if (node == null) return;
        
        inorderHelper(node.left, result);
        result.add(node.val);
        inorderHelper(node.right, result);
    }
    
    // Iterative with stack - Time: O(n), Space: O(h)
    public List<Integer> inorderIterative(TreeNode root) {
        List<Integer> result = new ArrayList<>();
        Stack<TreeNode> stack = new Stack<>();
        TreeNode current = root;
        
        while (current != null || !stack.isEmpty()) {
            // Go to leftmost node
            while (current != null) {
                stack.push(current);
                current = current.left;
            }
            
            // Process node
            current = stack.pop();
            result.add(current.val);
            
            // Move to right subtree
            current = current.right;
        }
        
        return result;
    }
    
    // Morris Traversal - Time: O(n), Space: O(1) !!!
    public List<Integer> inorderMorris(TreeNode root) {
        List<Integer> result = new ArrayList<>();
        TreeNode current = root;
        
        while (current != null) {
            if (current.left == null) {
                // No left child - process current
                result.add(current.val);
                current = current.right;
            } else {
                // Find inorder predecessor
                TreeNode predecessor = current.left;
                while (predecessor.right != null && predecessor.right != current) {
                    predecessor = predecessor.right;
                }
                
                if (predecessor.right == null) {
                    // Create thread
                    predecessor.right = current;
                    current = current.left;
                } else {
                    // Remove thread
                    predecessor.right = null;
                    result.add(current.val);
                    current = current.right;
                }
            }
        }
        
        return result;
    }
}
```

---

### 2. Preorder Traversal (Root-Left-Right)

```java
/**
 * Preorder: Root → Left → Right
 * Used for: copying tree, prefix expression
 */
class PreorderTraversal {
    
    // Recursive
    public List<Integer> preorderRecursive(TreeNode root) {
        List<Integer> result = new ArrayList<>();
        preorderHelper(root, result);
        return result;
    }
    
    private void preorderHelper(TreeNode node, List<Integer> result) {
        if (node == null) return;
        
        result.add(node.val);
        preorderHelper(node.left, result);
        preorderHelper(node.right, result);
    }
    
    // Iterative
    public List<Integer> preorderIterative(TreeNode root) {
        List<Integer> result = new ArrayList<>();
        if (root == null) return result;
        
        Stack<TreeNode> stack = new Stack<>();
        stack.push(root);
        
        while (!stack.isEmpty()) {
            TreeNode node = stack.pop();
            result.add(node.val);
            
            // Push right first (so left is processed first)
            if (node.right != null) {
                stack.push(node.right);
            }
            if (node.left != null) {
                stack.push(node.left);
            }
        }
        
        return result;
    }
}
```

---

### 3. Postorder Traversal (Left-Right-Root)

```java
/**
 * Postorder: Left → Right → Root
 * Used for: deleting tree, postfix expression
 */
class PostorderTraversal {
    
    // Recursive
    public List<Integer> postorderRecursive(TreeNode root) {
        List<Integer> result = new ArrayList<>();
        postorderHelper(root, result);
        return result;
    }
    
    private void postorderHelper(TreeNode node, List<Integer> result) {
        if (node == null) return;
        
        postorderHelper(node.left, result);
        postorderHelper(node.right, result);
        result.add(node.val);
    }
    
    // Iterative - using two stacks
    public List<Integer> postorderIterativeTwoStacks(TreeNode root) {
        List<Integer> result = new ArrayList<>();
        if (root == null) return result;
        
        Stack<TreeNode> stack1 = new Stack<>();
        Stack<TreeNode> stack2 = new Stack<>();
        
        stack1.push(root);
        
        while (!stack1.isEmpty()) {
            TreeNode node = stack1.pop();
            stack2.push(node);
            
            if (node.left != null) {
                stack1.push(node.left);
            }
            if (node.right != null) {
                stack1.push(node.right);
            }
        }
        
        while (!stack2.isEmpty()) {
            result.add(stack2.pop().val);
        }
        
        return result;
    }
    
    // Iterative - using one stack
    public List<Integer> postorderIterativeOneStack(TreeNode root) {
        List<Integer> result = new ArrayList<>();
        if (root == null) return result;
        
        Stack<TreeNode> stack = new Stack<>();
        TreeNode current = root;
        TreeNode lastVisited = null;
        
        while (current != null || !stack.isEmpty()) {
            while (current != null) {
                stack.push(current);
                current = current.left;
            }
            
            TreeNode peekNode = stack.peek();
            
            if (peekNode.right != null && lastVisited != peekNode.right) {
                current = peekNode.right;
            } else {
                result.add(peekNode.val);
                lastVisited = stack.pop();
            }
        }
        
        return result;
    }
}
```

---

### 4. Level-Order Traversal (BFS)

```java
/**
 * Level-order: Level by level, left to right
 * Time: O(n), Space: O(w) where w = max width
 */
class LevelOrderTraversal {
    
    // Standard BFS
    public List<List<Integer>> levelOrder(TreeNode root) {
        List<List<Integer>> result = new ArrayList<>();
        if (root == null) return result;
        
        Queue<TreeNode> queue = new LinkedList<>();
        queue.offer(root);
        
        while (!queue.isEmpty()) {
            int levelSize = queue.size();
            List<Integer> currentLevel = new ArrayList<>();
            
            for (int i = 0; i < levelSize; i++) {
                TreeNode node = queue.poll();
                currentLevel.add(node.val);
                
                if (node.left != null) {
                    queue.offer(node.left);
                }
                if (node.right != null) {
                    queue.offer(node.right);
                }
            }
            
            result.add(currentLevel);
        }
        
        return result;
    }
    
    // Zigzag level order
    public List<List<Integer>> zigzagLevelOrder(TreeNode root) {
        List<List<Integer>> result = new ArrayList<>();
        if (root == null) return result;
        
        Queue<TreeNode> queue = new LinkedList<>();
        queue.offer(root);
        boolean leftToRight = true;
        
        while (!queue.isEmpty()) {
            int levelSize = queue.size();
            List<Integer> currentLevel = new ArrayList<>();
            
            for (int i = 0; i < levelSize; i++) {
                TreeNode node = queue.poll();
                
                if (leftToRight) {
                    currentLevel.add(node.val);
                } else {
                    currentLevel.add(0, node.val);  // Add at beginning
                }
                
                if (node.left != null) queue.offer(node.left);
                if (node.right != null) queue.offer(node.right);
            }
            
            result.add(currentLevel);
            leftToRight = !leftToRight;
        }
        
        return result;
    }
}
```

---

## Binary Search Tree Operations

### 1. Search in BST

```java
/**
 * Search for value in BST
 * Time: O(h), Space: O(h) recursive or O(1) iterative
 */
class BSTSearch {
    
    // Recursive
    public TreeNode searchBST(TreeNode root, int val) {
        if (root == null || root.val == val) {
            return root;
        }
        
        if (val < root.val) {
            return searchBST(root.left, val);
        } else {
            return searchBST(root.right, val);
        }
    }
    
    // Iterative
    public TreeNode searchBSTIterative(TreeNode root, int val) {
        while (root != null && root.val != val) {
            root = val < root.val ? root.left : root.right;
        }
        return root;
    }
}
```

---

### 2. Insert into BST

```java
/**
 * Insert value into BST
 * Time: O(h), Space: O(h) recursive or O(1) iterative
 */
class BSTInsert {
    
    // Recursive
    public TreeNode insertIntoBST(TreeNode root, int val) {
        if (root == null) {
            return new TreeNode(val);
        }
        
        if (val < root.val) {
            root.left = insertIntoBST(root.left, val);
        } else {
            root.right = insertIntoBST(root.right, val);
        }
        
        return root;
    }
    
    // Iterative
    public TreeNode insertIntoBSTIterative(TreeNode root, int val) {
        if (root == null) {
            return new TreeNode(val);
        }
        
        TreeNode current = root;
        
        while (true) {
            if (val < current.val) {
                if (current.left == null) {
                    current.left = new TreeNode(val);
                    break;
                }
                current = current.left;
            } else {
                if (current.right == null) {
                    current.right = new TreeNode(val);
                    break;
                }
                current = current.right;
            }
        }
        
        return root;
    }
}
```

---

### 3. Delete from BST

```java
/**
 * Delete node from BST
 * Time: O(h), Space: O(h)
 */
class BSTDelete {
    
    public TreeNode deleteNode(TreeNode root, int key) {
        if (root == null) {
            return null;
        }
        
        if (key < root.val) {
            root.left = deleteNode(root.left, key);
        } else if (key > root.val) {
            root.right = deleteNode(root.right, key);
        } else {
            // Node to delete found
            
            // Case 1: No children
            if (root.left == null && root.right == null) {
                return null;
            }
            
            // Case 2: One child
            if (root.left == null) {
                return root.right;
            }
            if (root.right == null) {
                return root.left;
            }
            
            // Case 3: Two children
            // Find inorder successor (smallest in right subtree)
            TreeNode successor = findMin(root.right);
            root.val = successor.val;
            root.right = deleteNode(root.right, successor.val);
        }
        
        return root;
    }
    
    private TreeNode findMin(TreeNode node) {
        while (node.left != null) {
            node = node.left;
        }
        return node;
    }
}
```

---

### 4. Validate BST

**LeetCode 98**

```java
/**
 * Validate if tree is valid BST
 * Time: O(n), Space: O(h)
 */
class ValidateBST {
    
    public boolean isValidBST(TreeNode root) {
        return validate(root, null, null);
    }
    
    private boolean validate(TreeNode node, Integer min, Integer max) {
        if (node == null) {
            return true;
        }
        
        if ((min != null && node.val <= min) || 
            (max != null && node.val >= max)) {
            return false;
        }
        
        return validate(node.left, min, node.val) &&
               validate(node.right, node.val, max);
    }
    
    // Alternative: Inorder should be sorted
    public boolean isValidBSTInorder(TreeNode root) {
        List<Integer> inorder = new ArrayList<>();
        inorderTraversal(root, inorder);
        
        for (int i = 1; i < inorder.size(); i++) {
            if (inorder.get(i) <= inorder.get(i - 1)) {
                return false;
            }
        }
        
        return true;
    }
    
    private void inorderTraversal(TreeNode node, List<Integer> result) {
        if (node == null) return;
        inorderTraversal(node.left, result);
        result.add(node.val);
        inorderTraversal(node.right, result);
    }
}
```

---

## Tree Properties

### 1. Maximum Depth

```java
/**
 * Find maximum depth (height) of tree
 * Time: O(n), Space: O(h)
 */
class MaxDepth {
    
    // DFS
    public int maxDepth(TreeNode root) {
        if (root == null) {
            return 0;
        }
        
        int leftDepth = maxDepth(root.left);
        int rightDepth = maxDepth(root.right);
        
        return Math.max(leftDepth, rightDepth) + 1;
    }
    
    // BFS
    public int maxDepthBFS(TreeNode root) {
        if (root == null) return 0;
        
        Queue<TreeNode> queue = new LinkedList<>();
        queue.offer(root);
        int depth = 0;
        
        while (!queue.isEmpty()) {
            int levelSize = queue.size();
            depth++;
            
            for (int i = 0; i < levelSize; i++) {
                TreeNode node = queue.poll();
                if (node.left != null) queue.offer(node.left);
                if (node.right != null) queue.offer(node.right);
            }
        }
        
        return depth;
    }
}
```

---

### 2. Diameter of Binary Tree

**LeetCode 543**

```java
/**
 * Longest path between any two nodes
 * Time: O(n), Space: O(h)
 */
class DiameterOfBinaryTree {
    private int diameter = 0;
    
    public int diameterOfBinaryTree(TreeNode root) {
        height(root);
        return diameter;
    }
    
    private int height(TreeNode node) {
        if (node == null) {
            return 0;
        }
        
        int leftHeight = height(node.left);
        int rightHeight = height(node.right);
        
        // Update diameter: path through this node
        diameter = Math.max(diameter, leftHeight + rightHeight);
        
        return Math.max(leftHeight, rightHeight) + 1;
    }
}
```

---

### 3. Balanced Binary Tree

**LeetCode 110**

```java
/**
 * Check if tree is height-balanced
 * Time: O(n), Space: O(h)
 */
class BalancedBinaryTree {
    
    public boolean isBalanced(TreeNode root) {
        return checkHeight(root) != -1;
    }
    
    private int checkHeight(TreeNode node) {
        if (node == null) {
            return 0;
        }
        
        int leftHeight = checkHeight(node.left);
        if (leftHeight == -1) return -1;
        
        int rightHeight = checkHeight(node.right);
        if (rightHeight == -1) return -1;
        
        if (Math.abs(leftHeight - rightHeight) > 1) {
            return -1;  // Not balanced
        }
        
        return Math.max(leftHeight, rightHeight) + 1;
    }
}
```

---

## Lowest Common Ancestor

### 1. LCA of Binary Tree

**LeetCode 236**

```java
/**
 * Find LCA of two nodes in binary tree
 * Time: O(n), Space: O(h)
 */
class LCABinaryTree {
    
    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
        if (root == null || root == p || root == q) {
            return root;
        }
        
        TreeNode left = lowestCommonAncestor(root.left, p, q);
        TreeNode right = lowestCommonAncestor(root.right, p, q);
        
        if (left != null && right != null) {
            return root;  // p and q on different sides
        }
        
        return left != null ? left : right;
    }
}
```

---

### 2. LCA of BST

**LeetCode 235**

```java
/**
 * Find LCA in BST (can use BST property)
 * Time: O(h), Space: O(h) recursive or O(1) iterative
 */
class LCABST {
    
    // Recursive
    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
        if (p.val < root.val && q.val < root.val) {
            return lowestCommonAncestor(root.left, p, q);
        } else if (p.val > root.val && q.val > root.val) {
            return lowestCommonAncestor(root.right, p, q);
        } else {
            return root;  // Split point
        }
    }
    
    // Iterative
    public TreeNode lowestCommonAncestorIterative(TreeNode root, TreeNode p, TreeNode q) {
        while (root != null) {
            if (p.val < root.val && q.val < root.val) {
                root = root.left;
            } else if (p.val > root.val && q.val > root.val) {
                root = root.right;
            } else {
                return root;
            }
        }
        return null;
    }
}
```

---

## Serialization/Deserialization

### Serialize and Deserialize Binary Tree

**LeetCode 297**

```java
/**
 * Serialize tree to string and deserialize back
 * Time: O(n) for both, Space: O(n)
 */
class Codec {
    
    // Serialize using preorder traversal
    public String serialize(TreeNode root) {
        StringBuilder sb = new StringBuilder();
        serializeHelper(root, sb);
        return sb.toString();
    }
    
    private void serializeHelper(TreeNode node, StringBuilder sb) {
        if (node == null) {
            sb.append("null,");
            return;
        }
        
        sb.append(node.val).append(",");
        serializeHelper(node.left, sb);
        serializeHelper(node.right, sb);
    }
    
    // Deserialize
    public TreeNode deserialize(String data) {
        Queue<String> nodes = new LinkedList<>(Arrays.asList(data.split(",")));
        return deserializeHelper(nodes);
    }
    
    private TreeNode deserializeHelper(Queue<String> nodes) {
        String val = nodes.poll();
        if (val.equals("null")) {
            return null;
        }
        
        TreeNode node = new TreeNode(Integer.parseInt(val));
        node.left = deserializeHelper(nodes);
        node.right = deserializeHelper(nodes);
        
        return node;
    }
}

/**
 * Alternative: Level-order serialization
 */
class CodecLevelOrder {
    
    public String serialize(TreeNode root) {
        if (root == null) return "";
        
        StringBuilder sb = new StringBuilder();
        Queue<TreeNode> queue = new LinkedList<>();
        queue.offer(root);
        
        while (!queue.isEmpty()) {
            TreeNode node = queue.poll();
            
            if (node == null) {
                sb.append("null,");
            } else {
                sb.append(node.val).append(",");
                queue.offer(node.left);
                queue.offer(node.right);
            }
        }
        
        return sb.toString();
    }
    
    public TreeNode deserialize(String data) {
        if (data.isEmpty()) return null;
        
        String[] values = data.split(",");
        TreeNode root = new TreeNode(Integer.parseInt(values[0]));
        Queue<TreeNode> queue = new LinkedList<>();
        queue.offer(root);
        
        int i = 1;
        while (!queue.isEmpty()) {
            TreeNode node = queue.poll();
            
            if (!values[i].equals("null")) {
                node.left = new TreeNode(Integer.parseInt(values[i]));
                queue.offer(node.left);
            }
            i++;
            
            if (!values[i].equals("null")) {
                node.right = new TreeNode(Integer.parseInt(values[i]));
                queue.offer(node.right);
            }
            i++;
        }
        
        return root;
    }
}
```

---

## Advanced Tree Algorithms

### 1. Construct Binary Tree from Traversals

**LeetCode 105**

```java
/**
 * Construct tree from preorder and inorder
 * Time: O(n), Space: O(n)
 */
class ConstructTree {
    private int preIndex = 0;
    private Map<Integer, Integer> inorderMap;
    
    public TreeNode buildTree(int[] preorder, int[] inorder) {
        inorderMap = new HashMap<>();
        for (int i = 0; i < inorder.length; i++) {
            inorderMap.put(inorder[i], i);
        }
        
        return buildHelper(preorder, 0, inorder.length - 1);
    }
    
    private TreeNode buildHelper(int[] preorder, int inStart, int inEnd) {
        if (inStart > inEnd) {
            return null;
        }
        
        int rootVal = preorder[preIndex++];
        TreeNode root = new TreeNode(rootVal);
        
        int inIndex = inorderMap.get(rootVal);
        
        root.left = buildHelper(preorder, inStart, inIndex - 1);
        root.right = buildHelper(preorder, inIndex + 1, inEnd);
        
        return root;
    }
}
```

---

### 2. Binary Tree Maximum Path Sum

**LeetCode 124**

```java
/**
 * Find maximum path sum (path can start/end anywhere)
 * Time: O(n), Space: O(h)
 */
class MaxPathSum {
    private int maxSum = Integer.MIN_VALUE;
    
    public int maxPathSum(TreeNode root) {
        maxGain(root);
        return maxSum;
    }
    
    private int maxGain(TreeNode node) {
        if (node == null) {
            return 0;
        }
        
        // Recursively get max gain from left and right
        int leftGain = Math.max(maxGain(node.left), 0);
        int rightGain = Math.max(maxGain(node.right), 0);
        
        // Path through current node
        int pathSum = node.val + leftGain + rightGain;
        maxSum = Math.max(maxSum, pathSum);
        
        // Return max gain continuing from this node
        return node.val + Math.max(leftGain, rightGain);
    }
}
```

---

## Real-World Data Engineering Applications

### 1. File System Tree

```java
/**
 * Model file system as tree
 */
class FileSystem {
    
    static class FileNode {
        String name;
        boolean isDirectory;
        long size;
        List<FileNode> children;
        
        FileNode(String name, boolean isDirectory) {
            this.name = name;
            this.isDirectory = isDirectory;
            this.children = new ArrayList<>();
        }
    }
    
    /**
     * Calculate total size of directory
     */
    public long calculateSize(FileNode root) {
        if (!root.isDirectory) {
            return root.size;
        }
        
        long totalSize = 0;
        for (FileNode child : root.children) {
            totalSize += calculateSize(child);
        }
        
        root.size = totalSize;
        return totalSize;
    }
    
    /**
     * Find files larger than threshold
     */
    public List<String> findLargeFiles(FileNode root, long threshold) {
        List<String> result = new ArrayList<>();
        dfs(root, "", threshold, result);
        return result;
    }
    
    private void dfs(FileNode node, String path, long threshold, List<String> result) {
        String fullPath = path.isEmpty() ? node.name : path + "/" + node.name;
        
        if (!node.isDirectory && node.size > threshold) {
            result.add(fullPath);
        }
        
        if (node.isDirectory) {
            for (FileNode child : node.children) {
                dfs(child, fullPath, threshold, result);
            }
        }
    }
}
```

### 2. Spark Catalyst Query Plan

```java
/**
 * Expression tree for query optimization
 */
class QueryPlan {
    
    static class ExprNode {
        String operator;
        Object value;
        ExprNode left;
        ExprNode right;
        
        ExprNode(String operator) {
            this.operator = operator;
        }
        
        ExprNode(Object value) {
            this.value = value;
        }
    }
    
    /**
     * Optimize expression tree (constant folding)
     */
    public ExprNode optimize(ExprNode node) {
        if (node == null) return null;
        
        node.left = optimize(node.left);
        node.right = optimize(node.right);
        
        // Constant folding: if both children are constants, evaluate
        if (node.left != null && node.right != null &&
            node.left.value != null && node.right.value != null) {
            
            if (node.operator.equals("+")) {
                int result = (Integer)node.left.value + (Integer)node.right.value;
                return new ExprNode(result);
            }
            // ... other operators
        }
        
        return node;
    }
}
```

---

## 🎯 Interview Tips

### Common Patterns

1. **DFS for most tree problems**
2. **BFS for level-order, shortest path**
3. **Postorder for bottom-up calculation**
4. **Inorder for BST sorted order**

### Space Optimization

```java
// Morris Traversal achieves O(1) space by threading
// Temporarily modify tree structure, then restore
```

### Common Mistakes

1. **Not handling null nodes**
   ```java
   // ✅ Always check null first
   if (root == null) return ...;
   ```

2. **Confusing height vs depth**
   - Height: edges from node to deepest leaf
   - Depth: edges from root to node

3. **BST validation**
   ```java
   // ❌ Wrong - only checks immediate children
   root.left.val < root.val && root.right.val > root.val
   
   // ✅ Correct - checks range
   validate(node, min, max)
   ```

---

## 📊 Complexity Summary

| Operation | BST Average | BST Worst | Balanced Tree |
|-----------|------------|-----------|---------------|
| Search | O(log n) | O(n) | O(log n) |
| Insert | O(log n) | O(n) | O(log n) |
| Delete | O(log n) | O(n) | O(log n) |
| Traversal | O(n) | O(n) | O(n) |

---

**Next:** [String Algorithms](./12-String-Algorithms.md)
