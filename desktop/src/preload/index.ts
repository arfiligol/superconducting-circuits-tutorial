import { contextBridge } from "electron";

const desktopShell = {
  platform: process.platform,
  versions: {
    chrome: process.versions.chrome,
    electron: process.versions.electron,
    node: process.versions.node,
  },
};

contextBridge.exposeInMainWorld("desktopShell", desktopShell);
