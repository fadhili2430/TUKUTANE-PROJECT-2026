package com.tukutane.app

import android.Manifest
import android.app.AlertDialog
import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.view.View
import android.webkit.*
import android.widget.Button
import android.widget.TextView
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import com.google.firebase.messaging.FirebaseMessaging
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var swipeRefresh: SwipeRefreshLayout
    private lateinit var offlineLayout: View
    private lateinit var retryButton: Button
    private lateinit var offlineText: TextView

    private val TARGET_URL = "https://tukutaneproject.pythonanywhere.com/"
    private val VERSION_URL = "https://tukutaneproject.pythonanywhere.com/api/version"
    private val CURRENT_VERSION = "1.0.7"
    private var updateDialogShown = false
    private var tokenSyncDone = false

    private val notifPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { /* no-op — notification works regardless */ }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView       = findViewById(R.id.webView)
        swipeRefresh  = findViewById(R.id.swipeRefresh)
        offlineLayout = findViewById(R.id.offlineLayout)
        retryButton   = findViewById(R.id.retryButton)
        offlineText   = findViewById(R.id.offlineText)

        requestNotificationPermission()
        setupWebView()
        setupSwipeRefresh()
        setupBackNavigation()

        val openUrl = intent.getStringExtra("open_url")
        if (!openUrl.isNullOrEmpty() && isOnline()) {
            showWebView()
            webView.loadUrl(openUrl)
        } else if (isOnline()) {
            webView.loadUrl(TARGET_URL)
            checkForUpdate()
        } else {
            showOffline()
        }

        retryButton.setOnClickListener {
            if (isOnline()) {
                showWebView()
                webView.loadUrl(TARGET_URL)
            } else {
                offlineText.text = "Still no connection. Please check your internet."
            }
        }
    }

    private fun requestNotificationPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED) {
                notifPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
            }
        }
    }

    // ── FCM token sync ────────────────────────────────────────────────────────
    private fun syncFcmToken() {
        if (tokenSyncDone) return
        val prefs = getSharedPreferences("tukutane_prefs", Context.MODE_PRIVATE)
        val alreadySynced = prefs.getBoolean("token_synced", false)

        FirebaseMessaging.getInstance().token.addOnSuccessListener { token ->
            if (token.isNotEmpty()) {
                prefs.edit().putString("fcm_token", token).apply()
                if (!alreadySynced) {
                    sendTokenToServer(token)
                }
            }
        }
    }

    private fun sendTokenToServer(token: String) {
        // Use the WebView to POST the token — it already has the session cookie
        val js = """
            (function() {
                var fd = new FormData();
                fd.append('token', '$token');
                fetch('/api/fcm-token', {
                    method: 'POST',
                    body: fd,
                    credentials: 'same-origin'
                }).then(function(r) {
                    if (r.ok) {
                        console.log('FCM token synced');
                    }
                }).catch(function(e) { console.log('FCM sync error', e); });
            })();
        """.trimIndent()
        webView.evaluateJavascript(js, null)
        getSharedPreferences("tukutane_prefs", Context.MODE_PRIVATE)
            .edit().putBoolean("token_synced", true).apply()
        tokenSyncDone = true
    }

    private fun setupWebView() {
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            loadWithOverviewMode = true
            useWideViewPort = true
            setSupportZoom(false)
            builtInZoomControls = false
            displayZoomControls = false
            mixedContentMode = WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE
            cacheMode = WebSettings.LOAD_DEFAULT
            userAgentString = userAgentString + " TukutaneApp/1.0"
        }

        webView.webViewClient = object : WebViewClient() {
            override fun onPageStarted(view: WebView?, url: String?, favicon: android.graphics.Bitmap?) {
                super.onPageStarted(view, url, favicon)
                swipeRefresh.isRefreshing = true
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                swipeRefresh.isRefreshing = false
                // Sync FCM token when user is logged in (on dashboard or any auth page)
                if (url != null && (url.contains("/dashboard") || url.contains("/profile")
                            || url.contains("/rsvp") || url.contains("/organizer"))) {
                    syncFcmToken()
                }
            }

            override fun onReceivedError(view: WebView?, request: WebResourceRequest?, error: WebResourceError?) {
                super.onReceivedError(view, request, error)
                if (request?.isForMainFrame == true) {
                    swipeRefresh.isRefreshing = false
                    if (!isOnline()) showOffline()
                }
            }

            override fun onReceivedSslError(view: WebView?, handler: SslErrorHandler?, error: SslError?) {
                handler?.cancel()
            }

            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val url = request?.url?.toString() ?: return false
                return if (url.startsWith("http://") || url.startsWith("https://")) {
                    false
                } else {
                    try { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) }
                    catch (e: ActivityNotFoundException) { }
                    true
                }
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onGeolocationPermissionsShowPrompt(origin: String?, callback: GeolocationPermissions.Callback?) {
                callback?.invoke(origin, true, false)
            }
        }
    }

    private fun setupSwipeRefresh() {
        swipeRefresh.setColorSchemeColors(resources.getColor(R.color.primary, theme))
        swipeRefresh.setOnRefreshListener {
            if (isOnline()) { showWebView(); webView.reload() }
            else { swipeRefresh.isRefreshing = false; showOffline() }
        }
    }

    private fun setupBackNavigation() {
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (webView.canGoBack()) webView.goBack() else finish()
            }
        })
    }

    // ── Auto-update check ────────────────────────────────────────────────────
    private fun checkForUpdate() {
        if (updateDialogShown) return
        Thread {
            try {
                val conn = URL(VERSION_URL).openConnection() as HttpURLConnection
                conn.connectTimeout = 5000; conn.readTimeout = 5000
                conn.requestMethod = "GET"
                if (conn.responseCode == 200) {
                    val body = conn.inputStream.bufferedReader().readText()
                    val json = JSONObject(body)
                    val latest = json.getString("version")
                    val dlUrl  = json.optString("download_url", "")
                    if (isNewerVersion(latest, CURRENT_VERSION)) {
                        runOnUiThread { showUpdateDialog(latest, dlUrl) }
                    }
                }
                conn.disconnect()
            } catch (e: Exception) { }
        }.start()
    }

    private fun isNewerVersion(latest: String, current: String): Boolean {
        return try {
            val l = latest.split(".").map { it.toInt() }
            val c = current.split(".").map { it.toInt() }
            for (i in 0 until maxOf(l.size, c.size)) {
                val lv = l.getOrElse(i) { 0 }; val cv = c.getOrElse(i) { 0 }
                if (lv > cv) return true; if (lv < cv) return false
            }
            false
        } catch (e: Exception) { false }
    }

    private fun showUpdateDialog(newVersion: String, downloadUrl: String) {
        if (updateDialogShown || isFinishing) return
        updateDialogShown = true
        AlertDialog.Builder(this)
            .setTitle("Update Available 🎉")
            .setMessage("Tukutane v$newVersion is ready.\n\nInstall over your current version — no uninstall needed.")
            .setPositiveButton("Update Now") { _, _ ->
                val url = downloadUrl.ifEmpty { "https://github.com/fadhili2430/TUKUTANE-PROJECT-2026/releases/latest" }
                try { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) }
                catch (e: ActivityNotFoundException) { }
            }
            .setNegativeButton("Later", null)
            .setCancelable(true).show()
    }

    private fun isOnline(): Boolean {
        val cm = getSystemService(CONNECTIVITY_SERVICE) as ConnectivityManager
        val caps = cm.getNetworkCapabilities(cm.activeNetwork ?: return false) ?: return false
        return caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }

    private fun showOffline() { offlineLayout.visibility = View.VISIBLE; swipeRefresh.visibility = View.GONE }
    private fun showWebView() { offlineLayout.visibility = View.GONE; swipeRefresh.visibility = View.VISIBLE }
}
