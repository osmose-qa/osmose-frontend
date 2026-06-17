<template>
  <div>
    <div v-if="error">{{ error }}</div>
    <div v-else>
      <nav
        class="navbar navbar-expand-sm navbar-expand-md navbar-expand-lg navbar-dark"
        style="background-color: #212529"
      >
        <span class="navbar-brand">
          <translate :params="{ users: users.join(', ') }">
            User statistics for {users}
          </translate>
        </span>

        <div class="collapse navbar-collapse">
          <ul class="navbar-nav">
            <li class="nav-item">
              <router-link class="nav-link" :to="nav_link">
                <translate>Map</translate>
              </router-link>
            </li>
          </ul>
          <div class="form-inline my-2 my-lg-0">
            <a :href="byuser_count" class="badge badge-secondary">
              .rss <translate>count</translate> </a
            >&nbsp;
            <a :href="api_url_path('rss')" class="badge badge-secondary">
              .rss </a
            >&nbsp;
            <a :href="api_url_path('gpx')" class="badge badge-secondary">
              .gpx </a
            >&nbsp;
            <a :href="api_url_path('kml')" class="badge badge-secondary">
              .kml </a
            >&nbsp;
            <a :href="api_url_path('csv')" class="badge badge-secondary">
              .csv </a
            >&nbsp;
            <a :href="api_url_path()" class="badge badge-secondary"> .json </a
            >&nbsp;
            <a
              :href="api_url_path(undefined, 'full=true')"
              class="badge badge-secondary"
            >
              .json full </a
            >&nbsp;
            <a :href="api_url_path('geojson')" class="badge badge-secondary">
              .geojson </a
            >&nbsp;
            <a
              :href="api_url_path('geojson', 'full=true')"
              class="badge badge-secondary"
            >
              .geojson full
            </a>
          </div>
        </div>
      </nav>
      <br />

      <p>
        <translate :params="{ users: users.join('\', \'') }">
          This page shows issues on elements that were last modified by
          '{users}'. This doesn't mean that this user is responsible for all
          these issues.
        </translate>
      </p>
      <p v-if="count !== undefined">
        <span v-if="count < 500">
          <translate :params="{ count: count }">
            Number of found issues: {count}
          </translate>
        </span>
        <span v-else>
          <translate :params="{ count: count }">
            Number of found issues: more than {count}
          </translate>
        </span>
      </p>

      <issues-list
        v-if="username"
        :query="query"
        :main_website="main_website"
        :remote_url_read="remote_url_read"
        :page_args="`username=${username}&`"
        @count="setCount"
      />
    </div>
  </div>
</template>

<script lang="ts">
import IssuesList from '../../components/issues-list.vue'
import VueParent from '../Parent.vue'

export default VueParent.extend({
  data(): {
    users: string[]
    username: string
    count?: number
    main_website: string
    query: string
  } {
    return {
      users: [],
      username: '',
      count: undefined,
      main_website: '',
      query: '',
    }
  },

  computed: {
    nav_link(): string {
      const params = new URLSearchParams(this.query)
      params.set('username', this.username)
      return `../map/#${params.toString()}`
    },
    byuser_count(): string {
      return (
        `${API_URL}${window.location.pathname}`.replace(
          '/byuser/',
          '/byuser_count/'
        ) + `.rss?${this.query}`
      )
    },
  },

  components: {
    IssuesList,
  },

  watch: {
    $route() {
      this.render()
    },
  },

  mounted() {
    this.username = this.$route.params.user
    this.users = this.username.split(',')
    this.render()
  },

  methods: {
    api_url_path(format: string, query: string): string {
      return `${this.website}/api/0.3/issues${format ? '.' + format : ''}?${
        this.query
      }&username=${this.username}${query ? '&' + query : ''}`
    },

    render(): void {
      this.query = window.location.search.substring(1)

      this.fetchJsonProgressAssign(
        API_URL + window.location.pathname + '.json' + window.location.search,
        () => {
          document.title =
            'Osmose - ' +
            this.$t('Statistics for user {user}', {
              user: this.users.join(', '),
            })

          var rss = document.getElementById('rss')
          if (rss) {
            rss.remove()
          }
          rss = document.createElement('link')
          Object.assign(rss, {
            id: 'rss',
            href: this.api_url_path('rss'),
            rel: 'alternate',
            type: 'application/rss+xml',
            title: document.title,
          })
          document.head.appendChild(rss)
        }
      )
    },

    setCount(count: number) {
      this.count = count
    },
  },
})
</script>

<style scoped>
a.badge:visited {
  color: #fff; /* Unclicked color for bootstrap badge-secondary */
}
</style>
