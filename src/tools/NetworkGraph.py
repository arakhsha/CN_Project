import queue
import time


class GraphNode:
    def __init__(self, address):
        """
        Our own understanding: port is the port which node is listening on

        :param address: (ip, port)
        :type address: tuple

        """
        self.ip = address[0]
        self.port = address[1]
        self.parent = None
        self.children = []
        self.alive = False
        pass

    def set_parent(self, parent):
        self.parent = parent
        pass

    def set_address(self, new_address):
        self.ip = new_address[0]
        self.port = new_address[1]
        pass

    def __reset(self):
        self.parent = None
        self.children = []
        pass

    def add_child(self, child):
        self.children.append(child)
        pass

    def set_alive(self):
        self.alive = True
        pass

    def set_dead(self):
        self.alive = False
        pass

    def get_subtree(self):
        subtree = []
        subtree += self.children
        for child in self.children:
            subtree += child.get_subtree
        return subtree

    def is_full(self):
        return len(self.children) >= 2

    def is_available(self):
        return (not self.is_full()) and self.alive


class NetworkGraph:
    def __init__(self, root):
        self.root = root
        root.alive = True
        self.nodes = [root]

    def find_live_node(self, sender):
        """
        Here we should find a neighbour for the sender.
        Best neighbour is the node who is nearest the root and has not more than one child.

        Code design suggestion:
            1. Do a BFS algorithm to find the target.

        Warnings:
            1. Check whether there is sender node in our NetworkGraph or not; if exist do not return sender node or
               any other nodes in it's sub-tree.

        :param sender: The node address we want to find best neighbour for it.
        :type sender: tuple

        :return: Best neighbour for sender.
        :rtype: GraphNode
        """

        sender_node = self.find_node(sender[0], sender[1])
        if sender_node is None:
            return None
        else:
            bfs_queue = queue.Queue(-1)
            bfs_queue.put(self.root)
            while not bfs_queue.Empty:
                head = bfs_queue.get()
                bfs_queue.put(head.children)
                if head.is_available():
                    return head

    def find_node(self, ip, port):
        for node in self.nodes:
            if node.ip == ip and node.port == port:
                return node
        return None

    def turn_on_node(self, node_address):
        node = self.find_node(node_address[0], node_address[1])
        if node is None:
            raise ValueError
        else:
            node.set_alive()
        pass

    def turn_off_node(self, node_address):
        node = self.find_node(node_address[0], node_address[1])
        if node is None:
            raise ValueError
        else:
            node.set_dead()
        pass

    def remove_node(self, node_address):
        """
        when a node becomes disabled that node is removed and all of its subtree nodes become dead
        :param node_address:
        :return:
        """
        node = self.find_node(node_address[0], node_address[1])
        if node is None:
            raise ValueError
        else:
            for child_node in node.get_subtree():
                child_node.set_dead()
            self.nodes.remove(node)
        pass

    def add_node(self, ip, port, father_address):
        """
        Add a new node with node_address if it does not exist in our NetworkGraph and set its father.

        Warnings:
            1. Don't forget to set the new node as one of the father_address children.
            2. Before using this function make sure that there is a node which has father_address.

        :param ip: IP address of the new node.
        :param port: Port of the new node.
        :param father_address: Father address of the new node

        :type ip: str
        :type port: int
        :type father_address: tuple


        :return:
        """
        pass
