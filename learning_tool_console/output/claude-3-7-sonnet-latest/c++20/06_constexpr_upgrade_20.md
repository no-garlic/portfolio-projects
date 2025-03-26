# C++20 constexpr Improvements: std::vector, std::string, and Beyond

## Introduction

Compile-time programming has been steadily expanding in C++ since the introduction of `constexpr` in C++11. Each standard revision has brought new capabilities to compile-time evaluation, but C++20 represents a quantum leap by allowing dynamic memory allocation within `constexpr` contexts. This advancement enables the use of standard containers like `std::vector` and `std::string` in constant expressions, dramatically increasing the possibilities for compile-time computation. This article explores these improvements in depth, providing detailed examples of how these features can be used to shift computation from runtime to compile time.

## Evolution of constexpr Before C++20

Before diving into the C++20 enhancements, let's review the evolution of `constexpr`:

- **C++11** introduced `constexpr` functions and variables but with significant restrictions. Functions could contain only a single return statement, and no mutations were allowed.
- **C++14** loosened these restrictions by allowing multiple statements, local variables, loops, and conditionals in `constexpr` functions.
- **C++17** added if constexpr, constexpr lambdas, and made more standard library functions constexpr-enabled.

Despite these improvements, a critical limitation remained: `constexpr` code couldn't allocate or deallocate memory. This restriction effectively prevented standard containers like `std::vector` and `std::string` from being used in constant expressions because they rely on dynamic memory allocation.

## C++20's Dynamic Memory in constexpr

C++20 removes this fundamental limitation by allowing:

1. Dynamic memory allocation and deallocation in `constexpr` contexts
2. Non-trivial destructors in `constexpr` contexts
3. `try`/`catch` blocks in `constexpr` functions (though exceptions can't be thrown during constant evaluation)
4. `virtual` function calls in `constexpr` contexts

These changes enable containers and standard library functions that use dynamic memory to be `constexpr`-friendly.

## constexpr std::vector

Let's examine how `std::vector` can now be used in `constexpr` contexts:

```cpp
#include <vector>
#include <algorithm>
#include <iostream>

constexpr std::vector<int> create_fibonacci(int n) {
    std::vector<int> fib(n);
    if (n > 0) fib[0] = 0;
    if (n > 1) fib[1] = 1;
    
    for (int i = 2; i < n; ++i) {
        fib[i] = fib[i-1] + fib[i-2];
    }
    
    return fib;
}

constexpr bool is_sorted(const std::vector<int>& vec) {
    return std::is_sorted(vec.begin(), vec.end());
}

constexpr std::vector<int> sort_vector(std::vector<int> vec) {
    std::sort(vec.begin(), vec.end());
    return vec;
}

int main() {
    // Compile-time computation
    constexpr auto fibonacci = create_fibonacci(10);
    constexpr bool sorted = is_sorted(fibonacci);
    
    // Compile-time transformation
    constexpr auto unsorted = std::vector<int>{5, 3, 1, 4, 2};
    constexpr auto sorted = sort_vector(unsorted);
    
    // Use the results at runtime
    for (int value : fibonacci) {
        std::cout << value << ' ';
    }
    std::cout << "\nIs fibonacci sorted? " << (sorted ? "Yes" : "No") << std::endl;
    
    for (int value : sorted) {
        std::cout << value << ' ';
    }
    std::cout << std::endl;
}
```

Key points about `constexpr std::vector`:

1. All vector operations including construction, destruction, element access, insertion, and removal can be performed at compile time.
2. Algorithm functions like `std::sort`, `std::find`, and `std::transform` work with `constexpr` vectors.
3. The entire vector lifetime must be within the `constexpr` evaluation context.
4. Memory allocated during constant evaluation is automatically deallocated when the evaluation completes.

## constexpr std::string

Similarly, `std::string` can now be used in `constexpr` contexts:

```cpp
#include <string>
#include <algorithm>
#include <iostream>

constexpr std::string create_palindrome(std::string_view input) {
    std::string result{input};
    std::string reversed{input.rbegin(), input.rend()};
    result += reversed;
    return result;
}

constexpr bool is_palindrome(std::string_view str) {
    std::string_view first_half = str.substr(0, str.size() / 2);
    std::string_view second_half = str.substr((str.size() + 1) / 2);
    
    for (size_t i = 0; i < first_half.size(); ++i) {
        if (first_half[i] != second_half[second_half.size() - 1 - i]) {
            return false;
        }
    }
    return true;
}

constexpr std::string to_uppercase(std::string str) {
    for (char& c : str) {
        if (c >= 'a' && c <= 'z') {
            c = c - 'a' + 'A';
        }
    }
    return str;
}

int main() {
    // Compile-time string manipulation
    constexpr auto palindrome = create_palindrome("hello");
    constexpr bool is_pal = is_palindrome("racecar");
    constexpr auto uppercase = to_uppercase("Hello, World!");
    
    std::cout << "Palindrome: " << palindrome << std::endl;
    std::cout << "Is 'racecar' a palindrome? " << (is_pal ? "Yes" : "No") << std::endl;
    std::cout << "Uppercase: " << uppercase << std::endl;
}
```

Key points about `constexpr std::string`:

1. String operations like concatenation, substring extraction, and character manipulation can be performed at compile time.
2. String algorithms can be evaluated at compile time.
3. String operations that would normally allocate memory at runtime now do so at compile time.

## constexpr Algorithms and Other Container Improvements

In C++20, many standard library algorithms are now `constexpr`-enabled:

```cpp
#include <vector>
#include <algorithm>
#include <numeric>
#include <iostream>

constexpr std::vector<int> filter_even_numbers(const std::vector<int>& input) {
    std::vector<int> result;
    std::copy_if(input.begin(), input.end(), std::back_inserter(result),
                 [](int x) { return x % 2 == 0; });
    return result;
}

constexpr int sum_vector(const std::vector<int>& vec) {
    return std::accumulate(vec.begin(), vec.end(), 0);
}

constexpr std::vector<int> transform_vector(const std::vector<int>& input) {
    std::vector<int> result(input.size());
    std::transform(input.begin(), input.end(), result.begin(),
                  [](int x) { return x * x; });
    return result;
}

int main() {
    constexpr std::vector<int> numbers{1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    
    // Filter, transform, and sum at compile time
    constexpr auto even_numbers = filter_even_numbers(numbers);
    constexpr auto squared_numbers = transform_vector(numbers);
    constexpr auto sum = sum_vector(numbers);
    
    std::cout << "Sum of numbers: " << sum << std::endl;
    
    std::cout << "Even numbers: ";
    for (int num : even_numbers) {
        std::cout << num << ' ';
    }
    std::cout << std::endl;
    
    std::cout << "Squared numbers: ";
    for (int num : squared_numbers) {
        std::cout << num << ' ';
    }
    std::cout << std::endl;
}
```

Beyond `std::vector` and `std::string`, C++20 also makes several other containers `constexpr`-friendly:

- `std::array`
- `std::map` and `std::set`
- `std::unordered_map` and `std::unordered_set`

## Implementation Details and Constraints

While `constexpr` dynamic memory allocation is powerful, it comes with some constraints:

1. **Allocation Tracking**: The compiler must track all allocations and ensure they're properly deallocated before the `constexpr` evaluation completes.

2. **Lifetime Management**: Objects created during constant evaluation must not escape that evaluation context.

3. **Resource Limits**: Compilers typically impose limits on the resources (memory, computation steps) that can be used during constant evaluation.

```cpp
#include <vector>
#include <stdexcept>

constexpr std::vector<int> generate_large_vector(size_t size) {
    if (size > 10000) {
        // This might exceed compiler limits for constexpr evaluation
        throw std::runtime_error("Too large for constexpr");
    }
    
    std::vector<int> result(size);
    for (size_t i = 0; i < size; ++i) {
        result[i] = static_cast<int>(i);
    }
    return result;
}

int main() {
    // This will work in constexpr
    constexpr auto small_vec = generate_large_vector(1000);
    
    // This might fail to compile due to resource limits
    // Uncomment to test:
    // constexpr auto large_vec = generate_large_vector(1000000);
    
    return 0;
}
```

## Memory Leaks in constexpr

An important improvement is that the compiler now prevents memory leaks in `constexpr` contexts:

```cpp
#include <vector>
#include <memory>

constexpr bool test_memory_leak() {
    // This would leak at runtime, but is caught in constexpr evaluation
    int* ptr = new int(42);
    // Oops, forgot to delete
    return true;
}

// Won't compile: memory leak detected during constant evaluation
// constexpr bool leaked = test_memory_leak();

constexpr bool test_proper_cleanup() {
    int* ptr = new int(42);
    delete ptr;
    return true;
}

// This compiles fine
constexpr bool no_leak = test_proper_cleanup();

int main() {
    return 0;
}
```

## Practical Applications

Let's explore some practical applications of these improvements:

### Parse Configuration at Compile Time

```cpp
#include <string>
#include <vector>
#include <iostream>

struct ConfigEntry {
    std::string key;
    std::string value;
};

constexpr std::vector<ConfigEntry> parse_config(std::string_view config_text) {
    std::vector<ConfigEntry> result;
    
    size_t pos = 0;
    while (pos < config_text.size()) {
        size_t line_end = config_text.find('\n', pos);
        if (line_end == std::string_view::npos) {
            line_end = config_text.size();
        }
        
        std::string_view line = config_text.substr(pos, line_end - pos);
        pos = line_end + 1;
        
        // Skip empty lines or comments
        if (line.empty() || line[0] == '#') {
            continue;
        }
        
        size_t equals_pos = line.find('=');
        if (equals_pos != std::string_view::npos) {
            std::string_view key = line.substr(0, equals_pos);
            std::string_view value = line.substr(equals_pos + 1);
            
            // Trim whitespace (simplified)
            while (!key.empty() && key.back() == ' ') key.remove_suffix(1);
            while (!value.empty() && value.front() == ' ') value.remove_prefix(1);
            
            result.push_back({std::string(key), std::string(value)});
        }
    }
    
    return result;
}

int main() {
    constexpr std::string_view config_text = 
        "# Database configuration\n"
        "db_host = localhost\n"
        "db_port = 5432\n"
        "db_name = myapp\n"
        "db_user = admin\n";
    
    constexpr auto config = parse_config(config_text);
    
    // Use the parsed configuration at runtime
    for (const auto& entry : config) {
        std::cout << "Key: " << entry.key << ", Value: " << entry.value << std::endl;
    }
}
```

### Compile-Time Regular Expression Matching

While std::regex itself isn't constexpr (yet), we can implement simple pattern matching:

```cpp
#include <string>
#include <vector>
#include <iostream>

constexpr bool is_match(std::string_view text, std::string_view pattern) {
    // Simplified wildcard pattern matching (* matches any sequence)
    if (pattern.empty()) return text.empty();
    
    if (pattern[0] == '*') {
        // Match zero or more characters
        for (size_t i = 0; i <= text.size(); ++i) {
            if (is_match(text.substr(i), pattern.substr(1))) {
                return true;
            }
        }
        return false;
    }
    
    return !text.empty() && 
           (pattern[0] == '?' || text[0] == pattern[0]) && 
           is_match(text.substr(1), pattern.substr(1));
}

constexpr std::vector<std::string> filter_matches(
    const std::vector<std::string>& texts, std::string_view pattern) {
    
    std::vector<std::string> result;
    for (const auto& text : texts) {
        if (is_match(text, pattern)) {
            result.push_back(text);
        }
    }
    return result;
}

int main() {
    constexpr std::vector<std::string> file_names{
        "document.txt", "image.png", "spreadsheet.xlsx", 
        "presentation.pptx", "notes.txt"
    };
    
    constexpr auto txt_files = filter_matches(file_names, "*.txt");
    
    std::cout << "Text files:" << std::endl;
    for (const auto& file : txt_files) {
        std::cout << "  " << file << std::endl;
    }
}
```

## Performance Considerations

Using `constexpr` with containers offers several performance benefits:

1. **Reduced Runtime Overhead**: Computations performed at compile time don't incur runtime costs.

2. **Optimization Opportunities**: The compiler has more information to optimize code when values are known at compile time.

3. **Reduced Binary Size**: For constant data, the compiler can often generate more efficient representations than runtime initialization would.

However, it also comes with some costs:

1. **Increased Compilation Time**: Complex `constexpr` evaluations can significantly increase build times.

2. **Code Size**: If the same `constexpr` function is instantiated with many different constant arguments, code bloat can occur.

## Best Practices

Here are some guidelines for effective use of `constexpr` containers:

1. **Use for Deterministic Computations**: Ideal for algorithms that are deterministic and don't rely on external inputs.

2. **Balance Compile vs. Runtime**: Consider whether the computation truly needs to happen at compile time. Not everything should be `constexpr`.

3. **Watch Compilation Times**: Monitor your build times when introducing complex `constexpr` evaluations.

4. **Use `if constexpr` for Conditional Compilation**: For compile-time branches that select different implementations.

5. **Add Constraints**: Use static_assert to provide meaningful error messages when constraints are violated.

```cpp
#include <vector>
#include <string>
#include <type_traits>

template <typename T>
constexpr auto create_filled_vector(size_t size, const T& value) {
    static_assert(std::is_copy_constructible_v<T>, 
                  "T must be copy constructible");
                  
    if constexpr (std::is_trivially_copyable_v<T>) {
        // More efficient implementation for trivial types
        std::vector<T> result(size, value);
        return result;
    } else {
        // Potentially slower implementation for complex types
        std::vector<T> result;
        result.reserve(size);
        for (size_t i = 0; i < size; ++i) {
            result.push_back(value);
        }
        return result;
    }
}

int main() {
    // Uses the trivial implementation
    constexpr auto ints = create_filled_vector(10, 42);
    
    // Uses the non-trivial implementation
    constexpr auto strings = create_filled_vector(5, std::string("hello"));
    
    return 0;
}
```

## Conclusion

C++20's constexpr improvements represent a major advancement in compile-time programming capabilities. By enabling dynamic memory allocation in constant expressions, containers like std::vector and std::string can now be used in constexpr contexts, dramatically expanding what can be computed at compile time.

These improvements allow developers to move more computation from runtime to compile time, potentially improving performance, safety, and expressiveness. The ability to use containers and their algorithms in constexpr contexts makes functional and declarative programming styles more natural in C++.

While these features come with some constraints and potential compilation overhead, they provide powerful new tools for metaprogramming, configuration, and performance optimization. As compilers continue to improve their constexpr evaluation capabilities, we can expect these features to become increasingly important in modern C++ development.