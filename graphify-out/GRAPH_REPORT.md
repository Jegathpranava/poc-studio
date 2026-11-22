# Graph Report - poc-studio  (2026-11-22)

## Corpus Check
- 16 files · ~46,791 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: .css 3, .example 1, (none) 1)

## Summary
- 813 nodes · 2167 edges · 61 communities (42 shown, 19 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 207 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `18c09419`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- i
- W
- mount
- Uv
- Tasks
- I
- _t
- Xe
- constructor
- Cn
- A
- KT
- start
- Ar
- PoC Studio: design spec
- bS
- $v
- $f
- kz
- Wv
- app.js
- xT
- rt
- PoC Studio — Developer Guidelines & Architecture Rules
- readKeyframes
- readValue
- build.mjs
- Ov
- PoC Studio — Developer Guidelines & Architecture Rules
- UI preview
- add
- Qe
- initAnimation
- Fi
- addValue
- Hf
- safeToRemove
- yz
- eb
- h1
- r3
- ue
- sb
- addVariantChild
- dp
- ef
- i2
- l2
- mx
- measureInstanceViewportBox
- mg
- Na
- PA
- sortInstanceNodePosition
- vm
- owner-direction-2026-11-22.md
- NEXT_STEPS.md
- check-github-token.sh

## God Nodes (most connected - your core abstractions)
1. `A()` - 58 edges
2. `i()` - 53 edges
3. `a()` - 43 edges
4. `KT()` - 40 edges
5. `Tasks` - 31 edges
6. `o()` - 30 edges
7. `constructor()` - 30 edges
8. `Wv()` - 25 edges
9. `W()` - 25 edges
10. `Uv()` - 22 edges

## Surprising Connections (you probably didn't know these)
- `Ls()` --indirect_call--> `a()`  [INFERRED]
  design/preview/src/toast.js → design/preview/src/toast.js  _Bridges community 2 → community 1_
- `eo()` --indirect_call--> `a()`  [INFERRED]
  design/preview/src/toast.js → design/preview/src/toast.js  _Bridges community 6 → community 1_
- `js()` --indirect_call--> `i()`  [INFERRED]
  design/preview/src/toast.js → design/preview/src/toast.js  _Bridges community 11 → community 1_
- `Sv()` --indirect_call--> `t1()`  [INFERRED]
  design/preview/src/toast.js → design/preview/src/toast.js  _Bridges community 4 → community 12_
- `Ar()` --indirect_call--> `a()`  [INFERRED]
  design/preview/src/toast.js → design/preview/src/toast.js  _Bridges community 14 → community 1_

## Import Cycles
- None detected.

## Communities (61 total, 19 thin omitted)

### Community 1 - "i"
Cohesion: 0.08
Nodes (68): bD(), Cg(), ch(), Dd(), E1(), en(), er(), eu() (+60 more)

### Community 2 - "W"
Cohesion: 0.06
Nodes (45): _1(), ci(), cM(), Cr(), cS(), dO(), dS(), eS() (+37 more)

### Community 3 - "mount"
Cohesion: 0.06
Nodes (46): _4(), Be(), bg(), bindToMotionValue(), c2(), Cf(), cl(), createPanHandlers() (+38 more)

### Community 4 - "Uv"
Cohesion: 0.08
Nodes (41): bh(), bx(), De(), Eh(), ep(), Ft(), fu(), g1() (+33 more)

### Community 5 - "Tasks"
Cohesion: 0.05
Nodes (36): File map, Global constraints, Increment 1: skeleton (visible: the Runs page on real tokens), Increment 2: ingest, Meeting Intelligence, Gate 1 (visible: a transcript becomes an approved brief), Increment 3: Solution Architect (visible: an architecture page with a diagram and costs), Increment 4: Prototype Builder (visible: a screen pack, a building Next.js app, and a live preview), Increment 5: deck and video (visible: the reference-format deck and an MP4 in the app), Increment 6: QA, Gate 2, publish (visible: a real or mocked repo with issues) (+28 more)

### Community 6 - "I"
Cohesion: 0.07
Nodes (32): b1(), b3(), Ca(), du(), eo(), Fv(), hv(), I() (+24 more)

### Community 7 - "_t"
Cohesion: 0.12
Nodes (17): ao(), Da(), Dv(), dx(), e3(), hx(), mO(), pO() (+9 more)

### Community 8 - "Xe"
Cohesion: 0.13
Nodes (28): Ad(), bo(), Br(), Bu(), Dr(), Gd(), gE(), gO() (+20 more)

### Community 9 - "constructor"
Cohesion: 0.09
Nodes (28): af(), cancel(), constructor(), end(), endPanSession(), finish(), handleScroll(), kE() (+20 more)

### Community 10 - "Cn"
Cohesion: 0.12
Nodes (23): aS(), bp(), bT(), c1(), Cn(), cp(), cV(), dc() (+15 more)

### Community 11 - "A"
Cohesion: 0.15
Nodes (22): A(), a1(), Ax(), cd(), ey(), Fh(), hc(), hE() (+14 more)

### Community 12 - "KT"
Cohesion: 0.21
Nodes (21): Aa(), ap(), cT(), Fd(), gp(), Ih(), In(), KT() (+13 more)

### Community 13 - "start"
Cohesion: 0.20
Nodes (21): addListeners(), clearAnimation(), clearListeners(), commitStyles(), destroy(), getAxisMotionValue(), getProps(), ig() (+13 more)

### Community 14 - "Ar"
Cohesion: 0.13
Nodes (19): Ar(), Av(), $C(), cx(), d1(), fa(), fx(), lu() (+11 more)

### Community 15 - "PoC Studio: design spec"
Cohesion: 0.11
Nodes (18): 10. Delivery increments (each one runnable and verified), 11. Testing, 12. Work that must happen on the owner's machine, 13. Decisions made on the owner's behalf (Claude's call), 14. Open questions, 1. Intent and why, 2. Goals, non-goals, anti-goals, 3. Amendments to the brief (this spec wins) (+10 more)

### Community 16 - "bS"
Cohesion: 0.12
Nodes (18): bS(), build(), bz(), c4(), Ez(), mM(), mp(), Nf() (+10 more)

### Community 17 - "$v"
Cohesion: 0.19
Nodes (14): Az(), eT(), gu(), hT(), Iu(), Li(), nV(), Qd() (+6 more)

### Community 18 - "$f"
Cohesion: 0.17
Nodes (12): b4(), eD(), $f(), G2(), M2(), m4(), rm(), S2() (+4 more)

### Community 19 - "kz"
Cohesion: 0.17
Nodes (12): BM(), $e(), f2(), Fg(), Ka(), Kf(), Kg(), kz() (+4 more)

### Community 20 - "Wv"
Cohesion: 0.29
Nodes (12): ir(), jT(), lh(), Me(), oh(), pc(), Ud(), Ws() (+4 more)

### Community 21 - "app.js"
Cohesion: 0.22
Nodes (8): esc(), icon(), nav, renderRuns(), RUN_TABS, screens, statusLabel, T

### Community 22 - "xT"
Cohesion: 0.22
Nodes (11): Ai(), aT(), bn(), $d(), Ks(), l1(), r1(), ra() (+3 more)

### Community 23 - "rt"
Cohesion: 0.31
Nodes (11): bi(), Bv(), Id(), pr(), Ri(), rt(), Ti(), uT() (+3 more)

### Community 24 - "PoC Studio — Developer Guidelines & Architecture Rules"
Cohesion: 0.22
Nodes (8): 7 agents, Commands, Core tech stack (budget build, decided at intake), Human approval gates, Mission, PoC Studio — Developer Guidelines & Architecture Rules, Rules, Start here

### Community 25 - "readKeyframes"
Cohesion: 0.22
Nodes (9): complete(), Hy(), iz(), Jp(), measureEndState(), readKeyframes(), resolveNoneKeyframes(), resume() (+1 more)

### Community 26 - "readValue"
Cohesion: 0.22
Nodes (9): dl(), getBaseTarget(), getBaseTargetFromProps(), qf(), readValue(), readValueFromInstance(), renderInstance(), setBaseTarget() (+1 more)

### Community 27 - "build.mjs"
Cohesion: 0.32
Nodes (4): build(), here, orderScripts(), read()

### Community 28 - "Ov"
Cohesion: 0.29
Nodes (8): ab(), Ex(), ib(), $l(), nh(), Ov(), tb(), Vi()

### Community 29 - "PoC Studio — Developer Guidelines & Architecture Rules"
Cohesion: 0.29
Nodes (6): 6 Specialist Agents & State, Coding Style & Budget Rules, Core Tech Stack, Human Approval Gates, Mission, PoC Studio — Developer Guidelines & Architecture Rules

### Community 30 - "UI preview"
Cohesion: 0.33
Nodes (5): After approval, Build, Layout, Rules, UI preview

### Community 31 - "add"
Cohesion: 0.33
Nodes (6): add(), promote(), relegate(), remove(), Xi(), za()

### Community 32 - "Qe"
Cohesion: 0.40
Nodes (6): CO(), f1(), Qe(), s1(), se(), yu()

### Community 33 - "initAnimation"
Cohesion: 0.40
Nodes (5): attachTimeline(), initAnimation(), ll(), rl(), uy()

### Community 34 - "Fi"
Cohesion: 0.50
Nodes (5): eE(), Fi(), gR(), tr(), yR()

### Community 35 - "addValue"
Cohesion: 0.50
Nodes (4): addValue(), getValue(), removeValue(), removeValueFromRenderState()

### Community 36 - "Hf"
Cohesion: 0.50
Nodes (4): Ag(), fM(), Hf(), ui()

### Community 37 - "safeToRemove"
Cohesion: 0.50
Nodes (4): componentDidMount(), componentDidUpdate(), getSnapshotBeforeUpdate(), safeToRemove()

### Community 38 - "yz"
Cohesion: 0.50
Nodes (4): la(), Mf(), NM(), yz()

### Community 39 - "eb"
Cohesion: 0.67
Nodes (3): eb(), KO(), Sr()

### Community 40 - "h1"
Cohesion: 0.67
Nodes (3): h1(), qT(), vr()

### Community 41 - "r3"
Cohesion: 1.00
Nodes (3): km(), pi(), r3()

### Community 43 - "sb"
Cohesion: 1.00
Nodes (3): sb(), e(), n()

## Knowledge Gaps
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `c()` connect `i` to `constructor`, `A`, `app.js`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 50 inferred relationships involving `i()` (e.g. with `ap()` and `Ar()`) actually correct?**
  _`i()` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Should `toast.js` be split into smaller, more focused modules?**
  _Cohesion score 0.023809523809523808 - nodes in this community are weakly interconnected._
- **Why does `oT()` connect `i` to `toast.js`, `Cn`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `a()` (e.g. with `ap()` and `Ar()`) actually correct?**
  _`a()` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Should `i` be split into smaller, more focused modules?**
  _Cohesion score 0.08013640238704177 - nodes in this community are weakly interconnected._
- **Why does `we()` connect `_t` to `toast.js`, `i`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._