# SaveFilePlugin.java

`android/app/src/main/java/com/sessiondial/app/SaveFilePlugin.java`

The one piece of native Android code written for this app. It gives the page a `SaveFile.save()`
call that opens Android's own "save as" screen, lets the user choose a folder and file name, and
writes text to the file they chose. Export CSV uses it.

It works in two halves, because Android does not let an app wait for another screen. The app
asks for the screen to open, and Android calls back later with the result.

## The class and its name

```java
@CapacitorPlugin(name = "SaveFile")
public class SaveFilePlugin extends Plugin {
```

`@CapacitorPlugin(name = "SaveFile")` is the name the page uses to reach this code. In
`index.html` the matching line is `const Saver = nativePlugin('SaveFile');`.

## First half: `save()` opens the screen

```java
@PluginMethod
public void save(PluginCall call) {
```

`@PluginMethod` makes the method callable from JavaScript. `call` carries what the page sent
(`name`, `data`, `mimeType`) and is also how the answer is sent back.

```java
    String name = call.getString("name");
    if (name == null || call.getString("data") == null) {
        call.reject("name and data are required");
        return;
    }
```

Refuses to continue without a file name and content. `call.reject` makes the page's
`await Saver.save(...)` throw an error.

```java
    Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
    intent.addCategory(Intent.CATEGORY_OPENABLE);
    intent.setType(call.getString("mimeType", "text/csv"));
    intent.putExtra(Intent.EXTRA_TITLE, name);
```

An "intent" is a request to Android to open some screen.

- `ACTION_CREATE_DOCUMENT` asks for the system "save as" screen.
- `CATEGORY_OPENABLE` limits the choice to places that can really hold a file.
- `setType` says it is a CSV, so the picker shows the right icon and extension.
- `EXTRA_TITLE` pre-fills the file name box (for example `111526 - 111526.csv`).

```java
    try {
        startActivityForResult(call, intent, "onLocationPicked");
    } catch (ActivityNotFoundException e) {
        call.reject("This phone has no file picker", "UNAVAILABLE");
    }
```

Opens the screen and tells Capacitor to run `onLocationPicked` when the user comes back. If the
phone has no file picker at all, the error code `UNAVAILABLE` tells the page to fall back to the
share sheet.

## Second half: `onLocationPicked()` writes the file

```java
@ActivityCallback
private void onLocationPicked(PluginCall call, ActivityResult result) {
    if (call == null) return;
```

Runs when the "save as" screen closes. `call` is the same call object from the first half, so the
text to write is still available. It can be missing if Android restarted the app while the picker
was open; in that case there is nothing to do.

```java
    Intent picked = result.getData();
    Uri uri = picked == null ? null : picked.getData();
    JSObject ret = new JSObject();
    if (result.getResultCode() != Activity.RESULT_OK || uri == null) {
        ret.put("saved", false);
        call.resolve(ret);
        return;
    }
```

`uri` is Android's address for the file the user just created. If the user pressed Back, there is
no address. That is not an error, so the page gets `{ saved: false }` and shows "Export
cancelled."

```java
    try (OutputStream out = getContext().getContentResolver().openOutputStream(uri, "wt")) {
        out.write(call.getString("data").getBytes(StandardCharsets.UTF_8));
    } catch (Exception e) {
        call.reject("The file could not be written", "WRITE_FAILED", e);
        return;
    }
```

Opens the chosen file and writes the CSV text into it.

- `"wt"` means write and truncate: if the user chose to replace an existing file, the old
  contents are emptied first, so nothing is left over at the end.
- The `try ( ... )` form closes the file automatically, even if writing fails.
- A failure is reported to the page, which then offers "Copy as CSV".

```java
    ret.put("saved", true);
    ret.put("name", displayName(uri, call.getString("name")));
    call.resolve(ret);
```

Success. The page gets `{ saved: true, name: "..." }` and shows "Saved *name* with N sessions."

## `displayName()`: what the file ended up being called

```java
private String displayName(Uri uri, String fallback) {
    try (Cursor c = getContext().getContentResolver()
            .query(uri, new String[] { OpenableColumns.DISPLAY_NAME }, null, null, null)) {
        if (c != null && c.moveToFirst() && !c.isNull(0)) return c.getString(0);
    } catch (Exception ignored) {}
    return fallback;
}
```

The user can rename the file in the picker, and Android may add "(1)" if the name is taken. This
asks Android for the real name so the message on the page is accurate. If the lookup fails, it
uses the name the page suggested.

## Why no storage permission is needed

The manifest has no "read or write storage" permission. Android grants access to exactly the one
file the user created in the picker, and nothing else.
