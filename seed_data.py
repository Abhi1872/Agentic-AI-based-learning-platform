"""
Seed data script for Agentic AI Learning Platform
Run this to populate the database with UG Computer Science lessons and quizzes
"""
from app import app, db
from models import Student, Lesson, Quiz, QuizQuestion, Game, Teacher, ParentAccount, ParentStudentLink


def seed_lessons():
    """Create UG Computer Science lessons - Beginner to Advanced"""
    lessons_data = [
        {
            'title': 'Introduction to Programming',
            'description': 'Learn the fundamentals of programming and computational thinking',
            'subject': 'Computer Science',
            'category': 'programming',
            'difficulty_tier': 'beginner',
            'estimated_time': 15,
            'order_index': 1,
            'content_easy': """Welcome to Programming!

Programming is like giving instructions to a computer. Just like you follow steps to make a sandwich, computers follow steps to do tasks.

What is a Program?
A program is a list of instructions that tells the computer what to do.

Simple Example:
Imagine telling a robot to make tea:
1. Take a cup
2. Add water
3. Heat the water
4. Add tea bag
5. Wait 3 minutes
6. Remove tea bag

That's programming! You give clear steps, one at a time.

Key Words to Remember:
- Code: The instructions we write
- Program: A complete set of instructions
- Computer: The machine that follows our instructions

Fun Fact: Computers are very fast but not smart - they only do exactly what we tell them!""",
            'content_medium': """Introduction to Programming Concepts

Programming is the process of creating instructions that a computer can understand and execute. These instructions are written in programming languages.

Core Concepts:

1. Variables - Storage boxes for data
   Example: name = "Alice"
   This stores the text "Alice" in a box called "name"

2. Data Types - Different kinds of information
   - Numbers: 1, 2, 3.14
   - Text (Strings): "Hello World"
   - True/False (Boolean): True, False

3. Input/Output
   - Input: Getting information from the user
   - Output: Showing results to the user

4. Sequence
   - Instructions run one after another, top to bottom

Simple Python Example:
name = input("What is your name? ")
print("Hello, " + name + "!")

This program asks for your name and greets you.

Programming Languages:
- Python (beginner-friendly)
- JavaScript (for websites)
- Java (for applications)
- C++ (for games and systems)""",
            'content_advanced': """Programming Paradigms and Computational Thinking

Programming extends beyond syntax to encompass problem-solving methodologies and computational thinking.

Computational Thinking Components:
1. Decomposition - Breaking complex problems into smaller parts
2. Pattern Recognition - Identifying similarities and trends
3. Abstraction - Focusing on essential information
4. Algorithm Design - Creating step-by-step solutions

Programming Paradigms:

1. Procedural Programming
   - Sequential execution of instructions
   - Functions for code reuse
   - Example: C, Pascal

2. Object-Oriented Programming (OOP)
   - Data and functions bundled as objects
   - Concepts: Classes, Objects, Inheritance, Polymorphism
   - Example: Java, Python, C++

3. Functional Programming
   - Pure functions without side effects
   - Immutable data
   - Example: Haskell, Lisp

4. Event-Driven Programming
   - Program flow determined by events
   - Common in GUI and web applications

Code Quality Principles:
- DRY: Don't Repeat Yourself
- KISS: Keep It Simple, Stupid
- YAGNI: You Aren't Gonna Need It

Version Control:
Git is essential for tracking changes and collaboration.
Basic commands: git init, git add, git commit, git push"""
        },
        {
            'title': 'Variables and Data Types',
            'description': 'Understanding how computers store and handle different types of data',
            'subject': 'Computer Science',
            'category': 'programming',
            'difficulty_tier': 'beginner',
            'estimated_time': 20,
            'order_index': 2,
            'content_easy': """Variables and Data Types

What is a Variable?
A variable is like a labeled box where we store information.

Imagine you have boxes at home:
- A box labeled "Toys" for your toys
- A box labeled "Books" for your books

In programming:
- age = 10 (a box called "age" holding the number 10)
- name = "Sam" (a box called "name" holding the text "Sam")

Types of Data:

1. Numbers
   - Whole numbers: 1, 2, 3, 100
   - Decimal numbers: 3.14, 2.5

2. Text (Words)
   - "Hello"
   - "My name is Sam"

3. Yes or No (True/False)
   - Is it raining? True or False

Simple Example:
my_age = 12
my_name = "Jordan"
loves_coding = True

The computer remembers all these for us!""",
            'content_medium': """Variables and Data Types in Programming

Variables store data that can change during program execution. Data types define what kind of data can be stored.

Primitive Data Types:

1. Integer (int)
   - Whole numbers without decimals
   - Example: age = 25, count = -10

2. Float/Double
   - Decimal numbers
   - Example: price = 19.99, pi = 3.14159

3. String (str)
   - Text enclosed in quotes
   - Example: message = "Hello World"

4. Boolean (bool)
   - True or False values
   - Example: is_active = True

5. Character (char)
   - Single character
   - Example: grade = 'A'

Variable Naming Rules:
- Start with letter or underscore
- No spaces (use_underscores or camelCase)
- Case-sensitive (Name != name)
- Avoid reserved keywords

Type Conversion:
- str(100) converts 100 to "100"
- int("50") converts "50" to 50
- float("3.14") converts to 3.14

Constants:
Values that don't change, often in UPPERCASE:
PI = 3.14159
MAX_USERS = 100""",
            'content_advanced': """Advanced Data Types and Memory Management

Understanding data types at a deeper level involves memory allocation, type systems, and data structures.

Type Systems:

1. Static Typing (Java, C++)
   - Types checked at compile time
   - int age = 25;
   - Catches errors early

2. Dynamic Typing (Python, JavaScript)
   - Types checked at runtime
   - age = 25  # type inferred
   - More flexible but potential runtime errors

3. Strong vs Weak Typing
   - Strong: Strict type enforcement (Python)
   - Weak: Implicit type conversion (JavaScript)

Memory Representation:
- int (32-bit): -2,147,483,648 to 2,147,483,647
- long (64-bit): Much larger range
- float (32-bit): ~7 decimal digits precision
- double (64-bit): ~15 decimal digits precision

Reference Types:
- Objects, Arrays, Strings (in some languages)
- Stored on heap, variable holds memory address
- Garbage collection manages deallocation

Type Annotations (Python 3.5+):
def greet(name: str) -> str:
    return f"Hello, {name}"

Nullable Types:
- Optional values that can be None/null
- TypeScript: string | null
- Kotlin: String?

Immutability:
- Immutable: Cannot be changed after creation
- Strings in Python are immutable
- Benefits: Thread safety, predictability"""
        },
        {
            'title': 'Control Structures',
            'description': 'Learn how to control program flow with conditions and loops',
            'subject': 'Computer Science',
            'category': 'programming',
            'difficulty_tier': 'beginner',
            'estimated_time': 25,
            'order_index': 3,
            'content_easy': """Control Structures - Making Decisions

Programs can make decisions just like you do!

If-Then Decisions:
If it is raining, take an umbrella.
If you are hungry, eat food.

In code:
if weather == "rainy":
    take_umbrella()

Checking Conditions:
- Equal to: ==
- Not equal: !=
- Greater than: >
- Less than: <

Example:
age = 10
if age >= 10:
    print("You can ride the roller coaster!")
else:
    print("You need to be 10 or older.")

Loops - Doing Things Again and Again:

Counting Loop:
for i in range(5):
    print("Hello!")
This prints "Hello!" five times.

While Loop:
while hungry:
    eat_food()
Keep eating while you're hungry!

Loops help us avoid writing the same thing many times.""",
            'content_medium': """Control Flow Structures

Control structures determine the order in which statements are executed.

1. Conditional Statements:

if-elif-else:
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"

Comparison Operators:
== (equal), != (not equal)
> (greater), < (less)
>= (greater or equal), <= (less or equal)

Logical Operators:
and - Both conditions must be true
or - At least one condition must be true
not - Reverses the condition

if age >= 18 and has_license:
    can_drive = True

2. Loops:

For Loop (known iterations):
for i in range(1, 11):
    print(i)  # Prints 1 to 10

While Loop (unknown iterations):
count = 0
while count < 5:
    print(count)
    count += 1

Loop Control:
- break: Exit the loop immediately
- continue: Skip to next iteration
- pass: Do nothing (placeholder)

Nested Loops:
for i in range(3):
    for j in range(3):
        print(f"({i},{j})")""",
            'content_advanced': """Advanced Control Flow and Algorithm Patterns

Mastering control flow enables efficient algorithm design and complex program logic.

Switch/Match Statements:

Python 3.10+ Pattern Matching:
match command:
    case "start":
        initialize()
    case "stop":
        terminate()
    case _:
        unknown_command()

Short-Circuit Evaluation:
- and: Stops at first False
- or: Stops at first True
result = x != 0 and y/x > 2  # Prevents division by zero

Ternary Operators:
status = "adult" if age >= 18 else "minor"

Loop Patterns:

1. Accumulator Pattern:
total = 0
for num in numbers:
    total += num

2. Search Pattern:
found = None
for item in collection:
    if matches(item):
        found = item
        break

3. Filter Pattern:
evens = [x for x in numbers if x % 2 == 0]

Recursion vs Iteration:
Recursion - Function calls itself
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

Tail Recursion Optimization:
- Some languages optimize tail-recursive calls
- Converts to iteration for efficiency

Exception Handling:
try:
    result = risky_operation()
except ValueError as e:
    handle_error(e)
finally:
    cleanup()

Generator Functions:
def countdown(n):
    while n > 0:
        yield n
        n -= 1"""
        },
        {
            'title': 'Functions and Modular Programming',
            'description': 'Learn to organize code into reusable functions',
            'subject': 'Computer Science',
            'category': 'programming',
            'difficulty_tier': 'intermediate',
            'estimated_time': 25,
            'order_index': 4,
            'content_easy': """Functions - Reusable Code Blocks

What is a Function?
A function is like a recipe. You write it once and use it many times!

Example - A greeting function:
def say_hello(name):
    print("Hello, " + name + "!")

Using the function:
say_hello("Alice")  # Prints: Hello, Alice!
say_hello("Bob")    # Prints: Hello, Bob!

Parts of a Function:
1. Name: What we call it (say_hello)
2. Parameters: Information it needs (name)
3. Body: What it does (print the greeting)

Functions that Give Back Answers:
def add(a, b):
    return a + b

result = add(5, 3)  # result is 8

Why Use Functions?
- Write code once, use it many times
- Makes programs easier to read
- Easier to fix problems
- Can share with others

Think of functions like LEGO blocks - you can combine them to build bigger things!""",
            'content_medium': """Functions and Modular Programming

Functions encapsulate reusable code blocks that perform specific tasks.

Function Definition:
def function_name(parameters):
    '''Docstring - describes the function'''
    # Function body
    return result

Parameters and Arguments:

1. Positional Arguments:
def greet(name, greeting):
    return f"{greeting}, {name}!"
greet("Alice", "Hello")

2. Default Parameters:
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"
greet("Bob")  # Uses default greeting

3. Keyword Arguments:
greet(greeting="Hi", name="Carol")

4. *args and **kwargs:
def flexible(*args, **kwargs):
    print(args)    # Tuple of positional args
    print(kwargs)  # Dict of keyword args

Return Values:
- return exits function and returns value
- Functions without return give None
- Can return multiple values as tuple

Scope:
- Local: Variables inside function
- Global: Variables outside functions
- global keyword to modify global vars

Best Practices:
- One function, one task
- Meaningful names (calculate_tax, not ct)
- Keep functions short (under 20 lines ideal)
- Add docstrings for documentation""",
            'content_advanced': """Advanced Function Concepts and Functional Programming

Functions in modern programming extend beyond simple procedures to include higher-order functions and closures.

First-Class Functions:
Functions as objects that can be:
- Assigned to variables
- Passed as arguments
- Returned from functions

Higher-Order Functions:
def apply_twice(func, x):
    return func(func(x))

def double(n):
    return n * 2

result = apply_twice(double, 5)  # 20

Lambda Functions:
square = lambda x: x ** 2
numbers.sort(key=lambda x: x[1])

Map, Filter, Reduce:
# Map - apply function to all elements
doubled = list(map(lambda x: x*2, numbers))

# Filter - select elements
evens = list(filter(lambda x: x%2==0, numbers))

# Reduce - accumulate values
from functools import reduce
product = reduce(lambda a,b: a*b, numbers)

Closures:
def multiplier(n):
    def multiply(x):
        return x * n
    return multiply

triple = multiplier(3)
triple(5)  # 15

Decorators:
def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"Took {time.time()-start}s")
        return result
    return wrapper

@timing_decorator
def slow_function():
    time.sleep(1)

Partial Functions:
from functools import partial
add_five = partial(add, 5)

Recursion Patterns:
- Base case and recursive case
- Memoization for optimization
- Tail call optimization"""
        },
        {
            'title': 'Introduction to Data Structures',
            'description': 'Learn about organizing and storing data efficiently',
            'subject': 'Computer Science',
            'category': 'data_structures',
            'difficulty_tier': 'intermediate',
            'estimated_time': 30,
            'order_index': 5,
            'content_easy': """Data Structures - Organizing Information

What are Data Structures?
Just like you organize your room with shelves and boxes, data structures help organize information in a computer.

1. Lists (Arrays)
Think of a list like a line of people:
my_list = ["Apple", "Banana", "Cherry"]
- First item: my_list[0] = "Apple"
- Second item: my_list[1] = "Banana"

2. Dictionary (Like a real dictionary!)
Pairs of words and meanings:
my_dict = {"cat": "a furry pet", "dog": "a loyal friend"}
my_dict["cat"] gives "a furry pet"

3. Stack (Like a stack of plates)
- Add plates on top
- Take plates from top
Last In, First Out!

4. Queue (Like a line at a store)
- Join at the back
- Leave from the front
First In, First Out!

Why Learn This?
- Find things faster
- Save computer memory
- Make programs work better""",
            'content_medium': """Data Structures Fundamentals

Data structures organize data for efficient access and modification.

1. Arrays/Lists:
- Ordered collection with index access
- O(1) access by index
- O(n) search for value

fruits = ["apple", "banana", "cherry"]
fruits[0]      # "apple"
fruits.append("date")
fruits.pop()   # Removes last item

2. Dictionaries/Hash Maps:
- Key-value pairs
- O(1) average lookup

student = {
    "name": "Alice",
    "age": 20,
    "grades": [85, 90, 88]
}
student["name"]  # "Alice"

3. Sets:
- Unique elements only
- Fast membership testing

unique_nums = {1, 2, 3, 2}  # {1, 2, 3}
3 in unique_nums  # True

4. Tuples:
- Immutable ordered collection
- Hashable, can be dict keys

point = (3, 4)
x, y = point  # Unpacking

5. Stacks:
stack = []
stack.append(1)  # Push
stack.pop()      # Pop

6. Queues:
from collections import deque
queue = deque()
queue.append(1)     # Enqueue
queue.popleft()     # Dequeue

Choosing the Right Structure:
- Need order? List
- Need fast lookup? Dict/Set
- Need uniqueness? Set
- Need LIFO? Stack
- Need FIFO? Queue""",
            'content_advanced': """Advanced Data Structures and Complexity Analysis

Understanding data structure internals and trade-offs is crucial for algorithm design.

Time Complexity Summary:
Array:    Access O(1), Search O(n), Insert O(n)
HashMap:  Access O(1), Search O(1), Insert O(1)
Stack:    Push O(1), Pop O(1), Peek O(1)
Queue:    Enqueue O(1), Dequeue O(1)

Linked Lists:
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

Advantages: O(1) insertion/deletion at known position
Disadvantages: O(n) access, no random access

Types: Singly, Doubly, Circular

Trees:
- Hierarchical structure
- Root, nodes, leaves
- Binary Tree: Each node has max 2 children

Binary Search Tree (BST):
- Left child < parent < right child
- O(log n) search, insert, delete (balanced)

class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

Heaps:
- Complete binary tree
- Min-heap: Parent <= children
- Max-heap: Parent >= children
- O(log n) insert/delete, O(1) peek

Graphs:
- Nodes (vertices) connected by edges
- Directed vs Undirected
- Weighted vs Unweighted

Representations:
# Adjacency List
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D'],
}

# Adjacency Matrix
matrix[i][j] = 1  # Edge exists

Hash Tables:
- Hash function maps keys to indices
- Collision handling: Chaining, Open Addressing
- Load factor affects performance"""
        },
        {
            'title': 'Algorithms and Problem Solving',
            'description': 'Learn fundamental algorithms and problem-solving techniques',
            'subject': 'Computer Science',
            'category': 'algorithms',
            'difficulty_tier': 'intermediate',
            'estimated_time': 35,
            'order_index': 6,
            'content_easy': """Algorithms - Step by Step Solutions

What is an Algorithm?
An algorithm is a set of steps to solve a problem.

Example: Finding the biggest number
1. Look at the first number, remember it as "biggest"
2. Look at the next number
3. If it's bigger, this is now "biggest"
4. Repeat until no more numbers
5. The "biggest" is your answer!

Searching Algorithms:

Linear Search (Looking one by one):
- Start from first item
- Check each item
- Stop when you find it

Binary Search (For sorted items):
Like finding a word in a dictionary:
- Open to the middle
- Is your word before or after?
- Go to that half
- Repeat until found!

Sorting Algorithms:

Bubble Sort (Simple):
- Compare neighbors
- Swap if in wrong order
- Repeat until sorted

Why Learn Algorithms?
- Solve problems faster
- Use less computer power
- Think like a programmer!""",
            'content_medium': """Algorithms and Problem-Solving Strategies

Algorithms are precise sequences of steps that solve computational problems.

Big O Notation - Measuring Efficiency:
- O(1): Constant - same time regardless of size
- O(log n): Logarithmic - halving each step
- O(n): Linear - grows with input size
- O(n log n): Log-linear - efficient sorting
- O(n²): Quadratic - nested iterations
- O(2^n): Exponential - very slow

Searching Algorithms:

1. Linear Search - O(n)
def linear_search(arr, target):
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1

2. Binary Search - O(log n)
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

Sorting Algorithms:

1. Bubble Sort - O(n²)
2. Selection Sort - O(n²)
3. Insertion Sort - O(n²)
4. Merge Sort - O(n log n)
5. Quick Sort - O(n log n) average

Problem-Solving Steps:
1. Understand the problem
2. Plan your approach
3. Implement solution
4. Test with examples
5. Optimize if needed""",
            'content_advanced': """Advanced Algorithms and Complexity Theory

Mastering algorithms requires understanding design paradigms and complexity classes.

Algorithm Design Paradigms:

1. Divide and Conquer:
- Split problem into subproblems
- Solve subproblems recursively
- Combine solutions
Examples: Merge Sort, Quick Sort

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

2. Dynamic Programming:
- Optimal substructure
- Overlapping subproblems
- Memoization or tabulation

# Fibonacci with memoization
def fib(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib(n-1, memo) + fib(n-2, memo)
    return memo[n]

3. Greedy Algorithms:
- Make locally optimal choices
- Hope for global optimum
Example: Dijkstra's shortest path

4. Backtracking:
- Explore all possibilities
- Prune invalid paths
Example: N-Queens, Sudoku solver

Graph Algorithms:
- BFS: Level-order traversal, shortest path (unweighted)
- DFS: Explore depth first, cycle detection
- Dijkstra: Shortest path (weighted, positive)
- Bellman-Ford: Handles negative weights
- Kruskal/Prim: Minimum spanning tree

Complexity Classes:
- P: Solvable in polynomial time
- NP: Verifiable in polynomial time
- NP-Complete: Hardest problems in NP
- NP-Hard: At least as hard as NP-Complete"""
        },
        {
            'title': 'Database Fundamentals',
            'description': 'Learn how to store and retrieve data using databases',
            'subject': 'Computer Science',
            'category': 'databases',
            'difficulty_tier': 'intermediate',
            'estimated_time': 30,
            'order_index': 7,
            'content_easy': """Databases - Storing Information

What is a Database?
A database is like a digital filing cabinet where we store lots of information in an organized way.

Think About It:
- A library catalog (books and where they are)
- A contacts app (names and phone numbers)
- A game's high scores list

Tables:
A database uses tables, like a spreadsheet:

Students Table:
| ID | Name  | Age | Grade |
| 1  | Alice | 15  | 10    |
| 2  | Bob   | 14  | 9     |
| 3  | Carol | 15  | 10    |

Each row is one student (a record).
Each column is information about them (a field).

Basic Commands (SQL):
1. SELECT - Get information
   "Show me all students"

2. INSERT - Add new information
   "Add a new student"

3. UPDATE - Change information
   "Change Bob's grade"

4. DELETE - Remove information
   "Remove a student"

Why Databases?
- Store lots of data safely
- Find information quickly
- Multiple people can use it
- Data stays organized""",
            'content_medium': """Relational Database Concepts

Databases provide structured data storage with powerful query capabilities.

Relational Database Components:

1. Tables (Relations):
   - Rows (Records/Tuples)
   - Columns (Fields/Attributes)

2. Primary Key:
   - Unique identifier for each row
   - Cannot be NULL

3. Foreign Key:
   - References primary key in another table
   - Creates relationships between tables

SQL - Structured Query Language:

SELECT:
SELECT name, age FROM students WHERE grade = 10;
SELECT * FROM students ORDER BY name ASC;
SELECT COUNT(*) FROM students;

INSERT:
INSERT INTO students (name, age, grade)
VALUES ('David', 16, 11);

UPDATE:
UPDATE students SET grade = 11 WHERE name = 'Alice';

DELETE:
DELETE FROM students WHERE id = 3;

JOINs - Combining Tables:
SELECT students.name, courses.course_name
FROM students
JOIN enrollments ON students.id = enrollments.student_id
JOIN courses ON enrollments.course_id = courses.id;

Types of Joins:
- INNER JOIN: Only matching rows
- LEFT JOIN: All from left + matches
- RIGHT JOIN: All from right + matches
- FULL JOIN: All rows from both

Aggregate Functions:
COUNT(), SUM(), AVG(), MIN(), MAX()

GROUP BY:
SELECT grade, COUNT(*) FROM students GROUP BY grade;""",
            'content_advanced': """Advanced Database Design and Optimization

Professional database work requires understanding normalization, indexing, and transaction management.

Database Normalization:

1NF (First Normal Form):
- Atomic values (no lists in cells)
- Unique column names
- Same data type in column

2NF (Second Normal Form):
- 1NF + no partial dependencies
- All non-key attributes depend on entire key

3NF (Third Normal Form):
- 2NF + no transitive dependencies
- Non-key attributes depend only on key

BCNF (Boyce-Codd Normal Form):
- Every determinant is a candidate key

Indexing:
CREATE INDEX idx_name ON students(name);

Types:
- B-Tree: Default, good for ranges
- Hash: Exact matches only
- Composite: Multiple columns

Trade-offs:
- Speeds up SELECT
- Slows down INSERT/UPDATE/DELETE
- Uses storage space

Transactions (ACID):
- Atomicity: All or nothing
- Consistency: Valid state to valid state
- Isolation: Concurrent transactions isolated
- Durability: Committed data persists

BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

Query Optimization:
- EXPLAIN ANALYZE to see query plan
- Avoid SELECT * in production
- Use indexes appropriately
- Denormalize for read-heavy loads

NoSQL Databases:
- Document: MongoDB (JSON documents)
- Key-Value: Redis (caching)
- Column-Family: Cassandra (time-series)
- Graph: Neo4j (relationships)"""
        },
        {
            'title': 'Computer Networks',
            'description': 'Understand how computers communicate with each other',
            'subject': 'Computer Science',
            'category': 'networking',
            'difficulty_tier': 'advanced',
            'estimated_time': 35,
            'order_index': 8,
            'content_easy': """Computer Networks - Connecting Computers

What is a Network?
A network is when computers are connected so they can share information, like sending letters between friends.

Types of Networks:
1. Home Network - Your devices at home
2. School Network - All computers at school
3. The Internet - Networks around the world!

How Computers Talk:
Just like you have an address for mail, computers have addresses too!

IP Address:
Like a home address for a computer
Example: 192.168.1.1

URL (Web Address):
www.google.com is like a nickname for an IP address

Sending Messages:
When you send a message online:
1. Your computer breaks it into small pieces (packets)
2. Each piece travels through the network
3. They arrive and get put back together!

Important Parts:
- Router: Directs traffic (like a traffic cop)
- WiFi: Wireless connection
- Cable: Wired connection
- Modem: Connects to the internet

Fun Fact: The internet is made of millions of connected networks around the world!""",
            'content_medium': """Computer Networking Fundamentals

Networks enable communication between computing devices through established protocols and infrastructure.

Network Types by Size:
- PAN (Personal): Bluetooth devices
- LAN (Local): Home/office network
- MAN (Metropolitan): City-wide
- WAN (Wide): Countries/continents
- Internet: Global network of networks

OSI Model (7 Layers):
7. Application - User interfaces (HTTP, FTP)
6. Presentation - Data formatting
5. Session - Connection management
4. Transport - End-to-end delivery (TCP, UDP)
3. Network - Routing (IP)
2. Data Link - Local delivery (Ethernet)
1. Physical - Cables, signals

TCP/IP Model (4 Layers):
4. Application (HTTP, DNS, SMTP)
3. Transport (TCP, UDP)
2. Internet (IP, ICMP)
1. Network Access (Ethernet, WiFi)

IP Addressing:
IPv4: 192.168.1.1 (32-bit, ~4 billion addresses)
IPv6: 2001:0db8::1 (128-bit, virtually unlimited)

Subnet Mask: 255.255.255.0
Defines network vs host portion

Ports:
- HTTP: 80
- HTTPS: 443
- SSH: 22
- DNS: 53

DNS (Domain Name System):
Translates domain names to IP addresses
www.example.com → 93.184.216.34

HTTP/HTTPS:
- Request methods: GET, POST, PUT, DELETE
- Status codes: 200 OK, 404 Not Found, 500 Error
- HTTPS adds encryption (TLS/SSL)""",
            'content_advanced': """Advanced Networking and Network Security

Deep understanding of protocols, routing, and security is essential for modern systems.

TCP vs UDP:

TCP (Transmission Control Protocol):
- Connection-oriented
- Reliable, ordered delivery
- Flow control, congestion control
- Three-way handshake: SYN, SYN-ACK, ACK
- Use case: HTTP, FTP, Email

UDP (User Datagram Protocol):
- Connectionless
- No guaranteed delivery
- Lower latency
- Use case: Streaming, gaming, DNS

Routing:
- Static vs Dynamic routing
- Routing protocols: RIP, OSPF, BGP
- Autonomous Systems (AS)
- BGP: Internet backbone routing

Network Address Translation (NAT):
- Private to public IP mapping
- Conserves IPv4 addresses
- Types: Static, Dynamic, PAT

Firewalls:
- Packet filtering
- Stateful inspection
- Application layer filtering
- Rules: Allow/Deny based on IP, port, protocol

Network Security:

Encryption:
- Symmetric: AES (same key)
- Asymmetric: RSA (public/private keys)
- TLS: Secures HTTPS connections

VPN (Virtual Private Network):
- Encrypted tunnel over public internet
- Protocols: OpenVPN, WireGuard, IPSec

Common Attacks:
- DDoS: Overwhelming with traffic
- Man-in-the-Middle: Intercepting communication
- DNS Spoofing: Redirecting domains
- SQL Injection: Database attacks

Defense Strategies:
- Defense in depth
- Principle of least privilege
- Regular security audits
- Intrusion detection systems (IDS)"""
        },
        {
            'title': 'Object-Oriented Programming',
            'description': 'Master OOP concepts: classes, objects, inheritance, and polymorphism',
            'subject': 'Computer Science',
            'category': 'programming',
            'difficulty_tier': 'advanced',
            'estimated_time': 40,
            'order_index': 9,
            'content_easy': """Object-Oriented Programming - Building with Blocks

What is OOP?
OOP is a way to organize code using "objects" - like real things in the world!

Real World Example:
Think about a Dog:
- Properties: name, color, age
- Actions: bark, run, eat

In code, we create a "blueprint" (class) for dogs:

class Dog:
    name = "Buddy"
    color = "brown"
    
    def bark(self):
        print("Woof!")

Creating Objects:
my_dog = Dog()
my_dog.bark()  # Woof!

Objects are like copies made from the blueprint.

Why Use OOP?
1. Organize code like real things
2. Reuse code easily
3. Hide complex details
4. Work in teams better

Key Ideas:
- Class: The blueprint (recipe)
- Object: The actual thing (the cake)
- Properties: What it has (ingredients)
- Methods: What it does (baking steps)

It's like building with LEGO - you create pieces (classes) and combine them!""",
            'content_medium': """Object-Oriented Programming Concepts

OOP organizes code around objects that combine data (attributes) and behavior (methods).

Classes and Objects:

class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def introduce(self):
        return f"Hi, I'm {self.name}!"

# Creating objects (instances)
alice = Student("Alice", 20)
bob = Student("Bob", 22)

print(alice.introduce())  # Hi, I'm Alice!

Four Pillars of OOP:

1. Encapsulation:
   - Bundle data with methods
   - Hide internal details
   - Public/private access
   
   class BankAccount:
       def __init__(self):
           self.__balance = 0  # Private
       
       def deposit(self, amount):
           if amount > 0:
               self.__balance += amount

2. Inheritance:
   - Create new classes from existing ones
   - Child inherits from parent
   
   class Animal:
       def speak(self):
           pass
   
   class Dog(Animal):
       def speak(self):
           return "Woof!"

3. Polymorphism:
   - Same interface, different behaviors
   
   animals = [Dog(), Cat()]
   for animal in animals:
       print(animal.speak())  # Different sounds

4. Abstraction:
   - Hide complexity
   - Show only necessary details
   - Abstract classes/interfaces

Constructor (__init__):
- Called when object is created
- Initializes attributes

self Parameter:
- Reference to current instance
- Always first parameter in methods""",
            'content_advanced': """Advanced OOP and Design Patterns

Professional OOP requires understanding design principles and patterns for maintainable, scalable code.

SOLID Principles:

S - Single Responsibility:
   Each class has one job

O - Open/Closed:
   Open for extension, closed for modification

L - Liskov Substitution:
   Subtypes must be substitutable for base types

I - Interface Segregation:
   Many specific interfaces over one general

D - Dependency Inversion:
   Depend on abstractions, not concretions

Abstract Classes and Interfaces:

from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass
    
    @abstractmethod
    def perimeter(self):
        pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14159 * self.radius ** 2
    
    def perimeter(self):
        return 2 * 3.14159 * self.radius

Design Patterns:

Creational:
- Singleton: One instance only
- Factory: Create objects without specifying class
- Builder: Construct complex objects step by step

Structural:
- Adapter: Make incompatible interfaces work together
- Decorator: Add behavior dynamically
- Facade: Simplified interface to complex system

Behavioral:
- Observer: Notify dependents of changes
- Strategy: Interchangeable algorithms
- Command: Encapsulate requests as objects

Composition over Inheritance:
- Favor composing objects over deep hierarchies
- More flexible and maintainable

class Engine:
    def start(self): pass

class Car:
    def __init__(self):
        self.engine = Engine()  # Composition

Multiple Inheritance:
class FlyingCar(Car, Airplane):
    pass

Method Resolution Order (MRO):
- Python uses C3 linearization
- Use super() for cooperative inheritance"""
        },
        {
            'title': 'Software Development Lifecycle',
            'description': 'Learn about the complete process of building software',
            'subject': 'Computer Science',
            'category': 'software_engineering',
            'difficulty_tier': 'advanced',
            'estimated_time': 30,
            'order_index': 10,
            'content_easy': """Software Development - From Idea to App

How is Software Made?
Making software is like building a house - you need a plan!

The Steps:

1. Planning
   "What do we want to build?"
   - Talk to people who will use it
   - Write down what it should do

2. Designing
   "How will it look and work?"
   - Draw pictures of screens
   - Plan how parts connect

3. Building (Coding)
   "Let's write the code!"
   - Programmers write the code
   - Build it piece by piece

4. Testing
   "Does it work correctly?"
   - Try everything
   - Fix any problems (bugs)

5. Releasing
   "Share it with users!"
   - Put it where people can use it
   - App store, website, etc.

6. Maintenance
   "Keep it running well!"
   - Fix new bugs
   - Add new features

Working as a Team:
- Developers write code
- Designers make it look good
- Testers find problems
- Managers keep everyone organized

It's like a relay race - everyone does their part!""",
            'content_medium': """Software Development Lifecycle (SDLC)

The SDLC provides a structured approach to software development with defined phases and deliverables.

SDLC Phases:

1. Requirements Gathering:
   - Stakeholder interviews
   - User stories: "As a [user], I want [feature] so that [benefit]"
   - Functional vs non-functional requirements
   - Requirements documentation

2. System Design:
   - Architecture design
   - Database design
   - UI/UX wireframes
   - API specifications
   - Technology selection

3. Implementation:
   - Writing code
   - Code reviews
   - Version control (Git)
   - Following coding standards

4. Testing:
   - Unit testing (individual components)
   - Integration testing (components together)
   - System testing (entire system)
   - User acceptance testing (UAT)

5. Deployment:
   - Staging environment
   - Production release
   - CI/CD pipelines
   - Rollback procedures

6. Maintenance:
   - Bug fixes
   - Feature enhancements
   - Performance optimization
   - Security updates

Development Methodologies:

Waterfall:
- Sequential phases
- Complete one before next
- Good for well-defined projects

Agile:
- Iterative development
- Sprints (1-4 weeks)
- Continuous feedback
- Scrum, Kanban

DevOps:
- Development + Operations
- Continuous Integration/Delivery
- Infrastructure as Code
- Monitoring and feedback""",
            'content_advanced': """Advanced Software Engineering Practices

Modern software development requires sophisticated practices for quality, scalability, and team collaboration.

Agile Methodologies Deep Dive:

Scrum Framework:
- Roles: Product Owner, Scrum Master, Team
- Artifacts: Product Backlog, Sprint Backlog, Increment
- Ceremonies: Sprint Planning, Daily Standup, Sprint Review, Retrospective

Sprint Planning:
- Capacity planning
- Story point estimation
- Commitment to sprint goal

Kanban:
- Visualize workflow
- Limit work in progress (WIP)
- Continuous flow

Testing Strategies:

Test Pyramid:
        /\\
       /  \\  E2E
      /----\\  Integration
     /------\\  Unit (Most)

Unit Testing:
def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

Test-Driven Development (TDD):
1. Write failing test
2. Write minimal code to pass
3. Refactor

Code Coverage:
- Statement coverage
- Branch coverage
- Path coverage
- Aim for 80%+ coverage

CI/CD Pipeline:

stages:
  - build
  - test
  - security_scan
  - deploy_staging
  - deploy_production

Tools: Jenkins, GitHub Actions, GitLab CI

Infrastructure as Code:
- Terraform, Ansible
- Version-controlled infrastructure
- Reproducible environments

Monitoring and Observability:
- Logging: ELK Stack
- Metrics: Prometheus, Grafana
- Tracing: Jaeger, Zipkin
- Alerting: PagerDuty

Architecture Patterns:
- Microservices vs Monolith
- Event-driven architecture
- Serverless computing
- Container orchestration (Kubernetes)"""
        },
        {
            'title': 'Algorithms',
            'description': 'Master algorithm design and analysis for efficient problem solving',
            'subject': 'Computer Science',
            'category': 'algorithms',
            'difficulty_tier': 'intermediate',
            'estimated_time': 45,
            'order_index': 11,
            'content_easy': """What are Algorithms?

An algorithm is a step-by-step procedure to solve a problem. Think of it like a recipe that tells you exactly what to do to achieve a result.

Why Algorithms Matter:
- Solve problems efficiently
- Save computer time and memory
- Handle large amounts of data
- Make better software

Simple Example - Finding the Largest Number:
1. Start with the first number
2. Compare with each other number
3. Keep track of the biggest one
4. Return the biggest number at the end""",
            'content_medium': """Algorithm Analysis and Design

Understanding how to analyze algorithm efficiency using Big O notation and common algorithm design paradigms.

Time Complexity - Big O Notation:
- O(1): Constant time - doesn't depend on input size
- O(log n): Logarithmic - halves the problem each step
- O(n): Linear - grows proportionally with input
- O(n log n): Log-linear - efficient sorting algorithms
- O(n²): Quadratic - nested loops over input

Common Algorithms:
1. Sorting: Bubble Sort, Merge Sort, Quick Sort
2. Searching: Linear Search, Binary Search
3. Graph: BFS, DFS, Dijkstra's Algorithm""",
            'content_advanced': """Advanced Algorithm Design and Analysis

Exploring advanced algorithm paradigms including dynamic programming, greedy algorithms, graph algorithms, and NP-completeness.

Dynamic Programming:
Solves complex problems by breaking them into overlapping subproblems and storing their solutions. Examples: Fibonacci, Longest Common Subsequence, Knapsack Problem.

Greedy Algorithms:
Make locally optimal choices at each step. Examples: Huffman Coding, Kruskal's MST.

Graph Algorithms:
- Shortest Path: Dijkstra, Bellman-Ford, Floyd-Warshall
- Minimum Spanning Tree: Prim, Kruskal
- Network Flow: Ford-Fulkerson

NP-Completeness:
- P: Polynomial time solvable
- NP: Polynomial time verifiable
- NP-Complete: Hardest in NP (SAT, Clique, Vertex Cover)"""
        },
        {
            'title': 'Computer Architecture',
            'description': 'Understand how computers are built and how hardware executes programs',
            'subject': 'Computer Science',
            'category': 'architecture',
            'difficulty_tier': 'intermediate',
            'estimated_time': 40,
            'order_index': 12,
            'content_easy': """What is Computer Architecture?

Computer architecture is about understanding how computers work at the hardware level.

Main Components:
- CPU (Central Processing Unit): The brain that does calculations
- RAM (Memory): Fast, temporary storage for running programs
- Storage: Permanent storage like hard drives or SSDs
- Input/Output: Keyboard, mouse, monitor

How the CPU Works (Fetch-Decode-Execute Cycle):
1. Fetch: Get the next instruction from memory
2. Decode: Understand what the instruction means
3. Execute: Perform the instruction
4. Store: Save the result""",
            'content_medium': """CPU Architecture and Design

Exploring instruction set architectures, pipelining, and memory hierarchy.

Instruction Set Architecture (ISA):
- RISC: Simple, fixed-length instructions (ARM, RISC-V)
- CISC: Complex, variable-length instructions (x86)

Pipelining:
Allows multiple instructions to be processed simultaneously through stages: Fetch, Decode, Execute, Memory, Writeback.

Memory Hierarchy (Fast to Slow):
1. Registers: Fastest, smallest
2. L1/L2/L3 Cache: Very fast, small
3. Main Memory (RAM): Slower, larger
4. Storage (SSD/HDD): Slowest, largest""",
            'content_advanced': """Advanced Computer Architecture

Deep dive into superscalar execution, branch prediction, cache coherence, and multicore systems.

Superscalar and Out-of-Order Execution:
Modern CPUs execute multiple instructions per cycle using multiple execution units, register renaming, and reorder buffers.

Branch Prediction:
- Static: Always taken, backward taken
- Dynamic: 2-bit counters, correlating predictors, tournament predictors

Cache Coherence (MESI Protocol):
- Modified: Cache line is dirty, only copy
- Exclusive: Clean, only copy
- Shared: Clean, may exist in other caches
- Invalid: Cache line not valid

Parallelism Types:
- ILP: Instruction Level Parallelism
- TLP: Thread Level Parallelism
- DLP: Data Level Parallelism (SIMD)"""
        },
        {
            'title': 'Software Engineering',
            'description': 'Learn principles of building reliable, maintainable software systems',
            'subject': 'Computer Science',
            'category': 'software',
            'difficulty_tier': 'intermediate',
            'estimated_time': 35,
            'order_index': 13,
            'content_easy': """What is Software Engineering?

Software engineering is the practice of building software in an organized, reliable way.

Software Development Life Cycle:
1. Planning: Decide what to build
2. Analysis: Understand requirements
3. Design: Plan how to build it
4. Implementation: Write the code
5. Testing: Make sure it works
6. Deployment: Release to users
7. Maintenance: Fix bugs and add features

Good Coding Practices:
- Write clear, readable code
- Use meaningful variable names
- Add comments to explain complex logic
- Test your code before sharing""",
            'content_medium': """Software Development Methodologies

Understanding different approaches to organizing software development projects.

Agile Development:
- Sprints: Short development cycles (1-4 weeks)
- Daily Standups: Brief team sync meetings
- User Stories: Requirements from user perspective
- Continuous Integration: Frequent code merging

Design Patterns:
Reusable solutions to common problems:
- Singleton: Ensure only one instance exists
- Factory: Create objects without specifying class
- Observer: Notify multiple objects of changes
- Strategy: Define family of interchangeable algorithms

Version Control with Git:
Essential for team collaboration and tracking changes.""",
            'content_advanced': """Advanced Software Engineering

Exploring software architecture, microservices, DevOps, and quality assurance practices.

Software Architecture Patterns:
- Monolithic: Single deployable unit
- Microservices: Independent, loosely coupled services
- Event-Driven: Communication via events/messages
- Layered: Separation of concerns in layers

SOLID Principles:
- Single Responsibility
- Open/Closed
- Liskov Substitution
- Interface Segregation
- Dependency Inversion

CI/CD Pipeline:
Code Commit → Build → Test → Security Scan → Deploy

Testing Pyramid:
- Unit Tests (70%)
- Integration Tests (20%)
- E2E Tests (10%)"""
        },
        {
            'title': 'Compiler Design',
            'description': 'Understand how programming languages are translated into machine code',
            'subject': 'Computer Science',
            'category': 'compilers',
            'difficulty_tier': 'advanced',
            'estimated_time': 50,
            'order_index': 14,
            'content_easy': """What is a Compiler?

A compiler is a program that translates code written in one programming language into another language, usually machine code.

Compiler vs Interpreter:
- Compiler: Translates entire program at once, creates executable
- Interpreter: Translates and runs code line by line

Stages of Compilation:
1. Reading: The compiler reads your source code
2. Checking: It checks for errors in your code
3. Translating: It converts to machine language
4. Creating: It produces an executable program""",
            'content_medium': """Compiler Architecture

Understanding the phases of a compiler and how source code is transformed into executable code.

Compiler Phases:
1. Lexical Analysis (Scanner): Source code → Tokens
2. Syntax Analysis (Parser): Tokens → Parse Tree/AST
3. Semantic Analysis: Type checking, scope resolution
4. IR Generation: Abstract Syntax Tree → Intermediate Code
5. Optimization: Improve code efficiency
6. Code Generation: Generate machine code

Lexical Analysis:
Converts source code into tokens (keywords, identifiers, operators, literals).

Syntax Analysis:
Uses grammar rules to build Abstract Syntax Tree (AST).""",
            'content_advanced': """Advanced Compiler Design

Deep dive into optimization techniques, code generation, and advanced parsing.

Parser Types:
- Top-Down (LL): Recursive descent, LL(k) parsers
- Bottom-Up (LR): SLR, LALR, CLR parsers

Intermediate Representations:
- Three-Address Code (TAC)
- Static Single Assignment (SSA)

Optimization Techniques:
1. Constant Folding: x = 3 + 5 → x = 8
2. Dead Code Elimination
3. Loop Invariant Code Motion
4. Common Subexpression Elimination

Register Allocation:
Graph coloring algorithm for assigning variables to registers.

Code Generation:
Translating IR to target machine assembly/binary."""
        },
        {
            'title': 'Theory of Computation',
            'description': 'Explore the mathematical foundations of what computers can and cannot compute',
            'subject': 'Computer Science',
            'category': 'theory',
            'difficulty_tier': 'advanced',
            'estimated_time': 55,
            'order_index': 15,
            'content_easy': """What is Theory of Computation?

Theory of Computation studies what problems computers can solve and how efficiently.

Three Main Questions:
1. What is computation? (Formal models)
2. What can be computed? (Decidability)
3. How efficiently? (Complexity)

Simple Machines:
- Finite Automata: Like a vending machine with states
- Pushdown Automata: Can remember things in a stack
- Turing Machine: Can solve any computable problem""",
            'content_medium': """Automata Theory

Understanding formal languages and the machines that recognize them.

Chomsky Hierarchy:
- Type 3: Regular (Finite Automaton)
- Type 2: Context-Free (Pushdown Automaton)
- Type 1: Context-Sensitive (Linear Bounded Automaton)
- Type 0: Recursively Enumerable (Turing Machine)

Finite Automata:
- DFA: Deterministic Finite Automaton
- NFA: Nondeterministic Finite Automaton
- Equivalent in power

Regular Expressions:
Equivalent to finite automata for pattern matching.

Context-Free Grammars:
Used for programming language syntax (parsing).""",
            'content_advanced': """Advanced Computability and Complexity

Exploring undecidability, complexity classes, and the limits of computation.

The Halting Problem:
Proven undecidable by Alan Turing. No algorithm can determine whether an arbitrary program will halt.

Complexity Classes:
- P: Polynomial time solvable
- NP: Nondeterministic polynomial time verifiable
- NP-Complete: Hardest problems in NP
- NP-Hard: At least as hard as NP-Complete

Famous NP-Complete Problems:
SAT, Clique, Vertex Cover, Hamiltonian Path, TSP

P vs NP Question:
One of the millennium prize problems. Does P = NP?

Space Complexity:
L ⊆ NL ⊆ P ⊆ NP ⊆ PSPACE ⊆ EXPTIME"""
        },
        {
            'title': 'Machine Learning',
            'description': 'Learn how computers can learn from data to make predictions',
            'subject': 'Computer Science',
            'category': 'ai',
            'difficulty_tier': 'intermediate',
            'estimated_time': 45,
            'order_index': 16,
            'content_easy': """What is Machine Learning?

Machine Learning is a way for computers to learn from examples instead of being explicitly programmed.

Types of Machine Learning:
- Supervised Learning: Learning from labeled examples
- Unsupervised Learning: Finding patterns without labels
- Reinforcement Learning: Learning by trial and error

Real-World Examples:
- Email spam filters
- Movie recommendations
- Voice assistants
- Self-driving cars""",
            'content_medium': """Core ML Algorithms

Understanding fundamental machine learning algorithms.

Supervised Learning:
- Linear Regression: Predict continuous values
- Logistic Regression: Binary classification
- Decision Trees: Tree-based decisions
- Random Forest: Ensemble of trees
- Support Vector Machines: Find optimal boundary

Unsupervised Learning:
- K-Means Clustering: Group similar data
- PCA: Dimensionality reduction

Key Concepts:
- Overfitting: Model memorizes training data
- Underfitting: Model too simple
- Cross-Validation: Test on multiple splits
- Feature Engineering: Create useful input features""",
            'content_advanced': """Advanced Machine Learning

Deep learning, neural networks, and advanced optimization techniques.

Neural Networks:
- Perceptron: Single neuron
- Multi-Layer Perceptron: Hidden layers
- Activation Functions: ReLU, Sigmoid, Tanh

Deep Learning Architectures:
- CNN: Convolutional networks for images
- RNN/LSTM: Sequential data, time series
- Transformer: Attention mechanism, NLP
- GAN: Generative adversarial networks

Optimization:
- SGD, Momentum, Adam
- Learning Rate Scheduling
- Batch Normalization

Regularization:
- L1/L2 Regularization
- Dropout
- Early Stopping"""
        }
    ]
    
    Lesson.query.delete()
    
    for lesson_data in lessons_data:
        lesson = Lesson(**lesson_data)
        db.session.add(lesson)
    
    db.session.commit()
    print("UG Computer Science lessons seeded successfully!")


def seed_quizzes():
    """Create quizzes for CS lessons"""
    Quiz.query.delete()
    QuizQuestion.query.delete()
    
    lessons = Lesson.query.all()
    
    quiz_questions = {
        'Introduction to Programming': {
            'easy': [
                {
                    'question_text': 'What is a program?',
                    'option_a': 'A type of computer',
                    'option_b': 'A list of instructions for the computer',
                    'option_c': 'A computer game',
                    'option_d': 'The internet',
                    'correct_answer': 'B',
                    'explanation': 'A program is a set of instructions that tells the computer what to do.'
                },
                {
                    'question_text': 'What is code?',
                    'option_a': 'A secret message',
                    'option_b': 'A computer virus',
                    'option_c': 'Instructions we write for computers',
                    'option_d': 'A type of password',
                    'correct_answer': 'C',
                    'explanation': 'Code is the instructions programmers write for computers to follow.'
                }
            ],
            'medium': [
                {
                    'question_text': 'Which of these is a programming language?',
                    'option_a': 'English',
                    'option_b': 'Python',
                    'option_c': 'Windows',
                    'option_d': 'Google',
                    'correct_answer': 'B',
                    'explanation': 'Python is a popular programming language. The others are not programming languages.'
                },
                {
                    'question_text': 'What does print("Hello") do in Python?',
                    'option_a': 'Prints a document',
                    'option_b': 'Displays "Hello" on screen',
                    'option_c': 'Sends an email',
                    'option_d': 'Saves a file',
                    'correct_answer': 'B',
                    'explanation': 'The print() function displays text on the screen.'
                }
            ],
            'advanced': [
                {
                    'question_text': 'Which programming paradigm uses classes and objects?',
                    'option_a': 'Procedural',
                    'option_b': 'Functional',
                    'option_c': 'Object-Oriented',
                    'option_d': 'Declarative',
                    'correct_answer': 'C',
                    'explanation': 'Object-Oriented Programming (OOP) organizes code using classes and objects.'
                },
                {
                    'question_text': 'What does DRY stand for in programming?',
                    'option_a': 'Do Run Yourself',
                    'option_b': 'Don\'t Repeat Yourself',
                    'option_c': 'Data Runs Yearly',
                    'option_d': 'Debug Run Yesterday',
                    'correct_answer': 'B',
                    'explanation': 'DRY means Don\'t Repeat Yourself - avoid duplicating code.'
                }
            ]
        },
        'Variables and Data Types': {
            'easy': [
                {
                    'question_text': 'What is a variable?',
                    'option_a': 'A math problem',
                    'option_b': 'A labeled box that stores information',
                    'option_c': 'A computer part',
                    'option_d': 'A type of keyboard',
                    'correct_answer': 'B',
                    'explanation': 'A variable is like a labeled box where we store information.'
                },
                {
                    'question_text': 'What type of data is "Hello World"?',
                    'option_a': 'Number',
                    'option_b': 'Text (String)',
                    'option_c': 'True/False',
                    'option_d': 'Decimal',
                    'correct_answer': 'B',
                    'explanation': 'Text data enclosed in quotes is called a String.'
                }
            ],
            'medium': [
                {
                    'question_text': 'What is the result of int("42")?',
                    'option_a': '"42"',
                    'option_b': '42',
                    'option_c': '4.2',
                    'option_d': 'Error',
                    'correct_answer': 'B',
                    'explanation': 'int() converts the string "42" to the integer 42.'
                },
                {
                    'question_text': 'Which variable name is valid?',
                    'option_a': '2name',
                    'option_b': 'my-name',
                    'option_c': 'my_name',
                    'option_d': 'my name',
                    'correct_answer': 'C',
                    'explanation': 'Variable names can use underscores but cannot start with numbers or contain spaces/hyphens.'
                }
            ],
            'advanced': [
                {
                    'question_text': 'In statically typed languages, when are types checked?',
                    'option_a': 'At runtime',
                    'option_b': 'At compile time',
                    'option_c': 'Never',
                    'option_d': 'When the user clicks',
                    'correct_answer': 'B',
                    'explanation': 'Static typing checks types at compile time before the program runs.'
                },
                {
                    'question_text': 'Why are strings immutable in Python?',
                    'option_a': 'To save memory',
                    'option_b': 'For thread safety and predictability',
                    'option_c': 'Python limitation',
                    'option_d': 'They are not immutable',
                    'correct_answer': 'B',
                    'explanation': 'Immutable strings provide thread safety and predictable behavior.'
                }
            ]
        },
        'Control Structures': {
            'easy': [
                {
                    'question_text': 'What symbol do we use to check if two things are equal?',
                    'option_a': '=',
                    'option_b': '==',
                    'option_c': '!=',
                    'option_d': '<>',
                    'correct_answer': 'B',
                    'explanation': 'We use == to compare if two values are equal.'
                },
                {
                    'question_text': 'What does a loop do?',
                    'option_a': 'Stops the program',
                    'option_b': 'Repeats code multiple times',
                    'option_c': 'Saves files',
                    'option_d': 'Connects to internet',
                    'correct_answer': 'B',
                    'explanation': 'Loops repeat a block of code multiple times.'
                }
            ],
            'medium': [
                {
                    'question_text': 'What does "break" do in a loop?',
                    'option_a': 'Pauses the loop',
                    'option_b': 'Exits the loop immediately',
                    'option_c': 'Skips to next iteration',
                    'option_d': 'Crashes the program',
                    'correct_answer': 'B',
                    'explanation': 'break exits the loop immediately, stopping all iterations.'
                },
                {
                    'question_text': 'How many times does "for i in range(5)" loop?',
                    'option_a': '4 times',
                    'option_b': '5 times',
                    'option_c': '6 times',
                    'option_d': '1 time',
                    'correct_answer': 'B',
                    'explanation': 'range(5) generates 0,1,2,3,4 - five iterations.'
                }
            ],
            'advanced': [
                {
                    'question_text': 'What is short-circuit evaluation?',
                    'option_a': 'A programming error',
                    'option_b': 'Stopping evaluation when result is determined',
                    'option_c': 'A type of loop',
                    'option_d': 'Exception handling',
                    'correct_answer': 'B',
                    'explanation': 'Short-circuit evaluation stops when the result can be determined early.'
                }
            ]
        },
        'Introduction to Data Structures': {
            'easy': [
                {
                    'question_text': 'What is a list in programming?',
                    'option_a': 'A single value',
                    'option_b': 'An ordered collection of items',
                    'option_c': 'A type of loop',
                    'option_d': 'A function',
                    'correct_answer': 'B',
                    'explanation': 'A list is an ordered collection that can hold multiple items.'
                }
            ],
            'medium': [
                {
                    'question_text': 'What is the time complexity of accessing an array element by index?',
                    'option_a': 'O(n)',
                    'option_b': 'O(1)',
                    'option_c': 'O(log n)',
                    'option_d': 'O(n²)',
                    'correct_answer': 'B',
                    'explanation': 'Array access by index is O(1) - constant time, regardless of size.'
                }
            ],
            'advanced': [
                {
                    'question_text': 'Which data structure uses LIFO (Last In, First Out)?',
                    'option_a': 'Queue',
                    'option_b': 'Stack',
                    'option_c': 'Array',
                    'option_d': 'Linked List',
                    'correct_answer': 'B',
                    'explanation': 'Stacks follow LIFO - the last element added is the first removed.'
                }
            ]
        },
        'Algorithms and Problem Solving': {
            'easy': [
                {
                    'question_text': 'What is an algorithm?',
                    'option_a': 'A computer brand',
                    'option_b': 'Step-by-step instructions to solve a problem',
                    'option_c': 'A programming language',
                    'option_d': 'A type of computer',
                    'correct_answer': 'B',
                    'explanation': 'An algorithm is a precise set of steps to solve a problem.'
                }
            ],
            'medium': [
                {
                    'question_text': 'What is the time complexity of binary search?',
                    'option_a': 'O(n)',
                    'option_b': 'O(n²)',
                    'option_c': 'O(log n)',
                    'option_d': 'O(1)',
                    'correct_answer': 'C',
                    'explanation': 'Binary search halves the search space each step, giving O(log n).'
                }
            ],
            'advanced': [
                {
                    'question_text': 'Which algorithm design paradigm solves problems by breaking them into overlapping subproblems?',
                    'option_a': 'Divide and Conquer',
                    'option_b': 'Dynamic Programming',
                    'option_c': 'Greedy',
                    'option_d': 'Backtracking',
                    'correct_answer': 'B',
                    'explanation': 'Dynamic Programming handles overlapping subproblems with memoization.'
                }
            ]
        },
        'Database Fundamentals': {
            'easy': [
                {
                    'question_text': 'What is a database?',
                    'option_a': 'A word processor',
                    'option_b': 'An organized collection of data',
                    'option_c': 'A web browser',
                    'option_d': 'A type of cable',
                    'correct_answer': 'B',
                    'explanation': 'A database is an organized collection of data stored electronically.'
                }
            ],
            'medium': [
                {
                    'question_text': 'Which SQL command retrieves data from a table?',
                    'option_a': 'INSERT',
                    'option_b': 'UPDATE',
                    'option_c': 'SELECT',
                    'option_d': 'DELETE',
                    'correct_answer': 'C',
                    'explanation': 'SELECT is used to query and retrieve data from database tables.'
                }
            ],
            'advanced': [
                {
                    'question_text': 'What does ACID stand for in database transactions?',
                    'option_a': 'Add, Create, Insert, Delete',
                    'option_b': 'Atomicity, Consistency, Isolation, Durability',
                    'option_c': 'Automatic, Complete, Immediate, Direct',
                    'option_d': 'Access, Control, Index, Data',
                    'correct_answer': 'B',
                    'explanation': 'ACID ensures reliable transaction processing in databases.'
                }
            ]
        },
        'Computer Networks': {
            'easy': [
                {
                    'question_text': 'What is an IP address?',
                    'option_a': 'A password',
                    'option_b': 'A unique address for a computer on a network',
                    'option_c': 'A website name',
                    'option_d': 'An email address',
                    'correct_answer': 'B',
                    'explanation': 'An IP address uniquely identifies a device on a network.'
                }
            ],
            'medium': [
                {
                    'question_text': 'What does HTTP stand for?',
                    'option_a': 'High Transfer Text Protocol',
                    'option_b': 'HyperText Transfer Protocol',
                    'option_c': 'Home Text Transfer Program',
                    'option_d': 'Hyper Technical Transfer Protocol',
                    'correct_answer': 'B',
                    'explanation': 'HTTP is HyperText Transfer Protocol, used for web communication.'
                }
            ],
            'advanced': [
                {
                    'question_text': 'Which protocol provides reliable, ordered delivery of data?',
                    'option_a': 'UDP',
                    'option_b': 'TCP',
                    'option_c': 'ICMP',
                    'option_d': 'ARP',
                    'correct_answer': 'B',
                    'explanation': 'TCP provides reliable, ordered delivery through acknowledgments and retransmission.'
                }
            ]
        },
        'Object-Oriented Programming': {
            'easy': [
                {
                    'question_text': 'What is a class in programming?',
                    'option_a': 'A type of variable',
                    'option_b': 'A blueprint for creating objects',
                    'option_c': 'A loop',
                    'option_d': 'A database',
                    'correct_answer': 'B',
                    'explanation': 'A class is a blueprint that defines properties and methods for objects.'
                }
            ],
            'medium': [
                {
                    'question_text': 'What is inheritance in OOP?',
                    'option_a': 'Copying code',
                    'option_b': 'A child class receiving properties from parent class',
                    'option_c': 'Hiding data',
                    'option_d': 'Creating multiple objects',
                    'correct_answer': 'B',
                    'explanation': 'Inheritance allows a child class to inherit attributes and methods from a parent.'
                }
            ],
            'advanced': [
                {
                    'question_text': 'What does the "S" in SOLID stand for?',
                    'option_a': 'Simple Responsibility',
                    'option_b': 'Single Responsibility',
                    'option_c': 'Standard Responsibility',
                    'option_d': 'Shared Responsibility',
                    'correct_answer': 'B',
                    'explanation': 'Single Responsibility Principle: each class should have one reason to change.'
                }
            ]
        },
        'Software Development Lifecycle': {
            'easy': [
                {
                    'question_text': 'What is the first step in building software?',
                    'option_a': 'Writing code',
                    'option_b': 'Planning and requirements',
                    'option_c': 'Testing',
                    'option_d': 'Releasing',
                    'correct_answer': 'B',
                    'explanation': 'Planning and gathering requirements comes before any coding begins.'
                }
            ],
            'medium': [
                {
                    'question_text': 'What is Agile development?',
                    'option_a': 'Very fast coding',
                    'option_b': 'Iterative development with continuous feedback',
                    'option_c': 'Writing code without testing',
                    'option_d': 'Solo development',
                    'correct_answer': 'B',
                    'explanation': 'Agile focuses on iterative development, sprints, and continuous feedback.'
                }
            ],
            'advanced': [
                {
                    'question_text': 'What is CI/CD?',
                    'option_a': 'Code Integration / Code Deployment',
                    'option_b': 'Continuous Integration / Continuous Delivery',
                    'option_c': 'Computer Interface / Computer Design',
                    'option_d': 'Controlled Input / Controlled Data',
                    'correct_answer': 'B',
                    'explanation': 'CI/CD automates testing and deployment of code changes.'
                }
            ]
        }
    }
    
    for lesson in lessons:
        if lesson.title in quiz_questions:
            for difficulty, questions in quiz_questions[lesson.title].items():
                quiz = Quiz(lesson_id=lesson.id, difficulty=difficulty)
                db.session.add(quiz)
                db.session.flush()
                
                for idx, q_data in enumerate(questions):
                    question = QuizQuestion(
                        quiz_id=quiz.id,
                        order_index=idx,
                        **q_data
                    )
                    db.session.add(question)
    
    db.session.commit()
    print("Quizzes seeded successfully!")


def seed_games():
    """Create accessible learning games"""
    Game.query.delete()
    
    games_data = [
        {
            'name': 'Code Matching',
            'game_type': 'matching',
            'description': 'Match programming terms with their definitions',
            'instructions': 'Find pairs of matching cards. Click on two cards to flip them. Match all pairs to win!',
            'min_difficulty': 1,
            'max_difficulty': 5,
            'base_coins': 10,
            'base_stars': 1,
            'icon': 'layers',
            'color_theme': 'primary'
        },
        {
            'name': 'Sort the Code',
            'game_type': 'sequence',
            'description': 'Put code statements in the correct order',
            'instructions': 'Drag and arrange the code blocks to create a working program.',
            'min_difficulty': 1,
            'max_difficulty': 5,
            'base_coins': 15,
            'base_stars': 1,
            'icon': 'list-ordered',
            'color_theme': 'success'
        },
        {
            'name': 'Memory Cards',
            'game_type': 'memory',
            'description': 'Test your memory with programming concepts',
            'instructions': 'Find matching pairs by remembering card positions. Take your time!',
            'min_difficulty': 1,
            'max_difficulty': 5,
            'base_coins': 10,
            'base_stars': 1,
            'icon': 'brain',
            'color_theme': 'warning'
        },
        {
            'name': 'Drag & Drop Coding',
            'game_type': 'dragdrop',
            'description': 'Build code by dragging blocks to the right places',
            'instructions': 'Drag code pieces to the empty spots to complete the program.',
            'min_difficulty': 1,
            'max_difficulty': 5,
            'base_coins': 15,
            'base_stars': 1,
            'icon': 'move',
            'color_theme': 'info'
        }
    ]
    
    for game_data in games_data:
        game = Game(**game_data)
        db.session.add(game)
    
    db.session.commit()
    print("Games seeded successfully!")


def seed_demo_accounts():
    """Create demo accounts for students, teachers, and parents"""
    ParentStudentLink.query.delete()
    Student.query.delete()
    Teacher.query.delete()
    ParentAccount.query.delete()
    
    student = Student(
        student_id='DEMO001',
        name='Demo Student',
        email='demo@agentic.learn',
        current_difficulty='easy',
        audio_enabled=False,
        sign_language_enabled=False,
        emotion_detection_enabled=False,
        font_size=18
    )
    db.session.add(student)
    db.session.flush()
    
    teacher = Teacher(
        teacher_id='TEACH001',
        name='Demo Teacher',
        email='teacher@agentic.learn',
        subject='Computer Science'
    )
    db.session.add(teacher)
    
    parent = ParentAccount(
        parent_id='PARENT001',
        name='Demo Parent',
        email='parent@agentic.learn'
    )
    parent.generate_access_token()
    db.session.add(parent)
    db.session.flush()
    
    parent_student_link = ParentStudentLink(
        parent_id=parent.id,
        student_id=student.id,
        relationship='parent',
        can_view_reports=True,
        notifications_enabled=True
    )
    db.session.add(parent_student_link)
    
    db.session.commit()
    print("Demo accounts created!")
    print("  Student: DEMO001")
    print("  Teacher: TEACH001")
    print("  Parent: PARENT001 (linked to Demo Student)")


def run_seed():
    """Run all seed functions"""
    with app.app_context():
        seed_lessons()
        seed_quizzes()
        seed_games()
        seed_demo_accounts()
        print("\nDatabase seeded successfully!")
        print("You can log in with the Demo Student (DEMO001) or create a new profile.")


if __name__ == '__main__':
    run_seed()
