package com.sessiondial.app;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.provider.OpenableColumns;
import androidx.activity.result.ActivityResult;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.ActivityCallback;
import com.getcapacitor.annotation.CapacitorPlugin;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/**
 * Opens Android's own "save as" screen so the user picks the folder (and can rename the file),
 * then writes the text there. Used by Export CSV. Needs no storage permission, because Android
 * hands back access to just the one file the user created.
 */
@CapacitorPlugin(name = "SaveFile")
public class SaveFilePlugin extends Plugin {

    @PluginMethod
    public void save(PluginCall call) {
        String name = call.getString("name");
        if (name == null || call.getString("data") == null) {
            call.reject("name and data are required");
            return;
        }
        Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType(call.getString("mimeType", "text/csv"));
        intent.putExtra(Intent.EXTRA_TITLE, name);
        try {
            startActivityForResult(call, intent, "onLocationPicked");
        } catch (ActivityNotFoundException e) {
            call.reject("This phone has no file picker", "UNAVAILABLE");
        }
    }

    @ActivityCallback
    private void onLocationPicked(PluginCall call, ActivityResult result) {
        if (call == null) return;
        Intent picked = result.getData();
        Uri uri = picked == null ? null : picked.getData();
        JSObject ret = new JSObject();
        if (result.getResultCode() != Activity.RESULT_OK || uri == null) {
            ret.put("saved", false); // the user backed out of the picker
            call.resolve(ret);
            return;
        }
        // "wt" empties the file first, in case the user chose to replace an existing one.
        try (OutputStream out = getContext().getContentResolver().openOutputStream(uri, "wt")) {
            out.write(call.getString("data").getBytes(StandardCharsets.UTF_8));
        } catch (Exception e) {
            call.reject("The file could not be written", "WRITE_FAILED", e);
            return;
        }
        ret.put("saved", true);
        ret.put("name", displayName(uri, call.getString("name")));
        call.resolve(ret);
    }

    /** The name the file ended up with; the user may have changed it in the picker. */
    private String displayName(Uri uri, String fallback) {
        try (Cursor c = getContext().getContentResolver()
                .query(uri, new String[] { OpenableColumns.DISPLAY_NAME }, null, null, null)) {
            if (c != null && c.moveToFirst() && !c.isNull(0)) return c.getString(0);
        } catch (Exception ignored) {}
        return fallback;
    }
}
