# Checkoff 3: Python Libraries Implemented in C

*How NumPy and Python-to-C calls move heavy computation out of the Python interpreter.*

## Topic

Python is easy to write but known to be slow for number crunching. For this checkoff I wanted to find out **how slow, and why**, by timing one simple job three ways:

1. **Pure Python loop**: add two lists one element at a time.
2. **NumPy**: `a + b` on two NumPy arrays.
3. **Hand-written C**: a C function (`add.c`), compiled into a shared library (`libadd.so`) and called from Python with `ctypes`.

The job is element-wise addition of two arrays of 64-bit integers, at sizes from 10,000 up to 10,000,000 elements.

## What I Explored

- **How Python stores numbers.** A Python `int` is a full object on the heap with a type pointer, a reference count and the value. A list holds pointers to those objects. Every `a[i] + b[i]` has to look up the type, dispatch the `+` operation, and allocate a brand-new int object for the result.
- **How C stores numbers.** In C, `long long *a` points to a block of raw 8-byte integers sitting next to each other in memory. The loop in `add.c` compiles to a few machine instructions per element, with no type checks and no allocation.
- **Calling C from Python.** `ctypes` loads a compiled `.so` file and lets Python call its functions directly. `numpy.ctypeslib.ndpointer` passes a NumPy array's underlying memory buffer to C as a `long long *`, so nothing is copied.
- **Where NumPy fits.** NumPy arrays store numerical values in typed data buffers, often in contiguous memory, and operations like `a + b` run in precompiled C loops inside NumPy. So NumPy gives you C-like speed while you keep writing Python.
- **Benchmarking properly.** Each version is run several times and the *best* time is kept, using `time.perf_counter()`, so that one-off noise (other programs, cache warm-up) doesn't skew the result. The script also checks that the C output matches NumPy's (`assert (out == a + b).all()`), so we know the fast version is actually correct.

## Results

Results at **10 million elements** from `python3 benchmark.py` (best of 5 runs; best of 3 for the Python loop):

| Version       | Time (s) | Compared with C |
|---------------|----------|-----------------|
| Python loop   | 0.525    | ~33× slower     |
| NumPy `a + b` | 0.0212   | ~1.3× slower    |
| C via ctypes  | 0.0159   | fastest         |

The script also prints results for 10⁴, 10⁵ and 10⁶ elements.

## Most Interesting Discoveries

1. **The Python loop was about 33 times slower than C and 25 times slower than NumPy.** All three versions do the same math. The difference is overhead: for every element, Python fetches object references, dispatches `+` dynamically, creates a new result object and appends it to the list. With millions of elements, that overhead outweighs the arithmetic itself.
2. **Interpreter overhead happens once per array operation, not once per element.** With NumPy or the C function, Python makes one call and the whole element loop runs in native code. That is the main idea behind Python libraries implemented in C: Python is the interface and C is the engine.
3. **My C code was only slightly faster than NumPy (about 25%).** NumPy's `a + b` is already a compiled C loop, so hand-written C beats it only by a little. For ordinary array math, NumPy is the practical choice.


## Code Examples

| File           | Description |
|----------------|-------------|
| `add.c`        | C function `add_arrays(a, b, out, n)` that computes `out[i] = a[i] + b[i]` |
| `libadd.so`    | `add.c` compiled as a shared library (Linux x86-64) |
| `benchmark.py` | Loads `libadd.so` with `ctypes`, times all three versions at four array sizes, and checks the results match |

### How to Run

Requirements: Linux, macOS or WSL with `gcc` and Python 3 with NumPy.

```bash
# 1. Install NumPy (if needed)
pip install numpy

# 2. Compile the C code into a shared library
gcc -O2 -shared -fPIC -o libadd.so add.c

# 3. Run the benchmark (from this folder, since it loads ./libadd.so)
python3 benchmark.py
```

The included `libadd.so` is a Linux binary. On macOS, or if it fails to load, recompile it with step 2. On Windows, use WSL, or build a DLL (`gcc -O2 -shared -o libadd.dll add.c`) and change the `CDLL` path in `benchmark.py`.


## Presentation Materials

My presentation slides are in [`Python Libraries Implemented in C.pptx`](Python%20Libraries%20Implemented%20in%20C.pptx). Open the file in PowerPoint, Google Slides or Keynote.

The slides cover:
1. Python can hand off the expensive part to compiled code
2. Why a Python loop costs more (fetch, dispatch, create, append for every element)
3. A NumPy array is more like a C array (typed data buffer vs. separate Python objects)
4. Performance comparison at 10 million elements
5. What happens behind the scenes in Python, NumPy and C
6. Why use C extensions (performance, memory, reuse)

## Additional Resources

- Python docs: [`ctypes`, a foreign function library for Python](https://docs.python.org/3/library/ctypes.html)
- NumPy docs: [`numpy.ctypeslib`, using NumPy with ctypes](https://numpy.org/doc/stable/reference/routines.ctypeslib.html)
- NumPy docs: [What is NumPy? (why it's fast: vectorization)](https://numpy.org/doc/stable/user/whatisnumpy.html)
- Python docs: [`time.perf_counter`](https://docs.python.org/3/library/time.html#time.perf_counter)
- Jake VanderPlas: [Why Python is Slow: Looking Under the Hood](https://jakevdp.github.io/blog/2014/05/09/why-python-is-slow/)
- GCC manual: [Options That Control Optimization](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html)
- Course materials for COMP 211 (C, pointers and memory layout)
#