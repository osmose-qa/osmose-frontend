<template>
  <div id="doc">
    <div v-if="error">{{ error }}</div>

    <div v-if="welcome">
      <h5><translate>Welcome to Osmose-QA</translate></h5>
      <p>
        <translate>
          Osmose-QA is a quality assurance tool that detects issues in
          OpenStreetMap data.
        </translate>
      </p>
      <p>
        <translate>
          It detects a very wide range of issue types. It is also useful for
          integrating third-party data sets by conflation.
        </translate>
      </p>
      <p>
        <translate>
          Feel free to report any problem, idea or new open data you want to add
          to Osmose on our Github:
        </translate>
        <a href="https://github.com/osmose-qa" target="_blank"
          >Osmose-QA</a
        >
      </p>
      <p>
        <translate>
          In no case does Osmose-QA tell you the absolute right way to map.
          Always keep a critical eye.
        </translate>
      </p>
      <p>
        <translate> You can find help on the wiki: </translate>
        <a href="https://wiki.openstreetmap.org/wiki/Osmose" target="_blank">
          wiki.osm.org/Osmose
        </a>
      </p>
    </div>

    <div v-else>
      <h5>ℹ {{ title }}</h5>

      <template v-if="detail">
        <p v-html="detail"></p>
      </template>

      <template v-if="fix">
        <h6>✅ <translate>How to Fix</translate></h6>
        <p v-html="fix"></p>
      </template>

      <template v-if="trap">
        <h6>❌ <translate>Trap to avoid</translate></h6>
        <p v-html="trap"></p>
      </template>

      <template v-if="example">
        <h6><translate>Example</translate></h6>
        <p v-html="example"></p>
      </template>

      <h6>👁️ <translate>Hide markers</translate></h6>
      <p>
        <translate-slot>
          <span translate>Do not want to see {title} markers?</span>
          <template #title>
            <i>{{ title }}</i>
          </template>
        </translate-slot>
      </p>
      <button
        class="mb-3 btn btn-info btn-sm"
        @click.stop.prevent="$emit('hide-item-markers', item)"
      >
        <translate>Hide from map</translate>
      </button>

      <template v-if="source_link">
        <h6>🔗 <translate>Source Code</translate></h6>
        <p>
          <a :href="source_link" target="_blank">{{ source_title }}</a>
        </p>
      </template>

      <template v-if="resource_link">
        <h6>🔗 <translate>Resource used</translate></h6>
        <p>
          <a :href="resource_link" target="_blank">{{ resource_title }}</a>
        </p>
      </template>

      <div id="doc_bottom">
        <p>
          <translate>Want to improve this control or this doc?</translate>
          <a
            href="https://wiki.openstreetmap.org/wiki/Osmose#Help_and_issues_description"
            target="_blank"
          >
            wiki.osm.org/Osmose#Help
          </a>
        </p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { marked } from 'marked'
import { PropType } from 'vue'

import VueParent from '../Parent.vue'

export default VueParent.extend({
  props: {
    itemClass: {
      type: Array as PropType<string[]>,
      default: null,
    },
  },

  data(): {
    error: boolean
    welcome: boolean
    title?: string
    detail?: string
    fix?: string
    trap?: string
    example?: string
    source_link?: string
    resource_link?: string
    item?: number
  } {
    return {
      error: undefined,
      welcome: true,
      title: null,
      detail: null,
      fix: null,
      trap: null,
      example: null,
      source_link: null,
      resource_link: null,
      item: null,
    }
  },

  watch: {
    $route(to, from): void {
      if (
        typeof this._last_item !== 'undefined' &&
        to.params.lang != from.params.lang
      ) {
        this.setDoc(this._last_item, this._last_classs)
      }
    },

    itemClass(): void {
      if (this.itemClass) {
        this.setDoc(this.itemClass[0], this.itemClass[1])
      }
    },
  },

  mounted(): void {
    if (this.itemClass) {
      this.setDoc(this.itemClass[0], this.itemClass[1])
    }
  },

  methods: {
    basename(path: string): string {
      return path.split(/[\\/]/).pop()
    },

    setDoc(item: number, classs: string): void {
      if (
        item == this._last_item &&
        classs == this._last_classs &&
        this.$route.params.lang == this._last_lang
      ) {
        return
      }

      this.fetchJson(
        API_URL + `/api/0.3/items/${item}/class/${classs}?langs=auto`,
        (response) => {
          this._last_lang = this.$route.params.lang
          this._last_item = item
          this._last_classs = classs

          this.welcome = false

          const data = response.categories[0].items[0].class[0]

          var resource_url
          try {
            if (data.resource) {
              resource_url = new URL(data.resource)
            }
          } catch {
            // Ignore error
          }

          this.title = data.title && data.title.auto
          this.detail = data.detail && marked.parse(data.detail.auto)
          this.fix = data.fix && marked.parse(data.fix.auto)
          this.trap = data.trap && marked.parse(data.trap.auto)
          this.example = data.example && marked.parse(data.example.auto)
          this.source_link = data.source
          this.source_title = data.source && this.basename(data.source)
          this.resource_link = data.resource
          this.resource_title = resource_url
            ? `${resource_url.protocol}//${resource_url.host}`
            : data.resource
          this.item = item
        }
      )
    },
  },
})
</script>

<style scoped>
#doc {
  padding: 8px 24px;
}

#doc > div {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

#doc_bottom {
  opacity: 0.5;
  margin-top: auto;
}
</style>
