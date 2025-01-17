# Please install:
# betterproto[compiler]
# websockets
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
import numpy as np
import sys
from rich import print


import pytermgui as ptg

from time import sleep
import logging
import uuid
from dataclasses import dataclass, field
from typing import Optional

import betterproto
from typing_extensions import Dict, List
from websockets.frames import CloseCode
from websockets.sync.client import ClientConnection, connect
from dataclasses import dataclass
from typing import List

import betterproto
from tabulate import tabulate


class Side(betterproto.Enum):
    UNKNOWN = 0
    BID = 1
    OFFER = 2

@dataclass
class Portfolio(betterproto.Message):
    total_balance: float = betterproto.double_field(1)
    available_balance: float = betterproto.double_field(2)
    market_exposures: List["PortfolioMarketExposure"] = betterproto.message_field(3)


@dataclass
class PortfolioMarketExposure(betterproto.Message):
    market_id: int = betterproto.int64_field(1)
    position: float = betterproto.double_field(2)
    total_bid_size: float = betterproto.double_field(3)
    total_offer_size: float = betterproto.double_field(4)
    total_bid_value: float = betterproto.double_field(5)
    total_offer_value: float = betterproto.double_field(6)


@dataclass
class Order(betterproto.Message):
    id: int = betterproto.int64_field(1)
    market_id: int = betterproto.int64_field(2)
    owner_id: str = betterproto.string_field(3)
    transaction_id: int = betterproto.int64_field(4)
    price: float = betterproto.double_field(5)
    size: float = betterproto.double_field(6)
    side: "Side" = betterproto.enum_field(7)
    sizes: List["Size"] = betterproto.message_field(8)


@dataclass
class Size(betterproto.Message):
    transaction_id: int = betterproto.int64_field(1)
    size: float = betterproto.double_field(2)


@dataclass
class Trade(betterproto.Message):
    id: int = betterproto.int64_field(1)
    market_id: int = betterproto.int64_field(2)
    transaction_id: int = betterproto.int64_field(3)
    price: float = betterproto.double_field(4)
    size: float = betterproto.double_field(5)
    buyer_id: str = betterproto.string_field(6)
    seller_id: str = betterproto.string_field(7)


@dataclass
class Market(betterproto.Message):
    id: int = betterproto.int64_field(1)
    name: str = betterproto.string_field(2)
    description: str = betterproto.string_field(3)
    owner_id: str = betterproto.string_field(4)
    transaction_id: int = betterproto.int64_field(5)
    min_settlement: float = betterproto.double_field(6)
    max_settlement: float = betterproto.double_field(7)
    open: "MarketOpen" = betterproto.message_field(8, group="status")
    closed: "MarketClosed" = betterproto.message_field(9, group="status")
    orders: List["Order"] = betterproto.message_field(10)
    trades: List["Trade"] = betterproto.message_field(11)
    has_full_history: bool = betterproto.bool_field(12)


@dataclass
class MarketOpen(betterproto.Message):
    pass


@dataclass
class MarketClosed(betterproto.Message):
    settle_price: float = betterproto.double_field(1)


@dataclass
class MarketSettled(betterproto.Message):
    id: int = betterproto.int64_field(1)
    settle_price: float = betterproto.double_field(2)


@dataclass
class OrderCancelled(betterproto.Message):
    id: int = betterproto.int64_field(1)
    market_id: int = betterproto.int64_field(2)


@dataclass
class OrderCreated(betterproto.Message):
    market_id: int = betterproto.int64_field(1)
    user_id: str = betterproto.string_field(2)
    order: "Order" = betterproto.message_field(3, group="_order")
    fills: List["OrderCreatedOrderFill"] = betterproto.message_field(4)
    trades: List["Trade"] = betterproto.message_field(5)


@dataclass
class OrderCreatedOrderFill(betterproto.Message):
    id: int = betterproto.int64_field(1)
    market_id: int = betterproto.int64_field(2)
    owner_id: str = betterproto.string_field(3)
    size_filled: float = betterproto.double_field(4)
    size_remaining: float = betterproto.double_field(5)
    price: float = betterproto.double_field(6)
    side: "Side" = betterproto.enum_field(7)


@dataclass
class Payment(betterproto.Message):
    id: int = betterproto.int64_field(1)
    payer_id: str = betterproto.string_field(2)
    recipient_id: str = betterproto.string_field(3)
    transaction_id: int = betterproto.int64_field(4)
    amount: float = betterproto.double_field(5)
    note: str = betterproto.string_field(6)


@dataclass
class Payments(betterproto.Message):
    payments: List["Payment"] = betterproto.message_field(1)


@dataclass
class RequestFailed(betterproto.Message):
    request_details: "RequestFailedRequestDetails" = betterproto.message_field(1)
    error_details: "RequestFailedErrorDetails" = betterproto.message_field(2)


@dataclass
class RequestFailedRequestDetails(betterproto.Message):
    kind: str = betterproto.string_field(1)


@dataclass
class RequestFailedErrorDetails(betterproto.Message):
    message: str = betterproto.string_field(1)


@dataclass
class Out(betterproto.Message):
    market_id: int = betterproto.int64_field(1)


@dataclass
class User(betterproto.Message):
    id: str = betterproto.string_field(1)
    name: str = betterproto.string_field(2)
    is_bot: bool = betterproto.bool_field(3)


@dataclass
class Users(betterproto.Message):
    users: List["User"] = betterproto.message_field(1)


@dataclass
class Redeem(betterproto.Message):
    fund_id: int = betterproto.int64_field(1)
    amount: float = betterproto.double_field(2)


@dataclass
class Redeemed(betterproto.Message):
    transaction_id: int = betterproto.int64_field(1)
    user_id: str = betterproto.string_field(2)
    fund_id: int = betterproto.int64_field(3)
    amount: float = betterproto.double_field(4)


@dataclass
class ServerMessage(betterproto.Message):
    request_id: str = betterproto.string_field(19)
    portfolio: "Portfolio" = betterproto.message_field(1, group="message")
    market_data: "Market" = betterproto.message_field(2, group="message")
    market_created: "Market" = betterproto.message_field(3, group="message")
    market_settled: "MarketSettled" = betterproto.message_field(4, group="message")
    order_created: "OrderCreated" = betterproto.message_field(5, group="message")
    order_cancelled: "OrderCancelled" = betterproto.message_field(6, group="message")
    payments: "Payments" = betterproto.message_field(7, group="message")
    payment_created: "Payment" = betterproto.message_field(8, group="message")
    out: "Out" = betterproto.message_field(9, group="message")
    authenticated: "Authenticated" = betterproto.message_field(10, group="message")
    request_failed: "RequestFailed" = betterproto.message_field(11, group="message")
    user_created: "User" = betterproto.message_field(12, group="message")
    users: "Users" = betterproto.message_field(13, group="message")
    acting_as: "ActingAs" = betterproto.message_field(14, group="message")
    ownership_received: "Ownership" = betterproto.message_field(15, group="message")
    ownerships: "Ownerships" = betterproto.message_field(16, group="message")
    ownership_given: "OwnershipGiven" = betterproto.message_field(17, group="message")
    redeemed: "Redeemed" = betterproto.message_field(18, group="message")


@dataclass
class Authenticated(betterproto.Message):
    pass


@dataclass
class ActingAs(betterproto.Message):
    user_id: str = betterproto.string_field(1)


@dataclass
class Ownership(betterproto.Message):
    of_bot_id: str = betterproto.string_field(1)


@dataclass
class Ownerships(betterproto.Message):
    ownerships: List["Ownership"] = betterproto.message_field(1)


@dataclass
class OwnershipGiven(betterproto.Message):
    pass


@dataclass
class MakePayment(betterproto.Message):
    recipient_id: str = betterproto.string_field(1)
    amount: float = betterproto.double_field(2)
    note: str = betterproto.string_field(3)


@dataclass
class CreateMarket(betterproto.Message):
    name: str = betterproto.string_field(1)
    description: str = betterproto.string_field(2)
    min_settlement: float = betterproto.double_field(3)
    max_settlement: float = betterproto.double_field(4)


@dataclass
class SettleMarket(betterproto.Message):
    market_id: int = betterproto.int64_field(1)
    settle_price: float = betterproto.double_field(2)


@dataclass
class CreateOrder(betterproto.Message):
    market_id: int = betterproto.int64_field(2)
    price: float = betterproto.double_field(5)
    size: float = betterproto.double_field(6)
    side: "Side" = betterproto.enum_field(7)


@dataclass
class ClientMessage(betterproto.Message):
    request_id: str = betterproto.string_field(13)
    create_market: "CreateMarket" = betterproto.message_field(1, group="message")
    settle_market: "SettleMarket" = betterproto.message_field(2, group="message")
    create_order: "CreateOrder" = betterproto.message_field(3, group="message")
    cancel_order: "CancelOrder" = betterproto.message_field(4, group="message")
    out: "Out" = betterproto.message_field(5, group="message")
    make_payment: "MakePayment" = betterproto.message_field(6, group="message")
    authenticate: "Authenticate" = betterproto.message_field(7, group="message")
    act_as: "ActAs" = betterproto.message_field(8, group="message")
    create_bot: "CreateBot" = betterproto.message_field(9, group="message")
    give_ownership: "GiveOwnership" = betterproto.message_field(10, group="message")
    upgrade_market_data: "UpgradeMarketData" = betterproto.message_field(
        11, group="message"
    )
    redeem: "Redeem" = betterproto.message_field(12, group="message")


@dataclass
class UpgradeMarketData(betterproto.Message):
    market_id: int = betterproto.int64_field(1)


@dataclass
class CancelOrder(betterproto.Message):
    id: int = betterproto.int64_field(1)


@dataclass
class Authenticate(betterproto.Message):
    jwt: str = betterproto.string_field(1)
    id_jwt: str = betterproto.string_field(2)
    act_as: str = betterproto.string_field(3)


@dataclass
class ActAs(betterproto.Message):
    user_id: str = betterproto.string_field(1)


@dataclass
class CreateBot(betterproto.Message):
    name: str = betterproto.string_field(1)


@dataclass
class GiveOwnership(betterproto.Message):
    of_bot_id: str = betterproto.string_field(1)
    to_user_id: str = betterproto.string_field(2)


logger = logging.getLogger(__name__)


class TradingClient:
    """
    Client for interacting with the exchange server.
    """

    _ws: ClientConnection
    _state: "State"

    def __init__(self, api_url: str, jwt: str, act_as: str):
        """
        Connect, Authenticate, then make sure all of the messages holding initial state have been received.
        """
        self._ws = connect(api_url)
        self._state = State()
        self._outstanding_requests = set()
        authenticate = Authenticate(jwt=jwt, act_as=act_as)
        self.send(ClientMessage(authenticate=authenticate))
        while self._state._initializing:
            server_message = self.recv()
            _, message = betterproto.which_one_of(server_message, "message")
            if isinstance(message, RequestFailed):
                raise RuntimeError(
                    f"{message.request_details.kind} request failed during initialization: {message.error_details.message}"
                )

    def state(self) -> "State":
        """
        Return the up-to-date state of the client.
        """
        try:
            while True:
                self.recv(timeout=1e-100)
        except TimeoutError:
            return self._state

    def create_order(
        self,
        market_id: int,
        price: float,
        size: float,
        side: Side,
    ) -> OrderCreated:
        """
        Place an order on the exchange.
        Note that if price and size are passed as float or Decimal they will be quantized.
        """
        price_quantized = round(price, 2)
        if abs(price_quantized - price) > 1e-4:
            logger.warning(f"Price {price} quantized to {price_quantized}")
        size_quantized = round(size, 2)
        if abs(size_quantized - size) > 1e-4:
            logger.warning(f"Size {size} quantized to {size_quantized}")
        msg = ClientMessage(
            create_order=CreateOrder(
                market_id=market_id,
                price=price_quantized,
                size=size_quantized,
                side=side,
            ),
        )
        response = self.request(msg)
        _, message = betterproto.which_one_of(response, "message")
        assert isinstance(message, OrderCreated)
        return message

    def cancel_order(self, order_id: int) -> OrderCancelled:
        """
        Cancel an order on the exchange.
        """
        msg = ClientMessage(
            cancel_order=CancelOrder(
                id=order_id,
            ),
        )
        response = self.request(msg)
        _, message = betterproto.which_one_of(response, "message")
        assert isinstance(message, OrderCancelled)
        return message

    def out(self, market_id: int) -> Out:
        """
        Cancel all orders for a market.
        """
        msg = ClientMessage(
            out=Out(
                market_id=market_id,
            ),
        )
        response = self.request(msg)
        _, message = betterproto.which_one_of(response, "message")
        assert isinstance(message, Out)
        return message

    def redeem(self, fund_id: int, amount: float) -> Redeemed:
        """
        Redeem a position in a market.
        Note that if amount is passed as float or Decimal it will be quantized.
        """
        amount_quantized = round(amount, 2)
        if abs(amount_quantized - amount) > 1e-4:
            logger.warning(f"Amount {amount} quantized to {amount_quantized}")
        msg = ClientMessage(
            redeem=Redeem(
                fund_id=fund_id,
                amount=amount_quantized,
            ),
        )
        response = self.request(msg)
        _, message = betterproto.which_one_of(response, "message")
        assert isinstance(message, Redeemed)
        return message

    def request(
        self, message: ClientMessage
    ) -> ServerMessage:
        """
        Send a message to the server and wait for a response.
        """
        if not message.request_id:
            message.request_id = str(uuid.uuid4())
        self.send(message)
        while True:
            server_message = self.recv()
            if server_message.request_id == message.request_id:
                _, message = betterproto.which_one_of(server_message, "message")
                if isinstance(message, RequestFailed):
                    if message.request_details.kind == "CancelOrder":
                        logger.error(f"CancelOrder failed:")
                    raise RequestFailed(
                        f"{message.request_details.kind} request failed: {message.error_details.message}"
                    )
                return server_message

    def request_many(
        self, messages: List[ClientMessage]
    ) -> List[ServerMessage]:
        """
        Send a list of messages to the server and wait for responses.
        """
        for message in messages:
            if not message.request_id:
                message.request_id = str(uuid.uuid4())
            self.send(message)
        responses = [ServerMessage() for _ in messages]
        while any(not response.request_id for response in responses):
            server_message = self.recv()
            for i, message in enumerate(messages):
                if server_message.request_id == message.request_id:
                    _, response = betterproto.which_one_of(server_message, "message")
                    if isinstance(response, RequestFailed):
                        raise RequestFailed(
                            f"{response.request_details.kind} request failed: {response.error_details.message}"
                        )
                    responses[i] = server_message
        return responses

    def close(self, code: int = CloseCode.NORMAL_CLOSURE, reason: str = ""):
        """
        Close the connection to the server.
        """
        self._ws.close(code, reason)

    def recv(self, timeout: Optional[float] = None) -> ServerMessage:
        """
        Wait for a message from the server and update the state accordingly,
        returning the kind of message and the message.
        """
        message = self._ws.recv(timeout=timeout)
        assert isinstance(message, bytes)
        decoded = ServerMessage().parse(message)
        self._state._update(decoded)
        return decoded

    def send(self, message: ClientMessage):
        """
        Send a message to the server.
        """
        self._ws.send(bytes(message))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.close()
        else:
            self.close(CloseCode.INTERNAL_ERROR)


@dataclass
class State:
    """
    Aggregated state from the server
    """

    _initializing: bool = True
    acting_as: ActingAs = field(default_factory=ActingAs)
    portfolio: Portfolio = field(default_factory=Portfolio)
    payments: List[Payment] = field(default_factory=list)
    ownerships: List[Ownership] = field(default_factory=list)
    users: List[User] = field(default_factory=list)
    markets: Dict[int, Market] = field(default_factory=dict)

    def _update(self, server_message: ServerMessage):
        kind, message = betterproto.which_one_of(server_message, "message")

        if isinstance(message, ActingAs):
            # ActingAs is always the last message in the initialization sequence
            self.acting_as = message
            self._initializing = False

        elif isinstance(message, Portfolio):
            self.portfolio = message

        elif isinstance(message, Payments):
            self.payments = message.payments

        elif isinstance(message, Payment):
            assert kind == "payment_created"
            if all(payment.id != message.id for payment in self.payments):
                self.payments.append(message)

        elif isinstance(message, Ownerships):
            self.ownerships = message.ownerships

        elif isinstance(message, Ownership):
            assert kind == "ownership_received"
            if all(
                ownership.of_bot_id != message.of_bot_id
                for ownership in self.ownerships
            ):
                self.ownerships.append(message)

        elif isinstance(message, Users):
            self.users = message.users

        elif isinstance(message, User):
            assert kind == "user_created"
            if all(user.id != message.id for user in self.users):
                self.users.append(message)

        elif isinstance(message, Market):
            self.markets[message.id] = message

        elif isinstance(message, MarketSettled):
            self.markets[message.id].closed = MarketClosed(
                settle_price=message.settle_price
            )

        elif isinstance(message, OrderCancelled):
            self.markets[message.market_id].orders = [
                order
                for order in self.markets[message.market_id].orders
                if order.id != message.id
            ]

        elif isinstance(message, OrderCreated):
            orders = self.markets[message.market_id].orders
            if message.order.id:
                orders.append(message.order)
            if message.fills:
                for order in orders:
                    if fill := next(
                        (fill for fill in message.fills if fill.id == order.id),
                        None,
                    ):
                        order.size = fill.size_remaining
                self.markets[message.market_id].orders = [
                    order for order in orders if float(order.size) > 0
                ]
            if message.trades:
                self.markets[message.market_id].trades.extend(message.trades)


class RequestFailed(Exception):
    pass


def open_qt_window():
    app = QtWidgets.QApplication(sys.argv)
    win = pg.GraphicsLayoutWidget(show=True)
    win.setWindowTitle('Trading Visualization')
    
    # Create a plot area
    plot = win.addPlot()
    plot.setLabel('left', 'Price')
    plot.setLabel('bottom', 'Time')
    
    # Enable antialiasing for prettier plots
    pg.setConfigOptions(antialias=True)
    
    return app, win, plot

app, window, plot = open_qt_window()


# BEGIN USER CODE HERE:

api_url = "wss://trading-bootcamp.fly.dev/api"
jwt = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImNhOjA0OmZmOjViOjNmOmUwOmUzOjNjOmU2OmUwOjAzOjZiOjIxOmJiOjQ3OjVlIiwidHlwIjoiSldUIn0.eyJhdWQiOlsidHJhZGluZy1zZXJ2ZXItYXBpIl0sImF6cCI6ImE5ODY5YmIxMjI1ODQ4YjlhZDViYWQyYTA0YjcyYjVmIiwiZXhwIjoxNzMxNjMzMjU5LCJpYXQiOjE3MzEwMjg0NTgsImlzcyI6Imh0dHBzOi8vY3Jhenl0aWVndXkua2luZGUuY29tIiwianRpIjoiODc3OGUxZWEtNDY4ZC00YjM4LTkxOWEtZDFiNzJjNzFmNzY0Iiwib3JnX2NvZGUiOiJvcmdfMWExZDJjMTAxMGYiLCJwZXJtaXNzaW9ucyI6W10sInNjcCI6WyJvcGVuaWQiLCJwcm9maWxlIiwiZW1haWwiLCJvZmZsaW5lIl0sInN1YiI6ImtwX2UyZTI0NGNhODQxODRhODdiNjc2YWQ3MzNiNGM1MDVmIn0.WJSLxw8IbXZdm_iFYURqIC_DlqWtoQ97qc3XfpAGiquACVtZtfQXdaFax_Z1w1syVBhHTNzrbMuUtcU45haTO_rpS-pRvJNOglCmcKWQB38Gso_We4ZEmcS8x-3uLrlkOMlBNMFszH8DMdcTkLkojaGG2tCFOhmifmO_hpFvIyzeOCyPYaAu5YBMqn_wXE5hRmogbFuH_hwYc9mz02EeM-fP2jbsl6_ApeAPY8ttntfaSNvC4cTMgYp1sLUkJqL5x-CjPLnaaZc6-wuld-vA3e7tB1DvLn5urJ8ONxg2IH-mZz7iOTEIX2fKupLJNedfEGJLUMLaw3y59wUBzawIfQ"
act_as = "kp_e2e244ca84184a87b676ad733b4c505f"
client = TradingClient(api_url, jwt, act_as)


class Opinion:
    position: float
    highest_bid: float
    bid_volume: float
    lowest_offer: float
    offer_volume: float
    def __init__(self):
        self.position = 0
        self.highest_bid = None
        self.lowest_offer = None
        self.bid_volume = 0
        self.offer_volume = 0


class Actor:
    user: User
    # opinion in every market
    opinion: Dict[int, Opinion]
    index: int
    def __init__(self, user):
        self.user = user
        if user.name.startswith("bot:"):
            self.user.name = self.user.name[4:]
        self.opinion = {}
        for market_id in ids_to_names.keys():
            self.opinion[market_id] = Opinion()

        self.index = None

actors = {}

from rich.console import Console, Group
from rich.padding import Padding
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.prompt import Prompt

import itertools
import time

console = Console()


ids_to_names = {
    19: "ricki_time",
    20: "david_time",
    36: "dsf",
    39: "fds"
}

idx = 1

def generate_display() -> Layout:
    start = time.time()

    state = client.state()
    markets = {}
    for id, name in ids_to_names.items():
        markets[id] = state.markets.get(id)

    for user in state.users:
        #if not user.is_bot:
        #    continue
        actors[user.id] = Actor(user)

    for marked_id, name in ids_to_names.items():
        market = markets[marked_id]
        for trades in market.trades:
            # idk why, but some actors just dont exist?
            if trades.buyer_id not in actors:
                continue
            if trades.seller_id not in actors:
                continue

            actors[trades.buyer_id].opinion[market.id].bid_volume += trades.size
            actors[trades.seller_id].opinion[market.id].offer_volume += trades.size

            actors[trades.buyer_id].opinion[market.id].position += trades.size
            actors[trades.seller_id].opinion[market.id].position -= trades.size

            if actors[trades.buyer_id].opinion[market.id].highest_bid or -99999999 < trades.price:
                actors[trades.buyer_id].opinion[market.id].highest_bid = trades.price
            if actors[trades.seller_id].opinion[market.id].lowest_offer or 99999999 > trades.price:
                actors[trades.seller_id].opinion[market.id].lowest_offer = trades.price
        
        for order in market.orders:
            if order.side == Side.BID:
                actors[order.owner_id].opinion[market.id].bid_volume += order.size
            else:
                actors[order.owner_id].opinion[market.id].offer_volume += order.size

            if order.side == Side.BID:
                if actors[order.owner_id].opinion[market.id].highest_bid or -99999999 < order.price:
                    actors[order.owner_id].opinion[market.id].highest_bid = order.price
            else:
                if actors[order.owner_id].opinion[market.id].lowest_offer or 99999999 > order.price:
                    actors[order.owner_id].opinion[market.id].lowest_offer = order.price

    i = 0
    useless_actors = []
    for user in actors.values():
        sum = 0
        for market_id in ids_to_names.keys():
            sum += user.opinion[market_id].position
            if user.opinion[market_id].highest_bid is not None:
                sum += 1
            if user.opinion[market_id].lowest_offer is not None:
                sum += 1
        if sum == 0:
            useless_actors.append(user.user.id)
        i += 1

   # print("user", end="\t")
   # for market in ids_to_names.values():
   #     print(market, end="\t")

   # print()
    column_width = 12

    pos_table = Table(title="position", show_header=True, header_style="bold magenta")
    pos_table.add_column("User\\Market", style="dim", width=12)
    bid_offer_table = Table(title="offer/bid", show_header=True, header_style="bold magenta")
    bid_offer_table.add_column("User\\Market", style="dim", width=12)

    for market in ids_to_names.keys():
        pos_table.add_column(markets[market].name, width = column_width)
        grid = Table.grid(expand=True, padding=(0, 1, 0, 0))
        grid.add_column()
        grid.add_column(justify="right")
        grid.add_row(markets[market].name, "")
        grid.add_row("hi/lo", "vol")
        bid_offer_table.add_column(grid, width = column_width)

    for user in actors.values():
        if user.user.id in useless_actors:
            continue
        bid_offer_grids = []
        pos_text = []
        for market in ids_to_names.keys():
            bid_offer_grid = Table.grid(expand=True, padding=(0, 0, 0, 0))
            bid_offer_grid.add_column()
            bid_offer_grid.add_column(justify="right")
            bid_offer_grid.add_row(Padding(str(user.opinion[market].highest_bid), (0, 1, 0, 0)), str(user.opinion[market].bid_volume), style="#bbffbb")
            bid_offer_grid.add_row(Padding(str(user.opinion[market].lowest_offer), (0, 1, 0, 0)), str(user.opinion[market].offer_volume), style="#ffbbbb")
            bid_offer_grids.append(bid_offer_grid)
        
            position = user.opinion[market].position 
            pos_color = ""
            if position > 0:
                pos_color = "#bbffbb"
            elif position < 0:
                pos_color = "#ffbbbb"
            else:
                pos_color = "#bbbbff"

            pos_text.append(Text(str(position), style=pos_color))
        bid_offer_table.add_row(user.user.name[:7], *bid_offer_grids)

        pos_table.add_row(user.user.name[:7], *pos_text)
    #console.print(Group("\n"*10, pos_table,bid_offer_table))
    layout = Layout()
    layout.split(
        Layout(pos_table, name="position"),
        Layout(bid_offer_table, name="bid_offer")
    )
    
    #print("time", Panel(Group(str((time.time() - start)*1000), "ms"), width=10, height=3))
    # Clear the plot
    plot.clear()

    # Get market data for plotting
    for market_id in ids_to_names.keys():
        market = markets[market_id]
        
        # Create arrays for bid/offer prices and volumes
        bids = []
        bid_vols = []
        offers = []
        offer_vols = []
        
        for actor in actors.values():
            if actor.user.id not in useless_actors:
                if actor.opinion[market_id].highest_bid is not None:
                    bids.append(actor.opinion[market_id].highest_bid)
                    bid_vols.append(actor.opinion[market_id].bid_volume)
                if actor.opinion[market_id].lowest_offer is not None:
                    offers.append(actor.opinion[market_id].lowest_offer)
                    offer_vols.append(actor.opinion[market_id].offer_volume)
        
        if bids:
            # Plot bids in green
            plot.plot(bid_vols, bids, pen=None, symbol='o', symbolBrush='g', name=f'{market.name} Bids')
        
        if offers:
            # Plot offers in red  
            plot.plot(offer_vols, offers, pen=None, symbol='o', symbolBrush='r', name=f'{market.name} Offers')

    # Process Qt events
    app.processEvents()

    return Group(pos_table,bid_offer_table)



with Live(generate_display(), console=console, refresh_per_second=60) as live:
    while True:
        time.sleep(1/60)
        live.update(generate_display())
