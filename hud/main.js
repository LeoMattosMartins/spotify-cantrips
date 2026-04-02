const path = require('path');
const { app, BrowserWindow, Tray, Menu, nativeImage, ipcMain } = require('electron');

let hudWindow;
let tray;

function createHudWindow() {
  hudWindow = new BrowserWindow({
    width: 900,
    height: 520,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    hasShadow: false,
    webPreferences: {
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  hudWindow.setIgnoreMouseEvents(true, { forward: true });
  hudWindow.loadFile(path.join(__dirname, 'index.html'));
  hudWindow.showInactive();
}

function createTray() {
  const icon = nativeImage.createEmpty();
  tray = new Tray(icon);
  tray.setToolTip('Cantrips');
  tray.setContextMenu(
    Menu.buildFromTemplate([
      {
        label: 'Show HUD',
        click: () => hudWindow.showInactive()
      },
      {
        label: 'Hide HUD',
        click: () => hudWindow.hide()
      },
      {
        type: 'separator'
      },
      {
        label: 'Quit',
        click: () => app.quit()
      }
    ])
  );
}

app.whenReady().then(() => {
  createHudWindow();
  createTray();

  ipcMain.on('hud-visibility', (_event, shouldShow) => {
    if (!hudWindow) {
      return;
    }
    if (shouldShow) {
      hudWindow.showInactive();
    } else {
      hudWindow.hide();
    }
  });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createHudWindow();
    }
  });
});

app.on('window-all-closed', (event) => {
  event.preventDefault();
});
