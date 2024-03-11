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
    async def poll_pull_socket(self) -> int:
        return await self.pull_socket.poll()
    
    async def recv_pull(self) -> str:
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
    async def poll_rep_socket(self) -> int:
        return await self.rep_socket.poll()
    
    async def reply(self, data):
        await self.rep_socket.send_string(data)

    async def receive_req(self) -> str:
        return await self.rep_socket.recv_string()

    def close(self):
        if hasattr(self, 'pub_socket'):
            self.pub_socket.close()
        if hasattr(self, 'pull_socket'):
            self.pull_socket.close()
        if hasattr(self, 'rep_socket'):
            self.rep_socket.close()
        self.zmq_context.term()


async def pubsub_server_task(server):
    try:
        while True:
            poll_count = await server.poll_pull_socket()
            if poll_count > 0:
                msg = await server.recv_pull()
                print(f"Received: {msg}")
    except asyncio.CancelledError:
        pass
    finally:
        print("Exiting pubsub server task")


async def reqrep_server_task(server: ZmqServer):
    try:
        while True:
            poll_count = await server.poll_rep_socket()
            if poll_count > 0:
                msg = await server.receive_req()
                print(f"Received: {msg}")
                await server.reply("Received")
    except asyncio.CancelledError:
        pass
    finally:
        print("Exiting reqrep server task")


if __name__ == "__main__":
    server = ZmqServer("tcp://127.0.0.1:5555",
                       "tcp://127.0.0.1:5556", "tcp://127.0.0.1:5557")
    loop = asyncio.new_event_loop()
    pubsub_task = loop.create_task(pubsub_server_task(server))
    reqrep_task = loop.create_task(reqrep_server_task(server))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pubsub_task.cancel()
        reqrep_task.cancel()
        loop.run_until_complete(pubsub_task)
        loop.run_until_complete(reqrep_task)
    finally:
        print("Closing server...")
        server.close()

    loop.close()
