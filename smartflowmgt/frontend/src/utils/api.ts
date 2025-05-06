import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    withCredentials: true,
    setTimeout: 3000,
});

// 请求拦截器
api.interceptors.request.use(config => {
    const token = window.sessionStorage.getItem('token');
    if (token) config.headers.Authorization = token
    return config;
})

// 响应拦截器
api.interceptors.response.use(response => {
    if (response.data == "token过期" || response.data == "token无效") {
        try {
            const refresh_token = sessionStorage.getItem("refresh_token")
            api.post("/user/refresh", { "refresh": refresh_token }).then(res => {
                window.sessionStorage.setItem("token", res.data.access);
                window.location.reload()
            })
        }catch {
            // 刷新失败跳转登录
            sessionStorage.clear();
            window.location.href = '/login';
        }


    }
    return response
})
export default api;