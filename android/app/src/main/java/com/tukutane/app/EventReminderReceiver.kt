package com.tukutane.app

  import android.app.NotificationManager
  import android.app.PendingIntent
  import android.content.BroadcastReceiver
  import android.content.Context
  import android.content.Intent
  import androidx.core.app.NotificationCompat

  class EventReminderReceiver : BroadcastReceiver() {

      override fun onReceive(context: Context, intent: Intent) {
          val eventId = intent.getIntExtra("eventId", 0)
          val title = intent.getStringExtra("title") ?: "Your event is starting soon"
          val dateStr = intent.getStringExtra("dateStr") ?: ""
          val timeStr = intent.getStringExtra("timeStr") ?: ""

          val tapIntent = Intent(context, SplashActivity::class.java).apply {
              flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
          }
          val tapPendingIntent = PendingIntent.getActivity(
              context, eventId, tapIntent,
              PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
          )

          val timeDisplay = if (timeStr.length >= 5) timeStr.substring(0, 5) else timeStr
          val bodyText = if (dateStr.isNotEmpty() && timeStr.isNotEmpty()) {
              "Reminder: \"$title\" starts at $timeDisplay on $dateStr. See you there!"
          } else {
              "Reminder: \"$title\" is coming up soon. See you there!"
          }

          val notification = NotificationCompat.Builder(context, MainActivity.CHANNEL_ID)
              .setSmallIcon(R.drawable.ic_tukutane_logo)
              .setContentTitle("Event Reminder - Tukutane")
              .setContentText(bodyText)
              .setStyle(NotificationCompat.BigTextStyle().bigText(bodyText))
              .setPriority(NotificationCompat.PRIORITY_HIGH)
              .setAutoCancel(true)
              .setVibrate(longArrayOf(0, 300, 200, 300))
              .setContentIntent(tapPendingIntent)
              .build()

          val notificationManager =
              context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
          notificationManager.notify(eventId, notification)
      }
  }