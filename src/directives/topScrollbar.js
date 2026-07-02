/**
 * v-top-scrollbar 指令
 * 在 el-table 上方插入同步横向滚动条；仅当表格有横向溢出时才显示。
 */
export const vTopScrollbar = {
  mounted(el) {
    const getWrapper = () =>
      el.querySelector('.el-table__body-wrapper') ||
      el.querySelector('.el-scrollbar__wrap')

    const wrapper = getWrapper()
    if (!wrapper) return

    // 顶部滚动条容器（初始隐藏）
    const bar = document.createElement('div')
    bar.className = 'v-top-scrollbar'
    bar.style.cssText =
      'overflow-x:auto;overflow-y:hidden;height:8px;margin-bottom:2px;display:none;'

    const inner = document.createElement('div')
    inner.style.cssText = 'height:1px;'
    bar.appendChild(inner)

    el.parentNode.insertBefore(bar, el)

    // 同步宽度，并决定是否显示
    const syncWidth = () => {
      const tableEl = el.querySelector('.el-table__body table') ||
                      el.querySelector('table')
      const scrollW = tableEl ? tableEl.scrollWidth : wrapper.scrollWidth
      const clientW = wrapper.clientWidth
      inner.style.width = scrollW + 'px'
      // 只在有溢出时显示
      bar.style.display = scrollW > clientW + 2 ? 'block' : 'none'
    }

    // 双向同步滚动
    let syncing = false
    bar.addEventListener('scroll', () => {
      if (syncing) return
      syncing = true
      wrapper.scrollLeft = bar.scrollLeft
      requestAnimationFrame(() => { syncing = false })
    })
    wrapper.addEventListener('scroll', () => {
      if (syncing) return
      syncing = true
      bar.scrollLeft = wrapper.scrollLeft
      requestAnimationFrame(() => { syncing = false })
    })

    const ro = new ResizeObserver(syncWidth)
    ro.observe(el)
    syncWidth()

    el._topScrollbar = { bar, ro }
  },

  unmounted(el) {
    if (el._topScrollbar) {
      el._topScrollbar.ro.disconnect()
      el._topScrollbar.bar.remove()
      delete el._topScrollbar
    }
  }
}
