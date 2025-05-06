<template>
    <div class="login">

        <el-form ref="loginRef" :model="loginForm" :rules="loginRules" class="login-form">
            <h1 class="title">智能流程管理系统</h1>

            <el-form-item prop="username">

                <el-input v-model="loginForm.username" type="text" size="large" auto-complete="off" placeholder="账号">

                </el-input>
            </el-form-item>
            <el-form-item prop="password">
                <el-input v-model="loginForm.password" type="password" size="large" auto-complete="off"
                    placeholder="密码">

                </el-input>
            </el-form-item>


            <el-checkbox v-model="loginForm.rememberMe" style="margin:0px 0px 25px 0px;">记住密码</el-checkbox>
            <el-form-item style="width:100%;">
                <el-button size="large" type="primary" style="width:100%;" @click.prevent="handleLogin">
                    <span>登 录</span>

                </el-button>

            </el-form-item>
        </el-form>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import api from "@utils/api"
import { ElMessage } from 'element-plus'
import Cookies from 'js-cookie'
import { encrypt, decrypt } from '@utils/jsencrypt'
import router from '@/router'


const loginRef = ref(null)

const loginForm = ref({
    username: '',
    password: '',
    rememberMe: false
})

const loginRules = {
    username: [{
        required: true,
        message: '请输入账号',
        trigger: 'blur'
    }],
    password: [{
        required: true,
        message: '请输入密码',
        trigger: 'blur'
    }]
}

const handleLogin = () => {
    loginRef.value.validate(async (valid) => {
        if (valid) {
            api.post('/user/login', loginForm.value).then(res => {
                if (res.data.code == 200) {
                    window.sessionStorage.setItem("token", res.data.token);
                    window.sessionStorage.setItem("currentUser", JSON.stringify(res.data.user));
                    window.sessionStorage.setItem("menuList", JSON.stringify(res.data.menuList));
                    window.sessionStorage.setItem("refresh_token", res.data.refresh_token);
                    if (loginForm.value.rememberMe) {
                        Cookies.set('username', loginForm.value.username, { expires: 30 })
                        Cookies.set('password', encrypt(loginForm.value.password), { expires: 30 })
                        Cookies.set('rememberMe', loginForm.value.rememberMe, { expires: 30 })
                    } else {
                        Cookies.remove('username')
                        Cookies.remove('password')
                        Cookies.remove('rememberMe')
                    }
                    // 跳转到重定向页面或首页
                    const redirect = router.currentRoute.value.query.redirect || '/'
                    router.push(redirect)
                } else {
                    ElMessage.error(res.data.msg)
                }
            })
        }
    })
}

function getCookie() {
    const username = Cookies.get('username')
    const password = Cookies.get('password')
    const rememberMe = Cookies.get('rememberMe')
    if (username && password && rememberMe) {
        loginForm.value.username = username
        loginForm.value.password = decrypt(password)
        loginForm.value.rememberMe = Boolean(rememberMe)
    }
}
</script>

<style lang="scss" scoped>
a {
    color: white
}

.login {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    width: 100%;
    background-image: url("../assets/images/login-background.jpg");
    background-size: cover;
    position: relative;

    &>* {
        width: 90%;
        max-width: 400px;
    }
}

.title {
    margin: 0px auto 30px auto;
    text-align: center;
    color: #707070;
    font-size: 24px;
    font-weight: 500;
}

.login-form {
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.95);
    padding: 25px 30px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    margin: 0;

    .el-input {
        height: 40px;



        input {
            display: inline-block;
            height: 40px;
        }
    }

    .input-icon {
        height: 39px;
        width: 14px;
        margin-left: 0px;
    }

}

:deep(.el-form) {
    width: 100% !important;
}

:deep(.el-form-item__content) {
    display: block;
    width: 100%;
}

.login-tip {
    font-size: 13px;
    text-align: center;
    color: #bfbfbf;
}

.login-code {
    width: 33%;
    height: 40px;
    float: right;

    img {
        cursor: pointer;
        vertical-align: middle;
    }
}

.el-login-footer {
    height: 40px;
    line-height: 40px;
    position: fixed;
    bottom: 0;
    width: 100%;
    text-align: center;
    color: #fff;
    font-family: Arial;
    font-size: 12px;
    letter-spacing: 1px;
}

.login-code-img {
    height: 40px;
    padding-left: 12px;
}
</style>
