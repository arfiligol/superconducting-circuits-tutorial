import { app, BrowserWindow } from "electron";
import { join } from "node:path";

function createFallbackHtml(): string {
  return [
    "<!doctype html>",
    "<html lang=\"en\">",
    "  <head>",
    "    <meta charset=\"utf-8\" />",
    "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />",
    "    <title>Superconducting Circuits Desktop</title>",
    "    <style>",
    "      body { font-family: 'Avenir Next', 'Segoe UI', sans-serif; margin: 0; min-height: 100vh; display: grid; place-items: center; background: #101828; color: #f8fafc; }",
    "      main { max-width: 32rem; padding: 2rem; border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 24px; background: rgba(15, 23, 42, 0.82); }",
    "      h1 { margin-top: 0; font-size: 1.8rem; }",
    "      p { line-height: 1.6; color: #cbd5e1; }",
    "      code { font-family: ui-monospace, monospace; color: #93c5fd; }",
    "    </style>",
    "  </head>",
    "  <body>",
    "    <main>",
    "      <h1>Desktop shell ready</h1>",
    "      <p>This Electron wrapper will load the frontend workspace once a dev server or production bundle is wired in.</p>",
    "      <p>Set <code>DESKTOP_START_URL</code> to wrap a running frontend during migration.</p>",
    "    </main>",
    "  </body>",
    "</html>",
  ].join("");
}

function createWindow(): BrowserWindow {
  const window = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 960,
    minHeight: 640,
    backgroundColor: "#101828",
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      preload: join(__dirname, "../preload/index.js"),
    },
  });

  window.webContents.setWindowOpenHandler(() => ({ action: "deny" }));

  const startUrl = process.env.DESKTOP_START_URL;
  if (startUrl) {
    void window.loadURL(startUrl);
  } else {
    void window.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(createFallbackHtml())}`);
  }

  return window;
}

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
