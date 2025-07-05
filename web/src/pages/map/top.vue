<template>
  <div id="top_links">
    <ul id="topmenu">
      <li id="menu-lang">
        <a href="#" onclick="return false;">
          <translate>Change language</translate> ▼
        </a>
        <ul class="submenu">
          <li
            v-for="(v, k) in languages_name"
            :key="k"
            :class="$route.params.lang == k ? 'bold' : ''"
          >
            <router-link :to="'/' + k + location" @click="changeLang(v)">
              {{ v.name }} ({{ k }})
            </router-link>
          </li>
        </ul>
      </li>

      <li id="menu-byuser">
        <router-link :to="user ? `../byuser/${user}` : '../byuser/'">
          <translate
            translate-comment="TRANSLATORS: link to help in appropriate language"
          >
            Issues by user
          </translate>
        </router-link>
      </li>
      <li id="menu-statistics">
        <router-link to="../control/update_matrix">
          <translate translate-comment="TRANSLATORS: link to source code">
            Statistics
          </translate>
        </router-link>
      </li>

      <li>
        <a href="#" onclick="return false;"><translate>Export</translate> ▼</a>
        <ul class="submenu">
          <li>
            <a :href="`../issues/open?${params}`" target="_blank">
              <translate>Html list</translate>
            </a>
          </li>
          <li>
            <a
              :href="`${api_url}/api/0.3/issues.josm?${params}`"
              target="hiddenIframe"
            >
              JOSM
            </a>
          </li>
          <li>
            <a
              :href="`${api_url}/api/0.3/issues.rss?${params}`"
              target="_blank"
            >
              RSS
            </a>
          </li>
          <li>
            <a :href="`${api_url}/api/0.3/issues.gpx?${params}`">GPX</a>
          </li>
          <li>
            <a :href="`${api_url}/api/0.3/issues.kml?${params}`">KML</a>
          </li>
          <li>
            <a :href="`${api_url}/api/0.3/issues?${params}`" target="_blank">
              Json
            </a>
          </li>
          <li>
            <a
              :href="`${api_url}/api/0.3/issues.csv?${params}`"
              target="_blank"
            >
              CSV
            </a>
          </li>
          <li>
            <a :href="`/api/0.3/issues.geojson?${params}`" target="_blank">
              GeoJson
            </a>
          </li>
          <li>
            <a
              :href="`/api/0.3/issues.maproulette.geojson?${params}`"
              target="_blank"
            >
              Maproulette
            </a>
          </li>
        </ul>
      </li>

      <li id="menu-help">
        <a href="#" onclick="return false;"><translate>Help</translate> ▼</a>
        <ul class="submenu">
          <li>
            <router-link to="../contact">
              <translate>Contact</translate>
            </router-link>
          </li>
          <li>
            <a href="http://wiki.openstreetmap.org/wiki/Osmose">
              <translate>Help on wiki</translate>
            </a>
          </li>
          <li>
            <router-link to="../copyright">
              <translate>Copyright</translate>
            </router-link>
          </li>
          <li>
            <a href="https://github.com/osmose-qa">
              <translate>Sources</translate>
            </a>
          </li>
          <li>
            <router-link to="../translation">
              <translate>Translation</translate>
            </router-link>
          </li>
        </ul>
      </li>

      <delay
        tag="li"
        id="menu-delay"
        :warning="0.9"
        :error="1.6"
        :v="(Date.now() - Date.parse(timestamp)) / 1000 / 60 / 60 / 24"
      >
        <router-link to="../control/update_summary">
          {{ $t('Delay:') }}
          <time-ago v-if="timestamp" :datetime="timestamp" tooltip />
          <span v-else>-</span>
        </router-link>
      </delay>

      <li id="menu-user">
        <template v-if="user">
          <router-link :to="`../byuser/${user}`">
            {{ user }} ({{
              user_error_count[1] + user_error_count[2] + user_error_count[3]
            }}) ▼
          </router-link>
          <ul class="submenu">
            <li>
              <router-link :to="`../byuser/${user}?level=1`">
                {{
                  $t('Level {level} issues ({count})', {
                    level: 1,
                    count: user_error_count[1],
                  })
                }}
              </router-link>
            </li>
            <li>
              <router-link :to="`../byuser/${user}?level=2`">
                {{
                  $t('Level {level} issues ({count})', {
                    level: 2,
                    count: user_error_count[2],
                  })
                }}
              </router-link>
            </li>
            <li>
              <router-link :to="`../byuser/${user}?level=3`">
                {{
                  $t('Level {level} issues ({count})', {
                    level: 3,
                    count: user_error_count[3],
                  })
                }}
              </router-link>
            </li>
            <li>
              <a :href="api_url + `/${$route.params.lang}/logout`">
                <translate>Logout</translate>
              </a>
            </li>
          </ul>
        </template>
        <a v-else :href="api_url + `/${$route.params.lang}/login`">
          <translate>Login</translate>
        </a>
      </li>
      <li id="closed_marker_count" v-if="closed_marker_count">
        <span :title="$t('Number of closed makers in this session')">✔ {{ closed_marker_count }}</span>
      </li>
      <editor-menu
        :object_count="object_count"
        @editor-save="$emit('editor-save')"
      />
    </ul>
  </div>
</template>

<script lang="ts">
import { Map } from 'maplibre-gl'
import Vue, { PropType } from 'vue'
import TimeAgo from 'vue2-timeago'

import EditorMenu from './editor-menu.vue'
import Delay from '../../components/delay.vue'
import { ItemState, LanguagesName } from '../../types'

export default Vue.extend({
  components: {
    Delay,
    EditorMenu,
    TimeAgo,
  },
  props: {
    map: {
      type: Object as PropType<Map | null>,
      default: null,
    },
    mapState: {
      type: Object,
      required: true,
    },
    itemState: {
      type: Object as PropType<ItemState>,
      required: true,
    },
    languages_name: {
      type: Object as PropType<{ [lang: string]: LanguagesName }>,
      required: true,
    },
    user: {
      type: String as PropType<string | undefined>,
      default: undefined,
    },
    user_error_count: {
      type: Object as PropType<{ [level: number]: number } | null>,
      default: null,
    },
    timestamp: {
      type: String as PropType<string | undefined>,
      default: undefined,
    },
    closed_marker_count: {
      type: Number,
      default: null,
    },
    object_count: {
      type: Number,
      default: null,
    },
  },

  data(): {
    params: string
  } {
    return {
      params: '',
    }
  },

  computed: {
    api_url(): string {
      return API_URL
    },

    lang(): string {
      return this.$route.params.lang
    },

    location(): string {
      const i = window.location.pathname.indexOf('/', 1)
      return (
        window.location.pathname.substring(i) + '?' + window.location.search
      )
    },
  },

  watch: {
    itemState: {
      deep: true,
      handler(): void {
        this.setParams()
      },
    },

    mapState: {
      deep: true,
      handler(): void {
        this.setParams()
      },
    },
  },

  methods: {
    changeLang(lang: LanguagesName): void {
      window.document.dir = lang.direction
    },

    setParams(): void {
      const params = { ...this.mapState, ...this.itemState }
      delete params.lat
      delete params.lon
      params.limit = 500
      params.bbox = this.map.getBounds().toArray().flat().join(',')
      this.params = Object.entries(params)
        .filter(([, v]) => v !== undefined && v != null)
        .map(([k, v]) => encodeURIComponent(k) + '=' + encodeURIComponent(v))
        .join('&')
    },
  },
})
</script>

<style>
div#top_links {
  background-color: #ffffff;
  background-clip: padding-box;
  border-bottom: 2px solid rgba(0, 0, 0, 0.2);
  position: absolute;
  height: 24px;
  width: 100%;
  left: 0px;
  top: 0px;
  opacity: 0.9;
  font-size: 13px;
  z-index: 1025;
}

#topmenu {
  list-style-type: none;
  margin: 0;
  padding: 0;
  border: 0;
}
#topmenu li {
  display: inline-block;
  vertical-align: top;
  margin: 0;
  padding: 0;
  border: 0;
}
#topmenu li a:link,
#topmenu li a:visited {
  display: block;
  margin: 0;
  padding: 2px 8px;
  border-right: 1px solid #cccccc;
  text-decoration: none;
}
#topmenu li a:hover #topmenu li a:active {
  background-color: #b0b0b0;
}

#topmenu .submenu {
  display: none;
  list-style-type: none;
  margin: 0;
  padding: 0;
  border: 0;
}
#topmenu .submenu li {
  display: block;
  margin: 0;
  padding: 0;
  border: 0;
  border-top: 1px solid #003453;
  border-right: 1px solid #003453;
}
#topmenu .submenu li a:link,
#topmenu .submenu li a:visited {
  display: block;
  margin: 0;
  border: 0;
  text-decoration: none;
  background: #dddddd;
}
#topmenu .submenu li a:hover {
  background-image: none;
  background-color: #b0b0b0;
}

#topmenu li:hover > .submenu {
  display: block;
}

@media (max-width: 399px) {
  #topmenu #menu-lang,
  #topmenu #menu-openstreetmapfr,
  #topmenu #menu-byuser,
  #topmenu #menu-relation_analyser,
  #topmenu #menu-statistics,
  #topmenu #closed_marker_count,
  #topmenu #menu-help,
  #topmenu #menu-delay {
    display: none;
  }
}

@media (min-width: 400px) and (max-width: 767px) {
  #topmenu #menu-byuser,
  #topmenu #menu-relation_analyser,
  #topmenu #menu-statistics,
  #topmenu #closed_marker_count,
  #topmenu #menu-help,
  #topmenu #menu-delay {
    display: none;
  }
}

@media (min-width: 768px) and (max-width: 991px) {
  #topmenu #menu-byuser,
  #topmenu #menu-relation_analyser,
  #topmenu #menu-statistics,
  #topmenu #closed_marker_count,
  #topmenu #menu-help {
    display: none;
  }
}
</style>
