from src.Peer import Peer

if __name__ == "__main__":
    side = input()
    port = int(input("port:"))
    if side == '1':
        server = Peer("127.000.000.001", port, is_root=True)
        server.run()
    else:
        server_port = int(input("server port:"))
        client = Peer("127.000.000.001", port, is_root=False, root_address=("127.000.000.001", server_port))
        client.run()
