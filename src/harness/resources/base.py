class Resource:

    def configure(self, value):
        pass

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()
        await self.wait_closed()

    def close(self):
        pass

    async def wait_closed(self):
        pass
