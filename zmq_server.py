import asyncio
import time
import zmq
import zmq.asyncio


class ZmqServer():
    def __init__(self, pub_ip: str = None, pull_ip: str = None, rep_ip: str = None):
        self.zmq_context = zmq.asyncio.Context()
        self.poller = zmq.asyncio.Poller()
        if pub_ip:
            self.pub_socket = self.zmq_context.socket(zmq.PUB)
            self.pub_socket.bind(pub_ip)
            self.poller.register(self.pub_socket, zmq.POLLOUT)
        if pull_ip:
            self.pull_socket = self.zmq_context.socket(zmq.PULL)
            self.pull_socket.bind(pull_ip)
            self.poller.register(self.pull_socket, zmq.POLLIN)
        if rep_ip:
            self.rep_socket = self.zmq_context.socket(zmq.REP)
            self.rep_socket.bind(rep_ip)
            self.poller.register(self.rep_socket, zmq.POLLIN)

    # Pub sub
    async def publish(self, topic, data):
        print(f"Sending: {topic} {data}")
        await self.pub_socket.send_string(f"{topic} {data}")

    # def receive_pub(self):
    #     return self.pub_socket.recv_string()

    # Push pull
    async def poll_pull_socket(self):
        await self.pull_socket.poll()
    
    async def recv_pull(self):
        return await self.pull_socket.recv_string()
    
    async def recv_all_pulls(self) -> list[str]:
        poll_count = await self.pull_socket.poll(1)
        print(f"Poll count: {poll_count}")
        msgs = []
        for _ in range(poll_count):
            msgs.append(await self.pull_socket.recv_string())
        return msgs

    # Request reply
    # Req-Rep pattern is synchronous - client blocks until server replies
    async def poll_rep_socket(self):
        await self.rep_socket.poll()
    
    async def reply(self, data):
        await self.rep_socket.send_string(data)

    async def receive_req(self):
        return self.rep_socket.recv_string()

    def close(self):
        if hasattr(self, 'pub_socket'):
            self.pub_socket.close()
        if hasattr(self, 'pull_socket'):
            self.pull_socket.close()
        if hasattr(self, 'rep_socket'):
            self.rep_socket.close()
        self.zmq_context.term()


async def main(server):
    try:
        while True:
            msg = await server.poll_pull_socket()
            print(f"Received: {msg}")
    except asyncio.CancelledError:
        pass
    finally:
        print("Closing server")
        server.close()

if __name__ == "__main__":
    server = ZmqServer("tcp://127.0.0.1:5555",
                       "tcp://127.0.0.1:5556", "tcp://127.0.0.1:5557")
    loop = asyncio.new_event_loop()
    main_task = loop.create_task(main(server))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        main_task.cancel()
        loop.run_until_complete(main_task)

    print("I'm complete")
    loop.close()
