import zmq
import time


class ZmqServer():
    def __init__(self, pub_ip: str = None, pull_ip: str = None, rep_ip: str = None):
        self.zmq_context = zmq.Context()
        if pub_ip:
            self.pub_socket = self.zmq_context.socket(zmq.PUB)
            self.pub_socket.bind(pub_ip)
        if pull_ip:
            self.pull_socket = self.zmq_context.socket(zmq.PULL)
            self.pull_socket.bind(pull_ip)
        if rep_ip:
            self.rep_socket = self.zmq_context.socket(zmq.REP)
            self.rep_socket.bind(rep_ip)

    def publish(self, topic, data):
        print(f"Sending: {topic} {data}")
        self.pub_socket.send_string(f"{topic} {data}")

    def receive(self):
        return self.pub_socket.recv_string()

    def poll_pull_socket(self):
        return self.pull_socket.poll(1)

    def pull(self):
        return self.pull_socket.recv_string()

    def close(self):
        self.pub_socket.close()
        self.zmq_context.term()

    # Add request reply for Python exchange_connectors


if __name__ == "__main__":
    server = ZmqServer("tcp://127.0.0.1:5555", "tcp://127.0.0.1:5556")
    end_time = time.time() + 900  # 15 minutes

    while time.time() < end_time:
        if server.poll_pull_socket() > 0:
            print(server.pull())
        time.sleep(10)

    server.pub_socket.close()
    server.zmq_context.term()
