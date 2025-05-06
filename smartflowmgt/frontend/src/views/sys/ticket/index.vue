<template>
    <div class="app-container">

        <el-row :gutter="20" class="header">
            <el-col :span="7">
                <el-input placeholder="请输入工单号或关键字..." v-model="queryForm.query" clearable :loading="isSuggestLoading"
                    @input="handleSearch">
                    <template #append>
                        <el-select v-model="searchType" style="width: 120px">
                            <el-option label="全文检索" value="fulltext" />
                            <el-option label="主题" value="title" />
                        </el-select>
                    </template>
                </el-input>
            </el-col>
            <el-button type="success" :icon="DocumentAdd" @click="handleDialogValue()">新增工单</el-button>
            <el-button type="warning" :disabled="multipleSelection.length === 0" @click="handleExport">批量导出</el-button>
        </el-row>

        <el-table :data="tableData" stripe style="width: 100%" @selection-change="handleSelectionChange">
            <el-table-column type="selection" width="55" />
            <el-table-column prop="ticket_code" label="工单号" width="180" align="center" />
            <el-table-column label="工单状态" width="80" align="center">
                <template #default="scope">
                    <el-tag :type="scope.row.status_display === '待处理' ? 'danger' :
            scope.row.status_display === '处理中' ? 'primary' : 'success'">
                        {{ scope.row.status_display }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="title" label="主题" width="100" align="center" />
            <el-table-column prop="desc" label="描述" width="200" align="center" />
            <el-table-column label="附件" width="120" align="center">
                <template #default="scope">
                    <el-link type="primary" :disabled="!scope.row.attachments?.length"
                        @click="handlePreview(scope.row.attachments)">
                        {{ scope.row.attachments?.length || 0 }}个附件
                    </el-link>
                </template>
            </el-table-column>
            <el-table-column label="提出人" width="100" align="center">
                <template #default="scope">
                    {{ findUserById(scope.row.find_user)?.realname || findUserById(scope.row.find_user)?.username }}
                </template>
            </el-table-column>
            <el-table-column label="处理人" width="100" align="center">
                <template #default="scope">
                    {{ findUserById(scope.row.handler)?.realname || findUserById(scope.row.handler)?.username }}
                </template>
            </el-table-column>
            <el-table-column prop="deadline" label="截止时间" width="200" align="center" />
            <el-table-column prop="action" label="操作" width="400" fixed="right" align="center">
                <template v-slot="scope">
                    <el-button type="primary" :icon="Edit" @click="handleDialogValue(scope.row.id)"></el-button>
                    <el-button v-if="scope.row.status_display === '待处理'" type="primary"
                        @click="handleProcess(scope.row.id, 'handling')">
                        开始处理
                    </el-button>
                    <el-button v-else-if="scope.row.status_display === '处理中'" type="success"
                        @click="handleProcess(scope.row.id, 'handled')">
                        完成处理
                    </el-button>
                    <!-- <el-button type="info" @click="handlePreview(scope.row.attachments)">预览附件</el-button> -->
                </template>
            </el-table-column>

        </el-table>
        <el-pagination v-model:current-page="queryForm.pageNum" v-model:page-size="queryForm.pageSize"
            :page-sizes="[10, 20, 30, 40]" layout="total, sizes, prev, pager, next, jumper" :total="total"
            @size-change="handleSizeChange" @current-change="handleCurrentChange" />
        <Dialog v-model="dialogVisible" :dialogVisible="dialogVisible" :id="id" :dialogTitle="dialogTitle"
            @initTicketList="initTicketList"></Dialog>
        <FilePreview v-model="previewVisible" :file-ids="previewFiles" />
    </div>
</template>

<script setup>
import { Search, Delete, DocumentAdd, Edit, Tools, RefreshRight } from '@element-plus/icons-vue'
import { ref, watch, onMounted } from "vue";
import Dialog from './components/dialog.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from "@utils/api"
import FilePreview from '@/components/FilePreview.vue'


const isSuggestLoading = ref(false)
const userList = ref([])
const loadUsers = async () => {
    const res = await api.get("user/list")
    userList.value = res.data.data || []
}

onMounted(() => {
    loadUsers()
    initTicketList()
})

const findUserById = (userId) => {
    return userList.value.find(user => user.id === userId) || {}
}

const previewVisible = ref(false)
const previewFiles = ref([])

const handlePreview = (fileIds) => {
    previewFiles.value = fileIds
    previewVisible.value = true
}

const handleSuggestionClick = (text) => {
    queryForm.value.query = text
    handleSearch()
}

const tableData = ref([])
const total = ref(0)
const queryForm = ref({
    query: '',
    pageNum: 1,
    pageSize: 10
})

const defaultAvatar = new URL('@/assets/default-avatar.png', import.meta.url).href
const squareUrl = defaultAvatar

const dialogVisible = ref(false)

const dialogTitle = ref("")
const id = ref(-1)

const sysRoleList = ref([])



const delBtnStatus = ref(true)

const multipleSelection = ref([])

const handleSelectionChange = (selection) => {
    console.log("勾选了")
    console.log(selection)
    multipleSelection.value = selection;
    delBtnStatus.value = selection.length == 0;
}

const handleDialogValue = (ticketId) => {
    if (ticketId) {
        id.value = ticketId;
        dialogTitle.value = "处理工单"
    } else {
        id.value = -1;
        dialogTitle.value = "新增工单"
    }
    dialogVisible.value = true
}

const initTicketList = async () => {
    const res = await api.post("ticket/search", queryForm.value)
    console.log(res)
    tableData.value = res.data.ticketList
    total.value = res.data.total
}

const initESTicketList = async () => {
    const res = await api.post("ticket/es-search", {
        query: queryForm.value.query,
        page: queryForm.value.pageNum,
        size: queryForm.value.pageSize
    })

    tableData.value = res.data.hits.hits.map(h => ({
        ...h,
        id: h._id,
        ticket_code: h.ticket_code || '无工单号',
        status_display: h.status_display || '未知状态',
        attachments: h.attachments || [],
        title: h.title || '',
        desc: h.desc || '',
        find_user: h.find_user || null,
        handler: h.handler || null,
        deadline: h.deadline || ''
    }))
    total.value = res.data.hits.total.value
}

const handleSizeChange = (pageSize) => {
    queryForm.value.pageSize = pageSize
    queryForm.value.pageNum = 1
    handleSearch()
}

const handleCurrentChange = (pageNum) => {
    queryForm.value.pageNum = pageNum
    handleSearch()
}

const searchType = ref('fulltext')

const debounce = (fn, delay) => {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
};

const handleSearch = debounce(async () => {
    isSuggestLoading.value = true
    try {
        if (!queryForm.value.query.trim()) {
            await initTicketList()
            return
        }
        await (searchType.value === 'fulltext' ? initESTicketList() : initTicketList())
    } finally {
        isSuggestLoading.value = false
    }
}, 300)

const handleProcess = async (ticketId, newStatus) => {
    try {
        await api.put(`/ticket/${ticketId}/status`, { status: newStatus })
        ElMessage.success('状态更新成功')
        initTicketList() // 刷新列表
    } catch (e) {
        ElMessage.error(`状态更新失败: ${e.message}`)
    }
}

const handleExport = () => {
    ElMessageBox.confirm(
        multipleSelection.value.length === tableData.value.length
            ? '当前已全选本页数据，是否导出全部搜索结果？'
            : `确定导出选中的 ${multipleSelection.value.length} 条工单吗？`,
        '导出确认',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        }
    ).then(async () => {
        try {
            const params = {
                ids: multipleSelection.value.map(item => item.id),
                export_all: multipleSelection.value.length === tableData.value.length
            }

            const res = await api.post('ticket/export', params, { responseType: 'blob' })
            const url = window.URL.createObjectURL(new Blob([res.data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', `工单导出_${new Date().toLocaleString()}.xlsx`)
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
            window.URL.revokeObjectURL(url)
            ElMessage.success('导出文件下载完成')
        } catch (e) {
            ElMessage.error(`导出失败: ${e.message}`)
        }
    }).catch(() => { })
}

watch(searchType, (newVal) => {
    if (newVal === 'fulltext' && queryForm.value.query) {
        handleSearch()
    }
})

</script>

<style lang="scss" scoped>
.header {
    padding-bottom: 16px;
    box-sizing: border-box;

    .el-col-7 {
        width: 65%;
        max-width: 600px;
    }
}

.el-pagination {
    float: right;
    padding: 20px;
    box-sizing: border-box;
}

::v-deep th.el-table__cell {
    word-break: break-word;
    background-color: #f8f8f9 !important;
    color: #515a6e;
    height: 40px;
    font-size: 13px;

}

.el-tag--small {
    margin-left: 5px;
}
</style>
