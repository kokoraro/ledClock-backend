
```
# Local Run
pipenv install --dev

# Client (LED Driver)
export LOCAL_DEV=true && pipenv run python client/main.py

# Server (API)
pipenv run python server/server.py
```

For info on the LED Matrix library Refer to: https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/bindings/python