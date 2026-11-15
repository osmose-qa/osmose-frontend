<template>
  <div v-if="Object.keys(state).length > 0" id="tests">
    <div id="action_links">
      <translate>Select:</translate>
      <a href="#" @click.stop.prevent="toggle_all(true)">
        <translate>all</translate>
      </a>
      <a href="#" @click.stop.prevent="toggle_all(false)">
        <translate>nothing</translate>
      </a>
      <a href="#" @click.stop.prevent="toggle_all(-1)">
        <translate>invert</translate>
      </a>
    </div>

    <div v-for="categ in categories_format" :key="categ.id" class="test_group">
      <h1>
        <a href="#" @click.stop.prevent="toggle_categorie_block(categ.id)">
          <i class="toggleCategIco"></i>
          {{ categ.title.auto }}
        </a>
        <span class="count">
          {{ count_items[categ.id] }}/{{ total_items[categ.id] }}
        </span>
        <a href="#" @click.stop.prevent="toggle_categorie(categ.id, true)">
          <translate>all</translate>
        </a>
        <a href="#" @click.stop.prevent="toggle_categorie(categ.id, false)">
          <translate>nothing</translate>
        </a>
      </h1>

      <ul :id="`categorie_block_${categ.id}`">
        <li
          v-for="item in categ.items"
          :key="item.item"
          class="item"
          :title="item.class_format"
          :style="showItem(item) ? '' : 'display:none'"
        >
          <div :class="`marker-l marker-l-${item.item}`"></div>
          <div class="level">
            <template v-for="level in 3">
              <div
                v-if="item.levels_format[level]"
                :key="level"
                :class="`severity-level-${level} ${
                  active_levels.indexOf(level.toString()) >= 0 ? '' : 'disabled'
                }`"
              >
                <span>{{ item.levels_format[level] }}</span>
              </div>
              <div v-else :key="level"></div>
            </template>
          </div>
          <input
            v-model="item.selected"
            type="checkbox"
            @change="toggle_item(item.item, item.selected)"
          />
          <router-link target="_blank" :to="`../issues/open?item=${item.item}`">
            {{ item.title.auto }}
          </router-link>
          <span v-if="item.class.length > 1">
            <span
              v-if="class_detail_open == item.item"
              @click="class_detail_open = undefined"
              class="class_detail"
            >
              -
            </span>
            <span
              v-else
              @click="class_detail_open = item.item"
              class="class_detail"
            >
              +
            </span>
          </span>
          <div v-if="class_detail_open == item.item">
            <ul>
              <li v-for="classs in item.class" :key="classs.class">
                <a
                  href=""
                  @click.prevent="set_item_class(item.item, classs.class)"
                >
                  ⌖ {{ classs.class }} {{ classs.title.auto }}
                </a>
              </li>
            </ul>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import _ from 'lodash'
import Vue, { PropType } from 'vue'

import { ItemState, Category, Levels, Item } from '../../types'

export default Vue.extend({
  props: {
    categories: {
      type: Array as PropType<Category[]>,
      required: true,
    },
    item_levels: {
      type: Object as PropType<{ [level: number]: number[] }>,
      required: true,
    },
    itemState: {
      type: Object as PropType<ItemState>,
      required: true,
    },
  },

  data(): {
    active_levels: Levels
    total_items: { [category: number]: number }
    count_items: { [category: number]: number }
    state: ItemState
    class_detail_open: number | undefined
  } {
    return {
      active_levels: ['1', '2', '3'],
      total_items: {},
      count_items: {},
      state: Object.assign({}, this.itemState),
      class_detail_open: undefined,
    }
  },

  computed: {
    categories_format(): { [category: number]: number } {
      return this.categories.map((categorie: Category) => {
        this.total_items[categorie.id] = categorie.items.length
        categorie.items = categorie.items.map((item: Item) => {
          item.item_format = ('000' + item.item).slice(-4)
          item.class_format =
            this.$t('Item #{item}', { item: item.item_format }) +
            '\n' +
            item.class.map((c) => c.class + '. ' + c.title.auto).join('\n')
          item.levels_format = {}
          item.levels.forEach((level) => {
            item.levels_format[level.level] = level.count
          })
          return item
        })
        return categorie
      })
    },
  },

  watch: {
    categories(): void {
      this.set_item(this.state)
    },

    state: {
      deep: true,
      handler(): void {
        this.$emit('state-update', Object.assign({}, this.state))
      },
    },

    itemState: {
      deep: true,
      handler(): void {
        if (!_.isEqual(this.itemState, this.state)) {
          this.state = Object.assign({}, this.itemState)
          this.set_item(this.state)
        }
      },
    },
  },

  methods: {
    _select_items_loop(
      callback: (item: Item) => boolean,
      categ_id: number
    ): void {
      this.categories.forEach((categorie: Category) => {
        if (!categ_id || categorie.id == categ_id) {
          this.count_items[categorie.id] = 0
          categorie.items.forEach((item) => {
            if (callback) {
              item.selected = callback(item)
            }
            if (item.selected) {
              this.count_items[categorie.id]++
            }
          })
        }
      })
    },

    set_item(newState): void {
      const itemRegex = newState.item
        .split(',')
        .filter((item) => item != '')
        .map((item) => new RegExp(item.replace(/x/g, '.')))
      this._select_items_loop((item: Item) =>
        itemRegex.some((regex) => regex.test(('000' + item.item).slice(-4)))
      )
      this.$forceUpdate()
    },

    showItem(item: Item): boolean | string {
      return (
        this.item_levels[this.state.level].indexOf(item.item) >= 0 &&
        (!this.state.tags ||
          (item.tags && item.tags.indexOf(this.state.tags) >= 0))
      )
    },

    toggle_all(how: boolean | -1): void {
      this._select_items_loop((item: Item) =>
        how === -1 ? !item.selected : how
      )
      this.$forceUpdate()
      this.itemsChanged()
    },

    toggle_categorie(categ_id: number, how: (item: Item) => boolean): void {
      this._select_items_loop(() => how, categ_id)
      this.$forceUpdate()
      this.itemsChanged()
    },

    toggle_item(item_id: number, selected: boolean): void {
      this._select_items_loop((item: Item) =>
        item.item === item_id ? selected : item.selected
      )
      this.$forceUpdate()
      this.itemsChanged()
    },

    set_item_class(item_id: number, class_id: number): void {
      this._select_items_loop((item: Item) => item.item === item_id)
      this.state.class = class_id
      this.$forceUpdate()
      this.itemsChanged()
    },

    toggle_categorie_block(categ_id: number): void {
      const block = document.getElementById(`categorie_block_${categ_id}`)
      block.style.height = block.style.height == '0px' ? '' : '0px'
    },

    itemsChanged(): void {
      var full_categ = 0
      var item_mask = this.categories
        .filter((categorie: Category) => this.count_items[categorie.id] > 0)
        .map((categorie: Category) => {
          if (
            this.total_items[categorie.id] == this.count_items[categorie.id]
          ) {
            full_categ++
            return `${categorie.id / 10}xxx`
          } else {
            return categorie.items
              .filter((item) => item.selected)
              .map((item) => item.item_format)
              .join(',')
          }
        })
        .join(',')
      if (full_categ == this.categories.length) {
        item_mask = 'xxxx'
      }
      this.state.item = item_mask
    },
  },
})
</script>

<style scoped>
div#action_links {
  text-align: center;
}

@media (hover: none) {
  div#action_links {
    font-size: inherit;
  }
}

div.test_group img {
  margin-left: 20px;
}
div.test_group h1 {
  font-size: 12px;
  margin: 0px;
  margin-top: 5px;
}
@media (hover: none) {
  div.test_group h1 {
    font-size: 100%;
  }
}
div.test_group h1 i.toggleCategIco {
  display: inline-block;
  background: url('~../../../static/images/folder_open.png');
  width: 16px;
  height: 16px;
  margin: 2px 2px 0 2px;
}
div.test_group h1.folded i.toggleCategIco {
  background: url('~../../../static/images/folder.png');
}

div.test_group ul {
  list-style-type: none;
  margin: 0px;
  padding-left: 0px;
  padding-right: 0px;
  overflow: hidden;
  transition: height 1s ease-in-out 1s;
}

div.test_group li {
  padding-left: 2px;
  padding-right: 2px;
}

div.test_group li div.marker-l {
  display: inline-block;
  width: 12px;
  height: 12px;
}

@media (hover: none) {
  div.test_group li {
    font-size: inherit;
  }
}

div.test_group li input {
  margin: 3px 3px 3px 4px;
}

div.test_group li:hover {
  background-color: #ffc;
}

span#level-span {
  white-space: nowrap;
}

/* error levels */
div.test_group div.level {
  float: right;
  width: 48px;
  height: 16px;
}

html[dir='rtl'] div.test_group div.level {
  float: left;
}

div.test_group div.level div {
  width: 16px;
  height: 16px;
  display: inline-block;
}
div.test_group div.level div span {
  display: none;
}
div.test_group div.level div:hover span {
  display: block;
  padding: 5px;
  z-index: 20;
  overflow: visible;
}

.class_detail {
  cursor: pointer;
}
</style>
