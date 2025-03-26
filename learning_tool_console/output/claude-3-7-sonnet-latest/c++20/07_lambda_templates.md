# C++20 Lambda Improvements: Template Parameters in Lambda Expressions

## Introduction

Lambda expressions, introduced in C++11, have revolutionized how we write inline functions in C++. These anonymous function objects have steadily gained capabilities with each C++ standard iteration. C++14 brought generic lambdas with `auto` parameters, and C++17 added capture of `*this`. C++20 takes lambda functionality to the next level with several significant enhancements, with template parameters in lambdas being one of the most powerful additions.

This article explores how C++20 allows you to define explicit template parameters in lambda expressions, providing greater control and expressiveness compared to generic lambdas using `auto`. We'll examine the syntax, practical applications, and advantages of this feature through detailed examples.

## From Generic Lambdas to Templated Lambdas

Before diving into C++20's templated lambdas, let's briefly revisit generic lambdas from C++14:

```cpp
// C++14 generic lambda with auto parameter
auto genericLambda = [](auto x) { return x * 2; };
```

This lambda can accept any type that supports multiplication by 2. The compiler generates a template-like function call operator. However, generic lambdas have limitations:

1. Limited ability to enforce constraints on the `auto` parameters
2. No way to specify relationships between multiple type parameters
3. No way to use template-specific features like explicit specialization or fold expressions

C++20 addresses these limitations by allowing explicit template parameters:

```cpp
// C++20 templated lambda
auto templatedLambda = []<typename T>(T x) { return x * 2; };
```

## Syntax of Templated Lambdas

The general syntax for a templated lambda in C++20 is:

```cpp
auto lambda = []<template-parameter-list>(parameter-list) specifiers { body };
```

The template parameter list comes immediately after the capture clause and before the function parameters. Here's a more comprehensive example:

```cpp
auto lambda = []<typename T, typename U, int N>(T t, U u, std::array<T, N> arr) {
    // Function body
};
```

## Advantages of Templated Lambdas

### 1. Accessing Type Information

One of the most significant advantages of templated lambdas is the ability to access the actual type information:

```cpp
#include <iostream>
#include <type_traits>
#include <vector>

int main() {
    // Generic lambda (C++14)
    auto printGeneric = [](const auto& container) {
        // Cannot easily get the value_type of the container
        for (const auto& elem : container) {
            std::cout << elem << " ";
        }
        std::cout << std::endl;
    };
    
    // Templated lambda (C++20)
    auto printTemplated = []<typename Container>(const Container& container) {
        // Can access the Container::value_type
        using ValueType = typename Container::value_type;
        std::cout << "Container of " << typeid(ValueType).name() << " elements: ";
        for (const ValueType& elem : container) {
            std::cout << elem << " ";
        }
        std::cout << std::endl;
    };
    
    std::vector<int> vec = {1, 2, 3, 4, 5};
    printGeneric(vec);     // Outputs: 1 2 3 4 5
    printTemplated(vec);   // Outputs: Container of i elements: 1 2 3 4 5
    
    return 0;
}
```

### 2. Perfect Forwarding

Templated lambdas simplify perfect forwarding patterns:

```cpp
#include <iostream>
#include <utility>

// Before C++20: awkward perfect forwarding with generic lambda
auto forwardBefore = [](auto&&... args) {
    return [&](auto&& f) -> decltype(auto) {
        return f(std::forward<decltype(args)>(args)...);
    };
};

// C++20: clean perfect forwarding with templated lambda
auto forwardAfter = []<typename... Args>(Args&&... args) {
    return [&]<typename F>(F&& f) -> decltype(auto) {
        return std::forward<F>(f)(std::forward<Args>(args)...);
    };
};

void foo(int x, double y) {
    std::cout << "x: " << x << ", y: " << y << std::endl;
}

int main() {
    auto f1 = forwardBefore(42, 3.14);
    auto f2 = forwardAfter(42, 3.14);
    
    f1(foo);  // Outputs: x: 42, y: 3.14
    f2(foo);  // Outputs: x: 42, y: 3.14
    
    return 0;
}
```

### 3. Constraining Parameters with Concepts

C++20 concepts combine beautifully with templated lambdas:

```cpp
#include <iostream>
#include <concepts>
#include <type_traits>

template<typename T>
concept Numeric = std::is_arithmetic_v<T>;

int main() {
    // Constrained templated lambda using C++20 concepts
    auto add = []<Numeric T, Numeric U>(T a, U b) {
        return a + b;
    };
    
    std::cout << add(5, 3.14) << std::endl;       // Works: 8.14
    // std::cout << add("hello", 5) << std::endl;  // Compilation error: "hello" is not Numeric
    
    return 0;
}
```

### 4. Working with Template Template Parameters

Templated lambdas can even work with template template parameters:

```cpp
#include <iostream>
#include <vector>
#include <list>

int main() {
    // Lambda with template template parameter
    auto containerInfo = []<template<typename, typename...> class Container, 
                             typename T, typename... Args>
                          (const Container<T, Args...>& container) {
        std::cout << "Container size: " << container.size() << std::endl;
        std::cout << "Element type: " << typeid(T).name() << std::endl;
        if constexpr (std::is_same_v<Container<T, Args...>, std::vector<T>>) {
            std::cout << "This is a vector!" << std::endl;
        } else if constexpr (std::is_same_v<Container<T, Args...>, std::list<T>>) {
            std::cout << "This is a list!" << std::endl;
        }
    };
    
    std::vector<int> vec = {1, 2, 3};
    std::list<double> list = {1.1, 2.2, 3.3, 4.4};
    
    containerInfo(vec);
    std::cout << "-------------------" << std::endl;
    containerInfo(list);
    
    return 0;
}
```

### 5. Type Traits and SFINAE

Templated lambdas enable more expressive SFINAE patterns:

```cpp
#include <iostream>
#include <type_traits>
#include <vector>
#include <string>

int main() {
    // Lambda with SFINAE and type traits
    auto process = []<typename T>(const T& value) {
        if constexpr (std::is_integral_v<T>) {
            std::cout << "Processing integer: " << value * 2 << std::endl;
        } else if constexpr (std::is_floating_point_v<T>) {
            std::cout << "Processing float: " << value * 1.5 << std::endl;
        } else if constexpr (requires { typename T::value_type; }) {
            std::cout << "Processing container with " << value.size() << " elements" << std::endl;
        } else {
            std::cout << "Unknown type" << std::endl;
        }
    };
    
    process(42);                        // Integer
    process(3.14);                      // Float
    process(std::vector<int>{1, 2, 3}); // Container
    process(std::string("hello"));      // Container (string has value_type)
    
    return 0;
}
```

### 6. Recursive Lambdas

Templated lambdas can be used with recursive calls more cleanly:

```cpp
#include <iostream>
#include <vector>

int main() {
    // Recursive factorial using templated lambda
    auto factorial = []<typename T>(auto&& self, T n) -> T {
        if (n <= 1) return 1;
        return n * self(self, n - 1);
    };
    
    std::cout << "Factorial of 5: " << factorial(factorial, 5) << std::endl;
    
    // Recursive function to process nested vectors
    auto processNested = []<typename T>(auto&& self, const std::vector<T>& vec, int depth = 0) {
        for (const auto& item : vec) {
            if constexpr (std::is_same_v<T, std::vector<typename T::value_type>>) {
                // If T is a vector, recurse deeper
                self(self, item, depth + 1);
            } else {
                // Print item with indentation based on depth
                for (int i = 0; i < depth; ++i) std::cout << "  ";
                std::cout << "- " << item << std::endl;
            }
        }
    };
    
    std::vector<std::vector<int>> nestedVec = {{1, 2}, {3, 4, 5}};
    processNested(processNested, nestedVec);
    
    return 0;
}
```

## Comparing Generic and Templated Lambdas

To illustrate when you might prefer a templated lambda over a generic one, let's compare implementations:

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <type_traits>

int main() {
    std::vector<int> numbers = {1, 2, 3, 4, 5};
    
    // Generic lambda
    auto sumGeneric = [](const auto& container) {
        decltype(container.front()) sum = {};
        for (const auto& elem : container) {
            sum += elem;
        }
        return sum;
    };
    
    // Templated lambda
    auto sumTemplated = []<typename Container>(const Container& container) {
        // Can explicitly define the sum type using value_type
        typename Container::value_type sum = {};
        for (const auto& elem : container) {
            sum += elem;
        }
        return sum;
    };
    
    std::cout << "Generic sum: " << sumGeneric(numbers) << std::endl;
    std::cout << "Templated sum: " << sumTemplated(numbers) << std::endl;
    
    // More complex example with SFINAE
    auto processContainerGeneric = [](const auto& container) {
        // Harder to use SFINAE or type traits effectively
        using Container = std::decay_t<decltype(container)>;
        using ValueType = typename Container::value_type;
        
        if constexpr (std::is_arithmetic_v<ValueType>) {
            std::cout << "Container of arithmetic values" << std::endl;
        } else {
            std::cout << "Container of non-arithmetic values" << std::endl;
        }
    };
    
    auto processContainerTemplated = []<typename Container>(const Container& container) {
        using ValueType = typename Container::value_type;
        
        if constexpr (std::is_arithmetic_v<ValueType>) {
            std::cout << "Container of arithmetic values" << std::endl;
        } else {
            std::cout << "Container of non-arithmetic values" << std::endl;
        }
    };
    
    std::vector<std::string> strings = {"hello", "world"};
    processContainerGeneric(numbers);   // Arithmetic
    processContainerGeneric(strings);   // Non-arithmetic
    processContainerTemplated(numbers); // Arithmetic
    processContainerTemplated(strings); // Non-arithmetic
    
    return 0;
}
```

## Advanced Use Cases

### 1. Higher-Order Functions

Templated lambdas are particularly useful for higher-order functions:

```cpp
#include <iostream>
#include <vector>
#include <algorithm>

int main() {
    // Higher-order function that returns a filtering lambda
    auto makeFilter = []<typename Predicate>(Predicate pred) {
        return [pred = std::move(pred)]<typename Container>(Container& container) {
            Container result;
            std::copy_if(container.begin(), container.end(), 
                         std::back_inserter(result), pred);
            return result;
        };
    };
    
    auto isEven = [](int n) { return n % 2 == 0; };
    auto filterEven = makeFilter(isEven);
    
    std::vector<int> numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    auto evenNumbers = filterEven(numbers);
    
    std::cout << "Even numbers: ";
    for (int n : evenNumbers) {
        std::cout << n << " ";
    }
    std::cout << std::endl;
    
    return 0;
}
```

### 2. Meta-Programming in Lambdas

Templated lambdas enable meta-programming techniques:

```cpp
#include <iostream>
#include <tuple>
#include <string>

// Function to print a tuple
template<typename... Args>
void printTuple(const std::tuple<Args...>& t) {
    auto printer = []<typename Tuple, std::size_t... I>(const Tuple& tuple, std::index_sequence<I...>) {
        ((std::cout << (I == 0 ? "" : ", ") << std::get<I>(tuple)), ...);
    };
    
    std::cout << "(";
    printer(t, std::index_sequence_for<Args...>{});
    std::cout << ")" << std::endl;
}

int main() {
    auto t = std::make_tuple(42, "hello", 3.14);
    printTuple(t);  // Outputs: (42, hello, 3.14)
    
    // Metaprogramming within a lambda to check if types are comparable
    auto areComparable = []<typename T, typename U>() {
        if constexpr (requires(T t, U u) { t < u; }) {
            return "Types are comparable";
        } else {
            return "Types are not comparable";
        }
    };
    
    std::cout << areComparable.template operator()<int, double>() << std::endl;
    std::cout << areComparable.template operator()<int, std::string>() << std::endl;
    
    return 0;
}
```

### 3. Variadic Template Parameters

Templated lambdas work seamlessly with parameter packs:

```cpp
#include <iostream>
#include <tuple>
#include <utility>

int main() {
    // Lambda to print any number of arguments of any type
    auto printAll = []<typename... Args>(Args&&... args) {
        ((std::cout << args << " "), ...);
        std::cout << std::endl;
    };
    
    printAll(1, "hello", 3.14, 'a');  // Outputs: 1 hello 3.14 a
    
    // Apply a function to each element of a tuple
    auto applyToTuple = []<typename Func, typename... Ts>(Func&& func, const std::tuple<Ts...>& tuple) {
        [&]<std::size_t... I>(std::index_sequence<I...>) {
            (func(std::get<I>(tuple)), ...);
        }(std::index_sequence_for<Ts...>{});
    };
    
    auto printItem = [](const auto& item) {
        std::cout << item << std::endl;
    };
    
    auto myTuple = std::make_tuple(42, "C++20", 3.14159);
    applyToTuple(printItem, myTuple);
    
    return 0;
}
```

## Best Practices

When working with templated lambdas in C++20, consider these best practices:

1. **Use templated lambdas when you need type information**:
   If you need to access template-specific features or type information, prefer templated lambdas over generic ones.

2. **Combine with concepts for better error messages**:
   Templated lambdas allow use of concepts for parameter constraints, leading to clearer error messages.

3. **Consider readability**:
   For simple cases where `auto` is clear enough, you might still prefer generic lambdas for brevity.

4. **Use for metaprogramming within lambdas**:
   Templated lambdas enable sophisticated metaprogramming techniques that weren't possible with generic lambdas.

5. **Remember template syntax**:
   When working with nested templated lambdas, you may need to use the `.template` syntax for dependent names.

## Conclusion

C++20's templated lambdas represent a significant advancement in C++'s functional programming capabilities. They bridge the gap between the convenience of lambda expressions and the flexibility of template programming, enabling more expressive, type-safe, and powerful code. By allowing explicit template parameters in lambda expressions, C++20 provides developers with greater control over type deduction, better access to type information, and improved support for meta-programming techniques.

Whether you're working on template metaprogramming, generic algorithms, or simply need more precise control over your lambda's behavior, C++20's templated lambdas offer a powerful tool that can lead to more concise, expressive, and robust code. As you incorporate this feature into your C++ toolkit, you'll discover new patterns and techniques that were previously difficult or impossible to express with lambdas alone.