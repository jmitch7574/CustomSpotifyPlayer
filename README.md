# Custom Spotify Player

- A spotify client designed for running on raspberry pis with 480x320 display

> [!WARNING]
> A spotify premium account is required

# Setup

- Create a spotify application on the developer dashboard
  - Can set it up however you want, ensure the callback address is http://localhost:8000
- Clone the project
- Create a .env file with the following

```
CLIENT_ID=[your client ID here]
CLIENT_SECRET=[your client secret here]
```

- Run the following script

```
> python getUserAuthCode.py
```

- Your .env file should now look like the following

```
CLIENT_ID=[your client ID here]
CLIENT_SECRET=[your client secret here]
USER_REFRESH_KEY=[generated user refresh key]
```

- You can now run init.py and run the program
- The program will only work while your spotify account is playing music
