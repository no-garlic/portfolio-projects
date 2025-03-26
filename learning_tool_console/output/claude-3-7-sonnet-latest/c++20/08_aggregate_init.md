# Default Member Initializers in Aggregates: New C++20 Functionality

## Introduction

C++20 introduced a significant enhancement to aggregate types by allowing them to have default member initializers while still maintaining their status as aggregates. This feature bridges a long-standing gap in C++ that forced developers to choose between the simplicity of aggregate initialization and the convenience of default member values. In this article, we'll explore this new capability in detail, covering its syntax, semantics, and practical applications through numerous code examples.

## Understanding Aggregates in C++

Before diving into the new functionality, let's briefly review what makes a type an aggregate in C++. An aggregate is a class (struct, class, or union) that has:

- No user-declared or inherited constructors
- No private or protected non-static data members
- No virtual functions
- No virtual, private, or protected base classes

Aggregates can be initialized with aggregate initialization syntax, which is a clean and simple way to initialize members:

```cpp
struct Point {
    int x;
    int y;
};

// Aggregate initialization
Point p1 = {1, 2}; // x=1, y=2
```

## The Problem Before C++20

Prior to C++20, if you wanted to provide default values for members, you had to choose between two less-than-ideal approaches:

1. **Use constructors** - which would make your type non-aggregate:

```cpp
struct Point {
    int x;
    int y;
    
    // Adding a constructor makes this non-aggregate
    Point() : x(0), y(0) {}
    Point(int x_val, int y_val) : x(x_val), y(y_val) {}
};

// Now you must use constructor syntax
Point p1;          // x=0, y=0
Point p2(5, 10);   // x=5, y=10
// Point p3 = {1, 2}; // Still works, but not aggregate initialization
```

2. **Leave it as aggregate but implement default values elsewhere** - which could lead to scattered initialization logic:

```cpp
struct Point {
    int x;
    int y;
};

// Default initialization happens outside the struct
Point createDefaultPoint() {
    return {0, 0};
}

Point p1 = createDefaultPoint();
```

Neither approach was entirely satisfactory, especially when you wanted both the convenience of default values and the simplicity of aggregate initialization.

## C++20 Solution: Default Member Initializers in Aggregates

C++20 allows you to have default member initializers in aggregates. This means you can define default values directly within the class definition, and the type will still be considered an aggregate:

```cpp
struct Point {
    int x = 0;  // Default member initializer
    int y = 0;  // Default member initializer
};

// Still an aggregate, supports aggregate initialization
Point p1 = {};      // x=0, y=0
Point p2 = {5};     // x=5, y=0
Point p3 = {5, 10}; // x=5, y=10
```

## How Default Initialization Works with Aggregate Initialization

When using aggregate initialization, the rules are straightforward:

1. If you provide a value for a member, that value is used
2. If you don't provide a value for a member, the default member initializer is used
3. If neither is provided, the member is default-initialized

This leads to flexible and intuitive initialization:

```cpp
struct Config {
    std::string hostname = "localhost";
    int port = 8080;
    bool use_ssl = false;
    int timeout_ms = 30000;
};

// Use all defaults
Config c1 = {};  // hostname="localhost", port=8080, use_ssl=false, timeout_ms=30000

// Override just what you need
Config c2 = {"example.com"};  // hostname="example.com", others use defaults
Config c3 = {"api.example.org", 443, true};  // Custom hostname, port, and SSL setting
```

## Interaction with Designated Initializers

C++20 also introduced designated initializers, which work excellently with default member initializers:

```cpp
struct Configuration {
    std::string server = "main";
    int threads = 4;
    bool logging = false;
    std::string log_path = "/tmp/log.txt";
};

// Using designated initializers with default member initializers
Configuration config = {
    .threads = 8,
    .logging = true
    // server and log_path use their defaults
};
```

This combination allows for extremely readable and maintainable code.

## Complex Examples with Nested Aggregates

Default member initializers work seamlessly with nested aggregates:

```cpp
struct Address {
    std::string street = "Main St";
    std::string city = "Anytown";
    std::string state = "CA";
    std::string zip = "12345";
};

struct Person {
    std::string name;
    int age = 30;
    Address address;  // Nested aggregate with its own defaults
    std::vector<std::string> hobbies = {"Reading", "Hiking"};
};

// Various initialization patterns
Person p1 = {"Alice"}; // Uses default age, address, and hobbies
Person p2 = {"Bob", 25}; // Custom name and age, default address and hobbies
Person p3 = {"Charlie", 40, {"123 Oak St", "Someville"}}; // Partially initializing nested address
```

## Mixing with Non-Default-Initialized Members

You can mix members with and without default initializers:

```cpp
struct Employee {
    int id;  // No default - must be provided
    std::string name;  // No default - must be provided
    std::string department = "General";
    double salary = 50000.0;
    bool is_manager = false;
};

// id and name must be provided
Employee e1 = {101, "John Doe"};  // Other fields use defaults
Employee e2 = {202, "Jane Smith", "Engineering", 85000.0};  // is_manager uses default
```

## Default Initialization vs. Value Initialization

It's important to understand the difference between different forms of initialization:

```cpp
struct Widget {
    int x = 42;
    double y;  // No default initializer
};

// Default initialization (doesn't use member default initializers)
Widget w1;  // x is indeterminate, y is indeterminate

// Value initialization (uses member default initializers)
Widget w2 = {};  // x=42, y=0.0
Widget w3{};     // x=42, y=0.0
```

## Technical Details and Edge Cases

### Inheritance and Default Member Initializers

Default member initializers work with inheritance as you would expect:

```cpp
struct Base {
    int base_value = 100;
};

struct Derived : Base {
    int derived_value = 200;
};

Derived d = {};  // base_value=100, derived_value=200
Derived d2 = {50};  // base_value=50, derived_value=200
Derived d3 = {50, 150};  // base_value=50, derived_value=150
```

### Order of Initialization

Default member initializers are applied in the order of declaration, which can be important if there are dependencies between members:

```cpp
struct Example {
    int x = 10;
    int y = x * 2;  // y is initialized to 20, based on x's value
};

Example e = {};  // x=10, y=20
Example e2 = {5};  // x=5, y=20 (not 10 - y's initializer uses the default formula)
```

### Arrays as Members

Default member initializers work with array members too:

```cpp
struct ArrayContainer {
    int values[3] = {1, 2, 3};
    char name[10] = {'C', '+', '+', '2', '0'};
};

ArrayContainer a = {};  // all default values
ArrayContainer b = {{5, 6, 7}};  // values={5,6,7}, name uses default
```

## Best Practices

1. **Use default member initializers for sensible defaults:**
   Default values should represent the most common use case or a safe fallback.

2. **Document the defaults:**
   Make sure users of your code can easily identify what the default values are.

3. **Be mindful of performance:**
   Default member initializers can lead to double initialization if not used carefully:

```cpp
struct PerfSensitive {
    std::vector<int> large_data = std::vector<int>(1000000);  // Default initializer
};

// This will initialize large_data twice!
PerfSensitive p = {std::vector<int>(2000000)};
```

4. **Consider using designated initializers for clarity:**
   When only initializing a few members, designated initializers can make code more maintainable.

5. **Be careful with dependencies between members:**
   Remember that default member initializers are evaluated when the object is created, not at compile time.

## Comparing with Traditional Approaches

Let's compare the new approach with traditional methods:

```cpp
// Pre-C++20 approach with constructor
struct LegacyConfig {
    std::string host;
    int port;
    bool debug;
    
    LegacyConfig() : host("localhost"), port(8080), debug(false) {}
};

// C++20 approach with default member initializers
struct ModernConfig {
    std::string host = "localhost";
    int port = 8080;
    bool debug = false;
};

// Usage comparison
LegacyConfig lc1;  // Constructor initializes values
ModernConfig mc1 = {};  // Aggregate initialization with defaults
ModernConfig mc2 = {"example.com"};  // Override just host
```

The modern approach is more concise, offers more flexibility in initialization, and maintains the benefits of aggregate types.

## Conclusion

Default member initializers in aggregates represent a significant improvement in C++20, eliminating a long-standing pain point in the language. This feature enables developers to define sensible defaults within the class definition while preserving the simplicity and flexibility of aggregate initialization. Combined with other C++20 features like designated initializers, this creates a powerful, expressive syntax for creating and initializing objects. As you modernize your C++ codebase, incorporating default member initializers in aggregates can lead to more maintainable, self-documenting, and robust code.