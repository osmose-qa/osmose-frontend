import { SourceSpecification } from 'maplibre-gl'

function tileSource(url, options?): SourceSpecification {
  return {
    type: 'raster',
    tiles: [url + (options?.layer ? '?layer=' + options.layer : '')],
    tileSize: 256,
    attribution: options?.attribution,
    minzoom: 1,
    maxzoom: options?.maxzoom || 20,
  }
}

const osmAttribution =
  '&copy <a href="https://openstreetmap.org/copyright">OpenStreetMap</a> contributors'
export const mapBases: Record<string, SourceSpecification> = {
  // OpenStreetMap
  carto: tileSource('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: osmAttribution,
    maxzoom: 19,
  }),
  CyclOSM: tileSource(
    'https://a.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png',
    {
      attribution: osmAttribution,
      maxzoom: 19,
    }
  ),
  'ÖPNV Karte': tileSource('http://tile.memomaps.de/tilegen/{z}/{x}/{y}.png', {
    maxzoom: 17,
  }),
  'White background': tileSource('https://tile.openstreetmap.org/3/4/7.png'),
  'carto-de': tileSource('https://tile.openstreetmap.de/{z}/{x}/{y}.png', {
    attribution: osmAttribution,
    maxzoom: 19,
  }),
  'carto-fr': tileSource(
    'https://a.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png',
    {
      attribution: osmAttribution,
      maxzoom: 20,
    }
  ),
  HOT: tileSource('https://tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
    attribution: osmAttribution,
    maxzoom: 20,
  }),
  // Bing: tileSource(
  //   'https://ecn.t2.tiles.virtualearth.net/tiles/{quadkey}.jpeg?g=14226', {
  //     maxzoom: 18,
  // }),
  'MapBox Satellite': tileSource(
    'https://a.tiles.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.jpg?access_token=pk.eyJ1IjoiZnJvZHJpZ28iLCJhIjoiY2tza2x2YWQxMGE2djJvcG51emw4a3lzdCJ9.0Uy0TXwxjwFaMwD9phimPQ',
    {
      maxzoom: 18,
    }
  ),
  // OpenGeoFiction
  // 'Standard': tileSource('http://opengeofiction.net/osm_tiles/{z}/{x}/{y}.png', {attribution: osmAttribution}),
  // 'TopoMap': tileSource('http://opengeofiction.net/tiles-topo/{z}/{x}/{y}.png', {attribution: osmAttribution}),
  // 'histor': tileSource('http://opengeofiction.net/tiles-histor/{z}/{x}/{y}.png', {attribution: osmAttribution}),
  // 'Roantra': tileSource('http://opengeofiction.net/planet/Roantra/{z}/{x}/{y}.png', {attribution: osmAttribution}),
}

const urlOsmFr = (layer) =>
  `https://a.layers.openstreetmap.fr/${layer}/{z}/{x}/{y}.png`
const optionsOsmFr = {
  attribution: '',
  maxzoom: 19,
}
const mapOverlaySource = {
  'No name': tileSource(urlOsmFr('noname'), optionsOsmFr),
  'No Oneway': tileSource(urlOsmFr('nooneway'), optionsOsmFr),
  'No Ref on way': tileSource(urlOsmFr('noref'), optionsOsmFr),
  'Fixme tags': tileSource(urlOsmFr('fixme'), optionsOsmFr),
  'admin_level=4': tileSource(urlOsmFr('admin4'), optionsOsmFr),
  'admin_level=5': tileSource(urlOsmFr('admin5'), optionsOsmFr),
  'admin_level=6': tileSource(urlOsmFr('admin6'), optionsOsmFr),
  'admin_level=7': tileSource(urlOsmFr('admin7'), optionsOsmFr),
  'admin_level=8': tileSource(urlOsmFr('admin8'), optionsOsmFr),
  'admin_level=10': tileSource(urlOsmFr('admin10'), optionsOsmFr),
  'boundary=local_authority': tileSource(
    urlOsmFr('boundary_local_authority'),
    optionsOsmFr
  ),
  'boundary=political': tileSource(
    urlOsmFr('boundary_political'),
    optionsOsmFr
  ),
  'boundary=election': tileSource(urlOsmFr('boundary_election'), optionsOsmFr),
}

export const mapOverlay = {
  ...Object.fromEntries(Object.keys(mapOverlaySource).map((k) => [k, k])),
  mapillary: 'Mapillary',
  panoramax: 'Panoramax',
  markers: 'Osmose Issues',
  heatmap: 'Osmose Issues Heatmap',
}

export const glStyle = {
  version: 8,
  sources: {
    background: {
      type: 'raster',
      tiles: mapBases['carto'].tiles,
      tileSize: 256,
      attribution: mapBases['carto'].attribution,
      minzoom: mapBases['carto'].minzoom,
      maxzoom: mapBases['carto'].maxzoom,
    },
    osm: {
      type: 'geojson',
      data: {
        type: 'FeatureCollection',
        features: [],
      },
    },
    mapillary: {
      type: 'vector',
      tiles: [
        'https://tiles.mapillary.com/maps/vtp/mly1/2/{z}/{x}/{y}?access_token=MLY|4223665974375089|d62822dd792b6a823d0794ef26450398',
      ],
      maxzoom: 14,
    },
    panoramax: {
      type: 'vector',
      tiles: ['https://api.panoramax.xyz/api/map/{z}/{x}/{y}.mvt'],
      maxzoom: 14,
    },
    markers: {
      type: 'vector',
      tiles: [API_URL + `/api/0.3/issues/{z}/{x}/{y}.mvt`],
      maxzoom: 18,
    },
    heatmap: {
      type: 'vector',
      tiles: [API_URL + `/api/0.3/issues/{z}/{x}/{y}.heat.mvt`],
      maxzoom: 18,
    },
    ...Object.entries(mapOverlaySource)
      .map(([id, source]) => ({ [id]: source }))
      .reduce((merged, current) => ({ ...merged, ...current }), {}),
  },
  sprite: API_URL + '/assets/marker-gl-sprite',
  layers: [
    {
      id: 'background-color',
      type: 'background',
      paint: {
        'background-color': '#f2efe9',
      },
    },
    {
      id: 'background',
      type: 'raster',
      source: 'background',
    },
    ...Object.keys(mapOverlaySource).map((id) => ({
      id: id,
      name: id,
      type: 'raster',
      source: id,
      layout: { visibility: 'none' },
    })),
    {
      id: 'osm-point',
      type: 'circle',
      source: 'osm',
      filter: ['==', '$type', 'Point'],
      paint: {
        'circle-stroke-width': 3,
        'circle-opacity': 0.3,
        'circle-radius': 10,
        'circle-color': [
          'match',
          ['%', ['get', 'index'], 3],
          0,
          '#ff3333',
          1,
          '#59b300',
          2,
          '#3388ff',
          '#000',
        ],
        'circle-stroke-color': [
          'match',
          ['%', ['get', 'index'], 3],
          0,
          '#ff3333',
          1,
          '#59b300',
          2,
          '#3388ff',
          '#000',
        ],
      },
    },
    {
      id: 'osm-line',
      type: 'line',
      source: 'osm',
      filter: ['==', '$type', 'LineString'],
      paint: {
        'line-width': 5,
        'line-color': [
          'match',
          ['%', ['get', 'index'], 3],
          0,
          '#ff3333',
          1,
          '#59b300',
          2,
          '#3388ff',
          '#000',
        ],
      },
      layout: {
        'line-cap': 'round',
        'line-join': 'round',
      },
    },
    {
      id: 'osm-fill',
      type: 'fill',
      source: 'osm',
      filter: ['==', '$type', 'Polygon'],
      paint: {
        'fill-opacity': 0.3,
        'fill-color': [
          'match',
          ['%', ['get', 'index'], 3],
          0,
          '#ff3333',
          1,
          '#59b300',
          2,
          '#3388ff',
          '#000',
        ],
      },
    },
    {
      id: 'osm-fill-strock',
      type: 'line',
      source: 'osm',
      filter: ['==', '$type', 'Polygon'],
      paint: {
        'line-width': 5,
        'line-color': [
          'match',
          ['%', ['get', 'index'], 3],
          0,
          '#ff3333',
          1,
          '#59b300',
          2,
          '#3388ff',
          '#000',
        ],
      },
      layout: {
        'line-cap': 'round',
        'line-join': 'round',
      },
    },
    {
      id: 'mapillary-overview',
      type: 'circle',
      source: 'mapillary',
      'source-layer': 'overview',
      paint: {
        'circle-color': 'rgba(71, 218, 98, 1)',
      },
      layout: { visibility: 'none' },
    },
    {
      id: 'mapillary-sequence',
      type: 'line',
      source: 'mapillary',
      'source-layer': 'sequence',
      paint: {
        'line-width': [
          'interpolate',
          ['linear'],
          ['zoom'],
          0,
          0.5,
          10,
          2,
          14,
          4,
          16,
          5,
          22,
          3,
        ],
        'line-color': 'rgba(71, 218, 98, 1)',
      },
      layout: { visibility: 'none' },
    },
    {
      id: 'mapillary-image',
      type: 'circle',
      source: 'mapillary',
      'source-layer': 'sequence',
      paint: {
        'circle-radius': [
          'interpolate',
          ['linear'],
          ['zoom'],
          14,
          3,
          17,
          8,
          22,
          12,
        ],
        'circle-color': 'rgba(71, 218, 98, 1)',
      },
      layout: { visibility: 'none' },
    },
    {
      id: 'panoramax-sequences',
      type: 'line',
      source: 'panoramax',
      'source-layer': 'sequences',
      paint: {
        'line-width': [
          'interpolate',
          ['linear'],
          ['zoom'],
          0,
          0.5,
          10,
          2,
          14,
          4,
          16,
          5,
          22,
          3,
        ],
        'line-color': '#FF6F00',
      },
      layout: {
        'line-cap': 'square',
        visibility: 'none',
      },
    },
    {
      id: 'panoramax-pictures',
      type: 'circle',
      source: 'panoramax',
      'source-layer': 'pictures',
      paint: {
        'circle-radius': [
          'interpolate',
          ['linear'],
          ['zoom'],
          14,
          3,
          17,
          8,
          22,
          12,
        ],
        'circle-color': '#FF6F00',
      },
      layout: { visibility: 'none' },
    },
    {
      id: 'markers',
      type: 'symbol',
      source: 'markers',
      'source-layer': 'issues',
      layout: {
        'icon-image': ['concat', 'marker-b-', ['get', 'item']],
        'icon-anchor': 'bottom',
        'icon-allow-overlap': true,
        visibility: 'none',
      },
      paint: {
        'icon-opacity': ['case', ['feature-state', 'hidden'], 0, 1],
      },
    },
    {
      id: 'markers-limit',
      type: 'symbol',
      source: 'markers',
      'source-layer': 'limit',
      layout: {
        'icon-image': 'limit',
        'icon-allow-overlap': true,
        'icon-pitch-alignment': 'map',
        'icon-rotation-alignment': 'map',
        visibility: 'none',
      },
    },
    {
      id: 'heatmap13',
      type: 'fill',
      filter: ['<', ['zoom'], 13],
      source: 'heatmap',
      'source-layer': 'issues',
      paint: {
        'fill-color': [
          'rgb',
          ['round', ['-', ['/', ['get', 'color'], 256 * 256], 0.5]],
          ['%', ['round', ['-', ['/', ['get', 'color'], 256], 0.5]], 256],
          ['%', ['get', 'color'], 256],
        ],
        'fill-opacity': 1,
      },
      layout: { visibility: 'none' },
    },
    {
      id: 'heatmap',
      type: 'fill',
      filter: ['>=', ['zoom'], 13],
      source: 'heatmap',
      'source-layer': 'issues',
      paint: {
        'fill-color': [
          'rgb',
          ['round', ['-', ['/', ['get', 'color'], 256 * 256], 0.5]],
          ['%', ['round', ['-', ['/', ['get', 'color'], 256], 0.5]], 256],
          ['%', ['get', 'color'], 256],
        ],
        'fill-opacity': ['+', 0.25, ['*', ['/', ['get', 'count'], 256], 0.75]],
      },
      layout: { visibility: 'none' },
    },
  ],
  id: 'osmose',
}
