from functools import reduce

nums = [1, 2, 3, 4, 5]

# map
print(list(map(lambda x: x * 2, nums)))

# filter
print(list(filter(lambda x: x % 2 == 0, nums)))

# reduce
print(reduce(lambda x, y: x + y, nums))