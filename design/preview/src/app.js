// Screen switcher + the interactions that sell the flow.
const $ = (s, r = document) => r.querySelector(s)
const $$ = (s, r = document) => [...r.querySelectorAll(s)]
const D = window.DATA
const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c])
const icon = (n) => `<svg class="i" viewBox="0 0 24 24" aria-hidden="true">${window.ICONS[n]}</svg>`

// Runs table
const statusLabel = { run: 'Running', wait: 'Waiting for you', done: 'Delivered', fail: 'Needs attention' }
function renderRuns(q = '') {
  const body = $('#runs-body')
  if (!body) return
  const rows = D.runs.filter((r) => (r.client + r.sector + r.title).toLowerCase().includes(q.toLowerCase()))
  body.innerHTML = rows.length
    ? rows.map((r) => `<tr data-go="${r.go}">
        <td><div class="client">${esc(r.client)}</div><div class="xs muted">${esc(r.title)}</div></td>
        <td class="hide-sm"><span class="tag">${esc(r.sector)}</span></td>
        <td><span class="status ${r.status}">${r.status === 'wait' ? esc(r.waiting) : statusLabel[r.status]}</span></td>
        <td class="hide-sm mono num small">${esc(r.duration)}</td>
        <td class="r mono num small">${esc(r.cost)}</td>
        <td class="hide-sm muted small">${esc(r.when)}</td></tr>`).join('')
    : `<tr><td colspan="6"><div class="empty">${icon('search')}<h3>No runs match "${esc(q)}"</h3><p>Try a client name or a sector such as fintech.</p></div></td></tr>`
}
renderRuns()
$('#runs-q')?.addEventListener('input', (e) => renderRuns(e.target.value))

// Sticky run sub-nav on every run view
const RUN_TABS = [['live-run', 'Timeline'], ['gate-1', 'Brief'], ['architecture', 'Architecture'], ['prototype', 'Prototype'], ['deck', 'Deck and video'], ['gate-2', 'Publish']]
$$('.screen[data-run]').forEach((s) => {
  const d = s.dataset
  const bar = document.createElement('div')
  bar.className = 'subnav'
  const tabs = RUN_TABS.map(([id, t]) => '<a href="#' + id + '" data-go="' + id + '"' + (id === d.tab ? ' aria-current="page"' : '') + '>' + t + '</a>').join('')
  bar.innerHTML = '<div class="subnav-id"><a href="#runs" data-go="runs">Runs</a><span class="sep">/</span><b>' + d.client + '</b><span class="rid" title="Run ID">' + d.run + '</span><span class="tag">' + d.sector + '</span><span class="badge ' + d.state + '" role="status">' + d.stateLabel + '</span></div><nav class="subnav-tabs" aria-label="Run pages">' + tabs + '</nav>'
  s.prepend(bar)
})

// Screen switching
const screens = $$('.screen')
const nav = $('#nav')
function show(id) {
  const s = screens.find((x) => x.id === id) || screens[0]
  screens.forEach((x) => x.classList.toggle('active', x === s))
  ;[...nav.children].forEach((b) => b.setAttribute('aria-current', String(b.dataset.id === s.id)))
  document.body.classList.toggle('public', s.dataset.chrome === 'none')
  $$('[data-nav]').forEach((a) => a.toggleAttribute('aria-current', false))
  $$(`[data-nav="${s.dataset.nav}"]`).forEach((a) => a.setAttribute('aria-current', 'page'))
  history.replaceState(null, '', '#' + s.id)
  window.scrollTo(0, 0)
}
screens.forEach((s) => {
  const b = document.createElement('button')
  b.textContent = s.dataset.title
  b.dataset.id = s.id
  b.onclick = () => show(s.id)
  nav.appendChild(b)
})

// Toasts (sileo)
const T = {
  started: ['success', 'Run started', 'Meeting Intelligence is reading the transcript.'],
  approved1: ['success', 'Brief approved', 'Solution Architect is designing the system.'],
  changes: ['info', 'Change request sent', 'Only the prototype is rebuilt. About 2 minutes.'],
  published: ['success', 'Published', 'Repo created and 6 issues opened.'],
  copied: ['success', 'Link copied', 'Anyone with the link can view the summary, prototype and deck.'],
  saved: ['success', 'Settings saved'],
  retry: ['info', 'Retrying the build', 'Prototype Builder gets 3 more fix attempts.'],
  budget: ['success', 'Budget raised to $0.10 for this run', 'Pitch and Docs continues.'],
  tested: ['success', 'Gateway connected', 'fast, smart and claude-haiku-5-5 answered.'],
}
function toast(k) {
  const t = T[k]
  if (!t || !window.sileo) return
  window.sileo[t[0]](t[2] ? { title: t[1], description: t[2] } : { title: t[1] })
}

// Delegated clicks
document.addEventListener('click', (e) => {
  const el = e.target.closest('[data-go],[data-open],[data-close],[data-toast],[data-more],.sw,.seg button,.combo-btn,.combo-opt,.slide')
  if (!el) {
    $$('.combo.open').forEach((c) => c.classList.remove('open'))
    return
  }
  if (el.matches('a[href^="#"]')) e.preventDefault()
  if (el.dataset.open) $('#' + el.dataset.open).classList.add('open')
  if (el.hasAttribute('data-close')) el.closest('.scrim').classList.remove('open')
  if (el.dataset.go) show(el.dataset.go)
  if (el.dataset.toast) toast(el.dataset.toast)
  if (el.hasAttribute('data-more')) {
    const c = el.previousElementSibling
    c.classList.toggle('open')
    el.textContent = c.classList.contains('open') ? 'Show less' : 'Show more'
  }
  if (el.matches('.sw')) el.setAttribute('aria-checked', String(el.getAttribute('aria-checked') !== 'true'))
  if (el.matches('.seg button')) {
    $$('button', el.parentElement).forEach((b) => b.setAttribute('aria-pressed', String(b === el)))
    const dev = el.closest('.panel')?.querySelector('.device')
    if (dev && el.dataset.device) dev.classList.toggle('mobile', el.dataset.device === 'mobile')
  }
  if (el.matches('.combo-btn')) {
    const c = el.closest('.combo')
    c.classList.toggle('open')
    el.setAttribute('aria-expanded', String(c.classList.contains('open')))
    $('input', c)?.focus()
  }
  if (el.matches('.combo-opt')) {
    const c = el.closest('.combo')
    const label = el.dataset.value || $('input', c).value.trim()
    if (label) $('.combo-btn .val', c).textContent = label
    $$('.combo-opt', c).forEach((o) => o.setAttribute('aria-selected', String(o === el)))
    c.classList.remove('open')
  }
  if (el.matches('.slide')) {
    $$('.slide').forEach((s) => s.setAttribute('aria-current', String(s === el)))
    $('#slide-title').textContent = el.querySelector('.h').textContent
  }
})

// Combobox filtering with inline create
$$('.combo').forEach((c) => {
  const input = $('input', c)
  const create = $('.combo-opt.create', c)
  input?.addEventListener('input', () => {
    const q = input.value.trim().toLowerCase()
    $$('.combo-opt:not(.create)', c).forEach((o) => (o.style.display = o.dataset.value.toLowerCase().includes(q) ? '' : 'none'))
    create.style.display = q ? '' : 'none'
    $('.q', create).textContent = input.value.trim()
  })
})
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    $$('.scrim.open').forEach((s) => s.classList.remove('open'))
    $$('.combo.open').forEach((c) => c.classList.remove('open'))
  }
})

show(location.hash.slice(1) || 'runs')
