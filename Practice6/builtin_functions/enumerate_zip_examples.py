names = ["a", "b", "c"]
nums = [1, 2, 3]

# enumerate
for i, val in enumerate(names):
    print(i, val)

# zip
for n, v in zip(names, nums):
    print(n, v)

# zip в список
print(list(zip(names, nums)))
