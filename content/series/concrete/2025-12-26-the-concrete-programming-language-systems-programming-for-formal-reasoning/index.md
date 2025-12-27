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

## On This Specification

This document describes what we're building, not what we've finished building. The kernel formalization in Lean is ongoing work. Until that formalization is complete, this specification likely contains mistakes, ambiguities, and internal contradictions.

We state this not as an apology but as a feature of our approach. Most language specifications accumulate contradictions silently over years, edge cases where the spec says one thing and the implementation does another, or where two parts of the spec conflict in ways nobody noticed. These contradictions become load-bearing bugs that can never be fixed without breaking existing code.

By designing Concrete around a formally verified kernel from the start, we force these contradictions into the open. When we formalize a feature in Lean, the proof assistant will reject inconsistencies. Features that seem reasonable on paper will turn out to be unsound, and we'll have to redesign them. This is the point. We'd rather discover that our linearity rules have a hole *before* a million lines of code depend on the broken behavior.

The specification and the formalization will co-evolve. As we prove properties in Lean, we'll update this document. As we write this document, we'll discover what needs proving. The goal is convergence: eventually, this specification will be a human-readable projection of a machine-checked artifact.

## The Core Idea

Most languages treat verification as something bolted on after the fact. You write code, then maybe you write tests, maybe you run a linter, maybe you bring in a theorem prover for critical sections. The language itself remains agnostic about provability.

Concrete inverts this relationship. The language is *designed around* a verified core, a small kernel calculus formalized in Lean with mechanically-checked proofs of progress, preservation, linearity soundness, and effect soundness. The surface language exists only to elaborate into this kernel.

### What "Correct" Means

When we say a type-checked program is "correct by construction," we mean correct with respect to specific properties:

- **Memory safety**: no use-after-free, no double-free, no dangling references
- **Resource safety**: linear values consumed exactly once, no leaks
- **Effect correctness**: declared capabilities match actual effects

We do not guarantee termination. Recursive functions may diverge. We do not guarantee liveness or deadlock freedom. These properties are outside the current verification scope. The kernel proves progress (well-typed programs don't get stuck) and preservation (types are maintained during evaluation), which together yield memory and resource safety, not total correctness.

### The Trust Boundary

The kernel type system and its properties are mechanically checked in Lean. What remains trusted: the Lean proof checker itself, the elaborator (surface language to kernel), and the code generator (kernel to machine code). Verifying the elaborator and code generator is future work.

## The Compilation Pipeline

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

The kernel checkpoint is the semantic gate. Everything before it transforms syntax; everything after it preserves meaning.

## Types

### Primitives

```
Bool
Int, Int8, Int16, Int32, Int64
Uint, Uint8, Uint16, Uint32, Uint64
Float32, Float64
Char, String
Unit
```

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

### Standard Library Types

For domains where precision matters, the standard library includes:

- **Decimal**: fixed-point decimal arithmetic for financial calculations
- **BigInt**: arbitrary-precision integers
- **BigDecimal**: arbitrary-precision decimals

These avoid floating-point representation errors in financial systems and cryptographic applications.

## Linearity and Copy

All values in Concrete are linear by default. A linear value must be consumed exactly once, not zero times (that's a leak), not twice (that's a double-free). Consumption happens when you pass the value to a function that takes ownership, return it, destructure it via pattern matching, or explicitly call `destroy(x)`.

```
fn example!() {
    let f = open("data.txt")
    defer destroy(f)
    let content = read(&f)
    // destroy(f) runs here because of defer
}
```

If `f` isn't consumed on all paths, the program is rejected. If you try to use `f` after moving it, the program is rejected. This is compile-time enforcement, not runtime checking.

### The Copy Marker

Some types escape linear restrictions. The rules for `Copy` are:

1. **Copy is explicit and opt-in.** You must mark a type as `Copy`; it is never inferred.
2. **Copy is structural.** A type can be `Copy` only if all its fields are `Copy`.
3. **Copy types cannot have destructors.** If a type defines `destroy`, it cannot be `Copy`.
4. **Copy types cannot contain linear fields.** A `Copy` record with a `File` field is rejected.

```
type Copy Point {
    x: Float64,
    y: Float64
}
```

The primitive numeric types and `Bool` are built-in `Copy` types. `String` is linear. For generic types, linearity depends on the type parameter: `Option<Int>` is `Copy` because `Int` is; `Option<File>` is linear because `File` is.

`Copy` is not an escape hatch from thinking about resources. It's a marker for types that have no cleanup requirements and can be freely duplicated.

### Destructors

A linear type may define a destructor:

```
type File {
    handle: FileHandle
}

destroy File with(File) {
    close_handle(self.handle)
}
```

The destructor takes ownership of `self`, may require capabilities, and runs exactly once when explicitly invoked. `destroy(x)` is only valid if the type defines a destructor. A type without a destructor must be consumed by moving, returning, or destructuring.

### Defer

The `defer` statement schedules cleanup at scope exit:

```
fn process_files!() {
    let f1 = open("a.txt")
    defer destroy(f1)
    
    let f2 = open("b.txt")
    defer destroy(f2)
    
    // When scope exits:
    // 1. destroy(f2) runs
    // 2. destroy(f1) runs
}
```

Multiple `defer` statements execute in reverse order (LIFO). `defer` runs at scope exit including early returns and error propagation.

When a value is scheduled with `defer destroy(x)`, it becomes reserved. You cannot move it, destroy it again, or create borrows that overlap the deferred destruction point.

### Abort

Abort is immediate process termination, outside normal control flow:

- Out-of-memory conditions trigger abort
- Stack overflow triggers abort  
- Explicit `abort()` terminates immediately
- **Deferred cleanup does not run on abort**

This matches Zig's behavior: `defer` is for normal control flow, not catastrophic failure. Abort is outside language semantics. The process stops. There are no guarantees about state after abort begins.

## Borrowing

References let you use values without consuming them. References exist within lexical regions that bound their lifetime.

```
borrow f as fref in R {
    // fref has type &[File, R]
    // f is unusable in this block
    let len = length(fref)
}
// f is usable again
```

Unlike Rust, no lifetime parameters in function signatures. Functions that accept references are generic over the region, but implicitly:

```
fn length<R>(file: &[File, R]) -> Uint {
    ...
}
```

The function cannot store the reference because it cannot name `R` outside the call.

For single-expression borrows, the region is anonymous:

```
let len = length(&f)  // borrows f for just this call
```

### Borrowing Rules

1. While borrowed, the original is unusable
2. Multiple immutable borrows allowed
3. Mutable borrows exclusive: one `&mut T` at a time, no simultaneous `&T`
4. References cannot escape their region
5. Nested borrows of the same owned value forbidden
6. Derived references can't outlive the original's region

Closures cannot capture references if the closure escapes the borrow region.

## Capabilities

Concrete is **pure by default**. A function without capability annotations cannot perform IO, cannot allocate, cannot mutate external state. It computes a result from its inputs, nothing more.

Purity means no side effects and no heap allocation. Stack allocation and compile-time constants are permitted. Non-termination is possible; purity does not imply totality.

When a function needs effects, it declares them:

```
fn read_file(path: String) with(File) -> String {
    ...
}

fn process_data() with(File, Network, Alloc) -> Result {
    ...
}
```

Capabilities propagate monotonically. If `f` calls `g`, and `g` requires `File`, then `f` must declare `File` too. No implicit granting, no ambient authority. The compiler enforces this transitively.

### The Std Capability

For application entry points, Concrete provides a shorthand. The `!` suffix declares the `Std` capability:

```
fn main!() {
    println("Hello")
}
```

This desugars to `fn main() with(Std)`. `Std` includes file operations, network, clock, environment, random, and allocation, but excludes `Unsafe`.

**Library code should prefer explicit capability lists.** This is a social convention, not a mechanical enforcement. The compiler won't reject a library function that uses `Std`. But explicit capabilities make dependencies auditable. `Std` is a convenience for applications, not a license for libraries.

### Security Model

Capabilities don't sandbox code. If a dependency declares `with(Network)`, it gets network access. What they provide is **auditability**. You can grep for `with(Network)` and find every function that touches the network. You can verify that your JSON parser has no capabilities. You can review dependency updates by diffing capability declarations.

### Capability Polymorphism

Currently, you cannot be generic over capability sets:

```
// Not allowed
fn map<T, U, C>(list: List<T>, f: fn(T) with(C) -> U) with(C) -> List<U>
```

Each capability set must be concrete. This means generic combinators must be duplicated per capability set. Capability polymorphism is future work; the theory is well-understood (effect polymorphism in Koka, Eff, Frank), but adds complexity to the type system and the Lean formalization.

## Allocation

Allocation deserves special attention because it's often invisible. In most languages, many operations allocate behind your back: string concatenation, collection growth, closure creation.

Concrete treats allocation as a capability. Functions that allocate declare `with(Alloc)`. The call site binds which allocator:

```
fn main!() {
    let arena = Arena.new()
    defer arena.deinit()
    
    let list = create_list<Int>() with(Alloc = arena)
    push(&mut list, 42) with(Alloc = arena)
}
```

Inside `with(Alloc)`, the bound allocator propagates through nested calls. At the boundary, you see exactly where allocation happens and which allocator serves it.

Stack allocation does not require `Alloc`:

```
fn example() {
    let x: Int = 42                    // stack
    let arr: [100]Uint8 = zeroed()     // stack
}
```

Allocation-free code is provably allocation-free.

### Allocator Types

```
// General-purpose heap allocator
let gpa = GeneralPurposeAllocator.new()
defer gpa.deinit()

// Arena allocator, free everything at once
let arena = Arena.new(gpa)
defer arena.deinit()

// Fixed buffer allocator, no heap
let buf: [1024]Uint8 = zeroed()
let fba = FixedBufferAllocator.new(&buf)
```

All allocators implement a common `Allocator` trait.

## Error Handling

Errors are values:

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

The `?` operator propagates errors. When `?` triggers an early return, all `defer` statements in scope run first. Cleanup happens even on error paths.

No exceptions. No panic. Unrecoverable faults (out-of-memory, stack overflow, explicit abort) terminate immediately without running deferred cleanup.

## What You're Giving Up

Concrete is not a general-purpose language. It's for code that must be correct: cryptographic implementations, financial systems, safety-critical software, blockchain infrastructure.

**No garbage collection.** Memory is managed through linear types and explicit destruction. No GC pauses, no unpredictable latency, no hidden memory pressure.

**No implicit control flow.** What you see is what executes. No implicit function calls from operator overloading, no compiler-inserted destructor calls. `defer` statements are explicit: you write them, you see them, even though their execution occurs at scope exit.

**No implicit allocation.** Allocation requires the `Alloc` capability. `grep with(Alloc)` finds every function that might touch the heap.

**No interior mutability.** All mutation flows through `&mut` references. An immutable reference `&T` guarantees immutability, no hidden mutation behind an immutable facade.

**No reflection, no eval, no runtime metaprogramming.** All code paths are determined at compile time.

**No implicit global state.** All global interactions (file system, network, clock, environment) are mediated through capabilities.

**No variable shadowing.** Each variable name is unique within its scope.

**No null.** Optional values use `Option<T>`.

**No undefined behavior in safe code.** Kernel semantics are fully defined and proven sound. The `Unsafe` capability explicitly reintroduces the possibility of undefined behavior for FFI and low-level operations.

**No concurrency primitives.** The language provides no threads, no async/await, no channels. Concurrency is a library concern. This may change, but any future concurrency model must preserve determinism and linearity, likely through structured or deterministic concurrency. This is a design constraint, not an open question.

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

Borrowing in patterns:

```
fn peek(opt: &Option<Int>) -> Int {
    match opt {
        &Some(n) => n,
        &None => 0
    }
}
```

## Traits

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
```

Trait methods take `&self`, `&mut self`, or `self`. If a method takes `self`, calling it consumes the value.

## Type Inference

Type inference is **local only**. Function signatures must be fully annotated. Inside bodies, local types may be inferred:

```
fn process(data: List<Int>) with(Alloc) -> List<Int> {
    let doubled = map(data, fn(x) { x * 2 })  // inferred
    let filtered = filter(doubled, fn(x) { x > 0 })  // inferred
    filtered
}
```

You can always understand a function's interface without reading its body.

## Modules

```
module FileSystem

public fn open(path: String) with(File) -> Result<File, IOError> {
    ...
}

public fn read<R>(file: &[File, R]) with(File) -> String {
    ...
}

private fn validate(path: String) -> Bool {
    ...
}
```

Visibility is `public` or `private` (default). Capabilities are part of the signature and the public API contract.

```
import FileSystem
import FileSystem.{open, read, write}
import FileSystem as FS
```

## Unsafe and FFI

The `Unsafe` capability gates operations the type system cannot verify: foreign function calls, raw pointer operations, type transmutation, inline assembly, and linearity bypasses.

```
fn transmute<T, U>(value: T) with(Unsafe) -> U

fn ptr_read<T>(ptr: Address[T]) with(Unsafe) -> T

fn ptr_write<T>(ptr: Address[T], value: T) with(Unsafe)
```

`Unsafe` propagates through the call graph like any other capability. Grep for `with(Unsafe)` to find all trust boundaries.

### Raw Pointers

Raw pointers exist for FFI and low-level memory manipulation:

```
Address[T]       // raw pointer to T
```

Raw pointers are `Copy`. They carry no lifetime information and no linearity guarantees. This is safe because:

- Creating a raw pointer is safe. `address_of(r)` extracts an address.
- Holding a raw pointer is safe. It's a number.
- Using a raw pointer requires `Unsafe`. Dereference, arithmetic, and casting are gated.

```
fn to_ptr<T>(r: &T) -> Address[T] {
    address_of(r)  // safe
}

fn deref<T>(ptr: Address[T]) with(Unsafe) -> T {
    read_ptr(ptr)  // unsafe: no guarantee ptr is valid
}
```

`Copy` does not imply usable. Raw pointers can be freely duplicated because they carry no guarantees. Safety is enforced at the point of use, not at the point of creation.

### Foreign Functions

Declare foreign functions with `Unsafe` and the `foreign` directive:

```
fn malloc(size: Uint) with(Unsafe) -> Address[Unit] =
    foreign("malloc")

fn free(ptr: Address[Unit]) with(Unsafe) =
    foreign("free")
```

The compiler generates calling convention glue and links the symbol. Foreign signatures are restricted to C-compatible types. Details of the type mapping are deferred to a future FFI specification.

## Implementation

### Determinism

Concrete aims for **bit-for-bit reproducible builds**: same source + same compiler = identical binary. No timestamps, random seeds, or environment-dependent data in output.

For debugging, **deterministic replay**: random generation requires `Random` with explicit seed, system time requires `Clock`. Same inputs produce identical execution.

### The Grammar

LL(1). Every parsing decision with a single token of lookahead. No ambiguity, no backtracking.

This is a permanent design constraint, not an implementation detail. Future language evolution is bounded by what LL(1) can express. We accept this constraint for tooling simplicity and error message quality.

### Compilation Targets

**Native** via MLIR/LLVM, **C** for portability, **WebAssembly** for browser and edge. Cross-compilation is first-class.

### Tooling

Concrete ships with package manager, formatter, linter, test runner, and REPL. Part of the distribution, not external dependencies.

## What You Can Say About Programs

If a program type-checks:

**"This function is pure."** No capabilities declared. No side effects, no IO, no allocation.

**"This resource is used exactly once."** Linear type. No leaks, no double-free, no use-after-free.

**"These are the only effects this code can perform."** Capability set is explicit and complete.

**"This code cannot escape the type system."** Unsafe operations require `with(Unsafe)`.

**"Allocation happens here, using this allocator."** Call site binds the allocator.

**"Cleanup happens here."** `defer destroy(x)` is visible.

**"This build is reproducible."** Same inputs, same binary.

Mechanical guarantees from a type system proven sound in Lean. Not conventions, proofs.

## Example

```
module Main

import FileSystem.{open, read, write}
import Parse.{parse_csv}

fn process_file(input_path: String, output_path: String) with(File, Alloc) -> Result<Unit, Error> {
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

Everything is visible: resource acquisition, cleanup scheduling, error propagation, allocator binding.

## Who Should Use This

Concrete trades convenience for explicitness, flexibility for auditability. Prototyping is slower. Some patterns become verbose. You'll miss interior mutability for certain data structures.

But for cryptographic primitives, consensus protocols, financial transaction systems, medical device firmware, the trade is worth it. Strong claims about program behavior, mechanically verified.

A language you can trust the way you trust mathematics: not because someone promises it works, but because you can check the proof.

---

## Quick Reference

| Annotation | Meaning |
|------------|---------|
| `fn foo() -> T` | Pure function, no capabilities |
| `fn foo!() -> T` | Shorthand for `with(Std)` |
| `fn foo() with(C) -> T` | Requires capability set `C` |
| `with(Alloc)` | Function may allocate |
| `with(Alloc = a)` | Bind allocator `a` at call site |
| `T` | Linear type, consumed exactly once |
| `type Copy T` | Unrestricted type, freely duplicated |
| `&T` or `&[T, R]` | Immutable reference in region `R` |
| `&mut T` | Mutable reference |
| `Address[T]` | Raw pointer (unsafe to use) |
| `borrow x as y in R { }` | Explicit borrow with named region |
| `defer expr` | Run `expr` at scope exit |
| `destroy(x)` | Consume via destructor |
| `foreign("symbol")` | Foreign function binding |
