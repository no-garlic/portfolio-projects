# Explicitly Defaulted and Deleted Functions in Modern C++

## Introduction

C++11 introduced a powerful pair of mechanisms for controlling special member functions: explicitly defaulted and deleted functions. These features enable programmers to express their intentions clearly and precisely when it comes to the compiler-generated special member functions (constructors, destructors, copy/move operations) as well as preventing undesired implicit conversions or operator usages. These two language features—marked with `= default;` and `= delete;` syntax—significantly enhance code readability, expressiveness, and safety, while also enabling compiler optimizations that might otherwise be impossible.

## Explicitly Defaulted Functions (`= default;`)

### What Are Explicitly Defaulted Functions?

Explicitly defaulted functions tell the compiler to generate the default implementation for a special member function. Prior to C++11, if you wanted the compiler-generated version of a function but had to declare it for some reason, you had to provide an empty implementation, which could be less efficient than the compiler's default implementation.

The syntax is straightforward:

```cpp
return-type function-declaration = default;
```

This can be applied to:
- Default constructor
- Destructor
- Copy constructor
- Copy assignment operator
- Move constructor (C++11)
- Move assignment operator (C++11)

### When to Use Explicitly Defaulted Functions

Use `= default;` when:

1. You want to be explicit about your intentions to use the compiler-generated version.
2. You've declared a special member function that would otherwise suppress the automatic generation of one or more other special member functions.
3. You want to ensure the compiler-generated version is used, which might be more efficient than a manually implemented version.
4. You want to control where a function is defined (inline or out-of-line).

### Examples of Explicitly Defaulted Functions

#### Basic Usage Example

```cpp
class Widget {
public:
    // Explicitly defaulted default constructor
    Widget() = default;
    
    // Explicitly defaulted destructor
    ~Widget() = default;
    
    // Custom constructor that would suppress the default constructor
    // without the explicit default above
    Widget(int value) : value_(value) {}
    
private:
    int value_ = 0;
};
```

#### Controlling Copy and Move Operations

```cpp
class Resource {
public:
    Resource() = default;
    
    // Custom constructor
    Resource(const std::string& name) : name_(name) {}
    
    // Explicitly defaulted copy constructor
    Resource(const Resource&) = default;
    
    // Explicitly defaulted copy assignment
    Resource& operator=(const Resource&) = default;
    
    // Explicitly defaulted move constructor
    Resource(Resource&&) = default;
    
    // Explicitly defaulted move assignment
    Resource& operator=(Resource&&) = default;
    
private:
    std::string name_;
};
```

#### Out-of-Line Default Definition

You can also provide an out-of-line defaulted definition:

```cpp
class Widget {
public:
    Widget();
    ~Widget();
    
    // Other members...
};

// Out-of-line defaulted definitions
Widget::Widget() = default;
Widget::~Widget() = default;
```

This gives you control over which function definitions are included in your header files versus implementation files.

### Benefits of Explicitly Defaulted Functions

1. **Clarity**: Explicitly states your intent that you want the compiler-generated version.
2. **Performance**: The compiler may optimize defaulted functions better than manually implemented empty functions.
3. **Rule of Three/Five/Zero**: Helps maintain consistency when implementing special member functions.
4. **Maintainability**: Makes it clear which functions are compiler-generated and which are custom.

## Explicitly Deleted Functions (`= delete;`)

### What Are Explicitly Deleted Functions?

Explicitly deleted functions tell the compiler not to generate a particular function, and to emit an error if that function would be called. This provides a way to prevent certain operations by making them compile-time errors.

The syntax is:

```cpp
return-type function-declaration = delete;
```

### When to Use Explicitly Deleted Functions

Use `= delete;` when:

1. You want to prevent objects from being copied, moved, or default-constructed.
2. You want to prevent implicit type conversions that might lead to programming errors.
3. You want to disable certain overloads of a function.
4. You want to prevent heap allocation by deleting `operator new`.
5. You want to prevent usage of specific operators.

### Examples of Explicitly Deleted Functions

#### Preventing Copy and Move Operations

```cpp
class NonCopyable {
public:
    NonCopyable() = default;
    
    // Prevent copying
    NonCopyable(const NonCopyable&) = delete;
    NonCopyable& operator=(const NonCopyable&) = delete;
    
    // Allow moving
    NonCopyable(NonCopyable&&) = default;
    NonCopyable& operator=(NonCopyable&&) = default;
};
```

#### Preventing Default Construction

```cpp
class MandatoryInit {
public:
    // No default construction allowed
    MandatoryInit() = delete;
    
    // Must use this constructor
    explicit MandatoryInit(int value) : value_(value) {}
    
private:
    int value_;
};
```

#### Preventing Undesired Conversions

```cpp
class Number {
public:
    // Only accept int, not other types that convert to int
    Number(int value) : value_(value) {}
    
    // Prevent implicit conversion from double to avoid precision loss
    Number(double) = delete;
    
    // Prevent implicit conversion from char
    Number(char) = delete;
    
    // Prevent implicit conversion from bool
    Number(bool) = delete;
    
private:
    int value_;
};

void test() {
    Number n1(42);    // Fine
    Number n2(3.14);  // Error: call to deleted constructor
    Number n3('a');   // Error: call to deleted constructor
    Number n4(true);  // Error: call to deleted constructor
}
```

#### Preventing Function Overloads for Specific Types

```cpp
// Generic process function for any type
template<typename T>
void process(T value) {
    // Process most types...
}

// Delete overload for pointers to avoid dangerous behavior
template<typename T>
void process(T* value) = delete;

// Delete overload for C strings to avoid dangerous behavior
void process(char* value) = delete;
void process(const char* value) = delete;

void test() {
    int i = 42;
    process(i);       // OK
    process(&i);      // Error: call to deleted function
    
    char str[] = "hello";
    process(str);     // Error: call to deleted function
}
```

#### Preventing Heap Allocation

```cpp
class StackOnly {
public:
    StackOnly() = default;
    
    // Prevent heap allocation
    void* operator new(std::size_t) = delete;
    void* operator new[](std::size_t) = delete;
    void operator delete(void*) = delete;
    void operator delete[](void*) = delete;
};

void test() {
    StackOnly stackObj;           // OK
    StackOnly* pHeap = new StackOnly; // Error: call to deleted function
}
```

## Rules and Constraints

1. Only special member functions that would be implicitly declared by the compiler can be defaulted.
2. If you explicitly default a special member function that wouldn't be implicitly declared, or would be defined as deleted, the program is ill-formed.
3. A deleted function is implicitly inline.
4. Deleted functions participate in overload resolution and are only rejected if selected by the overload resolution process.
5. You can't delete regular (non-member) function templates, but you can delete specific instantiations.

## Best Practices

1. **Rule of Zero**: If you don't need to manually define any of the special member functions, don't define any of them.
2. **Rule of Five**: If you define or delete any of the copy constructor, copy assignment operator, move constructor, move assignment operator, or destructor, consider whether you should explicitly define or delete all five.
3. Be explicit about which operations are allowed and which are prohibited.
4. Use `= delete` for preventing problematic implicit conversions.
5. Prefer deleted functions over private undefined functions (pre-C++11 technique).
6. When defaulting special member functions, consider whether they should be defined inline (in the class definition) or out-of-line.

## Advanced Patterns

### Restricting Instantiation of Templates

```cpp
template<typename T>
class OnlyForIntegralTypes {
    // Disallow instantiation for non-integral types
    static_assert(std::is_integral<T>::value, "Only integral types allowed");
    
public:
    OnlyForIntegralTypes() = default;
    // ...
};

// Alternative approach using deleted constructor
template<typename T>
class OnlyForIntegralTypes2 {
public:
    OnlyForIntegralTypes2() = default;
    
    // Primary template is deleted
    template<typename U = T,
             typename = typename std::enable_if<!std::is_integral<U>::value>::type>
    OnlyForIntegralTypes2() = delete;
    
    // ...
};
```

### Preventing Inheritance

```cpp
class NonInheritable final {
public:
    NonInheritable() = default;
};

// Alternative approach for pre-C++11 compilers
class NonInheritable2 {
private:
    NonInheritable2() = default;
    friend class Factory; // Only Factory can create instances
};
```

### Ensuring Derived Classes Override Virtual Functions

```cpp
class Base {
public:
    virtual ~Base() = default;
    
    // Force derived classes to override this
    virtual void mustOverride() = 0;
    
    // Provide a default implementation that can be used
    virtual void canOverride() { /* default impl */ }
    
    // Prevent overriding of this method
    virtual void cannotOverride() final { /* implementation */ }
};

class Derived : public Base {
public:
    // Must implement this
    void mustOverride() override { /* implementation */ }
    
    // Optionally override this
    void canOverride() override { /* implementation */ }
    
    // Error: Cannot override final function
    // void cannotOverride() override { }
};
```

## Conclusion

Explicitly defaulted and deleted functions are powerful tools in modern C++ that allow programmers to express their intentions more clearly, prevent common programming errors, and enable compiler optimizations. By using `= default;` and `= delete;`, you can take control of special member functions and implicit conversions in a way that was not possible before C++11.

The `= default;` mechanism lets you explicitly request compiler-generated implementations when you would otherwise lose them due to the language rules, while `= delete;` allows you to prevent unwanted operations entirely with compile-time errors. Together, these features promote safer, more readable, and more efficient code—making them essential parts of the modern C++ programmer's toolkit.