from tkinter import *
from tkinter import simpledialog
from src.Peer import Peer
from tkinter import ttk

if __name__ == "__main__":
    def root(event=None):  # event is passed by binders.
        port = simpledialog.askinteger("Input", "Server Port?",
                                       parent=top,
                                       minvalue=0, maxvalue=65535)
        if port is None:
            return
        top.destroy()
        server = Peer("127.000.000.001", port, is_root=True, gui=True)
        server.run()

    def client(event=None):
        server_port = simpledialog.askinteger("Input", "Root Port?",
                                       parent=top,
                                       minvalue=0, maxvalue=65535)
        if server_port is None:
            return
        port = simpledialog.askinteger("Input", "Server Port?",
                                       parent=top,
                                       minvalue=0, maxvalue=65535)
        if port is None:
            return
        top.destroy()
        client = Peer("127.000.000.001", port, is_root=False, root_address=("127.000.000.001", server_port), gui=True)
        client.run()

    top = Tk()
    top.title("P2P App")
    top.geometry("200x100")

    choose_text = ttk.Label(top, text="Choose your application:")
    choose_text.pack()
    root_button = ttk.Button(top, text="Root", command=root)
    root_button.pack(side=LEFT)
    client_button = ttk.Button(top, text="Client", command=client)
    client_button.pack(side=RIGHT)
    mainloop()
