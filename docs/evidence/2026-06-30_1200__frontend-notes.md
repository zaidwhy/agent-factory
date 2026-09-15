## Receipts.dev Frontend - Setup and Run Notes

### Install and run

```bash
cd output/web
npm install
npm run dev
```

Dev server runs at: http://localhost:3000

### Environment variables

Copy `.env.local.example` to `.env.local`:

```bash
cp .env.local.example .env.local
```

Required variables:
- `NEXT_PUBLIC_API_URL` - FastAPI backend URL (default: `http://localhost:8000`)
- `NEXT_PUBLIC_APP_URL` - Frontend URL for generating share links (default: `http://localhost:3000`)

### Backend expected at

`http://localhost:8000` by default. Change `NEXT_PUBLIC_API_URL` in `.env.local` if your backend runs elsewhere.

The backend must have CORS configured to allow `http://localhost:3000`.

### GitHub OAuth setup

Create an OAuth App at https://github.com/settings/developers:
- Homepage URL: `http://localhost:3000`
- Authorization callback URL: `http://localhost:8000/api/v1/auth/github/callback`

Set `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` in `api/.env`.

### Build for production

```bash
npm run build
npm run start
```

### Docker

The frontend has a `Dockerfile`. Build args `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_APP_URL` must be passed at build time (Next.js bakes public env vars into the bundle):

```bash
docker build \
  --build-arg NEXT_PUBLIC_API_URL=https://api.receipts.dev \
  --build-arg NEXT_PUBLIC_APP_URL=https://receipts.dev \
  -t receipts-web .
```

### Architecture notes

- **App Router** (Next.js 15) - all routes use the `src/app/` directory
- **SSR profile pages** (`/[slug]/page.tsx`) - server-fetches profile + skills, generates OG metadata server-side, ISR revalidate=3600
- **Client pages** - dashboard, auth callback, and chat page are `"use client"` components
- **Auth** - JWT lives in an httpOnly cookie set by the backend. The Zustand store (`useAuth`) holds the decoded user object for UI rendering. All Axios requests use `withCredentials: true` to send the cookie automatically.
- **Chat session** - `session_token` is held in React component state (never persisted to localStorage since it has a 24-hour TTL and carries no PII)
- **Polling** - `useIndexStatus` polls GET /index/status every 5 seconds while status is queued/running, stops automatically when done/failed

### Key pages

| Route | Description |
|---|---|
| `/` | Landing page (SSR) |
| `/auth/callback` | OAuth callback handler (client) |
| `/dashboard` | Protected - repo list + indexing controls |
| `/[slug]` | Public profile (SSR + ISR) |
| `/[slug]/chat` | Recruiter chat interface (client) |
