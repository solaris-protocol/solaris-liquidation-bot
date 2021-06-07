## Project description

A Python bot for liquidation of unhealthy obligations in [Solaris protocol](https://github.com/solaris-protocol/solaris-protocol).

## How it works
### [Liquidation Scheme](https://raw.githubusercontent.com/solaris-protocol/solaris-protocol/master/howitworks.png)
1. The bot fetches all obligations accounts inside the protocol and tries to find an unhealthy one (`obligation.borrowed_value < obligation.unhealthy_borrow_value`) and checks if the liquidation will be profitable (`liquidation_reward > flashloan_fee`)

2. The bot sends a `liquidate_obligation` instruction to the liquidation program containing a public key of unhealthy obligation

3. Liquidation program gets some `liquidity_amount` from a lending program via flashloan and repays a loan. Then if it returns flashloan + `flashloan_fees` and takes a liquidation reward. If `balance_before < balance_after` it return `Ok()`, if now throws an error and reverts the transaction. 

#### [Liquidation Bot](https://github.com/solaris-protocol/solaris-liquidation-bot/tree/master/bot)
#### [Liquidation Program](https://github.com/solaris-protocol/solaris-liquidation-bot/tree/master/liquidation_program)
