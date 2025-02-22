+++
title = "Template Compiler (DRAFT)"
description = "Compiling HTML (or other) templates to Wasm Components"
date = "2023-01-08"
aliases = ["articles/template-compiler"]
+++

WebAssembly (Wasm) components are a compact, portable, and secure unit of code.
They're a <q>compile target</q> with a binary format, not a source code language.
So you won't write them by hand, you'll have tools to generate them for you.

<p>
In addition to languages like Rust, C++, JavaScript, and Python that are "General Purpose",
certain Domain-Specific languages may be good candidates for "componentizing".
</p>

For example,
<ul>
    <li>
        <strong>parser/grammar languages</strong> (e.g. lex, yacc)
        can be compiled to components with a single parse function that
        takes in text and returns an AST and
    </li>
    <li>
        <strong>templating languages</strong> (e.g. handlebars, pug)
        can be compiled into components with a single function that
        takes in parameters and returns the filled in template.
    </li>
</ul>

## Template-to-Component Compiler

Let's focus on the second example and make a compiler that converts templates into components!

A Wasm component has a type that's defined by a "world" in the
<a href="https://github.com/WebAssembly/component-model/blob/main/design/mvp/WIT.md">WIT interface-definition language</a>
which identifies all the things the component imports and exports.
For simple templates, we don't need any imports and we have exactly one export which is our templating function.

```js
world my-template {
    record params {
        title: string,
        ...
    }

    export apply: func(param: params) -> string
}
```

The exact fields and types that the parameters record has will depend on what our template
uses and we can infer that directly from the template file.

## Canonical ABI

To implement this high-level interface, we need to use the canonical ABI
which defines the way that high-level component types can be
passed into and returned from components using integer values
and the Wasm linear memory.

<figure>
    <img
        src="/tc-1/canon-abi.svg"
        width="400px"
        height="115px"
        alt="The canonical ABI connects the component model and core wasm"
    />
</figure>

<br>

### Lifting and Lowering

In the Canonical ABI, the Component Model is <q>higher</q> (as in higher-level)
than Core Wasm and Modules.
So, when things need to be converted upwards from Core Wasm to the Component Model, it's called <q>lifting</q>.
Conversely, when things need to be converted downards from the Component Model to Core Wasm, it's called <q>lowering</q>.

<figure>
    <img
        src="/tc-1/lift-lower.svg"
        width="550px"
        height="350px"
        alt="Lifting types from Core Wasm to the Component Model and lowering them from Component Model to Core Wasm"
    />
</figure>

<br>

### Imported and Exported Functions

When talking about functions, the direction of lifting and lowering corresponds
to whether the function is an export or import.

Exported functions are defined in the inner module and lifted to the component which re-exports it.
Imported functions are defined by a component import and lowered to the module import.

<figure>
    <img
        src="/tc-1/function-export-import.svg"
        width="700px"
        height="330px"
        alt="Diagram showing module exports being lifted to component exports, and component imports being lowed to module imports"
    />
</figure>

For exports and imports, the arguments go in the direction from caller to callee
and the returns go from callee to caller.

<figure>
    <img
        src="/tc-1/argument-return.svg"
        width="700px"
        height="250px"
        alt="Diagram showing export arguments being lowered and return being lifted, with import arguments being raised and return being lowered"
    />
</figure>

### Values

Values in the canonical ABI are either passed directly in arguments/returns
as a sequence of core Wasm values (e.g. i32, f32) or indirectly using memory.
The default is for values to be passed directly and memory indirection is used
when the value is too large to be passed directly or the value is part of a list.

<aside>
    <strong>Note:</strong> you can find more information in the 
    <a href="https://github.com/WebAssembly/component-model/blob/main/design/mvp/canonical-abi/definitions.py">
        canonical-abi/definitions.py
    </a>
</aside>

The canonical ABI allows components to select which string encoding to lift/lower strings from/into
and we will be choosing UTF-8 (the other options are UTF-16 and Latin 1 + UTF-16).
Strings in the canonical ABI are represented as an offset and length which has the direct
representation (i32, i32) and a memory representation of two 4-byte little endian integers.

<figure>
    <img
        src="/tc-1/string-memory.svg"
        width="700px"
        height="250px"
        alt="Diagram showing string memory being layed out with pointer and length together pointing at the text data"
    />
</figure>

Records are represented directly by concatenating the direct representation of all their fields in order
and are represented in memory by aligning and concatenating the memory representation of each field in order.

### Template ABI

The generated template function is exported, which means it will be defined in the module
then lifted and rexported in the outer component.

It has a single record argument, which is lowered into the template,
and it has a single string result, which is lifted back up to the caller.
Depending on the number of string parameters the parameter record will either
be passed directly or in memory.

## Allocators

In order to use the canonical ABI with arguments spilled to memory
(which can happen depending on the number of parameters),
we have to provide an allocator for the host to use for allocating
the spilled args.

There are many kinds of allocators but because we're only ever using
it to allocate arguments which are then all freed together we can
use one of the simplest allocators called a bump allocator.

## Generating the Module

To return a string, we just need to return the integer index in memory of the (index, length) pair.