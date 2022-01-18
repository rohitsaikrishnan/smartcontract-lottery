from brownie import network, accounts,config, MockV3Aggregator, VRFCoordinatorMock, LinkToken, Contract

LOCAL_BLOCKCHAIN_ENV = ["ganache-local", "development"]
FORKED_LOCAL_ENV = ["mainnet-fork", "mainnet-fork-dev"]

contract_to_mock = {"eth_usd_price_feed": MockV3Aggregator,
                    "vrf_coordinator": VRFCoordinatorMock,
                    "link_token": LinkToken}

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (network.show_active() in LOCAL_BLOCKCHAIN_ENV) or (network.show_active() in FORKED_LOCAL_ENV):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])

DECIMALS = 8
INITIAL_VALUE = 200000000000

def deploy_mocks(decimals = DECIMALS, initial_value = INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    linktoken = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(linktoken.address, {"from": account})
    print("Deployed!")


def fund_with_link(contract_address, account=None, link_token=None, amount=100000000000000000):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Fund Contract!")
    return tx


def get_contract(contract_name):
    """
    grab contract addresses from brownie config if defined else deploy a mock contract and return that mock contract

    Args:
        contract_name (string)

    return:
        brownie.network.contract.ProjectContract: the most recently deployed version of contract
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]

    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


