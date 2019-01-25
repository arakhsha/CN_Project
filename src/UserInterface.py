import threading
import time


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

