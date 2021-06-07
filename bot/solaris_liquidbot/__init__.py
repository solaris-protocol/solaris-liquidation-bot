from construct import Int8ub, Int64ub, Struct, Array, Byte, Bytes, Container
import requests
import json
import base64

PUBLIC_KEY_LAYOUT = Bytes(32)
DECIMAL = Array(3, Int64ub)

OBLIGATION_LAYOUT_LEN = 916
TOKEN_LENDING_PROGRAM_ID = '6h5geweHee42FbxZrYAcYJ8SGVAjG6sGow5dtzcKtrJw'

class LiquidBot:
    __url = 'https://api.devnet.solana.com'

    """ This is LiquidBot Class """
    def __init__(self, threaded=True):
        self.threaded = threaded

    def get_obligaions(self) -> dict:
        headers = {'Content-Type': 'application/json'}
        body = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getProgramAccounts",
            "params": [
                TOKEN_LENDING_PROGRAM_ID,
                {
                    "encoding": "jsonParsed",
                    "filters": [
                        {
                            "dataSize": OBLIGATION_LAYOUT_LEN
                        }
                    ]
                }
            ]
        })

        responce = requests.post(self.__url, headers=headers, data=body)
        if responce.status_code != 200:
            raise ValueError("Invalid request")

        return json.loads(responce.text).get('result')

    def get_unhealthy_obligations(self):
        unhealthy_obligations = []
        
        for obligation in self.get_obligaions():
            data = obligation.get('account').get('data')
            if type(data) == list and len(data) > 0:
                data = data[0]

            data = base64.b64decode(data)
            
            borrowed_data = data[1 + 8 + 1 + 32 + 32 + 16:][:16]
            borrowed_value = int.from_bytes(borrowed_data, "little")

            unhealthy_borrow_data = data[1 + 8 + 1 + 32 + 32 + 16 + 16 + 16:][:16]
            unhealthy_borrow_value = int.from_bytes(unhealthy_borrow_data, "little")

            if borrowed_value < unhealthy_borrow_value:
                print('Obligation is healthy and cannot be liquidated')

        return unhealthy_obligations