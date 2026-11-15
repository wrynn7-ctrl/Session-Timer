# The launcher icon

Five small files under `android/app/src/main/res/` together make the app's icon, plus ten
pictures for older phones. The icon is the timer's dial: a grey ring, a copper progress arc about
two-thirds of the way round, the pale wind-down zone before the top, and the tip dot.

## How Android builds an icon

Since Android 8 an icon is "adaptive": the app supplies a **background** layer and a
**foreground** layer, each 108 units square, and the launcher cuts them to its own shape (circle,
rounded square and so on). Only the middle 66 units are guaranteed to be visible, so the artwork
has to stay inside that.

## `mipmap-anydpi-v26/ic_launcher.xml` and `ic_launcher_round.xml`

```xml
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@drawable/ic_launcher_foreground"/>
    <monochrome android:drawable="@drawable/ic_launcher_monochrome"/>
</adaptive-icon>
```

The recipe. The two files are identical; Android asks for one or the other depending on the
launcher. `v26` in the folder name means "Android 8 and newer".

- `background` is a flat colour.
- `foreground` is the dial drawing.
- `monochrome` is a one-colour version for Android 13's "themed icons", where the launcher tints
  every icon to match the wallpaper.

## `values/ic_launcher_background.xml`

```xml
<color name="ic_launcher_background">#ECE9F0</color>
```

The background colour. It is the same pale lilac as the page background in light mode (`--bg` in
`index.html`).

## `drawable-v24/ic_launcher_foreground.xml`

The dial, drawn as vector paths so it stays sharp at any size. The canvas is 108 by 108, the ring
is centred at (54, 54) with radius 24 and a stroke 7 wide, which keeps it inside the safe middle.

It has four paths, drawn in this order so later ones sit on top:

| Path | Colour | What it is |
|---|---|---|
| A full circle | `#DCD5E1` | The grey track (`--track`). |
| A short arc from the 10 o'clock position to the top | `#E6C3AD` | The wind-down zone (`--wind`). |
| A long arc from the top, clockwise, to the 7:30 position | `#B5562A` | Progress so far (`--accent`), with rounded ends. |
| A small filled circle at the end of that arc | fill `#F6F4F8`, outline `#B5562A` | The tip dot. |

In a path, `M54,30` moves the pen to the top of the ring and `A24,24 ...` draws an arc of radius
24 to the end point that follows.

## `drawable-v24/ic_launcher_monochrome.xml`

The same ring in black only: the full circle at 30% opacity and the progress arc solid. Android
ignores the colour and uses the shape, tinting it itself. The wind-down zone and tip dot are left
out because they cannot be told apart in one colour.

## The `mipmap-*dpi` pictures

`ic_launcher.png` (rounded square) and `ic_launcher_round.png` (circle) in five sizes, from 48
to 192 pixels. Android 7 cannot use adaptive icons, so it gets these fixed pictures of the same
design. They were rendered from the same shapes and colours as the vector file.

## Changing the icon

Edit the paths or colours in `ic_launcher_foreground.xml` and the colour in
`ic_launcher_background.xml`. Phones on Android 8 and newer pick that up on the next build. The
PNGs would need re-rendering to match, which only matters for Android 7.
