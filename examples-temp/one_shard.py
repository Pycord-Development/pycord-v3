import pycord
import logging

app = pycord.GatewayApp(0, level=logging.DEBUG)


# Connects the bot with the token `token` to the Discord Gateway
app.connect('token')
