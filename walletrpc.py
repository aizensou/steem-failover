import json
import requests


class WalletRPC(object):
    def __init__(self, ip, port, rpcuser, rpcpassword):
        self.url = "http://%s:%s/rpc" % (ip, port)
        self.rpcuser = rpcuser
        self.rpcpassword = rpcpassword
        self._headers = {'content-type': 'application/json'}
        self._jsonrpc = "2.0"
        self._id = 1
        self._auth = (rpcuser, rpcpassword)
    def __call__(self, method, params=None):
        if params is None:
            params = []
        else:
            params = list(params)
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": self._jsonrpc,
            "id": self._id
        }
        data = json.dumps(payload)
        response = requests.post(self.url, data=data,
                             headers=self._headers, auth=self._auth)
        return response.json()

    def is_locked(self):
        return self("is_locked")

    def unlock(self, password):
        if self.is_locked():
            return self("unlock", [password])
        return True

    def get_account(self, account_name):
        try:
            return self("get_account", [account_name])['result']
        except KeyError:
            return ''

    def get_witness(self, witness):
        try:
            return self("get_witness", [witness])['result']
        except KeyError:
            return ''

    def info(self):
        try:
            return self("info")['result']
        except KeyError:
            return ''

    def get_block(self, block_num):
        return self("get_block", [block_num])

    def get_state(self, state):
        return self("get_state", [state])

    def update_witness(self, witness_name, url, signing_key, props, broadcast=True):
        return self("update_witness", [witness_name, url, signing_key, props, broadcast])

    def lock(self):
        return self("lock")

########################################################################################################################
def main(): # for testing the modul
    pass

if __name__ == '__main__': main()
