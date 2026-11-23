import json

with open("pricing_manifest.json", "r", encoding="utf-8") as f:
    manifest = json.load(f)

# Compact JSON representation for embedding
manifest_js = json.dumps(manifest, separators=(',', ':'))

with open("prototype_calculator.html", "r", encoding="utf-8") as f:
    html = f.read()

# Find script tag
script_idx = html.find("<script>")
if script_idx == -1:
    print("Could not find <script>")
    exit(1)

# Everything before <script> remains unchanged
pre_script = html[:script_idx]

new_script = f"""<script>
    /* ── Tab Switching ── */
    function showTab(id) {{
      document.querySelectorAll('.tab-panel').forEach(function(p) {{ p.classList.remove('active'); }});
      document.querySelectorAll('.tab-btn').forEach(function(b) {{ b.classList.remove('active'); }});
      document.getElementById('tab-' + id).classList.add('active');
      var btns = document.querySelectorAll('.tab-btn');
      var map = {{ calc: 0, porter: 1, game: 2, market: 3 }};
      btns[map[id]].classList.add('active');
    }}

    /* ── Single Source of Truth Manifest & Dynamic Loader ── */
    var FALLBACK_MANIFEST = {manifest_js};
    var MANIFEST = FALLBACK_MANIFEST;
    var USD_INR = MANIFEST.meta.usd_inr;
    var WORKLOADS = MANIFEST.workloads;

    var DATA = {{
      "AWS": {{
        sku: MANIFEST.providers.AWS.sku,
        od: MANIFEST.providers.AWS.od,
        ri: MANIFEST.providers.AWS.ri,
        storage_rate: MANIFEST.providers.AWS.storage.rate,
        egress_tiers: MANIFEST.providers.AWS.egress_tiers,
        free_egress: MANIFEST.providers.AWS.free_egress
      }},
      "Azure": {{
        sku: MANIFEST.providers.Azure.sku,
        od: MANIFEST.providers.Azure.od,
        ri: MANIFEST.providers.Azure.ri,
        storage_tiers: MANIFEST.providers.Azure.storage.tiers,
        egress_tiers: MANIFEST.providers.Azure.egress_tiers,
        free_egress: MANIFEST.providers.Azure.free_egress
      }},
      "GCP": {{
        sku: MANIFEST.providers.GCP.sku,
        od: MANIFEST.providers.GCP.od,
        ri: MANIFEST.providers.GCP.ri,
        storage_rate: MANIFEST.providers.GCP.storage.rate,
        egress_tiers: MANIFEST.providers.GCP.egress_tiers,
        free_egress: MANIFEST.providers.GCP.free_egress
      }}
    }};

    var currentWorkload = "A_Startup";
    var currentInstanceTier = "A_Startup";
    var currentStorage = 100;
    var currentEgress = 100;

    function gbToGiB(gb) {{
      return (gb * 1e9) / Math.pow(2, 30);
    }}

    function calcAzureStorage(gb) {{
      var gib = gbToGiB(gb);
      var tiers = DATA.Azure.storage_tiers;
      for (var i = 0; i < tiers.length; i++) {{
        if (gib <= tiers[i].gib) {{
          return {{ tier: tiers[i].tier, gib: tiers[i].gib, cost: tiers[i].price_usd }};
        }}
      }}
      var last = tiers[tiers.length - 1];
      return {{ tier: last.tier, gib: last.gib, cost: last.price_usd }};
    }}

    function calcEgress(tiers, gb, freeGb) {{
      var billable = Math.max(0, gb - freeGb);
      var cost = 0;
      for (var i = 0; i < tiers.length; i++) {{
        if (billable <= tiers[i][0]) break;
        cost += (Math.min(billable, tiers[i][1]) - tiers[i][0]) * tiers[i][2];
      }}
      return cost;
    }}

    function calcSupport(prov, usage, tier) {{
      if (tier === "basic") return 0.0;
      if (tier === "developer") {{
        if (prov === "AWS") return Math.max(29.0, 0.03 * usage);
        if (prov === "Azure") return 29.0;
        if (prov === "GCP") return Math.max(29.0, 0.03 * usage);
      }} else if (tier === "business") {{
        if (prov === "AWS") return Math.max(100.0, 0.10 * Math.min(usage, 10000.0));
        if (prov === "Azure") return 100.0;
        if (prov === "GCP") return 500.0 + 0.03 * usage;
      }}
      return 0.0;
    }}

    function updateSliderLabels() {{
      var stStr = (currentStorage >= 1000) ? (currentStorage / 1000).toFixed(1) + ' TB (' + currentStorage.toLocaleString() + ' GB)' : currentStorage.toLocaleString() + ' GB';
      var egStr = (currentEgress >= 1000) ? (currentEgress / 1000).toFixed(1) + ' TB (' + currentEgress.toLocaleString() + ' GB)' : currentEgress.toLocaleString() + ' GB';
      var elSt = document.getElementById('lbl-storage');
      var elEg = document.getElementById('lbl-egress');
      if (elSt) elSt.innerText = stStr;
      if (elEg) elEg.innerText = egStr;
    }}

    function updateWorkloadSpec() {{
      var sp = WORKLOADS[currentInstanceTier];
      var stStr = (currentStorage >= 1000) ? (currentStorage / 1000).toFixed(1) + ' TB' : currentStorage.toLocaleString() + ' GB';
      var egStr = (currentEgress >= 1000) ? (currentEgress / 1000).toFixed(1) + ' TB' : currentEgress.toLocaleString() + ' GB';
      var el = document.getElementById('workload-spec');
      if (el) {{
        el.innerText = sp.vcpu + ' vCPU · ' + sp.ram_gb + ' GB RAM · ' + stStr + ' Storage · ' + egStr + ' Egress';
      }}
    }}

    function setWorkload(wl) {{
      currentWorkload = wl;
      document.querySelectorAll('.seg button').forEach(function(b) {{
        if (b.id && (b.id.startsWith('btn-A') || b.id.startsWith('btn-B') || b.id.startsWith('btn-C') || b.id === 'btn-Custom')) {{
          b.classList.remove('on');
        }}
      }});
      var btn = document.getElementById('btn-' + wl);
      if (btn) btn.classList.add('on');

      if (wl !== 'Custom') {{
        currentInstanceTier = wl;
        currentStorage = WORKLOADS[wl].storage_gb;
        currentEgress = WORKLOADS[wl].egress_gb;

        var sSt = document.getElementById('slider-storage');
        var sEg = document.getElementById('slider-egress');
        if (sSt) sSt.value = currentStorage;
        if (sEg) sEg.value = currentEgress;

        document.querySelectorAll('#seg-instance button').forEach(function(b) {{ b.classList.remove('on'); }});
        var mapInst = {{"A_Startup":"btn-inst-A", "B_Midsize":"btn-inst-B", "C_DataHeavy":"btn-inst-C"}};
        var instBtn = document.getElementById(mapInst[wl]);
        if (instBtn) instBtn.classList.add('on');
      }}

      updateSliderLabels();
      updateWorkloadSpec();
      recalculate();
    }}

    function onSliderChange() {{
      var sSt = document.getElementById('slider-storage');
      var sEg = document.getElementById('slider-egress');
      if (sSt) currentStorage = parseInt(sSt.value);
      if (sEg) currentEgress = parseInt(sEg.value);

      currentWorkload = 'Custom';
      document.querySelectorAll('.seg button').forEach(function(b) {{
        if (b.id && (b.id.startsWith('btn-A') || b.id.startsWith('btn-B') || b.id.startsWith('btn-C') || b.id === 'btn-Custom')) {{
          b.classList.remove('on');
        }}
      }});
      var btnC = document.getElementById('btn-Custom');
      if (btnC) btnC.classList.add('on');

      updateSliderLabels();
      updateWorkloadSpec();
      recalculate();
    }}

    function setInstanceTier(tier) {{
      currentInstanceTier = tier;
      document.querySelectorAll('#seg-instance button').forEach(function(b) {{ b.classList.remove('on'); }});
      var mapInst = {{"A_Startup":"btn-inst-A", "B_Midsize":"btn-inst-B", "C_DataHeavy":"btn-inst-C"}};
      var instBtn = document.getElementById(mapInst[tier]);
      if (instBtn) instBtn.classList.add('on');

      var isExactPreset = (WORKLOADS[tier].storage_gb === currentStorage && WORKLOADS[tier].egress_gb === currentEgress);
      if (isExactPreset) {{
        currentWorkload = tier;
        document.querySelectorAll('.seg button').forEach(function(b) {{
          if (b.id && (b.id.startsWith('btn-A') || b.id.startsWith('btn-B') || b.id.startsWith('btn-C') || b.id === 'btn-Custom')) {{
            b.classList.remove('on');
          }}
        }});
        var btn = document.getElementById('btn-' + tier);
        if (btn) btn.classList.add('on');
      }} else {{
        currentWorkload = 'Custom';
        document.querySelectorAll('.seg button').forEach(function(b) {{
          if (b.id && (b.id.startsWith('btn-A') || b.id.startsWith('btn-B') || b.id.startsWith('btn-C') || b.id === 'btn-Custom')) {{
            b.classList.remove('on');
          }}
        }});
        var btnC = document.getElementById('btn-Custom');
        if (btnC) btnC.classList.add('on');
      }}

      updateWorkloadSpec();
      recalculate();
    }}

    function fmt(val, inr) {{
      if (inr) return '₹' + Math.round(val * USD_INR).toLocaleString('en-IN');
      return '$' + val.toFixed(2);
    }}

    function recalculate() {{
      var isINR = document.querySelector("input[name='currency']:checked").value === 'INR';
      var supportTier = document.getElementById('support-tier').value;
      var provs = ['AWS', 'Azure', 'GCP'];
      var tOd = {{}}, tRi = {{}}, bComp = {{}}, bExt = {{}};

      provs.forEach(function(p) {{
        var d = DATA[p], k = p.toLowerCase();
        var skuEl = document.getElementById(k + '-sku');
        if (skuEl) skuEl.innerText = d.sku[currentInstanceTier];

        var od = d.od[currentInstanceTier], ri = d.ri[currentInstanceTier];
        var stor = 0;
        if (p === 'Azure') {{
          var azDisk = calcAzureStorage(currentStorage);
          stor = azDisk.cost;
          var diskLabel = document.getElementById('azure-disk-label');
          if (diskLabel) diskLabel.innerText = azDisk.tier + ' (' + azDisk.gib + ' GiB)';
        }} else {{
          stor = d.storage_rate * currentStorage;
        }}

        var egr = calcEgress(d.egress_tiers, currentEgress, d.free_egress);
        var exitC = calcEgress(d.egress_tiers, currentStorage, d.free_egress);
        
        var usageOd = od + stor + egr;
        var usageRi = ri + stor + egr;
        var sup = calcSupport(p, usageOd, supportTier);
        
        var totalOd = usageOd + sup;
        var totalRi = usageRi + sup;
        var ext = stor + egr + sup;
        var hidd = (ext / totalOd) * 100;

        tOd[p] = totalOd; tRi[p] = totalRi; bComp[p] = od; bExt[p] = ext;

        var odEl = document.getElementById(k + '-od'); if (odEl) odEl.innerText = fmt(od, isINR);
        var riEl = document.getElementById(k + '-ri'); if (riEl) riEl.innerText = fmt(ri, isINR);
        var storEl = document.getElementById(k + '-storage'); if (storEl) storEl.innerText = fmt(stor, isINR);
        var egrEl = document.getElementById(k + '-egress'); if (egrEl) egrEl.innerText = fmt(egr, isINR);
        var supEl = document.getElementById(k + '-support'); if (supEl) supEl.innerText = fmt(sup, isINR);
        var totOdEl = document.getElementById(k + '-total-od'); if (totOdEl) totOdEl.innerText = fmt(totalOd, isINR);
        var totRiEl = document.getElementById(k + '-total-ri'); if (totRiEl) totRiEl.innerText = fmt(totalRi, isINR);
        var hidEl = document.getElementById(k + '-hidden'); if (hidEl) hidEl.innerText = hidd.toFixed(1) + '%';
        var exitEl = document.getElementById(k + '-exit'); if (exitEl) exitEl.innerText = fmt(exitC, isINR);
      }});

      // Live Winner Logic
      var minOd = Math.min(tOd.AWS, tOd.Azure, tOd.GCP);
      var winOdProv = Object.keys(tOd).find(function(k) {{ return tOd[k] === minOd; }});

      var winTitle = document.getElementById('winner-title');
      var winSub = document.getElementById('winner-sub');
      if (winTitle && winSub) {{
        if (winOdProv === 'AWS') {{
          var savAzure = tOd.Azure - tOd.AWS;
          var savGcp = tOd.GCP - tOd.AWS;
          winTitle.innerText = "AWS is cheapest overall for this configuration (" + fmt(tOd.AWS, isINR) + "/mo)";
          winSub.innerText = "Saves " + fmt(savAzure, isINR) + " vs. Azure · " + fmt(savGcp, isINR) + " vs. GCP · Lowest storage & 100GB free egress";
        }} else if (winOdProv === 'Azure') {{
          var savAws = tOd.AWS - tOd.Azure;
          winTitle.innerText = "Azure is cheapest overall for this configuration (" + fmt(tOd.Azure, isINR) + "/mo)";
          winSub.innerText = "Saves " + fmt(savAws, isINR) + " vs. AWS · Lowest 1-Year reservation compute rate";
        }} else {{
          winTitle.innerText = "Google Cloud is cheapest overall (" + fmt(tOd.GCP, isINR) + "/mo)";
          winSub.innerText = "Zero cloud exit switching penalty · 200GB free egress";
        }}
      }}

      renderBars(isINR, tOd, tRi, bComp, bExt);
    }}

    function renderBars(isINR, tOd, tRi, bComp, bExt) {{
      var currentMax = Math.max(tOd.AWS, tOd.Azure, tOd.GCP);
      var ceiling = Math.max(160, currentMax * 1.18);

      var h1 = '<div class="vchart-area">' +
        '<div class="vchart-grid-line l75"></div>' +
        '<div class="vchart-grid-line l50"></div>' +
        '<div class="vchart-grid-line l25"></div>' +
        '<span class="vchart-grid-label" style="top: 25%;">' + fmt(ceiling * 0.75, isINR) + '</span>' +
        '<span class="vchart-grid-label" style="top: 50%;">' + fmt(ceiling * 0.50, isINR) + '</span>' +
        '<span class="vchart-grid-label" style="top: 75%;">' + fmt(ceiling * 0.25, isINR) + '</span>';

      var h2 = '<div class="vchart-area" style="height: 155px;">' +
        '<div class="vchart-grid-line l75"></div>' +
        '<div class="vchart-grid-line l50"></div>' +
        '<div class="vchart-grid-line l25"></div>' +
        '<span class="vchart-grid-label" style="top: 25%;">75%</span>' +
        '<span class="vchart-grid-label" style="top: 50%;">50%</span>' +
        '<span class="vchart-grid-label" style="top: 75%;">25%</span>';

      ['AWS', 'Azure', 'GCP'].forEach(function(p) {{
        var hOdPx = Math.max(8, (tOd[p] / ceiling) * 125);
        var hRiPx = Math.max(8, (tRi[p] / ceiling) * 125);

        h1 += '<div class="vbar-group">' +
          '<div class="vbar-cols">' +
            '<div class="vbar-col-box">' +
              '<div class="vbar-val-float" title="' + p + ' On-Demand: ' + fmt(tOd[p], isINR) + '">' + fmt(tOd[p], isINR) + '</div>' +
              '<div class="vbar-pill fill-blue" style="height:' + hOdPx.toFixed(1) + 'px;" title="' + p + ' On-Demand: ' + fmt(tOd[p], isINR) + '"></div>' +
            '</div>' +
            '<div class="vbar-col-box">' +
              '<div class="vbar-val-float green" title="' + p + ' 1-Yr Commitment: ' + fmt(tRi[p], isINR) + '">' + fmt(tRi[p], isINR) + '</div>' +
              '<div class="vbar-pill fill-green" style="height:' + hRiPx.toFixed(1) + 'px;" title="' + p + ' 1-Yr Commitment: ' + fmt(tRi[p], isINR) + '"></div>' +
            '</div>' +
          '</div>' +
          '<div class="vbar-label">' + p + '</div>' +
        '</div>';

        var t = tOd[p], pc = (bComp[p] / t) * 100, pe = (bExt[p] / t) * 100;
        h2 += '<div class="vbar-group">' +
          '<div class="vbar-cols">' +
            '<div class="vbar-col-box" style="max-width: 56px;">' +
              '<div class="vbar-val-float orange" title="Hidden Extras: ' + pe.toFixed(1) + '%">' + pe.toFixed(0) + '% ext</div>' +
              '<div class="vbar-stacked-col" title="' + p + ': Compute ' + pc.toFixed(1) + '% | Hidden Extras ' + pe.toFixed(1) + '%">' +
                '<div class="vbar-stack-seg fill-indigo" style="height:' + pc.toFixed(1) + '%;"></div>' +
                '<div class="vbar-stack-seg fill-orange" style="height:' + pe.toFixed(1) + '%;"></div>' +
              '</div>' +
            '</div>' +
          '</div>' +
          '<div class="vbar-label">' + p + ' <span style="font-size:11px; font-weight:500; color:#86868b;">(' + pc.toFixed(0) + '% core)</span></div>' +
        '</div>';
      }});

      h1 += '</div>';
      h2 += '</div>';

      var cb = document.getElementById('cost-bars');
      var bb = document.getElementById('breakdown-bars');
      if (cb) cb.innerHTML = h1;
      if (bb) bb.innerHTML = h2;
    }}

    // Dynamic Manifest Loader
    async function loadPricingManifest() {{
      try {{
        var res = await fetch('pricing_manifest.json');
        if (res.ok) {{
          var m = await res.json();
          MANIFEST = m;
          USD_INR = m.meta.usd_inr;
          WORKLOADS = m.workloads;
          DATA.AWS.sku = m.providers.AWS.sku;
          DATA.AWS.od = m.providers.AWS.od;
          DATA.AWS.ri = m.providers.AWS.ri;
          DATA.AWS.storage_rate = m.providers.AWS.storage.rate;
          DATA.AWS.egress_tiers = m.providers.AWS.egress_tiers;
          DATA.AWS.free_egress = m.providers.AWS.free_egress;
          DATA.Azure.sku = m.providers.Azure.sku;
          DATA.Azure.od = m.providers.Azure.od;
          DATA.Azure.ri = m.providers.Azure.ri;
          DATA.Azure.storage_tiers = m.providers.Azure.storage.tiers;
          DATA.Azure.egress_tiers = m.providers.Azure.egress_tiers;
          DATA.Azure.free_egress = m.providers.Azure.free_egress;
          DATA.GCP.sku = m.providers.GCP.sku;
          DATA.GCP.od = m.providers.GCP.od;
          DATA.GCP.ri = m.providers.GCP.ri;
          DATA.GCP.storage_rate = m.providers.GCP.storage.rate;
          DATA.GCP.egress_tiers = m.providers.GCP.egress_tiers;
          DATA.GCP.free_egress = m.providers.GCP.free_egress;
          console.log("pricing_manifest.json loaded dynamically from server.");
        }}
      }} catch (err) {{
        console.warn("Could not fetch pricing_manifest.json over network (using embedded fallback):", err);
      }}
      updateSliderLabels();
      updateWorkloadSpec();
      recalculate();
    }}

    window.onload = function() {{
      loadPricingManifest();
    }};
  </script>
</body>
</html>
"""

final_html = pre_script + new_script
with open("prototype_calculator.html", "w", encoding="utf-8") as f:
    f.write(final_html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print("Updated prototype_calculator.html and index.html successfully!")
