from brownie import interface, config, network
from scripts.helpful_scripts import getAccount


def main():
    get_weth()


def get_weth():
    account = getAccount()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": 0.1 * 10 ** 18})
    tx.wait(1)
    print("Recieved 0.1 WETH")
