# Modern C++ String Conversion and Regular Expression Support

## Introduction

C++11 introduced significant improvements to string handling and added a standardized regular expression library. Before C++11, programmers typically relied on C-style functions like `sprintf`, `atoi`, and external libraries for regular expressions. The new features provide type-safe, more convenient alternatives that integrate seamlessly with the C++ type system. This article explores the string conversion functions (`std::to_string`, `std::stoi`, and related functions) and the regular expression library (`<regex>`), offering detailed explanations and practical examples.

## String Conversion Functions

### std::to_string

The `std::to_string` function converts numeric types to string representations. It provides a simple, type-safe way to convert numbers to strings without using `std::stringstream` or C-style functions.

#### Function Signature

The `std::to_string` function has multiple overloads:

```cpp
string to_string(int value);
string to_string(long value);
string to_string(long long value);
string to_string(unsigned value);
string to_string(unsigned long value);
string to_string(unsigned long long value);
string to_string(float value);
string to_string(double value);
string to_string(long double value);
```

#### Basic Usage Examples

```cpp
#include <iostream>
#include <string>

int main() {
    // Integer conversion
    int i = 42;
    std::string i_str = std::to_string(i);
    std::cout << "Integer to string: " << i_str << std::endl;
    
    // Floating-point conversion
    double d = 3.14159;
    std::string d_str = std::to_string(d);
    std::cout << "Double to string: " << d_str << std::endl;
    
    // Large number conversion
    long long large = 1234567890123456789LL;
    std::string large_str = std::to_string(large);
    std::cout << "Large number to string: " << large_str << std::endl;
    
    // Concatenating with other strings
    std::string message = "The answer is " + std::to_string(42) + "!";
    std::cout << message << std::endl;
    
    return 0;
}
```

#### Limitations

While `std::to_string` is convenient, it has some limitations:

1. No control over formatting (precision, decimal points, etc.)
2. Locale-independent (always uses the "C" locale)
3. May include trailing zeros for floating-point numbers

For more formatting control, `std::stringstream` or `std::format` (C++20) are better alternatives:

```cpp
#include <iostream>
#include <string>
#include <sstream>
#include <iomanip>

int main() {
    double value = 3.14159;
    
    // Using to_string (fixed representation with default precision)
    std::string str1 = std::to_string(value);
    
    // Using stringstream for formatting control
    std::stringstream ss;
    ss << std::fixed << std::setprecision(2) << value;
    std::string str2 = ss.str();
    
    std::cout << "to_string: " << str1 << std::endl;
    std::cout << "stringstream: " << str2 << std::endl;
    
    return 0;
}
```

### String to Number Conversions

C++11 introduced a family of functions to convert strings to various numeric types. These replace the C-style functions like `atoi()`, `atof()`, etc., and provide better error handling.

#### Function Signatures

```cpp
int stoi(const string& str, size_t* pos = nullptr, int base = 10);
long stol(const string& str, size_t* pos = nullptr, int base = 10);
long long stoll(const string& str, size_t* pos = nullptr, int base = 10);
unsigned long stoul(const string& str, size_t* pos = nullptr, int base = 10);
unsigned long long stoull(const string& str, size_t* pos = nullptr, int base = 10);
float stof(const string& str, size_t* pos = nullptr);
double stod(const string& str, size_t* pos = nullptr);
long double stold(const string& str, size_t* pos = nullptr);
```

Parameters:
- `str`: The input string to convert
- `pos`: Optional pointer to a variable that will store the position of the first character after the number
- `base`: Optional base for the conversion (only for integer types)

#### Basic Usage Examples

```cpp
#include <iostream>
#include <string>

int main() {
    // Basic conversions
    std::string int_str = "42";
    int i = std::stoi(int_str);
    std::cout << "String to int: " << i << std::endl;
    
    std::string float_str = "3.14159";
    float f = std::stof(float_str);
    std::cout << "String to float: " << f << std::endl;
    
    std::string double_str = "2.71828";
    double d = std::stod(double_str);
    std::cout << "String to double: " << d << std::endl;
    
    // Using different bases
    std::string hex_str = "2A";
    int hex_value = std::stoi(hex_str, nullptr, 16);
    std::cout << "Hex string to int: " << hex_value << std::endl;
    
    std::string bin_str = "101010";
    int bin_value = std::stoi(bin_str, nullptr, 2);
    std::cout << "Binary string to int: " << bin_value << std::endl;
    
    return 0;
}
```

#### Handling Position and Parsing Partial Strings

The `pos` parameter allows you to track where the number parsing ended and to parse only part of a string:

```cpp
#include <iostream>
#include <string>

int main() {
    std::string mixed = "42 is the answer";
    size_t pos = 0;
    
    int value = std::stoi(mixed, &pos);
    std::cout << "Parsed value: " << value << std::endl;
    std::cout << "Parsing stopped at position: " << pos << std::endl;
    std::cout << "Remaining text: \"" << mixed.substr(pos) << "\"" << std::endl;
    
    // Parse a number within text
    std::string data = "Price: 199.99 USD";
    size_t price_start = data.find_first_of("0123456789");
    
    if (price_start != std::string::npos) {
        double price = std::stod(data.substr(price_start), &pos);
        std::cout << "Price value: " << price << std::endl;
    }
    
    return 0;
}
```

#### Error Handling

These functions throw exceptions when they encounter errors:

```cpp
#include <iostream>
#include <string>
#include <stdexcept>

int main() {
    try {
        // Invalid integer
        std::string not_a_number = "abc";
        int value = std::stoi(not_a_number);
    } catch (const std::invalid_argument& e) {
        std::cout << "Invalid argument: " << e.what() << std::endl;
    }
    
    try {
        // Out of range for the target type
        std::string too_large = "99999999999999999999999";
        int value = std::stoi(too_large);
    } catch (const std::out_of_range& e) {
        std::cout << "Out of range: " << e.what() << std::endl;
    }
    
    // Example of safer parsing with error checking
    std::string user_input = "42x";
    size_t pos = 0;
    
    try {
        int value = std::stoi(user_input, &pos);
        
        if (pos < user_input.size()) {
            std::cout << "Warning: Parsed only " << pos << " characters. ";
            std::cout << "Remaining text: \"" << user_input.substr(pos) << "\"" << std::endl;
        } else {
            std::cout << "Successfully parsed entire input: " << value << std::endl;
        }
    } catch (const std::exception& e) {
        std::cout << "Error: " << e.what() << std::endl;
    }
    
    return 0;
}
```

## Regular Expression Support (std::regex)

C++11 introduced a standardized regular expression library, eliminating the need for external libraries like Boost.Regex or PCRE.

### Core Components

The C++ regex library consists of several key components:

1. **std::regex**: A regular expression object
2. **std::regex_match**: Checks if an entire string matches a pattern
3. **std::regex_search**: Searches for a pattern within a string
4. **std::regex_replace**: Replaces matched patterns
5. **std::match_results**: Stores the results of a match operation (usually used as `std::smatch` for strings)
6. **std::regex_iterator**: Iterates through all matches in a sequence
7. **std::regex_token_iterator**: Iterates through subexpressions of matches or non-matching subsequences

### Basic Usage Examples

#### Pattern Matching

```cpp
#include <iostream>
#include <string>
#include <regex>

int main() {
    // Simple regex matching
    std::string text = "Hello, C++11!";
    std::regex pattern("Hello, C\\+\\+11!");  // Need to escape + characters
    
    if (std::regex_match(text, pattern)) {
        std::cout << "Text matches the pattern" << std::endl;
    } else {
        std::cout << "No match" << std::endl;
    }
    
    // Using a raw string literal to avoid excessive escaping
    std::regex better_pattern(R"(Hello, C\+\+11!)");
    
    if (std::regex_match(text, better_pattern)) {
        std::cout << "Text matches the better pattern" << std::endl;
    }
    
    return 0;
}
```

#### Capturing Groups

```cpp
#include <iostream>
#include <string>
#include <regex>

int main() {
    std::string email = "john.doe@example.com";
    std::regex pattern(R"(([a-z\.]+)@([a-z\.]+)\.([a-z]+))");
    std::smatch matches;
    
    if (std::regex_match(email, matches, pattern)) {
        std::cout << "Full match: " << matches[0].str() << std::endl;
        std::cout << "Username: " << matches[1].str() << std::endl;
        std::cout << "Domain: " << matches[2].str() << std::endl;
        std::cout << "TLD: " << matches[3].str() << std::endl;
        
        // Using named iteration
        std::cout << "All captures:" << std::endl;
        for (size_t i = 0; i < matches.size(); ++i) {
            std::cout << "  [" << i << "]: " << matches[i].str() << std::endl;
        }
    }
    
    return 0;
}
```

#### Searching Within Text

```cpp
#include <iostream>
#include <string>
#include <regex>

int main() {
    std::string text = "The quick brown fox jumps over the lazy dog";
    std::regex word_pattern(R"(\b\w{5}\b)");  // Match 5-letter words
    std::smatch matches;
    
    std::cout << "5-letter words in the text:" << std::endl;
    
    // Search and iterate through all matches
    std::string::const_iterator searchStart(text.cbegin());
    while (std::regex_search(searchStart, text.cend(), matches, word_pattern)) {
        std::cout << "  " << matches[0].str() << " at position " 
                  << matches[0].first - text.cbegin() << std::endl;
        searchStart = matches[0].second;
    }
    
    return 0;
}
```

#### Using regex_iterator

```cpp
#include <iostream>
#include <string>
#include <regex>

int main() {
    std::string text = "2023-10-15, 2022-05-22, and 2021-12-01 are dates";
    std::regex date_pattern(R"((\d{4})-(\d{2})-(\d{2}))");
    
    std::cout << "Dates found:" << std::endl;
    
    auto words_begin = std::sregex_iterator(
        text.begin(), text.end(), date_pattern);
    auto words_end = std::sregex_iterator();
    
    for (std::sregex_iterator i = words_begin; i != words_end; ++i) {
        std::smatch match = *i;
        std::cout << "  Full date: " << match[0].str() << std::endl;
        std::cout << "    Year: " << match[1].str() << std::endl;
        std::cout << "    Month: " << match[2].str() << std::endl;
        std::cout << "    Day: " << match[3].str() << std::endl;
    }
    
    std::cout << "Total dates found: " 
              << std::distance(words_begin, words_end) << std::endl;
    
    return 0;
}
```

#### Text Replacement

```cpp
#include <iostream>
#include <string>
#include <regex>

int main() {
    std::string text = "The year is 2023, and C++11 was released in 2011.";
    
    // Basic replacement - replace all years with "YYYY"
    std::regex year_pattern(R"(\b\d{4}\b)");
    std::string result1 = std::regex_replace(text, year_pattern, "YYYY");
    std::cout << "Basic replacement: " << result1 << std::endl;
    
    // Backreference in replacement
    std::regex cpp_pattern(R"(C\+\+(\d+))");
    std::string result2 = std::regex_replace(text, cpp_pattern, "C++$1 (C plus plus$1)");
    std::cout << "With backreference: " << result2 << std::endl;
    
    // Format flags
    std::string result3 = std::regex_replace(text, year_pattern, "[$&]", 
                                            std::regex_constants::format_default);
    std::cout << "With format_default: " << result3 << std::endl;
    
    // Replace only the first occurrence
    std::string result4 = std::regex_replace(text, year_pattern, "YYYY", 
                                            std::regex_constants::format_first_only);
    std::cout << "First occurrence only: " << result4 << std::endl;
    
    return 0;
}
```

### Regex Syntax Options

The C++ regex library supports different syntax flavors through the `std::regex_constants::syntax_option_type` flags:

```cpp
#include <iostream>
#include <string>
#include <regex>

int main() {
    std::string text = "The price is $10.99";
    
    // Using ECMAScript syntax (default)
    std::regex pattern1(R"(\$\d+\.\d+)", std::regex_constants::ECMAScript);
    
    // Using basic POSIX syntax
    std::regex pattern2(R"(\$[0-9]\+\.[0-9]\+)", std::regex_constants::basic);
    
    // Using extended POSIX syntax
    std::regex pattern3(R"(\$[0-9]+\.[0-9]+)", std::regex_constants::extended);
    
    // Using grep syntax
    std::regex pattern4(R"(\$[0-9]\+\.[0-9]\+)", std::regex_constants::grep);
    
    // Case-insensitive matching
    std::regex pattern5("price", std::regex_constants::ECMAScript | 
                                 std::regex_constants::icase);
    
    // Check which patterns match
    std::cout << "ECMAScript: " 
              << std::regex_search(text, pattern1) << std::endl;
    std::cout << "Basic POSIX: " 
              << std::regex_search(text, pattern2) << std::endl;
    std::cout << "Extended POSIX: " 
              << std::regex_search(text, pattern3) << std::endl;
    std::cout << "grep: " 
              << std::regex_search(text, pattern4) << std::endl;
    std::cout << "Case-insensitive: " 
              << std::regex_search(text, pattern5) << std::endl;
    
    return 0;
}
```

### Tokenization with regex_token_iterator

```cpp
#include <iostream>
#include <string>
#include <regex>
#include <vector>

int main() {
    std::string csv = "Alice,30,New York,Engineer";
    std::regex separator(",");
    
    // Split by delimiter
    std::vector<std::string> tokens;
    std::copy(std::sregex_token_iterator(csv.begin(), csv.end(), separator, -1),
              std::sregex_token_iterator(),
              std::back_inserter(tokens));
    
    std::cout << "CSV fields:" << std::endl;
    for (const auto& token : tokens) {
        std::cout << "  " << token << std::endl;
    }
    
    // More complex example - extract HTML tag contents
    std::string html = "<p>First paragraph</p><p>Second paragraph</p><div>A div</div>";
    std::regex tag_pattern("<([a-z]+)>([^<]+)</\\1>");
    
    // Extract the text between tags (capture group 2)
    std::cout << "\nHTML tag contents:" << std::endl;
    std::sregex_token_iterator it(html.begin(), html.end(), tag_pattern, 2);
    std::sregex_token_iterator end;
    
    while (it != end) {
        std::cout << "  " << *it++ << std::endl;
    }
    
    return 0;
}
```

### Performance Considerations

The standard library regex implementation can be less performant than specialized regex libraries for complex patterns or large inputs. Here are some tips:

1. Compile patterns once and reuse them when possible
2. Consider using string algorithms for simple cases
3. Be cautious with complex patterns, especially those involving heavy backtracking
4. Profile your code with realistic inputs

```cpp
#include <iostream>
#include <string>
#include <regex>
#include <chrono>
#include <vector>

// Example of reusing a compiled regex pattern for performance
void process_emails(const std::vector<std::string>& emails) {
    // Compile pattern once
    std::regex email_pattern(R"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})");
    
    int valid_count = 0;
    
    auto start = std::chrono::high_resolution_clock::now();
    
    for (const auto& email : emails) {
        if (std::regex_match(email, email_pattern)) {
            valid_count++;
        }
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> duration = end - start;
    
    std::cout << "Validated " << valid_count << " emails out of " 
              << emails.size() << " in " << duration.count() 
              << " milliseconds" << std::endl;
}

int main() {
    std::vector<std::string> sample_emails = {
        "user@example.com",
        "invalid.email",
        "another_user@domain.co.uk",
        "no@domain",
        "test.email@subdomain.example.org"
    };
    
    process_emails(sample_emails);
    
    return 0;
}
```

## Conclusion

The string conversion functions and regular expression support introduced in C++11 significantly improve string handling capabilities in modern C++. The `std::to_string` function and the `std::stoi` family provide type-safe, convenient alternatives to C-style conversions, making code more readable and safer. The built-in regular expression library eliminates the need for external dependencies when working with pattern matching and text processing.

These features integrate well with the rest of the C++ standard library and follow modern C++ design principles. While the regex implementation might not be as performant as specialized libraries for complex cases, it serves well for most common text processing tasks.

By leveraging these modern C++ features, you can write more concise, type-safe, and maintainable code compared to using the older C-style string handling approaches.