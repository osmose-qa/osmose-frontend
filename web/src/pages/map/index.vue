<template>
  <div>
    <vue-topprogress ref="topProgress"></vue-topprogress>
    <div v-if="error">{{ error }}</div>
    <div>
      <top
        :map="map"
        :item-state="itemState"
        :map-state="mapState"
        :languages_name="languages_name"
        :user="user"
        :user_error_count="user_error_count"
        :timestamp="timestamp"
        :closed_marker_count="closed_marker_count"
        :object_count="editionStack.length"
        @editor-save="
          docWasOpen = $refs.doc.isShow();
          $refs.doc.hide();
          $refs.editor.show();
          $nextTick(() => {
            $refs.editorEditor.save()
          });
        "
      />
      <div class="map-container">
        <side-pannel
          :map="map"
          position="top-left"
          menuText="☰"
          menuTitle="Menu"
          class="side-pannel"
        >
          <items ref="items" :map-state="mapState" :error="error">
            <items-filters
              :original_tags="tags"
              :countries="countries"
              :item-state="itemState"
              @state-update="itemState = $event"
            />
            <items-list
              ref="items-list"
              :categories="categories"
              :item_levels="item_levels"
              :item-state="itemState"
              @state-update="itemState = $event"
            />
          </items>
        </side-pannel>
        <l-map
          :item-state="itemState"
          :map-state="mapState"
          @set-map="setMap($event)"
          class="map"
        />
        <MarkerLayer v-if="map" ref="markerLayer" :map="map" />
        <OsmObject
          v-if="map"
          ref="osmObject"
          :map="map"
          :remote-url-read="remote_url_read"
        />
        <side-pannel
          ref="doc"
          :map="map"
          position="top-right"
          menuText="ℹ"
          menuTitle="Doc"
          class="side-pannel"
        >
          <doc
            :map="map"
            :itemClass="doc"
            @hide-item-markers="onHideItemMarkers($event)"
          />
        </side-pannel>
        <side-pannel
          ref="editor"
          :map="map"
          :showInitial="false"
          class="side-pannel"
        >
          <editor
            ref="editorEditor"
            :main_website="main_website"
            :user="user"
            :edition_stack="editionStack"
            @edition="editionStack = $event"
            @issue-done="
              $refs.popup.corrected();
              $refs.editor.hide();
              if (docWasOpen) {
                $refs.doc.show()
              }
            "
            @cancel="
              $refs.editor.hide();
              if (docWasOpen) {
                $refs.doc.show()
              }
            "
          />
        </side-pannel>
      </div>
      <iframe id="hiddenIframe" name="hiddenIframe"></iframe>
      <popup
        ref="popup"
        v-if="map"
        :map="map"
        :initial-uuid="issueUuid"
        :main_website="main_website"
        :remote_url_read="remote_url_read"
        @update-issue-uuid="issueUuid = $event"
        @elems="$event ? $refs.osmObject.select($event) : $refs.osmObject.clear()"
        @remove-marker="
          $refs.markerLayer.remove($event);
          closed_marker_count += 1
        "
        @fix-edit="
          docWasOpen = $refs.doc.isShow();
          $refs.doc.hide();
          $refs.editor.show();
          $nextTick(() => {
            $refs.editorEditor.load($event.uuid, $event.fix)
          });
        "
        @show-doc="showDoc"
        @load-doc="loadDoc"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { Map } from 'maplibre-gl'

import Doc from './doc.vue'
import Editor from './editor.vue'
import ItemsFilters from './items-filters.vue'
import ItemsList from './items-list.vue'
import Items from './items.vue'
import LMap from './map.vue'
import MarkerLayer from './marker-layer.vue'
import OsmObject from './osm-object.vue'
import Popup from './popup.vue'
import SidePannel from './side-pannel.vue'
import Top from './top.vue'
import { ItemState, LanguagesName, Category } from '../../types'
import VueParent from '../Parent.vue'

interface MapState {
  lat: number
  lon: number
  zoom: number
}

export default VueParent.extend({
  data(): {
    error?: string
    languages_name: LanguagesName
    user: string
    user_error_count: { [level: number]: number }
    timestamp: string
    tags: string[]
    countries: string[]
    categories: Category[]
    main_website: string
    remote_url_read: string
    map: Map
    item_levels: Object
    itemState: ItemState
    issueUuid: string
    mapState: MapState
    editor: string[]
    doc: string[]
    closed_marker_count: number
    editionStack: string[]
    docWasOpen: boolean
  } {
    return {
      error: undefined,
      languages_name: {},
      user: null,
      user_error_count: null,
      timestamp: null,
      tags: [],
      countries: [],
      categories: [],
      main_website: '',
      remote_url_read: '',
      map: null,
      item_levels: {},
      itemState: {
        item: 'xxxx',
        level: '1',
        // TODO filtrer on existing tagss
        tags: null,
        fixable: null,
        class: null,
        useDevItem: null,
        source: null,
        username: null,
        country: null,
      },
      issueUuid: undefined,
      mapState: {
        lat: 46.97,
        lon: 2.75,
        zoom: 16,
      },
      editor: null,
      doc: null,
      closed_marker_count: null,
      editionStack: [],
      docWasOpen: false,
    }
  },

  components: {
    Top,
    SidePannel,
    LMap,
    Items,
    ItemsFilters,
    ItemsList,
    Doc,
    Editor,
    Popup,
    MarkerLayer,
    OsmObject,
  },

  created(): void {
    document.querySelector(
      'head'
    ).innerHTML += `<link rel="stylesheet" href="${API_URL}/assets/sprites.css" type="text/css"/>`
    this.initializeItemState()
    this.initializeMapState()
  },

  mounted(): void {
    this.setData()
  },

  watch: {
    $route(to, from): void {
      if (to.params.lang != from.params.lang) {
        this.setData()
      }
    },

    itemState: {
      deep: true,
      handler(): void {
        this.saveItemState()
      },
    },

    issueUuid: {
      handler(): void {
        this.saveItemState()
      },
    },

    mapState: {
      deep: true,
      handler(): void {
        this.saveMapState()
      },
    },

    closed_marker_count(): void {
      if (this.closed_marker_count == 100) {
        alert(this.$t(`You have made a large number of corrections. That great!

That may not be your case, but note that Osmose-QA is not intended to be used for Mechanical Editing. Take a look about that at:
- https://wiki.openstreetmap.org/wiki/Automated_edits
- https://wiki.openstreetmap.org/wiki/What%27s_the_problem_with_mechanical_edits%3F`))
      }
    },

    editionStack(): void {
      if (this.editionStack.length == 30) {
        alert(this.$t(`You have made a large number changes with the tags editor. Think about saving your changes. You can save multiple times while keeping the same changeset.`))
      }
    },
  },

  methods: {
    getUrlVars(): { [key: string]: string } {
      const vars = {}
      let hash: string[]
      if (window.location.href.indexOf('#') >= 0) {
        const hashes = window.location.href
          .slice(window.location.href.indexOf('#') + 1)
          .split('&')
        for (let i = 0; i < hashes.length; i += 1) {
          hash = hashes[i].split('=')
          vars[decodeURIComponent(hash[0])] = decodeURIComponent(hash[1])
        }
      }
      return vars
    },

    setUrlVars(vars: Object): void {
      const merge = {
        ...this.getUrlVars(),
        ...vars,
      }
      window.location.href =
        '#' +
        Object.entries(merge)
          .filter(([key, value]) => !!value)
          .map(
            ([key, value]) =>
              encodeURIComponent(key) +
              '=' +
              (key == 'loc' ? value : encodeURIComponent(value))
          )
          .join('&')
    },

    filter(keys: string[], state): void {
      return Object.fromEntries(
        Object.entries(state).filter(
          ([key, val]) => val !== undefined && val != null && keys.includes(key)
        )
      )
    },

    initializeItemState(): void {
      const keys = Object.keys(this.itemState)

      const vars = this.getUrlVars()
      this.issueUuid = vars.issue_uuid
      const urlState = this.filter(keys, vars)

      let localStorageState = {}
      if (
        Object.keys(urlState).length == 0 &&
        localStorage.getItem('itemState')
      ) {
        localStorageState = this.filter(
          keys,
          JSON.parse(localStorage.getItem('itemState'))
        )
      }

      Object.assign(this.itemState, localStorageState, urlState)
    },

    initializeMapState(): void {
      const keys = Object.keys(this.mapState)

      const urlState = this.filter(keys, this.getUrlVars())

      let localStorageState = {}
      if (
        Object.keys(urlState).length == 0 &&
        localStorage.getItem('mapState')
      ) {
        localStorageState = this.filter(
          keys,
          JSON.parse(localStorage.getItem('mapState'))
        )
      }

      Object.assign(this.mapState, localStorageState, urlState)
    },

    saveItemState(): void {
      localStorage.setItem('itemState', JSON.stringify(this.itemState))
      this.setUrlVars(
        Object.assign({}, this.itemState, { issue_uuid: this.issueUuid })
      )
    },

    saveMapState(): void {
      localStorage.setItem('mapState', JSON.stringify(this.mapState))
    },

    setData(): void {
      this.fetchJsonProgressAssign(
        API_URL + window.location.pathname + '.json' + window.location.search,
        (response) => {
          // Legacy global variables
          window.API_URL = API_URL

          document.title = 'Osmose'
          const description = document.getElementById('description')
          if (description) {
            description.content = this.$t(
              'Control, verification and correction of {project} issues',
              { project: response.main_project }
            )
          }
          const viewport = document.getElementById('viewport')
          if (viewport) {
            viewport.content =
              'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
          }
        }
      )
    },

    onHideItemMarkers(disabled_item): void {
      this.$refs['items-list'].toggle_item(disabled_item, false)
    },

    setMap(map): void {
      this.map = map
      const callback = () => {
        this.mapState.lat = this.map.getCenter().lat
        this.mapState.lon = this.map.getCenter().lng
        this.mapState.zoom = this.map.getZoom()
      }
      this.map.on('moveend', callback)
      this.map.on('zoomend', callback)

      // Permalink
      window.addEventListener('hashchange', () => {
        const vars = this.getUrlVars()
        Object.keys(this.itemState).forEach((k) => {
          if (this.itemState[k] != vars[k]) {
            this.itemState[k] = vars[k] == null ? '' : vars[k]
          }
        })
      })
    },

    showDoc(e) {
      this.$refs.doc?.show()
      this.doc = [e.item, e.classs]
    },

    loadDoc(e) {
      this.doc = [e.item, e.classs]
    },
  },
})
</script>

<style>
body {
  margin: 0;
  font-family: arial, helvetica, sans-serif;
}

.bold {
  font-weight: bold;
}

@media (max-width: 640px) and (hover: none) {
  .josm {
    display: none;
  }
}
</style>

<style scoped>
a:link,
a:visited {
  color: rgb(0, 123, 255);
}

.map-container {
  position: absolute;
  top: 23px;
  bottom: 0px;
  left: 0px;
  right: 0px;

  overflow: hidden;
  display: flex;
}

.map-container .side-pannel {
  flex: initial;
}

.map-container .map {
  flex: auto;
}
</style>
