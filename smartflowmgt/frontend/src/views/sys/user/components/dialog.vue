<template>
  <el-dialog
      model-value="dialogVisible"
      :title="dialogTitle"
      width="30%"
      @close="handleClose"
  >

    <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
    >
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" :disabled="form.id==-1?false:'disabled'"/>
        <el-alert
            v-if="form.id==-1"
            title="默认初始密码：123456"
            :closable="false"
            style="line-height: 10px;"
            type="success">
        </el-alert>
      </el-form-item>

      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email"/>
      </el-form-item>

      <el-form-item label="状态" prop="is_active">
        <el-radio-group v-model="form.is_active">
          <el-radio :label="true">正常</el-radio>
          <el-radio :label="false">禁用</el-radio>
        </el-radio-group>
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

import {defineEmits, defineProps, ref, watch} from "vue";
import {ElMessage} from 'element-plus'
import api from "@utils/api"

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
  username: "",
  password: "123456",
  is_active: true,
  email: "",
})


const checkUsername = async (rule, value, callback) => {
  if (form.value.id == -1) {
    const res = await api.post("user/check", {username: form.value.username});
    if (res.data.code == 500) {
      callback(new Error("用户名已存在！"));
    } else {
      callback();
    }
  } else {
    callback();
  }

}


const rules = ref({
  username: [
    {required: true, message: '请输入用户名'},
    {required: true, validator: checkUsername, trigger: "blur"}
  ],
  email: [{required: true, message: "邮箱地址不能为空", trigger: "blur"}, {
    type: "email",
    message: "请输入正确的邮箱地址",
    trigger: ["blur", "change"]
  }],
})

const formRef = ref(null)

const initFormData = async (id) => {
  const res = await api.get("user/action?id=" + id);
  form.value = res.data.user;
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
          username: "",
          password: "123456",
          is_active: true,
          email: "",
        }

      }
    }
)


const emits = defineEmits(['update:modelValue', 'initUserList'])

const handleClose = () => {
  emits('update:modelValue', false)
}

const handleConfirm = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      let result = await api.post("user/save", form.value);
      let data = result.data;
      if (data.code == 200) {
        ElMessage.success("操作成功！")
        formRef.value.resetFields();
        emits("initUserList")
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

<style scoped>

</style>
