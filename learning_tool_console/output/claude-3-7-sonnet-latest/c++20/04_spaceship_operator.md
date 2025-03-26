# C++20 Three-Way Comparison Operator (<=>): The Spaceship Operator

## Introduction

The C++20 standard introduced a significant addition to the language's comparison capabilities with the three-way comparison operator, commonly known as the "spaceship operator" due to its resemblance to a spaceship: `<=>`. This operator represents a paradigm shift in how comparisons are implemented in C++, addressing a long-standing issue: the tedious and error-prone task of manually defining all six comparison operators (`==`, `!=`, `<`, `<=`, `>`, `>=`) for custom types. The spaceship operator streamlines this process by providing a single operator that can generate the results for all relational comparisons, greatly reducing boilerplate code and potential inconsistencies.

## The Problem: Comparison Boilerplate

Before C++20, defining a complete set of comparison operators for a class was verbose and error-prone:

```cpp
class Version {
public:
    int major, minor, patch;
    
    bool operator==(const Version& other) const {
        return major == other.major && minor == other.minor && patch == other.patch;
    }
    
    bool operator!=(const Version& other) const {
        return !(*this == other);
    }
    
    bool operator<(const Version& other) const {
        if (major != other.major) return major < other.major;
        if (minor != other.minor) return minor < other.minor;
        return patch < other.patch;
    }
    
    bool operator<=(const Version& other) const {
        return *this < other || *this == other;
    }
    
    bool operator>(const Version& other) const {
        return !(*this <= other);
    }
    
    bool operator>=(const Version& other) const {
        return !(*this < other);
    }
};
```

This approach has several drawbacks:
- It's verbose and repetitive
- It's easy to introduce bugs (e.g., implementing `>` as `!(*this < other)` instead of `!(*this <= other)`)
- All operators must be updated if the comparison logic changes
- It's difficult to maintain consistency across all operators

## The Spaceship Operator Solution

The three-way comparison operator returns an ordering value rather than a boolean. This ordering can be used to derive all six comparison operations. C++20 provides three ordering types in the `<compare>` header:

- `std::strong_ordering`: For types with strict total ordering (like integers)
- `std::weak_ordering`: For types with equivalence rather than equality (like case-insensitive strings)
- `std::partial_ordering`: For types where not all values are comparable (like floating-point with NaN)

Each of these types can have one of the following values:
- `std::strong_ordering::less` / `std::weak_ordering::less` / `std::partial_ordering::less`
- `std::strong_ordering::equal` / `std::weak_ordering::equivalent` / `std::partial_ordering::equivalent`
- `std::strong_ordering::greater` / `std::weak_ordering::greater` / `std::partial_ordering::greater`
- `std::partial_ordering::unordered` (only for partial_ordering)

Here's how we can rewrite the Version class using the spaceship operator:

```cpp
#include <compare>

class Version {
public:
    int major, minor, patch;
    
    std::strong_ordering operator<=>(const Version& other) const {
        if (auto cmp = major <=> other.major; cmp != 0)
            return cmp;
        if (auto cmp = minor <=> other.minor; cmp != 0)
            return cmp;
        return patch <=> other.patch;
    }
    
    bool operator==(const Version& other) const = default;
};
```

That's it! The compiler will generate the other five operators based on these two. Note the use of C++20's if-with-initializer syntax, which improves readability and scoping.

## Auto-Generated Comparisons with `=default`

C++20 takes it even further by allowing you to default the three-way comparison operator:

```cpp
#include <compare>

class Version {
public:
    int major, minor, patch;
    
    auto operator<=>(const Version&) const = default;
};
```

With this minimal code, the compiler will:
1. Generate the three-way comparison by lexicographically comparing each member
2. Choose the appropriate return type based on the comparison category of the members
3. Generate all other comparison operators

This is incredibly powerful for simple data structures. The compiler-generated operators are also more efficient than manual implementations in most cases.

## Strong, Weak, and Partial Ordering

The three ordering types correspond to different semantics:

### Strong Ordering

Strong ordering implies a total order where `a == b` if and only if neither `a < b` nor `b < a`. Integer comparison is an example of strong ordering:

```cpp
int a = 5, b = 10;
auto result = a <=> b;  // std::strong_ordering::less
```

### Weak Ordering

Weak ordering represents equivalence rather than equality. Two objects may be equivalent (not less than each other) without being identical:

```cpp
#include <compare>
#include <string>
#include <cctype>

class CaseInsensitiveString {
    std::string text;
    
public:
    CaseInsensitiveString(std::string s) : text(std::move(s)) {}
    
    std::weak_ordering operator<=>(const CaseInsensitiveString& other) const {
        auto it1 = text.begin();
        auto it2 = other.text.begin();
        
        while (it1 != text.end() && it2 != other.text.end()) {
            char c1 = std::tolower(static_cast<unsigned char>(*it1));
            char c2 = std::tolower(static_cast<unsigned char>(*it2));
            
            if (c1 < c2) return std::weak_ordering::less;
            if (c1 > c2) return std::weak_ordering::greater;
            
            ++it1;
            ++it2;
        }
        
        if (it1 == text.end() && it2 == other.text.end())
            return std::weak_ordering::equivalent;
        return (it1 == text.end()) ? std::weak_ordering::less : std::weak_ordering::greater;
    }
    
    bool operator==(const CaseInsensitiveString& other) const {
        return (*this <=> other) == 0;
    }
};
```

Here, "Hello" and "hello" are equivalent but not identical.

### Partial Ordering

Partial ordering is for types where not all values can be ordered. The classic example is floating-point numbers with NaN values:

```cpp
#include <compare>

double a = 1.0, b = 2.0, nan = std::numeric_limits<double>::quiet_NaN();

auto result1 = a <=> b;   // std::partial_ordering::less
auto result2 = a <=> nan; // std::partial_ordering::unordered
auto result3 = nan <=> a; // std::partial_ordering::unordered
```

## Custom Comparisons with Different Types

The spaceship operator can be overloaded to handle comparisons between different types:

```cpp
#include <compare>
#include <string>
#include <string_view>

class Product {
    std::string name;
    int id;
    
public:
    Product(std::string n, int i) : name(std::move(n)), id(i) {}
    
    // Same-type comparison
    std::strong_ordering operator<=>(const Product& other) const {
        if (auto cmp = name <=> other.name; cmp != 0)
            return cmp;
        return id <=> other.id;
    }
    
    // Different-type comparison with string_view
    std::strong_ordering operator<=>(const std::string_view& other_name) const {
        if (auto cmp = name <=> other_name; cmp != 0)
            return cmp;
        // If names are equal, Product is greater (because it's more specific)
        return std::strong_ordering::greater;
    }
    
    // Make == consistent with <=>
    bool operator==(const Product& other) const = default;
    bool operator==(const std::string_view& other_name) const {
        return name == other_name;
    }
};
```

This allows for flexible comparisons like:

```cpp
Product p1("Apple", 1);
Product p2("Banana", 2);
std::string_view sv = "Apple";

bool b1 = p1 < p2;        // true (lexicographical comparison)
bool b2 = p1 <= sv;       // true (names are equal)
bool b3 = sv < p1;        // true (string_view compared to Product)
```

## The Rewrite Rules

When you define an `operator<=>`, the compiler uses rewrite rules to transform other comparison operators. For example:

- `a < b` becomes `(a <=> b) < 0`
- `a > b` becomes `(a <=> b) > 0`
- `a <= b` becomes `(a <=> b) <= 0`
- `a >= b` becomes `(a <=> b) >= 0`

However, `a == b` and `a != b` are not automatically rewritten based on `<=>`. If you want automatic generation of `==` and `!=`, you should define `operator==` as defaulted:

```cpp
bool operator==(const MyClass&) const = default;
```

## Practical Example: Sorting and Containers

The spaceship operator shines when using standard library containers and algorithms:

```cpp
#include <compare>
#include <vector>
#include <algorithm>
#include <iostream>

struct Employee {
    std::string name;
    int id;
    double salary;
    
    auto operator<=>(const Employee&) const = default;
};

int main() {
    std::vector<Employee> employees = {
        {"Alice", 101, 75000.0},
        {"Bob", 102, 70000.0},
        {"Alice", 103, 80000.0}
    };
    
    // Sort lexicographically (name, then id, then salary)
    std::sort(employees.begin(), employees.end());
    
    // Sort by salary
    std::sort(employees.begin(), employees.end(), 
              [](const Employee& a, const Employee& b) {
                  return a.salary < b.salary;
              });
    
    // Use in associative containers
    std::map<Employee, std::string> employeeInfo;
    employeeInfo[{"Alice", 101, 75000.0}] = "Senior Developer";
}
```

## Interaction with Legacy Code

Mixing spaceship operator with legacy code requires careful consideration:

```cpp
#include <compare>

class ModernClass {
public:
    int value;
    
    auto operator<=>(const ModernClass&) const = default;
};

class LegacyClass {
public:
    int value;
    
    bool operator<(const LegacyClass& other) const {
        return value < other.value;
    }
    
    bool operator==(const LegacyClass& other) const {
        return value == other.value;
    }
};

// Comparison between modern and legacy classes
std::strong_ordering operator<=>(const ModernClass& modern, const LegacyClass& legacy) {
    return modern.value <=> legacy.value;
}

// Make sure == is also defined for cross-type comparison
bool operator==(const ModernClass& modern, const LegacyClass& legacy) {
    return modern.value == legacy.value;
}
```

## Performance Considerations

The spaceship operator can improve performance by reducing the number of comparisons:

```cpp
#include <compare>
#include <chrono>
#include <vector>
#include <algorithm>
#include <iostream>

// Old-style comparison
class OldVersion {
public:
    int major, minor, patch;
    
    bool operator<(const OldVersion& other) const {
        if (major != other.major) return major < other.major;
        if (minor != other.minor) return minor < other.minor;
        return patch < other.patch;
    }
};

// New-style comparison
class NewVersion {
public:
    int major, minor, patch;
    
    auto operator<=>(const NewVersion&) const = default;
};

template<typename VersionType>
void benchmark() {
    std::vector<VersionType> versions(10000);
    
    // Fill with random versions
    for (auto& v : versions) {
        v.major = rand() % 10;
        v.minor = rand() % 100;
        v.patch = rand() % 1000;
    }
    
    auto start = std::chrono::high_resolution_clock::now();
    std::sort(versions.begin(), versions.end());
    auto end = std::chrono::high_resolution_clock::now();
    
    std::chrono::duration<double, std::milli> duration = end - start;
    std::cout << "Sort duration: " << duration.count() << " ms\n";
}
```

In many cases, the spaceship operator leads to more efficient code because:
1. It performs each member comparison only once
2. The compiler can optimize the defaulted version specifically
3. It avoids redundant evaluations of complex expressions

## Best Practices

When using the spaceship operator, consider these guidelines:

1. **Default when possible**: Use `=default` for simple data structures
2. **Be consistent**: If implementing `<=>` manually, also implement `==` or default it
3. **Choose the right ordering type**: Use the most restrictive that makes sense (prefer `strong_ordering` when possible)
4. **Be careful with floating-point**: Remember they require `partial_ordering`
5. **Consider compatibility**: Design cross-type comparisons carefully
6. **Mind the rewrite rules**: Understand how the compiler transforms comparison expressions

## Conclusion

The three-way comparison operator represents a significant step forward in C++ comparison semantics. It eliminates boilerplate code, reduces errors, and enables more expressive and maintainable code. By providing a single operator that handles all comparison logic, it simplifies the implementation of orderable types. Whether you're designing new types or refactoring existing code, the spaceship operator is a powerful addition to your C++ toolkit that aligns with modern C++'s emphasis on conciseness, correctness, and performance.