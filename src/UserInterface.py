import threading
import time
from tkinter import *
from tkinter import simpledialog
from tkinter import ttk


class UserInterface(threading.Thread):
    buffer = []

    def run(self):
        """
        Which the user or client sees and works with.
        This method runs every time to see whether there are new messages or not.
        """
        while True:
            message = input("Write your command:\n")
            self.buffer.append(message)


class GraphicalUserInterface(UserInterface):

    def __init__(self, is_root):
        UserInterface.__init__(self)
        self.is_root = is_root
        self.msgs = None

    def run(self):
        def register(event=None):
            self.buffer.append("register")

        def advertise(event=None):
            self.buffer.append("advertise")

        def sendmessage(event=None):
            msg = message_text.get()
            self.buffer.append("sendmessage" + " " + msg)
            message_text.set("")
            self.append_message(msg=msg)

        def show_map(event=None):
            self.buffer.append("showmap")

        top = Tk()
        top.title("P2P App")
        list1 = Listbox(top, height=6, width=35)
        self.msgs = list1
        list1.grid(row=0, column=0, rowspan=6, columnspan=2)

        sb1 = Scrollbar(top)
        sb1.grid(row=0, column=2, rowspan=6)

        list1.configure(yscrollcommand=sb1.set)
        sb1.configure(command=list1.yview)

        message_text = StringVar()
        e1 = ttk.Entry(top, textvariable=message_text)
        e1.bind("<Return>", sendmessage)
        e1.grid(row=7, column=0)

        b3 = ttk.Button(top, text="Send Message", width=12, command=sendmessage)
        b3.grid(row=8, column=0)

        if self.is_root:
            b1 = ttk.Button(top, text="ShowMap(Terminal)", width=12, command=show_map)
            b1.grid(row=0, column=4)
            pass
        else:
            b1 = ttk.Button(top, text="Register", width=12, command=register)
            b1.grid(row=0, column=4)

            b2 = ttk.Button(top, text="Advertise", width=12, command=advertise)
            b2.grid(row=1, column=4)
        mainloop()

    def append_message(self, msg):
        self.msgs.insert(END, msg)


if __name__ == "__main__":
    gui = GraphicalUserInterface(False)
    gui.run()

