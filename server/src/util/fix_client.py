import asyncio


class Application:
    sio = None
    timeout = 30

    def __init__(self, **kwargs):
        self.sio = kwargs.get("sio", None)
        self.timeout = kwargs.get("timeout", 30)

    async def connect(self):
        timeout = 30
        while timeout > 0:
            message = f"Message : {timeout}"
            print(f"Broadcasting: {message}")
            await self.sio.emit("fixme", message)
            timeout -= 1
            await asyncio.sleep(5)

    def broadcast(self, message):
        if hasattr(self, "sio"):
            async def async_emit(message):
                await self.sio.emit("fixme", message)
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError as e:
                if str(e).startswith("There is no current event loop in thread"):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                else:
                    raise
            if loop.is_running():
                asyncio.create_task(async_emit(message))
            else:
                loop.run_until_complete(async_emit(message))

                        

    def submitOrder(self, order, validation, trade_validation):
        print(f"fix app received order: {order} | validation: {validation}, tradeValidation: {trade_validation}")
        self.broadcast(order)
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
        self.sio = settings.get("sio", None)

    async def start_mock_client(self):
        env = self.env
        app = self.app
        fix_side = self.fix_side

        print(f"Connecting to {env} env | {app} app | {fix_side} fix_side")
        app = Application(sio=self.sio)
        asyncio.create_task(app.connect()) # Start the client. NOTE: not needed in real FIX Application as it is already running when initialized.
        return app


__name__ == "__main__" and FixClient(env="dev", app="fix", fix_side="dealer", timeout=10)
