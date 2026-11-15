(function () {
  var btn = document.getElementById("open-btn");
  var muteBtn = document.getElementById("mute-btn");

  var CARD = 140;   // ширина карточки + отступы (см. .roll-card в CSS)
  var TOTAL = 50;   // сколько карточек в ленте
  var WIN = 42;     // индекс выигрышной карточки
  var DURATION = 5000;

  // ---------- звук (генерируется в браузере, файлы не нужны) ----------
  var audioCtx = null;
  var muted = false;
  try { muted = localStorage.getItem("dc_muted") === "1"; } catch (e) {}

  function updateMuteBtn() {
    if (muteBtn) muteBtn.textContent = muted ? "🔇 Звук выкл." : "🔊 Звук вкл.";
  }
  updateMuteBtn();
  if (muteBtn) {
    muteBtn.addEventListener("click", function () {
      muted = !muted;
      try { localStorage.setItem("dc_muted", muted ? "1" : "0"); } catch (e) {}
      updateMuteBtn();
    });
  }

  function ctx() {
    if (!audioCtx) {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (AC) audioCtx = new AC();
    }
    if (audioCtx && audioCtx.state === "suspended") audioCtx.resume();
    return audioCtx;
  }

  function tick() {
    if (muted) return;
    var c = ctx();
    if (!c) return;
    var t = c.currentTime;
    var o = c.createOscillator();
    var g = c.createGain();
    o.type = "square";
    o.frequency.setValueAtTime(950, t);
    o.frequency.exponentialRampToValueAtTime(320, t + 0.04);
    g.gain.setValueAtTime(0.05, t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.05);
    o.connect(g);
    g.connect(c.destination);
    o.start(t);
    o.stop(t + 0.06);
  }

  var CHORDS = {
    common: [440],
    rare: [440, 554],
    mythical: [440, 554, 659],
    legendary: [440, 554, 659, 880],
    immortal: [523, 659, 784, 1047],
    arcana: [523, 659, 784, 1047, 1319, 1568]
  };

  function winSound(rarity) {
    if (muted) return;
    var c = ctx();
    if (!c) return;
    var notes = CHORDS[rarity] || CHORDS.common;
    notes.forEach(function (freq, i) {
      var t = c.currentTime + i * 0.09;
      var o = c.createOscillator();
      var g = c.createGain();
      o.type = "triangle";
      o.frequency.setValueAtTime(freq, t);
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(0.14, t + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.7);
      o.connect(g);
      g.connect(c.destination);
      o.start(t);
      o.stop(t + 0.75);
    });
  }

  // ---------- рулетка ----------
  if (!btn) return;
  var roulette = document.getElementById("roulette");
  var strip = document.getElementById("strip");
  var modal = document.getElementById("modal");
  var csrf = document.querySelector("[name=csrfmiddlewaretoken]").value;
  var spinning = false;

  function makeCard(it) {
    var d = document.createElement("div");
    d.className = "roll-card rarity-" + it.rarity;
    var img = document.createElement("img");
    img.src = it.image;
    img.alt = "";
    d.appendChild(img);
    return d;
  }

  function stripX() {
    var m = getComputedStyle(strip).transform;
    if (!m || m === "none") return 0;
    return new DOMMatrix(m).m41;
  }

  // тик каждый раз, когда под указателем сменилась карточка
  function watchTicks() {
    var last = -1;
    function frame() {
      if (!spinning) return;
      var idx = Math.floor((roulette.clientWidth / 2 - stripX()) / CARD);
      if (idx !== last) {
        last = idx;
        tick();
      }
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  function showResult(data) {
    document.getElementById("m-img").src = data.item.image;
    document.getElementById("m-name").textContent = data.item.name;
    document.getElementById("m-meta").textContent = data.item.hero + " · " + data.item.rarity_label;
    document.getElementById("m-card").className = "card rarity-" + data.item.rarity;
    modal.hidden = false;
    winSound(data.item.rarity);
    var bal = document.getElementById("balance");
    if (bal) {
      bal.textContent = data.balance;
      var box = bal.parentElement;
      box.classList.remove("flash");
      void box.offsetWidth;
      box.classList.add("flash");
    }
    btn.disabled = false;
  }

  function spin(data) {
    roulette.hidden = false;
    strip.innerHTML = "";
    strip.style.transition = "none";
    strip.style.transform = "translateX(0)";

    for (var i = 0; i < TOTAL; i++) {
      var it = i === WIN ? data.item : data.pool[Math.floor(Math.random() * data.pool.length)];
      strip.appendChild(makeCard(it));
    }

    void strip.offsetWidth; // принудительный reflow, чтобы анимация началась с нуля

    var offset = roulette.clientWidth / 2 - (WIN * CARD + CARD / 2) + (Math.random() * 80 - 40);
    strip.style.transition = "transform " + DURATION + "ms cubic-bezier(0.1, 0.7, 0.1, 1)";
    strip.style.transform = "translateX(" + offset + "px)";

    spinning = true;
    watchTicks();

    var done = false;
    function finish() {
      if (done) return;
      done = true;
      spinning = false;
      strip.children[WIN].classList.add("win");
      setTimeout(function () { showResult(data); }, 450);
    }
    strip.addEventListener("transitionend", finish, { once: true });
    setTimeout(finish, DURATION + 400); // запасной вариант, если transitionend не сработал

    roulette.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  btn.addEventListener("click", function () {
    ctx(); // создаём AudioContext внутри клика, иначе браузер заблокирует звук
    btn.disabled = true;
    fetch(btn.dataset.url, { method: "POST", headers: { "X-CSRFToken": csrf } })
      .then(function (r) {
        return r.json().then(function (data) { return { ok: r.ok, data: data }; });
      })
      .then(function (res) {
        if (!res.ok) {
          alert(res.data.error || "Ошибка");
          btn.disabled = false;
          return;
        }
        spin(res.data);
      })
      .catch(function () {
        alert("Ошибка сети");
        btn.disabled = false;
      });
  });

  document.getElementById("m-close").addEventListener("click", function () {
    modal.hidden = true;
  });
})();
