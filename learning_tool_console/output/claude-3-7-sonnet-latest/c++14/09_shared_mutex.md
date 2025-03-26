# Understanding std::shared_timed_mutex in C++14

## Introduction

C++14 introduced an important addition to its threading library: the `std::shared_timed_mutex` class. This synchronization primitive addresses a common scenario in concurrent programming known as the readers-writers problem. In many applications, multiple threads may read shared data simultaneously without conflict, but write operations require exclusive access to maintain data integrity. Prior to C++14, developers typically had to choose between a standard mutex (which locks exclusively) or implement custom reader-writer locks. The `std::shared_timed_mutex` elegantly solves this problem by providing built-in support for both shared (read) and exclusive (write) locking modes.

## The Readers-Writers Problem

Before diving into the specifics of `std::shared_timed_mutex`, let's understand the problem it solves. The readers-writers problem occurs when multiple threads access shared resources with different access patterns:

- **Readers**: Multiple threads that only read shared data can operate concurrently without conflict.
- **Writers**: Threads that modify shared data need exclusive access to maintain consistency.

Traditional mutexes provide exclusive access, which is unnecessarily restrictive for read-only operations. This is inefficient when most operations are reads, as it forces readers to wait for each other even though they could safely execute in parallel.

## The std::shared_timed_mutex Class

`std::shared_timed_mutex` is designed to optimize concurrent access patterns by supporting two locking modes:

1. **Exclusive ownership** (write mode): Only one thread can own the mutex, blocking all other threads.
2. **Shared ownership** (read mode): Multiple threads can simultaneously own the mutex in shared mode.

The class is defined in the `<shared_mutex>` header and provides the following core operations:

```cpp
// Write (exclusive) lock operations
void lock();
bool try_lock();
template <class Rep, class Period>
bool try_lock_for(const std::chrono::duration<Rep, Period>& rel_time);
template <class Clock, class Duration>
bool try_lock_until(const std::chrono::time_point<Clock, Duration>& abs_time);
void unlock();

// Read (shared) lock operations
void lock_shared();
bool try_lock_shared();
template <class Rep, class Period>
bool try_lock_shared_for(const std::chrono::duration<Rep, Period>& rel_time);
template <class Clock, class Duration>
bool try_lock_shared_until(const std::chrono::time_point<Clock, Duration>& abs_time);
void unlock_shared();
```

As you can see, it offers both immediate and timed locking operations for both exclusive and shared access modes.

## Lock Adapters: std::unique_lock and std::shared_lock

While you can use the mutex methods directly, C++ provides RAII wrappers to simplify mutex management:

- `std::unique_lock`: For exclusive ownership (write mode)
- `std::shared_lock`: For shared ownership (read mode) - also introduced in C++14

These adapters automatically release the mutex when they go out of scope, helping to prevent deadlocks and make the code exception-safe.

## Basic Usage Example

Let's look at a simple example of using `std::shared_timed_mutex` to protect a data structure that is frequently read but occasionally updated:

```cpp
#include <iostream>
#include <shared_mutex>
#include <thread>
#include <vector>
#include <chrono>

class ThreadSafeCounter {
private:
    mutable std::shared_timed_mutex mutex_;
    int value_ = 0;

public:
    // Multiple threads can read the counter's value at the same time.
    int get() const {
        std::shared_lock<std::shared_timed_mutex> lock(mutex_);
        return value_;
    }

    // Only one thread can increment the counter at a time.
    void increment() {
        std::unique_lock<std::shared_timed_mutex> lock(mutex_);
        value_++;
    }

    // Only one thread can reset the counter at a time.
    void reset() {
        std::unique_lock<std::shared_timed_mutex> lock(mutex_);
        value_ = 0;
    }
};

int main() {
    ThreadSafeCounter counter;

    // Create 10 reader threads that repeatedly read the counter value
    std::vector<std::thread> readers;
    for (int i = 0; i < 10; ++i) {
        readers.emplace_back([&counter, i]() {
            for (int j = 0; j < 5; ++j) {
                std::cout << "Reader " << i << " sees counter value: " 
                          << counter.get() << std::endl;
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
            }
        });
    }

    // Create 2 writer threads that repeatedly increment the counter
    std::vector<std::thread> writers;
    for (int i = 0; i < 2; ++i) {
        writers.emplace_back([&counter, i]() {
            for (int j = 0; j < 3; ++j) {
                counter.increment();
                std::cout << "Writer " << i << " incremented counter" << std::endl;
                std::this_thread::sleep_for(std::chrono::milliseconds(200));
            }
        });
    }

    // Join all threads
    for (auto& t : readers) t.join();
    for (auto& t : writers) t.join();

    std::cout << "Final counter value: " << counter.get() << std::endl;
    return 0;
}
```

In this example, multiple reader threads can concurrently read the counter's value, while writer threads must acquire exclusive access to modify it.

## Timed Locking Operations

One of the distinguishing features of `std::shared_timed_mutex` is its support for timed locking operations, which is not available in the simpler `std::shared_mutex` introduced in C++17. These timed variants are useful for avoiding deadlocks and implementing timeouts:

```cpp
#include <iostream>
#include <shared_mutex>
#include <thread>
#include <chrono>

class ResourceWithTimeout {
private:
    std::shared_timed_mutex mutex_;
    int data_ = 0;

public:
    bool update_with_timeout(int new_value, std::chrono::milliseconds timeout) {
        // Try to acquire the lock with a timeout
        if (mutex_.try_lock_for(timeout)) {
            // Lock acquired successfully
            try {
                std::cout << "Lock acquired, updating data to " << new_value << std::endl;
                data_ = new_value;
                std::this_thread::sleep_for(std::chrono::milliseconds(100)); // Simulate work
                mutex_.unlock();
                return true;
            } catch (...) {
                mutex_.unlock();
                throw;
            }
        } else {
            // Failed to acquire lock within the timeout period
            std::cout << "Failed to acquire lock within timeout period" << std::endl;
            return false;
        }
    }

    bool read_with_timeout(int& result, std::chrono::milliseconds timeout) {
        // Try to acquire a shared lock with a timeout
        if (mutex_.try_lock_shared_for(timeout)) {
            // Shared lock acquired successfully
            try {
                result = data_;
                std::this_thread::sleep_for(std::chrono::milliseconds(50)); // Simulate work
                mutex_.unlock_shared();
                return true;
            } catch (...) {
                mutex_.unlock_shared();
                throw;
            }
        } else {
            // Failed to acquire shared lock within the timeout period
            std::cout << "Failed to acquire shared lock within timeout period" << std::endl;
            return false;
        }
    }
};

int main() {
    ResourceWithTimeout resource;
    
    // Simulate a long-running exclusive lock
    std::thread writer1([&resource]() {
        resource.update_with_timeout(42, std::chrono::milliseconds(1000));
        // Hold the lock for a while
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    });
    
    // Allow the first thread to start
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    
    // Try to acquire the lock with a short timeout
    std::thread writer2([&resource]() {
        bool success = resource.update_with_timeout(100, std::chrono::milliseconds(100));
        std::cout << "Writer2 update result: " << (success ? "success" : "timeout") << std::endl;
    });
    
    // Try to read with a short timeout
    std::thread reader([&resource]() {
        int value;
        bool success = resource.read_with_timeout(value, std::chrono::milliseconds(150));
        if (success) {
            std::cout << "Reader got value: " << value << std::endl;
        }
    });
    
    writer1.join();
    writer2.join();
    reader.join();
    
    return 0;
}
```

This example demonstrates using timed locking to prevent indefinite blocking.

## Implementation of a Thread-Safe Cache

A common use case for `std::shared_timed_mutex` is implementing a thread-safe cache. Here's an example of a simple read-heavy cache:

```cpp
#include <iostream>
#include <unordered_map>
#include <shared_mutex>
#include <string>
#include <functional>
#include <thread>
#include <vector>

template<typename Key, typename Value>
class ThreadSafeCache {
private:
    mutable std::shared_timed_mutex mutex_;
    std::unordered_map<Key, Value> cache_;
    std::function<Value(const Key&)> compute_value_;

public:
    explicit ThreadSafeCache(std::function<Value(const Key&)> compute_func)
        : compute_value_(std::move(compute_func)) {}

    Value get(const Key& key) {
        // First, try to read from the cache with a shared lock
        {
            std::shared_lock<std::shared_timed_mutex> read_lock(mutex_);
            auto it = cache_.find(key);
            if (it != cache_.end()) {
                return it->second;  // Cache hit
            }
        }

        // Cache miss - compute the value and update the cache with an exclusive lock
        std::unique_lock<std::shared_timed_mutex> write_lock(mutex_);
        
        // Check again in case another thread updated the cache while we were acquiring the write lock
        auto it = cache_.find(key);
        if (it != cache_.end()) {
            return it->second;
        }

        // Actually compute and cache the value
        Value value = compute_value_(key);
        cache_[key] = value;
        return value;
    }

    void invalidate(const Key& key) {
        std::unique_lock<std::shared_timed_mutex> write_lock(mutex_);
        cache_.erase(key);
    }

    void clear() {
        std::unique_lock<std::shared_timed_mutex> write_lock(mutex_);
        cache_.clear();
    }

    size_t size() const {
        std::shared_lock<std::shared_timed_mutex> read_lock(mutex_);
        return cache_.size();
    }
};

// Example usage
int main() {
    // Create a cache with a compute function that squares its input
    ThreadSafeCache<int, int> cache([](int n) {
        std::cout << "Computing square of " << n << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(100)); // Simulate expensive computation
        return n * n;
    });

    // Run multiple threads that read from the cache
    std::vector<std::thread> threads;
    for (int i = 0; i < 10; ++i) {
        threads.emplace_back([&cache, i]() {
            for (int j = 0; j < 5; ++j) {
                int key = j % 3;  // Use only keys 0, 1, and 2 to demonstrate cache hits
                int value = cache.get(key);
                std::cout << "Thread " << i << " got value for key " << key << ": " << value << std::endl;
                std::this_thread::sleep_for(std::chrono::milliseconds(20));
            }
        });
    }

    // Occasionally invalidate a cache entry
    std::thread invalidator([&cache]() {
        std::this_thread::sleep_for(std::chrono::milliseconds(250));
        std::cout << "Invalidating key 1" << std::endl;
        cache.invalidate(1);
        
        std::this_thread::sleep_for(std::chrono::milliseconds(250));
        std::cout << "Clearing entire cache" << std::endl;
        cache.clear();
    });

    // Join all threads
    for (auto& t : threads) {
        t.join();
    }
    invalidator.join();

    std::cout << "Final cache size: " << cache.size() << std::endl;
    return 0;
}
```

This cache implementation demonstrates the power of using shared locks for reads and exclusive locks for writes. Multiple threads can read from the cache simultaneously, but writes require exclusive access.

## Performance Considerations

`std::shared_timed_mutex` is designed for scenarios where reads significantly outnumber writes. In such cases, it can offer substantial performance benefits by allowing concurrent reads. However, there are some important considerations:

1. **Overhead**: Shared mutexes typically have higher overhead than standard mutexes, so they may not be beneficial if read operations are very quick or if reads and writes occur with similar frequency.

2. **Read-to-write transitions**: When a thread attempts to acquire an exclusive lock while shared locks are held, new shared lock requests may be blocked until the exclusive lock is granted. This can lead to a "read starvation" problem where readers keep arriving and prevent writers from making progress.

3. **Platform-specific performance**: The implementation details can vary across platforms, affecting performance characteristics.

4. **Memory usage**: The implementation of `std::shared_timed_mutex` is more complex and may require more memory than a standard mutex.

## Comparison with std::mutex and std::shared_mutex

It's useful to understand how `std::shared_timed_mutex` relates to other synchronization primitives:

- **std::mutex**: Provides only exclusive locking. Simpler and typically has lower overhead, but doesn't allow concurrent reads.

- **std::shared_mutex** (C++17): Similar to `std::shared_timed_mutex` but without the timed locking methods. If you don't need the timed variants, this is a more lightweight option.

- **std::recursive_mutex, std::recursive_timed_mutex**: Allow the same thread to acquire the lock multiple times, which `std::shared_timed_mutex` does not support.

Here's a quick comparison table:

| Feature | std::mutex | std::shared_timed_mutex (C++14) | std::shared_mutex (C++17) |
|---------|------------|----------------------------------|----------------------------|
| Exclusive locking | Yes | Yes | Yes |
| Shared locking | No | Yes | Yes |
| Timed locking | No | Yes | No |
| Memory footprint | Smallest | Largest | Medium |
| Typical overhead | Lowest | Highest | Medium |

## Best Practices

When working with `std::shared_timed_mutex`, keep these best practices in mind:

1. **Use RAII lock adapters**: Always prefer `std::shared_lock` and `std::unique_lock` over direct mutex manipulation.

2. **Minimize the critical section**: Keep locked regions as small as possible to reduce contention.

3. **Be careful with lock ordering**: To prevent deadlocks, establish a consistent order when acquiring multiple locks.

4. **Consider lock upgrades**: Moving from a shared lock to an exclusive lock may require completely releasing the shared lock first, which can introduce race conditions.

5. **Use timed locks appropriately**: Timed locks are useful for avoiding deadlocks, but they add complexity. Use them when you need timeout functionality.

6. **Benchmark your specific use case**: The performance benefits of shared locks depend on your specific read/write patterns.

## Conclusion

The `std::shared_timed_mutex` introduced in C++14 provides a powerful tool for managing concurrent access to shared resources when reads significantly outnumber writes. By allowing multiple readers to access data simultaneously while ensuring writers have exclusive access, it can dramatically improve performance in read-heavy scenarios.

This mutex type is particularly valuable for implementing thread-safe caches, configuration managers, and other data structures that experience infrequent updates but frequent reads. The added timed locking capabilities offer flexibility for implementing timeouts and avoiding deadlocks.

When properly applied, `std::shared_timed_mutex` can help create concurrent systems that are both correct and efficient. While it has higher overhead than simpler synchronization primitives, its benefits in read-heavy workloads often outweigh the costs.