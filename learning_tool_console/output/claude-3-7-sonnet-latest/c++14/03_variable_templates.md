# Variable Templates in C++14: A Powerful Addition to Template Metaprogramming

## Introduction

C++14 introduced a significant extension to C++'s template system called variable templates. Before C++14, templates could be used to create generic classes, functions, and alias declarations, but there was no direct way to define templated variables. The addition of variable templates filled this gap, allowing developers to define variables that are parameterized by type or value, similar to how function templates parameterize functions. This article explores variable templates in depth, their syntax, use cases, best practices, and how they can improve your C++ code.

## Understanding Variable Templates

A variable template is a variable definition that is parameterized by a set of template parameters. The syntax mirrors that of class and function templates but applies to variable declarations:

```cpp
template<typename T>
constexpr T pi = T(3.1415926535897932385);
```

In this example, `pi` is a variable template that can be instantiated with different types. When used, the compiler generates a separate variable for each type used in the instantiation:

```cpp
double d = pi<double>;       // pi<double> is 3.14159...
float f = pi<float>;         // pi<float> is 3.14159...
long double ld = pi<long double>; // pi<long double> is 3.14159...
```

The template parameter `T` is used both as the type of the variable and to convert the literal value to the appropriate type through the `T(...)` constructor syntax.

## Syntax and Basic Usage

The general syntax of a variable template is:

```cpp
template<parameter-list>
[constexpr] type-name variable-name = initialization;
```

Where:
- `parameter-list` is the list of template parameters, which can include type parameters, non-type parameters, or template template parameters
- `constexpr` is optional and indicates the variable can be evaluated at compile time
- `type-name` is the type of the variable (which can depend on the template parameters)
- `variable-name` is the name of the template
- `initialization` is the initializer for the variable

Here's another example using a non-type template parameter:

```cpp
template<int N>
constexpr double power_of_two = N > 0 ? 2.0 * power_of_two<N-1> : 1.0;
```

This recursive template definition computes powers of two at compile time:

```cpp
double x = power_of_two<4>;  // 16.0
double y = power_of_two<10>; // 1024.0
```

## Use Cases for Variable Templates

### 1. Mathematical Constants with Type Safety

One of the most straightforward applications of variable templates is defining mathematical constants that automatically adapt to different numeric types:

```cpp
template<typename T>
constexpr T pi = T(3.1415926535897932385);

template<typename T>
constexpr T e = T(2.7182818284590452353);

template<typename T>
constexpr T golden_ratio = T(1.6180339887498948482);

// Usage
auto area = pi<double> * radius * radius;
auto compound_interest = principal * std::pow(e<float>, rate * time);
auto aesthetic_ratio = golden_ratio<long double>;
```

This approach ensures that constants are used with the appropriate precision for the calculation, reducing potential errors from type conversions.

### 2. Type Traits and Compile-Time Information

Variable templates are excellent for defining type traits and compile-time information about types:

```cpp
template<typename T>
constexpr bool is_integral_v = std::is_integral<T>::value;

template<typename T>
constexpr bool is_floating_point_v = std::is_floating_point<T>::value;

template<typename T>
constexpr std::size_t alignment_v = alignof(T);

// Usage
static_assert(is_integral_v<int>, "int must be integral");
static_assert(!is_floating_point_v<char>, "char must not be floating point");
static_assert(alignment_v<double> >= 4, "double must be aligned to at least 4 bytes");
```

In fact, C++17 standardized many of these with the `_v` suffix for type traits, inspired by this pattern enabled by variable templates.

### 3. Default Values That Depend on Type

Variable templates allow for specifying default values that depend on the type:

```cpp
template<typename T>
constexpr T default_epsilon = T(0.0001);

template<>
constexpr float default_epsilon<float> = 0.0001f;

template<>
constexpr double default_epsilon<double> = 0.00000001;

// Usage
template<typename T>
bool almost_equal(T a, T b, T epsilon = default_epsilon<T>) {
    return std::abs(a - b) < epsilon;
}
```

### 4. Compile-Time Lookup Tables

Variable templates can be used to create compile-time lookup tables:

```cpp
template<int N>
constexpr int factorial = N * factorial<N-1>;

template<>
constexpr int factorial<0> = 1;

// Usage
constexpr int fact5 = factorial<5>; // 120
```

## Advanced Techniques with Variable Templates

### Combining with Other Template Features

Variable templates can be combined with variadic templates, SFINAE, and other template features:

```cpp
// Variadic template variable for maximum value
template<typename T, T... Values>
constexpr T static_max = std::max({Values...});

// Usage
constexpr int max_value = static_max<int, 1, 5, 3, 7, 2>; // 7

// SFINAE with variable templates
template<typename T>
constexpr bool has_begin_method_v = 
    std::is_same_v<decltype(std::declval<T>().begin()), 
                   typename T::iterator>;

// Type-dependent initialization with SFINAE
template<typename T, 
         typename = std::enable_if_t<std::is_arithmetic_v<T>>>
constexpr T init_val = T(0);

template<typename T, 
         typename = std::enable_if_t<std::is_pointer_v<T>>,
         typename = void>  // Extra parameter to avoid redefinition
constexpr T init_val<T> = nullptr;
```

### Template Parameter Packs

Variable templates can work with parameter packs for advanced compile-time computations:

```cpp
// Calculate the sum of a pack of numbers at compile time
template<typename T, T... Values>
constexpr T sum_v = (... + Values);

// Usage
constexpr int sum = sum_v<int, 1, 2, 3, 4, 5>; // 15

// Count occurrences of a type in a parameter pack
template<typename T, typename... Args>
constexpr std::size_t count_type_v = (std::is_same_v<T, Args> + ...);

// Usage
constexpr auto count = count_type_v<int, float, int, char, int>; // 2
```

## Variable Templates vs. Alternative Approaches

Before variable templates, similar functionality was achieved through other means, each with limitations:

### Static Class Members vs. Variable Templates

Prior to C++14, a common approach was to use static members in class templates:

```cpp
// Before C++14
template<typename T>
struct constants {
    static constexpr T pi = T(3.1415926535897932385);
};

// Usage
double circle_area = constants<double>::pi * r * r;
```

Variable templates provide a cleaner syntax:

```cpp
// C++14 and later
template<typename T>
constexpr T pi = T(3.1415926535897932385);

// Usage
double circle_area = pi<double> * r * r;
```

### Function Templates vs. Variable Templates

Another approach was to use function templates that return constants:

```cpp
// Before C++14
template<typename T>
constexpr T get_pi() {
    return T(3.1415926535897932385);
}

// Usage
double circle_area = get_pi<double>() * r * r;
```

Variable templates eliminate the need for the function call syntax, making the code more readable.

## Best Practices for Variable Templates

### 1. Use `constexpr` When Possible

Making variable templates `constexpr` enables compile-time evaluation, which can improve performance and catch errors earlier:

```cpp
template<typename T>
constexpr T pi = T(3.1415926535897932385);  // Good: enables compile-time evaluation
```

### 2. Explicitly Convert Numeric Literals

When defining numeric constants, explicitly convert to the template type to avoid precision loss:

```cpp
// Good: explicit conversion to type T
template<typename T>
constexpr T pi = T(3.1415926535897932385);

// Bad: implicit conversion may lose precision
template<typename T>
constexpr T pi_bad = 3.1415926535897932385;
```

### 3. Provide Specializations for Specific Types When Needed

Specialize variable templates for types that require special handling:

```cpp
template<typename T>
constexpr T epsilon = T(0.000001);

// Specialized for float to use a larger epsilon
template<>
constexpr float epsilon<float> = 0.0001f;
```

### 4. Consider Naming Conventions

For variable templates that mirror existing type traits, consider using the `_v` suffix consistent with the standard library:

```cpp
template<typename T>
constexpr bool is_safe_numeric_cast_v = 
    (std::is_arithmetic_v<T> && std::is_arithmetic_v<U> && 
     sizeof(T) >= sizeof(U)) || std::is_convertible_v<U, T>;
```

## Examples of Variable Templates in the Standard Library

The C++ Standard Library has embraced variable templates since C++17, particularly for type traits:

```cpp
// C++17 variable templates for type traits
namespace std {
    template<typename T>
    inline constexpr bool is_void_v = is_void<T>::value;
    
    template<typename T>
    inline constexpr bool is_null_pointer_v = is_null_pointer<T>::value;
    
    template<typename T>
    inline constexpr bool is_integral_v = is_integral<T>::value;
    
    // Many more...
}
```

## Practical Example: Unit Conversion Library

Here's a practical example of using variable templates to create a unit conversion library:

```cpp
#include <iostream>
#include <type_traits>

// Unit conversion factors as variable templates
template<typename T>
constexpr T meters_to_feet = T(3.28084);

template<typename T>
constexpr T liters_to_gallons = T(0.264172);

template<typename T>
constexpr T celsius_to_fahrenheit_factor = T(9.0/5.0);

template<typename T>
constexpr T celsius_to_fahrenheit_offset = T(32);

// Conversion functions using variable templates
template<typename T, 
         typename = std::enable_if_t<std::is_floating_point_v<T>>>
T meters_to_feet_convert(T meters) {
    return meters * meters_to_feet<T>;
}

template<typename T, 
         typename = std::enable_if_t<std::is_floating_point_v<T>>>
T liters_to_gallons_convert(T liters) {
    return liters * liters_to_gallons<T>;
}

template<typename T, 
         typename = std::enable_if_t<std::is_floating_point_v<T>>>
T celsius_to_fahrenheit(T celsius) {
    return celsius * celsius_to_fahrenheit_factor<T> + celsius_to_fahrenheit_offset<T>;
}

int main() {
    // Works with different floating point types
    float distance_meters_f = 10.0f;
    double distance_meters_d = 10.0;
    
    std::cout << distance_meters_f << " meters = " 
              << meters_to_feet_convert(distance_meters_f) << " feet (float)\n";
    
    std::cout << distance_meters_d << " meters = " 
              << meters_to_feet_convert(distance_meters_d) << " feet (double)\n";
    
    // Temperature conversion
    float temp_c = 20.0f;
    double temp_c_d = 20.0;
    
    std::cout << temp_c << "°C = " 
              << celsius_to_fahrenheit(temp_c) << "°F (float)\n";
    
    std::cout << temp_c_d << "°C = " 
              << celsius_to_fahrenheit(temp_c_d) << "°F (double)\n";
    
    return 0;
}
```

## Conclusion

Variable templates represent a significant enhancement to C++'s template system, filling a gap that existed before C++14. They provide a clean, intuitive syntax for defining constants and values that depend on types, enabling more elegant and type-safe code. From mathematical constants to type traits, variable templates have become an essential tool in modern C++ programming.

By leveraging variable templates, developers can create more expressive code with less boilerplate, particularly when working with generic programming and compile-time computations. The ability to specialize variable templates for specific types adds flexibility, while the integration with other template features makes them a powerful addition to any C++ programmer's toolkit.

As you integrate variable templates into your code, remember to use them primarily for simple, widely-used constants and type-dependent values where readability and type safety are important. Combined with other modern C++ features, variable templates help create cleaner, more maintainable, and more efficient code.