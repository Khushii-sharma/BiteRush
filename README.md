# BiteRush

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
