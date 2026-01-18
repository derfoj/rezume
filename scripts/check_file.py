import os

path = r"c:\Users\andyl\OneDrive\Desktop\Coding_for_AI\reZume\frontend\src\assets\the_marc_aurel.png"
if os.path.exists(path):
    print(f"File exists: {path}")
else:
    print(f"File NOT found: {path}")
