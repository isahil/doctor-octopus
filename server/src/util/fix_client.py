import asyncio


class Application:
    sio = None
    broadcast = False
    timeout = 30

    def __init__(self, **kwargs):
        self.broadcast = kwargs.get("broadcast", False)
        self.sio = kwargs.get("sio", None)
        self.timeout = kwargs.get("timeout", 30)

    async def connect(self):
        timeout = 30
        while timeout > 0:
            message = f"Message : {timeout}"
            if self.broadcast is True:
                print(f"Broadcasting: {message}")
                await self.sio.emit("fixme", message)
            timeout -= 1
            await asyncio.sleep(2)

    async def submitOrder(self, order, validation, tradeValidation):
        print(f"fix app received order: {order}")
        await self.sio.emit("fixme", {order, validation, tradeValidation})
        return order


class FixClient:
    env = None
    app = None
    fix_side = None
    sio = None

    def __init__(self, settings):
        self.env = settings.get("env", "prod")
        self.app = settings.get("app", "fix")
        self.fix_side = settings.get("fix_side", "buy")
        self.broadcast = settings.get("broadcast", False)
        self.sio = settings.get("sio", None)

    async def start_mock_client(self):
        env = self.env
        app = self.app
        fix_side = self.fix_side
        broadcast = self.broadcast

        print(f"Connecting to {env} env | {app} app | {fix_side} fix_side | Broadcast: {broadcast}")
        app = Application(broadcast=broadcast, sio=self.sio)
        con = app.connect()
        asyncio.create_task(con)
        return app


__name__ == "__main__" and FixClient(env="dev", app="fix", fix_side="dealer", timeout=10)
