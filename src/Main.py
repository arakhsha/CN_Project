from src.Peer import Peer

if __name__ == "__main__":
    side = input()
    if side == '1':
        server = Peer("127.000.000.001", 20007, is_root=True)
        server.run()
    else:
        client = Peer("127.000.000.001", 10007, is_root=False, root_address=("127.000.000.001", 20007))
        client.run()
