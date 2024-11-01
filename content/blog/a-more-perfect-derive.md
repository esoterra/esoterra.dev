+++
title = "A More Perfect Derive"
date = "2024-11-01"
+++

## What is Derive?

In some languages, users need to write (or use tools to generate) boilerplate implementations for common functionality (like debug printing, comparison, hashing) over and over again  on each type they define.

```py
class Point():
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Point(x={self.x}, y={self.y})"
```

Rust has an awesome feature called "derive" and using it we can write `#[derive(Debug, PartialEq, Eq, Hash)]` and the implementations will be generated at compile time. This improves productivity and removes an easy place for little mistakes to be made.

```rust
#[derive(Debug)]
struct Point {
    x: f32,
    y: f32,
}
```

## How Should Derive Handle Generics?

When we derive a trait for a type that has generic parameters, it may not be possible to generate an implementation without putting bounds on those parameters.

For example, in the following `Pair` type, it is only possible to `Debug` print `Pair<X>` if `X` can be `Debug` printed.

```rust
struct Pair<X> {
    left: X,
    right: X,
}
```

This can be expressed by the following impl bound.

```rust
impl<X> std::fmt::Debug for Pair<X>
where
    X: std::fmt::Debug
{
    ...
}
```

## What About More Complex Generics?

Some types use a generic type parameter without actually structurally including a value of that type directly. For example, the following type `List<T>` doesn't include a a `T` directly.

```rust
struct List<T> {
    data: Rc<T>,
    next: Option<Rc<List<T>>>,
}
```

For some traits like `Debug`, a wrapper like `Rc` around a `T` will only implement a trait if `T` does. For other traits like `Clone`, this isn't necessarily true because an `Rc<T>` is `Clone` even if `T` isn't.

That means that we don't actually need to bound our `Clone` implementation for `List<T>` with `T: Clone`. It could look like the following:

```rust
impl<T> Clone for List<T> {
    fn clone(&self) {
        List {
            value: self.value.clone(),
            next: self.next.clone(),
        }
    }
}
```

However, with the current derive implementation it still actually has a bound like in the `Pair`-`Debug` example and looks like the following.

```rust
impl<T> Clone for List<T>
where
    T: Clone
{
    fn clone(&self) { /* as before */ }
}
```

That's because the Rust derive mechanism makes a conservative assumption: we shouldn't leak information about the fields of a type into the bounds of the derived implementation. If the internals of `List<T>` change, it may not be possible to derive `Clone` without bounds in the future and that could accidentally introduce a breaking change.

## What is Perfect Derive?

The name "Perfect Derive" refers to a derive algorithm which generates implementations without any unnecessary bounds. It has been discussed by the Rust lang team ([GitHub issue](https://github.com/rust-lang/lang-team/issues/152), [Notes](https://hackmd.io/M_Wuev3pSwG_p4RfLGgDYw)) and by the blog [smallcultfollowing.com](https://smallcultfollowing.com/babysteps//blog/2022/04/12/implied-bounds-and-perfect-derive/). The examples in the previous section are just a reiteration of what's covered by these sources.

## Why not just turn on Perfect Derive?

If in future editions of Rust the derive macro becomes "perfect", then users switching to the new edition may have the bounds on their derived trait implementations change in subtle ways which cause breakages.

Some of these users won't even be aware of these subtleties or the change and will likely be very confused. Others may be aware of the update, but not want to change the behavior of their crate or use the new perfect derive anyway because it makes it easier to cause breaking changes.

If you want to learn more about the challenges to "just doing it", I highly recommend the [smallcultfollowing.com](https://smallcultfollowing.com/babysteps//blog/2022/04/12/implied-bounds-and-perfect-derive/) post.

## Design Solutions

I think perfect derive should be opt-in in a clear way, so that we don't confuse users and they make an intentional choice between leaking implementation details in their API for more precise bounds or using the more conservative current approach.

### Separate Macro

One option is for users to choose between two attribute macros: one that performs perfect derive and one that performs classic derive. This is already possible today using the [`perfect-derive` crate](https://crates.io/crates/perfect-derive).

```rust
#[perfect_derive(Clone)]
struct List<T> { /* as before */ }
```

However, I don't think it's obvious to users what a name like this means, when they should use it, and why derive doesn't always work this way. So I'm not sure if this is the right option.

### Type Attributes

Another approach would be to let the user indicate when defining a type what types they want their derived implementations to be bound on. If this attribute is not provided, the generic parameters would be used, which is the same as the current behavior.

```rust
#[derive(Clone)]
struct List<T> { ... }

// or equivalently

#[derive(Clone)]
#[bound_derive(T)]
struct List<T> { ... }
```

By adding this attribute, users can get whatever bounds they want including what perfect derive would have chosen.

```rust
#[derive(Clone)]
#[bound_derive(Rc<T>)]
struct List<T> { ... }
```

This is very explicit and encourages users to think explicitly about what bounds they want on their trait implementations.

### Field Attributes

Another idea I had is to put an attribute on the fields of the type which indicates that the bounds may be narrowed using information about that field's type. 

```rust
#[derive(Clone)]
struct List<T> {
    #[bound_derive]
    data: Rc<T>,
    #[bound_derive]
    next: Option<Rc<List<T>>>,
}
```

In this model, both adding and removing the `bound_derive` attribute and changing the type of a field labeled `bound_derive` are potentially breaking changes, but changing the type of any other field is not. This seems like a reasonable behavior and parallels the semantics of `pub`.

If multiple fields use the same type parameter `T` but only some are marked `bound_derive`, then either pessimistic bounds need to be emitted which still bound on `T` or it should be rejected as ambiguous.

```rust
struct List<T> {
    data: Rc<T>,
    #[bound_derive]
    next: Option<Rc<List<T>>>,
}
```

## Wrap Up

Out of these options, I think field attributes are probably the most elegant. Giving users the tools to communicate when they want a field's type to become a public part of the API of their derived type by explicitly saying "hey you can use this" and in a way that mirrors `pub` feels like a great solution.

I don't currently have the time to implement this proposal or write an RFC, but hopefully this will bring some attention to perfect derive and ways to solve it.

Cheers,
Robin