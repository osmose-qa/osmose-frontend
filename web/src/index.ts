import 'nprogress/nprogress.css'

import numeral from 'numeral'
import Vue from 'vue'
import numFormat from 'vue-filter-number-format'
import SortedTablePlugin from 'vue-sorted-table'

import App from './app.vue'
import TranslateSlot from './components/translate-slot.vue'
import Translate from './components/translate.vue'
import { i18n, loadLanguageAsync } from './i18n'
import { router } from './router'

Vue.use(SortedTablePlugin)
Vue.filter('numFormat', numFormat(numeral))
Vue.component('Translate', Translate)
Vue.component('TranslateSlot', TranslateSlot)

document.addEventListener('DOMContentLoaded', () => {
  router.beforeEach((to, from, next) => {
    const lang = to.params.lang
    loadLanguageAsync(lang).then(() => next())
  })

  new Vue({
    el: '#app',
    router,
    i18n,
    render: (h) => h(App),
  })
})
