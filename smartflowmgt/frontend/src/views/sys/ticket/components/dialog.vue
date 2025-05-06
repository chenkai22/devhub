<template>
    <el-dialog model-value="dialogVisible" :title="dialogTitle" width="30%" @close="handleClose">

        <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
            <el-form-item label="工单号" v-if="form.id != -1" prop="ticket_code">
                <el-input v-model="form.ticket_code" :disabled="form.id == -1 ? false : 'disabled'" />
            </el-form-item>

            <el-form-item label="主题" prop="title">
                <el-input v-model="form.title" />
            </el-form-item>

            <el-form-item label="描述" prop="desc">
                <el-input v-model="form.desc" type="textarea" />
            </el-form-item>

            <el-form-item label="附件上传" v-if="form.id == -1">
                <FileUploader @upload-success="handleUploadSuccess" />
            </el-form-item>

            <el-form-item label="处理人" prop="handler">
                <el-select v-model="form.handler" filterable placeholder="请选择处理人" style="width: 100%">
                    <el-option v-for="user in userList" :key="user.id" :label="user.realname || user.username"
                        :value="user.id" />
                </el-select>
            </el-form-item>

            <el-form-item label="截止时间" prop="deadline">
                <el-date-picker v-model="form.deadline" type="datetime" placeholder="选择截止时间"
                    format="YYYY-MM-DD HH:mm:ss" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
            </el-form-item>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button type="primary" @click="handleConfirm">确认</el-button>
                <el-button @click="handleClose">取消</el-button>
            </span>
        </template>
    </el-dialog>
</template>

<script setup>

import { defineEmits, defineProps, ref, watch, onMounted } from "vue";
import { ElMessage } from 'element-plus'
import api from "@utils/api"
import FileUploader from '@/components/FileUploader.vue'


const userList = ref([]);
const loadUsers = async () => {
    const res = await api.get("user/list");
    userList.value = res.data.data || [];
};

onMounted(() => {
    loadUsers();
});

const handleUploadSuccess = (fileId) => {
    if (!form.value.attachments) {
        form.value.attachments = []
    }
    form.value.attachments.push(fileId)
    console.log("附件上传", form.value.attachments)
}

const props = defineProps(
    {
        id: {
            type: Number,
            default: -1,
            required: true
        },
        dialogTitle: {
            type: String,
            default: '',
            required: true
        },
        dialogVisible: {
            type: Boolean,
            default: false,
            required: true
        }
    }
)


const form = ref({
    id: -1,
    ticket_code: "",
    title: "123456",
    desc: true,
    find_user: "",
    handler: "",
    deadline: "",
})


const rules = ref({

})

const formRef = ref(null)

const initFormData = async (id) => {
    const res = await api.get("ticket/action?id=" + id);
    form.value = res.data.ticket;
}


watch(
    () => props.dialogVisible,
    () => {
        let id = props.id;
        if (id != -1) {
            initFormData(id)
        } else {
            form.value = {
                id: -1,
                ticket_code: "",
                title: "123456",
                desc: true,
                find_user: "",
                handler: "",
                deadline: "",
            }

        }
    }
)


const emits = defineEmits(['update:modelValue', 'initTicketList'])

const handleClose = () => {
    emits('update:modelValue', false)
}

const handleConfirm = () => {
    formRef.value.validate(async (valid) => {
        if (valid) {
            const submitData = {
                ...form.value,
                attachments: form.value.attachments || []
            };
            let result = await api.post("ticket/save", submitData);
            let data = result.data;
            if (data.code == 200) {
                ElMessage.success("操作成功！")
                formRef.value.resetFields();
                emits("initTicketList")
                handleClose();
            } else {
                ElMessage.error(data.msg);
            }
        } else {
            console.log("fail")
        }
    })
}

</script>

<style scoped></style>
