<template>
    <div class="app-container">
        <el-row :gutter="20">
            <el-col :span="16">
                <el-card>
                    <div ref="chart" style="height:400px"></div>
                </el-card>
            </el-col>

            <el-col :span="8">
                <el-card header="完成率统计">
                    <div ref="pieChart" style="height:400px"></div>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import api from '@utils/api'

const chart = ref(null)
const pieChart = ref(null)
let mainChartInstance = null
let pieChartInstance = null

const initCharts = async () => {
    const res = await api.get('/ticket/report')

    // 柱状图配置
    mainChartInstance.setOption({
        title: { text: '工单状态分布' },
        tooltip: {},
        xAxis: { data: ['待处理', '处理中', '已完成'] },
        yAxis: {},
        series: [{
            name: '数量',
            type: 'bar',
            data: [
                res.data.pending,
                res.data.processing,
                res.data.completed
            ]
        }]
    })

    // 饼图配置
    pieChartInstance.setOption({
        title: { text: '完成率' },
        tooltip: { trigger: 'item' },
        series: [{
            type: 'pie',
            data: [
                { value: res.data.completionRate, name: '完成率' },
                { value: 100 - res.data.completionRate, name: '未完成' }
            ]
        }]
    })
}

onMounted(async () => {
    mainChartInstance = echarts.init(chart.value)
    pieChartInstance = echarts.init(pieChart.value)
    await initCharts()
    window.addEventListener('resize', () => {
        mainChartInstance.resize()
        pieChartInstance.resize()
    })
})
</script>
<style scoped>
.chart-card {
    height: 500px;
}

.chart-card :deep(.el-card__body) {
    height: calc(100% - 40px);
    padding: 15px;
}
</style>