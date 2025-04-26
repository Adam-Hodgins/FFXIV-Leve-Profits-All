const worldEl = document.getElementById('worldSelect');
const jobEl   = document.getElementById('jobSelect');
const container = document.getElementById('tableContainer');

function clearTable() {
  container.innerHTML = '';
}

function renderTable(data) {
  if (!data.length) {
    container.innerHTML = '<p>No records found.</p>';
    return;
  }
  const cols = Object.keys(data[0]);
  let html = '<table><thead><tr>';
  for (let c of cols) {
    html += `<th>${c}</th>`;
  }
  html += '</tr></thead><tbody>';
  for (let row of data) {
    html += '<tr>';
    for (let c of cols) {
      html += `<td>${row[c]}</td>`;
    }
    html += '</tr>';
  }
  html += '</tbody></table>';
  container.innerHTML = html;
}

function fetchAndShow() {
  const world = worldEl.value;
  const job   = jobEl.value;
  if (!world || !job) { clearTable(); return; }

  fetch(`/data?world=${encodeURIComponent(world)}&job=${encodeURIComponent(job)}`)
    .then(r => r.ok ? r.json() : Promise.reject(r.statusText))
    .then(renderTable)
    .catch(err => {
      clearTable();
      container.innerHTML = `<p style="color:red">Error: ${err}</p>`;
    });
}

worldEl.addEventListener('change', () => {
  jobEl.disabled = !worldEl.value;
  clearTable();
});
jobEl.addEventListener('change', fetchAndShow);
