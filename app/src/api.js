const FormData = require('form-data');
module.exports = {
    /**
     * 获得匹配结果
     * @param param 参数
     * @param param.avatar 头像文件
     * @param param.clothing 上衣分类
     * @param success 成功回调
     * @param error 错误回调
     */
    getMatchings({ avatar, clothing }, success, error) {
        const form = new FormData();
        form.append('clothing', clothing);
        form.append('avatar', avatar);
        window.fetch('/api/query', { method: 'POST', body: form })
            .then((response) => {
                if (response.ok) {
                    return response.json();
                } else {
                }
            })
            .then(success)
            .catch(error);
    }
};
