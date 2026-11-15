/**
 * Interactive UI for the project demo.
 * The charts and graph are a deliberately synthetic teaching aid, not LLM outputs.
 * Real experiment measurements are produced separately by the Python runner.
 */
const $ = (selector) => document.querySelector(selector);
const clamp = (value, low, high) => Math.max(low, Math.min(high, value));
const pct = (value) => `${Math.round(value)}%`;
const escapeHTML = (s) => String(s).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const claims = [
  {
    id: 'HL-001', category: 'Transportation', title: 'HarborLink permanently halts all ferry service next month',
    statement: 'HarborLink’s fictional ferry service will permanently stop operating next month.',
    verdict: 'Refuted', impact: 'High', posted: 'Illustrative case · 1',
    summary: 'A brief maintenance closure has been reframed as a permanent shutdown.',
    evidence: [
      { id: 'E1', name: 'Operator bulletin', type: 'Primary source', strength: 96, excerpt: 'A weekend maintenance closure is scheduled. Regular ferry service resumes on Monday.', source: 'Fictional HarborLink bulletin (demo)' },
      { id: 'E2', name: 'Published service calendar', type: 'Supporting source', strength: 87, excerpt: 'Service remains scheduled for the following month, except for the announced weekend.', source: 'Fictional HarborLink timetable (demo)' },
      { id: 'E3', name: 'Unverified community posts', type: 'Social discussion', strength: 18, excerpt: 'Several accounts repeat the claim that the closure is permanent, without original documentation.', source: 'Synthetic social messages (demo)' }
    ]
  },
  {
    id: 'TL-002', category: 'Public services', title: 'Townline Library introduces Sunday opening hours',
    statement: 'The fictional Townline library added Sunday opening hours.',
    verdict: 'Supported', impact: 'Medium', posted: 'Illustrative case · 2',
    summary: 'The revised weekly schedule lists additional weekend hours.',
    evidence: [
      { id: 'E1', name: 'Updated operating calendar', type: 'Primary source', strength: 95, excerpt: 'The fictional library now opens on Sundays between 12:00 and 16:00.', source: 'Fictional library schedule (demo)' },
      { id: 'E2', name: 'Community announcement', type: 'Supporting source', strength: 79, excerpt: 'A notice announces the added Sunday opening window.', source: 'Fictional community notice (demo)' }
    ]
  },
  {
    id: 'SC-003', category: 'Technology', title: 'City to replace every school bus with self-driving vehicles',
    statement: 'A fictional city will replace every school bus with autonomous vehicles next year.',
    verdict: 'Not Enough Evidence', impact: 'Medium', posted: 'Illustrative case · 3',
    summary: 'There is no confirmed procurement or funding decision in the example record.',
    evidence: [
      { id: 'E1', name: 'Budget review', type: 'Incomplete source', strength: 55, excerpt: 'The synthetic briefing contains no approved funding line for the proposed replacement.', source: 'Fictional city briefing (demo)' },
      { id: 'E2', name: 'Online discussion', type: 'Social discussion', strength: 15, excerpt: 'Social users speculate about a possible pilot. No formal decision is shown.', source: 'Synthetic social messages (demo)' }
    ]
  }
];

const state = { view: 'overview', claimIndex: 0, rumor: 55, factCheck: 40, grounding: true, selectedAgent: 10, run: 1, loadedReport: null };
const viewMeta = {
  overview: ['Overview', 'When rumors spread, does AI follow?', 'Explore how repeated misleading claims compete with evidence, and how grounded prompts may help models resist them.'],
  claims: ['Claim explorer', 'Investigate a claim, not just a headline.', 'Compare the claim, its labeled verdict, and the synthetic social context used for controlled testing.'],
  network: ['Diffusion lab', 'Watch information move through a network.', 'Explore a stylized network of agents. This is a visual simulation, not observed user behavior.'],
  evidence: ['Evidence audit', 'Trace the answer back to evidence.', 'Separate primary sources from repeated social claims and inspect what a model should cite.'],
  experiments: ['Experiments', 'One claim. Three controlled conditions.', 'Design paired comparisons and export configurations before collecting real model measurements.']
};

function values() {
  // Illustrative deterministic formulas: never report these values as study outcomes.
  const r = state.rumor, f = state.factCheck;
  const ungrounded = clamp(88 - r * .57 + f * .13, 11, 98);
  const grounded = clamp(92 - r * .14 + f * .11, 35, 99);
  const gap = grounded - ungrounded;
  const misinformation = clamp(10 + r * .66 - f * .25, 0, 92);
  const spread = clamp(16 + r * .79 - f * .39, 2, 98);
  return { ungrounded, grounded, gap, misinformation, spread };
}

function metricCard(label, value, badge, flavor, icon) {
  return `<div class="metric-card"><div class="metric-head"><span>${label}</span><span class="metric-icon ${flavor}">${icon}</span></div><div class="metric-value">${value}</div><div class="metric-foot ${flavor}">${badge}</div></div>`;
}
function sectionHeading(title, caption, right = '') {
  return `<div class="section-head"><div><h2>${title}</h2><p>${caption}</p></div>${right}</div>`;
}
function gradientPath(points, w, h, pad = 24) {
  return points.map((point, i) => `${i ? 'L' : 'M'}${pad + i * (w - pad * 2) / (points.length - 1)},${h - pad - point * (h - pad * 2) / 100}`).join(' ');
}
function lineChart() {
  const levels = [0,20,40,60,80,100];
  const grounded = levels.map((r) => clamp(92-r*.14+state.factCheck*.11,35,99));
  const ungrounded = levels.map((r) => clamp(88-r*.57+state.factCheck*.13,11,98));
  const w = 610, h = 236;
  const grids = [20,40,60,80,100].map((v) => {
    const y = h - 24 - v * (h - 48)/100;
    return `<line x1="24" y1="${y}" x2="586" y2="${y}" stroke="#26384d" stroke-dasharray="3 6"/><text x="0" y="${y+3}" fill="#7e91aa" font-size="10">${v}</text>`;
  }).join('');
  const dots = (series, color) => series.map((v,i) => `<circle cx="${24 + i * (w-48)/(series.length-1)}" cy="${h-24-v*(h-48)/100}" r="3.2" fill="${color}" stroke="#132137" stroke-width="2"/>`).join('');
  return `<svg class="line-chart" viewBox="0 0 ${w} ${h}" role="img" aria-label="Synthetic illustration of reliability as rumor pressure grows: grounded and ungrounded comparison">
    <defs><linearGradient id="chartGrad" x1="0" x2="0" y1="0" y2="1"><stop stop-color="#61dfca" stop-opacity=".13"/><stop offset="1" stop-color="#61dfca" stop-opacity="0"/></linearGradient></defs>
    ${grids}<path d="${gradientPath(grounded,w,h)} L586 ${h-24} L24 ${h-24} Z" fill="url(#chartGrad)"/>
    <path d="${gradientPath(ungrounded,w,h)}" stroke="#f8aa78" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="${gradientPath(grounded,w,h)}" stroke="#61dfca" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    ${dots(ungrounded, '#f8aa78')}${dots(grounded, '#61dfca')}
    ${levels.map((v,i) => `<text x="${24+i*(w-48)/5}" y="${h-6}" font-size="11" text-anchor="middle" fill="#889ab3">${v}</text>`).join('')}
  </svg>`;
}
function chartPanel() {
  return `<article class="panel chart-panel">${sectionHeading('Reliability under rumor pressure','How a model might respond as repeated misinformation increases','<span class="tag tag-dim">Illustrative projection</span>')}
    <div class="chart-legend"><span><i class="legend-swatch aqua"></i> Evidence-first prompting</span><span><i class="legend-swatch peach"></i> Context-only prompting</span></div>
    ${lineChart()}<div class="chart-axis">Social misinformation intensity (synthetic posts) →</div></article>`;
}
function miniBars() {
  const m = values();
  return `<div class="comparison-bars"><div><div class="bar-label"><span>Evidence-first</span><strong>${pct(m.grounded)}</strong></div><div class="bar-track"><div class="bar-fill aqua" style="width:${m.grounded}%"></div></div></div>
   <div><div class="bar-label"><span>Context-only</span><strong>${pct(m.ungrounded)}</strong></div><div class="bar-track"><div class="bar-fill peach" style="width:${m.ungrounded}%"></div></div></div></div>`;
}
function controlSlider(id, title, help, value, color) {
  return `<label class="control-group" for="${id}"><div class="control-title"><span>${title}</span><strong>${value}%</strong></div><input type="range" min="0" max="100" step="5" id="${id}" value="${value}" style="--thumb:${color}"/><small>${help}</small></label>`;
}
function controlsPanel() {
  return `<article class="panel controls-panel">${sectionHeading('Scenario controls','Adjust the fictional experiment environment')}
    ${controlSlider('rumorSlider', 'Rumor repetition', 'Number of misleading posts in the simulated discussion',state.rumor,'#f8aa78')}
    ${controlSlider('factSlider', 'Fact-checker presence', 'Share of agents challenging unsupported claims',state.factCheck,'#61dfca')}
    <div class="control-title switch-row"><span>Evidence-first mode</span><button class="toggle ${state.grounding?'on':''}" id="groundToggle" role="switch" aria-checked="${state.grounding}" aria-label="Toggle evidence-first mode"><span></span></button></div>
    <div class="control-note">This panel updates a toy model to explain the research design. It does not run an LLM.</div>
  </article>`;
}
function verdictTag(verdict) {
  const className = verdict==='Supported'?'verdict-supported':verdict==='Refuted'?'verdict-refuted':'verdict-unknown';
  return `<span class="verdict-tag ${className}"><span class="small-dot"></span>${escapeHTML(verdict)}</span>`;
}
function claimSelect() {
  return `<div class="claim-pills">${claims.map((c,i)=>`<button class="claim-pill ${state.claimIndex===i?'selected':''}" data-claim="${i}"><span>${escapeHTML(c.id)}</span><strong>${escapeHTML(c.category)}</strong></button>`).join('')}</div>`;
}
function evidenceList(short=false) {
  const caseStudy=claims[state.claimIndex];
  return `<div class="evidence-list">${caseStudy.evidence.slice(0,short?2:10).map((e)=>`
  <div class="evidence-entry"><span class="evidence-marker">${e.id}</span><div><div class="evidence-entry-head"><strong>${escapeHTML(e.name)}</strong><span>${escapeHTML(e.type)}</span></div><p>${escapeHTML(e.excerpt)}</p><small>${escapeHTML(e.source)}</small></div><span class="strength">${e.strength}<span>/100</span></span></div>`).join('')}</div>`;
}
function claimSpotlight() {
  const c = claims[state.claimIndex];
  return `<article class="panel claim-spotlight"><div class="claim-top"><span class="eyebrow">ACTIVE CASE / ${escapeHTML(c.id)}</span>${verdictTag(c.verdict)}</div>
    <h3>${escapeHTML(c.title)}</h3><p>${escapeHTML(c.summary)}</p><div class="case-meta"><span>◉ ${escapeHTML(c.category)}</span><span>◈ ${escapeHTML(c.impact)} impact</span><span>◷ Fictional case</span></div>
    <button class="text-link" data-view="claims">Open claim explorer <span>→</span></button>
  </article>`;
}
function seeded(index) { const x = Math.sin(index * 89.173 + 4.718) * 43758.5453; return x - Math.floor(x); }
function agents() {
  return Array.from({length:74},(_,i)=>{
    const angle = (i*137.508)*Math.PI/180;
    const radial = 19 + Math.sqrt((i+1)/74) * 201;
    const x=250 + Math.cos(angle)*radial + (seeded(i+2)-.5)*14;
    const y=211 + Math.sin(angle)*radial*.78 + (seeded(i+19)-.5)*15;
    const checker = (i * 31 % 100)<state.factCheck;
    const reached = (i * 47 % 100)<values().spread;
    return {id:i+1,x:clamp(x,18,482),y:clamp(y,20,396),checker,reached,status:checker?'Fact-checker':reached?'Exposed to rumor':'Unexposed'};
  });
}
function networkSvg(compact=false) {
  const nodes=agents();
  let edges='';
  for(let i=2;i<nodes.length;i++){
    for(const parent of [Math.floor(i*.38),Math.floor(i*.69)]){
      const a=nodes[i], b=nodes[parent];
      edges+=`<line x1="${a.x.toFixed(1)}" y1="${a.y.toFixed(1)}" x2="${b.x.toFixed(1)}" y2="${b.y.toFixed(1)}" stroke="${a.reached?'#527c87':'#334258'}" stroke-opacity="${a.reached?'.35':'.22'}" stroke-width=".9"/>`;
    }
  }
  const circles=nodes.map(n=>{
    const selected=state.selectedAgent===n.id;
    const fill=n.checker?'#61dfca':n.reached?'#f8aa78':'#70829b';
    return `<circle data-agent="${n.id}" cx="${n.x.toFixed(1)}" cy="${n.y.toFixed(1)}" r="${selected?7.4:n.checker?4.7:3.8}" fill="${fill}" stroke="${selected?'#f7fbff':'#0e1829'}" stroke-width="${selected?'2.4':'1.1'}" tabindex="0" role="button" aria-label="Select synthetic agent ${n.id}" style="cursor:pointer"/>`;
  }).join('');
  return `<svg class="network-svg ${compact?'network-compact':''}" viewBox="0 0 500 420" role="group" aria-label="Clickable diagram of 74 fictional connected agents"><defs><radialGradient id="glow"><stop stop-color="#25516a" stop-opacity=".45"/><stop offset="1" stop-color="#102237" stop-opacity="0"/></radialGradient></defs><ellipse cx="250" cy="210" rx="239" ry="184" fill="url(#glow)"/>${edges}${circles}</svg>`;
}
function networkCard(compact=false) {
  const m=values();
  return `<article class="panel network-panel">${sectionHeading(compact?'Network activity':'Agent interaction map',compact?'74 fictional agents · stylized diffusion':'Click a node to inspect its generated state','<span class="tag tag-dim">SIMULATED</span>')}
    ${networkSvg(compact)}<div class="network-legend"><span><i class="legend-dot aqua"></i> Fact-checker</span><span><i class="legend-dot peach"></i> Rumor-exposed</span><span><i class="legend-dot slate"></i> Not exposed</span></div>
    ${compact?'':`<div class="agent-detail"><span class="agent-avatar">◉</span><div><strong>Agent #${String(state.selectedAgent).padStart(2,'0')}</strong><p>${agents()[state.selectedAgent-1]?.status || 'Not selected'} · Synthetic node</p></div><span class="agent-reach">${Math.round(m.spread)}% network exposure index</span></div>`}</article>`;
}
function overview() {
  const m=values();
  const activeValue=state.grounding?m.grounded:m.ungrounded;
  return `<div class="notice-bar"><div class="notice-icon">✳</div><div><strong>Research question:</strong> Can misleading social consensus influence model verdicts even when better evidence is present?</div><span>CONTROLLED STUDY</span></div>
    <div class="metrics-grid">
      ${metricCard('Selected prompting mode',pct(activeValue),state.grounding?'Evidence-first illustration':'Context-only illustration',state.grounding?'aqua':'peach','⬡')}
      ${metricCard('Context-only robustness',pct(m.ungrounded),'− More rumor-sensitive','peach','⌁')}
      ${metricCard('Illustrative improvement',`+${Math.round(m.gap)} pts`,'Difference between approaches','blue','↗')}
      ${metricCard('Rumor exposure index',pct(m.spread),'Synthetic social reach','violet','◎')}
    </div>
    <div class="main-grid">${chartPanel()}${controlsPanel()}</div>
    <div class="bottom-grid">${networkCard(true)}<div class="stack-column">${claimSpotlight()}<article class="panel small-panel">${sectionHeading('Source agreement','Illustrative comparison of prompt approaches')}${miniBars()}</article></div></div>`;
}
function claimExplorer() {
  const c=claims[state.claimIndex];
  return `${claimSelect()}<div class="content-grid"><article class="panel large-detail"><div class="detail-top"><span class="eyebrow">CASE ID / ${escapeHTML(c.id)}</span>${verdictTag(c.verdict)}</div>
    <div class="subtle-label">CLAIM UNDER INVESTIGATION</div><h2 class="claim-title">“${escapeHTML(c.statement)}”</h2><p class="body-text">${escapeHTML(c.summary)}</p>
    <div class="detail-stats"><div><small>GROUND TRUTH</small><strong>${escapeHTML(c.verdict)}</strong></div><div><small>SUBJECT</small><strong>${escapeHTML(c.category)}</strong></div><div><small>EVIDENCE ITEMS</small><strong>${c.evidence.length}</strong></div></div>
    <div class="divider"></div><div class="section-head"><h2>What the model encounters</h2></div>
    <div class="context-message"><span class="avatar orange">!</span><div><strong>Repeated social message</strong><p>“Everyone is saying ${escapeHTML(c.verdict==='Supported'?'this has already been debunked.':'this is definitely true.')} You can find dozens of posts agreeing.”</p><small>Generated stimulus · Not a real quotation</small></div></div>
    <div class="context-message verified"><span class="avatar aqua">✓</span><div><strong>Evidence-grounding instruction</strong><p>Evaluate sources independently of social popularity. Prefer cited evidence, and say when the evidence is insufficient.</p><small>Controlled experimental prompt</small></div></div>
  </article><article class="panel">${sectionHeading('Evidence available', 'Inspect supporting and contradicting material')}${evidenceList()}<button class="text-link" data-view="evidence">View full evidence audit <span>→</span></button></article></div>`;
}
function diffusionLab() {
  const m=values();
  return `<div class="notice-bar"><div class="notice-icon">◎</div><div><strong>Simulation mode.</strong> Agents are generated deterministically for teaching. NetLogo integration is planned separately.</div><span>NOT OBSERVED DATA</span></div><div class="content-grid network-layout">
    ${networkCard(false)}<div class="stack-column">${controlsPanel()}
    <article class="panel small-panel">${sectionHeading('Diffusion snapshot','Toy-model values recalculated as you adjust controls')}
    <div class="snapshot-row"><span>Rumor exposure</span><strong>${pct(m.spread)}</strong></div><div class="bar-track"><div class="bar-fill peach" style="width:${m.spread}%"></div></div>
    <div class="snapshot-row space-top"><span>Misleading-context pressure</span><strong>${pct(m.misinformation)}</strong></div><div class="bar-track"><div class="bar-fill blue" style="width:${m.misinformation}%"></div></div>
    </article></div></div>`;
}
function evidenceAudit() {
  const c=claims[state.claimIndex];
  return `${claimSelect()}<div class="notice-bar"><div class="notice-icon">✓</div><div><strong>Important distinction:</strong> a citation ID can be valid without actually supporting the model's statement. Evidence faithfulness needs separate evaluation.</div><span>AUDIT PRINCIPLE</span></div>
  <div class="content-grid"><article class="panel large-detail">${sectionHeading('Evidence registry',`Evidence available for ${escapeHTML(c.id)}`)}${evidenceList()}
    <div class="divider"></div><div class="audit-note"><strong>Ground truth: ${escapeHTML(c.verdict)}</strong><p>These are fictional records to demonstrate how source traceability would work. Real AVeriTeC cases include question–answer evidence and source URLs.</p></div>
  </article><article class="panel"><h2>Evidence quality checklist</h2><p class="body-text">Each completed experiment should record more than answer accuracy.</p>
    ${[['Evidence available','Was a reference actually supplied?'],['Citation ID validity','Does each citation point to a known evidence item?'],['Evidence support','Does the cited passage really justify the verdict?'],['Source provenance','Can the underlying source be identified?'],['Uncertainty behavior','Does the model abstain when evidence is insufficient?']].map(([name,sub])=>`<div class="check-row"><span class="checkmark">✓</span><div><strong>${name}</strong><small>${sub}</small></div></div>`).join('')}
  </article></div>`;
}
function experiments() {
  const m=values();
  const imported=state.loadedReport;
  const isMeasured=Boolean(imported && imported.metadata && !imported.metadata.synthetic_demo);
  const reportMetrics=imported?.metrics || {};
  const measured=(condition,fallback)=>imported ? Math.round(100*(reportMetrics[condition]?.verdict_accuracy ?? 0)) : fallback;
  const rows=[
    ['A','Evidence only','Claim + source evidence; no social posts',measured('evidence_only',m.grounded)],
    ['B','Rumor pressure','Claim + evidence + repeated misleading posts',measured('rumor_pressure',m.ungrounded)],
    ['C','Evidence first','Same rumor posts, but evidence is prioritized',measured('evidence_first',m.grounded)]
  ];
  return `<div class="notice-bar"><div class="notice-icon">⚗</div><div><strong>${imported?(isMeasured?'Imported model experiment':'Imported mock experiment'):'Paired evaluation'}:</strong> ${imported?'Scores below come from the local JSON file you supplied, not the built-in toy formula.':'Hold the claim and evidence constant, then vary the social context and prompting strategy.'}</div><span>${imported?(isMeasured?'MODEL RESULTS':'MOCK RESULTS'):'DESIGNED, NOT RUN'}</span></div>
    <div class="metrics-grid three">${metricCard('Experiment conditions','03','Paired by claim','blue','≋')}${metricCard('Current example claims',String(imported?.metadata?.claim_count || 3).padStart(2,'0'),imported?'From uploaded report':'Fictional fixtures','aqua','▤')}${metricCard('Model evaluations',String(isMeasured?imported.rows.length:0).padStart(2,'0'),isMeasured?'Results imported from local experiment':'No model runs imported','peach','⌁')}</div>
    <article class="panel experiment-table">${sectionHeading('Experiment matrix','Same input claim, controlled changes in social context')}
    <div class="table-scroll"><table><thead><tr><th>CONDITION</th><th>CONTEXT</th><th>ILLUSTRATIVE SCORE</th><th>STATUS</th></tr></thead><tbody>
    ${rows.map(([letter,name,sub,score])=>`<tr><td><span class="table-letter">${letter}</span><strong>${name}</strong></td><td><span class="table-context">${sub}</span></td><td><div class="table-score"><span class="table-score-fill" style="width:${score}%"></span></div><span class="small-score">${pct(score)}</span></td><td><span class="tag tag-dim">${imported?(isMeasured?'Imported run':'Mock result'):'Demo only'}</span></td></tr>`).join('')}</tbody></table></div>
    <div class="experiment-footer"><div><strong>${imported?'Experiment file imported':'Ready for real evaluation'}</strong><p>${imported?`Model: ${escapeHTML(imported.metadata.model)} · ${imported.rows.length} predictions · ${isMeasured?'Live-provider report':'Mock-provider report'}`:'Use the Python command-line runner with a local Qwen model to generate real result files.'}</p></div><div class="button-group"><button class="button button-secondary" id="importReportButton">Import results JSON</button><button class="button button-secondary" id="exportMatrixButton">Export configuration</button></div></div></article>
    <article class="panel">${sectionHeading('What we will measure','Research metrics planned for actual experiments')}
    <div class="measure-grid">${[['Verdict accuracy','Compare outputs to annotated claim labels.'],['Answer flip rate','How often social pressure changes the evidence-only verdict.'],['Citation-ID validity','Verify that referenced evidence identifiers exist.'],['Unsupported claim rate','Manually audit whether the cited text supports the answer.']].map(([title,description],i)=>`<div class="measure-card"><div>0${i+1}</div><strong>${title}</strong><p>${description}</p></div>`).join('')}</div></article>`;
}
function render() {
  const [name,title,description]=viewMeta[state.view];
  $('#breadcrumbCurrent').textContent=name; $('#pageTitle').textContent=title; $('#pageDescription').textContent=description;
  document.querySelectorAll('.nav-link').forEach(button=>{button.classList.toggle('active',button.dataset.view===state.view);button.setAttribute('aria-current',button.dataset.view===state.view?'page':'false');});
  const views={overview,claims:claimExplorer,network:diffusionLab,evidence:evidenceAudit,experiments};
  $('#viewContent').innerHTML=views[state.view]();
  const r=$('#rumorSlider'), f=$('#factSlider');
  if(r){r.addEventListener('input',(e)=>{state.rumor=Number(e.target.value);e.target.parentElement.querySelector('.control-title strong').textContent=`${state.rumor}%`;});r.addEventListener('change',render);}
  if(f){f.addEventListener('input',(e)=>{state.factCheck=Number(e.target.value);e.target.parentElement.querySelector('.control-title strong').textContent=`${state.factCheck}%`;});f.addEventListener('change',render);}
  $('#groundToggle')?.addEventListener('click',()=>{state.grounding=!state.grounding;render();});
  $('#exportMatrixButton')?.addEventListener('click',exportReport);
  $('#importReportButton')?.addEventListener('click',()=>$('#reportFile').click());
}
function changeView(view) {if(viewMeta[view]) {state.view=view;window.history.replaceState(null,'',`#${view}`);render();window.scrollTo({top:0,behavior:'smooth'});}}
function exportReport() {
  const response={warning:'SYNTHETIC UI DEMO — NOT A MEASURED LLM EXPERIMENT',generated_at:new Date().toISOString(),
    title:'ForesightAI dashboard illustration',case_id:claims[state.claimIndex].id,
    settings:{rumor_repetition_index:state.rumor,fact_checker_index:state.factCheck,evidence_first_mode:state.grounding},
    toy_metrics:values(),condition_labels:['evidence_only','rumor_pressure','evidence_first'],
    note:'Use the Python runner for actual model output, not these deterministic UI formulas.'};
  const blob=new Blob([JSON.stringify(response,null,2)],{type:'application/json'});
  const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='foresightai-synthetic-demo.json';a.click();URL.revokeObjectURL(url);
  toast('Synthetic demo configuration exported.');
}
let toastTimeout;
function toast(message){const node=$('#toast');node.textContent=message;node.classList.add('visible');clearTimeout(toastTimeout);toastTimeout=setTimeout(()=>node.classList.remove('visible'),3200);}
document.addEventListener('click',(event)=>{
  const button=event.target.closest('[data-view]');if(button){changeView(button.dataset.view);return;}
  const claim=event.target.closest('[data-claim]');if(claim){state.claimIndex=Number(claim.dataset.claim);render();return;}
  const agent=event.target.closest('[data-agent]');if(agent){state.selectedAgent=Number(agent.dataset.agent);render();}
});
document.addEventListener('keydown',(event)=>{
  if((event.key==='Enter'||event.key===' ')&&event.target.matches('[data-agent]')){event.preventDefault();state.selectedAgent=Number(event.target.dataset.agent);render();}
});
$('#exportButton').addEventListener('click',exportReport);
$('#reportFile').addEventListener('change',async (event)=>{
  const file=event.target.files?.[0];if(!file)return;
  try {
    const report=JSON.parse(await file.text());
    if(!report || !report.metadata || !report.metrics || !Array.isArray(report.rows) || typeof report.metadata.model!=='string') throw Error('Invalid ForesightAI result format');
    state.loadedReport=report;changeView('experiments');toast('Local experiment report imported.');
  } catch(error) {toast(`Could not import report: ${error.message}`);}
  event.target.value='';
});
$('#resetButton').addEventListener('click',()=>{Object.assign(state,{rumor:55,factCheck:40,grounding:true,claimIndex:0,selectedAgent:10});render();toast('Scenario controls reset.');});
window.addEventListener('hashchange',()=>{const next=location.hash.slice(1);if(viewMeta[next])changeView(next);});
if(viewMeta[location.hash.slice(1)])state.view=location.hash.slice(1);
render();
