function showImageLoader(state) {
  const loader = document.getElementById("img-loader");
  const img = document.getElementById("img-display");
  loader.style.display = state ? "block" : "none";
  img.style.opacity = state ? "0.5" : "1";
}

function logHistory(command, status) {
  const history = document.getElementById("history-log");
  const entry = document.createElement("li");
  entry.textContent = `${new Date().toLocaleTimeString()} - ${command}: ${status}`;
  history.insertBefore(entry, history.firstChild);
}

async function updateView() {
  try {
    showImageLoader(true);  // Показываем загрузчик
    const res = await fetch('/view_data');
    if (!res.ok) {
      throw new Error(`Server error: ${res.status}`);
    }
    const data = await res.json();
    console.log("Ответ от /view_data:", data);  // Отладка

    const imgEl = document.getElementById("img-display");
    imgEl.src = data.img;  // Устанавливаем без ?t=, так как base64 не кэшируется
  } catch (err) {
    console.error("Ошибка при обновлении:", err);
    logHistory("update", `Error: ${err.message}`);
  } finally {
    showImageLoader(false);  // Убираем загрузчик
  }
}

async function runCommand(command) {
  showImageLoader(true);
  try {
    const res = await fetch(`/${command}`);
    if (!res.ok) throw new Error('Server error');
    const data = await res.json();
    logHistory(command, data.status);
    await updateView();

    // ⏪ Если это Undo — обновим и номер кадра
    if (command === 'undo') {
      await updateFrameIndicator();
    }
  } catch (err) {
    console.error('Ошибка команды:', err);
    logHistory(command, "Error");
  } finally {
    showImageLoader(false);
  }
}

async function sendJson(endpoint, payload) {
  showImageLoader(true);
  try {
    const res = await fetch(`/${endpoint}`, {
      method: "POST",
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Server error');
    const data = await res.json();
    logHistory(endpoint, data.status);
    await updateView();
  } catch (err) {
    console.error('Ошибка отправки:', err);
    logHistory(endpoint, "Error");
  } finally {
    showImageLoader(false);
  }
  return false;
}

function sendForm(e) {
  e.preventDefault();
  const val = document.getElementById('input-param').value;
  if (!val) return false;

  runCommandGet(`/select?index=${val}`).then(() => {
    updateFrameIndicator();  // ✅ Обновить отображение "Кадр: X из Y"
  });

  return false;
}

async function runCommandGet(url) {
  showImageLoader(true);
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error('Server error');
    const data = await res.json();
    logHistory(url, data.status);
    await updateView();
  } catch (err) {
    console.error('Ошибка команды:', err);
    logHistory(url, "Error");
  } finally {
    showImageLoader(false);
  }
}

function sendAutoContrast(form) {
  const lower = parseInt(form.lower.value);
  const upper = parseInt(form.upper.value);

  if (isNaN(lower) || isNaN(upper) || lower < 0 || upper > 100 || lower >= upper) {
    alert("Введите корректные значения процентов: 0 ≤ lower < upper ≤ 100");
    return false;
  }

  const payload = {
    auto_contrast_percentiles: [lower, upper]
  };

  return sendJson('auto_contrast', payload);
}

function handleFormSubmit(event, payloadBuilder, endpoint) {
  event.preventDefault();  // <-- предотвращаем перезагрузку
  const payload = payloadBuilder(event.target);
  return sendJson(endpoint, payload);
}

function downloadData() {
  const link = document.createElement('a');
  link.href = '/download_data';
  link.download = ''; // имя будет задано на сервере через FileResponse
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

let currentIndex = 0;
let totalCount = 1;

async function updateFrameIndicator() {
  try {
    const [indexRes, countRes] = await Promise.all([
      fetch('/select_index'),
      fetch('/count_all_datas')
    ]);

    const indexData = await indexRes.json();
    const countData = await countRes.json();

    currentIndex = parseInt(indexData.status);
    totalCount = parseInt(countData.status);

    document.getElementById("frame-indicator").textContent = `Кадр: ${currentIndex + 1} из ${totalCount}`;
  } catch (err) {
    console.error("Ошибка при получении индекса и количества:", err);
  }
}

async function selectIndex(index) {
  if (index < 0 || index >= totalCount) return;

  try {
    showImageLoader(true);
    const res = await fetch(`/select?index=${index}`);
    const data = await res.json();
    logHistory(`select ${index}`, data.status);
    await updateView();
    await updateFrameIndicator();
  } catch (err) {
    console.error("Ошибка выбора кадра:", err);
    logHistory("select", "Error");
  } finally {
    showImageLoader(false);
  }
}

function selectPrev() {
  selectIndex(currentIndex - 1);
}

function selectNext() {
  selectIndex(currentIndex + 1);
}

function sendDarkIndexes(event) {
  event.preventDefault();
  const form = event.target;
  const start = form.index_start.value;
  const end = form.index_end.value;

  if (!start || !end) {
    alert("Оба индекса обязательны");
    return false;
  }

  const url = `/dark_indexes?index_start=${encodeURIComponent(start)}&index_end=${encodeURIComponent(end)}`;

  showImageLoader(true);
  fetch(url)
    .then(res => {
      if (!res.ok) throw new Error("Ошибка сервера");
      return res.json();
    })
    .then(data => {
      logHistory("dark_indexes", data.status);
      // Можно обновить картинку, если нужно:
      // return updateView();
    })
    .catch(err => {
      console.error("Ошибка:", err);
      logHistory("dark_indexes", "Error");
    })
    .finally(() => {
      showImageLoader(false);
    });

  return false;
}


// Инициализируем индикатор при загрузке страницы
document.addEventListener("DOMContentLoaded", () => {
  updateFrameIndicator();
});




// Убрали автоматический вызов updateView при загрузке
// document.addEventListener('DOMContentLoaded', () => {
//   updateView();
// });