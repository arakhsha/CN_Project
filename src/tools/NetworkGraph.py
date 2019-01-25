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
        self.latest_reunion_time = None
        self.is_root = False
        pass

    def set_parent(self, parent):
        self.parent = parent
        self.alive = True
        for child in self.children:
            child.alive = True
        self.latest_reunion_time = time.time() + 8
        pass

    def set_address(self, new_address):
        self.ip = new_address[0]
        self.port = new_address[1]
        pass

    def get_address(self):
        return self.ip, self.port

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
            subtree += child.get_subtree()
        return subtree

    def is_full(self):
        return len(self.children) >= 2

    def is_available(self):
        return (not self.is_full()) and self.alive

    def remove_from_parent(self):
        self.parent.remove_child(self)

    def remove_child(self, child):
        self.children.remove(child)

    def print_summary(self):
        print("ip/port:", self.ip, "/", str(self.port), "alive:", self.alive)
        if self.parent is not None:
            print("parent:", self.parent.ip + "/" + str(self.parent.port))
        else:
            print("parent: None")
        print("children:")
        for child in self.children:
            print(child.ip + "/" + str(child.port))
        print("last update:", self.latest_reunion_time)
        print("depth:", self.depth())

    def update_latest_reunion_time(self):
        self.latest_reunion_time = time.time()

    def is_expired(self):
        if self.is_root:
            return False
        return (time.time() - self.latest_reunion_time) <= self.expiration_time()

    def expiration_time(self):
        if self.depth() >= 0:
            return self.depth() * 2.5 + 4
        else:
            return 2.5 * 8 + 4

    def depth(self):
        if self.is_root:
            return 0
        if self.parent is None:
            return -1
        if self.parent.depth() == -1:
            return -1
        return self.parent.depth() + 1


class NetworkGraph:
    def __init__(self, root):
        self.root = root
        root.alive = True
        root.is_root = True
        self.nodes = [root]

    def find_parent(self, sender):
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
            while not bfs_queue.empty():
                head = bfs_queue.get()
                if head.is_available() and (sender_node.parent is not head):
                    return head
                for child in head.children:
                    if child is not sender_node:
                        bfs_queue.put(child)
            return None

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
        when a node becomes disabled that node becomes dead and removed from it's parent
        and all of its subtree nodes become dead too
        :param node_address:
        :return:
        """
        node = self.find_node(node_address[0], node_address[1])
        if node is None:
            raise ValueError
        else:
            for child_node in node.get_subtree():
                child_node.set_dead()

            node.remove_from_parent()
            node.parent = None
            node.set_dead()
            # self.nodes.remove(node)
        pass

    def register_node(self, ip, port):
        if self.find_node(ip, port) is None:
            new_node = GraphNode((ip, port))
            self.nodes.append(new_node)
        pass

    def assign_parent(self, ip, port, father_address):
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
        node = self.find_node(ip, port)
        parent_node = self.find_node(father_address[0], father_address[1])

        if node is None:
            raise ValueError("Node is not registered")

        if parent_node is None:
            raise ValueError("Parent Node is not registered")

        if node.parent is not None:
            # TODO: we still don't know what to do in this case
            parent_node.remove_child(node)
            pass

        # add to child
        node.set_parent(parent_node)
        # add to parent
        parent_node.add_child(node)
        pass

    def find_parent_and_assign(self, ip, port):
        parent = self.find_parent((ip, port))
        if parent is None:
            return None
        try:
            self.assign_parent(ip, port, parent.get_address())
        except ValueError as e:
            print(repr(e), ip, "/", port)
            return None
        return parent.get_address()

    def print_all(self):
        for node in self.nodes:
            node.print_summary()
            print("\n")

    def is_registered(self, peer_address):
        for node in self.nodes:
            ip, port = node.get_address()
            if ip == peer_address[0] and port == peer_address[1]:
                return True
        return False

    def __get_all_expired_nodes(self):
        result = []
        for node in self.nodes:
            if node.alive:
                if node.is_expired():
                    result.append(node)
        return result

    def remove_all_expired_nodes(self):
        for node in self.__get_all_expired_nodes():
            self.remove_node(node.get_address())

    def update_latest_reunion_time(self, peer_address):
        node = self.find_node(peer_address[0], peer_address[1])
        node.update_latest_reunion_time()


if __name__ == "__main__":
    root = GraphNode(("127.000.000.001", 10))
    networkGraph = NetworkGraph(root)
    while True:
        # 1. register node\n2. set father \n3. remove node \n4. show all nodes\n5. end\n"
        command = int(input(""))
        if command == 1:
            # ip:
            # port:
            ip = input("")
            port = int(input(""))
            networkGraph.register_node(ip, port)
        elif command == 2:
            # ip:
            # port:
            ip = input("")
            port = int(input(""))
            networkGraph.find_parent_and_assign(ip, port)
        elif command == 3:
            # ip:
            # port:
            ip = input("")
            port = int(input(""))
            networkGraph.remove_node((ip, port))
        elif command == 4:
            networkGraph.print_all()
        elif command == 5:
            break
