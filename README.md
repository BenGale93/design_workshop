# Python Design Workshop

20th October 2025

# Introduction

Benjamin Askew-Gale

* Software Engineer at NatWest
* [GitHub Profile](https://github.com/BenGale93)

## Agenda

* Introduce the code to refactor
* Dependency Injection
* Primitive Obsession
* Strategy Pattern
* Any other improvements

# Code to Refactor

## What does it do?

* Downloads raw files from GitHub.
* Breaks it into sections based on the file type.

## How could we improve it?

* How might it change in the future?
* How might someone use the output?
* How easy is it to understand?
* How easy is it to test?

# Dependency Injection

**Definition**

> Dependency injection is a technique in which an object or function receives
> other objects or functions that it requires, as opposed to creating them
> internally.

- Wikipedia

**Rule of Thumb**

Avoid initialising objects inside the function or class that is using them.
Particularly if they handle Input/Output (IO) tasks.

## Why?

* Easier to test
* Easier to customise behaviour
* Reduces coupling

## Example

```py
# Before
class PieMaker:
    def make(self) -> str:
        return "fruit pie"

class TakeAway:
    def __init__(self) -> None:
        self.food_maker = PieMaker()

    def order(self, customer: str):
        food = self.food_maker.make()
        print(f"Making {food} for {customer}")

take_away = TakeAway()
take_away.order("Ben")
```

```py
# After
class FruitPieMaker:
    def make(self) -> str:
        return "fruit pie"

class MeatPieMaker:
    def make(self) -> str:
        return "meat pie"

class TakeAway:
    def __init__(self, food_maker) -> None:
        self.food_maker = food_maker

    def order(self, customer: str):
        food = self.food_maker.make()
        print(f"Making {food} for {customer}")

take_away = TakeAway(MeatPieMaker())
take_away.order("Ben")
```

<!--

It does require a location in your code which is a bit messier and puts
everything together. I like to use class methods as alternative constructors
that use reasonable defaults.

-->


# Primitive Obsession

**Definition**

> Primitive obsession is a programming anti-pattern where only primitive data
> structures, such as integers, tuples, strings, lists and maps, are used to
> organise data.

**Rule of Thumb**

If you create a dictionary that always has the same keys, consider using a
class instead.

If common operations associated with that primitive don’t apply to the business
object, consider using a class instead.

## Why create dedicated types?

* Allows validation logic to be encapsulated with the type.
* Enforces business logic rules.
* Behaviour relevant to that type can be grouped with it using methods.
* Enables you to define interfaces, making code more flexible.

## Example

```py
# Before
pie = "fruit pie"

if "pie" not in pie:
    raise ValueError("Expected a type of pie.")
```

```py
# After
class Pie:
    def __init__(self, pie_type: str) -> None:
        if "pie" not in pie_type:
            raise ValueError("Expected a type of pie.")
        self.pie_type = pie

valid_pie = Pie("fruit_pie")
invalid_pie = Pie("burger")
```

<!--

If you have a UserID you would often use an integer as the underlying
primitive. Does it make sense to add two UserIDs together? No.

Similarly, if you have OrderID, does it make sense to provide that integer to a
register user function? No.

-->

# Strategy Pattern

**Definition**

> The strategy pattern enables selecting an algorithm at runtime.

**Rule of Thumb**

If you have an if statement, that could theoretically be infinitely long, to
select a particular algorithm within a function, consider using the strategy
pattern.

## Why?

* Easier to test
* Easier to customise behaviour
* Separates algorithm selection from usage

## Example

```py
# Before
def make_order(order: list[str], notify: str) -> None:
    print(f"Making order")
    if notify == "sms":
        print(f"Order summary to SMS: {order}")
    elif notify == "email":
        print(f"Order summary to email: {order}")
    elif notify == "social_media"
        print(f"Order summary to socials: {order}")
    else:
        raise ValueError("Unrecognised notification system")

make_order(["pie"], "email")
```

```py
# After
import typing as t

Notifier = t.Callable[[list[str]], None]

def sms_notifier(order: list[str]) -> None:
    print(f"Order summary to SMS: {order}")

def email_notifier(order: list[str]) -> None:
    print(f"Order summary to email: {order}")

def social_media_notifier(order: list[str]) -> None:
    print(f"Order summary to socials: {order}")

def make_order(order: list[str], notifier: Notifier) -> None:
    print(f"Making order")
    notifier(order)

make_order(["pie"], email_notifier)
```

<!--

In Python, you can implement the strategy pattern using functions or classes,
depending on the context.

You can also use functools.partial to make sure the function has the correct
signature.

-->

# Further Reading

* https://refactoring.guru/
* https://python-patterns.guide/
* https://www.youtube.com/@ArjanCodes
* https://python-3-patterns-idioms-test.readthedocs.io/en/latest/index.html
