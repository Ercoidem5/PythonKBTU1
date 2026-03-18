import os
path = "newdir"
os.mkdir(path)
os.makedirs(path, exist_ok=True)

os.listdir(path)

path2 = "newdir2"
os.chdir(path2)
os.rmdir(path2)


os.path.isdir(path)

