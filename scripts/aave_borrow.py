import web3
from brownie import config, network, interface
from scripts.get_weth import get_weth
from scripts.helpful_scripts import getAccount
from web3 import Web3

amount = Web3.toWei(0.1, "ether")
weth_address = config["networks"][network.show_active()]["weth_token"]
dai_address = config["networks"][network.show_active()]["dai_token"]
dai_eth_address = config["networks"][network.show_active()]["dai_eth_price_feed"]


def main():
    account = getAccount()

    lending_pool = get_lending_pool()

    # Wrap eth then approve it for transfering to Aave lending pool
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    approve_erc20(weth_address, amount, lending_pool.address)

    # Deposit weth
    print("Depositing")
    deposit_tx = lending_pool.deposit(
        weth_address, amount, account.address, 0, {"from": account}
    )
    deposit_tx.wait(1)
    print("Deposited")

    # Borrow Dai
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account.address)
    dai_eth = get_asset_price(dai_eth_address)
    amount_dai_to_borrow = (1 / dai_eth) * (borrowable_eth * 0.95)
    print(f"We are going to borrow {amount_dai_to_borrow}")
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        2,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("Borrow Complete")
    get_borrowable_data(lending_pool, account.address)

    # Repay borrowed Dai
    repay_all(
        Web3.toWei(amount_dai_to_borrow, "ether"), lending_pool, account, dai_address
    )


def repay_all(amount, lending_pool, account, token):
    print(f"Approving spend limit")
    approve_erc20(token, amount, lending_pool.address)
    print("Repaying debt...")
    repay_tx = lending_pool.repay(token, amount, 2, account.address, {"from": account})
    repay_tx.wait(1)
    print("Debt repayed!")
    get_borrowable_data(lending_pool, account.address)


def get_asset_price(price_feed):
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed)
    latest_price = Web3.fromWei(dai_eth_price_feed.latestRoundData()[1], "ether")
    print(f"Dai/Eth Price is {latest_price}")
    return float(latest_price)


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
    erc20 = interface.IERC20(token)
    tx = erc20.approve(sender, _amount, {"from": getAccount()})
    tx.wait(1)
    print("Approved")
