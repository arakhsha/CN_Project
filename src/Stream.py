from src.tools.simpletcp.tcpserver import TCPServer

from src.tools.Node import Node
import threading


class Stream:

    def __init__(self, ip, port):
        """
        The Stream object constructor.

        Code design suggestion:
            1. Make a separate Thread for your TCPServer and start immediately.


        :param ip: 15 characters
        :param port: 5 characters
        """

        self.nodes = []
        self.ip = Node.parse_ip(ip)
        self.port = port

        self._server_in_buf = b''

        def callback(address, queue, data):
            """
            The callback function will run when a new data received from server_buffer.

            :param address: Source address.
            :param queue: Response queue.
            :param data: The data received from the socket.
            :return:
            """
            queue.put(bytes('ACK', 'utf8'))
            if type(data) == bytes:
                self._server_in_buf += data
            elif type(data) == str:
                self._server_in_buf += bytes(data, "UTF-8")
            # print("Data Received, New Buffer:", self.read_in_buf())

        self.tcpserver = TCPServer(self.ip, self.port, callback)

        def run_sever():
            # print("TCPServer Started")
            self.tcpserver.run()

        server_thread = threading.Thread(target=run_sever, daemon=True)
        server_thread.start()

    def get_server_address(self):
        """

        :return: Our TCPServer address
        :rtype: tuple
        """
        return self.ip, self.port

    def clear_in_buff(self):
        """
        Discard any data in TCPServer input buffer.

        :return:
        """
        self._server_in_buf.clear()

    def add_node(self, server_address, set_register_connection=False):
        """
        Will add new a node to our Stream.

        :param server_address: New node TCPServer address.
        :param set_register_connection: Shows that is this connection a register_connection or not.

        :type server_address: tuple
        :type set_register_connection: bool

        :return:
        """
        for node in self.nodes:
            if node.is_register == set_register_connection and node.get_server_address() == server_address:
                return
        node = Node(server_address, set_root=False, set_register=set_register_connection)
        self.nodes.append(node)
        pass

    def remove_node(self, node):
        """
        Remove the node from our Stream.

        Warnings:
            1. Close the node after deletion.

        :param node: The node we want to remove.
        :type node: Node

        :return:
        """
        if node in self.nodes:
            self.nodes.remove(node)
            node.close()

    def get_node_by_server(self, ip, port, only_not_registers=False):
        """

        Will find the node that has IP/Port address of input.

        Warnings:
            1. Before comparing the address parse it to a standard format with Node.parse_### functions.

        :param ip: input address IP
        :param port: input address Port

        :return: The node that input address.
        :rtype: Node
        """
        for node in self.nodes:
            if node.get_server_address() == (ip, port):
                if not (node.is_register and only_not_registers):
                    return node
        return None

    def add_message_to_out_buff(self, address, message):
        """
        In this function, we will add the message to the output buffer of the node that has the input address.
        Later we should use send_out_buf_messages to send these buffers into their sockets.

        :param address: Node address that we want to send the message
        :param message: Message we want to send

        Warnings:
            1. Check whether the node address is in our nodes or not.

        :return:
        """
        node = self.get_node_by_server(address[0], address[1])
        if node is not None:
            node.add_message_to_out_buff(message)
        else:
            raise ValueError("Node not in Stream")

    def read_in_buf(self):
        """
        Only returns the input buffer of our TCPServer.

        :return: TCPServer input buffer.
        :rtype: bytearray
        """
        return self._server_in_buf

    def send_messages_to_node(self, node):
        """
        Send buffered messages to the 'node'

        Warnings:
            1. Insert an exception handler here; Maybe the node socket you want to send the message has turned off and
            you need to remove this node from stream nodes.

        :param node:
        :type node Node

        :return:
        """
        node.send_message()

    def send_out_buf_messages(self, only_register=False):
        """
        In this function, we will send hole out buffers to their own clients.

        :return:
        """
        for node in self.nodes:
            if node.is_register or (not only_register):
                node.send_message()

    def delete_buffer(self, length):
        self._server_in_buf = self._server_in_buf[length:]

    def get_nodes(self):
        return self.nodes


if __name__ == "__main__":
    side = input()
    if side == "1":
        stream1 = Stream("127.000.000.001", 10007)
        # print("TCPServer Started")
        input()
        stream1.add_node(("127.000.000.001", 20007))
        stream1.add_message_to_out_buff(("127.000.000.001", 20007), b"\xaa\xbb")
        stream1.send_out_buf_messages()

        stream1.add_message_to_out_buff(("127.000.000.001", 20007), b"\xcc\xdd")
        stream1.send_out_buf_messages()

        stream1.add_message_to_out_buff(("127.000.000.001", 20007), b"\xee\xff")
        stream1.send_out_buf_messages()
    elif side == "3":
        stream1 = Stream("127.000.000.001", 30007)
        # print("TCPServer Started")
        input()
        stream1.add_node(("127.000.000.001", 20007))
        stream1.add_message_to_out_buff(("127.000.000.001", 20007), b"\x11\x22")
        stream1.send_out_buf_messages()

        stream1.add_message_to_out_buff(("127.000.000.001", 20007), b"\x33\x44")
        stream1.send_out_buf_messages()

        stream1.add_message_to_out_buff(("127.000.000.001", 20007), b"\x55\66")
        stream1.send_out_buf_messages()
    else:
        stream2 = Stream("127.000.000.001", 20007)
        while True:
            pass




