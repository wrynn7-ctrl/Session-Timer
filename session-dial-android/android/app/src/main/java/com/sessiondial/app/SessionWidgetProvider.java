package com.sessiondial.app;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.SystemClock;
import android.widget.RemoteViews;

/**
 * The home screen widget: the session's status, its running time and one button that reads
 * "Start session" or "End and log".
 *
 * The widget does not run the timer. The page inside the app does, and tells this class what to
 * show through WidgetBridgePlugin. Tapping the button opens the app with a note saying which
 * button it was, and the page then starts or ends the session exactly as its own buttons would.
 * That keeps the chimes and the session log in one place.
 */
public class SessionWidgetProvider extends AppWidgetProvider {

    /** Where the last state sent by the page is kept, so the widget can be redrawn at any time. */
    static final String PREFS = "session_widget";
    static final String ACTION_START = "com.sessiondial.app.WIDGET_START";
    static final String ACTION_END = "com.sessiondial.app.WIDGET_END";
    /** Marks each tap so the same one is never acted on twice. */
    static final String EXTRA_TOKEN = "token";

    /** Android calls this when a widget is added, after a restart, and every half hour. */
    @Override
    public void onUpdate(Context context, AppWidgetManager manager, int[] ids) {
        manager.updateAppWidget(ids, render(context));
    }

    /** Redraws every copy of the widget. Called whenever the page reports a change. */
    static void updateAll(Context context) {
        AppWidgetManager manager = AppWidgetManager.getInstance(context);
        int[] ids = manager.getAppWidgetIds(new ComponentName(context, SessionWidgetProvider.class));
        if (ids.length > 0) manager.updateAppWidget(ids, render(context));
    }

    private static RemoteViews render(Context context) {
        SharedPreferences p = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        String status = p.getString("status", "idle");
        boolean running = "running".equals(status);
        boolean idle = !running && !"paused".equals(status);
        // Same sum as elapsedMs() in index.html: banked time plus the current stretch.
        long elapsed = idle ? 0
            : p.getLong("accumulated", 0) + (running ? Math.max(0, System.currentTimeMillis() - p.getLong("runStart", 0)) : 0);

        RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.widget_session);
        int statusText = idle ? R.string.widget_ready : running ? R.string.widget_running : R.string.widget_paused;
        views.setTextViewText(R.id.widget_status, context.getString(statusText, p.getInt("targetMin", 53)));
        // Android's own ticking clock view. Given the moment the count began, it keeps itself up
        // to date while running, so the widget needs no updates in between.
        views.setChronometer(R.id.widget_time, SystemClock.elapsedRealtime() - elapsed, null, running);
        views.setTextViewText(R.id.widget_button, context.getString(idle ? R.string.widget_start : R.string.widget_end));
        views.setOnClickPendingIntent(R.id.widget_button, openApp(context, idle ? ACTION_START : ACTION_END, idle ? 1 : 2));
        views.setOnClickPendingIntent(R.id.widget_root, openApp(context, Intent.ACTION_MAIN, 0));
        return views;
    }

    private static PendingIntent openApp(Context context, String action, int requestCode) {
        Intent intent = new Intent(context, MainActivity.class)
            .setAction(action)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            .putExtra(EXTRA_TOKEN, System.currentTimeMillis());
        return PendingIntent.getActivity(context, requestCode, intent,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }
}
