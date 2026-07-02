/**
 * v-top-scrollbar 指令
 * 在 el-table 上方插入一个同步横向滚动条，无需滚动到底部即可左右滑动。
 */
export const vTopScrollbar = {
  mounted(el) {
    // el-table 的横向滚动容器
    const getWrapper = () => el.querySelector('.el-table__body-wrapper') ||
                             el.querySelector('.el-scrollbar__wrap')

    const wrapper = getWrapper()
    if (!wrapper) return

    // 顶部滚动条容器
    const bar = document.createElement('div')
    bar.className = 'v-top-scrollbar'
    bar.style.cssText =
      'overflow-x:auto;overflow-y:hidden;height:8px;margin-bottom:2px;'

    // 撑开宽度用的内部空元素
    const inner = document.createElement('div')
    inner.style.cssText = 'height:1px;'
    bar.appendChild(inner)

    // 插到 el-table 上方
    el.parentNode.insertBefore(bar, el)

    // 同步宽度（取表格实际内容宽度）
    const syncWidth = () => {
      const tableEl = el.querySelector('.el-table__body table') ||
                      el.querySelector('table')
      inner.style.width = tableEl
        ? tableEl.scrollWidth + 'px'
        : wrapper.scrollWidth + 'px'
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

    // 监听表格尺寸变化，更新滚动条宽度
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
