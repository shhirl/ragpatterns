# DEPLOY — how ragpatterns.com gets from this repo to the internet

Written 9 September 2026. This is the whole hosting story; there is nothing else to know.

## The shape

```
laptop ── branch ── pull request ──▶ GitHub  shhirl/ragpatterns  (public, main protected)
                        │                          │
                        │ preview URL              │ merge to main
                        ▼                          ▼
              <branch>.ragpatterns.pages.dev   Cloudflare Pages ──▶ ragpatterns.com  (~20 s)
```

- **Static pages only** (`index.html`, `how-its-built.html`, `docs/`). No build step, no server. Cloudflare Pages serves the repo root as-is.
- **Railway is not used yet.** It enters at v1, when the Python service exists, at `api.ragpatterns.com`; the pages stay static and call it. Same setup as fixmybanana.com, but the pages themselves never move to Railway.
- The domain is registered at Cloudflare (bought 9 Sep 2026), so DNS for Pages is one click and there is nothing to point elsewhere.

## GitHub (done)

- Repo: https://github.com/shhirl/ragpatterns, public. Public because branch protection is free only on public repos, and because the site is a portfolio piece. The curated exports are git-ignored and were never committed; see `CLAUDE.md` for the privacy rules.
- `main` is protected: pull requests required, no direct pushes, no force pushes, no deletion, rules apply to admins too. Set with the GitHub API on 9 Sep 2026; visible under Settings → Branches.
- Every change is a branch + pull request. Shirley merges. An AI session opens PRs and never merges them.
- `.github/PULL_REQUEST_TEMPLATE.md` carries the checklist.

## Cloudflare Pages (done 9 Sep 2026)

Connected on 9 September 2026 by Claude driving Shirley's browser; she entered the GitHub sudo password herself. Project `ragpatterns`, production branch `main`, no build command, output `/`. Custom domains `ragpatterns.com` and `www.ragpatterns.com` both active; Cloudflare added the CNAME records to `ragpatterns.pages.dev` itself. First production deploy was the merge of PR #1. The GitHub app "Cloudflare Workers and Pages" has access to exactly two repos: `ragpatterns` and `shhirl-site`.

`_redirects` at the repo root sends `/docs/*` to `/` with a 302, so the build plan and design mockups are readable in the repo but not on the site. Cloudflare evaluates `_redirects` before static assets.

One Pages behaviour to know: it serves clean URLs, so `/how-its-built.html` answers 308 to `/how-its-built`. Internal links keep the `.html` (the local preview needs it); the redirect is free and cached.

The steps, kept for the next site:

1. Cloudflare dashboard → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**.
2. Pick the GitHub account `shhirl` (authorise the Cloudflare GitHub app if asked; grant it only `ragpatterns`) → repository **ragpatterns**.
3. Build settings: production branch `main`, framework preset **None**, build command *empty*, build output directory `/` (root). Save and deploy. First deploy takes under a minute and lands at `ragpatterns.pages.dev`.
4. Project → **Custom domains** → **Set up a custom domain** → `ragpatterns.com` → Cloudflare adds the DNS record itself because the zone is in the same account. Repeat for `www.ragpatterns.com` so both work; Pages redirects www to the apex.
5. Project → **Settings** → **Builds & deployments**: leave **Preview deployments** on "All branches" (default). Every pull request then gets a comment with its own preview URL; that is what the PR checklist asks to open.

After step 4 the loop is: merge a PR → live in about twenty seconds. There are no deploy commands.

## Rollback

Cloudflare Pages keeps every deployment. Project → **Deployments** → pick the previous one → **Rollback to this deployment**. Or revert the merge commit on GitHub through a PR; either is fine, the second leaves a record.

## When v1 adds the service

- New Railway project from the same repo, root directory `service/`, same pattern as fixmybanana (`railway.json`, `Procfile`, gunicorn). Custom domain `api.ragpatterns.com` added in Railway; Cloudflare gets a CNAME (proxied) to the Railway target.
- API keys live only in Railway variables and in a git-ignored `.env` locally. Nothing in the pages.
- Pages call the service with `fetch('https://api.ragpatterns.com/...')`. The service must send `Access-Control-Allow-Origin: https://ragpatterns.com`.
- Document it here when it happens, with the date.
