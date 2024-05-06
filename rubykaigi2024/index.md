----
marp: true
theme: rubykaigi2024
paginate: true
backgroundImage: url(./rubykaigi2024-bgs-main.png)
----

![bg](./rubykaigi2024-bgs.png)

----
<!--
_class: title
_backgroundImage: url(./rubykaigi2024-bgs-title.png)
-->

# An mruby for WebAssembly

## Presentation by Uchio Kondo

----
<!--
_class: normal
-->

![w:480](./profile.png)

# self.introduce!

- Uchio Kondo
  - from Fukuoka.rb
- Infra Engineer @ Mirrativ, Inc.
  - livestreaming & "live" gaming
- Translator of "Learnig eBPF"


----
<!--
_class: hero
_backgroundImage: url(./rubykaigi2024-bgs-yellowback.png)
-->

# Ruby and WebAssembly

----
<!--
_class: normal
-->

# Ruby for WebAssembly(WASM)?

- It's `ruby.wasm`, You know.
- A CRuby(MRI) That is compiled into wasm
  - C-based code -> Ruby runtime on wasm
  - WASI support

----
<!--
_class: normal
-->

# Showing another approach

- **mruby/edge** is yet another "Ruby on wasm"
- It is a basically mruby
  - but specialized for WebAssembly use case

----

<!--
_class: hero
_backgroundImage: url(./rubykaigi2024-bgs-whiteback.png)
-->

# So, What is mruby/edge?

----
<!--
_class:
  - normal
  - special1
-->

# mruby/edge getting started

- mruby/edge consists 2 components
  - mruby/edge "core" crate
  - the `mec` command (**m**ruby/**e**dge **c**ompiler)
  - Install `mec` first!

```
$ cargo install --version 0.3.0 mec
```

----
<!--
_class: normal
-->

# Prepare "Plain Old" Ruby script

```ruby
# fib.rb
def fib(n)
  case n
  when 0
    0
  when 1..2
    2
  else
    fib(n - 1) + fib(n - 2)
  end
end
```

----
<!--
_class: normal
-->

# Prepare RBS file for fib()

```ruby
# fib.export.rbs
def fib: (Integer) -> Integer
```

※ We have another option, but recommend to make this


----
<!--
_class: normal
-->

# Compile it into... WASM file

```
$ mec --no-wasi fib.rb
...
running: `cd .. && rm -rf work-mrubyedge-bhuxkrgcgOe5TAmDWFiMkgF5uVbnS9lR`
[ok] wasm file is generated: fib2.wasm

$ file fib.wasm
fib.wasm: WebAssembly (wasm) binary module version 0x1 (MVP)
```

----
<!--
_class: normal
-->

# Note that it has exported function `fib`

```
$ wasm-objdump -x -j Export ./fib.wasm

fib.wasm:       file format wasm 0x1
module name: <mywasm.wasm>

Section Details:

Export[3]:
 - memory[0] -> "memory"
 - func[417] <fib.command_export> -> "fib"
```

----
<!--
_class: normal
-->

# Then we can try it using (e.g.) wasmedge

```
$ wasmedge ./fib.wasm fib 15
610

$ wasmedge ./fib.wasm fib 20
6765
# ...
```

----
<!--
_class:
  - normal
  - sample2
-->

# Can this WASM available on a browser?

- prepare `wasm.html` including:

```html
<script async type="text/javascript">
  window.fire = function(e) {
    WebAssembly.instantiateStreaming(fetch("./fib.wasm"), {}).then(function (o) {
      let value = document.getElementById("myValue").value;
      let answer = o.instance.exports.fib(parseInt(value));
      document.getElementById("myAnswer").value = answer;
  });};
</script>
```

----
<!--
_class: normal
-->

# A working demo on the slide

<script type="text/javascript">
  window.fire = function(e) {
    WebAssembly.instantiateStreaming(fetch("./fib.wasm"), {})
      .then(function (o) {
        let value = document.getElementById("myValue").value;
        let answer = o.instance.exports.fib(parseInt(value));
        document.getElementById("myAnswer").style.backgroundColor = "#ffff00";
        document.getElementById("myAnswer").value = answer;
      }
    );    
  };
  console.log("done load function");
</script>

<button onclick="fire();">calc fib</button> 　　fib( <input id="myValue" type="text" value="20"> ) = <input id="myAnswer" type="text" value="?">
<br>

----
<!--
_class: normal
-->

# So with mruby/edge we can...

- Create a WASM file from Ruby script
- **Export** a specific "function" on that WASM
- In addition, we can specify **import functions**

----
<!--
_class: normal
-->

# Today, I will present you mruby/edge

- But before we understand mruby/edge, we have to have a graps with 2 technologies...
  - WebAssembly
  - ... and mruby!
- So let's start the journey together!

----
<!--
_class: hero
_backgroundImage: url(./rubykaigi2024-bgs-yellowback.png)
-->


# A Tour of WebAssembly

----
<!--
_class: normal
-->

# How do you know WebAssembly?

- Browser-based something...
- C++? or Rust? can be executed via WASM...
- Ruby or Python can run on browser by magical WASM power...
- Google meet? or Unity web games? or some cool contents

----
<!--
_class: normal
-->

# WebAssembly in a nutshell

- WebAssembly is a stack-based virtual machine
  - That can run its instructions on browser --
  - -- or *everywhere*

----
<!--
_class: normal
-->

# WebAssembly is used in:

- For example:
  - Browsers
  - Server-side programmes
  - Load Balancer Plugins, Containers, Supervisor
- ... everywhere!

----
<!--
_class:
  - normal
  - two-sides
-->

# Both browsers and servers

- As we have seen, one wasm binary can be executed both on browser and on terminal:

```
$ wasmedge ./fib.wasm fib 20
6765
```

![w:400 h:300](./dummy-image.png)

----
<!--
_class: normal
-->

# e.g. Server-side WASM embedding

* wasmer's Go API example

```golang
// ... omitted import
// go:embed fib.wasm
var wasmBytes []byte
func main() {
  store := wasmer.NewStore(wasmer.NewEngine())
  module, _ := wasmer.NewModule(store, wasmBytes)
  importObject := wasmer.NewImportObject()
  importObject.Register("env", map[string]wasmer.IntoExtern{"foo": fn})
  instance, _ := wasmer.NewInstance(module, importObject)
  addOne, _ := instance.Exports.GetFunction("add_one")
  result, _ := addOne(41)
}
```

----
<!--
_class: normal
-->

# e.g. proxy-wasm

```yaml
http_filters:
- name: envoy.filters.http.wasm
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.wasm.v3.Wasm
    config:
      name: "sample_envoy_filter"
      root_id: "sample_envoy_filter"
      vm_config:
        vm_id: sample_envoy_filter
        runtime: "envoy.wasm.runtime.v8"
        code:
          local:
            filename: "/etc/filter.wasm" # Here!
```

----
<!--
_class: normal
-->

# WASM's interface

- WASM can:
  - *export* its functions to outer libraries (as a normal sharedlibs)
  - *import* functions from outer world

----
<!--
_class: normal
-->

# How to import and export function

```
# rk2024.rb
def main(arg)
  answer = arg + 42
  show_answer(answer)
end
```

```
# rk2024.export.rbs
def main: (Integer) -> void
```

```
# rk2024.import.rbs
def show_answer: (Integer) -> void
```

----
<!--
_class: normal
-->

# Import this in browser

```
// Will be imvoked via main()
function show_answer(ans) {
  console.log("answer = ", ans);
}
// Specify what func to import
const importObject = {
  env: {show_answer: show_answer}
};
WebAssembly.instantiateStreaming(fetch("./rk2024.wasm"), importObject).then(
  (obj) => {
    // Call exported main() after load, with arg 21
    obj.instance.exports.main(21);
  },
);
```

----
<!--
_class: normal
-->

# The result:

![w:600 h:300](./dummy-image.png)

----
<!--
_class: hero
-->

# One more step into WebAssembly

----
<!--
_class: normal
-->

# WebAssembly is a binary with laid-out info

----
<!--
_class: hero
-->

# More topics on WASM

# WASI (in preview1)

# Component Models

----
<!--
_class: normal
-->

# WebAssembly is...

----

<!--
_class: normal2
style: section.normal2 h2 + ul { top: 66%; }
-- >

# But for mruby?

- I created yet another ruby for wasm...
- Named "mruby/edge"

## You should have 2 Questions...

- Why "yet another" wasm ruby?
- Why and How is it "mruby"?

----
<!--
_class: normal
-- >

# Here's Code

```ruby
def fib(n)
  case n
  when 0
    return 0
  when 1..2
    return 1
  else
    return fib(n-1) + fib(n-2)
  end
end
```

----
<!--
_class: normal
-- >

# Here's the Image, Niñas

- Here is the desc
- Also desc

![w:400](./dummy-image.png)

----
<!--
_class: normal
-- >

# Here's the Image #2, Niños

- Here is the desc
- Also desc

![w:600 h:360](./dummy-image.png)

----
<!--
_class: hero
_backgroundImage: url(./rubykaigi2024-bgs-whiteback.png)
-- >

# My first slide

----
<!--
_class: hero
_backgroundImage: url(./rubykaigi2024-bgs-yellowback.png)
-->

# My first slide v2
