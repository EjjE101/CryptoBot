# CryptoBot v1.0.0

<a href="#"><img src="images/bot.png"
alt="" width="201" height="155"/></a>

## About
CryptoBot is an automated, high(ish) frequency trading bot for cryptocurrencies. It uses **Machine Learning** to decide when to trade. Currently it supports only Bitcoins, and trading on the BTCC exchange. In the future I intend on adding other currencies and exchanges.  

This project is a very-hard-fork of Christopher Bynum's BitPredict which can be seen at: https://github.com/cbyn/bitpredict. The base code, and the idea, is modeled off the BitPredict project, so credit is due. However, CryptoBot has evolved immensely and looks very different than BitPredict, and have been taken several steps further.

The project is written entirely in **Python**, with the exception of some shell scripts.

## EjjE101
I found this project on github and have some ideas about improving it.
- [ ] implement websocket         [ 40% done ]
    todo:
    - [x] convert to bitfinex
    - [x] multiple currencies pairs
    - [ ] improve code
- [ ] improve trading strategy    [  0% done ]
    todo:
    - [ ] implement websocket
    - [ ] test for beter features
- [ ] multi currencies            [ 10% done ]
    todo:
    - [x] store alle currencies in mongodb
    - [ ] test for beter features

**What am i working on now?**
Currently working on implementing the websocket connection en improving the code that i have written. I need this because of the rate limit that is on de REST api, on bitfinex this is 90 request per second. With the websocket connection i received more then 1000 messages per second.

**Ideas
The trading strategy that is currently used opens a position and closest it 15 seconds later. I think this can be improved to re-evaluate your current position every second.

**Help the project
well do what i did and fork the project en improve the code
for training and back testing i need access to fast hardware (gpu). Also for collecting the data i need a vps or ec2 these cost money and so i'm looking for sponsers.
BTC 148XxY4qVf7z5X9rK3FtxiJaUcynXLraxb
ETH 0xb3EBA8abd933Bd7572dDF0c64aCD8eBaFFB420AB

All sponsers will be mentioned below
-


## Details
Features are created and saved to disk using the create_live_features.py script. The **Machine Learning features** include:
- Width
- Power Imbalance
- Power Adjusted Price
- Trade Count
- Trade Average
- Aggressor
- Trend
- These features were adapted from Christopher Bynum's BitPredict project. More details at: https://github.com/cbyn/bitpredict/
- Please feel free to suggest others!?

A target (named "final") is created using the future midpoint prices (at 5, 10, 15, 20, 25, 30 seconds in the future) of the midpoint between bids/asks for the books at those moments:
- -1 means the average price of future midpoints went down below a certain threshold percentage, after 15 seconds
- +1 means the average price of future midpoints went up above a certain threshold percentage, after 15 seconds
- 0 means the average price did not go up or below the threshold percentage, after 15 seconds

Using the features, we train a Machine Learning **classifier** model (using the strategy.py script) against the target value to give us one of three options:
- -1 means the price is predicted to go down, so trade accordingly
- +1 means the price is predicted to go up, so trade accordingly
- 0 means don't make a trade

I have tried it using the following classifiers:
- **XGBClassifier** from the XGBoost project: https://xgboost.readthedocs.io/en/latest/
- **RandomForestClassifier** from the scikit-learn library: http://scikit-learn.org/
- **GradientBoostingClassifier** from the scikit-learn library
- YMMV, try which one gives you the best results (strategy.py will back test and create the model)

predict.py is used to do the live trading.

## Inner Workings

- A trade is made (position took) and then reversed after 15 seconds
- The balance is kept in a 50/50 split, with 50% as bitcoin and 50% as cash (FIAT)
- When price is predicted to go down, bitcoins are traded for cash, and then bought back at a (hopefully) lower price, yielding a profit in the bitcoin balance.
- When price is predicted to go up, cash is traded for bitcoins, and then the bitcoins are sold back at a (hopefully) higher price, yielding a profit in the cash balance.
- Keep in mind that orders you make never execute immediately (if ever), which is why we want to take the average of the price midpoints for +/- 15 seconds. In case the trade actually takes places, and reverses, within a 15 second window.
- You will probably need several weeks of data before you can train a classifier to get you any meaningful results.

## Disclaimer
The bot is fully functional. However, this was more of an exercise to teach myself Machine Learning. I have not be able to make a consistent profit. Neither should you expect to. Please be very careful in using this bot, and assume all responsibility yourself. Never use it for trading more than you're willing to lose (i.e. use it for fun only).

## Other Notes
This is very much a work in progress. Contributions are welcome. If you can bring it to a consistent profitability, do share!
