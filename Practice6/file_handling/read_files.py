f = open("demofile.txt")
print(f.read()) 

with open("demofile.txt") as f:
  print(f.readline())
  print(f.readline())

f = open("demofile.txt")
print(f.readline())
f.close()