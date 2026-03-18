import os
import shutil

shutil.move("a.txt", "test/a.txt")

shutil.copy("a.txt", "copy_a.txt")
shutil.copy2("a.txt", "copy2_a.txt")

os.rename("copy_a.txt", "renamed.txt")

os.remove("renamed.txt")
shutil.rmtree("test")
