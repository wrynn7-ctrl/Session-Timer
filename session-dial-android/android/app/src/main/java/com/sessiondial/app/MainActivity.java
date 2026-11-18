package com.sessiondial.app;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(SaveFilePlugin.class); // Export CSV's "choose where to save" screen
        registerPlugin(WidgetBridgePlugin.class); // keeps the home screen widget in step with the timer
        super.onCreate(savedInstanceState);
    }
}
