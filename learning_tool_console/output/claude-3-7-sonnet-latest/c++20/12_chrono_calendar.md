# C++20 Calendar and Time Zone Support in std::chrono

## Introduction

The C++20 standard introduces comprehensive calendar and time zone support to the `std::chrono` library, significantly expanding its capabilities beyond the time-point and duration facilities provided in C++11. This major enhancement addresses a long-standing gap in the C++ Standard Library by providing standardized facilities for working with calendrical types (years, months, days), time zones, and formatting/parsing of date and time representations. Prior to C++20, developers had to rely on operating system APIs, external libraries like Boost.Date_Time, or Howard Hinnant's date library (which served as the basis for much of this new functionality). With these additions, C++ now offers a complete, type-safe, and platform-independent date and time library that integrates seamlessly with the existing chrono components.

## Calendar Types

### Basic Calendar Types

C++20 introduces several fundamental calendar types in the `std::chrono` namespace, including:

- `year`: Represents a year value
- `month`: Represents a month of the year (January through December)
- `day`: Represents a day of the month (1 through 31)
- `weekday`: Represents a day of the week (Sunday through Saturday)

These types are strongly typed and provide range checking:

```cpp
#include <chrono>
#include <iostream>

int main() {
    using namespace std::chrono;
    
    // Creating basic calendar types
    year y{2023};
    month m{3};  // March
    day d{15};
    weekday wd{Sunday};  // weekday can be constructed from std::chrono::Sunday, etc.
    
    // Range checking and validity
    try {
        month invalid_month{13};  // This will throw an exception
    } catch (const std::exception& e) {
        std::cout << "Exception caught: " << e.what() << std::endl;
    }
    
    // Arithmetic operations
    year next_year = y + years{1};
    month prev_month = m - months{1};
    
    // Comparison operations
    bool is_future = y > 2022y;  // Using year literal
    
    // Output
    std::cout << "Year: " << static_cast<int>(y) << std::endl;
    std::cout << "Month: " << static_cast<unsigned>(m) << std::endl;
    std::cout << "Day: " << static_cast<unsigned>(d) << std::endl;
    
    return 0;
}
```

### Compound Calendar Types

C++20 also introduces compound types that combine these basic calendar types:

- `year_month`: Combines year and month
- `month_day`: Combines month and day
- `month_day_last`: Represents the last day of a specific month
- `month_weekday`: Represents a specific weekday in a specific month (e.g., "first Sunday in May")
- `month_weekday_last`: Represents the last occurrence of a specific weekday in a specific month
- `year_month_day`: Combines year, month, and day to represent a complete calendar date
- `year_month_day_last`: Represents the last day of a specific month in a specific year

Here's an example of using these compound types:

```cpp
#include <chrono>
#include <iostream>
#include <format> // C++20 feature

int main() {
    using namespace std::chrono;
    
    // Creating compound calendar types
    year_month ym{2023y, March};
    month_day md{March, day{15}};
    year_month_day ymd{2023y, March, day{15}};
    
    // Getting the last day of a month
    year_month_day_last ymdl{2023y, month_day_last{February}};
    
    // Finding specific weekdays
    month_weekday first_sunday_in_may{May, weekday_indexed{Sunday, 1}};
    month_weekday_last last_friday_in_june{June, weekday_last{Friday}};
    
    // Convert to/from sys_days (which is a time_point)
    sys_days dp = sys_days{ymd};
    year_month_day ymd_from_dp = year_month_day{dp};
    
    // Calculating dates
    year_month_day today = year_month_day{floor<days>(system_clock::now())};
    year_month_day next_month = today + months{1};
    
    // Output
    std::cout << "Date: " << std::format("{}/{}/{}", 
        static_cast<int>(ymd.year()), 
        static_cast<unsigned>(ymd.month()), 
        static_cast<unsigned>(ymd.day())) << std::endl;
    
    std::cout << "Last day of Feb 2023: " << 
        static_cast<unsigned>(year_month_day{ymdl}.day()) << std::endl;
    
    return 0;
}
```

## Time-of-Day Types

C++20 adds time-of-day types to complement the calendar types:

- `hh_mm_ss`: Represents hours, minutes, seconds, and subseconds

```cpp
#include <chrono>
#include <iostream>

int main() {
    using namespace std::chrono;
    
    // Creating time components
    hours h{14};  // 2 PM
    minutes m{30};
    seconds s{45};
    milliseconds ms{500};
    
    // Creating an hh_mm_ss from a duration
    hh_mm_ss time{h + m + s + ms};
    
    // Accessing components
    std::cout << "Time: " 
              << time.hours().count() << "h "
              << time.minutes().count() << "m "
              << time.seconds().count() << "s "
              << duration_cast<milliseconds>(time.subseconds()).count() << "ms"
              << std::endl;
    
    // Creating from total seconds
    auto total_seconds = seconds{54321};
    hh_mm_ss time_from_seconds{total_seconds};
    std::cout << "Time from " << total_seconds.count() << " seconds: "
              << time_from_seconds.hours().count() << "h "
              << time_from_seconds.minutes().count() << "m "
              << time_from_seconds.seconds().count() << "s"
              << std::endl;
    
    return 0;
}
```

## Date and Time Integration

The new calendar and time-of-day types can be combined with the existing `std::chrono::time_point` types:

```cpp
#include <chrono>
#include <iostream>
#include <format>

int main() {
    using namespace std::chrono;
    
    // Current time point
    auto now = system_clock::now();
    
    // Convert to calendar representation
    auto today = year_month_day{floor<days>(now)};
    
    // Extract time of day
    auto time_since_midnight = now - floor<days>(now);
    auto time_of_day = hh_mm_ss{time_since_midnight};
    
    // Print complete date and time
    std::cout << std::format("Date: {}/{}/{}", 
        static_cast<int>(today.year()),
        static_cast<unsigned>(today.month()),
        static_cast<unsigned>(today.day())) << std::endl;
        
    std::cout << std::format("Time: {:02}:{:02}:{:02}.{:03}", 
        time_of_day.hours().count(),
        time_of_day.minutes().count(),
        time_of_day.seconds().count(),
        duration_cast<milliseconds>(time_of_day.subseconds()).count()) << std::endl;
    
    // Date arithmetic
    auto tomorrow = today + days{1};
    auto next_week = today + weeks{1};
    auto last_month = today - months{1};
    
    std::cout << "Tomorrow: " << std::format("{}/{}/{}", 
        static_cast<int>(tomorrow.year()),
        static_cast<unsigned>(tomorrow.month()),
        static_cast<unsigned>(tomorrow.day())) << std::endl;
    
    return 0;
}
```

## Time Zone Support

One of the most significant additions in C++20 is comprehensive time zone support. This feature integrates the IANA time zone database, allowing C++ programs to handle time zone conversions and daylight saving time transitions correctly.

### Time Zone Database

The time zone database is encapsulated in the `std::chrono::tzdb` class, which provides access to the collection of time zones:

```cpp
#include <chrono>
#include <iostream>

int main() {
    using namespace std::chrono;
    
    // Access the time zone database
    const tzdb& time_zone_db = get_tzdb();
    
    // List available time zones
    std::cout << "Available time zones:" << std::endl;
    int count = 0;
    for (const auto& zone : time_zone_db.zones) {
        std::cout << zone.name() << ", ";
        if (++count % 5 == 0) std::cout << std::endl;
        if (count >= 25) break;  // Just show a sample
    }
    std::cout << "... and more (" << time_zone_db.zones.size() << " total)" << std::endl;
    
    // Get information about the current tzdb version
    std::cout << "Time zone database version: " << time_zone_db.version << std::endl;
    
    return 0;
}
```

### Working with Time Zones

The library provides the `zoned_time` class, which associates a time point with a specific time zone:

```cpp
#include <chrono>
#include <iostream>
#include <format>

int main() {
    using namespace std::chrono;
    
    // Get current time in UTC
    auto now = system_clock::now();
    
    // Create zoned_time objects for different time zones
    zoned_time utc{current_zone(), now};  // Current system timezone
    zoned_time new_york{"America/New_York", now};
    zoned_time tokyo{"Asia/Tokyo", now};
    zoned_time london{"Europe/London", now};
    
    // Format and display the times
    std::cout << "Current time in different time zones:" << std::endl;
    std::cout << "UTC:       " << utc << std::endl;
    std::cout << "New York:  " << new_york << std::endl;
    std::cout << "Tokyo:     " << tokyo << std::endl;
    std::cout << "London:    " << london << std::endl;
    
    // Converting between time zones
    zoned_time ny_to_tokyo{tokyo.get_time_zone(), new_york};
    std::cout << "When it's " << new_york << " in New York," << std::endl;
    std::cout << "it's " << ny_to_tokyo << " in Tokyo" << std::endl;
    
    return 0;
}
```

### Handling Daylight Saving Time

The time zone support correctly handles daylight saving time transitions:

```cpp
#include <chrono>
#include <iostream>
#include <format>

int main() {
    using namespace std::chrono;
    
    // Define a time zone
    const time_zone* new_york = locate_zone("America/New_York");
    
    // Create a date during standard time
    year_month_day winter_date{2023y, January, day{15}};
    auto winter_midnight = local_days{winter_date} + hours{0};
    
    // Create a date during daylight saving time
    year_month_day summer_date{2023y, July, day{15}};
    auto summer_midnight = local_days{summer_date} + hours{0};
    
    // Create zoned_time objects
    zoned_time winter_zt{new_york, winter_midnight};
    zoned_time summer_zt{new_york, summer_midnight};
    
    // Get UTC offsets
    auto winter_info = new_york->get_info(winter_zt.get_sys_time());
    auto summer_info = new_york->get_info(summer_zt.get_sys_time());
    
    std::cout << "Winter (Jan 15) in New York:" << std::endl;
    std::cout << "  Local time: " << winter_zt.get_local_time() << std::endl;
    std::cout << "  UTC offset: " << winter_info.offset << std::endl;
    std::cout << "  DST: " << (winter_info.save == 0min ? "No" : "Yes") << std::endl;
    std::cout << "  Abbreviation: " << winter_info.abbrev << std::endl;
    
    std::cout << "Summer (Jul 15) in New York:" << std::endl;
    std::cout << "  Local time: " << summer_zt.get_local_time() << std::endl;
    std::cout << "  UTC offset: " << summer_info.offset << std::endl;
    std::cout << "  DST: " << (summer_info.save == 0min ? "No" : "Yes") << std::endl;
    std::cout << "  Abbreviation: " << summer_info.abbrev << std::endl;
    
    // Handling ambiguous times (during "fall back")
    year_month_day dst_end_date{2023y, November, day{5}};
    auto ambiguous_time = local_days{dst_end_date} + hours{1} + minutes{30};
    
    // choose earliest and choose latest resolve ambiguity differently
    zoned_time ambiguous_earliest{new_york, ambiguous_time, choose::earliest};
    zoned_time ambiguous_latest{new_york, ambiguous_time, choose::latest};
    
    std::cout << "Ambiguous time (1:30 AM during 'fall back'):" << std::endl;
    std::cout << "  Earliest interpretation: " << ambiguous_earliest << std::endl;
    std::cout << "  Latest interpretation: " << ambiguous_latest << std::endl;
    
    return 0;
}
```

## Formatting and Parsing

C++20 introduces date and time formatting capabilities that integrate with the new `<format>` library:

### Formatting Dates and Times

```cpp
#include <chrono>
#include <iostream>
#include <format>

int main() {
    using namespace std::chrono;
    
    // Current time
    auto now = system_clock::now();
    auto today = year_month_day{floor<days>(now)};
    
    // Basic formatting with std::format
    std::cout << std::format("ISO date: {:%F}", now) << std::endl;
    std::cout << std::format("Time: {:%T}", now) << std::endl;
    std::cout << std::format("Date and time: {:%c}", now) << std::endl;
    std::cout << std::format("Custom format: {:%Y-%m-%d %H:%M:%S}", now) << std::endl;
    
    // Formatting with time zones
    zoned_time zt{"America/Los_Angeles", now};
    std::cout << std::format("Los Angeles time: {:%F %T %Z}", zt) << std::endl;
    
    // Formatting calendar types
    std::cout << std::format("Year: {}", today.year()) << std::endl;
    std::cout << std::format("Month: {:%B}", today.month()) << std::endl;
    std::cout << std::format("Day: {}", today.day()) << std::endl;
    
    // Formatting with localization (requires C++20 std::format with locale support)
    try {
        std::cout << std::format(std::locale("en_US.UTF-8"), 
                                 "US formatted date: {:%x}", now) << std::endl;
        std::cout << std::format(std::locale("de_DE.UTF-8"), 
                                 "German formatted date: {:%x}", now) << std::endl;
    } catch (const std::exception& e) {
        std::cout << "Locale formatting error: " << e.what() << std::endl;
    }
    
    return 0;
}
```

### Parsing Dates and Times

C++20 introduces the `std::chrono::parse` function template for parsing dates and times:

```cpp
#include <chrono>
#include <iostream>
#include <format>

int main() {
    using namespace std::chrono;
    
    // Parsing a date string
    std::string date_str = "2023-05-15";
    year_month_day ymd{};
    std::istringstream is{date_str};
    
    from_stream(is, "%Y-%m-%d", ymd);
    
    if (is.fail()) {
        std::cout << "Failed to parse date" << std::endl;
    } else {
        std::cout << "Parsed date: " << std::format("{}/{}/{}", 
            static_cast<int>(ymd.year()),
            static_cast<unsigned>(ymd.month()), 
            static_cast<unsigned>(ymd.day())) << std::endl;
    }
    
    // Parsing a time string
    std::string time_str = "14:30:45";
    hh_mm_ss<seconds> time{};
    std::istringstream is2{time_str};
    
    from_stream(is2, "%H:%M:%S", time);
    
    if (is2.fail()) {
        std::cout << "Failed to parse time" << std::endl;
    } else {
        std::cout << "Parsed time: " << std::format("{:02}:{:02}:{:02}", 
            time.hours().count(),
            time.minutes().count(), 
            time.seconds().count()) << std::endl;
    }
    
    // Parsing a date and time with timezone
    std::string datetime_str = "2023-05-15 14:30:45 -0400";
    zoned_time<seconds> zt{current_zone(), system_clock::now()};
    std::istringstream is3{datetime_str};
    
    from_stream(is3, "%Y-%m-%d %H:%M:%S %z", zt);
    
    if (is3.fail()) {
        std::cout << "Failed to parse date and time" << std::endl;
    } else {
        std::cout << "Parsed date and time: " << zt << std::endl;
    }
    
    return 0;
}
```

## Practical Examples

### Calculating Age in Years

```cpp
#include <chrono>
#include <iostream>

int main() {
    using namespace std::chrono;
    
    // Define birth date
    year_month_day birth_date{1990y, January, day{15}};
    
    // Get current date
    auto today = year_month_day{floor<days>(system_clock::now())};
    
    // Convert to sys_days for arithmetic
    sys_days birth_days = sys_days{birth_date};
    sys_days today_days = sys_days{today};
    
    // Calculate difference in days
    days age_in_days = today_days - birth_days;
    
    // Approximate age in years (not accounting for leap years in a precise way)
    int age_in_years = age_in_days.count() / 365;
    
    // A more precise calculation
    int years = static_cast<int>(today.year()) - static_cast<int>(birth_date.year());
    if (today.month() < birth_date.month() || 
        (today.month() == birth_date.month() && today.day() < birth_date.day())) {
        years--;
    }
    
    std::cout << "Age in days: " << age_in_days.count() << std::endl;
    std::cout << "Approximate age in years: " << age_in_years << std::endl;
    std::cout << "Precise age in years: " << years << std::endl;
    
    return 0;
}
```

### Business Days Calculator

```cpp
#include <chrono>
#include <iostream>
#include <vector>

// Function to check if a date is a weekend
bool is_weekend(const std::chrono::year_month_day& date) {
    using namespace std::chrono;
    weekday wd{sys_days{date}};
    return wd == Saturday || wd == Sunday;
}

// Function to check if a date is a holiday (simplified example)
bool is_holiday(const std::chrono::year_month_day& date) {
    using namespace std::chrono;
    
    // Example holidays for US 2023 (simplified)
    std::vector<year_month_day> holidays = {
        year_month_day{2023y, January, day{1}},    // New Year's Day
        year_month_day{2023y, January, day{16}},   // Martin Luther King Jr. Day
        year_month_day{2023y, February, day{20}},  // Presidents' Day
        year_month_day{2023y, May, day{29}},       // Memorial Day
        year_month_day{2023y, July, day{4}},       // Independence Day
        year_month_day{2023y, September, day{4}},  // Labor Day
        year_month_day{2023y, October, day{9}},    // Columbus Day
        year_month_day{2023y, November, day{11}},  // Veterans Day
        year_month_day{2023y, November, day{23}},  // Thanksgiving
        year_month_day{2023y, December, day{25}}   // Christmas
    };
    
    for (const auto& holiday : holidays) {
        if (holiday == date) {
            return true;
        }
    }
    
    return false;
}

// Function to calculate business days between two dates
int business_days_between(const std::chrono::year_month_day& start_date,
                           const std::chrono::year_month_day& end_date) {
    using namespace std::chrono;
    
    sys_days start = sys_days{start_date};
    sys_days end = sys_days{end_date};
    
    if (start > end) {
        return -business_days_between(end_date, start_date);
    }
    
    int business_days = 0;
    sys_days current = start;
    
    while (current <= end) {
        year_month_day ymd{current};
        if (!is_weekend(ymd) && !is_holiday(ymd)) {
            business_days++;
        }
        current += days{1};
    }
    
    return business_days;
}

int main() {
    using namespace std::chrono;
    
    // Define start and end dates
    year_month_day start_date{2023y, June, day{1}};
    year_month_day end_date{2023y, June, day{30}};
    
    // Calculate business days
    int days = business_days_between(start_date, end_date);
    
    std::cout << "From " << static_cast<int>(start_date.year()) << "-"
              << static_cast<unsigned>(start_date.month()) << "-"
              << static_cast<unsigned>(start_date.day())
              << " to " << static_cast<int>(end_date.year()) << "-"
              << static_cast<unsigned>(end_date.month()) << "-"
              << static_cast<unsigned>(end_date.day())
              << " there are " << days << " business days." << std::endl;
    
    return 0;
}
```

### Flight Arrival Time Calculator

```cpp
#include <chrono>
#include <iostream>
#include <format>

int main() {
    using namespace std::chrono;
    
    // Flight departure: New York (JFK) on June 15, 2023 at 9:30 PM EDT
    zoned_time departure{
        locate_zone("America/New_York"),
        local_days{year_month_day{2023y, June, day{15}}} + hours{21} + minutes{30}
    };
    
    // Flight duration: 12 hours and 15 minutes
    auto duration = hours{12} + minutes{15};
    
    // Calculate arrival time in system time, then convert to Tokyo time zone
    auto arrival_sys_time = departure.get_sys_time() + duration;
    zoned_time arrival{locate_zone("Asia/Tokyo"), arrival_sys_time};
    
    // Display flight information
    std::cout << "Flight Information:" << std::endl;
    std::cout << "  Departure (New York): " << departure << std::endl;
    std::cout << "  Flight Duration: " << std::format("{}h {}m", 
                                         duration_cast<hours>(duration).count(),
                                         duration_cast<minutes>(duration % hours{1}).count()) << std::endl;
    std::cout << "  Arrival (Tokyo): " << arrival << std::endl;
    
    // Calculate local date information for the arrival
    year_month_day departure_ymd{floor<days>(departure.get_local_time())};
    year_month_day arrival_ymd{floor<days>(arrival.get_local_time())};
    
    // Calculate days difference
    auto departure_days = local_days{departure_ymd};
    auto arrival_days = local_days{arrival_ymd};
    auto days_diff = (arrival_days - departure_days).count();
    
    std::cout << "  Days later: " << days_diff << std::endl;
    
    return 0;
}
```

## Conclusion

C++20's calendar and time zone support in the `std::chrono` library represents one of the most significant enhancements to the Standard Library in recent years. It provides developers with a comprehensive suite of tools for dealing with dates, times, and time zones in a type-safe and platform-independent manner. The library's design emphasizes correctness, readability, and efficiency, with features like strong typing, range checking, and proper handling of calendar arithmetic.

By integrating with the IANA time zone database, the library accurately handles time zone conversions and daylight saving time transitions, solving a notoriously difficult problem in software development. The integration with the `<format>` library further enhances its usability, allowing for flexible formatting and parsing of date and time values.

These additions make C++ competitive with other languages that have long had robust date/time libraries as part of their standard offerings. For C++ developers, this means no longer needing to rely on external libraries or platform-specific code for common date and time operations, leading to more portable, readable, and maintainable code.