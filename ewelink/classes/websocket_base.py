import json
import time

from ewelink.data.errors import errors

try:
    import websocket
except Exception:  # pragma: no cover
    websocket = None


class WebSocketBase:
    @staticmethod
    def websocket_request(url, payloads, delay_time=1.0):
        if websocket is None:
            return {"error": errors["unknown"]}

        responses = []
        try:
            ws = websocket.create_connection(url)
            try:
                for payload in payloads:
                    ws.send(payload)
                    time.sleep(delay_time)

                    while True:
                        ws.settimeout(0.1)
                        try:
                            message = ws.recv()
                            responses.append(json.loads(message))
                        except Exception:
                            break
            finally:
                ws.close()
        except Exception as exc:
            return WebSocketBase.custom_throw_error(exc)

        return responses

    @staticmethod
    def custom_throw_error(exc):
        message = str(exc)
        if "WebSocket is not opened" in message:
            return {"error": 406, "msg": errors[406]}
        return {"error": errors["unknown"]}
