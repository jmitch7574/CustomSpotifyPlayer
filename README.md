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
USER_REFRESH_KEY=
RESOLUTION_X=
RESOLUTION_Y=
FULLSCREEN= (optional, only runs fullscreen if key is present)
```

- Run the following code to get a user token refresh key for your application

```
> python getUserAuthCode.py
```

- This should load up your web browser with a spotify confirmation page, click accept.

> [!IMPORTANT]
> If you're aiming on running this on a micro coputer, it may be best you get the refresh token on a desktop first before copying it to your micro computer.

- Your .env file should now have your refresh key
- You can now run init.py and run the program
- The program will only work while your spotify account is playing music

# Notes

- The program cannot be resized at runtime, it is fixed at the .env resolution
- Do not expect amazing code, it is currently a proof of concept
