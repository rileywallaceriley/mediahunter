# Media Hunter

## Deployment Instructions (Render)

1. Go to https://dashboard.render.com/
2. Click "New Web Service"
3. Connect this repo
4. Use the following settings:

- Build command:
```
pip install -r requirements.txt
```

- Start command:
```
gunicorn app:app
```

- Environment: Python 3

You're good to go!
