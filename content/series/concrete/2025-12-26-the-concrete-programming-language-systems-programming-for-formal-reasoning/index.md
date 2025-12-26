+++
title = "The Concrete Programming Language: Systems Programming for Formal Reasoning"
date = "2025-12-26"
description = ""
[taxonomies]
keywords=[] 
[extra]
pinned = false
+++

There's a tension at the heart of systems programming. We want languages expressive enough to build complex systems, yet simple enough to reason about with confidence. We want performance without sacrificing safety. We want the freedom to write low-level code and the guarantees that come from formal verification.

Concrete is an attempt to resolve these tensions through commitment to a single organizing principle: **every design choice must answer the question, can a machine reason about this?**

## The Core Idea

Most languages treat verification as something bolted on after the fact. You write code, then maybe you write tests, maybe you run a linter, maybe you bring in a theorem prover for critical sections. The language itself remains agnostic about provability.

Concrete inverts this relationship. The language is *designed around* a verified core, a small kernel calculus formalized in Lean with mechanically-checked proofs of progress, preservation, linearity soundness, and effect soundness. The surface language exists only to elaborate into this kernel. If your program type-checks, it's correct by construction. 

### The Trust Boundary

Precision about what's verified matters. The kernel type system and its properties are mechanically checked in Lean. What remains trusted: the Lean proof checker itself, the elaborator (surface language to kernel), and the code generator (kernel to machine code). Verifying the elaborator and code generator is future work.

## The Compilation Pipeline

Understanding how Concrete programs become executables clarifies what guarantees you get and where:

```
Source Code (.concrete)
       ↓
   Lexer/Parser (LL(1) recursive descent)
       ↓
   Surface AST
       ↓
   Elaboration
     - Type checking
     - Linearity checking
     - Capability checking
     - Borrow/region checking
     - Defer insertion points
     - Allocator binding resolution
       ↓
   Kernel IR (core calculus)
       ↓
   Kernel Checker ← proven sound in Lean
       ↓
   Code Generation
       ↓
   Machine Code
```

The kernel checkpoint is the semantic gate. Everything before it transforms syntax; everything after it preserves meaning. The kernel checker verifies that the elaborated program satisfies linearity, capabilities, and effect constraints—properties proven sound in Lean.

## What You're Giving Up

Concrete is not a general-purpose language for every project. It's designed for code that *must* be correct: cryptographic implementations, financial systems, safety-critical software, blockchain infrastructure, anything where bugs have consequences measured in dollars or lives.

To get there, Concrete eliminates entire categories of language features:

**No garbage collection.** Memory is managed through linear types and explicit destruction. Every resource is consumed exactly once. No GC pauses, no unpredictable latency, no hidden memory pressure.

**No hidden control flow.** When you read Concrete code, what you see is what executes. There are no implicit function calls from operator overloading, no invisible destructor insertion, no exception unwinding behind your back. If a function is called, you see it. If cleanup happens, you see the `defer` statement.

**No implicit allocation.** Allocation requires the `Alloc` capability, and the caller explicitly binds which allocator to use. `grep with(Alloc)` finds every function that might touch the heap.

**No interior mutability.** All mutation flows through `&mut` references. An immutable reference `&T` actually guarantees immutability—no `Cell`, no `RefCell`, no `UnsafeCell` escape hatches in safe code. If you need a cache, pass `&mut`. If you need lazy initialization, initialize before borrowing. For advanced patterns that genuinely require interior mutability, unsafe primitives gated by the `Unsafe` capability exist, but safe code cannot accidentally acquire interior mutability.

**No reflection, no eval, no runtime metaprogramming.** All code paths are determined at compile time. This breaks certain patterns but makes verification tractable.

**No global state.** All state is passed explicitly or accessed through capabilities.

**No variable shadowing.** Each variable name is unique within its scope. This prevents a class of subtle bugs and makes code more auditable.

**No null.** Optional values use `Option<T>`. No billion-dollar mistakes.

**No undefined behavior.** Kernel semantics are fully defined and proven sound.

The result is a language that restricts what you can express in exchange for mechanical guarantees about what your code actually does.

## Capabilities: Making Effects Legible

The capability system is where Concrete's design philosophy becomes most visible. Rather than treating side effects as the default and purity as an opt-in annotation, Concrete is **pure by default**. A function without capability annotations cannot perform IO, cannot allocate, cannot mutate external state. It's a mathematical function that computes a result from its inputs, nothing more.

Purity in Concrete means no side effects and no heap allocation. Stack allocation and compile-time constants are permitted. Notably, Concrete does not guarantee termination—recursive functions may diverge. This is intentional: systems programming sometimes requires non-termination, but side effects must remain explicit.

When a function needs to perform effects, it declares exactly which ones:

```
fn read_file(path: String) with(FileRead) -> String {
    ...
}

fn process_with_network() with(FileRead, Network, Alloc) -> Result {
    ...
}
```

Capabilities propagate monotonically through the call graph. If `f` calls `g`, and `g` requires `FileRead`, then `f` must declare `FileRead` too. There's no implicit granting, no ambient authority. The compiler enforces this transitively, making all effects visible in signatures.

### The `Std` Capability

For application entry points and prototyping, Concrete provides a shorthand. The `!` suffix declares the `Std` capability:

```
fn main!() {
    println("Hello")
}
```

This desugars to `fn main() with(Std)`. The `Std` capability includes common platform effects—file operations, network, clock, environment, random, and allocation—but explicitly excludes `Unsafe`. Library code should prefer explicit capability lists; `!` is a convenience for applications.

### Security Model

Capabilities don't sandbox code—if a dependency declares `with(Network)`, it gets network access. What they provide is **auditability**. You can grep your codebase for `with(Network)` and find every function that touches the network. You can verify that your JSON parser has no capabilities at all. You can review dependency updates by diffing capability declarations.

The `Unsafe` capability surfaces all unsafe operations through the same system. There's no `unsafe` keyword; instead, unsafe operations require declaring `with(Unsafe)`, and that requirement propagates like any other capability. Your trust boundaries become grep-able.

## Linear Types: Resources as Values

All values in Concrete are linear by default. A linear value must be consumed exactly once—not zero times (that's a leak), not twice (that's a double-free). Consumption happens when you pass the value to a function that takes ownership, return it, destructure it via pattern matching, or explicitly call `destroy(x)`.

```
fn example!() {
    let f = open("data.txt")
    defer destroy(f)
    let content = read(&f)
    // destroy(f) runs here because of defer
}
```

If `f` isn't consumed on all paths, the program is rejected. If you try to use `f` after moving it, the program is rejected. This is compile-time enforcement, not runtime checking.

Some types—integers, booleans, floats—are explicitly marked `Copy` and escape linear restrictions:

```
type Copy Int
type Copy Bool
type Copy Float64
```

But the default is linearity, which forces you to think about resource ownership as you write code rather than hoping the runtime sorts it out.

### Destructors

A linear type may define a destructor that executes when `destroy(x)` is called:

```
type File {
    handle: FileHandle
}

destroy File with(FileClose) {
    platform_close(self.handle)
}
```

The destructor takes ownership of `self`, may require capabilities, and runs exactly once when explicitly invoked. Crucially, `destroy(x)` is only valid if the type defines a destructor. A type without a destructor cannot be destroyed—it must be consumed by moving, returning, or destructuring. This prevents accidental discard and forces resource handling through program logic.

### Defer: Explicit Cleanup

The `defer` statement makes cleanup explicit. Unlike languages where destructors run implicitly at scope boundaries, Concrete requires you to write `defer destroy(f)`. You see the cleanup in the source. The compiler never secretly inserts destructor calls.

```
fn process_files!() {
    let f1 = open("a.txt")
    defer destroy(f1)           // you see this
    
    let f2 = open("b.txt")
    defer destroy(f2)           // you see this
    
    // When scope exits:
    // 1. destroy(f2) runs
    // 2. destroy(f1) runs
}
```

Multiple `defer` statements execute in reverse order (LIFO). `defer` runs at scope exit including early returns and error propagation. It's deterministic—not "eventually" like GC finalizers.

When a value is scheduled with `defer destroy(x)`, it becomes reserved. You cannot move it, destroy it again, or create borrows that might overlap the deferred destruction point.

## Borrowing Without Lifetime Annotations

Concrete's borrowing system draws from Rust but simplifies it. References exist within lexical regions—scopes that bound their lifetime. You can have multiple immutable borrows or one mutable borrow. References can't escape their region.

```
borrow f as fref in R {
    // fref has type &[File, R]
    // f is unusable in this block
    let len = length(fref)
}
// f is usable again
```

The key difference from Rust: no lifetime parameters in function signatures. Functions that accept references are generic over the region, but this genericity is implicit:

```
fn length<R>(file: &[File, R]) -> Uint {
    ...
}
```

The function cannot store the reference because it has no way to name `R` outside the call. The region system ensures references can't outlive their source, but you don't annotate lifetimes everywhere.

For single-expression borrows, the region is anonymous:

```
let len = length(&f)  // borrows f for just this call
```

### Borrowing Rules

The rules are strict but comprehensible:

1. While borrowed, the original is unusable
2. Multiple immutable borrows are allowed
3. Mutable borrows are exclusive—one `&mut T` at a time, no simultaneous `&T`
4. References cannot escape their region
5. Nested borrows of the same owned value are forbidden
6. Borrowing a reference is allowed, but the derived reference can't outlive the original's region

Closures may not capture references if the closure escapes the borrow region. This ensures references never outlive their lexical scope.

## Allocation as a Capability

Allocation deserves special attention because it's so often invisible. In most languages, many operations allocate behind your back—string concatenation, collection growth, closure creation. You find out about allocation pressure through profiling or by hitting OOM.

Concrete treats allocation as a capability. Functions that may allocate declare `with(Alloc)`. The call site binds which allocator to use:

```
fn main!() {
    let arena = Arena.new()
    defer arena.deinit()
    
    let list = create_list<Int>() with(Alloc = arena)
    push(&mut list, 42) with(Alloc = arena)
}
```

Inside a function with `with(Alloc)`, allocation "just works"—the bound allocator propagates through nested calls. But at the boundary, you see exactly where allocation happens and which allocator serves it.

Allocator binding is lexically scoped. A nested binding may shadow an outer one. Closures capture allocator bindings only if invoked within the lexical scope where the binding is in effect—if a closure escapes, it must accept an explicit allocator parameter.

Stack allocation does not require the `Alloc` capability:

```
fn example() {
    let x: Int = 42                    // stack
    let arr: [100]Uint8 = zeroed()     // stack
}
```

This makes allocation-free code provably allocation-free.

### Allocator Types

Concrete provides several allocator types out of the box:

```
// General-purpose heap allocator
let gpa = GeneralPurposeAllocator.new()
defer gpa.deinit()

// Arena allocator — free everything at once
let arena = Arena.new(gpa)
defer arena.deinit()

// Fixed buffer allocator — no heap, uses stack memory
let buf: [1024]Uint8 = zeroed()
let fba = FixedBufferAllocator.new(&buf)
```

All allocators implement a common `Allocator` trait with `alloc`, `free`, and `realloc` methods.

## Error Handling

Errors are values, not exceptions:

```
fn parse(input: String) -> Result<Config, ParseError> {
    ...
}

fn load_config!() -> Result<Config, Error> {
    let f = open("config.toml")?
    defer destroy(f)
    
    let content = read(&f)
    let config = parse(content)?
    Ok(config)
}
```

The `?` operator propagates errors. When `?` triggers an early return, all `defer` statements in scope run before returning. This interaction is crucial—cleanup happens even on error paths, and you can see exactly where.

There are no exceptions and no panic mechanism in the core language. If the runtime terminates due to an unrecoverable fault, deferred expressions are not guaranteed to run.

## Pattern Matching

Exhaustive pattern matching with linear type awareness:

```
fn describe(opt: Option<Int>) -> String {
    match opt {
        Some(n) => format("Got {}", n),
        None => "Nothing"
    }
}
```

Linear types in patterns must be consumed:

```
fn handle!(result: Result<Data, File>) {
    match result {
        Ok(data) => use_data(data),
        Err(f) => destroy(f)
    }
}
```

Both branches consume their linear values. Borrowing in patterns is also supported:

```
fn peek(opt: &Option<Int>) -> Int {
    match opt {
        &Some(n) => n,
        &None => 0
    }
}
```

## Traits and Bounded Polymorphism

Traits provide bounded polymorphism:

```
trait Ord {
    fn compare(&self, other: &Self) -> Ordering
}

trait Show {
    fn show(&self) -> String
}

fn sort<T: Ord>(list: List<T>) with(Alloc) -> List<T> {
    ...
}

fn sort_and_print<T: Ord + Show>(list: List<T>) with(Alloc, Console) -> List<T> {
    let sorted = sort(list)
    print_all(&sorted)
    sorted
}
```

Trait methods may take the receiver as `&self`, `&mut self`, or `self`. If a trait method takes `self`, calling it consumes the value following linear consumption rules. Trait implementations for linear types are allowed—they just must respect the receiver mode.

## Generics and Parametricity

Generic functions cannot accidentally become effectful depending on instantiation. Capabilities are checked before monomorphization and are invariant under instantiation:

```
fn map<T, U>(list: List<T>, f: fn(T) -> U) -> List<U> {
    ...
}
```

This function is pure regardless of what `T` and `U` are. If `f` requires capabilities, that must be declared:

```
fn map_io<T, U>(list: List<T>, f: fn(T) with(IO) -> U) with(IO) -> List<U> {
    ...
}
```

There's no capability polymorphism—you cannot be generic over capability sets. Each capability set must be concrete. This simplifies the type system and avoids questions about capability set operations at the type level.

## Type Inference

Type inference is **local only**:

- Function signatures must be fully annotated (parameters, return type, capabilities)
- Inside function bodies, local variable types may be inferred from their initializers
- Type information flows in one direction (from annotations to inference, never backward)

```
fn process(data: List<Int>) with(Alloc) -> List<Int> {
    let doubled = map(data, fn(x) { x * 2 })  // type inferred
    let filtered = filter(doubled, fn(x) { x > 0 })  // type inferred
    filtered
}
```

This keeps type errors local and makes signatures self-documenting. You can always understand a function's interface without reading its body.

## Modules

```
module FileSystem

public fn open(path: String) with(FileOpen) -> Result<File, IOError> {
    ...
}

public fn read<R>(file: &[File, R]) with(FileRead) -> String {
    ...
}

private fn validate(path: String) -> Bool {
    ...
}
```

Visibility is `public` or `private` (the default). Types, functions, and constants can be marked either way.

Capabilities are part of a function's signature and therefore part of the public API contract. Changing the required capability set of a public function is a breaking change.

Imports support aliasing and selective imports:

```
import FileSystem
import FileSystem.{open, read, write}
import FileSystem as FS
```

## Types

### Primitives

```
Bool
Int, Int8, Int16, Int32, Int64
Uint, Uint8, Uint16, Uint32, Uint64
Float32, Float64
Char, String
```

All primitive numeric types and `Bool` are `Copy`. `String` is linear.

### Algebraic Data Types

```
type Option<T> {
    Some(T),
    None
}

type Result<T, E> {
    Ok(T),
    Err(E)
}

type List<T> {
    Nil,
    Cons(T, List<T>)
}
```

### Records

```
type Point {
    x: Float64,
    y: Float64
}
```

A record is `Copy` only if explicitly marked and all fields are `Copy`:

```
type Copy Point {
    x: Float64,
    y: Float64
}
```

For generic types, linearity depends on the type parameter. `Option<Int>` is `Copy` because `Int` is. `Option<File>` is linear because `File` is.

### Standard Library Types

For domains where precision matters, the standard library includes:

- **Decimal** — Fixed-point decimal arithmetic for financial calculations
- **BigInt** — Arbitrary-precision integers
- **BigDecimal** — Arbitrary-precision decimals

These avoid floating-point representation errors in financial systems and cryptographic applications.

## Determinism

### Reproducible Builds

Concrete aims for **bit-for-bit reproducible builds**:

- Same source code + same compiler version = identical binary
- No timestamps, random seeds, or environment-dependent data embedded in output
- Build order does not affect output

### Perfect Replayability

For debugging, Concrete supports **deterministic replay**:

- All sources of non-determinism are explicit and controllable
- Random number generation requires `Random` capability with explicit seed
- System time requires `Clock` capability
- Given the same inputs and capability bindings, execution is identical

This enables reproducing Heisenbugs that depend on timing or randomness. When your program behaves the same way every time given the same inputs, debugging becomes tractable.

## The Grammar as Guarantee

Concrete uses an LL(1) grammar. Every parsing decision can be made with a single token of lookahead. No ambiguity, no backtracking, no lexer hacks.

This might seem like an implementation detail, but it has consequences for the developer experience. Simple tooling can parse Concrete—any LL(1) parser generator works. Syntax errors are local and comprehensible. There are no parser edge cases that behave differently in different tools.

The grammar enforces stylistic constraints: keywords are reserved, statements and expressions are syntactically distinct, blocks use braces, standard operator precedence is built in. You can't invent surprising syntax.

## Compilation Targets

Concrete supports multiple backends:

- **Native** — Direct machine code via MLIR/LLVM
- **C** — Portable C output for maximum platform support
- **WebAssembly** — For browser and edge deployment

Cross-compilation is a first-class feature. Specify target at build time.

## Tooling

Unlike languages where essential tooling is an afterthought or third-party dependency, Concrete ships with built-in tools:

- **Package manager** — Dependency resolution and versioning
- **Formatter** — Canonical code formatting (one true style)
- **Linter** — Static analysis and style checking
- **Test runner** — Built-in test framework
- **REPL** — Interactive evaluation for debugging and exploration

These are part of the language distribution, not external dependencies with their own versioning and compatibility concerns.

## Profiling and Tracing

Profiling and tracing are first-class features:

- Built into the runtime, not bolted on
- Low overhead when disabled
- Structured output for tooling integration

While code is read more often than written, it is executed even more often than read. Performance visibility matters, especially for systems programming.

## What You Can Say About Programs

If a program type-checks in Concrete, you gain mechanical knowledge about it:

**"This function is pure."** No capabilities declared. The compiler proves it performs no side effects, no IO, no mutation, no allocation. You can reason about it as a mathematical function.

**"This resource is used exactly once."** Linear type. The compiler proves no leaks, no double-free, no use-after-free.

**"These are the only effects this code can perform."** Capability set is explicit. It cannot secretly touch the network or file system.

**"This code cannot escape the type system."** Unsafe operations require `with(Unsafe)`. You can grep for all trust boundaries.

**"Allocation happens here, using this allocator."** Call site binds the allocator. No hidden heap activity.

**"Cleanup happens here."** `defer destroy(x)` is visible. The compiler doesn't insert invisible destructor calls.

**"This build is reproducible."** Same inputs, same binary. Debugging is tractable.

These are mechanical guarantees derived from the type system, which is itself proven sound in Lean. Not best practices, not conventions—proofs.

## Example: File Processing

```
module Main

import FileSystem.{open, read, write}
import Parse.{parse_csv}

fn process_file!(input_path: String, output_path: String) with(Alloc) -> Result<(), Error> {
    let in_file = open(input_path)?
    defer destroy(in_file)
    
    let content = read(&in_file)
    let data = parse_csv(content)?
    let output = transform(&data)
    
    let out_file = open(output_path)?
    defer destroy(out_file)
    
    write(&mut out_file, output)
    Ok(())
}

fn transform(data: &List<Row>) -> String {
    ...
}

fn main!() {
    let arena = Arena.new()
    defer arena.deinit()
    
    match process_file("input.csv", "output.txt") with(Alloc = arena) {
        Ok(()) => println("Done"),
        Err(e) => println("Error: " + e.message())
    }
}
```

Everything is visible: resource acquisition, cleanup scheduling, error propagation, allocator binding. No hidden control flow.

## Who Should Use This

Concrete is not for every project. It trades convenience for explicitness, flexibility for auditability. Prototyping is slower. Some patterns become verbose or impossible. You'll miss interior mutability when building certain data structures. You'll miss runtime reflection when building serialization libraries.

But for code where correctness is paramount—cryptographic primitives, consensus protocols, financial transaction systems, medical device firmware—the trade is worth it. You get a language where you can make strong claims about program behavior and those claims are mechanically verified.

The verified kernel means the language semantics won't drift. The capability system means effects are auditable. The linear types mean resources are managed with precision. The LL(1) grammar means tooling is straightforward. Reproducible builds mean debugging is tractable.

Concrete aims to be a language you can trust the way you trust mathematics: not because someone promises it works, but because you can check the proof yourself.

---

## Quick Reference

| Annotation | Meaning |
|------------|---------|
| `fn foo() -> T` | Pure function, no capabilities, no allocation |
| `fn foo!() -> T` | Shorthand for `with(Std)` |
| `fn foo() with(C) -> T` | Requires capability set `C` |
| `with(Alloc)` | Function may allocate |
| `with(Alloc = a)` | Bind allocator `a` at call site |
| `T` | Linear type, must be consumed exactly once |
| `type Copy T` | Unrestricted type, can be copied or ignored |
| `&T` or `&[T, R]` | Immutable reference in region `R` |
| `&mut T` or `&mut [T, R]` | Mutable reference in region `R` |
| `borrow x as y in R { }` | Explicit borrow with named region |
| `defer expr` | Run `expr` when scope exits |
| `destroy(x)` | Consume `x` via destructor |
| `destroy T with(C) { }` | Define destructor for type `T` requiring capability `C` |

