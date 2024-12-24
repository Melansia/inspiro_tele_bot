# A small telegram bot

I've build this telegram bot just for fun and practicing with python,
This bot can give you a random meme from that is taken from calling the reddit - Meme_Api "Summon a random meme at will"

Also it provide a random inspire quote with a picture using Inspirobot.

Initially this bot was build for a Windows machine, later on I got my hands on a raspberry pi and decided to have the pi run it 24/7

Ok, nice, I have moved the code there installed all the necessary dependencies and tried to run the code and then it started...

With a bit of debugging and fixing the timeout errors as well as system related one - `The chromium binary is not available for arm64`, 
moved from `playwright` library to `selenium` in order to be able to get the inspiration images and feed them to the users.