# Unordered Containers in Modern C++: std::unordered_map and std::unordered_set

## Introduction

C++11 introduced a significant addition to the Standard Template Library (STL) with the inclusion of unordered associative containers. Prior to C++11, the STL provided associative containers like `std::map` and `std::set`, which were implemented as balanced binary trees (typically red-black trees). These containers offered logarithmic time complexity for operations like insertion, deletion, and lookup. The unordered containers—`std::unordered_map`, `std::unordered_set`, `std::unordered_multimap`, and `std::unordered_multiset`—provide hash table-based alternatives that offer amortized constant-time performance for these operations.

This article focuses on the two most commonly used unordered containers: `std::unordered_map` and `std::unordered_set`. We'll explore their functionality, performance characteristics, customization options, and best practices for their effective use.

## Hash Tables: The Foundation of Unordered Containers

Before delving into the specifics of these containers, it's important to understand the underlying data structure: the hash table.

A hash table works by using a hash function to map keys to array indices (buckets). The hash function transforms the key into an integer, which is then reduced to a valid index in the underlying array using modulo arithmetic. This allows for constant-time average case performance for insertions, erasures, and lookups.

When multiple keys hash to the same bucket (a collision), the values are stored in a linked list or other data structure within that bucket. This is why operations have amortized constant time complexity rather than guaranteed constant time—in the worst case, many elements could hash to the same bucket, degrading performance.

## std::unordered_map

### Basic Usage

`std::unordered_map` is an associative container that stores key-value pairs with unique keys. Unlike `std::map`, which keeps elements sorted by key, `std::unordered_map` organizes elements based on their hash values.

Here's a simple example of using `std::unordered_map`:

```cpp
#include <iostream>
#include <unordered_map>
#include <string>

int main() {
    // Create an unordered_map with string keys and int values
    std::unordered_map<std::string, int> scores;
    
    // Insert elements
    scores["Alice"] = 95;
    scores["Bob"] = 87;
    scores["Charlie"] = 92;
    
    // Access elements
    std::cout << "Alice's score: " << scores["Alice"] << std::endl;
    
    // Check if a key exists
    if (scores.find("David") == scores.end()) {
        std::cout << "David's score not found" << std::endl;
    }
    
    // Iterate through all key-value pairs
    for (const auto& pair : scores) {
        std::cout << pair.first << ": " << pair.second << std::endl;
    }
    
    return 0;
}
```

### Key Operations and Members

`std::unordered_map` provides the following key operations:

1. **Element Access**:
   - `operator[]`: Accesses or inserts an element
   - `at()`: Accesses an element with bounds checking

2. **Iterators**:
   - `begin()`, `end()`: Returns iterators to the beginning and end
   - `cbegin()`, `cend()`: Returns const iterators

3. **Capacity**:
   - `empty()`: Checks if the container is empty
   - `size()`: Returns the number of elements
   - `max_size()`: Returns the maximum possible number of elements

4. **Modifiers**:
   - `insert()`: Inserts elements
   - `emplace()`: Constructs elements in-place
   - `erase()`: Removes elements
   - `clear()`: Removes all elements
   - `swap()`: Swaps the contents with another container

5. **Lookup**:
   - `find()`: Finds an element with a specific key
   - `count()`: Returns the number of elements with a specific key (0 or 1)
   - `equal_range()`: Returns a range of elements with a specific key

6. **Bucket Interface**:
   - `bucket_count()`: Returns the number of buckets
   - `max_bucket_count()`: Returns the maximum number of buckets
   - `bucket_size()`: Returns the number of elements in a specific bucket
   - `bucket()`: Returns the bucket index for a key
   - `load_factor()`: Returns the average number of elements per bucket
   - `max_load_factor()`: Gets or sets the maximum load factor
   - `rehash()`: Sets the number of buckets
   - `reserve()`: Reserves space for a specific number of elements

Let's see some of these operations in action:

```cpp
#include <iostream>
#include <unordered_map>
#include <string>

int main() {
    std::unordered_map<std::string, int> inventory = {
        {"apples", 10},
        {"bananas", 15},
        {"oranges", 8}
    };
    
    // Element access
    std::cout << "We have " << inventory["apples"] << " apples" << std::endl;
    
    // Using at() with exception handling
    try {
        std::cout << "We have " << inventory.at("grapes") << " grapes" << std::endl;
    } catch (const std::out_of_range& e) {
        std::cout << "No grapes in inventory: " << e.what() << std::endl;
    }
    
    // Insert using different methods
    inventory.insert({"grapes", 20});
    inventory.insert(std::make_pair("pears", 12));
    
    // Emplace constructs the element in-place
    inventory.emplace("strawberries", 30);
    
    // Updating an existing value
    inventory["apples"] = 25;
    
    // Iterating 
    for (const auto& [fruit, count] : inventory) {
        std::cout << fruit << ": " << count << std::endl;
    }
    
    // Lookup operation
    auto it = inventory.find("bananas");
    if (it != inventory.end()) {
        std::cout << "Found " << it->first << ": " << it->second << std::endl;
    }
    
    // Erase by key
    inventory.erase("oranges");
    
    // Get bucket information
    std::cout << "Number of buckets: " << inventory.bucket_count() << std::endl;
    std::cout << "Load factor: " << inventory.load_factor() << std::endl;
    std::cout << "Max load factor: " << inventory.max_load_factor() << std::endl;
    
    // Find which bucket contains "apples"
    std::cout << "Bucket for 'apples': " << inventory.bucket("apples") << std::endl;
    
    return 0;
}
```

### Performance Considerations

One key advantage of `std::unordered_map` over `std::map` is performance for lookup, insertion, and deletion operations:

- `std::map`: O(log n) time complexity
- `std::unordered_map`: O(1) average time complexity (worst case O(n))

Here's a simple benchmark comparing the two:

```cpp
#include <iostream>
#include <chrono>
#include <map>
#include <unordered_map>
#include <string>
#include <random>

// Utility function to measure execution time
template <typename Func>
long long measureTime(Func func) {
    auto start = std::chrono::high_resolution_clock::now();
    func();
    auto end = std::chrono::high_resolution_clock::now();
    return std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
}

int main() {
    const int NUM_OPERATIONS = 1000000;
    std::vector<std::string> keys;
    
    // Generate random keys
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, 1000000);
    
    for (int i = 0; i < NUM_OPERATIONS; ++i) {
        keys.push_back("key" + std::to_string(dis(gen)));
    }
    
    // Test std::map
    std::map<std::string, int> ordered_map;
    long long map_insert_time = measureTime([&]() {
        for (const auto& key : keys) {
            ordered_map[key] = 1;
        }
    });
    
    // Test std::unordered_map
    std::unordered_map<std::string, int> unordered_map;
    long long unordered_insert_time = measureTime([&]() {
        for (const auto& key : keys) {
            unordered_map[key] = 1;
        }
    });
    
    // Measure lookup times
    int dummy = 0;
    long long map_lookup_time = measureTime([&]() {
        for (const auto& key : keys) {
            dummy += ordered_map[key];
        }
    });
    
    long long unordered_lookup_time = measureTime([&]() {
        for (const auto& key : keys) {
            dummy += unordered_map[key];
        }
    });
    
    std::cout << "std::map insert time: " << map_insert_time << " microseconds\n";
    std::cout << "std::unordered_map insert time: " << unordered_insert_time << " microseconds\n";
    std::cout << "std::map lookup time: " << map_lookup_time << " microseconds\n";
    std::cout << "std::unordered_map lookup time: " << unordered_lookup_time << " microseconds\n";
    
    return 0;
}
```

## std::unordered_set

### Basic Usage

`std::unordered_set` is an unordered associative container that contains a set of unique objects. Like `std::unordered_map`, it uses a hash table for its implementation, but it stores only values (keys) without associated mapped values.

Here's a basic example:

```cpp
#include <iostream>
#include <unordered_set>
#include <string>

int main() {
    // Create an unordered_set of strings
    std::unordered_set<std::string> words = {"apple", "banana", "cherry"};
    
    // Insert elements
    words.insert("date");
    words.insert("elderberry");
    
    // Check if an element exists
    if (words.find("banana") != words.end()) {
        std::cout << "Found 'banana' in the set" << std::endl;
    }
    
    // Attempt to insert a duplicate element
    auto [iter, success] = words.insert("apple");
    if (!success) {
        std::cout << "'apple' was already in the set" << std::endl;
    }
    
    // Iterate through the set
    for (const auto& word : words) {
        std::cout << word << std::endl;
    }
    
    return 0;
}
```

### Key Operations and Members

`std::unordered_set` provides similar operations to `std::unordered_map`, minus the key-value pair semantics:

1. **Iterators**:
   - `begin()`, `end()`, `cbegin()`, `cend()`

2. **Capacity**:
   - `empty()`, `size()`, `max_size()`

3. **Modifiers**:
   - `insert()`: Inserts elements
   - `emplace()`: Constructs elements in-place
   - `erase()`: Removes elements
   - `clear()`: Removes all elements
   - `swap()`: Swaps the contents with another container

4. **Lookup**:
   - `find()`: Finds an element
   - `count()`: Returns the number of elements (0 or 1)
   - `equal_range()`: Returns a range of elements matching the key

5. **Bucket Interface**:
   - `bucket_count()`, `max_bucket_count()`, `bucket_size()`, `bucket()`
   - `load_factor()`, `max_load_factor()`, `rehash()`, `reserve()`

Here's a more detailed example of using `std::unordered_set`:

```cpp
#include <iostream>
#include <unordered_set>
#include <string>

struct Person {
    std::string name;
    int age;
    
    // Define equality operator for the set
    bool operator==(const Person& other) const {
        return name == other.name && age == other.age;
    }
};

// Define a hash function for Person
namespace std {
    template<>
    struct hash<Person> {
        size_t operator()(const Person& p) const {
            // Combine hash of name and age
            // (this is a simple example; more sophisticated combining might be needed)
            return hash<string>()(p.name) ^ hash<int>()(p.age);
        }
    };
}

int main() {
    // Create an unordered_set of Person objects
    std::unordered_set<Person> people;
    
    // Insert elements
    people.insert({"Alice", 30});
    people.insert({"Bob", 25});
    
    // Emplace constructs the element in-place
    people.emplace("Charlie", 40);
    
    // Check if an element exists
    Person person_to_find = {"Bob", 25};
    if (people.find(person_to_find) != people.end()) {
        std::cout << "Found Bob, age 25" << std::endl;
    }
    
    // Bucket interface demonstration
    std::cout << "Number of buckets: " << people.bucket_count() << std::endl;
    std::cout << "Load factor: " << people.load_factor() << std::endl;
    
    // Force a rehash (resize the hash table)
    people.rehash(20);
    std::cout << "After rehash, buckets: " << people.bucket_count() << std::endl;
    
    // Reserve for a specific number of elements
    people.reserve(100);
    
    // Iterate through elements
    for (const auto& person : people) {
        std::cout << person.name << ", " << person.age << std::endl;
    }
    
    // Erase an element
    people.erase({"Alice", 30});
    std::cout << "Size after erasing Alice: " << people.size() << std::endl;
    
    return 0;
}
```

## Customizing Hash Functions and Equal Predicates

By default, the unordered containers use `std::hash` and `std::equal_to` for hashing and comparison. For standard types like integers, floating-point numbers, and strings, these work out of the box. However, for custom types, you need to provide a hash function and possibly an equality comparison function.

There are two ways to do this:

1. **Specializing `std::hash` for your type** (as shown in the `Person` example above)
2. **Providing custom hash and equality functors to the container**

Here's an example of the second approach:

```cpp
#include <iostream>
#include <unordered_map>
#include <string>

struct CaseInsensitiveHash {
    size_t operator()(const std::string& key) const {
        // Create a lowercase copy for hashing
        std::string lower = key;
        std::transform(lower.begin(), lower.end(), lower.begin(), 
                     [](unsigned char c) { return std::tolower(c); });
        return std::hash<std::string>()(lower);
    }
};

struct CaseInsensitiveEqual {
    bool operator()(const std::string& left, const std::string& right) const {
        return std::equal(left.begin(), left.end(), right.begin(), right.end(),
                        [](unsigned char a, unsigned char b) {
                            return std::tolower(a) == std::tolower(b);
                        });
    }
};

int main() {
    // Create a case-insensitive string-to-int map
    std::unordered_map<
        std::string, 
        int, 
        CaseInsensitiveHash, 
        CaseInsensitiveEqual
    > ciMap;
    
    // Insert some values
    ciMap["Apple"] = 1;
    ciMap["Banana"] = 2;
    
    // These lookups will succeed despite case differences
    std::cout << "apple: " << ciMap["apple"] << std::endl;
    std::cout << "BANANA: " << ciMap["BANANA"] << std::endl;
    
    // Demonstrate that different case strings are treated as the same key
    ciMap["APPLE"] = 10;
    std::cout << "After update, Apple: " << ciMap["Apple"] << std::endl;
    
    std::cout << "Map size: " << ciMap.size() << std::endl;  // Shows 2, not 4
    
    return 0;
}
```

## Advanced Usage Patterns

### Managing Bucket Count and Load Factor

The performance of unordered containers depends significantly on the load factor (the ratio of elements to buckets). A high load factor increases the chance of collisions, which reduces performance. You can control this by:

1. Setting the maximum load factor using `max_load_factor()`
2. Reserving space with `reserve()` or adjusting bucket count with `rehash()`

```cpp
#include <iostream>
#include <unordered_map>
#include <chrono>

int main() {
    const int NUM_ELEMENTS = 1000000;
    
    // Default settings
    std::unordered_map<int, int> map1;
    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < NUM_ELEMENTS; ++i) {
        map1[i] = i;
    }
    auto end = std::chrono::high_resolution_clock::now();
    auto duration1 = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    
    // Optimized settings
    std::unordered_map<int, int> map2;
    map2.max_load_factor(0.25);  // Lower load factor
    map2.reserve(NUM_ELEMENTS);   // Reserve space for all elements
    
    start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < NUM_ELEMENTS; ++i) {
        map2[i] = i;
    }
    end = std::chrono::high_resolution_clock::now();
    auto duration2 = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    
    std::cout << "Default settings insertion time: " << duration1 << " ms\n";
    std::cout << "Optimized settings insertion time: " << duration2 << " ms\n";
    
    std::cout << "Map1 buckets: " << map1.bucket_count() 
              << ", load factor: " << map1.load_factor() << std::endl;
    std::cout << "Map2 buckets: " << map2.bucket_count() 
              << ", load factor: " << map2.load_factor() << std::endl;
    
    return 0;
}
```

### Using Transparent Comparison (C++20)

C++20 introduced heterogeneous lookup for unordered containers, allowing you to look up elements without constructing the key type when using a transparent hash and equality functions:

```cpp
#include <iostream>
#include <unordered_map>
#include <string>
#include <string_view>

// In C++20, we can use transparent comparison to avoid string allocations
struct StringHash {
    using is_transparent = void;  // Mark as transparent
    
    size_t operator()(std::string_view sv) const {
        return std::hash<std::string_view>()(sv);
    }
    
    size_t operator()(const std::string& s) const {
        return std::hash<std::string_view>()(s);
    }
    
    size_t operator()(const char* s) const {
        return std::hash<std::string_view>()(s);
    }
};

struct StringEqual {
    using is_transparent = void;  // Mark as transparent
    
    bool operator()(std::string_view lhs, std::string_view rhs) const {
        return lhs == rhs;
    }
    
    bool operator()(const std::string& lhs, std::string_view rhs) const {
        return lhs == rhs;
    }
    
    bool operator()(std::string_view lhs, const std::string& rhs) const {
        return lhs == rhs;
    }
};

int main() {
    // Using transparent comparison
    std::unordered_map<std::string, int, StringHash, StringEqual> dictionary;
    
    dictionary["apple"] = 1;
    dictionary["banana"] = 2;
    
    // We can now look up with string_view or const char* without allocations
    std::string_view sv = "apple";
    const char* cstr = "banana";
    
    // These lookups use the transparent comparators
    std::cout << "apple: " << dictionary.find(sv)->second << std::endl;
    std::cout << "banana: " << dictionary.find(cstr)->second << std::endl;
    
    return 0;
}
```

### Handling Collision-Prone Keys

Some applications may have keys that are prone to hash collisions. In such cases, you can:

1. Improve your hash function
2. Use a custom allocator optimized for linked lists
3. Consider using ordered containers if the collision rate is too high

Here's an example of a problematic case and a solution:

```cpp
#include <iostream>
#include <unordered_set>
#include <vector>
#include <string>
#include <chrono>

// A poorly designed hash function that creates many collisions
struct BadHash {
    size_t operator()(int key) const {
        return key % 10;  // Only 10 possible hash values!
    }
};

// A better hash function
struct GoodHash {
    size_t operator()(int key) const {
        // Using a more sophisticated hash function
        // This is a simple example using multiplication by a prime
        return static_cast<size_t>(key * 2654435761ULL);
    }
};

int main() {
    const int NUM_ELEMENTS = 100000;
    
    // With bad hash function
    std::unordered_set<int, BadHash> set1;
    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < NUM_ELEMENTS; ++i) {
        set1.insert(i);
    }
    auto end = std::chrono::high_resolution_clock::now();
    auto duration1 = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    
    // With better hash function
    std::unordered_set<int, GoodHash> set2;
    start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < NUM_ELEMENTS; ++i) {
        set2.insert(i);
    }
    end = std::chrono::high_resolution_clock::now();
    auto duration2 = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    
    std::cout << "Bad hash function time: " << duration1 << " ms\n";
    std::cout << "Good hash function time: " << duration2 << " ms\n";
    
    // Examine bucket distributions
    std::cout << "\nBad hash bucket distribution:\n";
    for (size_t i = 0; i < 10; ++i) {
        std::cout << "Bucket " << i << ": " << set1.bucket_size(i) << " elements\n";
    }
    
    std::cout << "\nGood hash statistics:\n";
    int max_bucket_size = 0;
    for (size_t i = 0; i < set2.bucket_count(); ++i) {
        max_bucket_size = std::max(max_bucket_size, static_cast<int>(set2.bucket_size(i)));
    }
    std::cout << "Max bucket size: " << max_bucket_size << std::endl;
    std::cout << "Total buckets: " << set2.bucket_count() << std::endl;
    
    return 0;
}
```

## Common Pitfalls and Best Practices

### 1. Iterator Invalidation

Iterators to unordered containers can be invalidated by operations that modify the container:

- **Insertion**: Invalidates iterators if rehashing occurs
- **Erasure**: Invalidates only iterators to the erased elements
- **Rehashing**: Invalidates all iterators

```cpp
#include <iostream>
#include <unordered_map>
#include <string>

int main() {
    std::unordered_map<std::string, int> map = {
        {"one", 1},
        {"two", 2},
        {"three", 3}
    };
    
    // UNSAFE: This can cause undefined behavior if rehashing occurs
    for (auto it = map.begin(); it != map.end(); /* no increment here */) {
        if (it->second % 2 == 0) {
            // Erasing invalidates the current iterator
            map.erase(it++);  // Post-increment: use current value, then increment
        } else {
            ++it;
        }
    }
    
    // BETTER: Use the return value of erase() (C++11 and later)
    auto it = map.begin();
    while (it != map.end()) {
        if (it->second % 2 == 0) {
            it = map.erase(it);  // erase returns iterator to next element
        } else {
            ++it;
        }
    }
    
    for (const auto& [key, value] : map) {
        std::cout << key << ": " << value << std::endl;
    }
    
    return 0;
}
```

### 2. Key Mutability Caution

The keys in unordered containers should not be modified directly through iterators, as this would invalidate their position in the hash table.

```cpp
#include <iostream>
#include <unordered_set>
#include <string>

class MutableString {
public:
    MutableString(const std::string& s) : str(s) {}
    
    void append(const std::string& suffix) {
        str += suffix;  // Modifying the string!
    }
    
    const std::string& get() const { return str; }
    
    // For comparison in the set
    bool operator==(const MutableString& other) const {
        return str == other.str;
    }
    
private:
    std::string str;
};

// Hash function
namespace std {
    template<>
    struct hash<MutableString> {
        size_t operator()(const MutableString& ms) const {
            return hash<string>()(ms.get());
        }
    };
}

int main() {
    std::unordered_set<MutableString> names;
    
    names.insert(MutableString("Alice"));
    names.insert(MutableString("Bob"));
    
    // DANGEROUS: Do not modify a key that's already in a container
    // This will corrupt the hash table because the element's hash will change
    for (auto& name : names) {
        // Modifying the key in place - THIS IS BAD!
        // const_cast<MutableString&>(name).append(" Smith");
    }
    
    // CORRECT: Remove the old key and insert a modified one
    auto it = names.find(MutableString("Alice"));
    if (it != names.end()) {
        MutableString modifiedAlice = *it;
        names.erase(it);
        
        // Modify and reinsert
        modifiedAlice.append(" Smith");
        names.insert(modifiedAlice);
    }
    
    for (const auto& name : names) {
        std::cout << name.get() << std::endl;
    }
    
    return 0;
}
```

### 3. Reserve Capacity for Better Performance

To minimize rehashing and improve performance, reserve sufficient capacity upfront:

```cpp
#include <iostream>
#include <unordered_map>
#include <chrono>
#include <vector>
#include <random>

int main() {
    const int NUM_ELEMENTS = 1000000;
    
    std::vector<int> keys(NUM_ELEMENTS);
    
    // Generate random keys
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(1, INT_MAX);
    
    for (int i = 0; i < NUM_ELEMENTS; ++i) {
        keys[i] = dis(gen);
    }
    
    // Without reserving
    std::unordered_map<int, int> map1;
    auto start = std::chrono::high_resolution_clock::now();
    for (int key : keys) {
        map1[key] = key;
    }
    auto end = std::chrono::high_resolution_clock::now();
    auto duration1 = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    
    // With reserving
    std::unordered_map<int, int> map2;
    map2.reserve(NUM_ELEMENTS);  // Reserve space for all elements
    
    start = std::chrono::high_resolution_clock::now();
    for (int key : keys) {
        map2[key] = key;
    }
    end = std::chrono::high_resolution_clock::now();
    auto duration2 = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    
    std::cout << "Without reserve: " << duration1 << " ms\n";
    std::cout << "With reserve: " << duration2 << " ms\n";
    std::cout << "Improvement: " << (100.0 * (duration1 - duration2) / duration1) << "%\n";
    
    return 0;
}
```

### 4. Using emplace() Instead of insert()

When possible, use `emplace()` instead of `insert()` to avoid unnecessary temporary objects:

```cpp
#include <iostream>
#include <unordered_map>
#include <string>
#include <chrono>

class ExpensiveToCopy {
public:
    ExpensiveToCopy(const std::string& s, int v) : str(s), value(v) {
        // Simulate expensive copy
    }
    
    ExpensiveToCopy(const ExpensiveToCopy& other) : str(other.str), value(other.value) {
        // Expensive copy constructor
        std::this_thread::sleep_for(std::chrono::microseconds(1));
    }
    
    std::string str;
    int value;
};

int main() {
    const int ITERATIONS = 10000;
    
    // Using insert
    std::unordered_map<int, ExpensiveToCopy> map1;
    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < ITERATIONS; ++i) {
        map1.insert({i, ExpensiveToCopy("value", i)});
    }
    auto end = std::chrono::high_resolution_clock::now();
    auto duration1 = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    
    // Using emplace
    std::unordered_map<int, ExpensiveToCopy> map2;
    start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < ITERATIONS; ++i) {
        map2.emplace(i, "value", i);  // Constructs in-place
    }
    end = std::chrono::high_resolution_clock::now();
    auto duration2 = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    
    std::cout << "Using insert: " << duration1 << " ms\n";
    std::cout << "Using emplace: " << duration2 << " ms\n";
    
    return 0;
}
```

## Conclusion

Unordered containers in C++11 provide a powerful alternative to their ordered counterparts when fast access is the priority over ordering. They offer amortized constant-time lookup, insertion, and deletion operations, making them suitable for performance-critical applications.

Key points to remember:

1. Use `std::unordered_map` and `std::unordered_set` when ordering is not important and you need faster lookup times.
2. Understand that these containers use hash tables, which offer O(1) average time complexity but can degrade to O(n) in worst cases.
3. For custom types, provide appropriate hash functions and equality operators.
4. Manage the load factor and bucket count for optimal performance.
5. Be aware of iterator invalidation rules when modifying the containers.
6. Prefer `emplace()` over `insert()` when constructing elements in-place.
7. Reserve capacity upfront when the approximate number of elements is known.

With these considerations in mind, unordered containers can significantly improve the performance of your C++ applications, especially for lookup-intensive operations.