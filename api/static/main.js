async function runCommand(command) {
  showLoader(true);
  try {
    const res = await fetch(`/${command}`);
    const data = await res.json();
    logHistory(command, data.status);
    updateView();
  } catch (err) {
    logHistory(command, "Error");
  } finally {
    showLoader(false);
  }
}

function sendForm(e) {
  e.preventDefault();
  const val = document.getElementById('input-param').value;
  if (!val) return false;
  runCommand(`select?index=${val}`);
  return false;
}

function logHistory(cmd, status) {
  const el = document.createElement("li");
  el.innerText = `${new Date().toLocaleTimeString()} - ${cmd}: ${status}`;
  document.getElementById("history-log").prepend(el);
}

function showLoader(state) {
  document.getElementById("loader").style.display = state ? 'block' : 'none';
}

async function updateView() {
  const res = await fetch('/view');  // or maybe a dedicated /view_data endpoint
  const data = await res.json();
  document.getElementById("data-display").innerText = JSON.stringify(data.data, null, 2);
  // если img — это base64 или путь к изображению:
  document.getElementById("img-display").src = data.img;
}
