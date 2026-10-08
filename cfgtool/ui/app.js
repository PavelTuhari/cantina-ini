'use strict';

/* Окно настройки кассы.
 *
 * Три вкладки переключаются якорем в адресной строке — так на любую можно
 * дать ссылку и так её умеет открыть съёмка экрана.
 */

const $ = (id) => document.getElementById(id);

async function api(path, options) {
  const res = await fetch(path, options);
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch (e) { data = { detail: text }; }
  if (!res.ok) throw new Error((data && data.detail) || res.statusText);
  return data;
}

const post = (path, body) => api(path, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body || {}),
});

function el(tag, attrs, children) {
  const node = document.createElement(tag);
  for (const k in (attrs || {})) {
    if (k === 'class') node.className = attrs[k];
    else if (k === 'text') node.textContent = attrs[k];
    else if (k === 'html') node.innerHTML = attrs[k];
    else if (k.startsWith('on')) node.addEventListener(k.slice(2), attrs[k]);
    else if (attrs[k] !== null && attrs[k] !== undefined) node.setAttribute(k, attrs[k]);
  }
  (children || []).forEach((c) => node.appendChild(
    typeof c === 'string' ? document.createTextNode(c) : c));
  return node;
}

/* ---------------------------------------------------------------- вкладки */

const TABS = ['settings', 'checks', 'buttons'];

function showTab(name) {
  if (!TABS.includes(name)) name = 'settings';
  TABS.forEach((t) => { $('tab-' + t).hidden = (t !== name); });
  document.querySelectorAll('nav a').forEach((a) => {
    a.classList.toggle('active', a.dataset.tab === name);
  });
  if (name === 'checks') loadChecks();
  if (name === 'buttons') loadPanels();
}

window.addEventListener('hashchange', () => showTab(location.hash.slice(1)));

/* --------------------------------------------------------------- настройки */

let GROUPS = [];

async function loadSummary() {
  const data = await api('/api/summary');
  const s = data.summary;
  $('filePath').textContent = s['файл'] + '  ·  ' + s['кодировка'].toUpperCase();
  $('stats').replaceChildren(
    stat(s['различных имён'], 'параметров в файле'),
    stat(s['действуют'], 'действуют'),
    stat(s['не читаются'], 'не читаются', 'warn'),
    stat(s['мёртвые'], 'мёртвые', 'bad'),
    stat(s['не указано в файле'], 'касса умеет, но не задано'),
  );
  GROUPS = data.groups;
  const pick = $('groupPick');
  GROUPS.forEach((g) => pick.appendChild(
    el('option', { value: g.title, text: `${g.title} (${g.count})` })));
}

function stat(value, label, cls) {
  return el('div', { class: cls || '' }, [
    el('b', { text: String(value) }),
    el('span', { text: label }),
  ]);
}

let searchTimer = null;

async function loadOptions() {
  const params = new URLSearchParams();
  if ($('search').value.trim()) params.set('q', $('search').value.trim());
  if ($('groupPick').value) params.set('group', $('groupPick').value);
  if ($('statePick').value) params.set('state', $('statePick').value);
  if ($('showAbsent').checked) params.set('absent', 'true');
  const data = await api('/api/options?' + params.toString());
  $('optCount').textContent = `показано ${data.count}`;
  const box = $('options');
  box.replaceChildren();
  if (!data.options.length) {
    box.appendChild(el('p', { class: 'empty-note', text: 'Ничего не нашлось.' }));
    return;
  }
  data.options.forEach((o) => box.appendChild(optionRow(o)));
}

function stateP(o) {
  if (o.state === 'действует') return el('span', { class: 'pill p-ok', text: 'действует' });
  if (o.state === 'не читается') {
    return el('span', {
      class: 'pill p-warn',
      text: o.shadowedBy ? `перебита строкой ${o.shadowedBy}` : 'отключена решёткой',
    });
  }
  if (o.state === 'мёртвая') return el('span', { class: 'pill p-bad', text: 'касса её не читает' });
  return el('span', { class: 'pill p-acc', text: 'не задана, берётся умолчание' });
}

function optionRow(o) {
  const left = el('div', {}, [
    el('div', { class: 'name' }, [o.name, ' ', stateP(o)]),
  ]);
  if (o.note) left.appendChild(el('div', { class: 'note', text: o.note }));

  const meta = [`${o.kind || 'строка'} · ${o.source || 'не определено'}`];
  if (o.default) meta.push(`умолчание ${o.default}`);
  if (o.line) meta.push(`строка ${o.line}`);
  if (o.places && o.places.length) {
    meta.push('читается ' + o.places.map(
      (p) => p.file.split('/').pop() + ':' + p.line).join(', '));
  }
  left.appendChild(el('div', { class: 'meta', text: meta.join('  ·  ') }));

  const right = el('div', { class: 'edit' });
  if (o.secret) {
    right.appendChild(el('span', { class: 'hint', text: 'секрет, правится только в файле' }));
  } else if (o.state === 'мёртвая') {
    right.appendChild(el('span', { class: 'hint', text: 'менять нечего' }));
  } else {
    const input = editorFor(o);
    const saved = el('span', { class: 'saved' });
    const save = el('button', {
      class: 'primary',
      text: 'Записать',
      onclick: async () => {
        try {
          await post('/api/option', { name: o.name, value: input.value });
          saved.textContent = 'записано';
          setTimeout(() => { saved.textContent = ''; }, 2500);
          loadSummary.pending = true;
        } catch (e) {
          saved.textContent = e.message;
        }
      },
    });
    right.append(input, save, saved);
  }
  return el('div', { class: 'opt' }, [left, right]);
}

function editorFor(o) {
  const value = o.value === null || o.value === undefined ? '' : o.value;
  if (o.choices && o.choices.length) {
    const sel = el('select');
    if (!o.choices.includes(value)) sel.appendChild(el('option', { value, text: value || '(пусто)' }));
    o.choices.forEach((c) => sel.appendChild(el('option', { value: c, text: c })));
    sel.value = value;
    return sel;
  }
  if (o.kind === 'булево') {
    const sel = el('select');
    [['true', 'да'], ['false', 'нет']].forEach(([v, t]) => sel.appendChild(
      el('option', { value: v, text: t })));
    const norm = String(value).toLowerCase();
    sel.value = ['1', 'true', 'yes', 'y', 't'].includes(norm) ? 'true' : 'false';
    return sel;
  }
  return el('input', { type: 'text', value });
}

/* --------------------------------------------------------------- проверка */

async function loadChecks() {
  const d = await api('/api/checks');
  const box = $('checks');
  box.replaceChildren();

  if (d.lossy) {
    box.appendChild(el('div', {
      class: 'banner',
      text: `Файл записан в ${d.encoding.toUpperCase()}, но часть байт в эту `
        + 'кодировку не укладывается — так хранится зашифрованный ключ. '
        + 'Эти байты сохраняются как есть и при записи не портятся.',
    }));
  }

  box.appendChild(section('Задвоенные параметры',
    'При двух строках с одним именем касса читает первую сверху. Остальные '
    + 'не делают ничего — дописать исправление в конец файла не получится.',
    d.duplicates.length
      ? table(['Параметр', 'Строки'], d.duplicates.map((x) => [
        el('code', { text: x.name }),
        el('span', {}, x.lines.map((l, i) => el('span', {}, [
          i ? ', ' : '',
          el('code', { text: `${l.index}: ${l.value}` }),
          ' ',
          el('span', {
            class: 'pill ' + (l.effective ? 'p-ok' : 'p-warn'),
            text: l.effective ? 'читается' : 'нет',
          }),
        ]))),
      ]))
      : el('p', { class: 'empty-note', text: 'Задвоенных нет.' })));

  box.appendChild(section('Строки, которые касса не читает',
    'Отключены решёткой или перебиты дублем выше.',
    d.shadowed.length
      ? table(['Параметр', 'Строка', 'Значение', 'Почему'], d.shadowed.map((o) => [
        el('code', { text: o.name }),
        String(o.lines.length ? o.lines[o.lines.length - 1].index : ''),
        el('code', { text: o.lines.length ? o.lines[o.lines.length - 1].value : '' }),
        o.shadowedBy ? `перебита строкой ${o.shadowedBy}` : 'отключена решёткой',
      ]))
      : el('p', { class: 'empty-note', text: 'Таких нет.' })));

  box.appendChild(section('Мёртвые параметры',
    'Этих имён нет ни в одном исходнике кассы. Строка есть, смысла нет.',
    d.dead.length
      ? table(['Параметр', 'Строка', 'Значение'], d.dead.map((x) => [
        el('code', { text: x.name }), String(x.line || ''),
        el('code', { text: x.value === null ? '' : x.value }),
      ]))
      : el('p', { class: 'empty-note', text: 'Мёртвых нет.' })));
}

function section(title, about, body) {
  const card = el('div', { class: 'card' }, [el('h2', { text: title })]);
  if (about) card.appendChild(el('p', { class: 'about', text: about }));
  card.appendChild(el('div', { class: 'wrap' }, [body]));
  return card;
}

function table(headers, rows) {
  const thead = el('thead', {}, [el('tr', {}, headers.map(
    (h) => el('th', { text: h })))]);
  const tbody = el('tbody', {}, rows.map((r) => el('tr', {}, r.map(
    (c) => el('td', {}, [typeof c === 'string' ? document.createTextNode(c) : c])))));
  return el('table', {}, [thead, tbody]);
}

/* ------------------------------------------------------ кнопки тачскрина */

let TS = { panel: null, layer: 1, lng: 'RU', page: 0, buttons: [], commands: [] };

async function loadPanels() {
  try {
    const d = await api('/api/ts/panels');
    $('tsError').replaceChildren();
    $('tsControls').hidden = false;
    $('tsLayout').hidden = false;
    $('tsDiag').hidden = false;

    const pick = $('panelPick');
    if (!pick.options.length) {
      d.panels.forEach((p) => pick.appendChild(el('option', {
        value: p.id,
        text: `${p.id}${p.name ? ' · ' + p.name : ''} — ${p.cols}×${p.rows}`,
      })));
      const lng = $('lngPick');
      d.languages.forEach((l) => lng.appendChild(el('option', { value: l, text: l })));
      lng.value = d.languages.includes('RU') ? 'RU' : d.languages[0];
      const withButtons = d.panels.find((p) => p.layers.length && p.cols > 0);
      pick.value = withButtons ? withButtons.id : d.panels[0].id;
    }

    $('unsupported').replaceChildren(d.unsupported.length
      ? table(['Команда', 'Кнопок'], d.unsupported.map(
        (u) => [el('code', { text: u.cmd }), String(u.buttons)]))
      : el('p', { class: 'empty-note', text: 'Все команды кнопок касса выполняет.' }));

    if (!TS.commands.length) {
      TS.commands = (await api('/api/ts/commands')).commands;
    }
    await loadPanel();
  } catch (e) {
    $('tsControls').hidden = true;
    $('tsLayout').hidden = true;
    $('tsDiag').hidden = true;
    $('tsError').replaceChildren(el('div', { class: 'banner bad', text: e.message }));
  }
}

async function loadPanel() {
  const id = $('panelPick').value;
  const params = new URLSearchParams({
    id, layer: TS.layer, lng: $('lngPick').value || 'RU',
  });
  const d = await api('/api/ts/panel?' + params.toString());
  TS.panel = d.panel;
  TS.buttons = d.buttons;
  TS.lng = d.language;

  const lp = $('layerPick');
  lp.replaceChildren();
  const named = {};
  d.layers.forEach((l) => { named[l.layer] = l.name; });
  d.used.forEach((u) => lp.appendChild(el('option', {
    value: u.layer,
    text: `${u.layer}${named[u.layer] ? ' · ' + named[u.layer] : ''} (${u.buttons})`,
  })));
  if (!d.used.length) lp.appendChild(el('option', { value: 1, text: 'кнопок нет' }));
  lp.value = String(TS.layer);
  if (lp.value !== String(TS.layer) && lp.options.length) {
    TS.layer = Number(lp.options[0].value);
    lp.value = String(TS.layer);
  }

  const cap = TS.panel.capacity;
  $('panelInfo').textContent =
    `сетка ${TS.panel.cols}×${TS.panel.rows} = ${cap} ячеек, кнопок ${TS.buttons.length}`
    + (TS.panel.type === 1 ? ', панель из отдельных кнопок' : '')
    + (cap && TS.buttons.length > cap
      ? `, не помещается — ${Math.ceil(TS.buttons.length / cap)} страниц` : '');

  TS.preview = !!d.preview;
  renderPending(d.pending);
  renderGrid();
}

function renderPending(count) {
  const box = $('pendingBox');
  box.replaceChildren();
  if (!count) {
    box.appendChild(el('span', { class: 'hint', text: 'правок нет' }));
    return;
  }
  box.append(
    el('span', { class: 'pill p-warn', text: `не применено правок: ${count}` }),
    el('button', {
      class: 'primary',
      text: 'Применить и обновить кассу',
      onclick: async () => {
        const r = await post('/api/ts/apply');
        alert(`Записано правок: ${r.applied}.\nОбновлено представлений: `
          + `${(r.refreshed || []).length}.\nКасса увидит новое при следующем открытии панели.`);
        loadPanel();
      },
    }),
    el('button', {
      class: 'danger',
      text: 'Отменить',
      onclick: async () => {
        await post('/api/ts/discard');
        loadPanel();
      },
    }),
  );
}

function renderGrid() {
  const grid = $('tsGrid');
  const cols = TS.panel.cols || 1;
  const rows = TS.panel.rows || 1;
  const cap = cols * rows;
  grid.style.gridTemplateColumns = `repeat(${cols}, minmax(0, 1fr))`;
  grid.replaceChildren();

  const pages = cap ? Math.max(1, Math.ceil(TS.buttons.length / cap)) : 1;
  if (TS.page >= pages) TS.page = 0;
  renderPageNav(pages);

  const byOrd = {};
  TS.buttons.forEach((b) => { byOrd[b.ord] = b; });

  for (let i = 1; i <= cap; i += 1) {
    const ord = TS.page * cap + i;
    grid.appendChild(cell(ord, byOrd[ord]));
  }
  $('gridHint').textContent = (TS.panel.cols
    ? 'Номер в углу ячейки — её место в раскладке. Перетаскивание пишет '
      + 'закреплённую позицию, иначе кнопки встают по алфавиту подписи.'
    : 'У этой панели не задан размер сетки: она строится кассой на ходу.')
    + (TS.preview
      ? '  Показано с учётом несохранённых правок — касса пока рисует прежнее.'
      : '');
}

function renderPageNav(pages) {
  const box = $('pageNav');
  box.replaceChildren();
  if (pages <= 1) return;
  box.append(
    el('button', {
      text: '‹', onclick: () => { TS.page = Math.max(0, TS.page - 1); renderGrid(); },
    }),
    el('span', { class: 'hint', text: ` страница ${TS.page + 1} из ${pages} ` }),
    el('button', {
      text: '›', onclick: () => { TS.page = Math.min(pages - 1, TS.page + 1); renderGrid(); },
    }),
  );
}

function cell(ord, button) {
  const node = el('div', {
    class: 'ts-cell ' + (button ? 'filled' : 'empty')
      + (button && !button.supported ? ' unsupported' : ''),
  });
  node.appendChild(el('span', { class: 'ord', text: String(ord) }));
  if (!button) {
    node.dataset.ord = ord;
    node.addEventListener('dragover', (e) => { e.preventDefault(); node.classList.add('drop'); });
    node.addEventListener('dragleave', () => node.classList.remove('drop'));
    node.addEventListener('drop', (e) => onDrop(e, ord, node));
    return node;
  }

  const flags = [];
  if (button.pinned) flags.push('📌');
  if (!button.supported) flags.push('⚠');
  if (flags.length) node.appendChild(el('span', { class: 'flags', text: flags.join(' ') }));
  if (button.hasPicture) {
    // Картинку показываем ровно так, как её покажет касса: над подписью.
    node.appendChild(el('img', {
      class: 'btn-pic',
      src: '/api/ts/picture?' + new URLSearchParams({
        interface: TS.panel.id, layer: TS.layer,
        order: button.orderId, lng: TS.lng,
      }).toString(),
      alt: '',
      loading: 'lazy',
    }));
  } else if (button.icon) {
    node.appendChild(el('span', { class: 'icon', text: '◆' }));
  }
  node.appendChild(el('span', { class: 'cap', text: button.text || '(без подписи)' }));
  node.appendChild(el('span', { class: 'cmd', text: button.internalCmd || '—' }));
  if (button.color) node.style.background = button.color;

  node.draggable = true;
  node.dataset.ord = ord;
  node.addEventListener('dragstart', (e) => {
    e.dataTransfer.setData('text/plain', JSON.stringify(button));
  });
  node.addEventListener('dragover', (e) => { e.preventDefault(); node.classList.add('drop'); });
  node.addEventListener('dragleave', () => node.classList.remove('drop'));
  node.addEventListener('drop', (e) => onDrop(e, ord, node));
  node.addEventListener('click', () => selectButton(button, node));
  return node;
}

async function onDrop(event, ord, node) {
  event.preventDefault();
  node.classList.remove('drop');
  let dragged = null;
  try { dragged = JSON.parse(event.dataTransfer.getData('text/plain')); } catch (e) { return; }
  if (!dragged || dragged.ord === ord) return;
  try {
    await post('/api/ts/move', {
      interface: TS.panel.id, layer: TS.layer,
      orderId: dragged.orderId, cell: ord,
    });
    await loadPanel();
  } catch (e) {
    alert('Не вышло переставить: ' + e.message);
  }
}

function selectButton(button, node) {
  document.querySelectorAll('.ts-cell.selected').forEach(
    (n) => n.classList.remove('selected'));
  node.classList.add('selected');

  const box = $('tsEditor');
  box.replaceChildren();

  const caption = el('textarea', { value: button.text || '' });
  caption.value = button.text || '';
  const cmdPick = el('select');
  cmdPick.appendChild(el('option', { value: '', text: '(не менять)' }));
  TS.commands.forEach((c) => cmdPick.appendChild(el('option', {
    value: c.id,
    text: `${c.cmd}${c.supported ? '' : '  (касса не выполняет)'}`
      + (c.max ? `  ${c.min}..${c.max} парам.` : ''),
  })));
  const prm1 = el('input', { type: 'text', value: button.params[0] || '' });
  const prm2 = el('input', { type: 'text', value: button.params[1] || '' });
  const status = el('div', { class: 'hint' });

  box.append(
    field('Ячейка и команда сейчас',
      el('div', { class: 'hint' }, [
        el('code', { text: `ячейка ${button.ord} · ${button.internalCmd || 'команды нет'}` }),
      ])),
    field(`Подпись (${TS.lng})`, caption),
    field('Новая команда', cmdPick),
    field('Первый параметр', prm1),
    field('Второй параметр', prm2),
  );

  if (!button.supported && button.cmd) {
    box.appendChild(el('div', {
      class: 'banner bad',
      text: `Касса не разбирает команду «${button.cmd}»: такого имени нет `
        + 'в TS.cpp. Нажатие ничего не сделает.',
    }));
  }
  if (button.isJson) {
    box.appendChild(el('div', {
      class: 'banner',
      text: 'Подпись хранится вместе со значком шрифта иконок. Меняется '
        + 'только текст, значок остаётся.',
    }));
  }
  if (button.cod) {
    box.appendChild(el('div', {
      class: 'hint', text: `товар ${button.cod}`,
    }));
  }

  box.appendChild(pictureBlock(button, status));

  box.append(
    el('div', { class: 'toolbar', style: 'margin-top:12px' }, [
      el('button', {
        class: 'primary',
        text: 'Записать подпись',
        onclick: async () => {
          try {
            await post('/api/ts/caption', {
              interface: TS.panel.id, layer: TS.layer,
              orderId: button.orderId, lng: TS.lng, text: caption.value,
            });
            status.textContent = 'подпись записана, не забудьте применить';
            await loadPanel();
          } catch (e) { status.textContent = e.message; }
        },
      }),
      el('button', {
        text: 'Записать команду',
        onclick: async () => {
          if (!cmdPick.value) { status.textContent = 'команда не выбрана'; return; }
          try {
            await post('/api/ts/command', {
              interface: TS.panel.id, layer: TS.layer, orderId: button.orderId,
              cmdId: Number(cmdPick.value), prm1: prm1.value, prm2: prm2.value,
            });
            status.textContent = 'команда записана, не забудьте применить';
            await loadPanel();
          } catch (e) { status.textContent = e.message; }
        },
      }),
    ]),
    status,
    el('p', { class: 'hint', text:
      'Строку команды собирает сама база из выбранного имени и параметров — '
      + 'поэтому её нельзя вписать текстом.' }),
  );
}

function field(label, control) {
  return el('div', { class: 'field' }, [el('label', { text: label }), control]);
}

/* Картинка кнопки.
 *
 * Картинка лежит не у кнопки, а у записи содержимого, а запись бывает общей.
 * Поэтому перед заменой всегда показывается, скольких кнопок это коснётся.
 */
function pictureBlock(button, status) {
  const box = el('div', { class: 'field' });
  const q = new URLSearchParams({
    interface: TS.panel.id, layer: TS.layer, order: button.orderId, lng: TS.lng,
  }).toString();

  box.appendChild(el('label', { text: 'Картинка' }));
  const preview = el('div', { class: 'pic-preview' });
  box.appendChild(preview);
  const note = el('div', { class: 'hint' });
  box.appendChild(note);

  const file = el('input', { type: 'file', accept: 'image/*' });
  const upload = el('button', {
    class: 'primary',
    text: 'Поставить картинку',
    onclick: async () => {
      if (!file.files || !file.files[0]) { status.textContent = 'файл не выбран'; return; }
      const reader = new FileReader();
      reader.onload = async () => {
        const b64 = String(reader.result).split(',')[1];
        try {
          const r = await post('/api/ts/picture', {
            interface: TS.panel.id, layer: TS.layer,
            orderId: button.orderId, data: b64,
          });
          status.textContent = r.note
            + (r.sharedWith > 1 ? `, затронуто кнопок: ${r.sharedWith}` : '');
          await loadPanel();
        } catch (e) { status.textContent = e.message; }
      };
      reader.readAsDataURL(file.files[0]);
    },
  });
  const clear = el('button', {
    class: 'danger',
    text: 'Убрать',
    onclick: async () => {
      try {
        const r = await post('/api/ts/picture/clear', {
          interface: TS.panel.id, layer: TS.layer, orderId: button.orderId,
        });
        status.textContent = 'картинка снята'
          + (r.sharedWith > 1 ? `, затронуто кнопок: ${r.sharedWith}` : '');
        await loadPanel();
      } catch (e) { status.textContent = e.message; }
    },
  });

  box.append(file, el('div', { class: 'toolbar' }, [upload, clear]));

  api('/api/ts/picture/info?' + q).then((info) => {
    if (info.hasPicture) {
      preview.replaceChildren(el('img', {
        src: '/api/ts/picture?' + q + '&t=' + Date.now(),
        alt: 'картинка кнопки',
      }));
      note.textContent = `${info.kind}, ${Math.max(1, Math.round(info.bytes / 1024))} КБ`;
    } else {
      preview.replaceChildren(el('div', {
        class: 'pic-empty', text: 'картинки нет',
      }));
      note.textContent = button.cod
        ? 'Если картинки нет у самой кнопки, касса покажет фотографию товара.'
        : '';
    }
    if (info.sharedWith > 1) {
      box.appendChild(el('div', {
        class: 'banner',
        text: `Эту же запись содержимого используют ${info.sharedWith} кнопок. `
          + 'Картинка появится на всех.',
      }));
    }
    if (!info.contentId) {
      box.appendChild(el('div', {
        class: 'banner bad',
        text: 'У кнопки нет записи содержимого — картинку положить некуда.',
      }));
    }
  }).catch(() => {
    note.textContent = 'не удалось узнать про картинку';
  });

  return box;
}

/* ------------------------------------------------------------------ старт */

$('search').addEventListener('input', () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(loadOptions, 220);
});
['groupPick', 'statePick', 'showAbsent'].forEach(
  (id) => $(id).addEventListener('change', loadOptions));
$('panelPick').addEventListener('change', () => { TS.layer = 1; TS.page = 0; loadPanel(); });
$('layerPick').addEventListener('change', () => {
  TS.layer = Number($('layerPick').value); TS.page = 0; loadPanel();
});
$('lngPick').addEventListener('change', () => loadPanel());

(async function start() {
  await loadSummary();
  await loadOptions();
  showTab(location.hash.slice(1));
}());
