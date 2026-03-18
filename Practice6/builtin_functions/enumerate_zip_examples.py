names = ["a", "b", "c"]
nums = [1, 2, 3]

for i, val in enumerate(names):
    print(i, val)

for n, v in zip(names, nums):
    print(n, v)

print(list(zip(names, nums)))
