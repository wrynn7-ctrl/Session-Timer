package com.sessiondial.app;

import android.appwidget.AppWidgetManager;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import org.json.JSONObject;

/**
 * The link between the page and the home screen widget, in both directions.
 *
 * Page to widget: update() stores the timer's state and redraws the widget.
 * Widget to page: when a widget button opens the app, takeAction() (app just started) or the
 * "widgetAction" event (app already open) tells the page which button it was.
 */
@CapacitorPlugin(name = "WidgetBridge")
public class WidgetBridgePlugin extends Plugin {

    private SharedPreferences prefs() {
        return getContext().getSharedPreferences(SessionWidgetProvider.PREFS, Context.MODE_PRIVATE);
    }

    /** The page calls this after every change to the timer. */
    @PluginMethod
    public void update(PluginCall call) {
        JSONObject data = call.getData();
        prefs().edit()
            .putString("status", data.optString("status", "idle"))
            .putLong("runStart", data.optLong("runStart", 0))
            .putLong("accumulated", data.optLong("accumulated", 0))
            .putInt("targetMin", data.optInt("targetMin", 53))
            .apply();
        SessionWidgetProvider.updateAll(getContext());
        call.resolve();
    }

    /** Asked once when the page loads: was the app opened by a widget button? */
    @PluginMethod
    public void takeAction(PluginCall call) {
        JSObject ret = new JSObject();
        String action = consume(getActivity().getIntent());
        if (action != null) ret.put("action", action);
        call.resolve(ret);
    }

    /** A widget button was tapped while the app was already open. */
    @Override
    protected void handleOnNewIntent(Intent intent) {
        super.handleOnNewIntent(intent);
        String action = consume(intent);
        if (action == null) return;
        JSObject data = new JSObject();
        data.put("action", action);
        notifyListeners("widgetAction", data, true); // true: keep it until the page is listening
    }

    /** Returns "start" or "end" for a widget tap that has not been handled yet, otherwise null. */
    private String consume(Intent intent) {
        if (intent == null) return null;
        String action = SessionWidgetProvider.ACTION_START.equals(intent.getAction()) ? "start"
            : SessionWidgetProvider.ACTION_END.equals(intent.getAction()) ? "end" : null;
        if (action == null) return null;
        // Android can hand the app the same intent again, for example when it is reopened from
        // the recent apps list. Each tap carries a token; one already seen is ignored.
        long token = intent.getLongExtra(SessionWidgetProvider.EXTRA_TOKEN, 0);
        if (token != 0 && token == prefs().getLong("lastToken", 0)) return null;
        prefs().edit().putLong("lastToken", token).apply();
        SessionWidgetProvider.updateAll(getContext()); // gives the buttons fresh tokens
        return action;
    }

    /** Can this launcher add the widget when the app asks, or only by hand? */
    @PluginMethod
    public void canPin(PluginCall call) {
        JSObject ret = new JSObject();
        ret.put("value", Build.VERSION.SDK_INT >= Build.VERSION_CODES.O
            && AppWidgetManager.getInstance(getContext()).isRequestPinAppWidgetSupported());
        call.resolve(ret);
    }

    /** Opens the launcher's "add to home screen" prompt for the widget. */
    @PluginMethod
    public void requestPin(PluginCall call) {
        JSObject ret = new JSObject();
        boolean requested = false;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            requested = AppWidgetManager.getInstance(getContext()).requestPinAppWidget(
                new ComponentName(getContext(), SessionWidgetProvider.class), null, null);
        }
        ret.put("requested", requested);
        call.resolve(ret);
    }
}
