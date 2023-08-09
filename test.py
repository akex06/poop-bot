

class A:
    nn: int

    def __init__(self, n: int):
        A.nn = n

a = A(1)
print(a.nn)