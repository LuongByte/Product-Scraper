from gui import App
from ttkbootstrap import Window

if __name__ == "__main__":
    base = Window(themename="darkly")  
    app = App(base)
    base.mainloop()