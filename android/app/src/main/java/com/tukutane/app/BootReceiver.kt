package com.tukutane.app

  import android.content.BroadcastReceiver
  import android.content.Context
  import android.content.Intent

  class BootReceiver : BroadcastReceiver() {
      override fun onReceive(context: Context, intent: Intent) {
          if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
              // Reminders are re-scheduled when the user next opens the app and visits their RSVPs page.
          }
      }
  }