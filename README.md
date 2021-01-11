# Gemini API Python CLI

This is a Gemini API CLI to buy/sell btc/eth/usd. This avoids the web order fees and allows us to take advantage of the much lower API fees.

Installation:
---
1. Install python
2. Add your Gemini API key to `GEMINI_API_KEY` and your Gemini API Secret key to `GEMINI_API_SECRET` to your environment variables. The CLI will automatically grab it.

Usage Examples:
---

Check the **status** of open orders:
```
python3 gemini.py status
```

**Buy** 4 ethereum at $1100. There will be a confirmation for the order:
```
python3 gemini.py buy ethusd 4 1100
```

**Buy** 0.1 ethereum at $10000. There will be a confirmation for the order:
```
python3 gemini.py buy btcusd 0.1 10000
```

**Sell** 4 ethereum at $1400. There will be a confirmation for the order:
```
python3 gemini.py sell ethusd 4 1400
```

**Cancel** an order with order id "19400502009":
```
python3 gemini.py cancel 19400502009
```

**Cancel all** orders:
```
python3 gemini.py cancel --all
```
