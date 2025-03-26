# C++11 Thread Support Library: A Comprehensive Guide

## Introduction

C++11 introduced a standardized threading library, eliminating the need for platform-specific APIs or third-party libraries when writing multithreaded code. The thread support library consists of several headers: `<thread>`, `<mutex>`, `<condition_variable>`, `<future>`, and `<atomic>`. This article focuses on the three primary components: `<thread>`, `<mutex>`, and `<future>`, providing a thorough exploration of the tools available for concurrent programming in modern C++.

Before C++11, developers relied on platform-specific threading libraries like POSIX threads (pthreads) on Unix-like systems or Windows threads on Microsoft platforms. The standardization of threading in C++11 brought platform-independent concurrency support directly into the language, making multithreaded code more portable and easier to write.

## The `<thread>` Header

The `<thread>` header provides the fundamental building block for multithreaded programming: the `std::thread` class, which represents a single thread of execution.

### Creating Threads

A `std::thread` object can be created by passing a callable object (function, function object, or lambda) and its arguments to the constructor:

```cpp
#include <iostream>
#include <thread>
#include <string>

void simple_function() {
    std::cout << "Hello from a thread!" << std::endl;
}

void parameterized_function(const std::string& message, int count) {
    for (int i = 0; i < count; ++i) {
        std::cout << message << " " << i << std::endl;
    }
}

class ThreadFunctor {
public:
    void operator()() const {
        std::cout << "Thread functor executing" << std::endl;
    }
};

int main() {
    // Thread with simple function
    std::thread t1(simple_function);
    
    // Thread with parameterized function
    std::thread t2(parameterized_function, "Count", 3);
    
    // Thread with functor
    std::thread t3(ThreadFunctor());
    
    // Thread with lambda
    std::thread t4([]() {
        std::cout << "Thread with lambda executing" << std::endl;
    });
    
    // Wait for all threads to complete
    t1.join();
    t2.join();
    t3.join();
    t4.join();
    
    return 0;
}
```

### Thread Management

Once a thread is started, you must decide how to handle its lifetime:

#### Joining Threads

The `join()` method blocks the calling thread until the thread represented by the `std::thread` object completes execution:

```cpp
std::thread worker(task_function);
// Do some work in the main thread
worker.join(); // Wait for worker to finish
```

#### Detaching Threads

The `detach()` method disconnects the thread from its `std::thread` object, allowing the thread to execute independently:

```cpp
std::thread background_task(background_function);
background_task.detach(); // Run independently - be careful with this!
```

Detached threads continue running even after the `std::thread` object is destroyed, which can lead to issues if they access resources that go out of scope.

### Thread Identification

Each thread has a unique identifier that can be retrieved using `get_id()`:

```cpp
#include <iostream>
#include <thread>

void print_id() {
    std::cout << "Thread ID: " << std::this_thread::get_id() << std::endl;
}

int main() {
    std::thread t1(print_id);
    std::thread t2(print_id);
    
    std::cout << "t1 ID: " << t1.get_id() << std::endl;
    std::cout << "t2 ID: " << t2.get_id() << std::endl;
    std::cout << "Main thread ID: " << std::this_thread::get_id() << std::endl;
    
    t1.join();
    t2.join();
    
    return 0;
}
```

### Thread Utilities

The `<thread>` header also provides utilities for thread management:

#### Sleep Functions

```cpp
#include <iostream>
#include <thread>
#include <chrono>

int main() {
    std::cout << "Starting..." << std::endl;
    
    // Sleep for 2 seconds
    std::this_thread::sleep_for(std::chrono::seconds(2));
    
    std::cout << "After 2 seconds" << std::endl;
    
    // Sleep until a specific time point
    auto now = std::chrono::system_clock::now();
    auto wakeup_time = now + std::chrono::milliseconds(500);
    std::this_thread::sleep_until(wakeup_time);
    
    std::cout << "After additional 500ms" << std::endl;
    
    return 0;
}
```

#### Yield

The `yield()` function suggests that the implementation reschedule execution of threads:

```cpp
void cpu_intensive_task() {
    for (int i = 0; i < 1000000; ++i) {
        // Do some work
        if (i % 1000 == 0) {
            std::this_thread::yield(); // Give other threads a chance to run
        }
    }
}
```

### Hardware Concurrency

The `hardware_concurrency()` static method returns an indication of the number of threads that can truly execute concurrently:

```cpp
std::cout << "This system can run " 
          << std::thread::hardware_concurrency() 
          << " threads concurrently" << std::endl;
```

## The `<mutex>` Header

The `<mutex>` header provides synchronization primitives that protect shared data from being simultaneously accessed by multiple threads, preventing race conditions.

### Basic Mutex Types

#### std::mutex

The most basic synchronization primitive is `std::mutex`, which provides exclusive access to a resource:

```cpp
#include <iostream>
#include <thread>
#include <mutex>
#include <vector>

std::mutex g_mutex;
int g_counter = 0;

void increment_counter(int iterations) {
    for (int i = 0; i < iterations; ++i) {
        g_mutex.lock();
        ++g_counter;
        g_mutex.unlock();
    }
}

int main() {
    constexpr int iterations = 10000;
    std::vector<std::thread> threads;
    
    for (int i = 0; i < 10; ++i) {
        threads.push_back(std::thread(increment_counter, iterations));
    }
    
    for (auto& t : threads) {
        t.join();
    }
    
    std::cout << "Counter value: " << g_counter << std::endl;
    // Should output 100000
    
    return 0;
}
```

#### std::recursive_mutex

A `std::recursive_mutex` allows the same thread to lock the mutex multiple times:

```cpp
#include <iostream>
#include <thread>
#include <mutex>

class RecursiveCounter {
private:
    std::recursive_mutex mutex;
    int value = 0;
    
public:
    void increment() {
        std::lock_guard<std::recursive_mutex> lock(mutex);
        value++;
        
        // Recursive call is safe because of recursive_mutex
        if (value < 10) {
            increment();
        }
    }
    
    int get_value() {
        std::lock_guard<std::recursive_mutex> lock(mutex);
        return value;
    }
};

int main() {
    RecursiveCounter counter;
    counter.increment();
    std::cout << "Counter value: " << counter.get_value() << std::endl;
    return 0;
}
```

#### std::timed_mutex

A `std::timed_mutex` provides the ability to attempt to lock a mutex with a timeout:

```cpp
#include <iostream>
#include <thread>
#include <mutex>
#include <chrono>

std::timed_mutex resource_mutex;

void worker(int id) {
    if (resource_mutex.try_lock_for(std::chrono::milliseconds(200))) {
        std::cout << "Thread " << id << " acquired lock" << std::endl;
        
        // Simulate work
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        
        resource_mutex.unlock();
        std::cout << "Thread " << id << " released lock" << std::endl;
    } else {
        std::cout << "Thread " << id << " couldn't acquire lock within timeout" << std::endl;
    }
}

int main() {
    std::thread t1(worker, 1);
    std::thread t2(worker, 2);
    
    t1.join();
    t2.join();
    
    return 0;
}
```

### RAII Lock Guards

RAII (Resource Acquisition Is Initialization) lock guards automatically release the lock when they go out of scope, helping to prevent deadlocks and ensure proper mutex management.

#### std::lock_guard

The simplest RAII lock wrapper:

```cpp
#include <iostream>
#include <thread>
#include <mutex>
#include <vector>

std::mutex g_mutex;
int g_counter = 0;

void increment_counter(int iterations) {
    for (int i = 0; i < iterations; ++i) {
        // Automatically unlocks when going out of scope
        std::lock_guard<std::mutex> lock(g_mutex);
        ++g_counter;
    }
}

int main() {
    constexpr int iterations = 10000;
    std::vector<std::thread> threads;
    
    for (int i = 0; i < 10; ++i) {
        threads.push_back(std::thread(increment_counter, iterations));
    }
    
    for (auto& t : threads) {
        t.join();
    }
    
    std::cout << "Counter value: " << g_counter << std::endl;
    
    return 0;
}
```

#### std::unique_lock

More flexible than `lock_guard`, allowing deferred locking, timed locking, and manual unlocking:

```cpp
#include <iostream>
#include <thread>
#include <mutex>
#include <vector>

std::mutex write_mutex;
std::mutex read_mutex;

void complex_operation(int id) {
    // Defer locking until needed
    std::unique_lock<std::mutex> write_lock(write_mutex, std::defer_lock);
    std::unique_lock<std::mutex> read_lock(read_mutex, std::defer_lock);
    
    // Acquire both locks without deadlock
    std::lock(write_lock, read_lock);
    
    std::cout << "Thread " << id << " has both locks" << std::endl;
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    
    // Release just the write lock, keeping the read lock
    write_lock.unlock();
    std::cout << "Thread " << id << " released write lock, still has read lock" << std::endl;
    
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    
    // read_lock automatically released at the end of scope
}

int main() {
    std::vector<std::thread> threads;
    
    for (int i = 0; i < 5; ++i) {
        threads.push_back(std::thread(complex_operation, i));
    }
    
    for (auto& t : threads) {
        t.join();
    }
    
    return 0;
}
```

### Lock Functions

C++11 provides utility functions for managing multiple locks:

#### std::lock

Acquires multiple locks simultaneously while avoiding deadlocks:

```cpp
#include <iostream>
#include <thread>
#include <mutex>
#include <vector>

class BankAccount {
private:
    std::mutex mutex;
    int balance;
    
public:
    BankAccount(int initial_balance) : balance(initial_balance) {}
    
    friend void transfer(BankAccount& from, BankAccount& to, int amount);
};

void transfer(BankAccount& from, BankAccount& to, int amount) {
    // Lock both accounts at once to prevent deadlock
    std::lock(from.mutex, to.mutex);
    
    // Create lock_guards that adopt the already-locked mutexes
    std::lock_guard<std::mutex> from_lock(from.mutex, std::adopt_lock);
    std::lock_guard<std::mutex> to_lock(to.mutex, std::adopt_lock);
    
    from.balance -= amount;
    to.balance += amount;
    
    std::cout << "Transfer complete" << std::endl;
}

int main() {
    BankAccount account1(1000);
    BankAccount account2(2000);
    
    std::vector<std::thread> threads;
    
    for (int i = 0; i < 5; ++i) {
        threads.push_back(std::thread(transfer, std::ref(account1), std::ref(account2), 100));
        threads.push_back(std::thread(transfer, std::ref(account2), std::ref(account1), 50));
    }
    
    for (auto& t : threads) {
        t.join();
    }
    
    return 0;
}
```

#### std::scoped_lock (C++17)

While not part of C++11, it's worth mentioning that C++17 introduced `std::scoped_lock`, which simplifies the above code:

```cpp
void transfer(BankAccount& from, BankAccount& to, int amount) {
    // Automatically locks both mutexes without deadlock
    std::scoped_lock lock(from.mutex, to.mutex);
    
    from.balance -= amount;
    to.balance += amount;
    
    std::cout << "Transfer complete" << std::endl;
}
```

## The `<future>` Header

The `<future>` header provides facilities to obtain values that are set asynchronously and to check the state of asynchronous operations.

### std::future and std::promise

A `std::promise` is used to set a value that will be available through a `std::future`:

```cpp
#include <iostream>
#include <future>
#include <thread>
#include <string>

void produce_result(std::promise<std::string> promise) {
    try {
        // Simulate work
        std::this_thread::sleep_for(std::chrono::seconds(2));
        
        // Fulfill the promise
        promise.set_value("Result from worker thread");
    } catch (...) {
        // In case of exception, set the exception in the promise
        promise.set_exception(std::current_exception());
    }
}

int main() {
    // Create a promise
    std::promise<std::string> promise;
    
    // Get the future from the promise
    std::future<std::string> future = promise.get_future();
    
    // Launch the worker thread with the promise
    std::thread worker(produce_result, std::move(promise));
    
    std::cout << "Waiting for result..." << std::endl;
    
    // Wait for the result and retrieve it
    std::string result = future.get();
    
    std::cout << "Got result: " << result << std::endl;
    
    worker.join();
    
    return 0;
}
```

### std::async

The `std::async` function template provides a convenient way to run a function asynchronously and get a `std::future` for its result:

```cpp
#include <iostream>
#include <future>
#include <thread>
#include <vector>
#include <numeric>
#include <random>

// Function to compute the sum of elements in a vector
long long sum_vector(const std::vector<int>& vec, size_t start, size_t end) {
    return std::accumulate(vec.begin() + start, vec.begin() + end, 0LL);
}

int main() {
    // Generate a large vector of random numbers
    std::vector<int> data(100000000);
    std::mt19937 gen(42); // Fixed seed for reproducibility
    std::uniform_int_distribution<> dist(1, 100);
    
    for (auto& num : data) {
        num = dist(gen);
    }
    
    // Get the number of hardware threads
    unsigned int num_threads = std::thread::hardware_concurrency();
    std::vector<std::future<long long>> futures;
    
    // Divide the work among threads
    size_t chunk_size = data.size() / num_threads;
    
    auto start_time = std::chrono::high_resolution_clock::now();
    
    // Launch tasks asynchronously
    for (unsigned int i = 0; i < num_threads; ++i) {
        size_t start = i * chunk_size;
        size_t end = (i == num_threads - 1) ? data.size() : (i + 1) * chunk_size;
        
        // std::launch::async forces creation of a new thread
        futures.push_back(
            std::async(std::launch::async, sum_vector, std::ref(data), start, end)
        );
    }
    
    // Collect and sum results
    long long total_sum = 0;
    for (auto& future : futures) {
        total_sum += future.get();
    }
    
    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
    
    std::cout << "Sum: " << total_sum << std::endl;
    std::cout << "Calculation took " << duration.count() << " ms" << std::endl;
    
    return 0;
}
```

### Launch Policies

The `std::async` function accepts launch policies that control how the task is executed:

- `std::launch::async`: The task is executed on a new thread.
- `std::launch::deferred`: The task is executed on the calling thread when `get()` or `wait()` is called.
- `std::launch::async | std::launch::deferred` (default): The implementation chooses either policy.

```cpp
#include <iostream>
#include <future>
#include <thread>

void show_thread_id() {
    std::cout << "Thread ID: " << std::this_thread::get_id() << std::endl;
}

int main() {
    std::cout << "Main thread ID: " << std::this_thread::get_id() << std::endl;
    
    // Force async execution
    auto f1 = std::async(std::launch::async, show_thread_id);
    
    // Deferred execution
    auto f2 = std::async(std::launch::deferred, show_thread_id);
    
    // Implementation's choice
    auto f3 = std::async(show_thread_id);
    
    f1.wait();  // Already executed on a different thread
    
    std::cout << "Before calling f2.get()" << std::endl;
    f2.get();   // Will execute now on the main thread
    
    f3.wait();  // Might already have executed or will execute now
    
    return 0;
}
```

### std::shared_future

A `std::shared_future` allows multiple threads to wait for the same result:

```cpp
#include <iostream>
#include <future>
#include <thread>
#include <vector>

void worker(std::shared_future<int> shared_future, int id) {
    try {
        std::cout << "Thread " << id << " waiting for result..." << std::endl;
        int result = shared_future.get(); // Multiple threads can call get()
        std::cout << "Thread " << id << " got result: " << result << std::endl;
    } catch (const std::exception& e) {
        std::cout << "Thread " << id << " caught exception: " << e.what() << std::endl;
    }
}

int main() {
    std::promise<int> promise;
    std::future<int> future = promise.get_future();
    
    // Convert to shared_future
    std::shared_future<int> shared_future = future.share();
    
    // Create multiple threads that wait on the same future
    std::vector<std::thread> threads;
    for (int i = 0; i < 5; ++i) {
        threads.push_back(std::thread(worker, shared_future, i));
    }
    
    std::cout << "Press Enter to set the result..." << std::endl;
    std::cin.get();
    
    promise.set_value(42);
    
    for (auto& t : threads) {
        t.join();
    }
    
    return 0;
}
```

### Packaged Tasks

A `std::packaged_task` wraps a callable entity and allows its result to be retrieved asynchronously:

```cpp
#include <iostream>
#include <future>
#include <thread>
#include <functional>

int calculate(int x, int y) {
    std::this_thread::sleep_for(std::chrono::seconds(1));
    return x + y;
}

int main() {
    // Create a packaged_task with a function
    std::packaged_task<int(int, int)> task(calculate);
    
    // Get the future from the task
    std::future<int> result = task.get_future();
    
    // Launch the task on a new thread
    std::thread task_thread(std::move(task), 2, 3);
    
    // Wait for the result
    std::cout << "Waiting for result..." << std::endl;
    int sum = result.get();
    
    std::cout << "Result: " << sum << std::endl;
    
    task_thread.join();
    
    return 0;
}
```

## Combining the Components

Let's examine how to combine these three libraries in a more complex example: a thread pool implementation.

```cpp
#include <iostream>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <future>
#include <vector>
#include <queue>
#include <functional>
#include <memory>

class ThreadPool {
public:
    ThreadPool(size_t num_threads) : stop(false) {
        for (size_t i = 0; i < num_threads; ++i) {
            workers.emplace_back([this] {
                while (true) {
                    std::function<void()> task;
                    
                    {
                        std::unique_lock<std::mutex> lock(queue_mutex);
                        
                        // Wait until there's a task or stop flag is set
                        condition.wait(lock, [this] { 
                            return stop || !tasks.empty(); 
                        });
                        
                        // Exit if stop flag is set and queue is empty
                        if (stop && tasks.empty()) {
                            return;
                        }
                        
                        // Get task from queue
                        task = std::move(tasks.front());
                        tasks.pop();
                    }
                    
                    // Execute the task
                    task();
                }
            });
        }
    }
    
    template<class F, class... Args>
    auto enqueue(F&& f, Args&&... args) 
        -> std::future<typename std::result_of<F(Args...)>::type> {
        
        using return_type = typename std::result_of<F(Args...)>::type;
        
        // Create a packaged task with the function and arguments
        auto task = std::make_shared<std::packaged_task<return_type()>>(
            std::bind(std::forward<F>(f), std::forward<Args>(args)...)
        );
        
        // Get future from the task
        std::future<return_type> result = task->get_future();
        
        {
            std::unique_lock<std::mutex> lock(queue_mutex);
            
            // Don't allow enqueueing after stopping the pool
            if (stop) {
                throw std::runtime_error("enqueue on stopped ThreadPool");
            }
            
            // Add the task to the queue
            tasks.emplace([task]() { (*task)(); });
        }
        
        // Notify one waiting thread
        condition.notify_one();
        
        return result;
    }
    
    ~ThreadPool() {
        {
            std::unique_lock<std::mutex> lock(queue_mutex);
            stop = true;
        }
        
        // Notify all threads to check stop condition
        condition.notify_all();
        
        // Join all threads
        for (std::thread& worker : workers) {
            worker.join();
        }
    }
    
private:
    std::vector<std::thread> workers;
    std::queue<std::function<void()>> tasks;
    
    std::mutex queue_mutex;
    std::condition_variable condition;
    bool stop;
};

// Example usage
int main() {
    ThreadPool pool(4);  // Create a thread pool with 4 threads
    
    // Enqueue some tasks
    std::vector<std::future<int>> results;
    
    for (int i = 0; i < 8; ++i) {
        results.emplace_back(
            pool.enqueue([i] {
                std::cout << "Task " << i << " running on thread " 
                          << std::this_thread::get_id() << std::endl;
                
                std::this_thread::sleep_for(std::chrono::seconds(1));
                
                return i * i;
            })
        );
    }
    
    // Get the results
    for (size_t i = 0; i < results.size(); ++i) {
        std::cout << "Result " << i << ": " << results[i].get() << std::endl;
    }
    
    return 0;
}
```

This thread pool example demonstrates:
1. Using `std::thread` to create worker threads
2. Using `std::mutex` and `std::condition_variable` for thread synchronization
3. Using `std::packaged_task` and `std::future` to handle task results

## Best Practices and Common Pitfalls

### Best Practices

1. **Use RAII for mutex locking**: Always use `std::lock_guard`, `std::unique_lock`, or `std::scoped_lock` instead of manual `lock()` and `unlock()` calls to avoid forgetting to unlock.

2. **Minimize critical sections**: Keep the code protected by mutexes as small as possible to reduce contention.

3. **Prefer `std::async` for simple tasks**: For one-off asynchronous operations, `std::async` provides a clean and easy-to-use interface.

4. **Use appropriate mutex types**: Choose the right mutex for your needs (e.g., `std::recursive_mutex` if you need recursive locking).

5. **Avoid deadlocks**: Use `std::lock` or `std::scoped_lock` when acquiring multiple locks, and always acquire them in a consistent order.

### Common Pitfalls

1. **Detached threads accessing destroyed objects**: Be careful with `detach()`, as the thread might still be running after the objects it accesses are destroyed.

```cpp
// Dangerous code:
void process_data() {
    std::vector<int> data = {1, 2, 3, 4, 5};
    std::thread t([&data] {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        // Accessing 'data' here is dangerous
        for (int i : data) {
            std::cout << i << std::endl;
        }
    });
    t.detach(); // data will be destroyed when function returns, but thread still runs
}
```

2. **Race conditions**: Always protect shared data with appropriate synchronization primitives.

3. **Deadlocks**: Acquiring locks in inconsistent order can lead to deadlocks.

```cpp
// Potential deadlock:
std::mutex mutex1, mutex2;

// Thread 1
mutex1.lock();
// ... some work ...
mutex2.lock();

// Thread 2
mutex2.lock();
// ... some work ...
mutex1.lock();
```

4. **Using futures after they're consumed**: Calling `get()` on a `std::future` more than once is undefined behavior.

```cpp
// Incorrect usage:
std::future<int> f = std::async(std::launch::async, []{ return 42; });
int result1 = f.get(); // OK
int result2 = f.get(); // Undefined behavior!
```

5. **Excessive thread creation**: Creating too many threads can degrade performance. Consider using a thread pool for managing thread resources.

## Conclusion

The C++11 thread support library provides a comprehensive set of tools for concurrent programming. The `<thread>` header offers facilities for creating and managing threads, the `<mutex>` header provides synchronization primitives to protect shared data, and the `<future>` header enables asynchronous computation and communication between threads.

Understanding these components and how they interact is essential for writing robust and efficient multithreaded C++ applications. By following best practices and avoiding common pitfalls, you can harness the power of concurrency to improve the performance and responsiveness of your applications.

The standardization of threading in C++11 marked a significant milestone for the language, enabling portable concurrent code without relying on platform-specific libraries. Subsequent C++ standards have built upon this foundation, introducing additional features like `std::shared_mutex` in C++14 and `std::scoped_lock` in C++17, further enhancing C++'s concurrency capabilities.