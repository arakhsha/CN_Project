from src.Stream import Stream
from src.Packet import Packet, PacketFactory
from src.Type import Type
from src.UserInterface import UserInterface
from src.tools.Node import Node
from src.tools.SemiNode import SemiNode
from src.tools.NetworkGraph import NetworkGraph, GraphNode
import time
import threading

"""
    Peer is our main object in this project.
    In this network Peers will connect together to make a tree graph.
    This network is not completely decentralised but will show you some real-world challenges in Peer to Peer networks.
    
"""


class Peer:

    SEND_REUNION_INTERVAL = 4
    REUNION_BACK_TIMEOUT = 4 + 2 * (8 * 2.5) + 2
    def __init__(self, server_ip, server_port, is_root=False, root_address=None):
        """
        The Peer object constructor.

        Code design suggestions:
            1. Initialise a Stream object for our Peer.
            2. Initialise a PacketFactory object.
            3. Initialise our UserInterface for interaction with user commandline.
            4. Initialise a Thread for handling reunion daemon.

        Warnings:
            1. For root Peer, we need a NetworkGraph object.
            2. In root Peer, start reunion daemon as soon as possible.
            3. In client Peer, we need to connect to the root of the network, Don't forget to set this connection
               as a register_connection.


        :param server_ip: Server IP address for this Peer that should be pass to Stream.
        :param server_port: Server Port address for this Peer that should be pass to Stream.
        :param is_root: Specify that is this Peer root or not.
        :param root_address: Root IP/Port address if we are a client.

        :type server_ip: str
        :type server_port: int
        :type is_root: bool
        :type root_address: tuple
        """
        self.ip = Node.parse_ip(server_ip)
        self.port = server_port
        self.stream = Stream(server_ip, server_port)
        self.packet_factory = PacketFactory()

        self.interface = UserInterface()
        self.interface.setDaemon(True)
        self.parse_interface_thread = threading.Thread(target=self.handle_user_interface_buffer, daemon=True)

        self.is_root = is_root
        self.root_address = root_address
        self.reunion_daemon = threading.Thread(target=self.run_reunion_daemon, daemon=True)
        if is_root:
            root_node = GraphNode((server_port, server_ip))
            self.network_graph = NetworkGraph(root_node)

        if not is_root:
            self.stream.add_node(root_address, True)
            self.father_address = None
            self.send_reunion_timer = 4
            self.last_reunion_back = 0
            self.is_alive = False

    def start_user_interface(self):
        """
        For starting UserInterface thread.

        :return:
        """
        self.interface.start()
        self.parse_interface_thread.start()

    def handle_user_interface_buffer(self):
        """
        In every interval, we should parse user command that buffered from our UserInterface.
        All of the valid commands are listed below:
            1. Register:  With this command, the client send a Register Request packet to the root of the network.
            2. Advertise: Send an Advertise Request to the root of the network for finding first hope.
            3. SendMessage: The following string will be added to a new Message packet and broadcast through the network.

        Warnings:
            1. Ignore irregular commands from the user.
            2. Don't forget to clear our UserInterface buffer.
        :return:
        """
        while True:
            while len(self.interface.buffer) > 0:
                args = self.interface.buffer[0].split()
                command = args[0]
                self.interface.buffer = self.interface.buffer[1:]
                if command.lower() == "register":
                    self.register()
                elif command.lower() == "advertise":
                    self.advertise()
                elif command.lower() == "sendmessage":
                    if len(args) >= 1:
                        self.send_message(args[1])
            time.sleep(0.1)

    def run(self):
        """
        The main loop of the program.

        Code design suggestions:
            1. Parse server in_buf of the stream.
            2. Handle all packets were received from our Stream server.
            3. Parse user_interface_buffer to make message packets.
            4. Send packets stored in nodes buffer of our Stream object.
            5. ** sleep the current thread for 2 seconds **

        Warnings:
            1. At first check reunion daemon condition; Maybe we have a problem in this time
               and so we should hold any actions until Reunion acceptance.
            2. In every situation checkout Advertise Response packets; even is Reunion in failure mode or not

        :return:
        """
        self.start_user_interface()
        self.reunion_daemon.start()
        # TODO Warning 1?
        while True:
            packet = self.parse_in_buf()
            while packet is not None:
                self.handle_packet(packet)
                packet = self.parse_in_buf()
            self.stream.send_out_buf_messages()
            time.sleep(2)


    def run_reunion_daemon(self):
        """

        In this function, we will handle all Reunion actions.

        Code design suggestions:
            1. Check if we are the network root or not; The actions are identical.
            2. If it's the root Peer, in every interval check the latest Reunion packet arrival time from every node;
               If time is over for the node turn it off (Maybe you need to remove it from our NetworkGraph).
            3. If it's a non-root peer split the actions by considering whether we are waiting for Reunion Hello Back
               Packet or it's the time to send new Reunion Hello packet.

        Warnings:
            1. If we are the root of the network in the situation that we want to turn a node off, make sure that you will not
               advertise the nodes sub-tree in our GraphNode.
            2. If we are a non-root Peer, save the time when you have sent your last Reunion Hello packet; You need this
               time for checking whether the Reunion was failed or not.
            3. For choosing time intervals you should wait until Reunion Hello or Reunion Hello Back arrival,
               pay attention that our NetworkGraph depth will not be bigger than 8. (Do not forget main loop sleep time)
            4. Suppose that you are a non-root Peer and Reunion was failed, In this time you should make a new Advertise
               Request packet and send it through your register_connection to the root; Don't forget to send this packet
               here, because in the Reunion Failure mode our main loop will not work properly and everything will be got stock!

        :return:
        """
        interval = 0.1
        if self.is_root:
            while True:
                self.network_graph.remove_all_expired_nodes()
                time.sleep(interval)
        else:
            while True:
                self.send_reunion_timer -= interval
                if self.send_reunion_timer <= 0 and self.is_alive:
                    self.send_reunion()
                    self.send_reunion_timer = Peer.SEND_REUNION_INTERVAL
                if time.time() - self.last_reunion_back > Peer.REUNION_BACK_TIMEOUT and self.is_alive:
                    self.timeout()
                time.sleep(interval)


    def send_broadcast_packet(self, broadcast_packet):
        """

        For setting broadcast packets buffer into Nodes out_buff.

        Warnings:
            1. Don't send Message packets through register_connections.

        :param broadcast_packet: The packet that should be broadcast through the network.
        :type broadcast_packet: Packet

        :return:
        """
        pass

    def handle_packet(self, packet):
        """

        This function act as a wrapper for other handle_###_packet methods to handle the packet.

        Code design suggestion:
            1. It's better to check packet validation right now; For example Validation of the packet length.

        :param packet: The arrived packet that should be handled.

        :type packet Packet

        """
        # print("A New Packet Received!")
        # print("Header: ", packet.get_header())
        # print("Body: ", packet.get_body())

        # TODO: packet validation

        if packet.get_type() == Type.register:
            self.__handle_register_packet(packet)
        elif packet.get_type() == Type.advertise:
            self.__handle_advertise_packet(packet)
        elif packet.get_type() == Type.join:
            self.__handle_join_packet(packet)
        elif packet.get_type() == Type.message:
            self.__handle_message_packet(packet)
        elif packet.get_type() == Type.reunion:
            self.__handle_reunion_packet(packet)

    def __check_registered(self, source_address):
        """
        If the Peer is the root of the network we need to find that is a node registered or not.

        :param source_address: Unknown IP/Port address.
        :type source_address: tuple

        :return:
        """
        # TODO: ba rakhsha check konam
        return self.network_graph.is_registered(source_address)

    def __handle_advertise_packet(self, packet):
        """
        For advertising peers in the network, It is peer discovery message.

        Request:
            We should act as the root of the network and reply with a neighbour address in a new Advertise Response packet.

        Response:
            When an Advertise Response packet type arrived we should update our parent peer and send a Join packet to the
            new parent.

        Code design suggestion:
            1. Start the Reunion daemon thread when the first Advertise Response packet received.
            2. When an Advertise Response message arrived, make a new Join packet immediately for the advertised address.

        Warnings:
            1. Don't forget to ignore Advertise Request packets when you are a non-root peer.
            2. The addresses which still haven't registered to the network can not request any peer discovery message.
            3. Maybe it's not the first time that the source of the packet sends Advertise Request message. This will happen
               in rare situations like Reunion Failure. Pay attention, don't advertise the address to the packet sender
               sub-tree.
            4. When an Advertise Response packet arrived update our Peer parent for sending Reunion Packets.

        :param packet: Arrived register packet

        :type packet Packet

        :return:
        """
        pass

    def __handle_register_packet(self, packet):
        """
        For registration a new node to the network at first we should make a Node with stream.add_node for'sender' and
        save it.

        Code design suggestion:
            1.For checking whether an address is registered since now or not you can use SemiNode object except Node.

        Warnings:
            1. Don't forget to ignore Register Request packets when you are a non-root peer.

        :param packet: Arrived register packet
        :type packet Packet
        :return:
        """
        body = packet.get_body()
        type = body[0:3]
        if type == "REQ" and self.is_root:
            ip = body[3:18]
            port = int(body[18:23])
            print("Registering ", ip, port)
            # TODO Graph Checks and operations
            self.stream.add_node((ip, port), set_register_connection=True)
            res = self.packet_factory.new_register_packet("RES", (self.ip, self.port))
            self.stream.add_message_to_out_buff((ip, port), res.get_buf())
        elif type == "RES" and (not self.is_root):
            if body[3:6] == "ACK":
                print("Register ACKed")

    def __check_neighbour(self, address):
        """
        It checks is the address in our neighbours array or not.

        :param address: Unknown address

        :type address: tuple

        :return: Whether is address in our neighbours or not.
        :rtype: bool
        """
        pass

    def __handle_message_packet(self, packet):
        """
        Only broadcast message to the other nodes.

        Warnings:
            1. Do not forget to ignore messages from unknown sources.
            2. Make sure that you are not sending a message to a register_connection.

        :param packet: Arrived message packet

        :type packet Packet

        :return:
        """
        pass

    def __handle_reunion_packet(self, packet):
        """
        In this function we should handle Reunion packet was just arrived.

        Reunion Hello:
            If you are root Peer you should answer with a new Reunion Hello Back packet.
            At first extract all addresses in the packet body and append them in descending order to the new packet.
            You should send the new packet to the first address in the arrived packet.
            If you are a non-root Peer append your IP/Port address to the end of the packet and send it to your parent.

        Reunion Hello Back:
            Check that you are the end node or not; If not only remove your IP/Port address and send the packet to the next
            address, otherwise you received your response from the root and everything is fine.

        Warnings:
            1. Every time adding or removing an address from packet don't forget to update Entity Number field.
            2. If you are the root, update last Reunion Hello arrival packet from the sender node and turn it on.
            3. If you are the end node, update your Reunion mode from pending to acceptance.


        :param packet: Arrived reunion packet
        :return:
        """
        body = packet.get_body()
        type = body[0:3]
        number_of_entries = int(body[3:5])
        entries = []
        for i in range(number_of_entries):
            entry_ip = body[5 + i * 20: 5 + i * 20 + 15]
            entry_port = int(body[5 + i * 20 + 15: 5 + i * 20 + 20])
            entries.append((entry_ip, entry_port))
        if number_of_entries < 1:
            print("Warning: Invalid Reunion Packet")
            return
        if type == "REQ":
            if self.is_root:
                self.network_graph.update_latest_reunion_time(entries[0])
                first_hop = entries[-1]
                entries.reverse()
                res = self.packet_factory.new_reunion_packet("RES", (self.ip, self.port), entries)
                self.stream.add_message_to_out_buff(first_hop, res.get_buf())
            else:
                if not self.is_alive:
                    return
                entries.append((self.ip, self.port))
                res = self.packet_factory.new_reunion_packet("REQ", (self.ip, self.port), entries)
                self.stream.add_message_to_out_buff(self.father_address, res.get_buf())

        if type == "RES":
            if self.is_root:
                print("Warning: Invalid Reunion Packet")
                return
            if (self.ip, self.port) == entries[0]:
                self.last_reunion_back = time.time()
                return
            if (self.ip, self.port) != entries[-1]:
                print("Warning: Invalid Reunion Packet")
                return
            entries = entries[0:-1]
            next_hop = entries[-1]
            res = self.packet_factory.new_reunion_packet("RES", (self.ip, self.port), entries)
            self.stream.add_message_to_out_buff(next_hop, res.get_buf())






    def __handle_join_packet(self, packet):
        """
        When a Join packet received we should add a new node to our nodes array.
        In reality, there is a security level that forbids joining every node to our network.

        :param packet: Arrived register packet.


        :type packet Packet

        :return:
        """
        new_address = packet.get_source_server_address()
        self.stream.add_node(new_address, set_register_connection=False)

    def __get_neighbour(self, sender):
        """
        Finds the best neighbour for the 'sender' from the network_nodes array.
        This function only will call when you are a root peer.

        Code design suggestion:
            1. Use your NetworkGraph find_live_node to find the best neighbour.

        :param sender: Sender of the packet
        :return: The specified neighbour for the sender; The format is like ('192.168.001.001', '05335').
        """
        return self.network_graph.find_parent_and_assign(sender[0], sender[1])

    def parse_in_buf(self):
        buffer = self.stream.read_in_buf()
        header_size = 20
        if len(buffer) < header_size:
            return None

        packet = Packet(buf=buffer)
        packet_length = packet.get_length()
        if len(buffer) < packet_length:
            return None
        packet = Packet(buf=buffer[0:packet_length])
        self.stream.delete_buffer(packet_length)
        return packet

    def register(self):
        print("Register Command!")
        if self.is_root:
            return
        req = self.packet_factory.new_register_packet("REQ", (self.ip, self.port), (self.ip, self.port))
        self.stream.add_message_to_out_buff(self.root_address, req.get_buf())

    def advertise(self):
        print("Advertisement Command!")
        pass

    def send_message(self, message):
        print("Message Command! Message:", message)
        pass

    def send_reunion(self):
        reunion_packet = self.packet_factory.new_reunion_packet("REQ", (self.ip, self.port), [(self.ip, self.port)])
        self.stream.add_message_to_out_buff(self.father_address, reunion_packet.get_buf())

    def timeout(self):
        self.is_alive = False
        self.advertise()
