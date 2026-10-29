// Minimal stand-in for the Claude dashboard runtime (`dash`), so the page in
// painel/index.html runs as a plain static site. Reads the bases from dados/.
(function () {
  const DATASETS = ['mensal', 'anual', 'municipios_2023', 'regional', 'apuracao'];
  const DEFAULT_PARAMS = { tipo: 'Reclamações' };
  const loaded = {};
  const calcs = {};
  const calcCache = {};
  const draws = {};
  const listeners = [];
  let params = { ...DEFAULT_PARAMS };
  let scheduled = false;

  const load = (id) => {
    if (loaded[id]) return;
    loaded[id] = { status: 'loading', data: [] };
    fetch('dados/' + id + '.json')
      .then((r) => { if (!r.ok) throw new Error(r.status + ' ' + r.statusText); return r.json(); })
      .then((rows) => { loaded[id] = { status: 'ok', data: rows }; Object.keys(calcCache).forEach((k) => delete calcCache[k]); schedule(); })
      .catch((e) => { loaded[id] = { status: 'error', data: [], message: String(e) }; schedule(); });
  };

  const data = (id) => {
    if (calcs[id]) {
      if (calcCache[id]) return calcCache[id];
      const ins = calcs[id].inputs.map(data);
      const bad = ins.find((d) => d.status !== 'ok');
      if (bad) return { status: bad.status, data: [] };
      try {
        calcCache[id] = { status: 'ok', data: calcs[id].fn(...ins.map((d) => d.data)) };
      } catch (e) {
        console.error('calc ' + id, e);
        calcCache[id] = { status: 'error', data: [], message: String(e) };
      }
      return calcCache[id];
    }
    if (!DATASETS.includes(id)) return { status: 'missing', data: [] };
    load(id);
    return loaded[id];
  };

  const visible = (el) => !el.closest('[hidden]');
  const runDraw = (name) => {
    document.querySelectorAll('[data-draw="' + name + '"]').forEach((el) => {
      if (!visible(el)) return;
      try { draws[name](el); } catch (e) { console.error('draw ' + name, e); }
    });
  };
  const redrawAll = () => {
    scheduled = false;
    listeners.forEach((fn) => { try { fn(); } catch (e) { console.error(e); } });
    Object.keys(draws).forEach(runDraw);
  };
  const schedule = () => { if (!scheduled) { scheduled = true; requestAnimationFrame(redrawAll); } };

  window.dash = {
    colors: ['#0060a8', '#e87000', '#8c9400', '#006808', '#685848', '#6d74a8', '#00508c', '#c62828'],
    data,
    calc: (id, spec) => { calcs[id] = spec; },
    loader: () => {},
    draw: (name, fn) => {
      if (fn) { draws[name] = fn; schedule(); } else if (draws[name]) runDraw(name);
    },
    onData: (fn) => { listeners.push(fn); schedule(); },
    params: () => ({ ...params }),
    setParams: (p) => {
      Object.entries(p).forEach(([k, v]) => { if (v == null) delete params[k]; else params[k] = v; });
      schedule();
    },
    resetParams: () => { params = { ...DEFAULT_PARAMS }; schedule(); },
    setLink: (name) => { try { history.replaceState(null, '', '#' + name); } catch (e) { /* ignore */ } },
    refresh: () => {},
  };

  // Redraw when a tab is shown and when the width changes
  document.addEventListener('DOMContentLoaded', () => {
    const mo = new MutationObserver(schedule);
    document.querySelectorAll('.ar-page').forEach((p) => mo.observe(p, { attributes: true, attributeFilter: ['hidden'] }));
  });
  let lastW = window.innerWidth;
  window.addEventListener('resize', () => { if (window.innerWidth !== lastW) { lastW = window.innerWidth; schedule(); } });
})();
