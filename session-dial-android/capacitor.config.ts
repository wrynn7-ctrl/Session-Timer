import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  // The app's permanent ID on the phone. Change it before the first install if you want your own;
  // changing it later makes Android treat it as a different app.
  appId: 'com.sessiondial.app',
  appName: 'Session Dial',
  webDir: 'www',
  plugins: {
    LocalNotifications: {
      // Tint of the small icon in the notification shade (the dial's copper).
      iconColor: '#B5562A'
    }
  }
};

export default config;
