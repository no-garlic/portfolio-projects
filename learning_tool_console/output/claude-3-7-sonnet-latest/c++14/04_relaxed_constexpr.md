# Relaxed constexpr in C++14: Bringing Compile-Time Programming to the Next Level

## Introduction

In C++11, the `constexpr` specifier was introduced as a revolutionary feature that enabled compile-time computation. However, the initial implementation came with significant restrictions that limited its practical use. C++14 dramatically expanded the capabilities of `constexpr` functions by relaxing these constraints, allowing for loops, conditionals, multiple return statements, and variable mutations within constexpr functions. This enhancement transformed compile-time programming from a niche technique to a powerful tool for performance optimization and code safety. This article explores the relaxed constexpr features introduced in C++14, providing comprehensive examples and best practices.

## Background: constexpr in C++11

To appreciate the improvements in C++14, let's first understand the limitations of C++11's constexpr functions:

```cpp
// C++11 constexpr functions were limited to a single return statement
constexpr int factorial(int n) {
    return n <= 1 ? 1 : n * factorial(n - 1);
}

// This worked because the entire function is a single expression
// using the ternary conditional operator
```

C++11 constexpr functions were essentially restricted to:
- A single return statement
- No loops (for, while, do-while)
- No local variable declarations (except those with no initializers)
- No if-else statements or switch statements
- No mutation of variables (including function parameters)

These restrictions meant that many algorithms that could conceptually be evaluated at compile time required convoluted recursive solutions or could not be implemented as constexpr at all.

## Relaxed constexpr in C++14

C++14 significantly relaxed these constraints, allowing constexpr functions to contain:

1. Loops (for, while, do-while)
2. Multiple return statements
3. If-else and switch statements
4. Local variable declarations with initializers
5. Mutation of variables (except static or thread_local variables)

Let's examine each of these features with examples.

### 1. Loops in constexpr Functions

C++14 allows all standard loop constructs within constexpr functions:

```cpp
// Factorial using a loop instead of recursion
constexpr int factorial(int n) {
    int result = 1;
    for (int i = 2; i <= n; ++i) {
        result *= i;
    }
    return result;
}

// Usage remains the same
static_assert(factorial(5) == 120, "Factorial calculation incorrect");

// This allows other loop types as well
constexpr int sum_up_to(int n) {
    int sum = 0;
    int i = 1;
    while (i <= n) {
        sum += i;
        ++i;
    }
    return sum;
}

static_assert(sum_up_to(10) == 55, "Sum calculation incorrect");
```

### 2. Multiple Return Statements

C++14 allows multiple return points in a constexpr function:

```cpp
constexpr int absolute_value(int n) {
    if (n >= 0) {
        return n;  // First possible return point
    } else {
        return -n; // Second possible return point
    }
}

static_assert(absolute_value(-5) == 5, "Absolute value calculation incorrect");
static_assert(absolute_value(5) == 5, "Absolute value calculation incorrect");
```

### 3. Conditional Statements

Full support for if-else and switch statements makes constexpr functions more readable and versatile:

```cpp
constexpr int max_of_three(int a, int b, int c) {
    if (a >= b && a >= c) {
        return a;
    } else if (b >= a && b >= c) {
        return b;
    } else {
        return c;
    }
}

static_assert(max_of_three(5, 10, 3) == 10, "Max calculation incorrect");

// Switch statements are also allowed
constexpr int day_of_week_to_number(const char* day) {
    switch (day[0]) {
        case 'M': return 1; // Monday
        case 'T': 
            if (day[1] == 'u') return 2; // Tuesday
            else return 4;               // Thursday
        case 'W': return 3; // Wednesday
        case 'F': return 5; // Friday
        case 'S':
            if (day[1] == 'a') return 6; // Saturday
            else return 7;               // Sunday
        default: return 0;   // Invalid
    }
}

// Cannot directly use string literals in static_assert comparison
// But can use it in constexpr contexts
```

### 4. Local Variable Declarations and Mutations

C++14 allows declaring and modifying local variables within constexpr functions:

```cpp
constexpr bool is_prime(int n) {
    if (n <= 1) return false;
    if (n <= 3) return true;
    
    // Check if n is divisible by 2 or 3
    if (n % 2 == 0 || n % 3 == 0) return false;
    
    // Local variable declaration and mutation
    int i = 5;
    while (i * i <= n) {
        if (n % i == 0 || n % (i + 2) == 0) {
            return false;
        }
        i += 6;  // Variable mutation
    }
    
    return true;
}

static_assert(is_prime(11), "11 is prime");
static_assert(!is_prime(15), "15 is not prime");
```

### 5. Complex Examples of Relaxed constexpr

Let's see some more sophisticated examples that showcase the power of relaxed constexpr:

#### Computing Fibonacci Numbers

```cpp
constexpr int fibonacci(int n) {
    int a = 0, b = 1;
    
    if (n == 0) return a;
    if (n == 1) return b;
    
    for (int i = 2; i <= n; ++i) {
        int temp = a + b;
        a = b;
        b = temp;
    }
    
    return b;
}

static_assert(fibonacci(0) == 0, "fibonacci(0) should be 0");
static_assert(fibonacci(1) == 1, "fibonacci(1) should be 1");
static_assert(fibonacci(10) == 55, "fibonacci(10) should be 55");
```

#### Binary Search in Compile Time

```cpp
template <typename T, size_t N>
constexpr int binary_search(const T (&arr)[N], T value, int low, int high) {
    while (low <= high) {
        int mid = low + (high - low) / 2;
        
        if (arr[mid] == value) {
            return mid;  // Found the element
        }
        
        if (arr[mid] < value) {
            low = mid + 1;  // Look in the right half
        } else {
            high = mid - 1;  // Look in the left half
        }
    }
    
    return -1;  // Element not found
}

constexpr int my_array[] = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19};
static_assert(binary_search(my_array, 11, 0, 9) == 5, 
              "Binary search failed to find 11 at index 5");
static_assert(binary_search(my_array, 12, 0, 9) == -1, 
              "Binary search incorrectly found value 12");
```

#### String Manipulation at Compile Time

```cpp
constexpr bool is_palindrome(const char* str, int length) {
    int left = 0;
    int right = length - 1;
    
    while (left < right) {
        if (str[left] != str[right]) {
            return false;
        }
        ++left;
        --right;
    }
    
    return true;
}

// Helper to compute length
constexpr int str_length(const char* str) {
    int length = 0;
    while (str[length] != '\0') {
        ++length;
    }
    return length;
}

// Combined function
constexpr bool check_palindrome(const char* str) {
    return is_palindrome(str, str_length(str));
}

static_assert(check_palindrome("radar"), "radar is a palindrome");
static_assert(check_palindrome("level"), "level is a palindrome");
static_assert(!check_palindrome("hello"), "hello is not a palindrome");
```

## Practical Applications of Relaxed constexpr

### 1. Performance Optimization

Relaxed constexpr enables more complex calculations to be performed at compile time, reducing runtime overhead:

```cpp
// Lookup tables generated at compile time
constexpr int generate_square(int n) {
    return n * n;
}

constexpr int generate_squares_table(int max) {
    int result[100] = {0};  // Note: fixed size for demonstration
    for (int i = 0; i < max && i < 100; ++i) {
        result[i] = generate_square(i);
    }
    return result[max-1];  // Return last value for verification
}

static_assert(generate_squares_table(10) == 81, "Square table generation incorrect");
```

### 2. Type Traits and Metaprogramming

The relaxed constexpr rules significantly simplify template metaprogramming:

```cpp
template <typename T>
constexpr bool is_power_of_two(T value) {
    if (value <= 0) return false;
    
    while (value > 1) {
        if (value % 2 != 0) {
            return false;
        }
        value /= 2;
    }
    
    return true;
}

static_assert(is_power_of_two(16), "16 is a power of 2");
static_assert(!is_power_of_two(18), "18 is not a power of 2");
```

### 3. Safe Enumeration Conversion

Constexpr can be used for compile-time validation of enum conversions:

```cpp
enum class Color { Red, Green, Blue };
enum class TrafficLight { Red, Yellow, Green };

constexpr bool is_valid_color_conversion(Color color, TrafficLight& result) {
    switch (color) {
        case Color::Red:
            result = TrafficLight::Red;
            return true;
        case Color::Green:
            result = TrafficLight::Green;
            return true;
        default:
            return false;  // No matching traffic light color
    }
}

constexpr bool test_conversion() {
    TrafficLight light;
    bool result = is_valid_color_conversion(Color::Red, light);
    return result && (light == TrafficLight::Red);
}

static_assert(test_conversion(), "Color conversion test failed");
```

## Limitations and Best Practices

### Remaining Limitations in C++14

While C++14 constexpr is much more flexible than C++11, some limitations remain:

1. No try-catch blocks within constexpr functions
2. No undefined behavior allowed in constexpr evaluation
3. No allocation/deallocation of memory (new/delete)
4. No modification of static or thread_local variables
5. No virtual function calls
6. Some standard library functions are not constexpr

### Best Practices

1. **Start simple**: Begin with functions that have obvious compile-time value, like mathematical computations.

2. **Keep constexpr functions pure**: Avoid side effects, even if technically possible.

3. **Test at compile time**: Use static_assert to verify your constexpr functions.

4. **Provide constexpr and non-constexpr paths**: For complex functions, consider:

```cpp
template <typename T>
constexpr T complex_calculation(T input) {
    if (std::is_constant_evaluated()) {
        // C++20 feature, but illustrates the point
        // Compile-time friendly implementation
        return compile_time_implementation(input);
    } else {
        // Potentially more optimized runtime implementation
        return runtime_implementation(input);
    }
}
```

5. **Be mindful of compile-time overhead**: Very complex constexpr evaluations can increase compilation time.

6. **Document constexpr guarantees**: Make it clear to users what conditions must be met for compile-time evaluation.

## Conclusion

The relaxed constexpr feature in C++14 represents a significant leap forward for compile-time programming in C++. By allowing loops, conditional statements, variable mutations, and multiple return statements, C++14 transformed constexpr from a limited feature into a powerful tool for metaprogramming and optimization. This extended functionality enables clearer and more intuitive code while maintaining the performance benefits of compile-time evaluation. As C++ continues to evolve, constexpr capabilities have expanded even further in C++17 and C++20, building on these solid foundations provided by C++14.