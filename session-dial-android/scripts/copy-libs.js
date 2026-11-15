// Copies Capacitor's browser library into www/ so the page can load it with a plain <script> tag.
// Runs automatically after `npm install`, which keeps www/capacitor.js matched to the installed version.
const fs = require('fs');
const path = require('path');
const from = path.join(__dirname, '..', 'node_modules', '@capacitor', 'core', 'dist', 'capacitor.js');
const to = path.join(__dirname, '..', 'www', 'capacitor.js');
if (fs.existsSync(from)) {
  fs.copyFileSync(from, to);
  console.log('Copied capacitor.js into www/');
}
