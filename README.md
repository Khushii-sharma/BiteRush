# BiteRush

## Run locally with Razorpay

Create a private `.env` file once by copying the example:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Open `.env`, add your matching test-mode key ID and key secret from your
Razorpay dashboard, and save it. Django loads this file automatically whenever
it starts, so you do not need to set the variables again in PowerShell.
`.env` is excluded from Git; never commit or share it. Environment variables
already set by the operating system or deployment platform take precedence.

Start Django as usual:

```powershell
python manage.py runserver
```

Checkout displays a configuration message if either variable is missing. If
Razorpay reports an authentication failure, confirm the key ID and secret are
the matching pair and are both test-mode or both live-mode credentials.

## Deploy on Render

1. Push the contents of this `biterush` directory to a GitHub, GitLab, or
   Bitbucket repository.
2. In Render, select **New + → Blueprint** and connect that repository.
   Render will read `render.yaml` to create the Django web service and its
   PostgreSQL database.
3. When prompted, set `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` to your
   Razorpay credentials in the Render dashboard. Use test credentials to test
   payments; use live credentials only when ready to accept real payments.
4. Wait for the first deploy to finish, then open the service's `onrender.com`
   URL.

The Blueprint uses Render's free PostgreSQL plan, which is temporary and
expires after its trial period. Upgrade the database to a paid plan in Render
before relying on it for persistent production data. The free web service may
also spin down when idle.

For subsequent releases, push to the connected Git branch; Render will build,
collect static files, run database migrations at startup, and deploy
automatically.
