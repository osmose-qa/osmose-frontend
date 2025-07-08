<template>
  <div>
    <h1><translate>How to help translation</translate></h1>
    <p>
      <translate>
        Osmose tool is mainly developped by french people, and we aim to add
        more languages.
      </translate>
    </p>
    <p>
      <translate>
        To make Osmose a real multi-lingual tool, we need your help to improve
        current translations, and add new translations
      </translate>
    </p>

    <h2><translate>Pages to translate</translate></h2>
    <h3><translate>Osmose pages</translate></h3>
    <ul>
      <li>
        <translate-slot>
          <span translate>Translation is done on {Weblate}</span>
          <template #Weblate>
            <a href="https://hosted.weblate.org/engage/osmose/">Weblate</a>
          </template>
        </translate-slot>
      </li>
    </ul>
    <div style="transifex-chart">
      <a
        target="_blank"
        style="text-decoration: none; color: black; font-size: 66%"
        href="https://hosted.weblate.org/projects/osmose/"
        title="See more information on Weblate"
      >
        <translate>Translation progress: osmose</translate>
      </a>
      <br />
      <a target="_blank" href="https://hosted.weblate.org/engage/osmose/">
        <img
          border="0"
          src="https://hosted.weblate.org/widget/osmose/open-graph.png"
        />
      </a>
      <br />
      <a target="_blank" href="https://hosted.weblate.org/engage/osmose/">
        <img
          border="0"
          src="https://hosted.weblate.org/widget/osmose/multi-auto.svg"
        />
      </a>
    </div>

    <h3><translate>Wiki pages</translate></h3>
    <ul>
      <li>
        <a :href="$t('http://wiki.openstreetmap.org/wiki/Osmose')">
          <translate>Osmose QA main page</translate>
        </a>
      </li>
    </ul>

    <h2><translate>For new language or countries</translate></h2>
    <ul>
      <li>
        <translate-slot>
          <span translate>
            You can create a new language directly on {Weblate}.
          </span>
          <template #Weblate>
            <a href="https://hosted.weblate.org/engage/osmose/">Weblate</a>
          </template>
        </translate-slot>
      </li>
      <li>
        <translate-slot>
          <span translate>
            For new countries, we can be contacted through a direct email to
            {email}.
          </span>
          <template #email>
            <a href="mailto:osmose-contact@openstreetmap.fr">
              osmose-contact@openstreetmap.fr
            </a>
          </template>
        </translate-slot>
      </li>
    </ul>

    <h2><translate>Bug tracking system</translate></h2>
    <ul>
      <li>
        <translate-slot>
          <span translate>
            {osmose-frontend} can be used to report any issue with translations.
          </span>
          <template #osmose-frontend>
            <a href="https://github.com/osmose-qa/osmose-frontend/issues">
              osmose-frontend
            </a>
          </template>
        </translate-slot>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  mounted(): void {
    document.title = 'Osmose - ' + this.$t('How to help translation')
  },
})
</script>
