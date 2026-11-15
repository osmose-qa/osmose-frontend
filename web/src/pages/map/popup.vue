<template>
  <div id="popupTpl">
    <div v-if="status == 'clean'" class="bulle_other"></div>
    <div v-if="status == 'error'" class="bulle_other">{{ error }}</div>
    <div v-if="status == 'loading'" class="bulle_other">
      <center>
        <img src="~../../../static/images/throbbler.gif" alt="downloading" />
      </center>
    </div>
    <div v-if="status == 'fill'">
      <div class="bulle_msg">
        <div class="bulle_row bulle_err">
          <h5>
            <span :class="`severity-level severity-level-${level}`"></span>{{ title.auto }}
          </h5>
          <div v-if="subtitle">{{ subtitle.auto }}</div>
          <a
            :href="`../issue/${uuid}`"
            target="_blank"
            :title="$t('Issue details')"
          >
            <span style="display: block; text-align: right;" :title="$t('Report based on data from date')">
              <translate>Reported on</translate> {{ b_date }}
            </span>
          </a>
        </div>
        <div
          v-for="elem in elems"
          :key="`${elem.type}/${elem.id}`"
          class="bulle_row bulle_elem"
        >
          <template v-if="!elem.infos">
            <b>
              <a
                target="_blank"
                :href="main_website + `${elem.type}/${elem.id}`"
                :title="$t('Show Object on {where}', { where: main_website })"
              >
                {{ elem.type }} {{ elem.id }}</a
              >
            </b>
          </template>
          <a
            v-if="elem.type == 'relation'"
            target="_blank"
            :href="`http://polygons.openstreetmap.fr/?id=${elem.id}`"
          >
            analyser
          </a>
          <a
            v-if="elem.type == 'node'"
            :href="`http://localhost:8111/load_object?objects=n${elem.id}`"
            target="hiddenIframe"
            class="josm"
            :title="$t('Edit Object with {where}', { where: 'JOSM' })"
          >
            josm</a
          >
          <a
            v-if="elem.type == 'node'"
            :href="main_website + `edit?editor=id&node=${elem.id}`"
            target="_blank"
            class="id"
            :title="$t('Edit Object with {where}', { where: 'iD' })"
          >
            iD</a
          >
          <a
            v-if="elem.type == 'way'"
            :href="`http://localhost:8111/load_object?objects=w${elem.id}`"
            target="hiddenIframe"
            class="josm"
            :title="$t('Edit Object with {where}', { where: 'JOSM' })"
          >
            josm</a
          >
          <a
            v-if="elem.type == 'way'"
            :href="main_website + `edit?editor=id&way=${elem.id}`"
            target="_blank"
            class="id"
            :title="$t('Edit Object with {where}', { where: 'iD' })"
          >
            iD</a
          >
          <a
            v-if="elem.type == 'relation'"
            :href="`http://localhost:8111/import?url=${remote_url_read}api/0.6/${elem.type}/${elem.id}/full`"
            target="hiddenIframe"
            class="josm"
            :title="$t('Edit Object with {where}', { where: 'JOSM' })"
          >
            josm</a
          >
          <a
            v-if="elem.type == 'relation'"
            :href="main_website + `edit?editor=id&relation=${elem.id}`"
            target="_blank"
            class="id"
            :title="$t('Edit Object with {where}', { where: 'iD' })"
          >
            iD</a
          >
          <a
            href="#"
            class="editor_edit"
            :title="
              $t('Edit Object with {where}', {
                where: $t('online Osmose Editor'),
              })
            "
            @click.stop.prevent="editor(uuid)"
          >
            edit</a
          >
          <br />
          <div v-for="fix in elem.fixes" :key="fix.num" class="fix">
            <div class="fix_links">
              <a
                :href="
                  'http://localhost:8111/import?url=' +
                  api_url +
                  `/api/0.3/issue/${uuid}/fix/${fix.num}`
                "
                target="hiddenIframe"
                class="josm"
                :title="$t('Load the fix in {where}', { where: 'JOSM' })"
              >
                fix-josm</a
              >
              <a
                href="#"
                class="editor_fix"
                :title="
                  $t('Load the fix in {where}', {
                    where: $t('online Osmose Editor'),
                  })
                "
                @click.stop.prevent="editor(uuid, fix.num)"
              >
                fix-edit</a
              >
            </div>
            <div v-for="o in fix.add" :key="o.k" class="add">
              <b>{{ o.k }}</b> =
              <a v-if="o.vlink" :href="o.vlink" target="popup_tag2link">
                {{ o.v }}
              </a>
              <span v-else>
                {{ o.v }}
              </span>
            </div>
            <div v-for="o in fix.mod" :key="o.k" class="mod">
              <b>{{ o.k }}</b> =
              <a v-if="o.vlink" :href="o.vlink" target="popup_tag2link">
                {{ o.v }}
              </a>
              <span v-else>
                {{ o.v }}
              </span>
            </div>
            <div v-for="o in fix.del" :key="o.k" class="del">
              <b>{{ o.k }}</b>
            </div>
          </div>
          <div v-for="tag in elem.tags" :key="tag.k">
            <b>{{ tag.k }}</b> =
            <a v-if="tag.vlink" :href="tag.vlink" target="popup_tag2link">
              {{ tag.v }}
            </a>
            <span v-else>
              {{ tag.v }}
            </span>
          </div>
        </div>
        <div v-for="fix in new_elems" :key="fix.num" class="bulle_row bulle_elem">
          <div class="fix">
            <div class="fix_links">
              <a
                :href="
                  'http://localhost:8111/import?url=' +
                  api_url +
                  `/api/0.3/issue/${uuid}/fix/${fix.num}`
                "
                target="hiddenIframe"
                class="josm"
                :title="$t('Add the new object in {where}', { where: 'JOSM' })"
              >
                fix-josm</a
              >
            </div>
            <div v-for="o in fix.add" :key="o.k" class="add">
              <b>{{ o.k }}</b> =
              <a v-if="o.vlink" :href="o.vlink" target="popup_tag2link">
                {{ o.v }}
              </a>
              <span v-else>
                {{ o.v }}
              </span>
            </div>
            <div v-for="o in fix.mod" :key="o.k" class="mod">
              <b>{{ o.k }}</b> =
              <a v-if="o.vlink" :href="o.vlink" target="popup_tag2link">
                {{ o.v }}
              </a>
              <span v-else>
                {{ o.v }}
              </span>
            </div>
            <div v-for="o in fix.del" :key="o.k" class="del">
              <b>{{ o.k }}</b>
            </div>
          </div>
        </div>
      </div>
      <div id="bulle_editor" class="bulle_row">
        <a
          :href="main_website + `?mlat=${lat}&mlon=${lon}#map=18/${lat}/${lon}`"
          target="popup_osm"
          :title="$t('Show the area on {where}', { where: main_website })"
        >
          osm.org</a
        >
        <a
          :href="main_website + `edit#map=18/${lat}/${lon}`"
          target="_blank"
          :title="$t('Edit the area on {where}', { where: main_website })"
        >
          iD-area</a
        >
        <a
          :href="`http://localhost:8111/load_and_zoom?left=${minlon}&bottom=${minlat}&right=${maxlon}&top=${maxlat}`"
          target="hiddenIframe"
          class="josm"
          :title="$t('Edit the area on {where}', { where: 'JOSM' })"
        >
          josm-area</a
        >
      </div>
      <div id="bulle_footer" class="bulle_row">
        <div id="bulle_button">
          <div class="btn-group" role="group">
            <a
              class="popup_help btn btn-info btn-sm"
              role="button"
              href="#"
              :title="$t('Help')"
              @click.stop.prevent="doc(item, classs)"
            >
              ℹ <translate>Help</translate>
            </a>
            <a
              class="false_positive btn btn-danger btn-sm"
              role="button"
              href="#"
              target="hiddenIframe"
              :title="
                $t('false positive') +
                ' - ' +
                $t(
                  'Report the issue as improper, if it is not an issue according to you. The issue will not be displayed to anyone anymore.'
                )
              "
              @click="setFalsePositive(uuid)"
            >
              ✘ <translate>Not an issue</translate>
            </a>
            <a
              class="corrected btn btn-success btn-sm"
              role="button"
              href="#"
              target="hiddenIframe"
              :title="
                $t('corrected') +
                ' - ' +
                $t(
                  'After fixing the issue in the OSM data, mark it as done. It will also disappear automatically on the next check.'
                )
              "
              @click="setDone(uuid)"
            >
              ✔ <translate>Fixed</translate>
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Popup, Map } from 'maplibre-gl'
import Vue, { PropType } from 'vue'

import confirmFalsePositive from '../../components/confirmFalsePositive.vue'
import { Elem, Fix } from '../../types'

export default Vue.extend({
  mixins: [confirmFalsePositive],

  props: {
    map: {
      type: Object as PropType<Map>,
      required: true,
    },
    initialUuid: {
      type: String,
      default: undefined,
    },
    main_website: {
      type: String,
      required: true,
    },
    remote_url_read: {
      type: String,
      required: true,
    },
  },

  data(): {
    popup: Popup | null
    open_popup?: string | null // uuid
    status: 'clean' | 'error' | 'loading' | 'fill'
    error?: string
    uuid?: string
    level?: number
    item?: number
    class?: number
    title?: string
    subtitle?: string
    b_date?: string
    elems?: Elem[]
    new_elems?: Elem[]
    lon?: number
    lat?: number
    minlat?: number
    maxlat?: number
    minlon?: number
    maxlon?: number
  } {
    return {
      popup: null,
      open_popup: null,
      status: 'clean',
      error: null,
      uuid: null,
      level: null,
      item: null,
      class: null,
      title: null,
      subtitle: null,
      b_date: null,
      elems: [],
      new_elems: [],
      lon: null,
      lat: null,
      minlat: null,
      maxlat: null,
      minlon: null,
      maxlon: null,
    }
  },

  watch: {
    elems() {
      this.$emit('elems', this.elems)
    },
  },

  computed: {
    api_url(): string {
      return (API_URL.startsWith('http') ? '' : location.protocol) + API_URL
    },

    classs(): string {
      return this.class
    },
  },

  mounted(): void {
    this.map.on('load', () => {
      this.popup = new Popup({ closeOnClick: false })
        .setMaxWidth('280px')
        .setOffset([0, -24])
        .setDOMContent(document.getElementById('popupTpl'))

      if (this.initialUuid) {
        this._openPopup(this.initialUuid, [0, 0], this)
      }

      this.map.on('click', 'markers', (e) => {
        e.preventDefault()
        if (e.features[0].properties.uuid) {
          if (this.open_popup === e.features[0].properties.uuid) {
            this._closePopup()
          } else {
            this.feature_id = e.features[0].id
            this._openPopup(
              e.features[0].properties.uuid,
              e.features[0].geometry.coordinates.slice(),
              e.features[0]
            )
          }
        }
      })

      this.popup.on('close', (e) => {
        this._closePopup()
      })

      this.map.on('click', (e) => {
        if (e.defaultPrevented === false) {
          this._closePopup()
        }
      })
    })
  },

  methods: {
    _closePopup(): void {
      this.$emit('update-issue-uuid', null)
      this.open_popup = undefined
      if (this.map) {
        this.popup.remove()
      }
    },

    _openPopup(uuid, lngLat, layer): void {
      if (this.open_popup === uuid) {
        return
      }
      this.open_popup = uuid
      this.$emit('update-issue-uuid', uuid)

      this.status = 'loading'
      this.popup.setLngLat(lngLat).addTo(this.map)

      setTimeout(() => {
        if (this.popup.isOpen()) {
          // Popup still open, so download content
          this.load(uuid, this.popup)
          this.layer = layer
        } else {
          this.status = 'clean'
        }
      }, 100)
    },

    _dismissMarker(): void {
      setTimeout(() => {
        this.corrected()
      }, 200)
    },

    corrected(): void {
      this.$emit('remove-marker', this.feature_id)
      this._closePopup()
    },

    load(uuid: string, popop: Popup): void {
      fetch(API_URL + `/api/0.3/issue/${uuid}?langs=auto`, {
        headers: new Headers({
          'Accept-Language': this.$route.params.lang,
        }),
      })
        .then((response) => response.json())
        .then((response) => {
          Object.assign(this, response)
          this.status = 'fill'
          popop.setLngLat([this.lon, this.lat])

          this.$emit('issue-data', response)

          this.$nextTick(() => {
            this.$emit('load-doc', {
              item: response.item,
              classs: response['class'],
            })
          })
        })
        .catch((error) => {
          this.error = error.message
          this.status = 'error'
        })
    },

    setDone(uuid: string): void {
      fetch(API_URL + `/api/0.3/issue/${uuid}/done`)
      this._dismissMarker()
    },

    setFalsePositive(uuid: string): void {
      if (this.confirmeFalsePositive(uuid)) {
        fetch(API_URL + `/api/0.3/issue/${uuid}/false`)
        this._dismissMarker()
      }
    },

    editor(uuid: string, fix: Fix): void {
      this.$emit('fix-edit', { uuid, fix })
    },

    doc(item: number, classs: number): void {
      this.$emit('show-doc', { item, classs })
    },
  },
})
</script>

<style>
.maplibregl-popup {
  will-change: unset; /* Overide MapLibre CSS to avoid blury popup text */
}

.maplibregl-popup-content {
  box-shadow: 0 3px 14px rgba(0, 0, 0, 0.4);
  border-radius: 6px;
  padding: 0px;
}

.maplibregl-popup-content .btn {
  color: #fff;
}
.maplibregl-popup-content .bulle_msg a {
  text-decoration: underline;
}
</style>

<style scoped>
.bulle_other {
  min-width: 200px;
  max-height: 100px;
  padding: 5px;
}

.bulle_row {
  padding: 0px 10px;
}

.bulle_row:first-child {
  padding-top: 10px;
  border-radius: 6px 6px 0px 0px;
}
.bulle_row:last-child {
  padding-bottom: 10px;
  border-radius: 0px 0px 6px 6px;
}

.bulle_msg {
  min-width: 200px;
  max-height: 250px;
  overflow: auto;
  word-wrap: break-word;
}
.bulle_msg div.closebubble {
  float: right;
  color: #eeeeee;
  font-weight: bold;
  background-color: #aaaaaa;
  margin-right: 2px;
  text-decoration: none;
}
.bulle_msg div.closebubble a:link,
.bulle_msg div.closebubble a:visited {
  color: #eeeeee;
}
.bulle_msg div.closebubble a:hover {
  color: #000000;
}
.bulle_msg div.help {
  background-color: #0083ff;
}
.bulle_msg div.help a:hover {
  color: #d1d1d1;
}

.bulle_err {
  background-color: #f3f3f3;
  border-bottom: solid 1px lightgray;
}

.bulle_elem {
  direction: ltr;
}

.bulle_elem .fix {
  border: solid 1px lightgray;
}
.bulle_elem .fix_links {
  float: right;
}
.bulle_elem .fix .add {
  color: green;
}
.bulle_elem .fix .mod {
  color: darkorange;
}
.bulle_elem .fix .del {
  color: red;
}

#bulle_editor {
  display: block;
  text-align: right;
}

#bulle_footer {
  display: table;
  width: 100%;
}

#bulle_button {
  display: table-cell;
  float: right;
  padding-top: 5px;
  padding-left: 5px;
}
html[dir='rtl'] #bulle_button {
  float: left;
  padding-left: 0px;
  padding-right: 5px;
}

#bulle_button .btn-group {
  direction: ltr;
}

.bulle_elem .add b:before {
  content: ' + ';
}
.bulle_elem .del b:before {
  content: ' - ';
}
.bulle_elem .mod b:before {
  content: ' ~ ';
}

.severity-level {
  display: inline-block;
  vertical-align: middle;
  margin: 0px 2px 0px 0px;
}
</style>
