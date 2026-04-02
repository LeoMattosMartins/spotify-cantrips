const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('cantripsMeta', {
  websocketUrl: 'ws://127.0.0.1:8765',
  setHudVisible: (visible) => ipcRenderer.send('hud-visibility', visible)
});
