const BASE_URL = "http://172.30.225.147:8000";

const $ = s => document.querySelector(s);

const urlInput = $("#urlInput");
const meta = $("#meta");
const thumb = $("#thumb");
const titleDiv = $("#title");
const formats = $("#formats");
const log = $("#log");
const progressWrap = $("#progressWrap");
const fill = $("#fill");
const progText = $("#progText");

function writeLog(msg) {
  log.textContent += msg + "\n";
}

async function fetchMeta(url) {
  try {
    const res = await fetch(`${BASE_URL}/meta`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ url })
    });

    const j = await res.json();
    if (j.error) return;

    titleDiv.textContent = j.title || "";
    thumb.src = j.thumbnail || "";
    meta.classList.remove("hidden");
    formats.classList.remove("hidden");

  } catch (e) {
    writeLog("Meta error: " + e);
  }
}

urlInput.addEventListener("input", () => {
  const url = urlInput.value.trim();
  if (url.includes("youtube.com") || url.includes("youtu.be")) {
    fetchMeta(url);
  }
});

async function download(quality) {
  const url = urlInput.value.trim();
  if (!url) return alert("Paste a YouTube URL");

  progressWrap.classList.remove("hidden");
  fill.style.width = "0%";
  progText.textContent = "Starting...";

  try {
    const response = await fetch(`${BASE_URL}/download`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ url, quality })
    });

    const blob = await response.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `yt_${quality}.mp4`;
    document.body.appendChild(a);
    a.click();
    a.remove();

    progText.textContent = "Download finished";
    fill.style.width = "100%";

  } catch (err) {
    alert("Download failed");
    writeLog(err);
  }
}

formats.addEventListener("click", e => {
  const btn = e.target.closest("button");
  if (!btn) return;
  download(btn.dataset.q);
});
