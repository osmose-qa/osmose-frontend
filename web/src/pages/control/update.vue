<template>
  <div>
    <div v-if="error">{{ error }}</div>
    <table
      v-else
      class="table table-striped table-bordered table-hover table-sm"
    >
      <thead class="thead-dark">
        <tr>
          <th><translate>source</translate></th>
          <th style="min-width: 800px"><translate>remote url</translate></th>
          <th><translate>timestamp</translate></th>
          <th><translate>version</translate></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="res in list" :key="res.timestamp">
          <td>
            <router-link :to="`../../issues/open?source=${res.source_id}`">
              {{ res.source_id }}
            </router-link>
          </td>
          <td>{{ remote(res) }}</td>
          <td>{{ res.timestamp }}</td>
          <td>{{ res.version }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
import VueParent from '../Parent.vue'

interface Update {
  source_id: number
  timestamp: string
  version: string
  remote_url: string
  remote_ip: string
}

export default VueParent.extend({
  data(): {
    error: boolean
    list: Update[]
  } {
    return {
      error: undefined,
      list: [],
    }
  },

  mounted() {
    const source_id = this.$route.params.source_id
    this.fetchJsonProgressAssign(
      API_URL + `/control/update/${source_id}.json` + window.location.search
    )
    document.title = 'Osmose - ' + this.$t('Update')
  },

  methods: {
    remote(res: Update): string {
      var url = res.remote_url
      if (url.startsWith('http://') || url.startsWith('https://')) {
        url = url.split('/')[2]
      } else if (res.remote_ip) {
        url = res.remote_ip
      }
      return url
    },
  },
})
</script>
