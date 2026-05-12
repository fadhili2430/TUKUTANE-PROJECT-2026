package com.tukutane.app

import android.Manifest
import android.annotation.SuppressLint
import android.app.AlarmManager
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.NetworkRequest
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.view.View
import android.webkit.*
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ProgressBar
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import java.util.*

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var swipeRefreshLayout: SwipeRefreshLayout
    private lateinit var progressBar: ProgressBar
    private lateinit var offlineLayout: LinearLayout
    private lateinit var retryButton: Button

    private val TARGET_URL = "https://tukutaneproject.pythonanywhere.com/"
    private var isPageLoaded = false

    companion object {
        const val CHANNEL_ID          = "tukutane_event_reminders"
        const val CHANNEL_NAME        = "Event Reminders"
        const val CHANNEL_DESC        = "Notifications for events you have RSVP'd to"
        const val BADGE_CHANNEL_ID    = "tukutane_badge"
        const val BADGE_NOTIFICATION_ID = 999999
    }

    private val requestNotificationPermission =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { }

    private val requestLocationPermission =
        registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { }

    private val networkCallback = object : ConnectivityManager.NetworkCallback() {
        override fun onAvailable(network: Network) {
            runOnUiThread {
                if (!isPageLoaded) {
                    showWebView()
                    webView.reload()
                }
            }
        }

        override fun onLost(network: Network) {
            runOnUiThread {
                if (!isPageLoaded) {
                    showOfflineScreen()
                }
            }
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView            = findViewById(R.id.webView)
        swipeRefreshLayout = findViewById(R.id.swipeRefreshLayout)
        progressBar        = findViewById(R.id.progressBar)
        offlineLayout      = findViewById(R.id.offlineLayout)
        retryButton        = findViewById(R.id.retryButton)

        createNotificationChannels()
        requestPermissions()
        setupWebView()
        setupSwipeRefresh()
        setupNetworkMonitoring()
        setupBackNavigation()

        retryButton.setOnClickListener {
            if (isConnected()) {
                showWebView()
                webView.loadUrl(TARGET_URL)
            }
        }

        if (isConnected()) {
            webView.loadUrl(TARGET_URL)
        } else {
            showOfflineScreen()
        }
    }

    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val nm = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

            // High-priority channel for event reminder pop-ups
            val reminderChannel = NotificationChannel(
                CHANNEL_ID, CHANNEL_NAME, NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = CHANNEL_DESC
                enableVibration(true)
                enableLights(true)
            }
            nm.createNotificationChannel(reminderChannel)

            // Silent channel used only to drive the launcher icon badge count
            val badgeChannel = NotificationChannel(
                BADGE_CHANNEL_ID, "Upcoming Events", NotificationManager.IMPORTANCE_MIN
            ).apply {
                description = "Shows upcoming RSVP count on the app icon"
                setShowBadge(true)
                setSound(null, null)
                enableVibration(false)
                enableLights(false)
            }
            nm.createNotificationChannel(badgeChannel)
        }
    }

    private fun requestPermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(
                    this, Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                requestNotificationPermission.launch(Manifest.permission.POST_NOTIFICATIONS)
            }
        }

        val fineGranted = ContextCompat.checkSelfPermission(
            this, Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
        val coarseGranted = ContextCompat.checkSelfPermission(
            this, Manifest.permission.ACCESS_COARSE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED

        if (!fineGranted || !coarseGranted) {
            requestLocationPermission.launch(
                arrayOf(
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION
                )
            )
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun setupWebView() {
        val settings = webView.settings
        settings.javaScriptEnabled                  = true
        settings.domStorageEnabled                  = true
        settings.loadWithOverviewMode               = true
        settings.useWideViewPort                    = true
        settings.setSupportZoom(false)
        settings.builtInZoomControls                = false
        settings.displayZoomControls                = false
        settings.cacheMode                          = WebSettings.LOAD_DEFAULT
        settings.mixedContentMode                   = WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE
        settings.mediaPlaybackRequiresUserGesture   = false
        settings.allowFileAccess                    = false
        settings.loadsImagesAutomatically           = true
        settings.javaScriptCanOpenWindowsAutomatically = false
        settings.setGeolocationEnabled(true)

        webView.setBackgroundColor(ContextCompat.getColor(this, R.color.background))
        webView.addJavascriptInterface(TukutaneNotifier(this), "TukutaneAndroid")

        webView.webViewClient = object : WebViewClient() {

            override fun onPageStarted(view: WebView?, url: String?, favicon: android.graphics.Bitmap?) {
                super.onPageStarted(view, url, favicon)
                progressBar.visibility = View.VISIBLE
                progressBar.progress   = 0
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                progressBar.visibility     = View.GONE
                swipeRefreshLayout.isRefreshing = false
                isPageLoaded               = true
            }

            override fun onReceivedError(
                view: WebView?,
                request: WebResourceRequest?,
                error: WebResourceError?
            ) {
                super.onReceivedError(view, request, error)
                if (request?.isForMainFrame == true) {
                    isPageLoaded                    = false
                    progressBar.visibility          = View.GONE
                    swipeRefreshLayout.isRefreshing = false
                    showOfflineScreen()
                }
            }

            @SuppressLint("WebViewClientOnReceivedSslError")
            override fun onReceivedSslError(
                view: WebView?,
                handler: SslErrorHandler?,
                error: android.net.http.SslError?
            ) {
                handler?.proceed()
            }

            override fun shouldOverrideUrlLoading(
                view: WebView?,
                request: WebResourceRequest?
            ): Boolean {
                val url = request?.url?.toString() ?: return false
                return if (url.startsWith("https://tukutaneproject.pythonanywhere.com") ||
                    url.startsWith("http://tukutaneproject.pythonanywhere.com")
                ) {
                    false
                } else {
                    try {
                        startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
                    } catch (e: ActivityNotFoundException) { }
                    true
                }
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                super.onProgressChanged(view, newProgress)
                progressBar.progress = newProgress
                if (newProgress == 100) progressBar.visibility = View.GONE
            }

            override fun onGeolocationPermissionsShowPrompt(
                origin: String?,
                callback: GeolocationPermissions.Callback?
            ) {
                val fineGranted = ContextCompat.checkSelfPermission(
                    this@MainActivity, Manifest.permission.ACCESS_FINE_LOCATION
                ) == PackageManager.PERMISSION_GRANTED
                val coarseGranted = ContextCompat.checkSelfPermission(
                    this@MainActivity, Manifest.permission.ACCESS_COARSE_LOCATION
                ) == PackageManager.PERMISSION_GRANTED

                if (fineGranted || coarseGranted) {
                    callback?.invoke(origin, true, false)
                } else {
                    requestLocationPermission.launch(
                        arrayOf(
                            Manifest.permission.ACCESS_FINE_LOCATION,
                            Manifest.permission.ACCESS_COARSE_LOCATION
                        )
                    )
                    callback?.invoke(origin, false, false)
                }
            }
        }
    }

    private fun setupSwipeRefresh() {
        swipeRefreshLayout.setColorSchemeResources(R.color.colorPrimary)
        swipeRefreshLayout.setOnRefreshListener {
            if (isConnected()) {
                isPageLoaded = false
                webView.reload()
            } else {
                swipeRefreshLayout.isRefreshing = false
                showOfflineScreen()
            }
        }
    }

    private fun setupBackNavigation() {
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (webView.canGoBack()) {
                    webView.goBack()
                } else {
                    isEnabled = false
                    onBackPressedDispatcher.onBackPressed()
                }
            }
        })
    }

    private fun setupNetworkMonitoring() {
        val cm = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val request = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .build()
        cm.registerNetworkCallback(request, networkCallback)
    }

    private fun isConnected(): Boolean {
        val cm = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = cm.activeNetwork ?: return false
        val caps    = cm.getNetworkCapabilities(network) ?: return false
        return caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }

    private fun showWebView() {
        offlineLayout.visibility      = View.GONE
        swipeRefreshLayout.visibility = View.VISIBLE
    }

    private fun showOfflineScreen() {
        swipeRefreshLayout.visibility = View.GONE
        offlineLayout.visibility      = View.VISIBLE
    }

    override fun onDestroy() {
        try {
            val cm = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            cm.unregisterNetworkCallback(networkCallback)
        } catch (e: Exception) { }
        webView.stopLoading()
        webView.destroy()
        super.onDestroy()
    }

    // JavaScript bridge — called by web pages to interact with native Android features
    inner class TukutaneNotifier(private val context: Context) {

        /**
         * Schedule a reminder notification 1 hour before an RSVP'd event.
         */
        @JavascriptInterface
        fun scheduleEventReminder(eventId: Int, title: String, dateStr: String, timeStr: String) {
            try {
                val timeParts = timeStr.split(":")
                val hour   = timeParts.getOrNull(0)?.toIntOrNull() ?: 0
                val minute = timeParts.getOrNull(1)?.toIntOrNull() ?: 0

                val dateParts = dateStr.split("-")
                val year  = dateParts.getOrNull(0)?.toIntOrNull() ?: return
                val month = dateParts.getOrNull(1)?.toIntOrNull() ?: return
                val day   = dateParts.getOrNull(2)?.toIntOrNull() ?: return

                val eventCal = Calendar.getInstance().apply {
                    set(year, month - 1, day, hour, minute, 0)
                    set(Calendar.MILLISECOND, 0)
                    add(Calendar.HOUR_OF_DAY, -1)
                }

                val triggerAt = eventCal.timeInMillis
                if (triggerAt <= System.currentTimeMillis()) return

                val intent = Intent(context, EventReminderReceiver::class.java).apply {
                    putExtra("eventId", eventId)
                    putExtra("title",   title)
                    putExtra("dateStr", dateStr)
                    putExtra("timeStr", timeStr)
                }

                val pendingIntent = PendingIntent.getBroadcast(
                    context, eventId, intent,
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                )

                val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager

                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                    if (alarmManager.canScheduleExactAlarms()) {
                        alarmManager.setExactAndAllowWhileIdle(
                            AlarmManager.RTC_WAKEUP, triggerAt, pendingIntent
                        )
                    } else {
                        alarmManager.set(AlarmManager.RTC_WAKEUP, triggerAt, pendingIntent)
                    }
                } else {
                    alarmManager.setExactAndAllowWhileIdle(
                        AlarmManager.RTC_WAKEUP, triggerAt, pendingIntent
                    )
                }
            } catch (e: Exception) { }
        }

        /**
         * Cancel a previously scheduled reminder.
         */
        @JavascriptInterface
        fun cancelEventReminder(eventId: Int) {
            try {
                val intent = Intent(context, EventReminderReceiver::class.java)
                val pendingIntent = PendingIntent.getBroadcast(
                    context, eventId, intent,
                    PendingIntent.FLAG_NO_CREATE or PendingIntent.FLAG_IMMUTABLE
                )
                pendingIntent?.let {
                    val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
                    alarmManager.cancel(it)
                    it.cancel()
                }
            } catch (e: Exception) { }
        }

        /**
         * Update the launcher icon badge with the number of upcoming RSVP'd events.
         * Called by the RSVPs page every time it loads.
         * Uses a silent, ongoing notification so the count appears on the icon
         * without making a sound or showing a heads-up banner.
         */
        @JavascriptInterface
        fun setBadgeCount(count: Int) {
            try {
                val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

                if (count <= 0) {
                    nm.cancel(BADGE_NOTIFICATION_ID)
                    return
                }

                val label = if (count == 1) "1 upcoming event" else "$count upcoming events"

                val tapIntent = Intent(context, MainActivity::class.java).apply {
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP
                }
                val tapPendingIntent = PendingIntent.getActivity(
                    context, 0, tapIntent,
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                )

                val notification = NotificationCompat.Builder(context, BADGE_CHANNEL_ID)
                    .setSmallIcon(R.drawable.ic_tukutane_logo)
                    .setContentTitle(label)
                    .setContentText("Tap to view your RSVPs")
                    .setNumber(count)
                    .setPriority(NotificationCompat.PRIORITY_MIN)
                    .setOngoing(true)
                    .setVisibility(NotificationCompat.VISIBILITY_SECRET)
                    .setSilent(true)
                    .setContentIntent(tapPendingIntent)
                    .build()

                nm.notify(BADGE_NOTIFICATION_ID, notification)
            } catch (e: Exception) { }
        }

        /**
         * Returns true so web pages can detect they are running inside the Android app.
         */
        @JavascriptInterface
        fun isNativeApp(): Boolean = true
    }
}
