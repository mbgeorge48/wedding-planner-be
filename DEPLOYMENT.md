# Deployment Guide (Railway.app)

This guide outlines how to deploy your wedding planner application to [Railway.app](https://railway.app) using the Docker configuration we've set up.

## Prerequisites
1.  A [GitHub](https://github.com) account with your code pushed to a repository.
2.  A [Railway.app](https://railway.app) account.

## Step 1: Create a New Project
1.  Log in to Railway and click **+ New Project**.
2.  Select **Deploy from GitHub repo**.
3.  Choose your wedding planner repository.
4.  Click **Deploy Now**.

## Step 2: Add a Database
1.  In your Railway project dashboard, click **+ Add Service**.
2.  Select **Database** -> **Add PostgreSQL**.
3.  Railway will automatically create the database and provide connection variables.

## Step 3: Configure Environment Variables
1.  Go to the **Variables** tab for your web service in Railway.
2.  Click **Bulk Import** and paste the contents of your local `.env` file (or refer to `.env.example`).
3.  **CRITICAL**: Update the following variables to use Railway's provided database values:
    *   `DB_NAME`: `${{Postgres.PGDATABASE}}`
    *   `DB_USER`: `${{Postgres.PGUSER}}`
    *   `DB_PASSWORD`: `${{Postgres.PGPASSWORD}}`
    *   `DB_HOST`: `${{Postgres.PGHOST}}`
    *   `DB_PORT`: `${{Postgres.PGPORT}}`
4.  Ensure `DEBUG` is set to `False` for production.
5.  Set `ALLOWED_HOSTS` to your Railway domain and eventually your custom domain.

## Step 4: Verification
Railway will automatically detect the `Dockerfile`, build the optimized Tailwind CSS, run migrations via the `entrypoint.sh` script, and start the server. 
1.  Check the **Deployments** tab for build logs.
2.  Once complete, click the generated URL (e.g., `xxx.up.railway.app`) to view your site.

---

## Connecting Your AWS Domain
1.  In Railway, go to **Settings** -> **Domains** -> **Custom Domain**.
2.  Enter your domain (e.g., `rsvp.yourwedding.com`).
3.  Railway will give you a **CNAME** target (e.g., `xxx.up.railway.app`).
4.  Log in to your **AWS Console** -> **Route 53**.
5.  Go to **Hosted Zones** -> select your domain.
6.  Click **Create record**:
    *   **Record name**: `rsvp` (or leave blank for root).
    *   **Record type**: `CNAME`.
    *   **Value**: Paste the Railway target URL.
7.  Wait a few minutes for DNS to propagate. Railway will automatically issue an SSL certificate.

## Ongoing Updates
Every time you `git push` to your GitHub main branch, Railway will automatically:
1.  Re-build your Docker image.
2.  Re-build the optimized Tailwind CSS.
3.  Run any new database migrations.
4.  Zero-downtime deploy the new version.
