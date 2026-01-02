+++
title = "Type Systems: From Generics to Dependent Types"
date = 2026-01-01
description = "Type system concepts from generics to dependent types, with code examples in Rust, Scala, and Idris"
[taxonomies]
keywords=["programming languages", "type systems", "rust", "functional programming"]
[extra]
author = "Federico Carrone"
pinned = true
+++

Every type error you've ever cursed at was a bug caught before production. Type systems reject nonsense at compile time so you don't discover it at 3 AM. But they vary wildly in what they can express and what guarantees they provide.

This guide covers type system concepts from the foundational ideas every programmer uses daily to the research frontier where types can prove your matrix multiplication is dimensionally correct.

<!-- more -->

## TL;DR

If you learn nothing else: ADTs + pattern matching + generics. These three concepts will improve your code in any language and take days to learn, not months.

The concepts here roughly progress from generics (reusable code) through traits (shared behavior) to linear types (resource safety) to dependent types (proving correctness). Each step buys you more compile-time guarantees at the cost of more work satisfying the type checker. If you know Java or TypeScript and want to go deeper, Rust hits a good balance between expressiveness and practicality.

## How to Read This Guide

The concepts are organized into tiers by complexity and practical relevance:

| Tier | What's Here | You Should Know If... |
|------|-------------|----------------------|
| 1: Foundational | Generics, ADTs, pattern matching | You write code |
| 2: Mainstream Advanced | Traits, GADTs, flow typing, existentials | You design libraries |
| 3: Serious Complexity | HKT, linear/ownership types, effects | You want deep FP or systems programming |
| 4: Research Level | Dependent types, session types | You work on PLs or verification |
| 5: Cutting Edge | HoTT, QTT, graded modalities | You do research |

You don't need to read linearly. Jump to what interests you. But concepts build on each other: if GADTs confuse you, make sure you understand [ADTs](#algebraic-data-types) first.

## Orthogonal Dimensions

Type systems are not a linear progression. They combine **orthogonal axes** independently. A language chooses a point on each axis.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TYPE SYSTEM TAXONOMY                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. CHECKING          Static ←───────────────────────────→ Dynamic          │
│                              ↑                                              │
│                           Gradual                                           │
│                                                                             │
│  2. EQUALITY          Nominal ←─────────────────────────→ Structural        │
│                                                                             │
│  3. POLYMORPHISM      None → Parametric → Bounded → Higher-Kinded           │
│                         ↓                                                   │
│                      Ad-hoc (overloading, traits, typeclasses)              │
│                                                                             │
│  4. INFERENCE         Explicit → Local → Bidirectional → Full (HM)          │
│                                                                             │
│  5. PREDICATES        Simple → Refinement → Dependent                       │
│                                                                             │
│  6. RESOURCES         Unrestricted → Relevant → Affine → Linear → Ordered   │
│                                                                             │
│  7. EFFECTS           Implicit → Monadic → Algebraic                        │
│                                                                             │
│  8. FLOW              Insensitive ←───────────────────→ Flow-Sensitive      │
│                                                                             │
│  9. COMMUNICATION     Untyped → Typed Messages → Actors → Session Types     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

EXAMPLE LANGUAGE POSITIONS:

  Rust        = Static + Nominal + Parametric + Bidirectional + Affine + Sensitive
  TypeScript  = Gradual + Structural + Parametric + Constraint + Sensitive
  Haskell     = Static + Nominal + Higher-Kinded + HM + Monadic
  Python      = Dynamic + Nominal + Ad-hoc + Explicit
  Go          = Static + Structural + Parametric + Local + Typed Channels
```

Each axis is independent. You can have static + structural (TypeScript), static + nominal (Java), or gradual + nominal (Python+mypy). The combinations create the design space.

### 1. Time of Checking

| Approach | When Types Checked | Examples |
|----------|-------------------|----------|
| **Static** | Compile time | Rust, Haskell, Java |
| **Dynamic** | Runtime | Python, Ruby, JavaScript |
| **Gradual** | Both, with boundaries | TypeScript, Python+mypy |

### 2. Type Equality

| Approach | Types Equal When... | Examples |
|----------|---------------------|----------|
| **Nominal** | Same declared name | Java, Rust, C# |
| **Structural** | Same shape/fields | TypeScript, Go interfaces |

### 3. Polymorphism

| Kind | What It Abstracts | Examples |
|------|-------------------|----------|
| **Parametric** | Type variables (`T`) | Generics in all typed languages |
| **Ad-hoc** | Different impls per type | Overloading, typeclasses, traits |
| **Subtype** | Substitutability | OOP inheritance, structural subtyping |
| **Bounded** | Constrained type variables | `T: Ord`, `T extends Comparable` |

### 4. Type Inference

| Strategy | How Types Inferred | Examples |
|----------|-------------------|----------|
| **Hindley-Milner** | Global, principal types | ML, Haskell, OCaml |
| **Bidirectional** | Up and down the AST | Rust, Scala, Agda |
| **Local** | Within expressions only | Java `var`, C++ `auto` |
| **Constraint-based** | Solve constraint systems | TypeScript, gradual systems |

### 5. Predicate Refinement

| Level | What Types Express | Examples |
|-------|-------------------|----------|
| **Simple** | Base types only | Most languages |
| **Refinement** | Types + predicates (`{x: Int \| x > 0}`) | Liquid Haskell, F* |
| **Dependent** | Types compute from values | Idris, Agda, Lean |

### 6. Substructural / Resource Tracking

| Discipline | Usage Rule | Examples |
|------------|-----------|----------|
| **Unrestricted** | Any number of times | Most languages |
| **Affine** | At most once | Rust ownership |
| **Linear** | Exactly once | Linear Haskell, Rust borrows |
| **Relevant** | At least once | Research systems |
| **Ordered** | Once, in order | Stack disciplines |

### 7. Effect Tracking

| Approach | What's Tracked | Examples |
|----------|---------------|----------|
| **None** | Effects implicit | Java, Python, Go |
| **Monadic** | Effects in type wrappers | Haskell IO |
| **Algebraic** | First-class effect handlers | Koka, OCaml 5 |

### 8. Flow Sensitivity

| Approach | Type Changes With... | Examples |
|----------|---------------------|----------|
| **Insensitive** | Fixed at declaration | Java, C |
| **Sensitive** | Control flow | TypeScript, Kotlin, Rust |

### 9. Concurrency / Communication

| Approach | What's Typed | Examples |
|----------|-------------|----------|
| **Untyped** | No protocol checking | Most languages |
| **Marker traits** | Send/Sync capabilities | Rust |
| **Session types** | Protocol state machines | Research, Links |

---

**Real languages combine these axes.** Rust is static + nominal + parametric + bidirectional + affine + flow-sensitive + marker traits. TypeScript is gradual + structural + parametric + constraint-based + flow-sensitive. There's no single "best" combination; each serves different goals.

## The Expressiveness Map

How type systems relate in terms of expressiveness versus annotation burden:

```text
                    EXPRESSIVENESS
                    Low ──────────────────► High
                    │
         Simple     │  ML            Haskell+Exts
         Inference  │   │               │
                    │   ▼               ▼
                    │  Rust ────► Rust+GATs
                    │   │               │
                    │   │      Scala 3  │
                    │   │         │     │
                    │   ▼         ▼     ▼
                    │         OCaml+Mods
                    │              │
                    │              ▼
         Needs      │         F*/Lean ◄── Refinements
         Annotations│              │
                    │              ▼
                    │         Idris/Agda ◄── Full Dependent
                    │              │
                    │              ▼
         Proof      │         Coq/Lean4 ◄── Proof Assistant
         Required   │              │
                    │              ▼
                    │         Cubical ◄── HoTT
                    │
                    ▼
              ANNOTATION BURDEN
```

The further right you go, the more you can express in types. The further down you go, the more work you must do to satisfy the type checker. The sweet spot depends on your domain.

---

## Dynamic Type Systems

Dynamic typing is a valid type system category, not the absence of types. In dynamic languages, types exist and are checked, just at runtime rather than compile time.

### How It Works

Values carry type tags at runtime. Operations check these tags before executing:

```python
# Python: types checked at runtime
def add(a, b):
    return a + b

add(1, 2)       # Works: both ints
add("a", "b")   # Works: both strings
add(1, "b")     # TypeError at runtime!
```

The type error still happens. It just happens when you run the code, not when you compile it. This trades earlier error detection for flexibility and development speed.

### Why Choose Dynamic Typing

- **Prototyping and exploration**: When you don't yet know what shape your data will take
- **Scripts and glue code**: Short-lived code where development speed matters more than maintenance
- **REPLs and interactive development**: Immediate feedback without compilation
- **Highly dynamic domains**: Serialization, ORMs, and metaprogramming where static types fight the problem
- **Duck typing**: If it quacks like a duck, use it as a duck. No need for explicit interface declarations

Dynamic typing isn't "no types." It's "types checked later."

The question isn't "static vs dynamic" but "how much static?" Python with type hints, TypeScript with strict mode, Rust with full ownership tracking: these represent different points on a spectrum. Pick the point that matches your problem.

Python, Ruby, JavaScript, Lisp, Clojure, Erlang, Elixir. Most have optional type systems now (Python's type hints, TypeScript for JavaScript).

## Gradual Typing

Gradual typing blends static and dynamic checking within the same language. You can add types incrementally, and the system inserts runtime checks at the boundaries between typed and untyped code.

### How It Works

In a gradually typed system, you can leave parts of your code untyped (using `any` or equivalent) while fully typing other parts. The type checker verifies the typed portions statically. At runtime, checks are inserted where typed code interacts with untyped code.

```typescript
// TypeScript: gradual typing in action
function greet(name: string): string {
    return `Hello, ${name}`;
}

// Fully typed: checked statically
greet("Ada");  // OK at compile time

// Escape hatch: 'any' bypasses static checking
function processUnknown(data: any): void {
    // No compile-time checking on 'data'
    console.log(data.someProperty);  // Could fail at runtime
}

// The boundary: where typed meets untyped
function fromExternal(json: any): User {
    // Runtime validation needed here
    return json as User;  // Risky! No guarantee json matches User
}
```

The **gradual guarantee** is the formal property that makes this work: adding type annotations should not change program behavior (unless there's a type error). You can migrate from untyped to typed code one function at a time without breaking anything.

This enables incremental adoption:
1. Start with a dynamically typed codebase
2. Add types to critical paths first
3. Gradually expand type coverage
4. Runtime checks catch boundary violations

### Blame Tracking

When a type error occurs at a boundary, who's at fault? **Blame tracking** attributes errors to the untyped side of the boundary. If typed code calls untyped code and gets a wrong type back, blame falls on the untyped code.

```python
# Python with type hints
def typed_function(x: int) -> int:
    return x + 1

def untyped_function(y):
    return "not an int"  # Bug here

# At runtime, the error is blamed on untyped_function
result: int = untyped_function(5)  # Runtime TypeError
```

TypeScript, Python (with mypy/pyright), PHP (with Hack), Racket (Typed Racket), Dart (before null safety), C# (with nullable reference types).

# Tier 1: Foundational

These concepts are solved problems with efficient algorithms. Every modern statically-typed language supports them. If you use a typed language, you're already using these. Understanding them deeply makes you more effective.

## Hindley-Milner Type Inference

Static typing traditionally meant annotating everything. Java's infamous:

```java
Map<String, List<Integer>> map = new HashMap<String, List<Integer>>();
```

This verbosity is why many developers fled to dynamic languages. But dynamic typing means discovering type mismatches at runtime, often in production.

What if the compiler could *figure out* the types? In 1969, Roger Hindley discovered (and Robin Milner independently rediscovered in 1978) an algorithm that can infer the most general type for any expression in a certain class of type systems, without any annotations.

The key observation: even without annotations, code contains type information. If you write `x + 1`, the compiler knows `x` must be a number because `+` requires numbers. If you write `x.len()`, `x` must be something with a `len` method. These constraints propagate through your program.

The algorithm works by:
1. Assigning fresh type variables to unknown types (like algebra: let `x` be unknown)
2. Collecting constraints from how values are used (`x + 1` means `x` must be numeric)
3. Unifying constraints to find the most general solution (solving the equations)

The "most general" part matters. If you write a function that works on any list, the algorithm infers "list of anything," not "list of integers." You get maximum reusability automatically.

- The brevity of Python with the safety of static typing
- Write code without type annotations; the compiler figures them out
- Catch type errors at compile time, not runtime
- The inferred type is always the *most general*, so your function works for all types that fit

```rust
// Rust: The compiler infers all types here
fn compose<A, B, C>(f: impl Fn(B) -> C, g: impl Fn(A) -> B) -> impl Fn(A) -> C {
    move |x| f(g(x))
}

let add_one = |x| x + 1;        // inferred: i32 -> i32
let double = |x| x * 2;         // inferred: i32 -> i32
let add_one_then_double = compose(double, add_one);

// No type annotations needed, compiler infers everything
let result = add_one_then_double(5);  // 12
```

```rust
// Even complex generic code needs minimal annotations
fn map<T, U>(items: Vec<T>, f: impl Fn(T) -> U) -> Vec<U> {
    items.into_iter().map(f).collect()
}

let numbers = vec![1, 2, 3];
let strings = map(numbers, |n| n.to_string());
// Compiler infers: T = i32, U = String
```

The trade-off: some advanced features ([GADTs](#generalized-algebraic-data-types-gadts), [higher-rank types](#rank-n-polymorphism)) break inference and require annotations. But for everyday code, you get static typing's safety without its traditional verbosity. Available in ML, OCaml, Haskell, Rust, F#, Elm, and Scala.

### Beyond HM: Other Inference Strategies

Hindley-Milner is the gold standard for inference in purely functional languages, but other strategies exist:

| Strategy | How It Works | Used In |
|----------|--------------|---------|
| **Bidirectional** | Types flow both up (inference) and down (checking) | Rust, Scala, Agda |
| **Constraint-based** | Collect constraints, solve with SMT/unification | Gradual typing, refinement types |
| **Local** | Infer within expressions, require declarations at boundaries | Java (var), C++ (auto) |

**Bidirectional typing** is particularly important for modern languages. Instead of pure inference (bottom-up) or pure checking (top-down), types flow both ways. When you write `let x: Vec<i32> = vec![1, 2, 3]`, the expected type `Vec<i32>` flows *down* to help infer the element type. When you write `let x = vec![1, 2, 3]`, the literal types flow *up* to infer `Vec<i32>`.

This scales better than pure HM to richer type systems. GADTs, higher-rank types, and dependent types all work well with bidirectional typing because explicit annotations guide inference where needed.

---

## Parametric Polymorphism (Generics)

You write a function to get the first element of a list of integers. Then you need it for strings. Then for custom types. You end up with `first_int`, `first_string`, `first_user`, duplicated code that differs only in types.

The alternative, using a universal type like `Object` or `any`, throws away type safety entirely. You're back to hoping you don't pass the wrong thing.

Abstract over the type itself. Write the function *once* with a type parameter, and it works for *any* type. The crucial property is **parametricity**: the function must behave the same way regardless of what type you plug in. It can't inspect the type or behave differently for integers versus strings.

This constraint is a feature, not a limitation. When a function is parametric in `T`, it can only shuffle `T` values around. It can't create new `T`s out of thin air, can't compare them, can't print them. This means generic functions come with "theorems for free": guarantees about their behavior that follow purely from their type signature.

For example, a function with signature `fn mystery<T>(x: T) -> T` can *only* return `x`. There's nothing else it could possibly return. The type signature alone proves the implementation. Similarly, `fn pair<T>(x: T) -> (T, T)` must return `(x, x)`. The parametricity constraint eliminates every other possibility.

- Write once, use with any type
- No code duplication
- Compiler verifies each usage with concrete types
- Parametricity guarantees properties: a function `fn identity<T>(x: T) -> T` can *only* return `x`

```rust
// Rust: One function works for any type T
fn first<T>(slice: &[T]) -> Option<&T> {
    slice.first()
}

first(&[1, 2, 3]);              // Option<&i32>
first(&["a", "b"]);             // Option<&&str>
first(&[User::new("Ada")]);     // Option<&User>

// The implementation is identical for all types
// Parametricity: we can't inspect T, so we can only shuffle values around
```

```rust
// What can this function possibly do?
fn mystery<T>(x: T) -> T {
    // We can't:
    // - Print x (we don't know it implements Display)
    // - Compare x (we don't know it implements Eq)
    // - Clone x (we don't know it implements Clone)
    // We can ONLY return x
    x
}
```

---

## Subtyping

You have a function that operates on any `Animal`. You've defined `Dog`, `Cat`, and `Bird` types. Without some way to express "a Dog *is* an Animal," you'd need separate functions for each type, or abandon type safety.

If type `B` has everything type `A` has (and possibly more), you can use a `B` anywhere an `A` is expected. This is subtyping: `Dog <: Animal` means Dog is a subtype of Animal.

Think of it as a contract. An `Animal` promises certain capabilities: it has a name, it can speak. A `Dog` fulfills that contract and more: it also has a breed and can fetch. Anywhere the code expects "something that has a name and can speak," a Dog works fine. The extra capabilities are ignored but don't cause problems.

This is the Liskov Substitution Principle encoded in the type system: if `Dog <: Animal`, then any property that holds for `Animal` should hold for `Dog`. You can substitute Dogs for Animals without breaking correctness.

### Nominal vs Structural: Two Philosophies

This is a fundamental classification of type systems, not just a detail of subtyping:

| Aspect | Nominal | Structural |
|--------|---------|------------|
| Type equality | Based on declared name | Based on shape/structure |
| Subtyping | Explicit declaration required | Implicit if structure matches |
| Philosophy | "What it's called" | "What it can do" |
| Abstraction | Strong boundaries | Flexible composition |
| Refactoring | Rename breaks compatibility | Structure changes break compatibility |

**Nominal typing** requires explicit declarations. Even if two types have identical fields, they're different types unless related by declaration:

```java
// Java: nominal typing
class Meters { double value; }
class Feet { double value; }

// These are DIFFERENT types despite identical structure
Meters m = new Meters();
Feet f = m;  // ERROR: incompatible types
```

**Structural typing** cares only about shape. If it has the right fields and methods, it fits:

```typescript
// TypeScript: structural typing
interface Point { x: number; y: number; }

// Any object with x and y is a Point
const p: Point = { x: 1, y: 2 };           // OK
const q: Point = { x: 1, y: 2, z: 3 };     // OK (extra field allowed)

class Coordinate { x: number; y: number; }
const r: Point = new Coordinate();          // OK (same structure)
```

**Go's approach** is interesting: nominal for defined types, but interfaces are structural. A type implements an interface if it has the right methods, no declaration needed.

```go
// Go: structural interfaces
type Reader interface {
    Read(p []byte) (n int, err error)
}

// MyFile implements Reader without declaring it
type MyFile struct { ... }
func (f MyFile) Read(p []byte) (int, error) { ... }

// Works: MyFile has the right method
func process(r Reader) { ... }
process(MyFile{})  // OK
```

- Polymorphism through substitutability
- Model "is-a" relationships
- Accept broader types in function parameters
- Return narrower types from functions

```typescript
// TypeScript: Structural subtyping
interface Animal {
    name: string;
    speak(): string;
}

interface Dog {
    name: string;
    breed: string;
    speak(): string;
    fetch(): void;
}

function greet(animal: Animal): string {
    return `${animal.name} says ${animal.speak()}`;
}

const dog: Dog = {
    name: "Rex",
    breed: "German Shepherd",
    speak: () => "Woof!",
    fetch: () => console.log("Fetching...")
};

greet(dog);  // OK! Dog has everything Animal needs

// The compiler checks structural compatibility
// Dog has name: string ✓
// Dog has speak(): string ✓
// Extra fields (breed, fetch) are fine
```

The downside: subtyping complicates type inference and introduces variance questions. When `Dog <: Animal`, is `List<Dog>` a subtype of `List<Animal>`? It depends on whether the list is read-only (covariant), write-only (contravariant), or mutable (invariant). See [Variance](#variance) for details. Rust sidesteps this by using traits instead of subtyping for polymorphism.

---

## Algebraic Data Types

You're modeling a user who can be either anonymous or logged in. In a typical OOP language, you might write:

```java
class User {
    String name;       // null if anonymous
    boolean isLoggedIn;
}
```

Tony Hoare calls null references his "billion dollar mistake"—but the problem runs deeper than null. This type allows four states: anonymous with no name, anonymous with a name (!), logged in with a name, logged in without a name (!). Two of these are nonsense, but your type permits them. Every function must check for and handle impossible states.

Types should describe *exactly* the valid states. We need two tools:

- **Sum types** (enums, tagged unions): "this OR that", a value is one of several variants
- **Product types** (structs, records): "this AND that", a value contains all fields

Combined, these are **algebraic data types** (ADTs). The "algebra" comes from how you calculate possible values: products multiply (struct with 2 bools = 2 × 2 = 4 states), sums add (enum with 3 variants = 3 states).

Here's the algebra in action. Consider:
- `bool` has 2 values: `true`, `false`
- `(bool, bool)` has 2 × 2 = 4 values: `(true, true)`, `(true, false)`, `(false, true)`, `(false, false)`
- `enum Either { Left(bool), Right(bool) }` has 2 + 2 = 4 values: `Left(true)`, `Left(false)`, `Right(true)`, `Right(false)`

The power comes from combining them. You model your domain with exactly the states that make sense. If a user is either anonymous (no data) or logged in (with name and email), you write that directly. The type system then enforces that you can't access a name for an anonymous user, because that field doesn't exist in that variant.

- **Make illegal states unrepresentable**: if your type can't hold invalid data, you can't have bugs from invalid data
- No null checks for "impossible" cases
- Self-documenting domain models
- Exhaustive [pattern matching](#pattern-matching) (covered next)

```rust
// Rust: This type CANNOT represent an invalid state
enum User {
    Anonymous,
    LoggedIn { name: String, email: String },
}

// There is no way to construct:
// - "Logged in with no name" (LoggedIn requires name)
// - "Anonymous with a name" (Anonymous has no fields)

fn greet(user: &User) -> String {
    match user {
        User::Anonymous => "Hello, guest".to_string(),
        User::LoggedIn { name, .. } => format!("Hello, {}", name),
    }
}
```

```rust
// Model a payment result: each variant has exactly the data it needs
enum PaymentResult {
    Success { transaction_id: String, amount: f64 },
    Declined { reason: String },
    NetworkError { retry_after_seconds: u32 },
}

// No nulls. No "reason" field that's only valid sometimes.
// Each variant is self-contained.
```

```rust
// The classic: Option replaces null
enum Option<T> {
    None,
    Some(T),
}

// Result replaces exceptions
enum Result<T, E> {
    Ok(T),
    Err(E),
}

// These are ADTs! Sum types with generic parameters.
```

If you come from OOP, ADTs require rethinking how you model data. Instead of class hierarchies with methods, you define data structures and functions that pattern match on them. Available in Rust, Haskell, OCaml, F#, Scala, Swift, and Kotlin.

---

## Pattern Matching

Given an algebraic data type, you need to branch on its variants and extract data. With OOP, you'd use `instanceof` checks or the visitor pattern, both verbose and error-prone. Worse: when you add a new variant, the compiler doesn't tell you about all the places that need updating.

Pattern matching is the natural counterpart to [ADTs](#algebraic-data-types). If constructors *build* sum types, pattern matching *deconstructs* them. They're two sides of the same coin.

The compiler knows every possible variant of your sum type. When you write a `match`, it checks that you've covered them all. Forget a case? Compile error. Add a new variant to your enum? Every `match` in your codebase that doesn't handle it becomes a compile error. This is **exhaustiveness checking**.

The comparison to `if-else` or `switch` is instructive. In most languages, `switch` doesn't warn you about missing cases. Pattern matching does. And unlike the visitor pattern (OOP's answer to this problem), pattern matching is concise and doesn't require boilerplate classes.

- **Exhaustiveness checking**: forget a case, get a compile error
- **Refactoring safety**: add a variant, compiler shows everywhere to update
- **Destructuring built-in**: extract fields while matching
- Cleaner than if-else chains or visitor patterns

```rust
// Rust: Compiler ensures all cases handled
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(u8, u8, u8),
}

fn process(msg: Message) -> String {
    match msg {
        Message::Quit => "Goodbye".to_string(),
        Message::Move { x, y } => format!("Moving to ({}, {})", x, y),
        Message::Write(text) => format!("Writing: {}", text),
        Message::ChangeColor(r, g, b) => format!("Color: #{:02x}{:02x}{:02x}", r, g, b),
    }
}

// If you forget a case:
// error[E0004]: non-exhaustive patterns: `Message::ChangeColor(_, _, _)` not covered
```

```rust
// Guards add conditions
fn describe(n: i32) -> &'static str {
    match n {
        0 => "zero",
        n if n < 0 => "negative",
        n if n % 2 == 0 => "positive even",
        _ => "positive odd",
    }
}

// Nested patterns
fn first_two<T: Clone>(items: &[T]) -> Option<(T, T)> {
    match items {
        [a, b, ..] => Some((a.clone(), b.clone())),
        _ => None,
    }
}
```

Pattern matching is now in C# 8+, Python 3.10+, and most functional languages. Once you use it, you won't go back.

---

# Tier 2: Mainstream Advanced

These features appear in modern production languages but require more sophistication to use well. They're essential for library authors and for writing highly generic code.

## Traits / Typeclasses

You want to sort a list. Sorting requires comparison. How does the generic sort function know how to compare your custom `User` type?

Approaches without traits:
- **Inheritance**: `User extends Comparable`, but what if User comes from a library you don't control?
- **Pass a comparator every time**: verbose, easy to forget
- **Duck typing**: no compile-time safety, crashes at runtime if method missing

Separate the *interface* from the *type*. Define `Ord` (ordering), `Eq` (equality), `Display` (printing) as standalone interfaces called traits (Rust) or typeclasses (Haskell). Then declare that `User` implements them, *even if you didn't write User*.

This solves the "expression problem": how do you add both new types and new operations without modifying existing code? With OOP inheritance, adding new types is easy (new subclass), but adding new operations is hard (modify every class). With traits, you can add new operations (new trait) and implement them for existing types, even types from other libraries.

The implementation is resolved at compile time, with zero runtime cost. When you call `user.cmp(&other)`, the compiler knows exactly which comparison function to use because it knows the concrete type. No vtable lookup, no dynamic dispatch. This is called **monomorphization**: the compiler generates specialized code for each type you use.

The "coherence" rule prevents chaos: there can be at most one implementation of a trait for a type. You can't have two different ways to compare Users. This means you can always predict which implementation will be used.

- **Ad-hoc polymorphism**: different behavior for different types, resolved at compile time
- **Retroactive implementation**: add interfaces to types you don't own
- **Coherence**: at most one implementation per type (no ambiguity)
- **Trait bounds**: require capabilities, not inheritance

```rust
// Rust: Define a trait
trait Summary {
    fn summarize(&self) -> String;
}

// Implement for your type
struct Article {
    title: String,
    author: String,
    content: String,
}

impl Summary for Article {
    fn summarize(&self) -> String {
        format!("{} by {}", self.title, self.author)
    }
}

// Implement for a type you don't own
impl Summary for i32 {
    fn summarize(&self) -> String {
        format!("The number {}", self)
    }
}

// Use as a bound: T must implement Summary
fn notify<T: Summary>(item: &T) {
    println!("Breaking news! {}", item.summarize());
}

// Or with impl Trait syntax
fn notify_short(item: &impl Summary) {
    println!("Breaking news! {}", item.summarize());
}
```

```rust
// Standard library traits
use std::fmt::Display;
use std::cmp::Ord;

// Multiple bounds
fn print_sorted<T: Display + Ord>(mut items: Vec<T>) {
    items.sort();
    for item in items {
        println!("{}", item);
    }
}

// Default implementations
trait Greet {
    fn name(&self) -> &str;

    fn greet(&self) -> String {
        format!("Hello, {}!", self.name())  // default impl
    }
}
```

Rust's orphan rules restrict where you can implement traits to prevent conflicting implementations. This is sometimes frustrating but maintains coherence.

---

## Associated Types

You're defining an `Iterator` trait. Each iterator produces items of some type. With regular generics, you'd write `Iterator<Item>`. But this makes `Iterator<i32>` and `Iterator<String>` *different traits*, and a type can only implement one of them.

What you want: the item type should be *determined by* the implementing type, not chosen by the user.

Some type parameters are *outputs* (determined by the implementation), not *inputs* (chosen by the caller). Associated types express this: "when you implement this trait, you must specify what Item is."

The distinction matters. With a regular type parameter like `Iterator<T>`, you're saying "this is an iterator that could work with any T." But that's not how iterators work. A `VecIterator` always produces the type that the Vec contains. The type is determined by the iterator, not chosen by the user.

Think of it as a type-level function. Given a type that implements `Iterator`, you can ask "what does it produce?" and get back the associated `Item` type. `Vec<i32>` implements `Iterator` with `Item = i32`. `HashMap<K, V>` implements `Iterator` with `Item = (K, V)`. The implementing type determines the associated type.

- **Cleaner APIs**: one trait, not a family of traits
- **Type-level functions**: the implementing type determines the associated type
- **Better error messages**: "Item not found" vs. "Iterator<??> not satisfied"

```rust
// Rust: The standard Iterator trait
trait Iterator {
    type Item;  // Associated type: implementor decides

    fn next(&mut self) -> Option<Self::Item>;
}

// Implementing: specify what Item is
struct Counter {
    count: u32,
    max: u32,
}

impl Iterator for Counter {
    type Item = u32;  // Counter produces u32s

    fn next(&mut self) -> Option<u32> {
        if self.count < self.max {
            self.count += 1;
            Some(self.count)
        } else {
            None
        }
    }
}

// Using: the Item type is known from the iterator type
fn sum_all<I: Iterator<Item = i32>>(iter: I) -> i32 {
    iter.fold(0, |acc, x| acc + x)
}
```

```rust
// Without associated types (what you'd have to write)
trait BadIterator<Item> {
    fn next(&mut self) -> Option<Item>;
}

// Problem: impl BadIterator<i32> and impl BadIterator<String>
// are different traits! A type could implement both!
```

Associated types are less flexible than type parameters when you need the same type to implement a trait multiple ways. But for most cases, they make APIs cleaner.

---

## Flow-Sensitive Typing

You check if a value is null before using it. You know it's not null inside the `if` block. But does the type system know?

```java
// Java: the type system doesn't track the check
Object x = maybeNull();
if (x != null) {
    // You KNOW x isn't null here
    // But the type is still Object, not NonNull<Object>
    x.toString();  // Still need to handle potential null?
}
```

**Flow-sensitive typing** (also called **occurrence typing** or **type narrowing**) refines types based on control flow. After a type check, the type system narrows the variable's type in branches where the check succeeded.

Type information *changes* as you move through code. The type of `x` isn't fixed at its declaration. It evolves based on what the program has learned. After `if (x !== null)`, the type of `x` in the `then` branch is narrower than at the start.

This bridges static and dynamic typing philosophies. Dynamic languages always know the runtime type. Static languages traditionally fix types at declaration. Flow-sensitive typing lets static types benefit from runtime checks without losing static guarantees.

```typescript
// TypeScript: flow-sensitive typing
function process(value: string | number | null) {
    // Here: value is string | number | null

    if (value === null) {
        return;  // value is null in this branch
    }
    // Here: value is string | number (null eliminated)

    if (typeof value === "string") {
        // Here: value is string
        console.log(value.toUpperCase());  // OK: string method
    } else {
        // Here: value is number
        console.log(value.toFixed(2));     // OK: number method
    }
}

// Works with user-defined type guards too
interface Cat { meow(): void; }
interface Dog { bark(): void; }

function isCat(pet: Cat | Dog): pet is Cat {
    return (pet as Cat).meow !== undefined;
}

function speak(pet: Cat | Dog) {
    if (isCat(pet)) {
        pet.meow();  // TypeScript knows pet is Cat here
    } else {
        pet.bark();  // TypeScript knows pet is Dog here
    }
}
```

```kotlin
// Kotlin: smart casts
fun process(x: Any) {
    if (x is String) {
        // x is automatically cast to String here
        println(x.length)  // No explicit cast needed
    }

    // Works with null checks too
    val name: String? = getName()
    if (name != null) {
        // name is String here, not String?
        println(name.length)
    }
}
```

- **Eliminates redundant casts**: The compiler tracks what you've already checked
- **Catches impossible branches**: If a branch can never execute, the compiler warns
- **Natural null handling**: Null checks automatically narrow types
- **Type guards**: User-defined functions can narrow types

Flow-sensitive typing complicates the type system. The type of a variable depends on *where* you are in the code, not just its declaration. This makes type checking more complex and can lead to surprising behavior when variables are reassigned or captured in closures.

TypeScript, Kotlin, Ceylon, Flow (JavaScript), Rust (with pattern matching), Swift, and increasingly other modern languages.

---

## Intersection and Union Types

You have a value that could be one of several types. Or a value that must satisfy multiple interfaces simultaneously. Regular generics and subtyping don't express these relationships cleanly.

```typescript
// How do you type a function that accepts string OR number?
// How do you require an object to be BOTH Serializable AND Comparable?
```

**Union types** (`A | B`) represent "this OR that." A value of type `A | B` is either an `A` or a `B`. You must handle both possibilities before using type-specific operations.

**Intersection types** (`A & B`) represent "this AND that." A value of type `A & B` has all properties of both `A` and `B`. It satisfies both interfaces simultaneously.

These correspond to logical OR (union) and AND (intersection).

```typescript
// TypeScript: Union types
type StringOrNumber = string | number;

function process(value: StringOrNumber) {
    // Must narrow before using type-specific operations
    if (typeof value === "string") {
        console.log(value.toUpperCase());  // OK: string method
    } else {
        console.log(value.toFixed(2));     // OK: number method
    }
}

// Discriminated unions: tagged sum types
type Result<T, E> =
    | { kind: "ok"; value: T }
    | { kind: "error"; error: E };

function handle<T, E>(result: Result<T, E>) {
    switch (result.kind) {
        case "ok": return result.value;      // TypeScript knows value exists
        case "error": throw result.error;    // TypeScript knows error exists
    }
}
```

```typescript
// TypeScript: Intersection types
interface Named { name: string; }
interface Aged { age: number; }

type Person = Named & Aged;  // Must have both name AND age

const person: Person = {
    name: "Ada",
    age: 36
};

// Intersection for mixin-style composition
interface Loggable { log(): void; }
interface Serializable { serialize(): string; }

type LoggableAndSerializable = Loggable & Serializable;

function process(obj: LoggableAndSerializable) {
    obj.log();           // OK: has Loggable
    obj.serialize();     // OK: has Serializable
}
```

```scala
// Scala 3: Union and intersection types
def process(value: String | Int): String = value match
  case s: String => s.toUpperCase
  case i: Int => i.toString

// Intersection: must satisfy both traits
trait Runnable { def run(): Unit }
trait Stoppable { def stop(): Unit }

def manage(service: Runnable & Stoppable): Unit =
  service.run()
  service.stop()
```

- **Precise typing for heterogeneous data**: JSON, configs, APIs with variant responses
- **Mixin composition**: Combine interfaces without inheritance hierarchies
- **Discriminated unions**: Type-safe pattern matching on tagged variants
- **Subtyping relationships**: `A` is subtype of `A | B`; `A & B` is subtype of `A`

### Intersection Types in Type Theory

In formal type theory, intersection types have deeper significance. The **intersection type discipline** can type more programs than simple types: some programs untypable in System F become typable with intersections. This is because intersections allow giving a term multiple types simultaneously.

```text
// The identity function can have type:
λx.x : Int → Int           // for integers
λx.x : String → String     // for strings
λx.x : (Int → Int) ∧ (String → String)  // BOTH at once with intersection
```

This enables **principal typings** for some systems and is used in program analysis and partial evaluation.

TypeScript (extensive), Scala 3, Flow, Ceylon, Pike, CDuce, and research languages. Java has limited intersection types in generics (`<T extends A & B>`). Haskell achieves similar effects through typeclasses.

---

## Generalized Algebraic Data Types (GADTs)

You're building a type-safe expression language. You have `Add(expr, expr)` and `Equal(expr, expr)`. `Add` should return an integer; `Equal` should return a boolean. But with regular ADTs, the `Expr` type has no way to track what type of value each expression produces.

Your `eval` function either:
- Returns `Object` and requires downcasting (unsafe)
- Returns a sum type like `Value::Int | Value::Bool` and requires checking (verbose)

Let each constructor specify its own, more precise return type. `Add` constructs an `Expr<Int>`; `Equal` constructs an `Expr<Bool>`. The type parameter tracks what the expression evaluates to.

With regular ADTs, all constructors return the same type. `Some(x)` and `None` both return `Option<T>` for the same `T`. But with GADTs, different constructors can return *different* type instantiations. `LitInt(5)` returns `Expr<Int>`. `LitBool(true)` returns `Expr<Bool>`. The "generalized" means this flexibility.

Pattern matching reveals the payoff. If you match on an `Expr<Int>` and see a `LitInt`, the compiler knows the type parameter is `Int`. It can use this knowledge to type-check the branch correctly. You can return an `Int` directly, not a wrapped type. This information flow from patterns to type checking is what makes type-safe evaluators possible.

The cost: type inference breaks. The compiler can't always figure out what type an expression should have, because it depends on which constructor was used. You need explicit type annotations at GADT match sites.

- **Type-safe interpreters and DSLs**: the type tracks the expression's result type
- **Eliminates impossible patterns**: if you match on `Expr<Int>`, you know it's not `LitBool`
- **More precise types**: information flows from patterns to the type checker

Rust doesn't support GADTs directly. Scala 3 has clean syntax:

```scala
// Scala 3: GADT syntax
enum Expr[A]:
  case LitInt(value: Int) extends Expr[Int]
  case LitBool(value: Boolean) extends Expr[Boolean]
  case Add(left: Expr[Int], right: Expr[Int]) extends Expr[Int]
  case Equal(left: Expr[Int], right: Expr[Int]) extends Expr[Boolean]
  case If[T](cond: Expr[Boolean], thenBr: Expr[T], elseBr: Expr[T]) extends Expr[T]

// Type-safe eval: return type matches expression type
def eval[A](expr: Expr[A]): A = expr match
  case Expr.LitInt(n) => n           // here A = Int, return Int ✓
  case Expr.LitBool(b) => b          // here A = Boolean, return Boolean ✓
  case Expr.Add(l, r) => eval(l) + eval(r)
  case Expr.Equal(l, r) => eval(l) == eval(r)
  case Expr.If(c, t, e) => if eval(c) then eval(t) else eval(e)

// This WON'T compile:
// Expr.Add(Expr.LitBool(true), Expr.LitInt(1))
// Error: expected Expr[Int], got Expr[Boolean]

// Usage
val expr: Expr[Int] = Expr.Add(Expr.LitInt(1), Expr.LitInt(2))
val result: Int = eval(expr)  // Type-safe: result is Int, not Object
```

GADTs are available in Haskell, OCaml, and Scala 3. TypeScript has limited support through type guards.

---

## Existential Types

You want a collection of things that share a trait, but they're different concrete types: `Vec<???>` containing integers, strings, and custom structs. But `Vec<T>` requires one specific `T`.

Hide the concrete type behind an interface. An existential type says: "there *exists* some type `T` implementing this trait, but I won't tell you which." You can only use operations from the trait, nothing type-specific.

The duality with generics:
- **Generics (universal)**: caller picks the type, "for *all* types T, this works"
- **Existentials**: callee picks the type, "there *exists* some type T, but you don't know which"

Why is this useful? Consider a plugin system. Each plugin is a different type, but they all implement `Plugin`. You want a `Vec<Plugin>` containing all your plugins. With generics alone, you'd need `Vec<SomeSpecificPlugin>`. With existentials, you get `Vec<Box<dyn Plugin>>`: a collection of "things that are some type implementing Plugin." The concrete types are hidden (existentially quantified), but you can still call Plugin methods on them.

- **Heterogeneous collections**: mix different types with shared interfaces
- **Information hiding**: callers can't depend on the concrete type
- **Dynamic dispatch**: select implementation at runtime

```rust
// Rust: dyn Trait is an existential type
use std::fmt::Display;

fn make_displayables() -> Vec<Box<dyn Display>> {
    vec![
        Box::new(42),
        Box::new("hello"),
        Box::new(3.14),
    ]
}

fn print_all(items: Vec<Box<dyn Display>>) {
    for item in items {
        println!("{}", item);  // Can only call Display methods
    }
}

// You don't know the concrete types, but you can display them all
```

```rust
// impl Trait in return position is also existential
fn make_iterator() -> impl Iterator<Item = i32> {
    // Caller doesn't know this is specifically a Range
    // They only know it's "some iterator of i32"
    0..10
}

// Useful for hiding complex iterator adapter chains
fn complex_iter() -> impl Iterator<Item = i32> {
    (0..100)
        .filter(|x| x % 2 == 0)
        .map(|x| x * x)
        .take(10)
}
```

The cost: `dyn Trait` has runtime overhead (vtable lookup) and you can't recover the concrete type. Use generics when you know the type statically.

---

## Rank-N Polymorphism

Normally, the *caller* of a generic function chooses the type parameter. But sometimes you want the *callee* to choose. Consider a function that applies a transformation to both elements of a pair, but the elements have different types.

```rust
// This doesn't work in Rust
fn apply_to_both<T>(f: impl Fn(T) -> T, pair: (i32, String)) -> (i32, String) {
    (f(pair.0), f(pair.1))  // Error! T can't be both i32 and String
}
```

In Rank-1 polymorphism (normal generics), `forall` is at the outside: the caller picks one `T` for the whole function. In Rank-2+, `forall` appears inside argument types: "the argument must be a function that works for *any* type."

The "rank" refers to how deeply `forall` can be nested:
- **Rank 0**: No polymorphism. `int -> int`.
- **Rank 1**: `forall` at the top. `forall T. T -> T`. Caller picks `T`.
- **Rank 2**: `forall` in argument position. `(forall T. T -> T) -> int`. The *argument* must be polymorphic.
- **Rank N**: Arbitrary nesting.

Why would you want this? Consider the ST monad trick in Haskell. `runST` has type `(forall s. ST s a) -> a`. The `s` type variable is universally quantified *inside* the argument. This means `runST` picks `s`, not the caller. Since `s` is chosen by `runST` and immediately goes out of scope, no reference tagged with `s` can escape. This is how Haskell provides safe, in-place mutation: the type system guarantees mutable references can't leak outside `runST`.

The cost is severe: type inference becomes undecidable for Rank-2 and above. You must annotate everything. Most languages avoid this complexity.

- **More precise types**: "must work for all types" is a strong requirement
- **Encapsulation**: ST monad uses Rank-2 types to ensure references can't escape
- **Enable patterns impossible with Rank-1**

Rust can't express Rank-N types directly. OCaml can:

```ocaml
(* OCaml: Rank-2 polymorphism via record types *)

(* Rank-1: caller chooses 'a *)
let id : 'a -> 'a = fun x -> x

(* Rank-2 requires a record with polymorphic field *)
type poly_fn = { f : 'a. 'a -> 'a }

let apply_to_both (p : poly_fn) (x, y) = (p.f x, p.f y)

(* This works: id is polymorphic *)
let result = apply_to_both { f = id } (42, "hello")
(* result = (42, "hello") *)

(* This FAILS: (+1) only works on int, not any type *)
(* let bad = apply_to_both { f = fun x -> x + 1 } (42, "hello") *)
(* Error: This field value has type int -> int
   which is less general than 'a. 'a -> 'a *)
```

```haskell
-- Haskell: cleaner Rank-2 syntax with RankNTypes extension
{-# LANGUAGE RankNTypes #-}

-- runST : (forall s. ST s a) -> a

-- The 's' type variable is chosen by runST, not the caller.
-- This makes it impossible to return an STRef outside runST,
-- because the 's' won't match anything outside.
```

Rank-N types are rare outside Haskell. Most languages don't support them, and you can usually work around their absence.

---

# Tier 3: Serious Complexity

These features require significant learning investment but let you write abstractions impossible in simpler type systems. They're common in functional programming languages and increasingly appearing in mainstream languages.

## Higher-Kinded Types (HKT)

`Vec`, `Option`, `Result`: they're all "containers" you can map a function over. You write `map` for `Vec`. Then for `Option`. Then for `Result`. The implementations look structurally identical:

```rust
fn map_vec<A, B>(items: Vec<A>, f: impl Fn(A) -> B) -> Vec<B>
fn map_option<A, B>(item: Option<A>, f: impl Fn(A) -> B) -> Option<B>
fn map_result<A, B, E>(item: Result<A, E>, f: impl Fn(A) -> B) -> Result<B, E>
```

Can't we abstract over the *container itself*?

Types have **kinds**, just as values have types:

```text
Int         : Type                    -- a plain type
Vec         : Type -> Type            -- takes a type, returns a type
Result      : Type -> Type -> Type    -- takes two types, returns a type
```

`Int` is a complete type. But `Vec` by itself is not a type. You can't have a variable of type `Vec`. You need `Vec<i32>` or `Vec<String>`. `Vec` is a *type constructor*: give it a type, get back a type.

HKT lets you abstract over type constructors like `Vec` and `Option`, instead of only types like `Int`. You can define `Functor` as a trait for *any* type constructor, then implement it once for each container.

The pattern `Functor`, `Applicative`, `Monad` from functional programming all require HKT. They describe properties of *containers*, not specific types. "Functor" means "you can map over this container." That applies to `Vec`, `Option`, `Result`, `Future`, `IO`, and infinitely many other type constructors. Without HKT, you'd write `map_vec`, `map_option`, `map_result` separately. With HKT, you write one `map` that works for any `Functor`.

- **Functor, Monad, Applicative**: abstract patterns over any container
- **Write code once**: works for `Option`, `Result`, `Vec`, `Future`, `IO`, ...
- **Foundation of functional programming abstractions**

Type inference becomes undecidable in general. Languages with HKT require explicit annotations. Rust deliberately avoids full HKT (using GATs as a workaround for some cases).

Rust doesn't have HKT. Scala 3 does:

```scala
// Scala 3: F[_] is a type constructor (kind: Type -> Type)
trait Functor[F[_]]:
  def map[A, B](fa: F[A])(f: A => B): F[B]

// Implement for List
given Functor[List] with
  def map[A, B](fa: List[A])(f: A => B): List[B] = fa.map(f)

// Implement for Option
given Functor[Option] with
  def map[A, B](fa: Option[A])(f: A => B): Option[B] = fa.map(f)

// Now we can write generic code over ANY functor
def double[F[_]: Functor](fa: F[Int]): F[Int] =
  summon[Functor[F]].map(fa)(_ * 2)

double(List(1, 2, 3))              // List(2, 4, 6)
double(Option(5))                  // Some(10)
double(Option.empty[Int])          // None

// Monad builds on Functor
trait Monad[M[_]] extends Functor[M]:
  def pure[A](a: A): M[A]
  def flatMap[A, B](ma: M[A])(f: A => M[B]): M[B]

  // map can be derived from flatMap
  def map[A, B](fa: M[A])(f: A => B): M[B] =
    flatMap(fa)(a => pure(f(a)))
```

HKT is standard in Haskell, Scala, and PureScript. Rust avoids full HKT but added GATs (Generic Associated Types) as a partial workaround. If your language doesn't support HKT, don't fight it. Three similar functions are fine if they're short.

---

## Linear and Affine Types

Resources must be managed: files closed, memory freed, locks released. Forget to close a file? Leak. Close it twice? Crash. Use it after closing? Undefined behavior.

Garbage collectors handle memory but not files, sockets, or locks. Manual management is error-prone—Microsoft reports that 70% of their security vulnerabilities are memory safety issues, and use-after-free remains a top exploit vector. Can the type system track resource usage?

Most type systems only track *what* a value is. Linear types also track *how many times* it's used. This is the **substructural** family, named because they restrict the structural rules of logic (weakening, contraction, exchange):

| Type | Rule | Structural Rule Restricted | Use Case |
|------|------|---------------------------|----------|
| Unrestricted | Any number of times | None | Normal values |
| Affine | At most once | Contraction (no duplication) | Rust ownership, can drop unused |
| Linear | Exactly once | Contraction + Weakening | Must handle, can't forget |
| Relevant | At least once | Weakening (no discarding) | Must use, can duplicate |
| Ordered | Exactly once, in order | Contraction + Weakening + Exchange | Stack disciplines |

**Ordered types** are the most restrictive: values must be used exactly once and in LIFO order. They model stack-based resources where you can't reorder operations.

Rust uses **affine types**: values are used at most once (moved), but you can drop them without using them. True **linear types** require using values exactly once. You can't forget to handle something.

"Use" includes transferring ownership. When you pass a `String` to a function that takes it by value, you've "used" the String. It's gone from your scope. You can't use it again. The borrow checker tracks ownership and prevents use-after-move.

Borrowing (`&T` and `&mut T`) is how Rust escapes the "use once" restriction when you need it. A borrow doesn't consume the value; it temporarily lends access. The original owner keeps ownership and can use the value after the borrow ends. The borrow checker ensures borrows don't outlive the owner.

- **Memory safety without GC**: no runtime overhead, no pauses
- **Resource safety**: can't forget to close files
- **Prevent use-after-free**: type system rejects it
- **No data races**: ownership prevents shared mutable state

```rust
// Rust: Affine types (values used at most once)
fn consume(s: String) {
    println!("{}", s);
}   // s dropped here

fn main() {
    let s = String::from("hello");
    consume(s);        // s moved into consume
    // println!("{}", s);  // ERROR: value borrowed after move
}

// File handles: RAII through ownership
use std::fs::File;
use std::io::Read;

fn read_file() -> std::io::Result<String> {
    let mut file = File::open("data.txt")?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    Ok(contents)
}   // file automatically closed here (Drop trait)

// Can't use file after it's moved/dropped
// Can't forget to close (happens automatically)
// Can't close twice (Drop runs exactly once)
```

```rust
// Borrowing: temporarily use without consuming
fn print_length(s: &String) {  // borrows s
    println!("Length: {}", s.len());
}   // borrow ends, s still valid

fn main() {
    let s = String::from("hello");
    print_length(&s);  // lend s
    print_length(&s);  // can lend again
    println!("{}", s); // s still valid
}

// Mutable borrows: exclusive access
fn append_world(s: &mut String) {
    s.push_str(" world");
}

fn main() {
    let mut s = String::from("hello");
    append_world(&mut s);
    // Only ONE mutable borrow at a time (prevents data races)
}
```

The borrow checker takes practice. Some patterns (graphs, doubly-linked lists) fight against it. But once you internalize ownership thinking, most code just works.

### The Broader Family: Ownership, Regions, and Capabilities

Linear/affine types are part of a broader family of resource-tracking type systems:

| System | What It Tracks | Example |
|--------|----------------|---------|
| **Linear/Affine** | Usage count (exactly/at most once) | Move semantics |
| **Ownership** | Who owns a value | Rust's ownership model |
| **Region/Lifetime** | How long a reference is valid | Rust lifetimes (`'a`) |
| **Capability** | What permissions a value grants | Object-capability languages |

**Ownership types** make the owner explicit in the type. Rust combines ownership with affine types: the owner is responsible for cleanup, and ownership can transfer exactly once. This is more than tracking usage; it's tracking *responsibility*.

**Region types** (or **lifetime types**) track the *scope* where a reference is valid. Rust's lifetime annotations (`&'a T`) are region types: they prove references don't outlive the data they point to.

```rust
// Rust: lifetimes are region types
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

// The 'a says: the returned reference is valid as long as
// BOTH input references are valid. The compiler checks this.
```

**Capability types** encode *permissions*, not just structure. A `ReadCapability<File>` lets you read, while `WriteCapability<File>` lets you write. The type system ensures you can only perform operations you have capabilities for. This is object-capability security expressed in types.

These ideas originated in research (region inference in MLKit, capability calculus, Cyclone's safe C) but reached mainstream through Rust. Languages like Vale and Austral explore different points in this design space.

---

## Effect Systems

Does this function do I/O? Throw exceptions? Modify global state? In most languages, you can't tell from the signature. A function that *looks* pure might read from the network, crash your program, or modify a global variable.

```java
// What does this do? You have to read the implementation.
String process(String input)
```

Track what **effects** a function can perform in its type. Pure functions have no effects. `readFile` has an `IO` effect. `throw` has an `Exception` effect. A function `String -> Int` with no effects can only compute on its input. A function `String -> IO Int` might read files, hit the network, or launch missiles.

Effects propagate: call `readFile` inside your function, your function now has `IO` too. The compiler tracks this automatically.

Some systems also provide **effect handlers**: intercept an effect and provide custom behavior. Instead of performing I/O, you could log what I/O *would* happen. Instead of throwing an exception, you could collect errors. This is like dependency injection, but for effects. You write code using abstract effects, then "handle" them differently in tests versus production.

- **Effects visible in signatures**: see at a glance what a function can do
- **Purity is provable**: no-effect functions are guaranteed pure
- **Effect polymorphism**: generic over what effects are used
- **Effect handlers**: programmable control flow, algebraic effects

```koka
// Koka: Effects are part of the type

// Pure function: no effects
fun pureAdd(x: int, y: int): int
  x + y

// Function with IO and exception effects
fun readConfig(path: string): <io, exn> string
  val contents = read-text-file(path)   // io effect
  if contents.is-empty then
    throw("Config file is empty")        // exn effect
  contents

// Effect polymorphism: map preserves whatever effects f has
fun map(xs: list<a>, f: (a) -> e b): e list<b>
  match xs
    Nil -> Nil
    Cons(x, rest) -> Cons(f(x), map(rest, f))

// If f is pure, map is pure
// If f has io effect, map has io effect
```

```koka
// Effect handlers: provide custom interpretations of effects
effect ask<a>
  ctl ask(): a

fun program(): ask<int> int
  val x = ask()
  val y = ask()
  x + y

// Handle by providing values
fun main(): io ()
  // Handle 'ask' by returning 10 each time
  with handler
    ctl ask() resume(10)

  val result = program()  // 20
  println(result.show)
```

Effect systems are in Koka, Eff, Frank, and Unison. Haskell uses monads as a workaround. Most mainstream languages don't have them, so you can use discipline instead: pure functions in the core, effects at the edges.

---

## Refinement Types

Your function divides two numbers. The divisor can't be zero. You add a runtime check:

```rust
fn divide(x: i32, y: i32) -> i32 {
    if y == 0 { panic!("division by zero"); }
    x / y
}
```

But the caller might *know* y is non-zero because it's from a non-empty list length. You're checking unnecessarily. And what if you forget the check somewhere?

Attach logical predicates to types. Instead of `Int`, write `{x: Int | x > 0}`. A refinement type is a base type plus a predicate that values must satisfy.

This is a sweet spot between regular types and full dependent types. Regular types distinguish "integer" from "string" but can't distinguish "positive integer" from "negative integer." Dependent types can express almost anything but require proofs. Refinement types let you express common properties (non-null, positive, in bounds) and use automated solvers to verify them.

The compiler uses an **SMT solver** (Satisfiability Modulo Theories) to verify predicates at compile time. SMT solvers are automated theorem provers that can handle arithmetic, bit vectors, arrays, and more. When you write `divide(x, y)` where `y` must be positive, the solver checks whether `y > 0` is provable from the context. If `y` came from a list length, and lists are non-empty, the solver can prove this automatically.

Division by zero becomes a *type error*, caught before running. Buffer overflows too. Array index out of bounds. Integer overflow. These become compile-time checks when you add the right refinements.

- **Prove properties at compile time**: non-zero, positive, in bounds
- **Eliminate runtime checks**: when the compiler can prove safety
- **Catch errors earlier**: type checker finds the bug, not production
- **Lightweight verification**: more than types, less than full proofs

```fstar
// F*: Refinement types with dependent types

// Natural numbers: ints >= 0
type nat = x:int{x >= 0}

// Positive numbers: ints > 0
type pos = x:int{x > 0}

// Division requires positive divisor (not just non-zero!)
val divide : int -> pos -> int
let divide x y = x / y

// This compiles: 5 is provably positive
let result = divide 10 5

// This FAILS at compile time:
// let bad = divide 10 0
// Error: expected pos, got int literal 0

// This also fails without more info:
// let risky (y: int) = divide 10 y
// Error: can't prove y > 0
```

```fstar
// Vectors with length in the type (simple dependent types)
val head : #a:Type -> l:list a{length l > 0} -> a
let head #a l = List.hd l

// This compiles:
let first = head [1; 2; 3]

// This fails:
// let bad = head []
// Error: can't prove length [] > 0

// Safe indexing: index must be less than length
val nth : #a:Type -> l:list a -> i:nat{i < length l} -> a

// The refinement i < length l guarantees bounds safety
```

The SMT solver can fail or timeout on complex predicates. When it works, it's like magic. When it doesn't, you're debugging why the solver can't prove something you know is true. F*, Dafny, Liquid Haskell, and Ada/SPARK all use this approach.

### When Refinement Types Aren't Enough

Refinement types work well for predicates on values: `{x: Int | x > 0}`, bounds checks, non-nullity, arithmetic constraints. SMT solvers handle these automatically. But they hit walls.

The first wall is type-level computation. You want `printf "%d + %d = %d"` to have type `Int -> Int -> Int -> String`. The format string determines the type. This isn't a predicate on a value—it's computing a type from a value. Refinement types can't express this.

The second wall is state. Session types need types that change based on what operations you've performed. Refinement types constrain values but can't express "after calling `open()`, the handle is in state Open." For this you need dependent types or linear types.

The third wall is induction. SMT solvers are decision procedures for specific theories—linear arithmetic, bit vectors, arrays. They don't do induction. Refinement types can say "this list has length > 0" but struggle with "this vector has length n + m." You can write `{v: Vec | len(v) = len(a) + len(b)}`, and for simple cases SMT solvers can verify it. But proving it across recursive calls—showing each step preserves the invariant—requires induction the solver can't do.

F* sits on the boundary—it has both refinement types (SMT-backed) and full dependent types (proof-backed). You start with refinements and escalate to manual proofs when the solver fails. This is a reasonable mental model: refinement types are dependent types where an automated prover handles the easy cases. If an SMT solver can verify your property in a few seconds, refinement types work. If you need type computation, state tracking, or induction, you've crossed into dependent type territory.

---

# Tier 4: Research Level

These concepts are primarily found in research languages and proof assistants. They provide the strongest guarantees but require significant expertise. Understanding them helps even if you never use them directly.

## Dependent Types

You want a function that appends two vectors. The result should have length `n + m`. With regular types, you can express "returns a vector" but not "returns a vector whose length is the sum of the inputs."

```rust
// Regular types: can't express the length relationship
fn append<T>(a: Vec<T>, b: Vec<T>) -> Vec<T>
```

Refinement types help with predicates, but what if types could *compute*?

Types can depend on values. `Vector<3, Int>` (a vector of 3 integers) is a different type than `Vector<5, Int>`. These aren't the same type with the same length checked at runtime. They're *different types*. A function expecting a 3-element vector won't accept a 5-element vector, just like a function expecting a String won't accept an Int.

Function types can express relationships between inputs and outputs:

```text
append : Vector<n, a> -> Vector<m, a> -> Vector<n + m, a>
```

The return type *computes* from the input types. If you append a 3-element vector to a 5-element vector, you get an 8-element vector. The `n + m` is evaluated at the type level. Types and terms live in the same world.

This is the Curry-Howard correspondence in full force. Types are propositions. Programs are proofs. `Vector<n, a>` is a proposition: "there exists a vector of n elements of type a." Constructing such a vector proves the proposition. A function type `Vector<n, a> -> Vector<n, a>` is an implication: "if you give me a proof of n-vector, I'll give you back a proof of n-vector."

The payoff: matrix multiplication that's dimensionally checked at compile time. `Matrix<n, m> × Matrix<m, p> → Matrix<n, p>`. If dimensions don't match, the code doesn't compile.

- **Type checking requires evaluation**: undecidable in general
- **Termination checking required**: non-terminating functions break type checking
- **Proving is different from programming**: you need to think about why code is correct, not just that it works
- **Verbose proofs**: sometimes more proof code than actual code

```idris
-- Idris 2: Dependent types

-- Vector indexed by its length
data Vect : Nat -> Type -> Type where
    Nil  : Vect 0 a
    (::) : a -> Vect n a -> Vect (S n) a

-- head: ONLY works on non-empty vectors
-- Not a runtime check. The TYPE prevents calling on empty.
head : Vect (S n) a -> a
head (x :: xs) = x

-- No case for Nil needed! Vect (S n) can't be Nil.
-- The S n pattern means "at least 1"

-- append: the type PROVES lengths add
append : Vect n a -> Vect m a -> Vect (n + m) a
append Nil       ys = ys
append (x :: xs) ys = x :: append xs ys

-- Type-safe matrix multiplication
Matrix : Nat -> Nat -> Type -> Type
Matrix rows cols a = Vect rows (Vect cols a)

-- Dimensions must match, checked at COMPILE TIME
matMul : Num a => Matrix n m a -> Matrix m p a -> Matrix n p a

-- This won't compile:
-- matMul (2x3 matrix) (5x2 matrix)
-- Error: expected Matrix 3 p, got Matrix 5 2
```

```idris
-- Type-safe printf!
-- The format string determines the function's type

printf : (fmt : String) -> PrintfType fmt

-- printf "%s is %d years old"
-- has type: String -> Int -> String

-- printf "%d + %d = %d"
-- has type: Int -> Int -> Int -> String

-- Wrong number/type of arguments = compile error
```

Dependent types are in Idris 2, Agda, Coq, Lean 4, and F*. For most application code, they're overkill. [Refinement types](#refinement-types) or [phantom types](#phantom-types) often suffice.

---

## Communication and Protocol Typing

Concurrency introduces problems that go beyond sequential code. Functions have types, but what about *interactions*? Type systems for communication ensure that distributed components agree on protocols, preventing deadlocks and message mismatches at compile time.

### Why Concurrency Needs Types Beyond Functions

In sequential code, a function type `A -> B` tells you everything: give an `A`, get a `B`. But concurrent systems have:

- **Ordering constraints**: Must send request before receiving response
- **Protocol states**: What you can do depends on what happened before
- **Multiple parties**: Client, server, and maybe others must agree
- **Failure modes**: Deadlock, livelock, message type mismatch

Regular function types can't express "after you send X, you must receive Y before sending Z." Protocol violations compile fine but fail at runtime.

### Session Types

**Session types** encode communication protocols in channel types. The channel's type *changes* as you use it, tracking protocol state.

Distributed systems communicate over channels. Client sends `Request`, server responds with `Response`. But what if the client sends two requests without waiting? Or expects a response that never comes? Protocol violations cause deadlocks or silent failures, discovered only in production.

Session types fix this by making channels typed state machines. Start with `!Request.?Response.End`. After sending a request, you have `?Response.End`. After receiving the response, you have `End`. Each operation transforms the type. Using the wrong operation is a type error.

Key concept: **duality**. The client's view is the *dual* of the server's view: sends become receives and vice versa. If the client has `!Request.?Response.End`, the server has `?Request.!Response.End`. The types are symmetric. This ensures both sides agree on the protocol, verified at compile time. Well-typed programs can't deadlock.

```text
// Session types: Types encode protocols

// Notation:
// !T  = send value of type T
// ?T  = receive value of type T
// .   = sequencing
// End = session finished

// Client's protocol view
type BuyerProtocol =
    !String.       // send book title
    ?Price.        // receive price
    !Bool.         // send accept/reject
    End

// Server's view: the DUAL (swap ! and ?)
type SellerProtocol =
    ?String.       // receive title
    !Price.        // send price
    ?Bool.         // receive decision
    End

// Implementation (pseudocode)
buyer(channel: BuyerProtocol) {
    send(channel, "Types and Programming Languages");
    // channel now has type ?Price.!Bool.End

    let price = receive(channel);
    // channel now has type !Bool.End

    send(channel, price < 100);
    // channel now has type End

    close(channel);
}

// Multiparty session: Three-way protocol
global protocol Purchase(Buyer, Seller, Shipper) {
    item(String) from Buyer to Seller;
    price(Int) from Seller to Buyer;

    choice at Buyer {
        accept:
            payment(Int) from Buyer to Seller;
            address(String) from Buyer to Shipper;
            delivery(Date) from Shipper to Buyer;
        reject:
            cancel() from Buyer to Seller;
            cancel() from Buyer to Shipper;
    }
}
```

Session types are mostly in research: Links, Scribble, and various academic implementations. Few production systems use them directly, but the ideas influence API design.

### Actor Message Typing

**Actor systems** (Erlang, Akka, Orleans) use message passing instead of shared memory. Each actor has a mailbox and processes messages sequentially. But what messages can an actor receive?

Without typing, any message can be sent to any actor. Typos in message names, wrong payload types, or protocol violations surface only at runtime.

**Typed actors** constrain what messages an actor can receive:

```scala
// Akka Typed: Actor's message type is explicit
object Counter {
  sealed trait Command
  case class Increment(replyTo: ActorRef[Int]) extends Command
  case class GetValue(replyTo: ActorRef[Int]) extends Command
}

// The actor can ONLY receive Counter.Command messages
def counter(value: Int): Behavior[Counter.Command] =
  Behaviors.receive { (context, message) =>
    message match {
      case Increment(replyTo) =>
        replyTo ! (value + 1)
        counter(value + 1)
      case GetValue(replyTo) =>
        replyTo ! value
        Behaviors.same
    }
  }

// Sending wrong message type = compile error
// counterRef ! "hello"  // ERROR: String is not Counter.Command
```

```erlang
%% Erlang: Dialyzer can check message types via specs
-spec loop(state()) -> no_return().
loop(State) ->
    receive
        {increment, From} ->
            From ! {ok, State + 1},
            loop(State + 1);
        {get, From} ->
            From ! {ok, State},
            loop(State)
    end.
```

### Comparing Approaches

| Approach | What's Typed | Guarantees | Examples |
|----------|-------------|------------|----------|
| **Untyped channels** | Nothing | None | Raw sockets, most languages |
| **Typed messages** | Message payload types | No wrong payloads | Go channels, Rust mpsc |
| **Actor behavior types** | What actor accepts | No invalid messages | Akka Typed, Pony |
| **Session types** | Protocol state machine | No protocol violations | Links, research |
| **Multiparty session** | N-party protocols | Global protocol safety | Scribble, research |

### Practical Adoption

Rust's `Send` and `Sync` traits are a lightweight form of concurrency typing: they mark which types can safely cross thread boundaries. This isn't protocol typing, but it prevents data races at compile time.

Go's typed channels (`chan int`, `chan Message`) ensure payload types match but don't track protocol state.

Full session types remain mostly academic, but the ideas are seeping into practice. TypeScript's discriminated unions with exhaustive matching approximate protocol states. Rust's typestate pattern uses the type system to enforce valid sequences of operations.

---

## Quantitative Type Theory (QTT)

Linear types track usage (use exactly once). Dependent types need to inspect values at the type level. But inspecting a value for typing shouldn't count as "using" it at runtime!

```idris
-- We want the length n to be:
-- - Available at compile time (for type checking)
-- - Erased at runtime (zero cost)
data Vect : Nat -> Type -> Type
```

How do you combine linear/affine types with dependent types cleanly?

Annotate each variable with a **quantity** from a semiring:
- **0**: compile-time only (erased at runtime)
- **1**: exactly once (linear)
- **ω**: unlimited

The key problem this solves: in dependent types, type-checking might *use* a value to determine a type, but that "use" shouldn't count at runtime. The length `n` in `Vect n a` is used at the type level to ensure vectors have the right size. But at runtime, you don't want to pass `n` around. It should be erased.

With QTT, you write `(0 n : Nat)` to say "n exists for type-checking but has zero runtime representation." The `0` quantity means "used zero times at runtime." The type checker uses it. The compiled code doesn't include it.

This also cleanly handles linear resources. A file handle has quantity 1: use it exactly once. A normal integer has quantity ω: use it as many times as you want. The quantities form a semiring, which makes them compose correctly when you combine functions.

```idris
-- Idris 2 uses QTT natively

-- The 'n' has quantity 0: erased at runtime!
data Vect : (0 n : Nat) -> Type -> Type where
    Nil  : Vect 0 a
    (::) : a -> Vect n a -> Vect (S n) a

-- n is available for type checking but has zero runtime cost

-- Linear function: use x exactly once
dup : (1 x : a) -> (a, a)  -- ERROR: can't use x twice!

-- Valid linear function
consume : (1 x : File) -> IO ()

-- Unrestricted
normal : (x : Int) -> Int
normal x = x + x  -- Fine, x is unrestricted (quantity ω)

-- Mixing: erased type, linear value
id : (0 a : Type) -> (1 x : a) -> a
id _ x = x
-- a exists only at compile time
-- x is used exactly once at runtime
```

Idris 2 uses QTT. Granule is a research language exploring graded types more generally.

---

## Cubical Type Theory

Homotopy Type Theory (HoTT) introduced revolutionary ideas: types as spaces, equality as paths. The **univalence axiom** says equivalent types are equal. But it was just an axiom that didn't compute. Asking "are these two proofs of equality the same?" got no answer.

Make equality *computational*. In standard type theory, you can prove two things are equal, but you can't always *compute* with that equality. Univalence (equivalent types are equal) was an axiom: you could assert it, but it didn't reduce to anything. Asking "is this proof of equality the same as that one?" might not give an answer.

Cubical type theory fixes this by taking homotopy seriously. A proof of equality `a = b` is literally a path from `a` to `b`. Formally, it's a function from the interval type `I` (representing [0,1]) to the type, where the function maps 0 to `a` and 1 to `b`. You can walk along the path. You can reverse it (symmetry). You can concatenate paths (transitivity).

This geometric intuition makes equality computational. Univalence becomes a theorem: given an equivalence between types, you can construct a path between them. And crucially, transporting values along this path actually *applies* the equivalence. Everything reduces. Everything computes. You also get functional extensionality (functions equal if they agree on all inputs) and higher inductive types (quotients, circles, spheres as types) for free.

```agda
-- Cubical Agda

{-# OPTIONS --cubical #-}

open import Cubical.Core.Everything

-- I is the interval type: points from 0 to 1
-- A path from a to b is a function I → A
-- where i0 ↦ a and i1 ↦ b

-- Reflexivity: constant path
refl : ∀ {A : Type} {a : A} → a ≡ a
refl {a = a} = λ i → a  -- For all points, return a

-- Symmetry: reverse the path
sym : ∀ {A : Type} {a b : A} → a ≡ b → b ≡ a
sym p = λ i → p (~ i)   -- ~ negates interval points

-- Function extensionality: just works!
-- If f x ≡ g x for all x, then f ≡ g
funExt : ∀ {A B : Type} {f g : A → B}
       → (∀ x → f x ≡ g x)
       → f ≡ g
funExt p = λ i x → p x i

-- Univalence: equivalences give paths between types
ua : ∀ {A B : Type} → A ≃ B → A ≡ B

-- And this COMPUTES: transporting along ua
-- actually applies the equivalence!
```

Cubical Agda, redtt, cooltt, and Arend implement cubical type theory. Unless you're doing research in type theory or formalizing mathematics, you won't need this.

---

## Separation Logic Types

You're writing code with pointers. How do you know two pointers don't alias? That modifying `*x` won't affect `*y`? In C, you don't. It's undefined behavior waiting to happen.

```c
void swap(int *x, int *y) {
    int tmp = *x;
    *x = *y;
    *y = tmp;
}
// What if x == y? This breaks!
```

Reason about **ownership of heap regions**. The key operator is **separating conjunction** (`*`): `P * Q` means "P holds for some heap region, Q holds for a *separate* region." If you prove you own separate regions, they can't alias.

Classical logic has conjunction (∧): "P and Q are both true." Separation logic adds a new conjunction (*): "P holds for part of memory, Q holds for a *different* part of memory, and these parts don't overlap." This is the missing piece for reasoning about pointers.

When you write `{x ↦ 5 * y ↦ 10}`, you're asserting: x points to 5, y points to 10, *and x and y are different locations*. The separating conjunction makes non-aliasing explicit. Without it, modifying `*x` might affect `*y`. With it, you know they're independent.

The **frame rule** makes proofs modular. If you prove `{P} code {Q}` (running code in state P yields state Q), then `{P * R} code {Q * R}` for any R. Whatever R describes is *framed out*, untouched by code. You can reason about each piece of memory independently.

Rust's borrow checker embodies these ideas. Mutable borrows are exclusive ownership of a memory region. The guarantee that you can't have two `&mut` to the same location is the separating conjunction at work. Concurrent separation logic extends this to reason about shared-memory concurrency.

```text
// Separation logic specifications (pseudocode)

// Points-to assertion: x points to value v
x ↦ v

// Separating conjunction: DISJOINT ownership
// x ↦ a * y ↦ b means x and y are different locations
{x ↦ a * y ↦ b}    // precondition: x points to a, y points to b, SEPARATELY
swap(x, y)
{x ↦ b * y ↦ a}    // postcondition: values swapped

// The * GUARANTEES x ≠ y
// Without separation: swap(p, p) would break!

// Frame rule: what you don't touch, stays the same
// If: {P} code {Q}
// Then: {P * R} code {Q * R}
// R is "framed out", untouched by code

// Linked list segment from head to tail
lseg(head, tail) =
    (head = tail ∧ emp)                            // empty segment
  ∨ (∃v, next. head ↦ (v, next) * lseg(next, tail)) // node + rest
```

```rust
// Rust's borrow checker encodes similar ideas
fn swap(x: &mut i32, y: &mut i32) {
    // Rust GUARANTEES x and y don't alias
    // Can't have two &mut to the same location!
    let tmp = *x;
    *x = *y;
    *y = tmp;
}

// This won't compile:
// let mut n = 5;
// swap(&mut n, &mut n);  // Error: can't borrow n mutably twice
```

You get separation logic ideas implicitly through Rust's borrow checker. For explicit proofs, tools like Iris (Coq), Viper, and VeriFast let you verify pointer-manipulating code.

---

## Sized Types

Dependent type systems need to know all functions terminate. Otherwise type checking could loop forever. Typically they require **structural recursion**: arguments must get smaller in a syntactic sense.

But this rejects valid programs:

```text
merge : Stream → Stream → Stream
merge (x:xs) (y:ys) = x : y : merge xs ys
```

Neither `xs` nor `ys` is structurally smaller than both original arguments!

Track *sizes* abstractly in types. A `Stream<i>` has "size" `i`. Operations might not be syntactically smaller but are *semantically* smaller in size. The type checker tracks sizes symbolically.

The problem is termination checking. Dependent type checkers must ensure all functions terminate, otherwise type-checking could loop forever. Simple structural recursion ("the argument gets smaller") works for many cases but rejects valid programs.

Consider merging two streams. At each step, you take one element from each stream. Neither stream is "structurally smaller" than both inputs. But semantically, you're making progress: you're consuming both streams. Sized types capture this. Each stream has an abstract size. After taking an element, the remaining stream has a smaller size. The type checker sees sizes decreasing and accepts the function.

For coinductive data (infinite structures like streams), you need **productivity checking**: you must produce output in finite time. Sized types handle this too. The output stream's size depends on the input sizes in a way that guarantees you always make progress.

```agda
{-# OPTIONS --sized-types #-}

open import Size

-- Stream indexed by size
data Stream (i : Size) (A : Set) : Set where
  _∷_ : A → Thunk (Stream i) A → Stream (↑ i) A

-- ↑ i means "larger than i"
-- Thunk delays evaluation (coinduction)

-- take: consume part of a sized stream
take : ∀ {i A} → Nat → Stream i A → List A
take zero    _        = []
take (suc n) (x ∷ xs) = x ∷ take n (force xs)

-- map preserves size
map : ∀ {i A B} → (A → B) → Stream i A → Stream i B
map f (x ∷ xs) = f x ∷ λ where .force → map f (force xs)

-- merge: interleave two streams
-- Both streams get "used", sizes track this correctly
zipWith : ∀ {i A B C} → (A → B → C) → Stream i A → Stream i B → Stream i C
zipWith f (x ∷ xs) (y ∷ ys) =
  f x y ∷ λ where .force → zipWith f (force xs) (force ys)

-- Without sized types, the termination checker might reject these
-- because it can't see that streams are being consumed productively
```

Agda supports sized types. They're useful when the termination checker is too strict, particularly for coinductive definitions.

---

## Pure Type Systems

There are many typed lambda calculi: simply typed, System F, System Fω, the Calculus of Constructions, Martin-Löf type theory. Each has its own rules for what can depend on what. Is there a unified framework?

**Pure Type Systems** (PTS) provide a single parameterized framework that encompasses most typed lambda calculi. A PTS is defined by three sets:

- **Sorts** (S): The "types of types." Typically `*` (the type of ordinary types) and `□` (the type of `*` itself)
- **Axioms** (A): Which sorts have which sorts as their type (e.g., `* : □`)
- **Rules** (R): Triples `(s₁, s₂, s₃)` specifying that functions from `s₁` to `s₂` live in `s₃`

By varying these parameters, you recover different type systems:

| System | Rules | What It Expresses |
|--------|-------|-------------------|
| Simply Typed λ-calculus | `(*, *, *)` | Terms depending on terms |
| System F | `(*, *, *)`, `(□, *, *)` | Types depending on types (polymorphism) |
| System Fω | `(*, *, *)`, `(□, *, *)`, `(□, □, □)` | Higher-kinded types |
| λP (LF) | `(*, *, *)`, `(*, □, □)` | Types depending on terms (dependent types) |
| Calculus of Constructions | All four combinations | Full dependent types + polymorphism |

The **Lambda Cube** visualizes this: three axes representing term-to-term, type-to-type, and term-to-type abstraction. Each corner is a different type system.

```text
                    λC (CoC)
                   /|
                  / |
                 /  |
               λPω  λP2
               /|   /|
              / |  / |
             /  | /  |
           λω   λP   System F
            |   |   /
            |   |  /
            |   | /
            λ→ (Simply Typed)
```

### Why It Matters

PTS provides:

- **Unified theory**: Understand all these systems as instances of one framework
- **Metatheoretic results**: Prove properties (normalization, type preservation) once, apply everywhere
- **Design guidance**: When designing a type system, you're choosing a point in this space
- **Implementation reuse**: Type checkers can be parameterized by PTS specification

The Calculus of Constructions (top corner) is the basis for Coq. Martin-Löf Type Theory (related but distinct) underlies Agda. Understanding PTS clarifies what dependent types *are*: the ability to form types that depend on terms, placed on equal footing with other forms of abstraction.

### Connection to Practice

When you write `Vector<n, T>` in a dependently typed language, you're using term-to-type dependency: the type `Vector` depends on the term `n`. This is the λP axis of the Lambda Cube. When you write `forall T. T -> T`, you're using type-to-term polymorphism: the System F corner.

Modern dependently typed languages live near the CoC corner, with various additions (universes, inductive types, effects) that go beyond the pure PTS framework but are still understood through it.

### Further Reading

- "Lambda Calculi with Types" by Henk Barendregt (the definitive reference)
- "Type Theory and Formal Proof" by Rob Nederpelt and Herman Geuvers

---

# Tier 5: Cutting Edge Research

These concepts are at the research frontier. They haven't reached mainstream languages yet, but they influence future designs. Brief coverage for completeness:

| Concept | What It Explores | Why It Matters |
|---------|------------------|----------------|
| **Graded Modal Types** | Unify effects + linearity in one framework | Single system for many features |
| **Call-by-Push-Value** | Unify call-by-name and call-by-value | Cleaner operational semantics |
| **Polarized Types** | Positive (data) vs. negative (codata) types | Better duality understanding |
| **Ornaments** | Systematically derive related types | Auto-generate `List` from `Nat` |
| **Type-Level Generic Programming** | Reflect on type structure | Auto-derive instances |
| **Logical Relations** | Prove program equivalence | Foundation for verification |
| **Realizability** | Extract programs from proofs | Programs from math automatically |
| **Observational Type Theory** | Equality without axioms | Computation + extensionality |
| **Two-Level Type Theory** | Separate meta from object level | Clean staging/metaprogramming |
| **Multimodal Type Theory** | Multiple modalities (necessity, etc.) | Generalize many features |

### Graded Modal Types (Brief Example)

```granule
-- Granule: grades unify linearity and effects

id : forall {a : Type} . a [1] -> a   -- use exactly once
id [x] = x

dup : forall {a : Type} . a [2] -> (a, a)  -- use exactly twice
dup [x] = (x, x)

-- Grades form a semiring, combining naturally
-- One system handles linearity, privacy, information flow...
```

---

# Practical Concepts

A few concepts that don't fit the tier structure but are practically important:

## Variance

When `Dog <: Animal`, what's the relationship between `Container<Dog>` and `Container<Animal>`? It depends on how the container uses its type parameter.

This question matters for every generic type. You might expect `Container<Dog>` to be a subtype of `Container<Animal>` always. But that's wrong in general, and understanding why is key to writing correct generic code.

The intuition: if you can only *get* values out of a container (produce), then `Container<Dog>` can substitute for `Container<Animal>`. You asked for animals, I give you dogs, dogs are animals, everyone's happy. But if you can *put* values into a container (consume), it's the reverse. A container that accepts any animal can accept dogs. But a container that only accepts dogs can't substitute for one that accepts any animal, because someone might try to put a cat in it.

Mutable containers are the problem case. You can both get and put. Neither subtyping direction is safe. `Container<Dog>` must be invariant: no subtyping relationship with `Container<Animal>`.

```typescript
// TypeScript: variance annotations

// Covariant (out): Container<Dog> <: Container<Animal>
// "Producers" are covariant
interface Producer<out T> {
    produce(): T;
}
// If it produces Dogs, it produces Animals

// Contravariant (in): Container<Animal> <: Container<Dog>
// "Consumers" are contravariant
interface Consumer<in T> {
    consume(x: T): void;
}
// If it eats any Animal, it can eat Dogs

// Invariant: no subtyping relationship
// Mutable containers must be invariant
interface MutableBox<T> {
    get(): T;       // covariant use
    set(x: T): void; // contravariant use
}
// Both uses = invariant
```

---

## Phantom Types

Type parameters that appear in the type but not in the data. Used for compile-time distinctions.

At first, this sounds pointless. Why have a type parameter that doesn't affect the data? The answer: to carry information at the type level that the compiler checks, even though the runtime doesn't need it.

Consider a `UserId` and a `ProductId`. Both are just integers at runtime. But mixing them up is a bug. With phantom types, `Id<User>` and `Id<Product>` are different types, even though both hold a single integer. The phantom parameter (`User` or `Product`) exists only for the type checker. Zero runtime cost. Full compile-time safety.

The Mars Climate Orbiter (1999) was lost because one team used metric units while another used imperial—$327 million burned up in the Martian atmosphere. Phantom types turn unit mismatches into compile errors: `Distance<Meters>` and `Distance<Feet>` can't be mixed.

```rust
use std::marker::PhantomData;

// Unit types (no data, just type-level tags)
struct Meters;
struct Feet;

// Distance carries a unit, but only at type level
struct Distance<Unit> {
    value: f64,
    _unit: PhantomData<Unit>,  // zero runtime cost
}

impl<U> Distance<U> {
    fn new(value: f64) -> Self {
        Distance { value, _unit: PhantomData }
    }
}

// Can only add distances with the same unit
fn add<U>(a: Distance<U>, b: Distance<U>) -> Distance<U> {
    Distance::new(a.value + b.value)
}

let meters: Distance<Meters> = Distance::new(100.0);
let feet: Distance<Feet> = Distance::new(50.0);

// add(meters, feet);  // ERROR: expected Meters, got Feet
add(meters, Distance::new(50.0));  // OK: both Meters
```

---

## Row Polymorphism

Functions that work on records with "at least these fields," preserving other fields.

Regular generics abstract over types. Row polymorphism abstracts over *record structure*. A function `getName` needs records with a `name` field. It shouldn't care about other fields. Row polymorphism lets you write this: "give me any record with at least a `name: String` field, and I'll return the name."

Extra fields pass through unchanged. If you have `{ name: "Ada", age: 36, title: "Countess" }` and call `getName`, you get "Ada" back. The function ignores `age` and `title`, but doesn't require you to strip them first. More flexible than structural subtyping because it's parametric: works uniformly for any extra fields.

This is common in functional languages with records (PureScript, Elm, OCaml) and solves the problem of writing functions that operate on "records with certain fields" without committing to a specific record type.

```purescript
-- PureScript: Row polymorphism

-- Works on ANY record with a name field
-- The | r means "and possibly other fields"
getName :: forall r. { name :: String | r } -> String
getName rec = rec.name

-- Preserves extra fields!
getName { name: "Ada", age: 36 }             -- "Ada"
getName { name: "Alan", email: "a@b.c" }     -- "Alan"

-- Can require multiple fields
greet :: forall r. { name :: String, title :: String | r } -> String
greet rec = rec.title <> " " <> rec.name

greet { name: "Lovelace", title: "Countess", birth: 1815 }
-- "Countess Lovelace"
-- The 'birth' field passes through, ignored but preserved
```

---

# Languages Compared

Rather than ranking languages linearly, this section maps popular languages across the taxonomy axes. Real languages are bundles of trade-offs.

## Comparison Tables

### Core Type System

| Language | Checking | Discipline | Polymorphism |
|----------|----------|------------|--------------|
| **Rust** | Static | Nominal | Parametric + traits |
| **Haskell** | Static | Nominal | Parametric + typeclasses |
| **OCaml** | Static | Nominal + structural | Parametric + modules |
| **Scala** | Static | Nominal | Parametric + implicits |
| **TypeScript** | Gradual | Structural | Parametric + unions |
| **Python** | Dynamic | Nominal + protocols | Runtime ad-hoc |
| **Java** | Static | Nominal | Parametric (erased) |
| **C#** | Static | Nominal | Parametric |
| **Go** | Static | Structural | Parametric + interfaces |
| **C++** | Static | Nominal | Templates |
| **Lean/Coq** | Static | Dependent | Full dependent |

### Advanced Features

| Language | Inference | Linearity | Effects | Soundness |
|----------|-----------|-----------|---------|-----------|
| **Rust** | Bidirectional | Affine + lifetimes | Via types | Sound |
| **Haskell** | HM extended | Optional linear | Monads | Mostly sound |
| **OCaml** | HM | None | Algebraic | Sound |
| **Scala** | Bidirectional | None | Library | Edges unsound |
| **TypeScript** | Constraint | None | None | Unsound* |
| **Python** | Minimal | None | None | Unsound |
| **Java** | Local | None | None | Mostly sound |
| **C#** | Local | None | None | Sound |
| **Go** | Local | None | None | Sound |
| **C++** | Minimal | Manual/move | None | Easy to break |
| **Lean/Coq** | Bidirectional | None | Pure | Sound |

*TypeScript is intentionally unsound for pragmatic reasons.

## Language Profiles

### Rust

**Core identity**: Ownership and affine typing for systems safety.

Rust's type system is built around *resource management*. Affine types (values used at most once) combine with the borrow checker to eliminate use-after-free, data races, and resource leaks at compile time. Lifetimes are region types that prove references don't outlive their referents.

Trade-offs: No garbage collector means some patterns (cyclic structures) require workarounds. Expect to fight the borrow checker for a few weeks before it clicks. But for systems code, the safety guarantees are unmatched outside research languages.

**Best for**: Systems programming, performance-critical applications, anywhere memory safety matters.

---

### Haskell

**Core identity**: Parametric polymorphism plus effect encoding.

Haskell pioneered typeclasses (ad-hoc polymorphism without inheritance) and proved that effect tracking via monads works at scale. The type system supports higher-kinded types, GADTs, type families, and with extensions, approaches dependent types.

Trade-offs: Complexity accumulates. Extensions interact in surprising ways. Lazy evaluation complicates reasoning about performance. Productive Haskell requires internalizing concepts that don't transfer from imperative languages.

**Best for**: Compilers, financial systems, anywhere correctness matters more than onboarding speed.

---

### OCaml

**Core identity**: Pragmatic functional programming with sound foundations.

OCaml keeps Hindley-Milner inference simple while adding modules with structural typing. The module system enables abstraction and separate compilation. Recently added algebraic effects bring first-class effect handling.

Trade-offs: Less expressive than Haskell, fewer libraries than mainstream languages. But the simplicity is intentional: the type system stays predictable.

**Best for**: Compilers (including Rust's original), theorem provers, DSL implementation.

---

### Scala

**Core identity**: Maximum expressiveness on the JVM.

Scala pushes the boundaries of what's expressible in a statically typed language: path-dependent types, implicits for type-level computation, union and intersection types. Scala 3 cleans up the syntax while adding match types and explicit term inference.

Trade-offs: The expressiveness creates complexity. Compile times suffer. Some corners are unsound. The type system can be "too powerful" for teams that don't need it.

**Best for**: Complex domain modeling, big data (Spark), anywhere you need JVM compatibility with advanced types.

---

### TypeScript

**Core identity**: Structural gradual typing with strong flow sensitivity.

TypeScript chose structural typing to model JavaScript's duck typing, and gradual typing to enable incremental adoption. Its flow-sensitive type narrowing is among the best: the type of a variable changes based on control flow. Union types and discriminated unions bring algebraic data types to JavaScript.

Trade-offs: Intentionally unsound in several places (bivariant function parameters, type assertions). The goal is usability and tooling, not proofs. `any` is always an escape hatch.

**Best for**: Large JavaScript codebases, teams migrating from untyped to typed, frontend development.

---

### Python

**Core identity**: Runtime flexibility with optional static hints.

Python's type system is bolted on: the runtime ignores type hints entirely. Tools like mypy and pyright check them statically. This enables gradual adoption but means types are advisory, not enforced.

Trade-offs: No runtime guarantees. Type coverage varies across the ecosystem. But the flexibility is intentional: Python prioritizes "getting things done" over proving correctness.

**Best for**: Scripting, data science, rapid prototyping, anywhere development speed trumps runtime safety.

---

### Java

**Core identity**: Nominal enterprise typing with conservative evolution.

Java's generics use type erasure for backward compatibility, limiting what's expressible. The type system is nominal: explicit declarations define relationships. Evolution is slow and deliberate.

Trade-offs: Verbose. Limited inference. No value types (until Valhalla). But stability and backward compatibility matter for enterprise software. Code written in 2004 still compiles.

**Best for**: Enterprise systems, Android development, anywhere long-term stability matters.

---

### C#

**Core identity**: Pragmatic nominal typing with steady evolution.

C# evolves faster than Java, adding features like nullable reference types (flow-sensitive null tracking), pattern matching, and records. The type system is nominal but increasingly expressive.

Trade-offs: Windows-centric history (though .NET Core is cross-platform). Less expressive than Scala or Haskell. But the evolution is pragmatic: features that work in enterprise settings.

**Best for**: Windows development, game development (Unity), enterprise .NET systems.

---

### Go

**Core identity**: Structural minimalism.

Go deliberately limits the type system. Interfaces are structural (implement by having the methods), generics were added reluctantly. The philosophy: simple tools for simple problems.

Trade-offs: Lack of expressiveness means repetitive code. No sum types means error handling via multiple returns. But the simplicity aids onboarding and tooling.

**Best for**: Cloud infrastructure, CLI tools, services where simplicity aids maintenance.

---

### C++

**Core identity**: Unchecked power.

C++ templates are Turing-complete, enabling extreme metaprogramming. Move semantics approximate affine types but aren't enforced. The type system can express almost anything but guarantees almost nothing.

Trade-offs: Easy to write undefined behavior. Compile errors are notorious. But when you need zero-overhead abstraction with full control, nothing else competes.

**Best for**: Game engines, embedded systems, performance-critical code where control matters more than safety.

---

### Lean and Coq

**Core identity**: Types are proofs.

These are proof assistants first, programming languages second. Full dependent types mean types can express any mathematical proposition, and programs are proofs of those propositions. Type checking is theorem proving.

Trade-offs: Writing proofs is hard. Libraries are limited. But for verified software (CompCert, seL4), they're the gold standard.

**Best for**: Formal verification, mathematics formalization, critical systems requiring proofs.

---

## One-Sentence Summaries

| Language | Core Type System Identity |
|----------|---------------------------|
| Rust | Ownership and affine typing for memory safety |
| Haskell | Parametric polymorphism plus monadic effects |
| OCaml | Sound HM inference with structural modules |
| Scala | Maximum expressiveness on the JVM |
| TypeScript | Structural gradual typing with flow sensitivity |
| Python | Runtime flexibility with optional static hints |
| Java | Conservative nominal enterprise typing |
| C# | Pragmatic nominal typing with steady evolution |
| Go | Structural minimalism by design |
| C++ | Unchecked power via templates |
| Lean/Coq | Dependent types where programs are proofs |

---

# Synthesis

## What Makes Type Systems Hard

### Decidability

The more expressive, the harder to check automatically:

| Feature | Type Checking |
|---------|---------------|
| Simply typed | Decidable, linear time |
| Hindley-Milner | Decidable, exponential worst case |
| System F (rank-N) | Checking decidable, *inference* undecidable |
| Dependent types | Undecidable in general (needs termination checking) |

### Inference

How much can the compiler figure out without annotations?

| Feature | Inference |
|---------|-----------|
| Local types | Full |
| Generics (HM) | Full |
| GADTs | Partial (needs annotations at GADT matches) |
| Higher-rank | None (requires explicit foralls) |
| Dependent | Almost none (proving needs guidance) |

### Type Equality

When are two types "the same"?

| System | Equality |
|--------|----------|
| Simple | Syntactic: `Int = Int` |
| With aliases | Structural: `type Age = Int`, then `Age = Int` |
| Dependent | Computational: must evaluate to compare |
| HoTT | Homotopical: paths between types |

### Feature Interaction

Features often compose poorly:

- **Subtyping + inference**: makes inference much harder
- **Dependent types + effects**: need special care (effects in types)
- **Linear types + higher-order functions**: subtle ownership tracking
- **GADTs + type families**: can make inference unpredictable

---

## Practical Evidence: Do Types Actually Help?

Anecdotes claim types catch bugs. But what does the evidence say?

### Empirical Studies

| Study | Finding |
|-------|---------|
| **Hanenberg et al. (2014)** | Static types improved development time for larger tasks but not small ones |
| **Mayer et al. (2012)** | Type annotations aided code comprehension, especially for unfamiliar code |
| **Gao et al. (2017)** | ~15% of JavaScript bugs in studied projects would have been caught by TypeScript/Flow |
| **Ray et al. (2014)** | Languages with stronger type systems correlated with fewer bug-fix commits (GitHub study of 729 projects) |
| **Microsoft (2019)** | 70% of security vulnerabilities in their C/C++ code were memory safety issues (addressable by Rust-style types) |

The evidence is **mixed but generally positive**:

- Types help most for **larger codebases** and **unfamiliar code**
- Types help less for **small scripts** where overhead exceeds benefit
- **Memory safety types** (Rust) show clearest wins for security-critical code
- **Gradual adoption** (TypeScript) shows measurable bug reduction even with partial coverage

### Tooling Impact

Type systems enable tooling that untyped languages can't match:

| Capability | Enabled By | Example |
|------------|-----------|---------|
| **Accurate autocomplete** | Type information | IDE knows methods on a variable |
| **Safe refactoring** | Type checking | Rename symbol across codebase |
| **Go to definition** | Type resolution | Jump to actual implementation |
| **Inline documentation** | Type signatures | See parameter/return types |
| **Dead code detection** | Exhaustiveness | Unreachable branches flagged |
| **Compile-time errors** | Type checking | Catch mistakes before running |

Languages like TypeScript transformed JavaScript development primarily through **tooling**, not runtime safety. The types exist largely to power the IDE experience.

### Developer Experience Trade-offs

| Aspect | Stronger Types | Weaker Types |
|--------|----------------|--------------|
| **Initial velocity** | Slower (annotations, fighting checker) | Faster (just write code) |
| **Refactoring confidence** | High (compiler catches breakage) | Low (hope tests cover it) |
| **Onboarding** | Easier (types document intent) | Harder (read implementation) |
| **Compile times** | Longer (type checking is work) | Shorter or none |
| **Error messages** | Sometimes cryptic | N/A |

The sweet spot varies by project. A weekend script doesn't need Rust's borrow checker. A database engine does.

---

## Verification in Practice

Dependent types and proof assistants blur the line between programming and mathematics. How are they actually used?

### Real Verified Systems

| System | What It Proves | Language/Tool |
|--------|---------------|---------------|
| **CompCert** | C compiler preserves program semantics | Coq |
| **seL4** | Microkernel has no bugs (full functional correctness) | Isabelle/HOL |
| **HACL*** | Cryptographic library is correct and side-channel resistant | F* |
| **Everest** | Verified HTTPS stack (TLS 1.3) | F*, Dafny, Vale |
| **CertiKOS** | Concurrent OS kernel isolation | Coq |
| **Iris** | Concurrent separation logic framework | Coq |
| **Lean's mathlib** | 100,000+ mathematical theorems | Lean 4 |

These are **production systems**, not toys. CompCert is used in aerospace. seL4 runs in military helicopters. HACL* is in Firefox and Linux.

### The Verification Workflow

Writing verified code differs from normal programming:

```text
1. SPECIFICATION
   Write a formal spec of what the code should do
   (This is often harder than writing the code)

2. IMPLEMENTATION
   Write the code that implements the spec

3. PROOF
   Prove the implementation satisfies the spec
   (Interactive: you guide the prover)
   (Automated: SMT solver finds proof or fails)

4. EXTRACTION
   Generate executable code from the verified artifact
   (Coq → OCaml/Haskell, F* → C/WASM)
```

### Proof Burden

The ratio of proof code to implementation code is sobering:

| Project | Implementation | Proof | Ratio |
|---------|---------------|-------|-------|
| seL4 | ~10K lines C | ~200K lines proof | 20:1 |
| CompCert | ~20K lines C | ~100K lines Coq | 5:1 |
| Typical F* | varies | 2-10x implementation | 2-10:1 |

This is why verification is reserved for **critical infrastructure**, not business logic. But the ratio is improving as tools mature.

### Lightweight Verification

Full proofs are expensive. Lighter-weight approaches offer partial guarantees:

| Approach | What You Get | Cost |
|----------|-------------|------|
| **Refinement types** (Liquid Haskell) | Prove properties via SMT | Low annotations |
| **Property-based testing** (QuickCheck) | Find counterexamples | Write properties |
| **Fuzzing** | Find crashes/bugs | CPU time |
| **Model checking** | Explore state space | Build model |
| **Design by contract** | Runtime checks from specs | Write contracts |

Refinement types are the sweet spot for many applications: you get meaningful guarantees (array bounds, non-null, positive) without full proofs. Liquid Haskell and F* make this practical.

### When to Verify

| Verify When... | Skip Verification When... |
|----------------|---------------------------|
| Security-critical (crypto, auth) | Prototype/MVP |
| Safety-critical (medical, aerospace) | Business logic |
| High-assurance infrastructure | UI code |
| Correctness matters more than ship date | Deadline-driven |
| Bugs are catastrophically expensive | Bugs are cheap to fix |

Most code doesn't need formal verification. But for the code that does, types that can express and check proofs are invaluable.

---

## The Complexity Ranking

| Rank | Concept | Learning | Implementing | Worth It For |
|------|---------|----------|--------------|--------------|
| 1 | ADTs + Pattern Matching | Low | Low | Everyone |
| 2 | Generics | Low | Medium | Everyone |
| 3 | Traits/Typeclasses | Medium | Medium | Library authors |
| 4 | Affine Types (Rust) | Medium | Medium | Systems programmers |
| 5 | GADTs | Hard | Medium | DSL/compiler writers |
| 6 | HKT | Hard | Hard | FP enthusiasts |
| 7 | Effect Systems | Hard | Hard | Language designers |
| 8 | Refinement Types | Hard | Hard | Verified software |
| 9 | Dependent Types | Very Hard | Very Hard | Researchers, proof engineers |
| 10 | Session Types | Very Hard | Very Hard | Protocol verification |
| 11 | Cubical/HoTT | Extreme | Extreme | Mathematics, foundations |

---

## What to Learn Based on Your Goals

| Your Goal | Focus On |
|-----------|----------|
| Write better code in any language | ADTs, pattern matching, generics, traits |
| Systems programming | Affine types (learn Rust) |
| Library design | Generics, traits, associated types |
| Functional programming | HKT, typeclasses, effects |
| Build compilers/interpreters | GADTs, dependent types basics |
| Formal verification | Refinement types, dependent types |
| PL research | Everything, including HoTT |

---

## The Future

Several trends are reshaping how we think about types:

1. **Effect systems going mainstream**: Unison, Koka showing the way. Expect more languages to track effects.

2. **Refinement types in practical languages**: Lightweight verification becoming accessible.

3. **Linear types spreading**: Rust proved affine types work at scale. Others will follow.

4. **Gradual dependent types**: Getting dependent types into mainstream languages incrementally.

5. **Better tooling**: Type errors becoming clearer. IDE support improving. The UX gap is closing.

---

## Conclusion

Type systems exist on a spectrum from "helpful autocomplete" to "machine-checked mathematical proofs." Where you should be on that spectrum depends on what you're building.

For most code, Tier 1-2 concepts (ADTs, generics, traits, pattern matching) eliminate entire categories of bugs: null pointer exceptions, forgotten enum cases, type mismatches. They're available in Rust, Scala, Swift, Kotlin, and even TypeScript.

Tier 3 concepts (HKT, linear types, effects) require more investment but let you abstract over containers, track resources, and prove purity. Rust's ownership model shows that "hard" concepts can become mainstream when the tooling is right.

Tier 4+ concepts (dependent types, session types, HoTT) are mostly for researchers and specialists, but they're where tomorrow's mainstream features come from. Linear types were "research" until Rust. Effect systems might be next.

The best investment is understanding the *ideas* over the syntax. Once you grok "make illegal states unrepresentable," you'll apply it in any language. Once you understand why linear types matter, you'll appreciate Rust's borrow checker instead of fighting it.

Types are not bureaucracy. They're a design tool. Use them well.

---

## Further Reading

**Books:**
- "Types and Programming Languages" by Benjamin Pierce, the textbook
- "Software Foundations", free online, interactive proof-based introduction
- "Programming Language Foundations in Agda", dependent types for programmers

**Languages to try:**
- **Rust**: Best practical introduction to affine types
- **Haskell**: HKT, typeclasses, GADTs, the functional programming standard
- **Idris 2**: Most accessible dependent types
- **Koka**: Clean effect system design

**Papers:**
- "Propositions as Types" by Philip Wadler, covers the Curry-Howard correspondence
- "Theorems for Free" by Philip Wadler, what parametricity guarantees
- "Linear Types Can Change the World", why linearity matters
