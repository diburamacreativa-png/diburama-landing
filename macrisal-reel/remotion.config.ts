import {Config} from '@remotion/cli/config';
import {existsSync} from 'node:fs';

// Salida: H.264, yuv420p, calidad alta.
Config.setCodec('h264');
Config.setPixelFormat('yuv420p');
Config.setCrf(16);
// PNG sin pérdidas + rango de color estándar (limitado, BT.709) para redes sociales.
Config.setVideoImageFormat('png');
Config.setColorSpace('bt709');
Config.setOverwriteOutput(true);
Config.setAudioCodec('aac');
Config.setAudioBitrate('320k');

// En este entorno Chromium ya está instalado; si no existe, Remotion descarga el suyo.
const localChrome = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
if (existsSync(localChrome)) {
  Config.setBrowserExecutable(localChrome);
}
