const canvas = document.getElementById('skeleton');
const hud = document.getElementById('hud');
const camera = document.getElementById('camera');
const panel = document.getElementById('panel');
const modeEl = document.getElementById('mode');
const trackEl = document.getElementById('track');

const FINGER_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 4],
  [0, 5], [5, 6], [6, 7], [7, 8],
  [0, 9], [9, 10], [10, 11], [11, 12],
  [0, 13], [13, 14], [14, 15], [15, 16],
  [0, 17], [17, 18], [18, 19], [19, 20],
  [5, 9], [9, 13], [13, 17]
];

const ctx = canvas.getContext('2d');

async function startCameraPreview() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: false,
    });
    camera.srcObject = stream;
  } catch {
    modeEl.textContent = 'CAMERA BLOCKED';
  }
}

function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}

function drawDebugOverlay(debug) {
  const zone = debug.zone || { x_min: 0.2, x_max: 0.8, y_min: 0.2, y_max: 0.8 };
  const x = zone.x_min * canvas.width;
  const y = zone.y_min * canvas.height;
  const width = (zone.x_max - zone.x_min) * canvas.width;
  const height = (zone.y_max - zone.y_min) * canvas.height;

  ctx.strokeStyle = 'rgba(255, 198, 112, 0.95)';
  ctx.lineWidth = 2;
  ctx.setLineDash([8, 6]);
  ctx.strokeRect(x, y, width, height);
  ctx.setLineDash([]);

  const status = debug.in_engagement_zone ? 'IN ZONE' : 'OUT OF ZONE';
  const hand = debug.hand_detected ? 'HAND: YES' : 'HAND: NO';
  const vx = Number(debug.x_velocity || 0).toFixed(3);
  const vy = Number(debug.y_velocity || 0).toFixed(3);

  ctx.fillStyle = 'rgba(9, 18, 30, 0.78)';
  ctx.fillRect(16, 16, 250, 90);

  ctx.fillStyle = '#f5d08a';
  ctx.font = '600 13px Avenir Next, Segoe UI, sans-serif';
  ctx.fillText(`ZONE: ${status}`, 28, 38);
  ctx.fillText(hand, 28, 58);
  ctx.fillText(`X VELOCITY: ${vx}`, 28, 78);
  ctx.fillText(`Y VELOCITY: ${vy}`, 28, 98);
}

function drawLandmarks(landmarks, debug) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawDebugOverlay(debug || {});

  if (!landmarks || !landmarks.length) {
    return;
  }

  ctx.strokeStyle = 'rgba(87, 228, 255, 0.98)';
  ctx.lineWidth = 3;
  ctx.shadowColor = 'rgba(52, 230, 255, 0.7)';
  ctx.shadowBlur = 6;

  for (const [start, end] of FINGER_CONNECTIONS) {
    const a = landmarks[start];
    const b = landmarks[end];
    ctx.beginPath();
    ctx.moveTo(a[0] * canvas.width, a[1] * canvas.height);
    ctx.lineTo(b[0] * canvas.width, b[1] * canvas.height);
    ctx.stroke();
  }

  ctx.shadowBlur = 0;
  ctx.fillStyle = '#66ffd4';
  ctx.strokeStyle = 'rgba(0, 30, 36, 0.9)';
  ctx.lineWidth = 1.5;
  for (const point of landmarks) {
    ctx.beginPath();
    ctx.arc(point[0] * canvas.width, point[1] * canvas.height, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
  }
}

function render(payload) {
  const active = Boolean(payload.system_active);
  window.cantripsMeta.setHudVisible(true);
  modeEl.textContent = active ? 'ACTIVE' : 'LOW-POWER LISTEN';
  panel.classList.toggle('inactive', !active);

  const track = payload.track || {};
  trackEl.textContent = `${track.name || 'Unknown'} — ${track.artist || 'Unknown'}`;

  drawLandmarks(payload.landmarks || [], payload.debug || {});
}

function connect() {
  const socket = new WebSocket(window.cantripsMeta.websocketUrl);

  socket.addEventListener('message', (event) => {
    try {
      const payload = JSON.parse(event.data);
      render(payload);
    } catch {}
  });

  socket.addEventListener('close', () => {
    setTimeout(connect, 1000);
  });
}

window.addEventListener('resize', resize);
resize();
startCameraPreview();
connect();
