# Korea Capital Gains Tax Calculator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-contained HTML prototype for a Korea residential capital gains tax calculator that classifies both the disposed asset and other household-held real estate before estimating tax.

**Architecture:** Start with one `index.html` artifact that keeps domain logic, evidence data, and UI rendering separated inside distinct script sections. If the prototype is promoted, extract the same boundaries into `src/domain`, `src/evidence`, and `src/ui`.

**Tech Stack:** Plain HTML, CSS, and JavaScript for MVP; PAS Workbench design tokens; mock evidence JSON; later Korean Law MCP / National Tax Service adapters.

---

## File Map

- Create: `prototypes/korea-capital-gains-tax/index.html`
  - Self-contained UI prototype.
  - Contains scoped CSS, domain functions, mock evidence, and rendering logic.
- Create: `prototypes/korea-capital-gains-tax/fixtures.js`
  - Synthetic test scenarios for manual and automated checks.
- Create: `prototypes/korea-capital-gains-tax/README.md`
  - Scope, review gate, source basis, and local usage.
- Modify later: `.mcp.json` under the relevant plugin only after connector scope is finalized.

## Task 1: Prototype Shell

**Files:**
- Create: `prototypes/korea-capital-gains-tax/index.html`
- Create: `prototypes/korea-capital-gains-tax/README.md`

- [ ] **Step 1: Create the prototype directory**

Run:

```bash
mkdir -p prototypes/korea-capital-gains-tax
```

Expected: directory exists.

- [ ] **Step 2: Add the initial HTML shell**

Add this structure to `prototypes/korea-capital-gains-tax/index.html`:

```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>대한민국 주택 양도세 워크벤치</title>
  <style>
    :root {
      --bg: #f6f7f8;
      --surface: #ffffff;
      --surface-muted: #eef1f4;
      --line: #d8dde3;
      --line-strong: #b9c1ca;
      --text: #17202a;
      --text-muted: #5f6b78;
      --accent: #0f766e;
      --accent-soft: #d8f3ee;
      --risk: #b42318;
      --risk-soft: #fee4e2;
      --warn: #b54708;
      --warn-soft: #ffead5;
      --ok: #027a48;
      --ok-soft: #dcfae6;
      --info: #175cd3;
      --info-soft: #dbeafe;
      --radius: 8px;
      --font: Pretendard, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: var(--font);
      letter-spacing: -0.02em;
      line-height: 1.6;
    }
  </style>
</head>
<body>
  <div class="report-shell">
    <aside class="report-sidebar">
      <strong>양도세 워크벤치</strong>
      <nav>
        <a href="#asset">양도대상</a>
        <a href="#household">보유 부동산</a>
        <a href="#result">판정/계산</a>
        <a href="#evidence">근거</a>
      </nav>
    </aside>
    <main class="report-main">
      <header class="report-header">
        <p class="eyebrow">대한민국 주택 양도소득세</p>
        <h1>세대 보유 부동산을 먼저 판정하는 양도세 계산기</h1>
        <span class="badge badge-draft">draft · 전문가 검토 필요</span>
      </header>
      <section class="kpi-strip" id="summary"></section>
      <section class="report-section" id="asset"></section>
      <section class="report-section" id="household"></section>
      <section class="report-section" id="result"></section>
      <section class="report-section" id="evidence"></section>
    </main>
  </div>
  <script>
    const appState = {
      disposedAsset: null,
      householdProperties: []
    };
  </script>
</body>
</html>
```

- [ ] **Step 3: Add README**

Add this to `prototypes/korea-capital-gains-tax/README.md`:

```markdown
# Korea Capital Gains Tax Prototype

Draft prototype for a non-specialist residential real estate capital gains tax
workbench.

This is not tax advice. Outputs are estimates for professional review. The MVP
uses mock evidence records and must mark source claims as unverified until live
retrieval is connected.

Open `index.html` in a browser.
```

- [ ] **Step 4: Commit**

Run:

```bash
git add prototypes/korea-capital-gains-tax/index.html prototypes/korea-capital-gains-tax/README.md
git commit -m "docs: scaffold korea capital gains tax prototype"
```

Expected: commit succeeds.

## Task 2: Domain Classifiers

**Files:**
- Modify: `prototypes/korea-capital-gains-tax/index.html`

- [ ] **Step 1: Add asset classification functions**

Add this script block after `appState`:

```html
<script>
  function classifyPropertyForHouseCount(property) {
    const reasons = [];
    const gaps = [];

    if (["apartment", "detached", "row_house", "multi_family"].includes(property.type)) {
      reasons.push("공부상 주택 유형으로 입력됨");
      return { status: "included", label: "주택 수 포함 가능성 높음", reasons, gaps, sourceIds: ["nts-yangdo-guide", "income-tax-act"] };
    }

    if (property.type === "officetel") {
      if (property.actualUse === "residential") {
        reasons.push("오피스텔이 실제 주거용으로 사용된 것으로 입력됨");
        return { status: "candidate", label: "주택 수 포함 검토 필요", reasons, gaps: ["실제 사용 용도 증빙", "임대차계약서", "사업자등록 여부"], sourceIds: ["tax-case-source-needed"] };
      }
      if (property.actualUse === "business") {
        reasons.push("업무용 사용으로 입력됨");
        return { status: "candidate", label: "제외 가능성 있으나 증빙 필요", reasons, gaps: ["업무용 사용 증빙"], sourceIds: ["tax-case-source-needed"] };
      }
      return { status: "unknown", label: "오피스텔 용도 확인 필요", reasons, gaps: ["실제 주거용 사용 여부"], sourceIds: ["tax-case-source-needed"] };
    }

    if (["housing_right", "occupancy_right"].includes(property.type)) {
      reasons.push("주택 취득 권리 유형으로 입력됨");
      return { status: "candidate", label: "주택 수 포함 특례 검토 필요", reasons, gaps: ["취득일", "기존 주택 양도 예정일", "특례 요건"], sourceIds: ["nts-one-house-special"] };
    }

    if (property.type === "mixed_use") {
      reasons.push("상가주택 또는 혼합용도 건물로 입력됨");
      return { status: "candidate", label: "주택 부분 비율 확인 필요", reasons, gaps: ["주거 면적", "상업 면적", "실제 사용 현황"], sourceIds: ["tax-case-source-needed"] };
    }

    return { status: "unknown", label: "주택 해당성 판정불가", reasons, gaps: ["자산 유형", "공부상 용도", "실제 사용 현황"], sourceIds: ["income-tax-act"] };
  }

  function classifyHousehold(properties) {
    const classifications = properties.map((property) => ({
      property,
      classification: classifyPropertyForHouseCount(property)
    }));
    const includedCount = classifications.filter((item) => item.classification.status === "included").length;
    const uncertainCount = classifications.filter((item) => ["candidate", "unknown"].includes(item.classification.status)).length;

    if (includedCount === 1 && uncertainCount === 0) return { status: "one_house_candidate", label: "1세대 1주택 가능성 높음", classifications };
    if (includedCount <= 1 && uncertainCount > 0) return { status: "conditional", label: "1세대 1주택 여부 조건부", classifications };
    if (includedCount === 2) return { status: "temporary_two_house_check", label: "일시적 2주택 특례 검토 필요", classifications };
    return { status: "multi_house_candidate", label: "다주택 가능성 높음", classifications };
  }
</script>
```

- [ ] **Step 2: Test manually in browser console**

Run in the browser console:

```javascript
classifyHousehold([
  { id: "disposed", type: "apartment", actualUse: "residential" },
  { id: "spouse-office", type: "officetel", actualUse: "unknown" }
]).label
```

Expected: `"1세대 1주택 여부 조건부"`.

- [ ] **Step 3: Commit**

Run:

```bash
git add prototypes/korea-capital-gains-tax/index.html
git commit -m "feat: add house-count classification rules"
```

Expected: commit succeeds.

## Task 3: Tax Calculation Scaffold

**Files:**
- Modify: `prototypes/korea-capital-gains-tax/index.html`

- [ ] **Step 1: Add arithmetic helpers**

Add this script block after the classifier script:

```html
<script>
  function yearsBetween(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime()) || end < start) return null;
    return Math.floor((end - start) / (365.2425 * 24 * 60 * 60 * 1000));
  }

  function calculateGain(input) {
    const transferValue = Number(input.transferValue || 0);
    const acquisitionValue = Number(input.acquisitionValue || 0);
    const necessaryExpenses = Number(input.necessaryExpenses || 0);
    return transferValue - acquisitionValue - necessaryExpenses;
  }

  function calculateDraftTax(input, householdJudgment) {
    const gain = calculateGain(input);
    const holdingYears = yearsBetween(input.acquisitionDate, input.transferDate);
    const basicDeduction = gain > 0 ? 2500000 : 0;
    const longTermDeduction = householdJudgment.status === "one_house_candidate" && holdingYears >= 3
      ? Math.floor(gain * 0.06)
      : 0;
    const taxableBase = Math.max(0, gain - longTermDeduction - basicDeduction);
    const incomeTax = Math.floor(taxableBase * 0.24);
    const localIncomeTax = Math.floor(incomeTax * 0.1);

    return {
      status: householdJudgment.status === "one_house_candidate" ? "draft" : "conditional",
      gain,
      holdingYears,
      longTermDeduction,
      basicDeduction,
      taxableBase,
      incomeTax,
      localIncomeTax,
      totalTax: incomeTax + localIncomeTax,
      caveat: "MVP 산식은 구조 검증용 초안이며 세율·공제율은 공식 source snapshot으로 교체 필요"
    };
  }
</script>
```

- [ ] **Step 2: Test manually in browser console**

Run:

```javascript
calculateDraftTax({
  transferValue: 1000000000,
  acquisitionValue: 700000000,
  necessaryExpenses: 20000000,
  acquisitionDate: "2018-01-01",
  transferDate: "2026-05-18"
}, classifyHousehold([{ id: "disposed", type: "apartment", actualUse: "residential" }])).totalTax
```

Expected: a positive number. Treat the amount as a placeholder until source-verified rates are implemented.

- [ ] **Step 3: Commit**

Run:

```bash
git add prototypes/korea-capital-gains-tax/index.html
git commit -m "feat: add draft capital gains tax arithmetic"
```

Expected: commit succeeds.

## Task 4: Guided UI

**Files:**
- Modify: `prototypes/korea-capital-gains-tax/index.html`

- [ ] **Step 1: Render disposed asset form**

Add rendering functions:

```html
<script>
  function renderAssetForm() {
    document.querySelector("#asset").innerHTML = `
      <h2>1. 이번에 파는 부동산</h2>
      <div class="form-grid">
        <label>자산 유형
          <select id="disposed-type">
            <option value="apartment">아파트</option>
            <option value="detached">단독주택</option>
            <option value="row_house">연립/다세대</option>
            <option value="officetel">오피스텔</option>
            <option value="mixed_use">상가주택/혼합용도</option>
            <option value="housing_right">분양권</option>
            <option value="occupancy_right">입주권</option>
            <option value="unknown">잘 모르겠음</option>
          </select>
        </label>
        <label>실제 사용
          <select id="disposed-use">
            <option value="residential">주거용</option>
            <option value="business">업무용</option>
            <option value="mixed">혼합</option>
            <option value="unknown">잘 모르겠음</option>
          </select>
        </label>
        <label>양도가액 <input id="transfer-value" inputmode="numeric" value="1000000000"></label>
        <label>취득가액 <input id="acquisition-value" inputmode="numeric" value="700000000"></label>
        <label>필요경비 <input id="necessary-expenses" inputmode="numeric" value="20000000"></label>
        <label>취득일 <input id="acquisition-date" type="date" value="2018-01-01"></label>
        <label>양도일 <input id="transfer-date" type="date" value="2026-05-18"></label>
      </div>
    `;
  }
</script>
```

- [ ] **Step 2: Render household property list**

Add:

```html
<script>
  function renderHouseholdSection() {
    document.querySelector("#household").innerHTML = `
      <h2>2. 세대 보유 부동산</h2>
      <p class="section-note">본인, 배우자, 같은 세대원이 가진 부동산을 추가하세요. 주택 수 포함 여부는 시스템이 판정합니다.</p>
      <button type="button" id="add-property">보유 부동산 추가</button>
      <div id="property-list"></div>
    `;
    document.querySelector("#add-property").addEventListener("click", () => {
      appState.householdProperties.push({ id: crypto.randomUUID(), type: "officetel", actualUse: "unknown", label: "추가 부동산" });
      renderAll();
    });
  }
</script>
```

- [ ] **Step 3: Render result and evidence**

Add:

```html
<script>
  const evidence = {
    "nts-yangdo-guide": {
      title: "국세청 알기 쉬운 양도소득세",
      url: "https://www.nts.go.kr/tax/yangdo_2.html",
      verified: false
    },
    "income-tax-act": {
      title: "소득세법 및 하위 법령",
      url: "https://www.law.go.kr",
      verified: false
    },
    "nts-one-house-special": {
      title: "국세청 1세대1주택 비과세 관련 주택수 특례",
      url: "https://www.nts.go.kr/tax/yangdo_2.html",
      verified: false
    },
    "tax-case-source-needed": {
      title: "국세법령정보시스템 판례/예규 확인 필요",
      url: "https://txsi.hometax.go.kr",
      verified: false
    }
  };

  function renderAll() {
    renderAssetForm();
    renderHouseholdSection();
    const disposedAsset = {
      id: "disposed",
      type: document.querySelector("#disposed-type")?.value || "apartment",
      actualUse: document.querySelector("#disposed-use")?.value || "residential"
    };
    const household = classifyHousehold([disposedAsset, ...appState.householdProperties]);
    const tax = calculateDraftTax({
      transferValue: document.querySelector("#transfer-value")?.value,
      acquisitionValue: document.querySelector("#acquisition-value")?.value,
      necessaryExpenses: document.querySelector("#necessary-expenses")?.value,
      acquisitionDate: document.querySelector("#acquisition-date")?.value,
      transferDate: document.querySelector("#transfer-date")?.value
    }, household);

    document.querySelector("#summary").innerHTML = `
      <div><strong>${household.label}</strong><span>세대 주택 수 판정</span></div>
      <div><strong>${tax.totalTax.toLocaleString()}원</strong><span>초안 예상세액</span></div>
      <div><strong>${tax.status}</strong><span>결과 상태</span></div>
    `;
    document.querySelector("#result").innerHTML = `
      <h2>3. 판정 및 계산</h2>
      <p>${tax.caveat}</p>
      <pre>${JSON.stringify({ household, tax }, null, 2)}</pre>
    `;
    document.querySelector("#evidence").innerHTML = `
      <h2>4. 근거 및 Gap Classification</h2>
      <ul>${Object.values(evidence).map((item) => `<li><a href="${item.url}">${item.title}</a> · ${item.verified ? "verified" : "unverified"}</li>`).join("")}</ul>
    `;
  }

  renderAll();
</script>
```

- [ ] **Step 4: Commit**

Run:

```bash
git add prototypes/korea-capital-gains-tax/index.html
git commit -m "feat: add guided capital gains tax UI"
```

Expected: commit succeeds.

## Task 5: Fixtures And Verification

**Files:**
- Create: `prototypes/korea-capital-gains-tax/fixtures.js`
- Modify: `prototypes/korea-capital-gains-tax/README.md`

- [ ] **Step 1: Add synthetic fixtures**

Create `fixtures.js`:

```javascript
export const fixtures = [
  {
    name: "one-house apartment",
    disposedAsset: { id: "disposed", type: "apartment", actualUse: "residential" },
    otherProperties: [],
    expectedHouseholdStatus: "one_house_candidate"
  },
  {
    name: "spouse officetel unknown use",
    disposedAsset: { id: "disposed", type: "apartment", actualUse: "residential" },
    otherProperties: [{ id: "spouse-officetel", type: "officetel", actualUse: "unknown" }],
    expectedHouseholdStatus: "conditional"
  },
  {
    name: "mixed-use building unknown split",
    disposedAsset: { id: "disposed", type: "mixed_use", actualUse: "mixed" },
    otherProperties: [],
    expectedHouseholdStatus: "conditional"
  }
];
```

- [ ] **Step 2: Add manual verification checklist**

Append to `README.md`:

```markdown
## Manual Verification

- Open `index.html`.
- Confirm the first viewport shows draft status, house-count status, and tax estimate.
- Add an officetel as another household property.
- Confirm the result changes to conditional or review-needed.
- Confirm evidence entries are marked unverified until live retrieval is connected.
- Confirm no text overlaps at 390px mobile width and 1440px desktop width.
```

- [ ] **Step 3: Commit**

Run:

```bash
git add prototypes/korea-capital-gains-tax/fixtures.js prototypes/korea-capital-gains-tax/README.md
git commit -m "test: add capital gains tax prototype fixtures"
```

Expected: commit succeeds.

## Task 6: MCP Evidence Integration Design

**Files:**
- Modify: `docs/implementation/korean-law-mcp-setup.md`
- Create: `docs/implementation/korea-tax-source-connector-notes.md`

- [ ] **Step 1: Document tool requirements**

Create `docs/implementation/korea-tax-source-connector-notes.md`:

```markdown
# Korea Tax Source Connector Notes

## Required Read Tools

- `search_law(query, effective_date)` for statutes and subordinate regulations.
- `get_law_text(identifier, article, effective_date)` for exact provisions.
- `search_decisions(query, source_type, effective_date)` for rulings, precedents,
  and tax tribunal decisions.
- `get_decision_text(identifier)` for cited decision text.
- `search_nts_guidance(query)` for National Tax Service guidance if not covered
  by the law connector.
- `get_nts_guidance(identifier)` for official guidance text.

## Required Result Metadata

- source name
- source type
- citation-ready identifier
- URL
- retrieved timestamp
- effective date or publication date
- verified flag
- short snippet

## Safety Gate

The calculator must not upgrade a result from `draft` to `reviewed`. Only a
qualified human reviewer can do that outside the app.
```

- [ ] **Step 2: Commit**

Run:

```bash
git add docs/implementation/korea-tax-source-connector-notes.md
git commit -m "docs: define korea tax source connector requirements"
```

Expected: commit succeeds.

## Task 7: Final Verification

**Files:**
- No file changes unless verification reveals an issue.

- [ ] **Step 1: Run repository checks**

Run:

```bash
python3 -m compileall scripts
uv run --with pyyaml python scripts/lint-tool-scope.py
git status --short
```

Expected:

- scripts compile.
- lint-tool-scope passes.
- git status shows only expected local changes, if any.

- [ ] **Step 2: Run vault harness verification**

From `/Users/kjun/vault`, run:

```bash
./Harness/verify.sh
```

Expected: verification passes or produces documented non-blocking failures.

## Self-Review

- Spec coverage: plan covers guided UI, disposed asset classification, other
  household property classification, tax arithmetic scaffold, evidence layer,
  MCP connector requirements, and verification.
- Placeholder scan: no `TBD` or unstated implementation steps remain. Draft tax
  rates are explicitly marked as placeholders requiring source replacement.
- Type consistency: `disposedAsset`, `householdProperties`, `classifyHousehold`,
  `calculateDraftTax`, and evidence IDs are consistent across tasks.

