# CryptoBot v1.0.1

<a href="#"><img src="images/bot.png"
alt="" width="201" height="155"/></a>

## About
CryptoBot is(will be) an automated, high frequency trading bot for cryptocurrencies. It uses **Machine Learning** to decide when to trade. Currently it supports only Bitcoins, and trading on the BTCC exchange. In the future I intend on adding other currencies and exchanges.  

## List of sources
https://github.com/AdeelMufti/CryptoBot
https://github.com/cbyn/bitpredict

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

**Ideas**

The trading strategy that is currently used opens a position and closest it 15 seconds later. I think this can be improved to re-evaluate your current position every second.

**Help the project**

well do what i did and fork the project en improve the code.
Also for training and back testing i need access to fast hardware (gpu). Also for collecting the data i need a vps or ec2 these cost money and so i am looking for sponsors.

BTC 148XxY4qVf7z5X9rK3FtxiJaUcynXLraxb</br>
ETH 0xb3EBA8abd933Bd7572dDF0c64aCD8eBaFFB420AB

All sponsers will be mentioned below
-[ ]
-[ ]
-[ ]
