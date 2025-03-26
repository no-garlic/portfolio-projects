# std::string_view in C++17: A Non-Owning View of String Data

## Introduction

C++17 introduced `std::string_view`, a lightweight, non-owning reference to a string or a part of a string. Before `string_view`, functions that needed to accept string data often used parameters like `const std::string&` or `const char*`, both with significant drawbacks. `const std::string&` can force unnecessary copies when given string literals or substrings, while `const char*` lacks the rich interface of `std::string` and requires manual length tracking. `std::string_view` solves these problems by providing a consistent, efficient way to refer to string data without owning it.

## Basic Concept and Benefits

`std::string_view` is defined in the `<string_view>` header and provides a read-only view of a contiguous sequence of characters. Its key characteristics are:

1. **Non-owning**: It doesn't manage or own the referenced memory
2. **Read-only**: Cannot modify the viewed characters
3. **Lightweight**: Consists of just a pointer and a length
4. **Consistent interface**: Similar to `std::string` but simpler

The primary benefit is performance: `string_view` avoids unnecessary memory allocations and copies. This is particularly valuable in APIs that receive string parameters but don't need to modify them.

## Creating a std::string_view

You can create a `string_view` from various string types:

```cpp
#include <string_view>
#include <string>
#include <iostream>

void example_creation() {
    // From string literal
    std::string_view sv1 = "Hello, world!";
    
    // From std::string
    std::string str = "Hello, C++17";
    std::string_view sv2 = str;
    
    // From character array with explicit length
    char arr[] = {'H', 'e', 'l', 'l', 'o'};
    std::string_view sv3(arr, 5);
    
    // From another string_view
    std::string_view sv4 = sv1;
    
    // Empty string_view
    std::string_view sv5;
    
    std::cout << "sv1: " << sv1 << "\n";
    std::cout << "sv2: " << sv2 << "\n";
    std::cout << "sv3: " << sv3 << "\n";
    std::cout << "sv4: " << sv4 << "\n";
    std::cout << "sv5 length: " << sv5.length() << "\n";
}
```

## Core API and Operations

`std::string_view` provides many familiar methods from `std::string`:

```cpp
void string_view_operations() {
    std::string_view sv = "Hello, world!";
    
    // Size operations
    std::cout << "Length: " << sv.length() << "\n";  // 13
    std::cout << "Size: " << sv.size() << "\n";      // 13
    std::cout << "Empty: " << sv.empty() << "\n";    // 0 (false)
    std::cout << "Max size: " << sv.max_size() << "\n";
    
    // Access operations
    std::cout << "First char: " << sv[0] << "\n";           // H
    std::cout << "Last char: " << sv[sv.size() - 1] << "\n"; // !
    std::cout << "Front: " << sv.front() << "\n";           // H
    std::cout << "Back: " << sv.back() << "\n";             // !
    std::cout << "Data pointer: " << static_cast<const void*>(sv.data()) << "\n";
    
    // Substring operations
    std::string_view hello = sv.substr(0, 5);   // "Hello"
    std::cout << "Substring: " << hello << "\n";
    
    // Search operations
    std::cout << "Find 'world': " << sv.find("world") << "\n";     // 7
    std::cout << "Contains 'Hello': " << (sv.find("Hello") != std::string_view::npos) << "\n";  // true
    
    // Compare operations
    std::cout << "Starts with 'He': " << sv.starts_with("He") << "\n";  // C++20 feature
    std::cout << "Ends with 'ld!': " << sv.ends_with("ld!") << "\n";    // C++20 feature
    
    // Removal operations
    std::string_view sv2 = "  trimmed  ";
    sv2.remove_prefix(2);  // Removes first 2 characters
    sv2.remove_suffix(2);  // Removes last 2 characters
    std::cout << "After trim: '" << sv2 << "'\n";  // "trimmed"
}
```

Note that `starts_with` and `ends_with` are actually C++20 features, but they're mentioned here for completeness. In C++17, you need to use:

```cpp
bool starts_with(std::string_view sv, std::string_view prefix) {
    return sv.substr(0, prefix.size()) == prefix;
}

bool ends_with(std::string_view sv, std::string_view suffix) {
    return sv.size() >= suffix.size() && 
           sv.substr(sv.size() - suffix.size()) == suffix;
}
```

## Performance Benefits

One of the main advantages of `string_view` is avoiding unnecessary memory allocations. Consider this example:

```cpp
#include <string>
#include <string_view>
#include <chrono>
#include <iostream>
#include <vector>

// Function taking string by const reference
void processStringRef(const std::string& str) {
    // Just prevent compiler optimization
    volatile char c = str[0];
}

// Function taking string_view
void processStringView(std::string_view sv) {
    // Just prevent compiler optimization
    volatile char c = sv[0];
}

void performance_comparison() {
    const int ITERATIONS = 1000000;
    std::vector<std::string> strings;
    
    // Generate 100 strings
    for (int i = 0; i < 100; ++i) {
        strings.push_back("String #" + std::to_string(i));
    }
    
    // Test with const std::string&
    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < ITERATIONS; ++i) {
        processStringRef(strings[i % 100]);
    }
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed1 = end - start;
    
    // Test with std::string_view
    start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < ITERATIONS; ++i) {
        processStringView(strings[i % 100]);
    }
    end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed2 = end - start;
    
    std::cout << "const std::string&: " << elapsed1.count() << "s\n";
    std::cout << "std::string_view:   " << elapsed2.count() << "s\n";
    
    // Processing substrings - here string_view really shines
    start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < ITERATIONS; ++i) {
        // Creates a new string for the substring
        processStringRef(strings[i % 100].substr(0, 5));
    }
    end = std::chrono::high_resolution_clock::now();
    elapsed1 = end - start;
    
    start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < ITERATIONS; ++i) {
        // Just creates a new view - no allocation
        processStringView(std::string_view(strings[i % 100]).substr(0, 5));
    }
    end = std::chrono::high_resolution_clock::now();
    elapsed2 = end - start;
    
    std::cout << "Substring with const std::string&: " << elapsed1.count() << "s\n";
    std::cout << "Substring with std::string_view:   " << elapsed2.count() << "s\n";
}
```

This demonstrates the significant performance advantage of `string_view` when working with substrings. When using `std::string::substr()`, a new string is allocated and the characters are copied. With `std::string_view::substr()`, only a new view is created (just a pointer and length), with no memory allocation.

## Real-World Use Cases

### Parsing Functions

`string_view` is excellent for parsing tasks where you need to examine parts of strings without modifying them:

```cpp
#include <string_view>
#include <iostream>
#include <vector>

std::vector<std::string_view> split(std::string_view str, char delimiter) {
    std::vector<std::string_view> result;
    
    size_t start = 0;
    size_t end = str.find(delimiter);
    
    while (end != std::string_view::npos) {
        result.push_back(str.substr(start, end - start));
        start = end + 1;
        end = str.find(delimiter, start);
    }
    
    // Add the last piece
    if (start < str.length()) {
        result.push_back(str.substr(start));
    }
    
    return result;
}

void parsing_example() {
    std::string input = "apple,banana,cherry,date,elderberry";
    
    // Split the string into tokens
    std::vector<std::string_view> tokens = split(input, ',');
    
    // Print the tokens
    for (const auto& token : tokens) {
        std::cout << "Token: " << token << "\n";
    }
    
    // We can further process these tokens without making copies
    for (const auto& token : tokens) {
        if (token.starts_with('a')) {  // C++20 feature
            std::cout << "Starts with 'a': " << token << "\n";
        }
        
        if (token.length() > 6) {
            std::cout << "Long fruit: " << token << "\n";
        }
    }
}
```

### Function Parameters

Using `string_view` for parameters ensures efficient handling regardless of the source:

```cpp
#include <string_view>
#include <string>
#include <iostream>

// Accept any string-like input efficiently
void log(std::string_view message) {
    std::cout << "[LOG] " << message << "\n";
}

void function_parameters_example() {
    // All of these are efficient, no copies made
    log("Literal string");
    
    std::string std_string = "Standard string";
    log(std_string);
    
    const char* c_string = "C-style string";
    log(c_string);
    
    char buffer[20] = "Character buffer";
    log(buffer);
    
    // Using substring is also efficient
    log(std_string.substr(0, 8));  // Would create a new string
    log(std::string_view(std_string).substr(0, 8));  // No new allocation
}
```

### String Processing Functions

Creating a library of string processing functions that work with `string_view`:

```cpp
#include <string_view>
#include <iostream>
#include <cctype>
#include <algorithm>

bool contains_ignore_case(std::string_view haystack, std::string_view needle) {
    auto to_lower = [](unsigned char c) { return std::tolower(c); };
    
    return std::search(
        haystack.begin(), haystack.end(),
        needle.begin(), needle.end(),
        [&](unsigned char a, unsigned char b) {
            return to_lower(a) == to_lower(b);
        }
    ) != haystack.end();
}

bool is_numeric(std::string_view str) {
    return !str.empty() && std::all_of(str.begin(), str.end(), 
                                       [](unsigned char c) { return std::isdigit(c); });
}

std::string_view trim_left(std::string_view str) {
    auto it = std::find_if_not(str.begin(), str.end(), 
                              [](unsigned char c) { return std::isspace(c); });
    return str.substr(std::distance(str.begin(), it));
}

std::string_view trim_right(std::string_view str) {
    auto it = std::find_if_not(str.rbegin(), str.rend(), 
                              [](unsigned char c) { return std::isspace(c); });
    return str.substr(0, str.length() - std::distance(str.rbegin(), it));
}

std::string_view trim(std::string_view str) {
    return trim_left(trim_right(str));
}

void string_processing_example() {
    std::string s = "  Hello, World!  ";
    std::cout << "Original: '" << s << "'\n";
    std::cout << "Trimmed: '" << trim(s) << "'\n";
    
    std::cout << "Contains 'world' (case insensitive): " 
              << contains_ignore_case(s, "world") << "\n";
    
    std::string nums = "12345";
    std::cout << "Is numeric: " << is_numeric(nums) << "\n";
    std::cout << "Is alphanumeric: " << is_numeric("abc123") << "\n";
}
```

## Lifetime Management and Potential Pitfalls

The biggest risk with `string_view` is dangling references. Since it doesn't own the memory it refers to, you must ensure the underlying data outlives the view:

```cpp
#include <string_view>
#include <string>
#include <iostream>

std::string_view dangerous_function() {
    std::string local_string = "This string will disappear!";
    return local_string;  // DANGEROUS: returns view to a temporary that will be destroyed
}

std::string_view also_dangerous(const std::string& s) {
    return s.substr(0, 5);  // DANGEROUS: returns view to a temporary std::string
}

void safe_usage(std::string_view sv) {
    // Safe: we're just using the view during the function call
    std::cout << "View: " << sv << "\n";
}

void lifetime_examples() {
    // WRONG: Dangling reference
    std::string_view bad_sv = dangerous_function();
    std::cout << "Bad view: " << bad_sv << "\n";  // Undefined behavior
    
    std::string str = "Hello, world";
    
    // WRONG: View to a temporary substring
    std::string_view also_bad = also_dangerous(str);
    std::cout << "Also bad: " << also_bad << "\n";  // Undefined behavior
    
    // CORRECT: Original data outlives the view
    std::string_view good_sv = str;
    std::cout << "Good view: " << good_sv << "\n";
    
    // CORRECT: Taking substring from string_view, not std::string
    std::string_view better_sv = std::string_view(str).substr(0, 5);
    std::cout << "Better view: " << better_sv << "\n";
    
    // CORRECT: String literal has static lifetime
    std::string_view static_sv = "I'll live forever";
    std::cout << "Static view: " << static_sv << "\n";
}
```

Here are some lifetime management rules to follow:

1. **Never** return a `string_view` to a local string variable
2. **Avoid** returning a `string_view` from a function unless the source has a longer lifetime
3. **Be careful** with `string_view` to temporary objects or expressions
4. **Use `string_view::substr()`** instead of `std::string::substr()` when you need a view of a substring

## Comparison with Other String Types

Here's how `string_view` compares to other string representations:

```cpp
#include <string>
#include <string_view>
#include <iostream>
#include <memory>
#include <vector>

void comparison_example() {
    // Memory usage
    std::cout << "sizeof(char*): " << sizeof(char*) << " bytes\n";
    std::cout << "sizeof(std::string): " << sizeof(std::string) << " bytes\n";
    std::cout << "sizeof(std::string_view): " << sizeof(std::string_view) << " bytes\n";
    
    // Let's create a large string
    std::string large_string(1000, 'x');
    
    // Various ways to reference this string:
    
    // 1. const char* - lightweight but loses length information
    const char* c_str = large_string.c_str();
    std::cout << "c_str length must be calculated: " << strlen(c_str) << "\n";
    
    // 2. const std::string& - heavyweight reference, but has full string functionality
    const std::string& str_ref = large_string;
    std::cout << "str_ref length: " << str_ref.length() << "\n";
    
    // 3. std::string - makes a full copy, expensive for large strings
    std::string str_copy = large_string;
    std::cout << "str_copy length: " << str_copy.length() << "\n";
    
    // 4. std::string_view - lightweight, keeps length, has most string functionality
    std::string_view str_view = large_string;
    std::cout << "str_view length: " << str_view.length() << "\n";
    
    // Substring handling:
    // With std::string - allocates new memory
    std::string substr_copy = large_string.substr(10, 20);
    
    // With std::string_view - just adjusts pointers, no allocation
    std::string_view substr_view = std::string_view(large_string).substr(10, 20);
    
    // Substring from string_view is very efficient
    std::string_view another_view = str_view.substr(5, 10);
}
```

## Integration with the Standard Library

C++17 provides overloads for many standard algorithms and functions to work with `string_view`:

```cpp
#include <string_view>
#include <algorithm>
#include <iostream>

void standard_library_integration() {
    std::string_view text = "Hello, World!";
    
    // Find the first occurrence of 'o'
    auto it = std::find(text.begin(), text.end(), 'o');
    if (it != text.end()) {
        std::cout << "Found 'o' at position " << std::distance(text.begin(), it) << "\n";
    }
    
    // Count occurrences of 'l'
    int count = std::count(text.begin(), text.end(), 'l');
    std::cout << "Number of 'l': " << count << "\n";
    
    // Check if text contains all lowercase letters
    bool all_lower = std::all_of(text.begin(), text.end(), 
                                [](char c) { return std::islower(c); });
    std::cout << "All lowercase: " << all_lower << "\n";
    
    // Transform to uppercase (note: we need to create a new string since string_view is read-only)
    std::string upper(text.length(), ' ');
    std::transform(text.begin(), text.end(), upper.begin(), 
                  [](char c) { return std::toupper(c); });
    std::cout << "Uppercase: " << upper << "\n";
}
```

## Converting Back to std::string

Sometimes you need to convert a `string_view` back to a `std::string`, especially when you need to modify the string or store it:

```cpp
#include <string_view>
#include <string>
#include <iostream>

void conversion_example() {
    std::string_view sv = "Hello, string_view!";
    
    // Convert to std::string
    std::string str(sv);
    
    // Alternative conversion
    std::string str2 = std::string(sv);
    
    // This also works
    std::string str3{sv.data(), sv.size()};
    
    // If you have a function that requires std::string
    void requires_string(const std::string& s) {
        std::cout << "Got string: " << s << "\n";
    }
    
    // Implicit conversion - creates a temporary string
    requires_string(sv);
    
    // Explicit conversion
    requires_string(std::string(sv));
}
```

## Advanced Usage: Unicode and Non-ASCII Text

`string_view` works with bytes, not characters, so care must be taken with multibyte encodings:

```cpp
#include <string_view>
#include <string>
#include <iostream>

void unicode_example() {
    // UTF-8 encoded string with non-ASCII characters
    std::string utf8_string = "Hello, 世界!";
    std::string_view sv = utf8_string;
    
    std::cout << "UTF-8 string view: " << sv << "\n";
    std::cout << "Byte length: " << sv.length() << "\n";
    
    // WARNING: String view operations are byte-based, not character-based
    // So this might cut a multibyte character in half!
    std::string_view first_half = sv.substr(0, sv.length() / 2);
    std::cout << "First half (potentially invalid UTF-8): " << first_half << "\n";
    
    // For proper Unicode handling, you need a Unicode-aware library
    // string_view just gives you a view of the raw bytes
}
```

## Conclusion

`std::string_view` addresses a longstanding problem in C++ by providing a lightweight, non-owning reference to string data. It combines the efficiency of raw pointers with most of the convenience of `std::string`, making it an ideal choice for function parameters and operations that don't need to own or modify strings.

The key benefits of `string_view` include avoiding unnecessary memory allocations, particularly when working with substrings, and providing a consistent interface for all string-like inputs. However, these benefits come with an important responsibility: you must ensure the underlying string data outlives any views that reference it.

By using `string_view` appropriately, you can significantly improve the performance of string-heavy code without sacrificing readability or safety. It has quickly become an essential tool in the modern C++ programmer's toolkit.