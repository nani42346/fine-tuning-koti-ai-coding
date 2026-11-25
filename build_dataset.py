"""
Builds train_dataset.jsonl for Koti AI Coding.

Each topic has several phrasings of the same question and ONE concise answer.
Answers are short on purpose: the model learns to answer the question, use
Markdown code blocks, and stop - instead of rambling.

Run:  python build_dataset.py
"""
import json
import random

DATA = [
    # ------------------------------------------------------------ small talk / identity
    (["hi", "hello", "hey", "hii", "hello there"],
     "Hello! I'm Koti AI Coding, your coding mentor. What can I help you with today?"),
    (["hi how are you", "how are you", "how are you doing today", "hey, how's it going?"],
     "I'm doing great, thanks for asking! How can I help you with your code today?"),
    (["good morning", "good evening"],
     "Good day to you too! What would you like to code or learn today?"),
    (["thank you", "thanks a lot", "thanks, that helped"],
     "You're welcome! Let me know if you have any other questions."),
    (["bye", "goodbye", "see you later"],
     "Goodbye! Happy coding!"),
    (["who are you", "what is your name", "introduce yourself"],
     "I'm **Koti AI Coding**, a coding mentor built on TinyLlama 1.1B and fine-tuned with LoRA. "
     "I can write code, explain programming concepts and help you debug."),
    (["what can you do", "how can you help me", "what are your features"],
     "I can help you:\n\n- **Write code** in Python, JavaScript, SQL and more\n"
     "- **Explain concepts** like recursion, OOP and data structures\n"
     "- **Debug errors** and suggest fixes\n\nJust ask a question to get started."),
    (["ok", "okay", "cool", "nice"],
     "Great! What would you like to do next?"),

    # ------------------------------------------------------------ python basics
    (["Write a Python program for factorial", "Factorial using recursion in Python", "Create a factorial function in Python"],
     "```python\ndef factorial(n):\n    if n < 0:\n        raise ValueError(\"n must be non-negative\")\n"
     "    if n in (0, 1):\n        return 1\n    return n * factorial(n - 1)\n\nprint(factorial(5))  # 120\n```\n\n"
     "The function calls itself with `n - 1` until it reaches the base case `0` or `1`, then multiplies the results on the way back."),
    (["Find factorial using a loop in Python", "Iterative factorial in Python"],
     "```python\ndef factorial(n):\n    result = 1\n    for i in range(2, n + 1):\n        result *= i\n    return result\n\n"
     "print(factorial(5))  # 120\n```\n\nThe loop multiplies every number from 2 to `n`. It avoids recursion limits for large `n`."),
    (["Write a Python palindrome program", "Check if a string is a palindrome in Python", "Python palindrome example"],
     "```python\ndef is_palindrome(text):\n    cleaned = \"\".join(ch.lower() for ch in text if ch.isalnum())\n"
     "    return cleaned == cleaned[::-1]\n\nprint(is_palindrome(\"madam\"))                   # True\n"
     "print(is_palindrome(\"A man, a plan, a canal: Panama\"))  # True\n```\n\n"
     "It keeps only letters and digits, lowercases them, and compares the string with its reverse (`[::-1]`)."),
    (["Write a Python program for Fibonacci series", "Print Fibonacci numbers in Python", "Fibonacci sequence in Python"],
     "```python\ndef fibonacci(n):\n    a, b = 0, 1\n    result = []\n    for _ in range(n):\n        result.append(a)\n        a, b = b, a + b\n"
     "    return result\n\nprint(fibonacci(10))  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]\n```\n\n"
     "Each number is the sum of the previous two. `a, b = b, a + b` updates both values in one step."),
    (["Check if a number is prime in Python", "Python program to check prime number", "Write a prime number checker in Python"],
     "```python\ndef is_prime(n):\n    if n < 2:\n        return False\n    i = 2\n    while i * i <= n:\n        if n % i == 0:\n            return False\n        i += 1\n"
     "    return True\n\nprint(is_prime(17))  # True\nprint(is_prime(18))  # False\n```\n\n"
     "We only test divisors up to the square root of `n`, because a larger factor would pair with a smaller one we already checked."),
    (["Reverse a string in Python", "How do I reverse a string in Python?"],
     "```python\ntext = \"hello\"\nreversed_text = text[::-1]\nprint(reversed_text)  # olleh\n```\n\n"
     "The slice `[::-1]` walks the string from the end to the start with step `-1`."),
    (["Reverse a list in Python", "How to reverse a list in Python"],
     "```python\nnums = [1, 2, 3, 4]\n\nnums.reverse()          # in place\nprint(nums)             # [4, 3, 2, 1]\n\n"
     "backwards = nums[::-1]  # new list\nprint(backwards)        # [1, 2, 3, 4]\n```\n\n"
     "`list.reverse()` changes the list itself, while slicing with `[::-1]` returns a new reversed copy."),
    (["Find the largest number in a list in Python", "Python program to find maximum in a list"],
     "```python\nnums = [4, 17, 9, 2]\nprint(max(nums))  # 17\n\n# Without max():\nlargest = nums[0]\nfor n in nums:\n    if n > largest:\n        largest = n\nprint(largest)  # 17\n```\n\n"
     "`max()` is the simplest way. The loop shows the logic: keep the biggest value seen so far."),
    (["Sum of a list in Python", "Add all numbers in a list in Python"],
     "```python\nnums = [1, 2, 3, 4]\nprint(sum(nums))  # 10\n```\n\nThe built-in `sum()` adds every item in the list."),
    (["Count vowels in a string in Python", "Python program to count vowels"],
     "```python\ndef count_vowels(text):\n    return sum(1 for ch in text.lower() if ch in \"aeiou\")\n\nprint(count_vowels(\"Hello World\"))  # 3\n```\n\n"
     "The generator yields `1` for each vowel and `sum()` adds them up."),
    (["Check even or odd in Python", "Python program for even or odd number"],
     "```python\nn = 7\nif n % 2 == 0:\n    print(\"Even\")\nelse:\n    print(\"Odd\")\n```\n\n"
     "`%` gives the remainder. A number is even when the remainder after dividing by 2 is `0`."),
    (["Swap two variables in Python", "How to swap two numbers in Python"],
     "```python\na, b = 5, 10\na, b = b, a\nprint(a, b)  # 10 5\n```\n\nPython packs the right side into a tuple and unpacks it, so no temporary variable is needed."),
    (["Remove duplicates from a list in Python", "How to get unique items from a list in Python"],
     "```python\nitems = [3, 1, 3, 2, 1]\n\nunique = list(dict.fromkeys(items))  # keeps order\nprint(unique)  # [3, 1, 2]\n\n"
     "print(set(items))  # {1, 2, 3}  (order not guaranteed)\n```\n\n"
     "`dict.fromkeys` keeps the first occurrence of each item in order; a `set` is faster but unordered."),
    (["Sort a list in Python", "How to sort a list in descending order in Python"],
     "```python\nnums = [5, 2, 9, 1]\n\nprint(sorted(nums))                # [1, 2, 5, 9] new list\nprint(sorted(nums, reverse=True))  # [9, 5, 2, 1]\n\n"
     "nums.sort()  # sorts in place\n```\n\n`sorted()` returns a new list; `list.sort()` changes the original. Use `reverse=True` for descending order."),
    (["Sort a list of dictionaries by a key in Python", "Python sort by key"],
     "```python\npeople = [{\"name\": \"Ana\", \"age\": 30}, {\"name\": \"Ben\", \"age\": 25}]\n"
     "people.sort(key=lambda p: p[\"age\"])\nprint(people)  # Ben (25) first, then Ana (30)\n```\n\n"
     "The `key` function tells `sort` which value to compare."),
    (["What is a list comprehension in Python?", "Explain list comprehension with an example"],
     "A list comprehension builds a list in one line:\n\n```python\nsquares = [x * x for x in range(5)]\nprint(squares)  # [0, 1, 4, 9, 16]\n\n"
     "evens = [x for x in range(10) if x % 2 == 0]\nprint(evens)    # [0, 2, 4, 6, 8]\n```\n\n"
     "The pattern is `[expression for item in iterable if condition]`."),
    (["Read a file in Python", "How to read a text file line by line in Python"],
     "```python\nwith open(\"data.txt\", \"r\", encoding=\"utf-8\") as f:\n    for line in f:\n        print(line.strip())\n```\n\n"
     "`with` closes the file automatically, and iterating over `f` reads one line at a time."),
    (["Write to a file in Python", "How to save text to a file in Python"],
     "```python\nwith open(\"output.txt\", \"w\", encoding=\"utf-8\") as f:\n    f.write(\"Hello, file!\\n\")\n```\n\n"
     "Mode `\"w\"` creates or overwrites the file; use `\"a\"` to append instead."),
    (["How to handle exceptions in Python", "Explain try except in Python"],
     "```python\ntry:\n    value = int(input(\"Number: \"))\n    print(10 / value)\nexcept ValueError:\n    print(\"That is not a number.\")\n"
     "except ZeroDivisionError:\n    print(\"Cannot divide by zero.\")\nfinally:\n    print(\"Done.\")\n```\n\n"
     "Code that may fail goes in `try`. Each `except` handles one error type, and `finally` always runs."),
    (["Write a Python class example", "Explain classes and objects in Python"],
     "```python\nclass Dog:\n    def __init__(self, name):\n        self.name = name\n\n    def bark(self):\n        return f\"{self.name} says woof!\"\n\n"
     "rex = Dog(\"Rex\")\nprint(rex.bark())  # Rex says woof!\n```\n\n"
     "A **class** is a blueprint; an **object** (`rex`) is an instance of it. `__init__` sets up each new object, and `self` refers to that object."),
    (["Explain inheritance in Python", "Python inheritance example"],
     "```python\nclass Animal:\n    def speak(self):\n        return \"...\"\n\nclass Cat(Animal):\n    def speak(self):\n        return \"Meow\"\n\n"
     "print(Cat().speak())  # Meow\n```\n\n`Cat` inherits from `Animal` and **overrides** `speak`. Inheritance lets classes reuse and extend behaviour."),
    (["What is a dictionary in Python?", "Python dictionary example"],
     "A dictionary stores **key-value pairs**:\n\n```python\nstudent = {\"name\": \"Asha\", \"age\": 21}\nprint(student[\"name\"])        # Asha\n"
     "student[\"grade\"] = \"A\"          # add a key\nprint(student.get(\"city\", \"-\"))  # - (default if missing)\n\nfor key, value in student.items():\n    print(key, value)\n```"),
    (["Difference between list and tuple in Python", "List vs tuple in Python"],
     "- A **list** `[1, 2, 3]` is **mutable**: you can add, remove or change items.\n"
     "- A **tuple** `(1, 2, 3)` is **immutable**: it cannot change after creation.\n\n"
     "Use tuples for fixed data (like coordinates) and lists for collections that change. Tuples can also be dictionary keys."),
    (["What is a lambda function in Python?", "Explain lambda in Python"],
     "A lambda is a small anonymous function written in one line:\n\n```python\nsquare = lambda x: x * x\nprint(square(4))  # 16\n\n"
     "nums = [3, 1, 2]\nprint(sorted(nums, key=lambda n: -n))  # [3, 2, 1]\n```\n\nThey are handy as short `key` or callback functions."),
    (["What are *args and **kwargs in Python?", "Explain args and kwargs"],
     "```python\ndef show(*args, **kwargs):\n    print(args)    # tuple of positional arguments\n    print(kwargs)  # dict of keyword arguments\n\n"
     "show(1, 2, name=\"Koti\")\n# (1, 2)\n# {'name': 'Koti'}\n```\n\n`*args` collects extra positional arguments and `**kwargs` collects extra keyword arguments."),
    (["What is a decorator in Python?", "Explain Python decorators with example"],
     "A decorator wraps a function to add behaviour without changing its code:\n\n```python\ndef log_call(func):\n    def wrapper(*args, **kwargs):\n"
     "        print(f\"Calling {func.__name__}\")\n        return func(*args, **kwargs)\n    return wrapper\n\n@log_call\ndef greet(name):\n    return f\"Hi {name}\"\n\n"
     "print(greet(\"Ana\"))  # Calling greet, then Hi Ana\n```"),
    (["What is a generator in Python?", "Explain yield in Python"],
     "A generator produces values one at a time with `yield`, saving memory:\n\n```python\ndef count_up(n):\n    for i in range(n):\n        yield i\n\n"
     "for value in count_up(3):\n    print(value)  # 0 1 2\n```\n\nThe function pauses at each `yield` and resumes when the next value is requested."),
    (["Convert a string to an integer in Python", "How to convert string to int in Python"],
     "```python\nnum = int(\"42\")\nprint(num + 1)  # 43\n\nprice = float(\"3.5\")\nprint(price)    # 3.5\n```\n\n"
     "`int()` raises `ValueError` if the text is not a valid number, so wrap it in `try/except` for user input."),
    (["Check if a key exists in a dictionary in Python", "Python check key in dict"],
     "```python\ndata = {\"a\": 1}\nprint(\"a\" in data)        # True\nprint(data.get(\"b\", 0))   # 0 (default)\n```\n\nUse `in` to test for a key and `.get()` to read with a default."),
    (["Merge two dictionaries in Python", "Combine dictionaries in Python"],
     "```python\na = {\"x\": 1}\nb = {\"y\": 2}\nmerged = a | b       # Python 3.9+\nprint(merged)        # {'x': 1, 'y': 2}\n\nmerged = {**a, **b}  # older versions\n```\n\nIf a key appears in both, the value from the right-hand dictionary wins."),
    (["Count word frequency in Python", "Count occurrences of words in a string in Python"],
     "```python\nfrom collections import Counter\n\ntext = \"the cat and the hat\"\ncounts = Counter(text.split())\nprint(counts.most_common(2))  # [('the', 2), ('cat', 1)]\n```\n\n"
     "`Counter` counts each item, and `most_common(n)` returns the top `n`."),

    # ------------------------------------------------------------ algorithms & data structures
    (["Write binary search in Python", "Binary search algorithm in Python", "Implement binary search"],
     "```python\ndef binary_search(arr, target):\n    low, high = 0, len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n"
     "        if arr[mid] == target:\n            return mid\n        if arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1\n\n"
     "print(binary_search([1, 3, 5, 7, 9], 7))  # 3\n```\n\n"
     "Binary search works on a **sorted** list and halves the search range each step, so it runs in **O(log n)** time."),
    (["Write bubble sort in Python", "Bubble sort algorithm in Python"],
     "```python\ndef bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        swapped = False\n        for j in range(n - 1 - i):\n"
     "            if arr[j] > arr[j + 1]:\n                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n                swapped = True\n        if not swapped:\n            break\n    return arr\n\n"
     "print(bubble_sort([5, 1, 4, 2]))  # [1, 2, 4, 5]\n```\n\n"
     "Each pass moves the largest remaining value to the end. It is **O(n²)**, so it is only good for learning or tiny lists."),
    (["Write quick sort in Python", "Quicksort algorithm in Python"],
     "```python\ndef quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n"
     "    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n"
     "    return quick_sort(left) + middle + quick_sort(right)\n\nprint(quick_sort([3, 6, 1, 8, 2]))  # [1, 2, 3, 6, 8]\n```\n\n"
     "Pick a pivot, split the list into smaller and larger parts, and sort each part recursively. Average time is **O(n log n)**."),
    (["Write merge sort in Python", "Merge sort algorithm in Python"],
     "```python\ndef merge_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    mid = len(arr) // 2\n    left, right = merge_sort(arr[:mid]), merge_sort(arr[mid:])\n"
     "    merged, i, j = [], 0, 0\n    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            merged.append(left[i]); i += 1\n"
     "        else:\n            merged.append(right[j]); j += 1\n    return merged + left[i:] + right[j:]\n\nprint(merge_sort([5, 2, 4, 1]))  # [1, 2, 4, 5]\n```\n\n"
     "Split the list in half, sort each half, then merge the two sorted halves. It always runs in **O(n log n)**."),
    (["Write a Python function to reverse a linked list", "Reverse a linked list in Python"],
     "```python\nclass Node:\n    def __init__(self, value, next=None):\n        self.value = value\n        self.next = next\n\n"
     "def reverse(head):\n    prev = None\n    while head:\n        head.next, prev, head = prev, head, head.next\n    return prev\n```\n\n"
     "Walk the list once, pointing each node's `next` back at the previous node. It runs in **O(n)** time and **O(1)** extra space."),
    (["Implement a stack in Python", "Stack data structure in Python"],
     "```python\nstack = []\nstack.append(1)    # push\nstack.append(2)\nprint(stack.pop())  # 2  (last in, first out)\nprint(stack[-1])    # 1  (peek)\n```\n\n"
     "A Python list works as a stack: `append` pushes and `pop` removes the most recent item."),
    (["Implement a queue in Python", "Queue data structure in Python"],
     "```python\nfrom collections import deque\n\nqueue = deque()\nqueue.append(\"a\")      # enqueue\nqueue.append(\"b\")\nprint(queue.popleft())  # a  (first in, first out)\n```\n\n"
     "`deque.popleft()` is O(1). Avoid `list.pop(0)`, which is O(n)."),
    (["What is the difference between a stack and a queue?", "Stack vs queue"],
     "- **Stack** – Last In, First Out (LIFO). Like a pile of plates: you take the top one first.\n"
     "- **Queue** – First In, First Out (FIFO). Like a line at a shop: the first person is served first.\n\n"
     "Stacks are used for undo and function calls; queues for task scheduling and BFS."),
    (["What is Big O notation?", "Explain time complexity"],
     "Big O describes how an algorithm's running time grows as the input size `n` grows:\n\n"
     "- **O(1)** – constant, e.g. list index access\n- **O(log n)** – binary search\n- **O(n)** – a single loop\n"
     "- **O(n log n)** – merge sort\n- **O(n²)** – nested loops, bubble sort\n\nIt focuses on the growth rate, not exact seconds."),
    (["Explain recursion with a simple example", "What is recursion?"],
     "Recursion is when a function calls itself to solve a smaller version of the same problem.\n\n"
     "```python\ndef countdown(n):\n    if n == 0:          # base case\n        print(\"Done!\")\n        return\n    print(n)\n    countdown(n - 1)    # recursive call\n\ncountdown(3)  # 3 2 1 Done!\n```\n\n"
     "Every recursive function needs a **base case** to stop, otherwise it recurses forever."),
    (["Find duplicate elements in a list in Python", "Python find duplicates"],
     "```python\ndef find_duplicates(items):\n    seen, dupes = set(), set()\n    for x in items:\n        if x in seen:\n            dupes.add(x)\n        seen.add(x)\n    return list(dupes)\n\n"
     "print(find_duplicates([1, 2, 3, 2, 1]))  # [1, 2]\n```\n\nA set gives O(1) lookups, so this runs in O(n)."),
    (["Two sum problem in Python", "Find two numbers that add up to a target"],
     "```python\ndef two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen:\n            return [seen[target - n], i]\n        seen[n] = i\n    return []\n\n"
     "print(two_sum([2, 7, 11, 15], 9))  # [0, 1]\n```\n\nStore each number's index; for each new number check whether its complement was already seen. O(n) time."),
    (["Check if two strings are anagrams in Python", "Anagram program in Python"],
     "```python\ndef is_anagram(a, b):\n    return sorted(a.lower()) == sorted(b.lower())\n\nprint(is_anagram(\"listen\", \"silent\"))  # True\n```\n\n"
     "Two words are anagrams if they contain the same letters, so their sorted letters match."),

    # ------------------------------------------------------------ javascript
    (["Write a JavaScript function to reverse a string", "Reverse a string in JavaScript"],
     "```javascript\nfunction reverseString(str) {\n  return str.split(\"\").reverse().join(\"\");\n}\n\nconsole.log(reverseString(\"hello\")); // \"olleh\"\n```\n\n"
     "`split` turns the string into an array, `reverse` flips it, and `join` builds the string again."),
    (["Difference between let, const and var in JavaScript", "let vs var vs const"],
     "- `var` – function-scoped, can be redeclared, hoisted as `undefined`. Avoid in modern code.\n"
     "- `let` – block-scoped and can be reassigned.\n- `const` – block-scoped and cannot be reassigned (objects inside can still change).\n\n"
     "Use `const` by default and `let` when the value must change."),
    (["What is a promise in JavaScript?", "Explain async await in JavaScript"],
     "A **Promise** represents a value that will be available later. `async/await` makes it read like normal code:\n\n"
     "```javascript\nasync function getUser() {\n  try {\n    const res = await fetch(\"https://api.example.com/user\");\n    const user = await res.json();\n"
     "    console.log(user);\n  } catch (err) {\n    console.error(\"Request failed:\", err);\n  }\n}\n```\n\n`await` pauses the function until the promise resolves; errors are caught with `try/catch`."),
    (["Why does my JavaScript forEach not wait for async calls?", "forEach with async await not working"],
     "`forEach` ignores the promises returned by an `async` callback, so it doesn't wait. Use `for...of` or `Promise.all`:\n\n"
     "```javascript\n// One after another\nfor (const id of ids) {\n  await saveItem(id);\n}\n\n// All at the same time\nawait Promise.all(ids.map((id) => saveItem(id)));\n```"),
    (["Explain map, filter and reduce in JavaScript", "JavaScript array methods map filter reduce"],
     "```javascript\nconst nums = [1, 2, 3, 4];\n\nnums.map((n) => n * 2);             // [2, 4, 6, 8]\nnums.filter((n) => n % 2 === 0);    // [2, 4]\n"
     "nums.reduce((sum, n) => sum + n, 0); // 10\n```\n\n`map` transforms every item, `filter` keeps items that pass a test, and `reduce` combines items into one value."),
    (["What is the difference between == and === in JavaScript?", "== vs === JavaScript"],
     "`==` compares values **after type conversion**, while `===` compares value **and type**:\n\n"
     "```javascript\n0 == \"0\";   // true\n0 === \"0\";  // false\n```\n\nPrefer `===` to avoid surprising conversions."),
    (["Write a React counter component", "React useState example"],
     "```jsx\nimport { useState } from \"react\";\n\nexport default function Counter() {\n  const [count, setCount] = useState(0);\n  return (\n"
     "    <button onClick={() => setCount(count + 1)}>\n      Clicked {count} times\n    </button>\n  );\n}\n```\n\n"
     "`useState` stores the count; calling `setCount` updates it and re-renders the component."),

    # ------------------------------------------------------------ SQL
    (["Write an SQL query to find the second highest salary", "Second highest salary SQL"],
     "```sql\nSELECT MAX(salary) AS second_highest\nFROM employees\nWHERE salary < (SELECT MAX(salary) FROM employees);\n```\n\n"
     "The subquery finds the top salary; the outer query finds the highest salary below it."),
    (["Explain SQL joins", "Difference between inner join and left join"],
     "- **INNER JOIN** – only rows that match in both tables.\n- **LEFT JOIN** – all rows from the left table, plus matches from the right (NULL if none).\n"
     "- **RIGHT JOIN** – the opposite of LEFT JOIN.\n- **FULL JOIN** – all rows from both tables.\n\n"
     "```sql\nSELECT c.name, o.total\nFROM customers c\nLEFT JOIN orders o ON o.customer_id = c.id;\n```"),
    (["SQL query to count rows by group", "Explain GROUP BY in SQL"],
     "```sql\nSELECT department, COUNT(*) AS employees\nFROM employees\nGROUP BY department\nHAVING COUNT(*) > 5;\n```\n\n"
     "`GROUP BY` makes one row per department, `COUNT(*)` counts rows in each group, and `HAVING` filters the groups."),

    # ------------------------------------------------------------ concepts / tooling
    (["What is OOP?", "Explain object oriented programming"],
     "Object-Oriented Programming organises code into **objects** that bundle data and behaviour. Its four main ideas:\n\n"
     "1. **Encapsulation** – hide internal details behind methods\n2. **Inheritance** – reuse code from a parent class\n"
     "3. **Polymorphism** – the same method name behaves differently per class\n4. **Abstraction** – expose only what users need"),
    (["What is an API?", "Explain REST API"],
     "An **API** (Application Programming Interface) lets programs talk to each other. A **REST API** uses HTTP methods on URLs:\n\n"
     "- `GET /users` – read\n- `POST /users` – create\n- `PUT /users/1` – update\n- `DELETE /users/1` – delete\n\nData is usually sent as JSON."),
    (["Create a simple FastAPI endpoint", "FastAPI hello world"],
     "```python\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get(\"/hello/{name}\")\ndef hello(name: str):\n    return {\"message\": f\"Hello, {name}!\"}\n```\n\n"
     "Run it with `uvicorn main:app --reload` and open `http://127.0.0.1:8000/hello/Koti`."),
    (["What is Git?", "Basic git commands"],
     "Git is a version control system that tracks changes to your code. Common commands:\n\n"
     "```bash\ngit init                 # start a repository\ngit add .                # stage changes\ngit commit -m \"message\"  # save a snapshot\n"
     "git push                 # upload to a remote\ngit pull                 # download updates\n```"),
    (["What is a virtual environment in Python?", "How to create a venv in Python"],
     "A virtual environment keeps each project's packages separate.\n\n```bash\npython -m venv venv\nvenv\\Scripts\\activate      # Windows\nsource venv/bin/activate   # macOS/Linux\npip install requests\n```"),
    (["What is machine learning?", "Explain machine learning simply"],
     "Machine learning is teaching computers to learn patterns from data instead of following hand-written rules. "
     "For example, a model sees many labelled emails and learns to tell spam from non-spam. "
     "The main types are **supervised**, **unsupervised** and **reinforcement** learning."),
    (["What is fine-tuning in deep learning?", "Explain LoRA fine-tuning"],
     "**Fine-tuning** continues training a pre-trained model on your own data so it specialises in your task. "
     "**LoRA** (Low-Rank Adaptation) freezes the original weights and trains small extra matrices instead, "
     "so it needs far less memory and produces a small adapter file."),

    # ------------------------------------------------------------ debugging
    (["What does IndexError: list index out of range mean?", "Fix list index out of range error"],
     "It means you accessed a position that doesn't exist. For a list of length 3, valid indexes are `0`, `1` and `2`.\n\n"
     "```python\nitems = [10, 20, 30]\nfor i in range(len(items)):  # not range(len(items) + 1)\n    print(items[i])\n```\n\nCheck your loop bounds or use `for item in items:`."),
    (["What does TypeError: can only concatenate str (not \"int\") to str mean?", "Fix cannot concatenate str and int"],
     "You tried to join text and a number with `+`. Convert the number or use an f-string:\n\n"
     "```python\nage = 21\nprint(\"Age: \" + str(age))\nprint(f\"Age: {age}\")\n```"),
    (["What is a KeyError in Python?", "Fix KeyError in Python dictionary"],
     "A `KeyError` means the key isn't in the dictionary. Check first or use `.get()`:\n\n"
     "```python\nuser = {\"name\": \"Ana\"}\nprint(user.get(\"email\", \"not set\"))  # no error\n```"),
    (["Fix IndentationError in Python", "What does IndentationError mean?"],
     "Python uses indentation to group code, so every line in a block must be indented the same way. "
     "Use **4 spaces** per level and don't mix tabs and spaces.\n\n```python\nif True:\n    print(\"inside\")   # 4 spaces\nprint(\"outside\")\n```"),
    (["ModuleNotFoundError: No module named requests", "How to fix ModuleNotFoundError in Python"],
     "The package isn't installed in the Python you are using. Install it into your active environment:\n\n"
     "```bash\npip install requests\n```\n\nIf you use a virtual environment, activate it first so the package goes to the right place."),
    (["Why is my Python code giving None?", "Function returns None in Python"],
     "A function returns `None` when it has no `return` statement (or `return` without a value):\n\n"
     "```python\ndef add(a, b):\n    result = a + b   # missing return!\n\ndef add_fixed(a, b):\n    return a + b\n```"),
]


def main():
    random.seed(42)
    rows = []
    for questions, answer in DATA:
        for q in questions:
            rows.append({"messages": [
                {"role": "user", "content": q},
                {"role": "assistant", "content": answer},
            ]})
    random.shuffle(rows)
    with open("train_dataset.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote {len(rows)} examples from {len(DATA)} topics -> train_dataset.jsonl")


if __name__ == "__main__":
    main()
