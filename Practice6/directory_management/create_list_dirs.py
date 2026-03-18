import os
path = "newdir"
os.mkdir(path)
os.makedirs(path, exist_ok=True)

# список файлов и папок
os.listdir(path)

os.scandir(path)

os.path.exists(path)

os.path.isdir(path)

