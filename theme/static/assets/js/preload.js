var start = new Date().getTime();

function onLoad() {
  var now = new Date().getTime();
  var latency = now - start;
  document.getElementById("pageloadtime").textContent = latency + 'ms';
}
