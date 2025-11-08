import tkinter as tk
from gui import Application

def main():
    """
    Initializes and runs the main application window.
    """
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

if __name__ == '__main__':
    main()
