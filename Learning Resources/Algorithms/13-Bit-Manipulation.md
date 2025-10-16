# Bit Manipulation

**Difficulty:** Medium  
**Learning Time:** 3-4 days  
**Interview Frequency:** ⭐⭐⭐⭐ (High)  
**Common In:** Low-level optimization, cryptography, competitive programming

---

## 📚 Table of Contents

1. [Bit Manipulation Fundamentals](#bit-manipulation-fundamentals)
2. [Common Bit Operations](#common-bit-operations)
3. [XOR Tricks](#xor-tricks)
4. [Counting Bits](#counting-bits)
5. [Bitmask Techniques](#bitmask-techniques)
6. [Real-World Applications](#real-world-applications)

---

## Bit Manipulation Fundamentals

### Basic Operations

```java
/**
 * Fundamental bit operations
 */
class BitOperations {
    
    // Get bit at position i (0-indexed from right)
    boolean getBit(int num, int i) {
        return ((num >> i) & 1) == 1;
    }
    
    // Set bit at position i to 1
    int setBit(int num, int i) {
        return num | (1 << i);
    }
    
    // Clear bit at position i (set to 0)
    int clearBit(int num, int i) {
        return num & ~(1 << i);
    }
    
    // Toggle bit at position i
    int toggleBit(int num, int i) {
        return num ^ (1 << i);
    }
    
    // Update bit at position i to value (0 or 1)
    int updateBit(int num, int i, boolean value) {
        int mask = ~(1 << i);
        return (num & mask) | ((value ? 1 : 0) << i);
    }
    
    // Check if num is power of 2
    boolean isPowerOfTwo(int num) {
        return num > 0 && (num & (num - 1)) == 0;
    }
    
    // Count trailing zeros
    int countTrailingZeros(int num) {
        return Integer.numberOfTrailingZeros(num);
    }
    
    // Isolate rightmost 1-bit
    int isolateRightmost1(int num) {
        return num & (-num);
    }
    
    // Clear rightmost 1-bit
    int clearRightmost1(int num) {
        return num & (num - 1);
    }
}
```

### Bit Manipulation Properties

```
AND (&):
  1 & 1 = 1
  1 & 0 = 0
  0 & 0 = 0
  
OR (|):
  1 | 1 = 1
  1 | 0 = 1
  0 | 0 = 0
  
XOR (^):
  1 ^ 1 = 0  (same = 0)
  1 ^ 0 = 1  (different = 1)
  0 ^ 0 = 0
  
NOT (~):
  ~1 = 0
  ~0 = 1
```

---

## Common Bit Operations

### 1. Swap Without Temp Variable

```java
/**
 * Swap two numbers without temporary variable
 */
class Swap {
    
    // Using XOR
    void swapXOR(int[] arr, int i, int j) {
        if (i != j) {  // Important: don't swap same element
            arr[i] = arr[i] ^ arr[j];
            arr[j] = arr[i] ^ arr[j];
            arr[i] = arr[i] ^ arr[j];
        }
    }
    
    // Using arithmetic (may overflow)
    void swapArithmetic(int[] arr, int i, int j) {
        if (i != j) {
            arr[i] = arr[i] + arr[j];
            arr[j] = arr[i] - arr[j];
            arr[i] = arr[i] - arr[j];
        }
    }
}
```

---

### 2. Power of Two

**LeetCode 231**

```java
/**
 * Check if number is power of 2
 * Time: O(1), Space: O(1)
 */
class Solution {
    public boolean isPowerOfTwo(int n) {
        // Power of 2 has only one bit set
        // n & (n-1) clears rightmost 1-bit
        return n > 0 && (n & (n - 1)) == 0;
    }
    
    // Alternative: Count set bits
    public boolean isPowerOfTwoCount(int n) {
        return n > 0 && Integer.bitCount(n) == 1;
    }
}
```

---

### 3. Reverse Bits

**LeetCode 190**

```java
/**
 * Reverse bits of unsigned 32-bit integer
 * Time: O(1), Space: O(1)
 */
class Solution {
    public int reverseBits(int n) {
        int result = 0;
        
        for (int i = 0; i < 32; i++) {
            result <<= 1;           // Shift result left
            result |= (n & 1);      // Add rightmost bit of n
            n >>= 1;                // Shift n right
        }
        
        return result;
    }
}
```

---

## XOR Tricks

### XOR Properties

```
a ^ 0 = a
a ^ a = 0
a ^ b ^ a = b  (XOR is commutative and associative)
```

### 1. Single Number

**LeetCode 136**

```java
/**
 * Find element that appears once (all others appear twice)
 * Time: O(n), Space: O(1)
 */
class Solution {
    public int singleNumber(int[] nums) {
        int result = 0;
        for (int num : nums) {
            result ^= num;  // Pairs cancel out to 0
        }
        return result;
    }
}
```

---

### 2. Single Number II

**LeetCode 137**

```java
/**
 * Find element that appears once (all others appear 3 times)
 * Time: O(n), Space: O(1)
 */
class Solution {
    public int singleNumber(int[] nums) {
        int ones = 0;
        int twos = 0;
        
        for (int num : nums) {
            twos |= ones & num;      // Add to twos if already in ones
            ones ^= num;             // Toggle in ones
            int threes = ones & twos; // Numbers appearing 3 times
            ones &= ~threes;         // Remove from ones
            twos &= ~threes;         // Remove from twos
        }
        
        return ones;
    }
    
    // Alternative: Count bits at each position
    public int singleNumberBitCount(int[] nums) {
        int result = 0;
        
        for (int i = 0; i < 32; i++) {
            int count = 0;
            int mask = 1 << i;
            
            for (int num : nums) {
                if ((num & mask) != 0) {
                    count++;
                }
            }
            
            if (count % 3 != 0) {
                result |= mask;
            }
        }
        
        return result;
    }
}
```

---

### 3. Single Number III

**LeetCode 260**

```java
/**
 * Find two elements that appear once (others appear twice)
 * Time: O(n), Space: O(1)
 */
class Solution {
    public int[] singleNumber(int[] nums) {
        // XOR all numbers - result is a ^ b (two unique numbers)
        int xor = 0;
        for (int num : nums) {
            xor ^= num;
        }
        
        // Find rightmost set bit (where a and b differ)
        int rightmostBit = xor & (-xor);
        
        // Divide numbers into two groups based on this bit
        int a = 0;
        int b = 0;
        
        for (int num : nums) {
            if ((num & rightmostBit) == 0) {
                a ^= num;  // Group 1
            } else {
                b ^= num;  // Group 2
            }
        }
        
        return new int[]{a, b};
    }
}
```

---

### 4. Missing Number

**LeetCode 268**

```java
/**
 * Find missing number in array [0, n]
 * Time: O(n), Space: O(1)
 */
class Solution {
    public int missingNumber(int[] nums) {
        int n = nums.length;
        int result = n;
        
        for (int i = 0; i < n; i++) {
            result ^= i ^ nums[i];
        }
        
        return result;
    }
    
    // Alternative: Sum formula
    public int missingNumberSum(int[] nums) {
        int n = nums.length;
        int expectedSum = n * (n + 1) / 2;
        int actualSum = 0;
        
        for (int num : nums) {
            actualSum += num;
        }
        
        return expectedSum - actualSum;
    }
}
```

---

## Counting Bits

### 1. Number of 1 Bits

**LeetCode 191**

```java
/**
 * Count number of 1 bits in integer
 * Time: O(1), Space: O(1)
 */
class Solution {
    public int hammingWeight(int n) {
        int count = 0;
        
        while (n != 0) {
            n &= (n - 1);  // Clear rightmost 1-bit
            count++;
        }
        
        return count;
    }
    
    // Using built-in
    public int hammingWeightBuiltIn(int n) {
        return Integer.bitCount(n);
    }
    
    // Brian Kernighan's Algorithm
    public int hammingWeightBrian(int n) {
        int count = 0;
        
        while (n != 0) {
            count++;
            n &= (n - 1);  // Clears rightmost set bit
        }
        
        return count;
    }
}
```

---

### 2. Counting Bits (0 to n)

**LeetCode 338**

```java
/**
 * Count bits for all numbers from 0 to n
 * Time: O(n), Space: O(n)
 */
class Solution {
    public int[] countBits(int n) {
        int[] result = new int[n + 1];
        
        for (int i = 1; i <= n; i++) {
            // i >> 1 is i / 2
            // i & 1 is i % 2
            result[i] = result[i >> 1] + (i & 1);
        }
        
        return result;
    }
    
    // Alternative: Using n & (n-1)
    public int[] countBitsAlternative(int n) {
        int[] result = new int[n + 1];
        
        for (int i = 1; i <= n; i++) {
            result[i] = result[i & (i - 1)] + 1;
        }
        
        return result;
    }
}
```

---

### 3. Hamming Distance

**LeetCode 461**

```java
/**
 * Hamming distance: number of positions with different bits
 * Time: O(1), Space: O(1)
 */
class Solution {
    public int hammingDistance(int x, int y) {
        int xor = x ^ y;  // 1 where bits differ
        return Integer.bitCount(xor);
    }
    
    // Manual counting
    public int hammingDistanceManual(int x, int y) {
        int xor = x ^ y;
        int count = 0;
        
        while (xor != 0) {
            count++;
            xor &= (xor - 1);
        }
        
        return count;
    }
}
```

---

## Bitmask Techniques

### 1. Subsets Generation

**LeetCode 78**

```java
/**
 * Generate all subsets using bitmask
 * Time: O(n * 2^n), Space: O(2^n)
 */
class Solution {
    public List<List<Integer>> subsets(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        int n = nums.length;
        
        // 2^n possible subsets
        for (int mask = 0; mask < (1 << n); mask++) {
            List<Integer> subset = new ArrayList<>();
            
            for (int i = 0; i < n; i++) {
                // Check if i-th bit is set
                if ((mask & (1 << i)) != 0) {
                    subset.add(nums[i]);
                }
            }
            
            result.add(subset);
        }
        
        return result;
    }
}
```

---

### 2. Maximum XOR of Two Numbers

**LeetCode 421**

```java
/**
 * Find maximum XOR of two numbers in array
 * Time: O(n), Space: O(1)
 */
class Solution {
    public int findMaximumXOR(int[] nums) {
        int max = 0;
        int mask = 0;
        
        // Build result bit by bit from left to right
        for (int i = 31; i >= 0; i--) {
            mask |= (1 << i);
            
            Set<Integer> prefixes = new HashSet<>();
            for (int num : nums) {
                prefixes.add(num & mask);
            }
            
            int candidate = max | (1 << i);
            
            // Check if candidate is achievable
            for (int prefix : prefixes) {
                if (prefixes.contains(candidate ^ prefix)) {
                    max = candidate;
                    break;
                }
            }
        }
        
        return max;
    }
}
```

---

### 3. UTF-8 Validation

**LeetCode 393**

```java
/**
 * Validate UTF-8 encoding
 * Time: O(n), Space: O(1)
 */
class Solution {
    public boolean validUtf8(int[] data) {
        int remainingBytes = 0;
        
        for (int num : data) {
            if (remainingBytes == 0) {
                // Determine number of bytes in character
                if ((num >> 5) == 0b110) {
                    remainingBytes = 1;
                } else if ((num >> 4) == 0b1110) {
                    remainingBytes = 2;
                } else if ((num >> 3) == 0b11110) {
                    remainingBytes = 3;
                } else if ((num >> 7) != 0) {
                    return false;  // Invalid start
                }
            } else {
                // Must be continuation byte (10xxxxxx)
                if ((num >> 6) != 0b10) {
                    return false;
                }
                remainingBytes--;
            }
        }
        
        return remainingBytes == 0;
    }
}
```

---

## Real-World Data Engineering Applications

### 1. Bloom Filter

```java
/**
 * Space-efficient probabilistic data structure
 */
class BloomFilter {
    private long[] bits;
    private int size;
    private int numHashes;
    
    public BloomFilter(int size, int numHashes) {
        this.size = size;
        this.numHashes = numHashes;
        this.bits = new long[(size + 63) / 64];  // 64 bits per long
    }
    
    /**
     * Add element to bloom filter
     */
    public void add(String element) {
        for (int i = 0; i < numHashes; i++) {
            int hash = hash(element, i);
            int index = Math.abs(hash % size);
            
            // Set bit
            bits[index / 64] |= (1L << (index % 64));
        }
    }
    
    /**
     * Check if element might be in set
     */
    public boolean mightContain(String element) {
        for (int i = 0; i < numHashes; i++) {
            int hash = hash(element, i);
            int index = Math.abs(hash % size);
            
            // Check if bit is set
            if ((bits[index / 64] & (1L << (index % 64))) == 0) {
                return false;  // Definitely not in set
            }
        }
        
        return true;  // Might be in set
    }
    
    private int hash(String element, int seed) {
        return (element.hashCode() * (seed + 1)) ^ (seed * 31);
    }
}
```

---

### 2. IP Address Manipulation

```java
/**
 * IP address operations using bit manipulation
 */
class IPAddressUtils {
    
    /**
     * Convert IP string to integer
     */
    public long ipToLong(String ip) {
        String[] parts = ip.split("\\.");
        long result = 0;
        
        for (int i = 0; i < 4; i++) {
            result |= (Long.parseLong(parts[i]) << (24 - 8 * i));
        }
        
        return result;
    }
    
    /**
     * Convert integer to IP string
     */
    public String longToIP(long ip) {
        return String.format("%d.%d.%d.%d",
            (ip >> 24) & 0xFF,
            (ip >> 16) & 0xFF,
            (ip >> 8) & 0xFF,
            ip & 0xFF
        );
    }
    
    /**
     * Check if IP is in subnet
     */
    public boolean isInSubnet(String ip, String subnet, int mask) {
        long ipLong = ipToLong(ip);
        long subnetLong = ipToLong(subnet);
        long maskLong = (-1L << (32 - mask)) & 0xFFFFFFFFL;
        
        return (ipLong & maskLong) == (subnetLong & maskLong);
    }
}
```

---

### 3. Bitset for Feature Flags

```java
/**
 * Efficient storage for feature flags
 */
class FeatureFlags {
    private long flags;
    
    // Feature constants
    public static final int FEATURE_A = 0;
    public static final int FEATURE_B = 1;
    public static final int FEATURE_C = 2;
    // ... up to 64 features
    
    public void enableFeature(int feature) {
        flags |= (1L << feature);
    }
    
    public void disableFeature(int feature) {
        flags &= ~(1L << feature);
    }
    
    public boolean isEnabled(int feature) {
        return (flags & (1L << feature)) != 0;
    }
    
    public void toggleFeature(int feature) {
        flags ^= (1L << feature);
    }
    
    /**
     * Check if any of the features are enabled
     */
    public boolean anyEnabled(int... features) {
        for (int feature : features) {
            if (isEnabled(feature)) {
                return true;
            }
        }
        return false;
    }
    
    /**
     * Check if all features are enabled
     */
    public boolean allEnabled(int... features) {
        for (int feature : features) {
            if (!isEnabled(feature)) {
                return false;
            }
        }
        return true;
    }
}
```

---

### 4. Compression/Decompression

```java
/**
 * Simple bit-level compression
 */
class BitCompressor {
    
    /**
     * Compress array of small integers
     */
    public byte[] compress(int[] data, int bitsPerValue) {
        int totalBits = data.length * bitsPerValue;
        byte[] compressed = new byte[(totalBits + 7) / 8];
        
        int bitPos = 0;
        
        for (int value : data) {
            for (int i = bitsPerValue - 1; i >= 0; i--) {
                if ((value & (1 << i)) != 0) {
                    int byteIndex = bitPos / 8;
                    int bitIndex = bitPos % 8;
                    compressed[byteIndex] |= (1 << (7 - bitIndex));
                }
                bitPos++;
            }
        }
        
        return compressed;
    }
    
    /**
     * Decompress to original array
     */
    public int[] decompress(byte[] compressed, int count, int bitsPerValue) {
        int[] data = new int[count];
        int bitPos = 0;
        
        for (int i = 0; i < count; i++) {
            int value = 0;
            
            for (int j = 0; j < bitsPerValue; j++) {
                int byteIndex = bitPos / 8;
                int bitIndex = bitPos % 8;
                
                if ((compressed[byteIndex] & (1 << (7 - bitIndex))) != 0) {
                    value |= (1 << (bitsPerValue - 1 - j));
                }
                
                bitPos++;
            }
            
            data[i] = value;
        }
        
        return data;
    }
}
```

---

## 🎯 Interview Tips

### Common Patterns

1. **XOR for finding unique elements**
2. **Bitmask for subset generation**
3. **n & (n-1) for power of 2 checks**
4. **Counting bits using DP**

### Useful Tricks

```java
// Get rightmost 1-bit
int rightmost = n & (-n);

// Clear rightmost 1-bit
int cleared = n & (n - 1);

// Check if i-th bit is set
boolean isSet = (n & (1 << i)) != 0;

// Set i-th bit
n |= (1 << i);

// Clear i-th bit
n &= ~(1 << i);

// Toggle i-th bit
n ^= (1 << i);
```

### Common Mistakes

1. **Integer overflow**
   ```java
   // Use long for large shifts
   long mask = 1L << 32;  // Not: 1 << 32
   ```

2. **Sign extension**
   ```java
   // Use >>> for unsigned right shift
   int unsigned = n >>> 1;
   ```

3. **XOR same element**
   ```java
   // Don't swap same position
   if (i != j) {
       arr[i] ^= arr[j];
       arr[j] ^= arr[i];
       arr[i] ^= arr[j];
   }
   ```

---

## 📊 Complexity Summary

| Operation | Time | Space | Use Case |
|-----------|------|-------|----------|
| Get/Set/Clear bit | O(1) | O(1) | Bit manipulation |
| Count bits | O(1) | O(1) | Hamming weight |
| XOR all | O(n) | O(1) | Find unique |
| Generate subsets | O(n * 2^n) | O(2^n) | All combinations |

---

**Next:** Review all algorithm categories and practice problems!
