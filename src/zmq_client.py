import asyncio
import time
import zmq
import zmq.asyncio

import threading


class ZmqClient():
    def __init__(self, sub_ip: str = None, push_ip: str = None, req_ip: str = None):
        self.zmq_context = zmq.Context()
        if sub_ip:
            self.sub_socket = self.zmq_context.socket(zmq.SUB)
            self.sub_socket.connect(sub_ip)
        if push_ip:
            self.push_socket = self.zmq_context.socket(zmq.PUSH)
            self.push_socket.connect(push_ip)
        if req_ip:
            self.req_socket = self.zmq_context.socket(zmq.REQ)
            self.req_socket.connect(req_ip)

    # Pub sub
    def subscribe(self, topic):
        print(f"Subscribing: {topic}")
        self.sub_socket.subscribe(topic)

    def receive_sub(self):
        # Blocks until a message is received
        return self.sub_socket.recv_string()
    # Push pull
    def push(self, topic, data):
        print(f"Sending: {topic} {data}")
        self.push_socket.send_string(f"{topic} {data}")

    # Request reply
    def request(self, data):
        self.req_socket.send_string(data)
        return self.req_socket.recv_string()

    # Close
    def close(self):
        if hasattr(self, 'sub_socket'):
            self.sub_socket.close()
        if hasattr(self, 'push_socket'):
            self.push_socket.close()
        if hasattr(self, 'req_socket'):
            self.req_socket.close()
        self.zmq_context.term()

    # Client Management Methods
    # Threadsafe - Each can be run on a separate thread
    def read_subscriber(self):
        while True:
            msg = self.receive_sub()
            print("Received:", msg)

    def keep_alive_subscriber(self, con_id, inst_id, book_type, timeout=600):
        while True:
            self.push(con_id, f"{inst_id} {book_type}")
            time.sleep(timeout)

    def req_tob_snapshot(self, inst_id, con_id):
        while True:
            tob = self.request(f"{inst_id} {con_id}")
            print("Received tob_snapshot:", tob)
            time.sleep(5)


if __name__ == "__main__":
    client = ZmqClient("tcp://127.0.0.1:5555",
                       "tcp://127.0.0.1:5556", "tcp://127.0.0.1:5557")

    # client.subscribe("2411")
    # subscriber_read_thread = threading.Thread(
    #     target=client.read_subscriber, daemon=True)
    # subscriber_read_thread.start()

    # # Keep alive
    # keep_alive_thread = threading.Thread(target=client.keep_alive_subscriber,
    #                                      args=("589141846", "2411", "top_of_book"), daemon=True)
    # keep_alive_thread.start()

    tob_snapshot_thread = threading.Thread(target=client.req_tob_snapshot,
                                           args=("2411", "589141846"), daemon=True)
    tob_snapshot_thread.start()

    time.sleep(1000)
    client.close()
    client.zmq_context.term()
