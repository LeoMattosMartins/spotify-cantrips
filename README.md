# Cantrips

Modular, gesture-based Spotify controller with a headless Python CV engine and transparent Electron HUD.

## Architecture

- `engine/` (Python 3.10+): MediaPipe/OpenCV hand tracking + command strategy pipeline.
- `hud/` (Electron): click-through transparent overlay for telemetry visuals.
- WebSocket bridge: JSON telemetry over `ws://127.0.0.1:8765`.

## Implemented Gesture Grimoire

- Upward vertical swipe: summon HUD (`SYSTEM_ACTIVE = true`)
- Downward vertical swipe: dismiss HUD (`SYSTEM_ACTIVE = false`)
- Open palm: play/resume (only when active)
- Closed fist: pause (only when active)
- Swipe right: next track (only when active)
- Swipe left: previous track (only when active)

## Runtime Rules Included

- Spatial engagement zone enforced for non-system gestures (configurable, default center 80% of frame).
- 1000ms global debounce for discrete Spotify commands.
- Active device verification before each Spotify command.
- Low-power listen mode at 15 FPS when HUD/system is inactive.
- Landmark broadcasting disabled in low-power mode.
- Debug overlay always visible when HUD is on screen (engagement zone + velocity telemetry).
- Swipe gestures use re-arm gating to prevent repeated triggers when the hand is held in one direction.

## 1) Spotify App Setup (required)

Each person cloning this repo must use their own Spotify Developer app and log in with their own account.

1. Go to `https://developer.spotify.com/dashboard`.
2. Create an app (name can be anything, e.g. `Cantrips Local`).
3. Open the app settings and add this Redirect URI:
   - `http://127.0.0.1:8888/callback`
4. Copy your app credentials:
   - `Client ID`
   - `Client Secret`

Keep these private. Never paste them into tracked files.

## 2) Local Environment Setup

### Python engine (macOS)

```bash
uv venv .venv
uv pip install -r requirements.txt
cp .env.example .env
```

If `uv` is not installed:

```bash
brew install uv
```

Edit `.env` and set:

```dotenv
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

### Electron HUD

```bash
cd hud
npm install
```

## 3) Launch Cantrips

Run both processes from a single terminal:

```bash
chmod +x run_cantrips.sh
./run_cantrips.sh
```

This starts the Python engine and the Electron HUD together.
Use `Ctrl+C` in that same terminal to stop both.

On first launch, your browser opens Spotify OAuth login/consent. Sign in with your Spotify account and approve access

## 4) Verify it is wired correctly

- Start playback in the Spotify desktop app.
- Run Cantrips and keep your hand in the center zone.
- Upward swipe: HUD appears with debug box and hand skeleton.
- Open palm: resume, closed fist: pause.
- Swipe right: next track, swipe left: previous track.

## Security and Secrets

- `.env` is ignored by git and must stay local.
- `.spotify-cache` (OAuth token cache) is ignored by git and must stay local.
- Never commit credentials or token cache files.
- `.env.example` is safe to commit; it contains placeholders only.
- Put your personal `Client ID` and `Client Secret` only in local `.env`, never in `README.md`, source files, or commits.

Because auth is local and untracked, anyone who clones this repo must provide their own Spotify app credentials and login themselves.

## Troubleshooting

- If commands do nothing, confirm a Spotify device is active and currently playing.
- If auth fails, confirm Redirect URI in Spotify dashboard exactly matches `.env`.
- If webcam does not open, set `CANTRIPS_CAMERA_INDEX` in `.env`.
- If you want to reset auth, delete local `.spotify-cache` and restart the engine.
