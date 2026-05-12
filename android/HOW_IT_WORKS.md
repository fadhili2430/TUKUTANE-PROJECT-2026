# How the Tukutane APK Works

## Architecture Overview

```
┌─────────────────────────────────────┐
│         Android Device              │
│                                     │
│  ┌─────────────────────────────┐    │
│  │      SplashActivity         │    │
│  │  (1.8s branded intro)       │    │
│  └────────────┬────────────────┘    │
│               │                     │
│  ┌────────────▼────────────────┐    │
│  │       MainActivity          │    │
│  │                             │    │
│  │  ┌──────────────────────┐   │    │
│  │  │  SwipeRefreshLayout  │   │    │
│  │  │  ┌────────────────┐  │   │    │
│  │  │  │    WebView     │  │   │    │
│  │  │  │                │  │   │    │
│  │  │  │  tukutane      │  │   │    │
│  │  │  │  project       │  │   │    │
│  │  │  │  website       │  │   │    │
│  │  │  └────────────────┘  │   │    │
│  │  └──────────────────────┘   │    │
│  │  ┌──────────────────────┐   │    │
│  │  │  OfflineScreen       │   │    │
│  │  │  (shown if no net)   │   │    │
│  │  └──────────────────────┘   │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

---

## Adaptability Features Explained

### 1. Responsive WebView
The WebView is configured with:
- `useWideViewPort = true` — tells the site to use its full responsive layout
- `loadWithOverviewMode = true` — fits the page width to the screen
- Zoom disabled — the website's own responsive CSS handles scaling

### 2. Pull-to-Refresh (SwipeRefreshLayout)
Wraps the WebView so the user can swipe down to reload the page — works just like native apps.

### 3. Network Detection & Offline Screen
- Monitors network state in real time via `ConnectivityManager.NetworkCallback`
- If the internet drops → shows a friendly offline screen
- When internet returns → automatically reloads the page
- "Try Again" button for manual retry

### 4. Progress Bar
A thin horizontal progress bar at the top shows page load progress (0–100%), then disappears — mimics browser UX.

### 5. Back Navigation
`onBackPressed()` checks if the WebView has history. If yes → goes back one page. If no → exits the app. This makes browsing feel native.

### 6. Splash Screen
A 1.8-second branded splash with the app icon, then transitions smoothly to the main screen.

### 7. External Link Handling
Links that go outside `tukutaneproject.pythonanywhere.com` open in the device's browser, keeping the app focused.

### 8. Hardware Acceleration
Enabled app-wide for smooth scrolling and rendering.

### 9. Orientation Support
The app handles `orientation|screenSize|keyboardHidden` config changes without restarting the WebView.

### 10. Security
- HTTPS enforced via `network_security_config.xml`
- No cleartext (HTTP) traffic allowed
- ProGuard enabled in release builds to shrink and obfuscate code

---

## How the APK is Built (GitHub Actions)

```
Your Code (GitHub repo)
        │
        ▼
  GitHub Actions triggers on push
        │
        ▼
  ubuntu-latest runner
        │
  ┌─────▼──────────────────────┐
  │  1. Checkout code           │
  │  2. Setup JDK 17            │
  │  3. Setup Android SDK       │
  │  4. Cache Gradle (faster)   │
  │  5. ./gradlew assembleDebug │ ← Always runs → debug APK
  │  6. ./gradlew assembleRelease│ ← Runs if keystore secrets set
  └─────────────────────────────┘
        │
        ▼
  APK uploaded as artifact
  (downloadable from Actions tab)
```

### Debug vs Release APK
| Feature | Debug APK | Release APK |
|---|---|---|
| Signing | Auto (debug key) | Your keystore |
| Install anywhere | Yes | Needs keystore match |
| Play Store ready | No | Yes |
| Size | Larger | Smaller (minified) |
| Speed | Same | Slightly faster |

---

## Steps to Get Your APK

### Step 1 — Push to GitHub
Create a GitHub repo and push this project to it.

### Step 2 — GitHub Actions runs automatically
Go to the **Actions** tab in your repo. You'll see the build running. It takes about 3–5 minutes.

### Step 3 — Download the APK
Once the build completes:
- Click the workflow run
- Scroll to **Artifacts**
- Download `tukutane-debug` (zip containing the APK)

### Step 4 — Install on your phone
Enable **"Install from unknown sources"** in Android settings, then open the APK file.

---

## For a Signed Release APK (Play Store ready)

You need to add 4 GitHub secrets:
| Secret Name | Value |
|---|---|
| `KEYSTORE_BASE64` | Your `.jks` file encoded as base64 |
| `KEYSTORE_PASSWORD` | Password for the keystore |
| `KEY_ALIAS` | Key alias name |
| `KEY_PASSWORD` | Key password |

Generate a keystore with:
```bash
keytool -genkey -v -keystore tukutane.jks -keyalg RSA -keysize 2048 -validity 10000 -alias tukutane
```

Then encode it:
```bash
base64 tukutane.jks
```

Paste the output as the `KEYSTORE_BASE64` secret.
