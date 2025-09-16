<template>
  <div>
    <vue-topprogress ref="topProgress"></vue-topprogress>
    <div v-if="error">{{ error }}</div>
    <div v-else-if="errors">
      <sorted-table
        :values="sortable(errors)"
        class="table table-striped table-bordered table-hover table-sm"
      >
        <thead class="thead-dark">
          <tr>
            <th scope="col" title="source">
              <sort-link name="source_id">
                <translate>source</translate>
              </sort-link>
            </th>
            <th scope="col" title="level">
              <sort-link name="level">
                <translate
                  translate-comment="TRANSLATORS: this should be replaced by a abbreviation for 'level'"
                >
                  lvl
                </translate>
              </sort-link>
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
            <th scope="col" :title="$t('information on issue')">E</th>
            <th scope="col" :title="$t('location')">
              <translate
                translate-comment="TRANSLATORS: this should be replaced by a abbreviation for 'location'"
              >
                loc
              </translate>
            </th>
            <th scope="col">
              <translate
                translate-comment="TRANSLATORS: this should be replaced by a abbreviation for 'elements'"
              >
                elms
              </translate>
            </th>
            <th scope="col">
              <sort-link name="subtitle_or_title">
                <translate>subtitle</translate>
              </sort-link>
            </th>
            <th v-if="opt_date" scope="col">
              <sort-link name="date"><translate>date</translate></sort-link>
            </th>
            <th
              v-if="!gen || gen === 'open'"
              :title="$t('False positive / Done')"
            >
              ✘/✔
            </th>
            <th v-if="gen == 'false'" :title="$t('delete issue')">✘</th>
          </tr>
        </thead>
        <template #body="sort">
          <tbody>
            <tr v-for="res in sort.values" :key="res.uuid">
              <td :title="`${res.country}-${res.analyser}`">
                <router-link :to="`?${page_args}source=${res.source_id}`">
                  {{ res.source_id }}
                </router-link>
              </td>
              <td>{{ res.level }}</td>
              <td>
                <img :src="getMakerImgSrc(res)" :alt="res.item" />
                <router-link :to="`?${page_args}item=${res.item}`">
                  {{ res.item }}
                </router-link>
                <span v_if="res.menu">{{ res['menu'] }}</span>
              </td>
              <td>{{ res.class }}</td>
              <td :title="$t('issue n°') + res.uuid">
                <router-link
                  :to="`../${'false' == gen ? 'false-positive' : 'issue'}/${
                    res.uuid
                  }`"
                >
                  E
                </router-link>
              </td>
              <td>
                <router-link
                  v-if="res.lat !== undefined && res.lon !== undefined"
                  :to="`/map/#${query}&amp;item=${res.item}&amp;zoom=17&amp;lat=${res.lat}&amp;lon=${res.lon}&amp;level=${res.level}&tags=&fixable=&issue_uuid=${res.uuid}`"
                >
                  {{ res.lon.toFixed(2) }}&nbsp;{{ res.lat.toFixed(2) }}
                </router-link>
              </td>
              <td v-if="res.elems">
                <span v-for="e in res.elems" :key="e.id">
                  <a
                    target="_blank"
                    :href="`${main_website}${e.type_long}/${e.id}`"
                    >{{ e.type.toLocaleLowerCase() }}{{ e.id }}</a
                  >&nbsp;<a
                    v-if="e.type === 'R'"
                    title="josm"
                    :href="`http://localhost:8111/import?url=${remote_url_read}api/0.6/relation/${e.id}/full`"
                    target="hiddenIframe"
                    @click="onJosmRelation(res)"
                  >
                    (j)
                  </a>
                  <a
                    v-else
                    title="josm"
                    :href="`http://localhost:8111/load_object?objects=${e.type.toLocaleLowerCase()}${
                      e.id
                    }`"
                    target="hiddenIframe"
                  >
                    (j)
                  </a>
                </span>
              </td>
              <td v-else>
                <a
                  :href="`http://localhost:8111/load_and_zoom?left=${
                    res.lon - 0.002
                  }&amp;bottom=${res.lat - 0.002}&amp;right=${
                    res.lon + 0.002
                  }&amp;top=${res.lat + 0.002}`"
                >
                  josm
                </a>
              </td>
              <td>{{ res.subtitle_or_title }}</td>
              <td v-if="opt_date">
                {{ res.date.substring(0, 10) }}&nbsp;{{
                  res.date.substring(11, 16)
                }}
              </td>
              <td v-if="!gen || gen === 'open'">
                <a
                  :id="`GET=issue/${res.uuid}/false`"
                  href="#"
                  :title="
                    $t('Mark issue #{uuid} as false positive', {
                      uuid: res.uuid,
                    })
                  "
                  @click.stop.prevent="setFalsePositive(res.uuid, $event)"
                >
                  ✘ </a
                >/
                <a
                  :id="`GET=issue/${res.uuid}/done`"
                  href="#"
                  :title="$t('Mark issue #{uuid} as fixed', { uuid: res.uuid })"
                  @click.stop.prevent="issue_action"
                >
                  ✔
                </a>
              </td>
              <td
                v-if="gen == 'false'"
                :title="$t('delete issue #{uuid}', { uuid: res.uuid })"
              >
                <a
                  :id="`DELETE=false-positive/${res.uuid}`"
                  href="#"
                  @click.stop.prevent="issue_action"
                >
                  ✘
                </a>
              </td>
            </tr>
          </tbody>
        </template>
      </sorted-table>
      <iframe id="hiddenIframe" name="hiddenIframe"></iframe>
    </div>
  </div>
</template>

<script lang="ts">
import { FeatureCollection, Feature, Point } from 'geojson'

import confirmFalsePositive from './confirmFalsePositive.vue'
import VueParent from '../pages/Parent.vue'

interface Issue {
  uuid: string
  country: string
  analyser: string
  source_id: number
  item: number
  class: number
  level: number
  menu: string
  lat: number
  lon: number
  elems: { id: number; type: string; type_long: string }[]
  date: string
  subtitle?: string
  title?: string
  subtitle_or_title?: string
}

export default VueParent.extend({
  mixins: [confirmFalsePositive],

  data(): {
    error: boolean
    errors: boolean
  } {
    return {
      error: undefined,
      errors: false,
    }
  },

  props: {
    query: {
      type: String,
      required: true,
    },
    gen: {
      type: String,
      default: null,
    },
    opt_date: {
      type: String,
      default: false,
    },
    main_website: {
      type: String,
      required: true,
    },
    remote_url_read: {
      type: String,
      required: true,
    },
    page_args: {
      type: String,
      required: true,
    },
  },

  computed: {
    api_url: () => API_URL,
  },

  watch: {
    query() {
      this.render()
    },
    page_args() {
      this.render()
    },
  },

  mounted() {
    this.render()
  },

  methods: {
    render() {
      this.fetchJsonProgress(
        `${API_URL}/api/0.3/issues.geojson?full=true&${this.page_args}${this.query}`,
        (json: FeatureCollection) => {
          this.errors = json.features
            .filter((feature) => feature.geometry.type === 'Point')
            .map((feature: Feature<Point>) => {
              const ret = feature.properties || {}
              ret.lon = feature.geometry.coordinates[0]
              ret.lat = feature.geometry.coordinates[1]
              return ret
            })
          this.$emit('count', this.errors.length)
        }
      )
    },

    sortable(issues: Issue[]): Issue[] {
      return issues.map((issue) => {
        issue.subtitle_or_title = issue.subtitle || issue.title || ''
        return issue
      })
    },

    onJosmRelation(issue: Issue) {
      fetch(
        `http://localhost:8111/zoom?left=${issue.lon - 0.002}&bottom=${
          issue.lat - 0.002
        }&right=${issue.lon + 0.002}&top=${issue.lat + 0.002}`
      ).then()
      return true
    },

    getMakerImgSrc(issue: Issue) {
      return API_URL + `/api/0.3/assets/markers/marker-l-${issue.item}.png`
    },

    issue_action(event: MouseEvent) {
      const container: HTMLElement = event.currentTarget?.parentElement
      const id = event.currentTarget?.id.split('=')
      const verb = id[0]
      const path = id[1]

      container.parentElement.classList = ['delete-row']
      fetch(API_URL + `/api/0.3/${path}`, {
        method: verb,
        cache: 'no-store',
      })
        .then(() => {
          setTimeout(() => {
            container.parentElement.remove()
          }, 1000)
        })
        .catch(() => {
          container.parent().css({ backgroundColor: '' })
        })
    },

    setFalsePositive(uuid: string, event: MouseEvent): void {
      if (this.confirmeFalsePositive(uuid)) {
        this.issue_action(event)
      }
    },
  },
})
</script>

<style>
tr.delete-row td {
  background-color: red;
  transition: all 0.7s linear;
}
</style>
