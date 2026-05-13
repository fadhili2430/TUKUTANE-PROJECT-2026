package com.tukutane.app

import android.app.AlertDialog
import android.content.ActivityNotFoundException
import android.content.Intent
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.webkit.*
import android.widget.Button
import android.widget.TextView
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AppCompatActivity
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
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
    private val CURRENT_VERSION = "1.0.0"
    private var updateDialogShown = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webView)
        swipeRefresh = findViewById(R.id.swipeRefresh)
        offlineLayout = findViewById(R.id.offlineLayout)
        retryButton = findViewById(R.id.retryButton)
        offlineText = findViewById(R.id.offlineText)

        setupWebView()
        setupSwipeRefresh()
        setupBackNavigation()

        if (isOnline()) {
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
                    false // load inside WebView
                } else {
                    try {
                        startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
                    } catch (e: ActivityNotFoundException) {
                        // ignore
                    }
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
        swipeRefresh.setColorSchemeColors(
            resources.getColor(R.color.primary, theme)
        )
        swipeRefresh.setOnRefreshListener {
            if (isOnline()) {
                showWebView()
                webView.reload()
            } else {
                swipeRefresh.isRefreshing = false
                showOffline()
            }
        }
    }

    private fun setupBackNavigation() {
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (webView.canGoBack()) {
                    webView.goBack()
                } else {
                    finish()
                }
            }
        })
    }

    // ── Auto-update check ────────────────────────────────────────────────────
    private fun checkForUpdate() {
        if (updateDialogShown) return
        Thread {
            try {
                val conn = URL(VERSION_URL).openConnection() as HttpURLConnection
                conn.connectTimeout = 5000
                conn.readTimeout = 5000
                conn.requestMethod = "GET"
                if (conn.responseCode == 200) {
                    val body = conn.inputStream.bufferedReader().readText()
                    val json = JSONObject(body)
                    val latestVersion = json.getString("version")
                    val downloadUrl = json.optString("download_url", "")
                    if (isNewerVersion(latestVersion, CURRENT_VERSION)) {
                        runOnUiThread {
                            showUpdateDialog(latestVersion, downloadUrl)
                        }
                    }
                }
                conn.disconnect()
            } catch (e: Exception) {
                // Silently ignore — update check is best-effort
            }
        }.start()
    }

    private fun isNewerVersion(latest: String, current: String): Boolean {
        return try {
            val lParts = latest.split(".").map { it.toInt() }
            val cParts = current.split(".").map { it.toInt() }
            for (i in 0 until maxOf(lParts.size, cParts.size)) {
                val l = lParts.getOrElse(i) { 0 }
                val c = cParts.getOrElse(i) { 0 }
                if (l > c) return true
                if (l < c) return false
            }
            false
        } catch (e: Exception) { false }
    }

    private fun showUpdateDialog(newVersion: String, downloadUrl: String) {
        if (updateDialogShown || isFinishing) return
        updateDialogShown = true
        AlertDialog.Builder(this)
            .setTitle("Update Available 🎉")
            .setMessage("A new version of Tukutane (v$newVersion) is available.\n\nUpdate now to get the latest features and improvements.")
            .setPositiveButton("Update Now") { _, _ ->
                val url = downloadUrl.ifEmpty { "https://github.com/fadhili2430/TUKUTANE-PROJECT-2026/releases/latest" }
                try {
                    startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
                } catch (e: ActivityNotFoundException) { }
            }
            .setNegativeButton("Later", null)
            .setCancelable(true)
            .show()
    }

    // ── Online/offline helpers ───────────────────────────────────────────────
    private fun isOnline(): Boolean {
        val cm = getSystemService(CONNECTIVITY_SERVICE) as ConnectivityManager
        val net = cm.activeNetwork ?: return false
        val caps = cm.getNetworkCapabilities(net) ?: return false
        return caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }

    private fun showOffline() {
        offlineLayout.visibility = View.VISIBLE
        swipeRefresh.visibility = View.GONE
    }

    private fun showWebView() {
        offlineLayout.visibility = View.GONE
        swipeRefresh.visibility = View.VISIBLE
    }
}
