import zmq
import time


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
        return self.sub_socket.recv_string()

    # Push pull
    def push(self, topic, data):
        print(f"Sending: {topic} {data}")
        self.push_socket.send_string(f"{topic} {data}")

    # Request reply
    def request(self, data):
        self.req_socket.send_string(data)
        return self.req_socket.recv_string()

    def close(self):
        if hasattr(self, 'sub_socket'):
            self.sub_socket.close()
        if hasattr(self, 'push_socket'):
            self.push_socket.close()
        if hasattr(self, 'req_socket'):
            self.req_socket.close()
        self.zmq_context.term()


if __name__ == "__main__":
    server = ZmqClient("tcp://127.0.0.1:5555", "tcp://127.0.0.1:5556", "tcp://127.0.0.1:5557")
    end_time = time.time() + 900  # 15 minutes

    server.subscribe("589141846_tob")
    while time.time() < end_time:
        server.push("589141846", "top_of_book")
        time.sleep(30)

    server.close()
    server.zmq_context.term()
