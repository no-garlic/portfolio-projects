# Lambda Captures by Move in Modern C++

## Introduction

Prior to C++14, lambda captures in C++ had significant limitations. You could only capture variables from the enclosing scope by value (`[x]`) or by reference (`[&x]`), but there was no direct way to move objects into the lambda closure. This restriction created inefficiencies when working with move-only types like `std::unique_ptr` or when you wanted to avoid expensive copies of large objects. C++14 introduced init-capture (also known as generalized lambda capture), which revolutionized how we can initialize lambda captures. This article explores the powerful technique of lambda captures by move, explaining its syntax, applications, and best practices.

## Understanding Init-Capture Syntax

The init-capture syntax, introduced in C++14, allows you to initialize a new variable in the lambda capture list rather than just capturing an existing variable. The general form is:

```cpp
[new_variable = expression] { /* lambda body */ }
```

When combined with `std::move()`, this enables moving resources into the lambda:

```cpp
[captured_var = std::move(original_var)] { /* lambda body */ }
```

This creates a new variable `captured_var` within the lambda's closure that takes ownership of the resource from `original_var` through move semantics.

## Basic Example: Moving a Unique Pointer

Let's start with a common use case - capturing a `std::unique_ptr` in a lambda:

```cpp
#include <iostream>
#include <memory>
#include <functional>

std::function<void()> createTask() {
    // A resource we want to use in our lambda
    auto resource = std::make_unique<int>(42);
    
    // Pre-C++14 approach would fail to compile:
    // return [resource] { std::cout << *resource << std::endl; };  // Error!
    
    // C++14 solution: move the unique_ptr into the lambda
    return [r = std::move(resource)] {
        if (r) {
            std::cout << "Resource value: " << *r << std::endl;
        }
    };
    
    // At this point, resource is null because ownership was transferred
}

int main() {
    auto task = createTask();
    task();  // Prints: Resource value: 42
    
    // We can call the lambda multiple times
    task();  // Still prints: Resource value: 42
    
    return 0;
}
```

In this example, `resource` is a `std::unique_ptr` that cannot be copied. The move capture transfers ownership of the managed object into the lambda's closure.

## Capturing Multiple Values with Move Semantics

You can move multiple objects into a lambda in the same capture list:

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <memory>

int main() {
    std::string heavy_string(1000000, 'x');
    std::vector<int> large_vector(100000, 42);
    auto unique_resource = std::make_unique<double>(3.14159);
    
    auto lambda = [
        s = std::move(heavy_string),
        v = std::move(large_vector),
        r = std::move(unique_resource)
    ] {
        std::cout << "String size: " << s.size() << std::endl;
        std::cout << "Vector size: " << v.size() << std::endl;
        std::cout << "Unique resource value: " << *r << std::endl;
    };
    
    // Original variables are in moved-from state
    std::cout << "Original string size after move: " << heavy_string.size() << std::endl;
    std::cout << "Original vector size after move: " << large_vector.size() << std::endl;
    std::cout << "Original unique_ptr valid: " << (unique_resource ? "yes" : "no") << std::endl;
    
    // Execute the lambda
    lambda();
    
    return 0;
}
```

This example demonstrates moving multiple resources into a lambda, avoiding expensive copies of large objects and enabling the capture of move-only types.

## Combining Different Capture Methods

You can combine move captures with regular value and reference captures:

```cpp
#include <iostream>
#include <memory>
#include <string>

int main() {
    int regular_value = 100;
    int& reference_value = regular_value;
    std::string heavy_data(1000000, 'x');
    auto unique_resource = std::make_unique<int>(42);
    
    auto lambda = [
        regular_value,                       // Capture by value (copy)
        &reference_value,                    // Capture by reference
        moved_data = std::move(heavy_data),  // Capture by move
        resource = std::move(unique_resource) // Capture move-only type
    ] {
        std::cout << "Regular value: " << regular_value << std::endl;
        std::cout << "Reference value: " << reference_value << std::endl;
        std::cout << "Moved data size: " << moved_data.size() << std::endl;
        std::cout << "Resource value: " << *resource << std::endl;
        
        // Modifying the reference affects the original variable
        reference_value += 10;
    };
    
    lambda();
    
    // Demonstrate that the reference was modified
    std::cout << "After lambda, regular_value = " << regular_value << std::endl;
    
    return 0;
}
```

## Move Capture with Computed Values

You can use expressions in the init-capture to initialize the captured variable with a computed value:

```cpp
#include <iostream>
#include <memory>
#include <vector>
#include <algorithm>

int main() {
    std::vector<int> data = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    
    // Capture a computed subset of data by moving it into a new vector
    auto lambda = [
        even_numbers = [&data] {
            std::vector<int> result;
            std::copy_if(data.begin(), data.end(), 
                        std::back_inserter(result),
                        [](int x) { return x % 2 == 0; });
            return result;
        }()  // Immediately invoke the lambda to compute the value
    ] {
        std::cout << "Even numbers: ";
        for (int num : even_numbers) {
            std::cout << num << " ";
        }
        std::cout << std::endl;
    };
    
    lambda();  // Prints: Even numbers: 2 4 6 8 10
    
    return 0;
}
```

In this example, we compute a subset of data as part of the capture initialization. The inner lambda is immediately invoked to create the vector that's moved into the outer lambda's capture.

## Using Move Capture with Asynchronous Operations

Move captures are particularly useful with asynchronous programming:

```cpp
#include <iostream>
#include <memory>
#include <string>
#include <future>
#include <thread>
#include <chrono>

class Database {
public:
    explicit Database(std::string connection_string) 
        : connection_string_(std::move(connection_string)) {
        std::cout << "Database constructed with connection: " 
                  << connection_string_ << std::endl;
    }
    
    ~Database() {
        std::cout << "Database destroyed" << std::endl;
    }
    
    std::string query(const std::string& sql) const {
        // Simulate query execution
        std::cout << "Executing query on " << connection_string_ << ": " 
                  << sql << std::endl;
        return "query_result";
    }
    
private:
    std::string connection_string_;
};

std::future<std::string> async_query(std::string sql) {
    auto db = std::make_unique<Database>("server:port/database");
    
    // Move the database connection into the lambda
    return std::async(std::launch::async, [db = std::move(db), sql = std::move(sql)] {
        // Simulate work
        std::this_thread::sleep_for(std::chrono::seconds(1));
        return db->query(sql);
    });
}

int main() {
    auto future = async_query("SELECT * FROM users");
    
    std::cout << "Query dispatched asynchronously" << std::endl;
    std::cout << "Result: " << future.get() << std::endl;
    
    return 0;
}
```

This example demonstrates how move capture simplifies resource management in asynchronous operations by transferring ownership of a database connection to the async task.

## Move Capture with mutable Lambdas

When combined with the `mutable` keyword, you can modify the moved objects within the lambda:

```cpp
#include <iostream>
#include <vector>
#include <string>

int main() {
    std::vector<int> data = {1, 2, 3, 4, 5};
    std::string message = "Original message";
    
    auto modify_lambda = [
        vec = std::move(data),
        msg = std::move(message)
    ] () mutable {
        // We can modify the captured variables because of 'mutable'
        vec.push_back(6);
        msg += " - Modified!";
        
        std::cout << "Inside lambda - Vector size: " << vec.size() << std::endl;
        std::cout << "Inside lambda - Message: " << msg << std::endl;
    };
    
    // Original variables are in moved-from state
    std::cout << "Original vector size after move: " << data.size() << std::endl;
    std::cout << "Original message after move: '" << message << "'" << std::endl;
    
    // First call
    modify_lambda();
    
    // Second call - notice the variables retain their modified state
    modify_lambda();
    
    return 0;
}
```

## Best Practices and Considerations

### 1. Always Check Moved-From Objects

Remember that after moving from an object, it's left in a valid but unspecified state. Don't assume anything about the value of the original variable after the move.

```cpp
auto resource = std::make_unique<int>(42);
auto lambda = [r = std::move(resource)] { /* ... */ };

// Don't use resource after moving from it without first checking
if (resource) {  // This will be false
    std::cout << *resource << std::endl;  // Undefined behavior if executed
}
```

### 2. Prefer Move Capture for Expensive or Move-Only Types

Use move captures when:
- Working with move-only types like `std::unique_ptr`
- Dealing with large objects where copying would be expensive
- You don't need the original object afterward

### 3. Avoid Unnecessary Moves

Don't use move captures for small, trivially copyable types:

```cpp
int x = 42;
// Unnecessary and no more efficient than [x]
auto lambda = [x_moved = std::move(x)] { /* ... */ }; 
```

### 4. Be Careful with Dangling References

If you move from an object but keep a reference to it, be aware of potential dangling references:

```cpp
std::string data = "Hello";
std::string& ref = data;

auto lambda = [moved_data = std::move(data)] { /* ... */ };

// ref now references a moved-from string, which is valid but content is unspecified
std::cout << "Ref after move: " << ref << std::endl;  // Legal but unpredictable
```

## Common Patterns

### Creating Closures with Resources

Move capture is excellent for creating closures that own resources:

```cpp
#include <iostream>
#include <memory>
#include <functional>

class Resource {
public:
    explicit Resource(int id) : id_(id) {
        std::cout << "Resource " << id_ << " created" << std::endl;
    }
    
    ~Resource() {
        std::cout << "Resource " << id_ << " destroyed" << std::endl;
    }
    
    void use() const {
        std::cout << "Using resource " << id_ << std::endl;
    }
    
private:
    int id_;
};

std::function<void()> create_resource_user() {
    auto resource = std::make_unique<Resource>(42);
    
    // Return a lambda that owns the resource
    return [r = std::move(resource)] {
        if (r) {
            r->use();
        }
    };
}

int main() {
    {
        auto resource_user = create_resource_user();
        std::cout << "Resource user created" << std::endl;
        
        resource_user();  // Using resource 42
    }
    
    std::cout << "End of scope - resource_user will be destroyed" << std::endl;
    // Resource 42 destroyed when resource_user is destroyed
    
    return 0;
}
```

### Implementing Move-Only Callbacks

You can use move capture to implement callbacks that can only be moved, not copied:

```cpp
#include <iostream>
#include <memory>
#include <utility>
#include <vector>

// A move-only callback type
class MoveOnlyCallback {
public:
    template<typename F>
    MoveOnlyCallback(F&& func) 
        : impl_(std::make_unique<Model<F>>(std::forward<F>(func))) {}
    
    // Allow move construction
    MoveOnlyCallback(MoveOnlyCallback&&) = default;
    MoveOnlyCallback& operator=(MoveOnlyCallback&&) = default;
    
    // Disallow copying
    MoveOnlyCallback(const MoveOnlyCallback&) = delete;
    MoveOnlyCallback& operator=(const MoveOnlyCallback&) = delete;
    
    void operator()() const {
        impl_->call();
    }
    
private:
    struct Concept {
        virtual ~Concept() = default;
        virtual void call() const = 0;
    };
    
    template<typename F>
    struct Model : Concept {
        F func_;
        explicit Model(F&& func) : func_(std::move(func)) {}
        void call() const override { func_(); }
    };
    
    std::unique_ptr<Concept> impl_;
};

class EventSystem {
public:
    void add_callback(MoveOnlyCallback callback) {
        callbacks_.push_back(std::move(callback));
    }
    
    void trigger_event() {
        for (const auto& callback : callbacks_) {
            callback();
        }
    }
    
private:
    std::vector<MoveOnlyCallback> callbacks_;
};

int main() {
    EventSystem events;
    
    // Create a resource
    auto resource = std::make_unique<int>(42);
    
    // Add a callback that takes ownership of the resource
    events.add_callback([r = std::move(resource)] {
        std::cout << "Callback using resource: " << *r << std::endl;
    });
    
    // Trigger the event
    events.trigger_event();
    
    return 0;
}
```

## Conclusion

Lambda captures by move, introduced in C++14 through init-capture syntax, significantly enhance the power and flexibility of C++ lambdas. This feature enables efficient transfer of ownership of resources into lambda closures, supports move-only types, and prevents unnecessary copies of large objects. By using the `[captured_var = std::move(original_var)]` syntax, you can create more efficient, expressive code, particularly in scenarios involving resource management, asynchronous programming, and complex data handling. As with all move semantics in C++, remember to be mindful of the state of moved-from objects and follow best practices to avoid subtle bugs. This powerful feature is an essential part of modern C++ programming that helps create more efficient and safer code.