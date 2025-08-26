typedef int (*volatile FuncT)(int);

int fib(int n) {
  if (n <= 1)
    return n;
  return fib(n - 1) + fib(n - 2);
}

int main() {
  FuncT f = fib;

  return f(13);
}
