import tkinter as tk
from gui import Application

def main():
    """
    Initializes and runs the main application window.
    It tries to load a dark theme using ttkthemes, but if the module
    is not found, it falls back to the standard tkinter window to
    prevent crashing.
    """
    try:
        # Attempt to import and use the dark theme
        from ttkthemes import ThemedTk
        root = ThemedTk(theme="equilux")
    except ImportError:
        # If ttkthemes is not found, create a standard Tk window
        print("ttkthemes not found. Falling back to the default theme.")
        root = tk.Tk()

    app = Application(master=root)
    app.mainloop()

if __name__ == '__main__':
    main()
