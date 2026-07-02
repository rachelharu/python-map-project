<script lang="ts">
  import { onMount } from 'svelte';
  import maplibregl from 'maplibre-gl';
  import 'maplibre-gl/dist/maplibre-gl.css';

  const API_BASE = import.meta.env.VITE_API_BASE_URL;

  let mapContainer: HTMLDivElement;
  let map: maplibregl.Map;

  let periods: string[] = [];
  let selectedPeriod = '';
  let selectedCountyGeoid = '';
  let selectedCountyName = '';
  let migrationSummary: any = null;
  let loadingMigration = false;
  let migrationError = '';

  function formatNumber(value: number | null | undefined) {
    if (value === null || value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US').format(value);
  }

  function formatSignedNumber(value: number | null | undefined) {
    if (value === null || value === undefined) return 'N/A';
    const formatted = formatNumber(Math.abs(value));
    if (value > 0) return `+${formatted}`;
    if (value < 0) return `-${formatted}`;
    return formatted;
  }

  function netLabel(value: number) {
    if (value > 0) return 'Net gain';
    if (value < 0) return 'Net loss';
    return 'No net change';
  }

  function netSummary(summary: any) {
    const net = summary.net_migration;
    const count = formatNumber(Math.abs(net));
    if (net > 0) return `${count} more people moved in than out.`;
    if (net < 0) return `${count} more people moved out than in.`;
    return 'The number of people moving in and out was equal.';
  }

  function inboundShare(summary: any) {
    const movedIn = summary.moved_in ?? 0;
    const movedOut = summary.moved_out ?? 0;
    const total = movedIn + movedOut;
    if (total <= 0) return 50;
    return Math.round((movedIn / total) * 100);
  }

  async function loadMigrationPeriods() {
    const res = await fetch(`${API_BASE}/metadata/migration-periods`);
    if (!res.ok) return;

    const data = await res.json();
    periods = data.periods ?? [];
    selectedPeriod = periods.at(-1) ?? '';
  }

  async function loadCountyMigration(geoid: string) {
    if (!geoid) return;

    loadingMigration = true;
    migrationError = '';
    migrationSummary = null;

    const url = new URL(`${API_BASE}/migration/counties/${geoid}`);
    if (selectedPeriod) {
      url.searchParams.set('period', selectedPeriod);
    }

    try {
      const res = await fetch(url.toString());
      if (!res.ok) {
        migrationError = 'No migration data for this county.';
        return;
      }

      migrationSummary = await res.json();
    } finally {
      loadingMigration = false;
    }
  }

  async function refreshCounties() {
    if (!map || !map.getSource('counties')) return;

    const b = map.getBounds();
    const url = new URL(`${API_BASE}/counties/in-bbox`);
    url.searchParams.set('west', String(b.getWest()));
    url.searchParams.set('south', String(b.getSouth()));
    url.searchParams.set('east', String(b.getEast()));
    url.searchParams.set('north', String(b.getNorth()));
    url.searchParams.set('limit', '2000');
    url.searchParams.set('simplify', '0.002');

    const res = await fetch(url.toString());
    const geojson = await res.json();
    const counties = map.getSource('counties') as maplibregl.GeoJSONSource;
    counties?.setData(geojson);
  }

  function updateSelectedCountyLayer() {
    if (!map || !map.getLayer('selected-county-outline')) return;
    map.setFilter('selected-county-outline', ['==', ['get', 'geoid'], selectedCountyGeoid]);
  }

  function selectCounty(feature: maplibregl.MapGeoJSONFeature) {
    const geoid = String(feature.properties?.geoid ?? '');
    if (!geoid) return;

    selectedCountyGeoid = geoid;
    selectedCountyName = String(feature.properties?.name ?? geoid);
    updateSelectedCountyLayer();
    loadCountyMigration(geoid);
  }

  onMount(() => {
    loadMigrationPeriods();

    map = new maplibregl.Map({
      container: mapContainer,
      style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
      center: [-98.5795, 39.8283],
      zoom: 4
    });

    map.on('load', () => {
      map.addSource('counties', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] }
      });

      map.addLayer({
        id: 'counties-fill',
        type: 'fill',
        source: 'counties',
        paint: {
          'fill-color': '#0f766e',
          'fill-opacity': 0.12
        }
      });

      map.addLayer({
        id: 'counties-outline',
        type: 'line',
        source: 'counties',
        paint: {
          'line-color': '#475569',
          'line-width': 0.65,
          'line-opacity': 0.55
        }
      });

      map.addLayer({
        id: 'selected-county-outline',
        type: 'line',
        source: 'counties',
        filter: ['==', ['get', 'geoid'], ''],
        paint: {
          'line-color': '#0f172a',
          'line-width': 3.2
        }
      });

      map.on('click', 'counties-fill', (event) => {
        const feature = event.features?.[0];
        if (feature) selectCounty(feature);
      });

      map.on('mouseenter', 'counties-fill', () => {
        map.getCanvas().style.cursor = 'pointer';
      });

      map.on('mouseleave', 'counties-fill', () => {
        map.getCanvas().style.cursor = '';
      });

      refreshCounties();
    });

    map.on('moveend', refreshCounties);
  });
</script>

<div class="layout">
  <div bind:this={mapContainer} class="map"></div>

  <aside class="panel">
    <div class="app-header">
      <div>
        <div class="eyebrow">Spatial Intel</div>
        <h1>County migration viewer</h1>
      </div>
    </div>

    <div class="control-row">
      <span>ACS period</span>
      <select
        bind:value={selectedPeriod}
        disabled={periods.length === 0}
        onchange={() => loadCountyMigration(selectedCountyGeoid)}
      >
        {#if periods.length === 0}
          <option>No data</option>
        {:else}
          {#each periods as period}
            <option value={period}>{period}</option>
          {/each}
        {/if}
      </select>
    </div>

    {#if loadingMigration}
      <div class="state-block">Loading migration data</div>
    {:else if migrationError}
      <div class="state-block">{migrationError}</div>
    {:else if migrationSummary}
      <div class="county-kicker">Selected county</div>
      <div class="county-name">{selectedCountyName}</div>

      <div class="net-card {migrationSummary.direction}">
        <span>{netLabel(migrationSummary.net_migration)}</span>
        <strong>{formatSignedNumber(migrationSummary.net_migration)}</strong>
        <p>{netSummary(migrationSummary)}</p>
      </div>

      <div class="stats">
        <div class="stat">
          <span>Migration gain</span>
          <strong>{formatNumber(migrationSummary.moved_in)}</strong>
        </div>
        <div class="stat">
          <span>Migration loss</span>
          <strong>{formatNumber(migrationSummary.moved_out)}</strong>
        </div>
      </div>

      <div class="balance">
        <div class="balance-labels">
          <span>In vs. out share</span>
          <strong>{inboundShare(migrationSummary)}%</strong>
        </div>
        <div class="balance-track">
          <div class="balance-fill" style={`width: ${inboundShare(migrationSummary)}%`}></div>
        </div>
      </div>

      <div class="source">
        ACS {migrationSummary.period} county migration flows
      </div>
    {:else}
      <div class="state-block">
        <strong>Select a county</strong>
        <span>Click a county on the map to inspect migration gain, migration loss, and net movement.</span>
      </div>
    {/if}
  </aside>
</div>

<style>
  :global(body) {
    margin: 0;
  }

  .layout {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 360px;
    height: 100vh;
    background: #e5e7eb;
    color: #0f172a;
    font-family:
      Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
      sans-serif;
  }

  .map {
    width: 100%;
    height: 100%;
  }

  .panel {
    display: flex;
    flex-direction: column;
    gap: 18px;
    padding: 22px;
    background: #f8fafc;
    border-left: 1px solid #cbd5e1;
    box-shadow: -12px 0 30px rgb(15 23 42 / 0.08);
  }

  .app-header {
    padding-bottom: 16px;
    border-bottom: 1px solid #dbe3ec;
  }

  .eyebrow {
    margin-bottom: 6px;
    color: #0f766e;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .control-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 10px 0 16px;
    border-bottom: 1px solid #dbe3ec;
  }

  .control-row span {
    color: #475569;
    font-size: 12px;
    font-weight: 700;
  }

  h1 {
    margin: 0;
    font-size: 22px;
    line-height: 1.15;
  }

  select {
    min-width: 124px;
    height: 36px;
    padding: 0 8px;
    border: 1px solid #b6c2cf;
    border-radius: 6px;
    background: #ffffff;
    color: #0f172a;
    font: inherit;
    font-size: 13px;
  }

  .county-kicker {
    margin-bottom: -10px;
    color: #64748b;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .county-name {
    margin-top: -4px;
    font-size: 21px;
    font-weight: 800;
    line-height: 1.2;
  }

  .stats {
    display: grid;
    gap: 0;
    border-top: 1px solid #dbe3ec;
  }

  .net-card {
    display: grid;
    gap: 8px;
    padding: 16px;
    border: 1px solid #dbe3ec;
    border-radius: 8px;
    background: #ffffff;
  }

  .net-card span {
    color: #475569;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .net-card strong {
    color: #1e293b;
    font-size: 38px;
    line-height: 1;
  }

  .net-card p {
    margin: 0;
    color: #475569;
    font-size: 13px;
    line-height: 1.35;
  }

  .net-card.gained strong {
    color: #047857;
  }

  .net-card.lost strong {
    color: #b91c1c;
  }

  .stat {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 16px;
    padding: 14px 0;
    border-bottom: 1px solid #dbe3ec;
  }

  .stat span {
    color: #475569;
    font-size: 13px;
  }

  .stat strong {
    color: #0f172a;
    font-size: 24px;
    line-height: 1;
  }

  .state-block {
    display: grid;
    gap: 6px;
    padding: 16px;
    border: 1px dashed #b6c2cf;
    border-radius: 8px;
    background: #ffffff;
    font-size: 14px;
    line-height: 1.45;
    color: #64748b;
  }

  .state-block strong {
    color: #0f172a;
    font-size: 15px;
  }

  .balance {
    display: grid;
    gap: 8px;
    padding-top: 2px;
  }

  .balance-labels {
    display: flex;
    justify-content: space-between;
    color: #475569;
    font-size: 12px;
    font-weight: 700;
  }

  .balance-labels strong {
    color: #0f172a;
  }

  .balance-track {
    height: 10px;
    overflow: hidden;
    border-radius: 999px;
    background: #e2e8f0;
  }

  .balance-fill {
    height: 100%;
    border-radius: inherit;
    background: #0f766e;
  }

  .source {
    color: #64748b;
    font-size: 12px;
    line-height: 1.4;
  }

  @media (max-width: 760px) {
    .layout {
      grid-template-columns: 1fr;
      grid-template-rows: minmax(0, 1fr) auto;
    }

    .panel {
      border-top: 1px solid #d1d5db;
      border-left: 0;
      box-shadow: 0 -12px 24px rgb(15 23 42 / 0.08);
    }
  }
</style>
