import time
import walletrpc
import requests
import yaml


def load_config(config_name):
    with open(config_name) as f:
        s = f.read()
        config = yaml.safe_load(s)
    return config

config_path = 'failover.yaml'

# load the config when module gets called
config = load_config(config_path)

settings = config['settings']
steem = config['steem']
mailgun = config['mailgun']
siging_keys = config['signing_keys']

wallet = walletrpc.WalletRPC(ip=settings['rpc_ip'], port=settings['cli_port'], rpcuser=settings['rpc_user'], rpcpassword=settings['rpc_password'])

# Properties to set on the witness update
props = {
    "account_creation_fee": steem['steem_account_creation_fee'],
    "maximum_block_size": steem['steem_maximum_block_size'],
    "sbd_interest_rate": steem['steem_sbd_interest_rate'],
}


# sending email notification through mailgun api
def send_mailgun(msg, subject):
    print("sending mail")
    return requests.post(
            mailgun['url'],
            auth=("api", mailgun['api']),
            data={"from": "Witness Watcher <admin@steemwitness.com>",
                  "to": [mailgun['email']],
                  "subject": subject,
                  "text": msg})


def get_signing_key(keys, current_key):
    while True:
        next_key = next (keys)
        if current_key != next_key:
            return next_key


# Check how many blocks a witness has missed
def check_witness():
    total_missed = wallet.get_witness(steem['witness'])['total_missed']
    current_skey = wallet.get_witness(steem['witness'])['signing_key']
    keys = iter (siging_keys.values())

    while True:
        current_missed = wallet.get_witness(steem['witness'])['total_missed']
        print("| Total missed = {} | Current key {} | Failover if >= {} |".format(current_missed, current_skey, total_missed + steem['allow_missed']))
        if current_missed >= total_missed + steem['allow_missed']:
            next_key = get_signing_key(keys, current_skey)
            # update witness
            print("Failover switch to signing key", next_key)
            update_witness(steem['witness'], steem['witness_url'], next_key, props)
            # update new stats
            total_missed = current_missed
            current_skey = next_key

        time.sleep(steem['check_rate'])


# Update the witness to the new signing key
def update_witness(witness, url, signing_key, props):
    # Create the witness_update transaction and broadcast
    wallet.unlock(settings['password'])
    wallet.update_witness(witness, url, signing_key, props)
    # Send email notification, if u don't need it, just comment out
    send_mailgun(msg="Failed over switched because u missed a lot of blocks", subject="Failover to backup witness node")


########################################################################################################################
if __name__ == '__main__':
    check_witness()
