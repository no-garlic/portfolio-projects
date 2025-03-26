# Smart Pointers in Modern C++: std::unique_ptr, std::shared_ptr, and std::weak_ptr

## Introduction

Memory management has always been one of the most challenging aspects of C++ programming. Before C++11, developers were responsible for manually allocating and deallocating memory using `new` and `delete`, which often led to memory leaks, dangling pointers, and double-deletion errors. Smart pointers were introduced as a solution to these problems. They encapsulate raw pointers within class objects that manage the lifetime of the pointed-to resource, automatically releasing memory when it's no longer needed.

C++11 standardized three key smart pointer types in the `<memory>` header:

1. `std::unique_ptr` - For exclusive ownership
2. `std::shared_ptr` - For shared ownership
3. `std::weak_ptr` - For non-owning references to resources managed by `std::shared_ptr`

This article provides a comprehensive guide to these smart pointers, their usage patterns, implementation details, and best practices.

## std::unique_ptr

### Concept and Purpose

`std::unique_ptr` implements exclusive ownership semantics. At any given time, exactly one `unique_ptr` instance owns the underlying resource. When that `unique_ptr` is destroyed or reassigned, the resource is automatically deleted. This makes `unique_ptr` perfect for:

- Managing resources that should never be shared
- Implementing RAII (Resource Acquisition Is Initialization) pattern
- Transferring ownership of resources
- Representing exclusive ownership in class member variables

### Basic Usage

```cpp
#include <iostream>
#include <memory>

int main() {
    // Creating a unique_ptr
    std::unique_ptr<int> ptr1(new int(42));
    
    // Better way (since C++14): Using make_unique
    auto ptr2 = std::make_unique<int>(42);
    
    // Accessing the managed object
    std::cout << "Value: " << *ptr2 << std::endl;
    *ptr2 = 100;
    std::cout << "New value: " << *ptr2 << std::endl;
    
    // Getting the raw pointer (be careful!)
    int* raw_ptr = ptr2.get();
    std::cout << "Raw pointer value: " << *raw_ptr << std::endl;
    
    // No need to delete - destruction happens automatically
    // when ptr1 and ptr2 go out of scope
}
```

### Ownership Transfer

A key feature of `unique_ptr` is that it cannot be copied, but it can be moved, which transfers ownership:

```cpp
#include <iostream>
#include <memory>
#include <vector>

std::unique_ptr<int> createValue() {
    return std::make_unique<int>(42);
}

void consumeValue(std::unique_ptr<int> ptr) {
    std::cout << "Consumed value: " << *ptr << std::endl;
    // ptr will be automatically destroyed when this function returns
}

int main() {
    // Transfer ownership from function return value
    auto ptr = createValue();
    
    // Transfer ownership to function
    consumeValue(std::move(ptr));
    
    // ptr is now nullptr
    if (!ptr) {
        std::cout << "ptr is now nullptr" << std::endl;
    }
    
    // Collecting unique_ptrs in a container
    std::vector<std::unique_ptr<int>> vec;
    vec.push_back(std::make_unique<int>(10));
    vec.push_back(std::make_unique<int>(20));
    
    // Moving from vector
    auto ptr2 = std::move(vec[0]);
    std::cout << "Moved from vector: " << *ptr2 << std::endl;
}
```

### Custom Deleters

You can customize how the managed resource is deleted by specifying a custom deleter:

```cpp
#include <iostream>
#include <memory>
#include <fstream>

void custom_deleter(int* p) {
    std::cout << "Custom deleting: " << *p << std::endl;
    delete p;
}

int main() {
    // Using a function as deleter
    {
        std::unique_ptr<int, void(*)(int*)> ptr(new int(42), custom_deleter);
    } // Calls custom_deleter here
    
    // Using a lambda as deleter
    {
        auto lambda_deleter = [](int* p) {
            std::cout << "Lambda deleting: " << *p << std::endl;
            delete p;
        };
        
        std::unique_ptr<int, decltype(lambda_deleter)> ptr(new int(100), lambda_deleter);
    } // Calls lambda_deleter here
    
    // Real-world example: auto-closing file
    {
        auto file_deleter = [](std::FILE* fp) { 
            std::cout << "Closing file automatically" << std::endl;
            std::fclose(fp); 
        };
        
        std::unique_ptr<std::FILE, decltype(file_deleter)> 
            fp(std::fopen("example.txt", "w"), file_deleter);
        
        if (fp) {
            std::fputs("Hello, world!", fp.get());
        }
    } // File automatically closed here
}
```

### Working with Arrays

`std::unique_ptr` has specialized support for arrays:

```cpp
#include <iostream>
#include <memory>

int main() {
    // Managing an array
    std::unique_ptr<int[]> arr(new int[5]{1, 2, 3, 4, 5});
    
    // Using make_unique for arrays (C++14)
    auto arr2 = std::make_unique<int[]>(5);
    
    // Accessing elements
    for (int i = 0; i < 5; ++i) {
        arr2[i] = i * 10;
        std::cout << "arr[" << i << "] = " << arr[i] << ", arr2[" << i << "] = " << arr2[i] << std::endl;
    }
    
    // No need to delete[] - handled automatically
}
```

## std::shared_ptr

### Concept and Purpose

`std::shared_ptr` implements shared ownership semantics. Multiple `shared_ptr` instances can point to the same resource, which is deleted only when the last `shared_ptr` owning it is destroyed. This makes `shared_ptr` ideal for:

- Resources that need to be shared across multiple objects
- Implementing reference-counted resources
- Resources with unknown or complex lifetime requirements

### Implementation Details

`std::shared_ptr` uses a control block that contains:
- A reference count tracking the number of `shared_ptr` instances
- A weak count tracking the number of `weak_ptr` instances
- The deleter function
- The allocator

This control block is allocated separately from the managed object, which introduces a level of indirection and some overhead.

### Basic Usage

```cpp
#include <iostream>
#include <memory>

int main() {
    // Creating a shared_ptr
    std::shared_ptr<int> ptr1(new int(42));
    
    // Better way: Using make_shared (more efficient)
    auto ptr2 = std::make_shared<int>(100);
    
    // Creating copies - both point to the same object
    std::shared_ptr<int> ptr3 = ptr2;
    std::shared_ptr<int> ptr4 = ptr3;
    
    // Modify through one pointer
    *ptr2 = 200;
    
    // All pointers see the change
    std::cout << "ptr2: " << *ptr2 << std::endl; // 200
    std::cout << "ptr3: " << *ptr3 << std::endl; // 200
    std::cout << "ptr4: " << *ptr4 << std::endl; // 200
    
    // Check reference count
    std::cout << "ptr2 use count: " << ptr2.use_count() << std::endl; // 3
    
    // Reset one pointer
    ptr3.reset();
    std::cout << "After reset, ptr2 use count: " << ptr2.use_count() << std::endl; // 2
    
    // Object is deleted when all shared_ptrs are gone
}
```

### Creating from unique_ptr

You can create a `shared_ptr` from a `unique_ptr`, which transfers ownership:

```cpp
#include <iostream>
#include <memory>

int main() {
    auto unique = std::make_unique<int>(42);
    
    // Transfer ownership to shared_ptr
    std::shared_ptr<int> shared = std::move(unique);
    
    // unique is now nullptr
    std::cout << "unique is null: " << (unique == nullptr) << std::endl;
    std::cout << "shared value: " << *shared << std::endl;
    std::cout << "shared use count: " << shared.use_count() << std::endl;
}
```

### Custom Deleters

Similar to `unique_ptr`, you can specify custom deleters:

```cpp
#include <iostream>
#include <memory>

struct NetworkResource {
    int id;
    NetworkResource(int i) : id(i) { 
        std::cout << "NetworkResource " << id << " created" << std::endl; 
    }
    ~NetworkResource() { 
        std::cout << "NetworkResource " << id << " destroyed normally" << std::endl; 
    }
};

void network_deleter(NetworkResource* p) {
    std::cout << "Custom deleting NetworkResource " << p->id << std::endl;
    delete p;
}

int main() {
    // Using custom deleter with shared_ptr
    {
        std::shared_ptr<NetworkResource> res1(new NetworkResource(1), network_deleter);
        
        // Copy the shared_ptr - deleter is part of the control block
        auto res2 = res1;
        
        std::cout << "Resource use count: " << res1.use_count() << std::endl;
    } // Custom deleter called when both pointers are destroyed
    
    // Using lambda deleter
    {
        auto lambda_deleter = [](NetworkResource* p) {
            std::cout << "Lambda deleting NetworkResource " << p->id << std::endl;
            delete p;
        };
        
        std::shared_ptr<NetworkResource> res(new NetworkResource(2), lambda_deleter);
    } // Lambda deleter called here
}
```

### Aliasing Constructor

`std::shared_ptr` provides an aliasing constructor that creates a shared pointer that shares ownership with another shared pointer but points to a different object:

```cpp
#include <iostream>
#include <memory>

struct Person {
    std::string name;
    int age;
    
    Person(const std::string& n, int a) : name(n), age(a) {
        std::cout << "Person created: " << name << std::endl;
    }
    
    ~Person() {
        std::cout << "Person destroyed: " << name << std::endl;
    }
};

int main() {
    // Create a shared_ptr to Person
    auto person = std::make_shared<Person>("Alice", 30);
    
    // Create a shared_ptr to the age member, shares ownership with person
    std::shared_ptr<int> age(person, &person->age);
    
    std::cout << "Name: " << person->name << std::endl;
    std::cout << "Age via person: " << person->age << std::endl;
    std::cout << "Age via age ptr: " << *age << std::endl;
    
    // Modify through the aliased pointer
    *age = 31;
    std::cout << "Modified age: " << person->age << std::endl;
    
    // Both pointers share ownership
    std::cout << "person use count: " << person.use_count() << std::endl; // 2
    
    // When person is reset, the Person object remains alive
    // because age still shares ownership
    person.reset();
    std::cout << "After person reset, age still valid: " << *age << std::endl;
    std::cout << "age use count: " << age.use_count() << std::endl;
    
    // Only when age is also destroyed will the Person be deleted
}
```

### Performance Considerations

While `std::shared_ptr` is very useful, it does come with some overhead:

1. **Memory Overhead**: Each `shared_ptr` requires a control block
2. **Atomic Operations**: Reference counting uses atomic operations for thread safety
3. **Initialization Cost**: Two allocations when using `new` directly, one with `make_shared`

Always prefer `std::make_shared` over direct constructor usage when possible:

```cpp
// Less efficient: two allocations (object + control block)
std::shared_ptr<int> ptr1(new int(42));

// More efficient: single allocation for both object and control block
auto ptr2 = std::make_shared<int>(42);
```

## std::weak_ptr

### Concept and Purpose

`std::weak_ptr` provides a non-owning "weak reference" to an object managed by `std::shared_ptr`. It doesn't affect the reference count and doesn't prevent the object from being destroyed. `weak_ptr` is designed to solve specific problems:

1. Breaking circular references in `shared_ptr` that would cause memory leaks
2. Caching resources without extending their lifetime
3. Observer pattern implementations where the observer shouldn't keep the subject alive

### Basic Usage

```cpp
#include <iostream>
#include <memory>

int main() {
    // Create a shared_ptr
    auto shared = std::make_shared<int>(42);
    std::cout << "shared use count: " << shared.use_count() << std::endl; // 1
    
    // Create a weak_ptr from it
    std::weak_ptr<int> weak = shared;
    std::cout << "After weak creation, shared use count: " << shared.use_count() << std::endl; // Still 1
    
    // To use a weak_ptr, we must convert it to a shared_ptr first
    if (auto temp = weak.lock()) {
        std::cout << "Value: " << *temp << std::endl;
        std::cout << "shared use count during lock: " << shared.use_count() << std::endl; // 2
    }
    std::cout << "shared use count after lock: " << shared.use_count() << std::endl; // Back to 1
    
    // Checking if weak_ptr is expired
    std::cout << "Is weak expired? " << weak.expired() << std::endl; // 0 (false)
    
    // Reset the shared_ptr
    shared.reset();
    std::cout << "Is weak expired after shared reset? " << weak.expired() << std::endl; // 1 (true)
    
    // Try to lock an expired weak_ptr
    if (auto temp = weak.lock()) {
        std::cout << "This won't print" << std::endl;
    } else {
        std::cout << "weak_ptr is expired, couldn't lock" << std::endl;
    }
}
```

### Solving Circular References

One of the main uses of `weak_ptr` is breaking circular references:

```cpp
#include <iostream>
#include <memory>
#include <string>
#include <vector>

// Forward declaration
class Person;

// A class that holds a collection of Person objects
class Club {
private:
    std::string name;
    std::vector<std::shared_ptr<Person>> members;
public:
    Club(const std::string& n) : name(n) {
        std::cout << "Club '" << name << "' created" << std::endl;
    }
    
    ~Club() {
        std::cout << "Club '" << name << "' destroyed" << std::endl;
    }
    
    void addMember(const std::shared_ptr<Person>& person) {
        members.push_back(person);
    }
    
    const std::string& getName() const { return name; }
};

// A Person belongs to a Club
class Person {
private:
    std::string name;
    
    // This would create a circular reference
    // std::shared_ptr<Club> club;
    
    // Using weak_ptr breaks the circular reference
    std::weak_ptr<Club> club;
    
public:
    Person(const std::string& n) : name(n) {
        std::cout << "Person '" << name << "' created" << std::endl;
    }
    
    ~Person() {
        std::cout << "Person '" << name << "' destroyed" << std::endl;
    }
    
    void joinClub(const std::shared_ptr<Club>& c) {
        club = c;
    }
    
    void showClub() const {
        if (auto c = club.lock()) {
            std::cout << name << " is a member of " << c->getName() << std::endl;
        } else {
            std::cout << name << " doesn't belong to any club" << std::endl;
        }
    }
};

int main() {
    // Create a scope to demonstrate destruction
    {
        // Create a club
        auto chess_club = std::make_shared<Club>("Chess Club");
        
        // Create some people
        auto alice = std::make_shared<Person>("Alice");
        auto bob = std::make_shared<Person>("Bob");
        
        // Make them join the club
        alice->joinClub(chess_club);
        bob->joinClub(chess_club);
        
        // Add them as members in the club
        chess_club->addMember(alice);
        chess_club->addMember(bob);
        
        // Show club membership
        alice->showClub();
        bob->showClub();
        
        std::cout << "\nLeaving scope - everything should be properly destroyed\n" << std::endl;
    }
    // Without weak_ptr, there would be a memory leak due to circular references
}
```

### Observer Pattern Implementation

`weak_ptr` is perfect for implementing the observer pattern:

```cpp
#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <algorithm>

// Forward declaration
class Observer;

// Subject that can be observed
class Subject {
    std::string name;
    int value;
    std::vector<std::weak_ptr<Observer>> observers;

public:
    Subject(const std::string& n) : name(n), value(0) {
        std::cout << "Subject '" << name << "' created" << std::endl;
    }
    
    ~Subject() {
        std::cout << "Subject '" << name << "' destroyed" << std::endl;
    }
    
    void addObserver(const std::shared_ptr<Observer>& observer) {
        observers.push_back(observer);
    }
    
    void removeObserver(const std::shared_ptr<Observer>& observer);
    
    void setValue(int v) {
        value = v;
        notifyObservers();
    }
    
    int getValue() const { return value; }
    const std::string& getName() const { return name; }
    
    void notifyObservers();
    
    // Clean up expired observers
    void cleanUp() {
        observers.erase(
            std::remove_if(observers.begin(), observers.end(),
                [](const std::weak_ptr<Observer>& wptr) { return wptr.expired(); }),
            observers.end()
        );
    }
};

// Observer that monitors subjects
class Observer {
    std::string name;
    
public:
    Observer(const std::string& n) : name(n) {
        std::cout << "Observer '" << name << "' created" << std::endl;
    }
    
    ~Observer() {
        std::cout << "Observer '" << name << "' destroyed" << std::endl;
    }
    
    void update(Subject* subject) {
        std::cout << "Observer '" << name << "' notified: Subject '" 
                  << subject->getName() << "' has new value " 
                  << subject->getValue() << std::endl;
    }
    
    const std::string& getName() const { return name; }
};

void Subject::notifyObservers() {
    // Clean up any expired observers and notify valid ones
    auto it = observers.begin();
    while (it != observers.end()) {
        if (auto obs = it->lock()) {
            obs->update(this);
            ++it;
        } else {
            it = observers.erase(it);
        }
    }
}

void Subject::removeObserver(const std::shared_ptr<Observer>& observer) {
    observers.erase(
        std::remove_if(observers.begin(), observers.end(),
            [&observer](const std::weak_ptr<Observer>& wptr) {
                auto sp = wptr.lock();
                return !sp || sp == observer;
            }),
        observers.end()
    );
}

int main() {
    // Create a subject
    auto temperature = std::make_shared<Subject>("Temperature Sensor");
    
    // Create a scope for some observers
    {
        auto display1 = std::make_shared<Observer>("Living Room Display");
        auto display2 = std::make_shared<Observer>("Kitchen Display");
        
        // Register observers
        temperature->addObserver(display1);
        temperature->addObserver(display2);
        
        // Change the value, should notify both observers
        temperature->setValue(22);
        
        std::cout << "\nLeaving inner scope - some observers will be destroyed\n" << std::endl;
    }
    
    // Clean up expired observers
    temperature->cleanUp();
    
    // This notification should not cause any issues, despite some observers being destroyed
    temperature->setValue(23);
    
    // Create another observer
    auto display3 = std::make_shared<Observer>("Bedroom Display");
    temperature->addObserver(display3);
    
    // Final update with the new observer
    temperature->setValue(24);
    
    std::cout << "\nEnd of program - everything will be cleaned up\n" << std::endl;
}
```

## Best Practices for Smart Pointers

### When to Use Each Type

1. **std::unique_ptr**:
   - For exclusive ownership
   - For implementing PIMPL idiom (Pointer to Implementation)
   - As a class member to manage exclusive resources
   - As a return value to transfer ownership
   - As the default choice when a smart pointer is needed

2. **std::shared_ptr**:
   - When ownership is shared among multiple objects
   - When you don't know which owner will be last
   - For cyclic data structures (along with weak_ptr)
   - When memory overhead and atomic operations are acceptable

3. **std::weak_ptr**:
   - To break circular references in shared_ptr
   - For observer pattern implementations
   - For caching where you don't want to extend the object's lifetime
   - When you need to check if an object still exists

### General Guidelines

1. **Prefer make_* Functions**:
   ```cpp
   // Prefer this
   auto ptr = std::make_unique<MyClass>(arg1, arg2);
   auto shared = std::make_shared<MyClass>(arg1, arg2);
   
   // Over this
   std::unique_ptr<MyClass> ptr(new MyClass(arg1, arg2));
   std::shared_ptr<MyClass> shared(new MyClass(arg1, arg2));
   ```

2. **Pass Smart Pointers Correctly**:
   ```cpp
   // Pass by value when ownership transfer is intended
   void takeOwnership(std::unique_ptr<Resource> resource);
   
   // Pass by reference when no ownership transfer is needed
   void useResource(const std::unique_ptr<Resource>& resource);
   
   // For shared_ptr, pass by value to increment reference count
   void shareOwnership(std::shared_ptr<Resource> resource);
   
   // Just need access? Pass raw pointer
   void justUseResource(Resource* resource);
   ```

3. **Don't Create Unnecessary shared_ptr**:
   ```cpp
   void processWidget(std::shared_ptr<Widget> widget) {
       // Implementation
   }
   
   int main() {
       auto w = std::make_shared<Widget>();
       
       // Good: passes shared_ptr by value
       processWidget(w);
       
       // Bad: creates temporary shared_ptr, less efficient
       processWidget(std::shared_ptr<Widget>(w.get()));
   }
   ```

4. **Use get() Carefully**:
   ```cpp
   auto ptr = std::make_unique<int>(42);
   
   // Dangerous - may lead to double delete if legacy_function takes ownership
   int* raw = ptr.get();
   legacy_function(raw);
   
   // Safe if legacy_function just uses the pointer
   legacy_function(ptr.get());
   ```

5. **Reset Before Reassignment**:
   ```cpp
   std::shared_ptr<LargeObject> global_object = std::make_shared<LargeObject>();
   
   void changeGlobalObject() {
       // Explicit reset before reassignment can help in some cases
       // by destroying the old object earlier
       global_object.reset();
       global_object = std::make_shared<LargeObject>();
   }
   ```

## Conclusion

Smart pointers are one of the most significant additions to modern C++, fundamentally changing how we manage resources. By adopting `std::unique_ptr`, `std::shared_ptr`, and `std::weak_ptr`, developers can write safer, more expressive code with fewer memory leaks and resource management bugs.

The three types of smart pointers provide different ownership semantics to address various scenarios:

- `std::unique_ptr` for exclusive ownership with zero overhead compared to raw pointers
- `std::shared_ptr` for shared ownership through reference counting
- `std::weak_ptr` for non-owning references that don't prevent resource deletion

By understanding the strengths, limitations, and appropriate use cases for each type, you can dramatically improve the safety and clarity of your C++ code. Smart pointers allow you to express ownership semantics directly in your API design, making code more self-documenting and reducing the cognitive burden of tracking resource lifetimes manually.