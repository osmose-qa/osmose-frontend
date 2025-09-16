<template>
  <div>
    <vue-topprogress ref="topProgress"></vue-topprogress>
    <div v-if="error">{{ error }}</div>
    <div v-else>
      <nav
        class="navbar navbar-expand-sm navbar-expand-md navbar-expand-lg navbar-dark"
        style="background-color: #212529"
      >
        <span v-if="favicon" class="navbar-brand">
          <img :src="favicon" />
        </span>
        <div class="collapse navbar-collapse">
          <ul class="navbar-nav">
            <li class="nav-item">
              <router-link class="nav-link" :to="`open?${queryBase}`">
                <translate>Open</translate>
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :to="`done?${queryBase}`">
                <translate>Fixed</translate>
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :to="`false-positive?${queryBase}`">
                <translate>False positives</translate>
              </router-link>
            </li>
            <li class="nav-item">
              <a
                class="nav-link"
                :href="`${api_url}/${$route.params.lang}/issues/graph.png?${query}`"
              >
                <translate>Graph</translate>
              </a>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :to="`../map/#${query}`">
                <translate>Map</translate>
              </router-link>
            </li>
          </ul>
          <div class="form-inline my-2 my-lg-0">
            <a
              :href="`${api_url}/api/0.3/issues.rss?${query}`"
              class="badge badge-secondary"
            >
              .rss </a
            >&nbsp;
            <a
              :href="`${api_url}/api/0.3/issues.gpx?${query}`"
              class="badge badge-secondary"
            >
              .gpx </a
            >&nbsp;
            <a
              :href="`${api_url}/api/0.3/issues.kml?${query}`"
              class="badge badge-secondary"
            >
              .kml </a
            >&nbsp;
            <a
              :href="`${api_url}/api/0.3/issues.csv?${query}`"
              class="badge badge-secondary"
            >
              .csv </a
            >&nbsp;
            <a
              :href="`${api_url}/api/0.3/issues?${query}`"
              class="badge badge-secondary"
            >
              .json </a
            >&nbsp;
            <a
              :href="`${api_url}/api/0.3/issues?${query}&full=true`"
              class="badge badge-secondary"
            >
              .json full</a
            >&nbsp;
            <a
              :href="`${api_url}/api/0.3/issues.geojson?${query}`"
              class="badge badge-secondary"
            >
              .geojson </a
            >&nbsp;
            <a
              :href="`${api_url}/api/0.3/issues.geojson?${query}&full=true`"
              class="badge badge-secondary"
            >
              .geojson full </a
            >&nbsp;
            <a
              :href="`${api_url}/api/0.3/issues.maproulette.geojson?${query}`"
              class="badge badge-secondary"
            >
              Maproulette
            </a>
          </div>
        </div>
      </nav>
      <br />

      <div class="form-inline col-sm-12 col-md-12">
        <form id="errors-list" method="get" action="">
          <h1 v-if="full_filter">Class filters</h1>
          <div class="form-row">
            <div class="form-group col-sm-3 col-md-3">
              <label for="item">
                <translate>Country</translate>
              </label>
              <select
                v-model="country"
                class="form-control form-control-sm"
                name="country"
              >
                <option value=""></option>
                <option v-for="res in countries" :key="res" :value="res">
                  {{ res }}
                </option>
              </select>
            </div>

            <div class="form-group col-sm-3 col-md-3">
              <label for="item">
                <translate>Item</translate>
              </label>
              <select
                v-model="item"
                class="form-control form-control-sm"
                name="item"
              >
                <option value="xxxx"></option>
                <option v-for="res in items" :key="res.item" :value="res.item">
                  {{ res.item }} - {{ res.menu.auto }}
                </option>
              </select>
            </div>

            <div class="form-group col-sm-3 col-md-3">
              <label for="level">
                <translate>Severity</translate>
              </label>
              <select
                v-model="level"
                name="level"
                class="form-control form-control-sm"
              >
                <option class="level-1__" value="1">
                  <translate>High</translate>
                </option>
                <option class="level-12_" value="1,2">
                  <translate>Normal or higher</translate>
                </option>
                <option class="level-123" value="1,2,3">
                  <translate>All</translate>
                </option>
                <option disabled="disabled"></option>
                <option class="level-_2_" value="2">
                  <translate>Normal only</translate>
                </option>
                <option class="level-__3" value="3">
                  <translate>Low only</translate>
                </option>
              </select>
            </div>

            <div class="form-group col-sm-3 col-md-3 buttons">
              <!-- {{ TRANSLATORS: 'Set' is used to choose a specific country/item on /errors }} -->
              <input
                type="submit"
                class="btn btn-secondary btn-sm"
                :value="$t('Set')"
              />
              &nbsp;
              <button
                v-if="!full_filter"
                type="button"
                class="btn btn-outline-secondary btn-sm"
                @click="full_filter = true"
              >
                <translate>More filters</translate>
                <span
                  v-if="extra_filter_number"
                  class="badge badge-secondary"
                  >{{ extra_filter_number }}</span
                >
              </button>
              <button
                v-else
                type="button"
                class="btn btn-outline-secondary btn-sm"
                @click="full_filter = false"
              >
                <translate>Less filters</translate>
              </button>
            </div>
          </div>

          <div v-if="full_filter">
            <div class="form-row">
              <div class="form-group col-sm-3 col-md-3">
                <label for="source">
                  <translate>Source id</translate>
                </label>
                <input
                  v-model="source"
                  name="source"
                  type="text"
                  class="form-control form-control-sm"
                />
              </div>

              <div class="form-group col-sm-3 col-md-3">
                <label for="class">
                  <translate>Class id</translate>
                </label>
                <input
                  v-model="class_"
                  name="class"
                  type="text"
                  class="form-control form-control-sm"
                />
              </div>

              <div class="form-group col-sm-3 col-md-3">
                <label for="tags">
                  <translate>Tag</translate>
                </label>
                <select
                  v-model="tags"
                  name="tags"
                  class="form-control form-control-sm"
                >
                  <option value=""></option>
                  <option v-for="tag in tags_list" :key="tag" :value="tag">
                    {{ $t(tag) }}
                  </option>
                </select>
              </div>

              <div class="form-group col-sm-3 col-md-3">
                <label for="useDevItem">
                  <translate>Show hidden items</translate>
                </label>
                <select
                  v-model="useDevItem"
                  name="useDevItem"
                  class="form-control form-control-sm"
                >
                  <option value="">
                    <translate>No (Default)</translate>
                  </option>
                  <option value="all">
                    <translate>All</translate>
                  </option>
                  <option value="true">
                    <translate>Only</translate>
                  </option>
                </select>
              </div>
            </div>

            <h1>Issue filters</h1>
            <div class="form-row">
              <div class="form-group col-sm-3 col-md-3">
                <label for="username">
                  <translate>OSM Username</translate>
                </label>
                <input
                  v-model="username"
                  name="username"
                  type="text"
                  class="form-control form-control-sm"
                />
              </div>

              <div class="form-group col-sm-3 col-md-3">
                <label for="bbox">
                  <translate>BBox</translate>
                </label>
                <input
                  v-model="bbox"
                  name="bbox"
                  type="text"
                  class="form-control form-control-sm"
                />
              </div>

              <div class="form-group col-sm-3 col-md-3">
                <label for="fixable">
                  <translate>Fixable</translate>
                </label>
                <select
                  v-model="fixable"
                  name="fixable"
                  class="form-control form-control-sm"
                >
                  <option value=""></option>
                  <option value="online"><translate>Online</translate></option>
                  <option value="josm">JOSM</option>
                </select>
              </div>
            </div>
          </div>
        </form>
      </div>

      <sorted-table
        id="table_source"
        :values="sortable(errors_groups).slice(0, showAnalyserCount)"
        class="table table-striped table-bordered table-hover table-sm"
      >
        <thead class="thead-dark">
          <tr>
            <th scope="col"><sort-link name="source_id">#</sort-link></th>
            <th scope="col">
              <sort-link name="analyser_country">
                <translate>source</translate>
              </sort-link>
            </th>
            <th scope="col">
              <sort-link name="timestamp"><translate>age</translate></sort-link>
            </th>
            <th scope="col">
              <sort-link name="item"><translate>item</translate></sort-link>
            </th>
            <th scope="col" title="class">
              <sort-link name="class">
                <translate
                  translate-comment="TRANSLATORS: this should be replaced by a abbreviation for 'class'"
                >
                  cl
                </translate>
              </sort-link>
            </th>
            <th scope="col">
              <sort-link name="title"><translate>title</translate></sort-link>
            </th>
            <th scope="col">
              <sort-link name="count"><translate>count</translate></sort-link>
            </th>
          </tr>
          <tr>
            <th colspan="6"><translate>Total</translate></th>
            <th style="text-align: left">{{ total }}</th>
          </tr>
        </thead>
        <template #body="sort">
          <tbody>
            <tr
              v-for="res in sort.values"
              :key="res.source_id + '|' + res.class"
            >
              <td>
                <router-link :to="`?source=${res.source_id}`">
                  {{ res.source_id }}
                </router-link>
              </td>
              <td>
                {{ res.analyser }}-
                <router-link :to="`?country=${res.country}`">
                  {{ res.country }}
                </router-link>
              </td>
              <td>
                <time-ago :datetime="res.timestamp" tooltip />
              </td>
              <td>
                <img
                  :src="api_url + `/api/0.3/markers/marker-l-${res.item}.png`"
                  :alt="res.item"
                />
                <router-link
                  :to="`?item=${res.item}&amp;country=${res.country}`"
                >
                  {{ res.item }}
                </router-link>
                <span v-if="res.menu">{{ res.menu }}</span>
              </td>
              <td>
                <router-link
                  :to="`?item=${res.item}&amp;class=${res.class}&amp;country=${res.country}`"
                >
                  {{ res.class }}
                </router-link>
              </td>
              <td>{{ res.title }}</td>
              <td>
                <router-link
                  :to="`?source=${res.source_id}&amp;item=${res.item}&amp;class=${res.class}`"
                >
                  {{ res.count === -1 ? 'N/A' : res.count }}
                </router-link>
              </td>
            </tr>
          </tbody>
        </template>
        <tfoot class="thead-dark">
          <tr v-if="showAnalyserCount < errors_groups.length">
            <th colspan="7">
              <a href="#" @click.prevent="showMoreAnalyser">
                <translate
                  >{{ showAnalyserCount }} / {{ errors_groups.length }} rows.
                  Show more.</translate
                >
              </a>
            </th>
          </tr>
          <tr>
            <th colspan="6"><translate>Total</translate></th>
            <th style="text-align: left">{{ total }}</th>
          </tr>
        </tfoot>
      </sorted-table>
      <br />

      <div>
        <issues-list
          v-if="gen"
          :query="query"
          :gen="gen"
          :opt_date="opt_date"
          :main_website="main_website"
          :remote_url_read="remote_url_read"
          :page_args="`status=${gen}&`"
        />
        <a href="#" @click.stop.prevent="show_more()">
          <translate>Show more issues</translate>
        </a>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import TimeAgo from 'vue2-timeago'

import IssuesList from '../../components/issues-list.vue'
import Translate from '../../components/translate.vue'
import VueParent from '../Parent.vue'

interface ErrorsGroup {
  item: number
  source_id: number
  class: number
  country: string
  analyser: string
  timestamp: string
  menu: string
  title: string
  count: number
  // computed
  analyser_country: string
}

export default VueParent.extend({
  data(): {
    error: boolean
    favicon?: string
    countries: string[]
    items: number[]
    errors_groups: ErrorsGroup[]
    total: number
    opt_date: boolean
    main_website: string
    remote_url_read: string
    query: string
    queryBase: string
    country: string
    item: number
    level: number[]
    limit: number
    source: number
    class_: number[]
    tags_list: string[]
    tags: string[]
    useDevItem: string
    username: string[]
    bbox: number[][]
    fixable: string
    full_filter: boolean
    extra_filter_number: number
    gen: string
    showAnalyserCount: number
  } {
    return {
      error: undefined,
      favicon: null,
      countries: [],
      items: [],
      errors_groups: [],
      total: 0,
      opt_date: false,
      main_website: '',
      remote_url_read: '',
      query: '',
      queryBase: '',
      country: this.$route.query.country,
      item: this.$route.query.item,
      level: this.$route.query.level,
      limit: this.$route.query.limit,
      source: null,
      class_: null,
      tags_list: [],
      tags: null,
      useDevItem: null,
      username: null,
      bbox: null,
      fixable: null,
      full_filter: false,
      extra_filter_number: 0,
      gen: undefined,
      showAnalyserCount: 100,
    }
  },

  computed: {
    api_url: () => API_URL,
    api_url_path: () => API_URL + window.location.pathname,
  },

  components: {
    IssuesList,
    TimeAgo,
    Translate,
  },

  watch: {
    $route() {
      this.render()
    },
  },

  mounted() {
    this.render()
  },

  methods: {
    sortable(data: ErrorsGroup[]): ErrorsGroup[] {
      return data
        .map((res) => {
          res.analyser_country = res.analyser + '-' + res.country
          return res
        })
        .sort((a, b) => b.count - a.count)
    },

    render(): void {
      this.country = this.$route.query.country
      this.item = this.$route.query.item
      this.level = this.$route.query.level
      this.limit = this.$route.query.limit
      this.source = this.$route.query.source
      this.class_ = this.$route.query.class
      this.tags = this.$route.query.tags
      this.useDevItem = this.$route.query.useDevItem
      this.username = this.$route.query.username
      this.bbox = this.$route.query.bbox
      this.fixable = this.$route.query.fixable
      this.count_extra_filter_number()

      if (this.extra_filter_number) {
        this.full_filter = true
      }

      this.query = window.location.search.substring(1)
      this.queryBase = this.query

      let title = {
        'issues/open': this.$t('Information'),
        'issues/done': this.$t('Fixed issues'),
        'issues/false-positive': this.$t('False positives'),
      }[this.$route.name]

      let status = {
        'issues/open': null,
        'issues/done': 'done',
        'issues/false-positive': 'false',
      }[this.$route.name]

      if (status) {
        this.query += `&status=${status}`
      }

      this.fetchJson(API_URL + '/api/0.3/tags', (response) => {
        this.tags_list = response.tags
      })

      this.fetchJsonAssign(
        API_URL +
          window.location.pathname +
          '.json' +
          window.location.search +
          (status ? `&status=${status}` : ''),
        () => {
          var res = this.items.find((e) => e.item == this.item)
          if (res) {
            title += ' - ' + res.menu.auto
            const favicon = document.getElementById('favicon')
            this.favicon = API_URL + `/api/0.3/markers/marker-l-${this.item}.png`
            favicon.href = this.favicon
          }

          document.title = 'Osmose - ' + title

          var rss = document.getElementById('rss')
          if (rss) {
            rss.remove()
          }
          rss = document.createElement('link')
          Object.assign(rss, {
            id: 'rss',
            href: `${this.website}/api/0.3/issues.rss?${this.query}`,
            rel: 'alternate',
            type: 'application/rss+xml',
            title: document.title,
          })
          document.head.appendChild(rss)
        }
      )
    },

    show_more(): void {
      var query = Object.assign({}, this.$route.query)
      query.limit = this.limit ? this.limit * 5 : 500
      this.$router.push({ name: this.$route.name, query })
    },

    showMoreAnalyser(): void {
      this.showAnalyserCount = Math.min(
        this.showAnalyserCount * 2,
        this.errors_groups.length
      )
    },

    count_extra_filter_number(): void {
      this.extra_filter_number =
        (this.source ? 1 : 0) +
        (this.class_ || this.class_ === 0 || this.class_ === '0' ? 1 : 0) +
        (this.tags ? 1 : 0) +
        (this.useDevItem ? 1 : 0) +
        (this.username ? 1 : 0) +
        (this.bbox ? 1 : 0) +
        (this.fixable ? 1 : 0)
    },
  },
})
</script>

<style scoped>
a.badge:visited {
  color: #fff; /* Unclicked color for bootstrap badge-secondary */
}
input[type='text'] {
  width: 100%;
}
.buttons {
  align-content: end;
}
#errors-list select {
  width: 100%;
}
</style>
