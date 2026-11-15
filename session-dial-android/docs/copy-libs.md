# scripts/copy-libs.js

`scripts/copy-libs.js`

A small script that runs automatically after `npm install` (it is the `postinstall` command in
`package.json`).

## Why it exists

The page talks to Android through Capacitor's browser library. Projects that use a bundler get
that library packed in automatically. This project has no bundler; `index.html` loads the
library with a plain tag:

```html
<script src="capacitor.js"></script>
```

So the file has to sit in `www/` beside the page. This script puts it there.

## What it does

```js
const from = path.join(__dirname, '..', 'node_modules', '@capacitor', 'core', 'dist', 'capacitor.js');
const to = path.join(__dirname, '..', 'www', 'capacitor.js');
```

Works out two paths: where npm put the library, and where the page expects it. `__dirname` is
the `scripts` folder, so `..` is the project root.

```js
if (fs.existsSync(from)) {
  fs.copyFileSync(from, to);
  console.log('Copied capacitor.js into www/');
}
```

Copies the file, replacing any older copy. The `existsSync` check means the script does nothing,
instead of failing the whole install, if the library is not there yet.

## Why copy on every install

It keeps `www/capacitor.js` at the same version as the installed Capacitor. If the two ever
disagreed, calls from the page to Android could fail in ways that are hard to trace.
