import { createStore } from 'vuex'

export default createStore({
    state: {
        editableTabsValue: '/index',
        editableTabs: [{
            title: '首页',
            name: '/index',
        }],
    },
    mutations: {
        ADD_TABS(state, tab) {
            if (state.editableTabs.findIndex(item => item.name === tab.name) === -1) {
                state.editableTabs.push({
                    title: tab.name,
                    name: tab.path
                })
            }
            state.editableTabsValue = tab.path
        },
        RESET_TAB(state) {
            state.editableTabsValue = '/index'
            state.editableTabs = [{
                title: '首页',
                name: '/index',
            }]
        }
    }
})