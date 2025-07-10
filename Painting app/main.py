import tkinter as tk
from paint_core import PaintApp # Import PaintApp from the new paint_core.py file

if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()
