import ctypes, time
import numpy as np
from numpy.ctypeslib import ndpointer

lib = ctypes.CDLL("./libadd.so")
i64 = ndpointer(dtype=np.int64, flags="C_CONTIGUOUS")
lib.add_arrays.argtypes = [i64, i64, i64, ctypes.c_longlong]
lib.add_arrays.restype = None

def py_loop(a, b):
    result = []
    for i in range(len(a)):
        result.append(a[i] + b[i])
    return result

def bench(f, *args, runs=5):
    best = float("inf")
    for _ in range(runs):
        t = time.perf_counter()
        f(*args)
        best = min(best, time.perf_counter() - t)
    return best

for n in (10**4, 10**5, 10**6, 10**7):
    a = np.arange(n, dtype=np.int64)
    b = np.arange(n, dtype=np.int64)
    la, lb = a.tolist(), b.tolist()
    out = np.empty(n, dtype=np.int64)

    t_py = bench(py_loop, la, lb, runs=3)
    t_np = bench(lambda: a + b)
    t_c = bench(lib.add_arrays, a, b, out, n)

    assert (out == a + b).all()
    print(f"n={n:>10,}  python={t_py:.4f}s  numpy={t_np:.5f}s  c={t_c:.5f}s")
