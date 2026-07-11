import tkinter as tk
import tkinter.messagebox as msgbox
from tkinter import *
#!/usr/bin/python
# -*- coding: UTF-8 -*-
top = tk.Tk()
CheckVar1 = IntVar()
CheckVar2 = IntVar()
cv = Canvas(top,bg = 'white',height=300,width=400)
C1 = Checkbutton(
    top,
    activebackground='yellow',
    text="吃饭",
    width=30,
    bg='white'
)
C1.pack()
cv.pack()
top.mainloop()