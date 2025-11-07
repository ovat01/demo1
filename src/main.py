from ttkthemes import ThemedTk
from gui import Application

def main():
    # Use ThemedTk to create the root window with the specified theme
    # This ensures the dark theme is applied when the application is run
    # via main.py, which is the entry point for the PyInstaller executable.
    root = ThemedTk(theme="equilux")
    app = Application(master=root)
    app.mainloop()

if __name__ == '__main__':
    main()
