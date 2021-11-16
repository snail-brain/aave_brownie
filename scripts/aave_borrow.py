import web3
from brownie import config, network, interface
from scripts.get_weth import get_weth
from scripts.helpful_scripts import getAccount
from web3 import Web3

amount = Web3.toWei(0.1, "ether")


def main():
    account = getAccount()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    lending_pool = get_lending_pool()
    approve_erc20("weth_token", amount, lending_pool.address)
    print("Depositing")
    tx = lending_pool.deposit(
        erc20_address, amount, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Deposited")
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account.address)


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account)
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} worth of Eth deposided")
    print(f"You have {available_borrow_eth} available eth to borrow")
    print(f"You have {total_debt_eth} worth of Eth debt")
    return float(available_borrow_eth), float(total_debt_eth)


def get_lending_pool():
    pool_address_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["address_provider"]
    )
    pool_address = pool_address_provider.getLendingPool()
    return interface.ILendingPool(pool_address)


def approve_erc20(token, _amount, sender):
    print("Approving")
    erc20 = interface.IERC20(config["networks"][network.show_active()][token])
    tx = erc20.approve(sender, _amount, {"from": getAccount()})
    tx.wait(1)
    print("Approved")
