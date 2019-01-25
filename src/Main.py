from src.Peer import Peer

if __name__ == "__main__":
    side = input()
    if side == '1':
        port = int(input("port:"))
        server = Peer("127.000.000.001", port, is_root=True)
        server.run()
    else:
        server_port = int(input("server port:"))
        port = int(input("port:"))
        client = Peer("127.000.000.001", port, is_root=False, root_address=("127.000.000.001", server_port))
        client.run()
