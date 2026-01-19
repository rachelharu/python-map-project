<script lang="ts">
  import { onMount } from 'svelte';
  import maplibregl from 'maplibre-gl';
  import 'maplibre-gl/dist/maplibre-gl.css';

  const API_BASE = import.meta.env.VITE_API_BASE_URL;

  let mapContainer: HTMLDivElement;
  let map: maplibregl.Map;

  let summary: any = null;

  function getBBox() {
    const b = map.getBounds();
    return {
      west: b.getWest(),
      south: b.getSouth(),
      east: b.getEast(),
      north: b.getNorth()
    };
  }

  async function refreshData() {
    if (!map) return;

    const bbox = getBBox();

    const pointsRes = await fetch(
      `${API_BASE}/events/in-bbox-time?` +
        new URLSearchParams({
          west: String(bbox.west),
          south: String(bbox.south),
          east: String(bbox.east),
          north: String(bbox.north),
          start: '2000-01-01T00:00:00Z',
          end: '2100-01-01T00:00:00Z',
          limit: '500'
        })
    );
    const points = await pointsRes.json();

    const summaryRes = await fetch(
      `${API_BASE}/events/changes-in-bbox?` +
        new URLSearchParams({
          west: String(bbox.west),
          south: String(bbox.south),
          east: String(bbox.east),
          north: String(bbox.north),
          window_minutes: '1440'
        })
    );
    summary = await summaryRes.json();

    if (map.getSource('events')) {
      (map.getSource('events') as maplibregl.GeoJSONSource).setData(points);
    }
  }

// dark/light mode will eventually be toggled 
// style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json'
  onMount(() => {
    map = new maplibregl.Map({
      container: mapContainer,
      style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
      center: [-118.2437, 34.0522],
      zoom: 10
    });

    map.on('load', () => {
      map.addSource('events', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: []
        }
      });

      map.addLayer({
        id: 'events-layer',
        type: 'circle',
        source: 'events',
        paint: {
          'circle-radius': 6,
          'circle-color': '#7dd3fc',
          'circle-stroke-width': 1,
          'circle-stroke-color': '#000'
        }
      });

      refreshData();
    });

    map.on('moveend', refreshData);
  });
</script>

<div class="layout">
  <div bind:this={mapContainer} class="map"></div>

  <div class="panel">
    <h2>Activity</h2>

    {#if summary}
      <div class="stat">
        <span>Current</span>
        <strong>{summary.current.count}</strong>
      </div>

      <div class="stat">
        <span>Previous</span>
        <strong>{summary.previous.count}</strong>
      </div>

      <div class="stat">
        <span>Delta</span>
        <strong>{summary.delta}</strong>
      </div>

      <div class="trend {summary.trend}">
        {summary.trend}
      </div>
    {:else}
      <p>Loading…</p>
    {/if}
  </div>
</div>

<style>
  .layout {
    display: grid;
    grid-template-columns: 1fr 280px;
    height: 100vh;
    background: #0f0f0f;
    color: #eaeaea;
  }

  .map {
    width: 100%;
    height: 100%;
  }

  .panel {
    padding: 1rem;
    background: #181818;
    border-left: 1px solid #222;
  }

  .stat {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.75rem;
  }

  .trend {
    margin-top: 1rem;
    padding: 0.5rem;
    text-align: center;
    border-radius: 4px;
    text-transform: uppercase;
    font-weight: bold;
  }

  .trend.new {
    background: #14532d;
    color: #86efac;
  }

  .trend.up {
    background: #1e3a8a;
    color: #93c5fd;
  }

  .trend.down {
    background: #7f1d1d;
    color: #fca5a5;
  }

  .trend.flat {
    background: #262626;
  }
</style>
