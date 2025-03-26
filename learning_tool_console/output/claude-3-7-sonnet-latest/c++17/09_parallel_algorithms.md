# C++17 Parallel Algorithms: Leveraging std::execution for Performance

## Introduction

C++17 introduced a significant enhancement to the Standard Template Library (STL) with parallel versions of many algorithms through the `std::execution` namespace. This feature allows developers to leverage multi-core processors efficiently without having to manually implement thread management or complex synchronization logic. By simply specifying an execution policy, algorithms can run sequentially, in parallel, or vectorized, making it easier than ever to write high-performance code.

This article explores the capabilities, syntax, and best practices of the parallel algorithms in C++17, with a focus on the different execution policies and their implications for performance and code behavior.

## Execution Policies

The `std::execution` namespace defines several execution policies that control how algorithms execute:

1. `std::execution::seq` - Sequential execution
2. `std::execution::par` - Parallel execution
3. `std::execution::par_unseq` - Parallel and vectorized execution
4. `std::execution::unseq` - Vectorized execution (added in C++20)

Let's explore each of these in detail:

### Sequential Execution (std::execution::seq)

This policy enforces sequential execution, which is equivalent to the traditional algorithm behavior prior to C++17. Operations are executed on a single thread, in the same order as would happen without specifying an execution policy.

```cpp
#include <algorithm>
#include <execution>
#include <vector>

std::vector<int> data = {/* ... */};
std::sort(std::execution::seq, data.begin(), data.end());
```

### Parallel Execution (std::execution::par)

The parallel execution policy allows the algorithm to be executed on multiple threads. The implementation may split the work into chunks that run concurrently, potentially providing significant performance improvements on multi-core systems.

```cpp
#include <algorithm>
#include <execution>
#include <vector>
#include <iostream>
#include <chrono>

int main() {
    const size_t SIZE = 10'000'000;
    std::vector<int> data(SIZE);
    
    // Initialize with values in reverse order
    for (size_t i = 0; i < SIZE; ++i) {
        data[i] = SIZE - i;
    }
    
    // Measure sequential sort
    auto start = std::chrono::high_resolution_clock::now();
    std::sort(std::execution::seq, data.begin(), data.end());
    auto end = std::chrono::high_resolution_clock::now();
    auto seq_duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    // Re-initialize data
    for (size_t i = 0; i < SIZE; ++i) {
        data[i] = SIZE - i;
    }
    
    // Measure parallel sort
    start = std::chrono::high_resolution_clock::now();
    std::sort(std::execution::par, data.begin(), data.end());
    end = std::chrono::high_resolution_clock::now();
    auto par_duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    std::cout << "Sequential sort took: " << seq_duration.count() << " ms\n";
    std::cout << "Parallel sort took: " << par_duration.count() << " ms\n";
    
    return 0;
}
```

### Parallel and Vectorized Execution (std::execution::par_unseq)

This policy allows both parallelization and vectorization of the algorithm. Vectorization means that the operations can use SIMD (Single Instruction Multiple Data) instructions where applicable, which process multiple data items simultaneously using CPU vector registers.

```cpp
std::vector<float> data(10'000'000);
// Initialize data

// Apply a transformation in parallel with potential vectorization
std::transform(std::execution::par_unseq, 
               data.begin(), data.end(), 
               data.begin(),
               [](float x) { return std::sqrt(x) * 2.0f; });
```

This policy can lead to the best performance for suitable operations, but has more restrictions on user-provided functions (they must be vectorizable).

### Vectorized Execution (std::execution::unseq, C++20)

C++20 added a fourth policy that allows vectorization without parallelization. While this is a C++20 feature, it's worth mentioning for completeness:

```cpp
std::vector<float> data(10'000'000);
// Initialize data

// Apply a transformation with vectorization only
std::transform(std::execution::unseq, 
               data.begin(), data.end(), 
               data.begin(),
               [](float x) { return std::sqrt(x) * 2.0f; });
```

## Supported Algorithms

Many of the algorithms in the STL now support parallel execution. Here's a non-exhaustive list:

- Non-modifying sequence operations: `std::all_of`, `std::any_of`, `std::none_of`, `std::for_each`, `std::find`, `std::find_if`, `std::count`, etc.
- Modifying sequence operations: `std::copy`, `std::move`, `std::swap_ranges`, `std::transform`, `std::replace`, etc.
- Sorting operations: `std::sort`, `std::stable_sort`, `std::partial_sort`, etc.
- Numeric operations: `std::reduce`, `std::transform_reduce`, `std::inclusive_scan`, etc.

The general pattern for using these algorithms with parallel execution policies is:

```cpp
std::algorithm_name(execution_policy, iterators_and_other_args...);
```

## Advanced Example: Parallel Image Processing

Let's look at a more substantial example that processes an image using parallel algorithms:

```cpp
#include <algorithm>
#include <execution>
#include <vector>
#include <cmath>
#include <iostream>
#include <chrono>

// Simplified RGB image structure
struct Pixel {
    unsigned char r, g, b;
};

struct Image {
    std::vector<Pixel> pixels;
    int width;
    int height;
    
    Image(int w, int h) : width(w), height(h), pixels(w * h) {}
    
    Pixel& at(int x, int y) {
        return pixels[y * width + x];
    }
};

// Apply a simple blur filter
void apply_blur(Image& image, const std::execution::parallel_policy&) {
    // Create a copy of the original image
    auto original = image.pixels;
    
    // Apply blur filter in parallel
    std::for_each(std::execution::par, 
                  std::begin(image.pixels), std::end(image.pixels),
                  [&original, &image](Pixel& p) {
                      // Get the current pixel's position
                      auto idx = &p - &image.pixels[0];
                      int x = idx % image.width;
                      int y = idx / image.width;
                      
                      // Skip border pixels for simplicity
                      if (x == 0 || y == 0 || x == image.width - 1 || y == image.height - 1) {
                          return;
                      }
                      
                      // Apply a 3x3 average blur
                      unsigned r = 0, g = 0, b = 0;
                      for (int dy = -1; dy <= 1; ++dy) {
                          for (int dx = -1; dx <= 1; ++dx) {
                              auto& neighbor = original[(y + dy) * image.width + (x + dx)];
                              r += neighbor.r;
                              g += neighbor.g;
                              b += neighbor.b;
                          }
                      }
                      
                      // Set the new pixel values (average of 9 pixels)
                      p.r = r / 9;
                      p.g = g / 9;
                      p.b = b / 9;
                  });
}

// Sequential version for comparison
void apply_blur_seq(Image& image) {
    // Create a copy of the original image
    auto original = image.pixels;
    
    // Apply blur filter sequentially
    for (int y = 1; y < image.height - 1; ++y) {
        for (int x = 1; x < image.width - 1; ++x) {
            unsigned r = 0, g = 0, b = 0;
            
            for (int dy = -1; dy <= 1; ++dy) {
                for (int dx = -1; dx <= 1; ++dx) {
                    auto& neighbor = original[(y + dy) * image.width + (x + dx)];
                    r += neighbor.r;
                    g += neighbor.g;
                    b += neighbor.b;
                }
            }
            
            auto& p = image.at(x, y);
            p.r = r / 9;
            p.g = g / 9;
            p.b = b / 9;
        }
    }
}

int main() {
    // Create a test image (2000x2000)
    const int width = 2000;
    const int height = 2000;
    Image image(width, height);
    
    // Fill with some test data
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            image.at(x, y) = {
                static_cast<unsigned char>(x % 256),
                static_cast<unsigned char>(y % 256),
                static_cast<unsigned char>((x + y) % 256)
            };
        }
    }
    
    // Process sequentially and measure time
    Image seq_image = image;
    auto start = std::chrono::high_resolution_clock::now();
    apply_blur_seq(seq_image);
    auto end = std::chrono::high_resolution_clock::now();
    auto seq_duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    // Process in parallel and measure time
    Image par_image = image;
    start = std::chrono::high_resolution_clock::now();
    apply_blur(par_image, std::execution::par);
    end = std::chrono::high_resolution_clock::now();
    auto par_duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    std::cout << "Sequential processing took: " << seq_duration.count() << " ms\n";
    std::cout << "Parallel processing took: " << par_duration.count() << " ms\n";
    
    return 0;
}
```

## Performance Considerations

When using parallel algorithms, consider the following performance factors:

1. **Problem Size**: Parallel execution introduces overhead. For small datasets, the overhead might outweigh the benefits of parallelism. Always benchmark with realistic data sizes.

2. **Hardware Capabilities**: The speedup you'll achieve depends on the number of cores/threads available and the memory bandwidth of your system.

3. **Algorithm Complexity**: Not all algorithms benefit equally from parallelization. Algorithms with independent operations (like element-wise transformations) tend to scale better than those requiring coordination.

4. **Memory Access Patterns**: Cache-friendly access patterns are crucial for performance. Random access patterns can cause cache thrashing in parallel scenarios.

Here's an example comparing different-sized workloads:

```cpp
#include <algorithm>
#include <execution>
#include <vector>
#include <iostream>
#include <chrono>
#include <random>
#include <functional>

// Utility to measure execution time
template<typename Func>
double measure_time_ms(Func&& func) {
    auto start = std::chrono::high_resolution_clock::now();
    func();
    auto end = std::chrono::high_resolution_clock::now();
    return std::chrono::duration<double, std::milli>(end - start).count();
}

int main() {
    // Test with different sizes
    std::vector<size_t> sizes = {10'000, 100'000, 1'000'000, 10'000'000};
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> distrib(1, 1000);
    
    for (auto size : sizes) {
        // Create and populate vector
        std::vector<int> data(size);
        std::generate(data.begin(), data.end(), [&]() { return distrib(gen); });
        
        // Make copies for each test
        auto data_seq = data;
        auto data_par = data;
        auto data_par_unseq = data;
        
        std::cout << "Data size: " << size << std::endl;
        
        // Sequential sort
        double time_seq = measure_time_ms([&]() {
            std::sort(std::execution::seq, data_seq.begin(), data_seq.end());
        });
        
        // Parallel sort
        double time_par = measure_time_ms([&]() {
            std::sort(std::execution::par, data_par.begin(), data_par.end());
        });
        
        // Parallel+vectorized sort
        double time_par_unseq = measure_time_ms([&]() {
            std::sort(std::execution::par_unseq, data_par_unseq.begin(), data_par_unseq.end());
        });
        
        std::cout << "  Sequential: " << time_seq << " ms\n";
        std::cout << "  Parallel: " << time_par << " ms (speedup: " 
                  << time_seq / time_par << "x)\n";
        std::cout << "  Parallel+Vectorized: " << time_par_unseq << " ms (speedup: " 
                  << time_seq / time_par_unseq << "x)\n";
        std::cout << std::endl;
    }
    
    return 0;
}
```

## Thread Safety and Exception Handling

When using parallel algorithms, there are important considerations for thread safety and exception handling:

### Thread Safety

1. **Callable Objects**: Functors, lambdas, or function pointers passed to parallel algorithms must be thread-safe. They might be called concurrently from multiple threads.

2. **Iterators and Ranges**: The iterators and ranges passed to parallel algorithms must be safe for concurrent dereferencing and incrementing.

3. **Side Effects**: Be cautious with side effects in your operations. Modifying shared state may lead to race conditions.

```cpp
// UNSAFE: Race condition on the counter
std::atomic<int> counter = 0;  // Even with atomic, this is problematic
std::for_each(std::execution::par, v.begin(), v.end(), [&counter](int x) {
    if (x % 2 == 0) counter++;  // Race condition
});

// SAFE: Use a reduction algorithm instead
int evens = std::count_if(std::execution::par, v.begin(), v.end(), 
                          [](int x) { return x % 2 == 0; });
```

### Exception Handling

Parallel algorithms have different exception handling semantics compared to their sequential counterparts:

1. If an exception is thrown from a user-provided function during parallel execution, `std::terminate` might be called.

2. The standard allows implementations to propagate exceptions in certain cases, but this is not guaranteed.

3. Best practice is to avoid throwing exceptions in functions passed to parallel algorithms.

```cpp
// Problematic: May call std::terminate
std::for_each(std::execution::par, v.begin(), v.end(), [](int& x) {
    if (x < 0) throw std::runtime_error("Negative value");  // Don't do this
    x = std::sqrt(x);
});

// Better approach: Handle errors without exceptions
std::for_each(std::execution::par, v.begin(), v.end(), [](int& x) {
    if (x < 0) x = 0;  // Handle the error condition without throwing
    else x = std::sqrt(x);
});
```

## Implementation Details and Compiler Support

The parallel algorithms feature requires a C++17-compliant compiler and library implementation. The major compilers (GCC, Clang, MSVC) support parallel algorithms, but there are some implementation considerations:

1. **Backend Threading Library**: The implementation might use different backends like Intel's Threading Building Blocks (TBB), OpenMP, or a custom implementation.

2. **Compiler Flags**: Some implementations require specific compiler flags:
   - GCC: `-pthread` to enable threading support
   - MSVC: `/openmp` or linking to a specific implementation
   - Clang: May require linking to a specific library like TBB

3. **Implementation Quality**: Different implementations may have varying performance characteristics.

Here's how to check if parallel algorithms are available:

```cpp
#include <algorithm>
#include <execution>
#include <iostream>

int main() {
    #if defined(__cpp_lib_parallel_algorithm) && (__cpp_lib_parallel_algorithm >= 201603)
        std::cout << "Parallel algorithms are supported\n";
        std::cout << "Feature test macro value: " << __cpp_lib_parallel_algorithm << "\n";
    #else
        std::cout << "Parallel algorithms are not supported\n";
    #endif
    
    return 0;
}
```

## Best Practices

To get the most out of parallel algorithms, consider these best practices:

1. **Benchmark Different Policies**: Always measure performance with different execution policies. Don't assume parallel execution will always be faster.

2. **Consider Problem Size**: Use parallel execution primarily for larger problems where the parallelization overhead is amortized.

3. **Avoid Race Conditions**: Ensure that operations performed in parallel don't have data dependencies or modify shared state without proper synchronization.

4. **Design for Parallelism**: Structure your algorithms to minimize communication and dependencies between parallel tasks.

5. **Mind the Memory Usage**: Parallel algorithms might use more memory due to temporary buffers or thread-local storage.

6. **Use Contiguous Memory**: Algorithms work best on contiguous memory (like `std::vector`) rather than linked data structures (like `std::list`).

7. **Combine Algorithms**: Sometimes using a single parallel algorithm is more efficient than chaining multiple operations with separate parallelism.

## Conclusion

C++17's parallel algorithms provide a powerful, standardized way to leverage multi-core processors without diving into complex thread management. By simply specifying an execution policy, developers can parallelize standard algorithms with minimal code changes. The `std::execution` namespace offers policies for sequential, parallel, and vectorized execution, allowing for flexibility in different scenarios.

While powerful, these features come with important considerations around thread safety, performance scaling, and exception handling. For optimal results, carefully benchmark your specific use cases, understand the characteristics of your data and operations, and follow best practices for parallel programming.

As multi-core processors continue to be the norm, the ability to easily parallelize algorithms becomes increasingly valuable. C++17's parallel algorithms represent a significant step toward making parallel programming more accessible to C++ developers, enabling them to write high-performance code that scales well on modern hardware.