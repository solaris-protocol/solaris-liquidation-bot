from construct import Int8ub, Int64ub, Struct, Array, Byte, Bytes, Container

PUBLIC_KEY_LAYOUT = Bytes(32)
OBLIGATION_LAYOUT_LEN = 265

class LiquidBot:
    __format = Struct(
        "version" / Int8ub,
        "deposited_collateral_tokens" / Int64ub,
        "collateral_reserve" / PUBLIC_KEY_LAYOUT,
        "cumulative_borrow_rate_wads" / Array(3, Int64ub),
        "borrowed_liquidity_wads" / Array(3, Int64ub),
        "borrow_reserve" / PUBLIC_KEY_LAYOUT,
        "token_mint" / PUBLIC_KEY_LAYOUT
    )

    """ This is LiquidBot Class """
    def __init__(self, threaded=True):
        self.threaded = threaded

    def deserialize_obligation(self, data: bytes) -> Container:
        if len(data) != OBLIGATION_LAYOUT_LEN:
            raise ValueError("Invalid data len")

        return self.__format.parse(data)
