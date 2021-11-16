from brownie import accounts, network, config


Local_Blockchain_Environments = ["development", "ganache-local"]
Forked_Environments = ["mainnet-fork"]


def getAccount(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)  # Select specific account based on its id or index
    if (
        network.show_active()
        in Local_Blockchain_Environments  # If using local chain, use the first address provided from that chain
        or network.show_active() in Forked_Environments
    ):
        return accounts[0]
    return accounts.add(  # Otherwise, use wallet associated with current network
        config["wallets"]["from_key"]
    )
