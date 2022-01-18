from brownie import Lottery,accounts,network,config, exceptions
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENV,get_account,fund_with_link,get_contract
from web3 import Web3
from scripts.deploy_lottery import deploy_lottery
from enum import Enum
import pytest

class LOTTERY_STATE(Enum):
    CLOSED = 0
    OPEN = 1
    CALCULATING_WINNER = 2



def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()

    lottery = deploy_lottery()
    entrance_fee = lottery.getEntranceFee()
    expected_entrance_fee = Web3.toWei(0.025,"ether")
    assert expected_entrance_fee == entrance_fee

def test_cant_enter_until_open():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()

    # Act/Assert
    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from":get_account(), "value": lottery.getEntranceFee()})

def test_can_enter_and_start():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    account = get_account()
    lottery = deploy_lottery()

    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # Assert
    assert lottery.lottery_state() == LOTTERY_STATE.OPEN.value
    assert lottery.players(0) == account

def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    account = get_account()
    lottery = deploy_lottery()
    lottery.startLottery({"from":account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    end_txn = lottery.endLottery()
    end_txn.wait(1)
    assert lottery.lottery_state() == LOTTERY_STATE.CALCULATING_WINNER.value

def test_can_pick_winner_correctly():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    account = get_account()
    lottery = deploy_lottery()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    transactions = lottery.endLottery({"from": account})
    request_id = transactions.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777
    starting_balance = account.balance()
    lottery_balance = lottery.balance()
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"from":account}
    )

    assert account.balance() == starting_balance + lottery_balance
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0















