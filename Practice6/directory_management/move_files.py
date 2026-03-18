import os
import shutil

# перемещение
shutil.move("a.txt", "test/a.txt")

# копирование
shutil.copy("a.txt", "copy_a.txt")
shutil.copy2("a.txt", "copy2_a.txt")

# переименование
os.rename("copy_a.txt", "renamed.txt")

# удаление
os.remove("renamed.txt")
shutil.rmtree("test")
