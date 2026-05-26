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
      zoom: 3.5
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
          'fill-color': '#2563eb',
          'fill-opacity': 0.14
        }
      });

      map.addLayer({
        id: 'counties-outline',
        type: 'line',
        source: 'counties',
        paint: {
          'line-color': '#64748b',
          'line-width': 0.8
        }
      });

      map.addLayer({
        id: 'selected-county-outline',
        type: 'line',
        source: 'counties',
        filter: ['==', ['get', 'geoid'], ''],
        paint: {
          'line-color': '#111827',
          'line-width': 3
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
    <div class="panel-header">
      <h1>Migration</h1>
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

    {#if selectedCountyName}
      <div class="county-name">{selectedCountyName}</div>
    {:else}
      <div class="empty">Select a county</div>
    {/if}

    {#if loadingMigration}
      <div class="empty">Loading</div>
    {:else if migrationError}
      <div class="empty">{migrationError}</div>
    {:else if migrationSummary}
      <div class="stats">
        <div class="stat">
          <span>Moved in</span>
          <strong>{formatNumber(migrationSummary.moved_in)}</strong>
        </div>
        <div class="stat">
          <span>Moved out</span>
          <strong>{formatNumber(migrationSummary.moved_out)}</strong>
        </div>
        <div class="stat primary {migrationSummary.direction}">
          <span>Net migration</span>
          <strong>{formatSignedNumber(migrationSummary.net_migration)}</strong>
        </div>
      </div>

      <div class="source">
        ACS {migrationSummary.period} county migration flows
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
    grid-template-columns: minmax(0, 1fr) 320px;
    height: 100vh;
    background: #f8fafc;
    color: #111827;
    font-family:
      Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
      sans-serif;
  }

  .map {
    width: 100%;
    height: 100%;
  }

  .panel {
    padding: 18px;
    background: #ffffff;
    border-left: 1px solid #d1d5db;
  }

  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 18px;
  }

  h1 {
    margin: 0;
    font-size: 18px;
    line-height: 1.2;
  }

  select {
    min-width: 112px;
    height: 34px;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    background: #ffffff;
    color: #111827;
    font: inherit;
  }

  .county-name {
    margin-bottom: 18px;
    font-size: 15px;
    font-weight: 700;
    line-height: 1.3;
  }

  .stats {
    display: grid;
    gap: 10px;
  }

  .stat {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 16px;
    padding: 12px 0;
    border-bottom: 1px solid #e5e7eb;
  }

  .stat span {
    color: #475569;
    font-size: 13px;
  }

  .stat strong {
    font-size: 22px;
    line-height: 1;
  }

  .stat.primary strong {
    font-size: 26px;
  }

  .stat.primary.gained strong {
    color: #047857;
  }

  .stat.primary.lost strong {
    color: #b91c1c;
  }

  .empty {
    color: #64748b;
    font-size: 14px;
  }

  .source {
    margin-top: 18px;
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
    }
  }
</style>
