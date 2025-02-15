# Automated solution to [https://game.cerbos.dev/](https://game.cerbos.dev/)

Unofficially sponsored by [supersimple.io](https://supersimple.io/)

1. install deps
```
pip install -r requirements.txt
```

2. open Chrome with remote debugging enabled, and open the Cerbos game
```
open -a "Google Chrome" --args --remote-debugging-port=9222
```

3. start the script
```
python3 browser.py
```

4. start your game and put your browser's focus inside the game.

The script will now automatically hit Left and Right arrows to win the game.

Edit `desired_score` in `browser.py` to pick how far you'd like to go.
