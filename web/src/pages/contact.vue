<template>
  <div>
    <h1><translate>Bug tracker</translate></h1>
    <p>
      <translate-slot>
        <span translate>
          Bug should be reported on {osmose-frontend} for issues around the
          website, or on {osmose-backend} for issues on the reported issues on
          OSM data, or for suggestion about analyses.
        </span>
        <template #osmose-frontend>
          <a href="https://github.com/osmose-qa/osmose-frontend/issues">
            osmose-frontend
          </a>
        </template>
        <template #osmose-backend>
          <a href="https://github.com/osmose-qa/osmose-backend/issues">
            osmose-backend
          </a>
        </template>
      </translate-slot>
    </p>

    <h1><translate>Providing patches</translate></h1>
    <p>
      <translate>
        Patches can be provided via merge requests on Github. This is the
        preferred way of handling patches.
      </translate>
    </p>
    <ul>
      <li>
        <a href="https://github.com/osmose-qa/osmose-backend">backend</a>
      </li>
      <li>
        <a href="https://github.com/osmose-qa/osmose-frontend">frontend</a>
      </li>
    </ul>

    <h1><translate>Development</translate></h1>
    <p>
      <translate-slot>
        <span translate>
          Development of Osmose is made as free software by {volunteers}.
        </span>
        <template #volunteers>
          <router-link to="copyright">
            <translate>volunteers</translate>
          </router-link>
        </template>
      </translate-slot>
    </p>
    <p>
      <translate>
        Adding new functionality of "Osmose Editor", initial support of mobile
        device and improvement of documentation was funded by region of
        Aquitaine, France; part of the OpenAquiMap project leading by "Les
        Petits Débrouillards d'Aquitaine".
      </translate>
    </p>
    <p>
      <translate>
        The servers analysing data are provided by OpenStreetMap-France and some
        others by contributors around the world. The servers for North America
        and other areas are funded by Mapbox.
      </translate>
    </p>
    <img
      src="~../../static/images/logo-aquitaine.png"
      alt="Logo of region of Aquitaine"
      width="340"
      height="100"
    />
    <img
      src="~../../static/images/logo-mapbox.png"
      alt="Logo of Mapbox"
      width="340"
      height="100"
    />

    <h1><translate>Contacting maintainers</translate></h1>
    <p>
      <translate-slot>
        <span translate>
          We can be contacted through a direct email to {email}.
        </span>
        <template #email>
          <a href="mailto:osmose-contact@openstreetmap.fr">
            osmose-contact@openstreetmap.fr
          </a>
        </template>
      </translate-slot>
    </p>
    <p>
      <translate-slot>
        <span translate>
          Keep in touch by watching at {twitter} on Twitter or at {mastodon} on
          Mastodon.
        </span>
        <template #twitter>
          <a href="https://twitter.com/osmose_qa">@osmose_qa</a>
        </template>
        <template #mastodon>
          <a href="https://en.osm.town/@OsmoseQA">@OsmoseQA@en.osm.town</a>
        </template>
      </translate-slot>
    </p>
    <p>
      <translate-slot>
        <span translate>
          Chat with Osmose-QA developers and community at {matrix} on Matrix.
        </span>
        <template #matrix>
          <a href="https://matrix.to/#/#osm-osmose:matrix.org">
            #osm-osmose:matrix.org
          </a>
        </template>
      </translate-slot>
    </p>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  mounted(): void {
    document.title = 'Osmose - ' + this.$t('Contact')
  },
})
</script>
