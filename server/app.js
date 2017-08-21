const path = require('path');
const app = require('koa')();
const Router = require('koa-router');
const api = new Router({ prefix: '/api' });
const exec = require('co-exec');
const bodyParser = require('koa-body');
const serve = require('koa-static');
const _ = require('lodash');
const pmongo = require('promised-mongo');

// config
const port = 5000;
const scriptsDir = '../scripts/';
const scripts = {
    extracSkinColor: path.resolve(`${scriptsDir}/extract_skin_color.py`)
};

// 颜色配置
const colorConfig = require('../config/web_safe_color_divide.json');

// 建立数据库连接
const db = pmongo('paper');

// apis
api.post('/query', function* (next) {
    //  获得头像
    const { fields, files } = this.request.body;
    const { clothing } = fields;
    const { avatar } = files;
    try {
        // 检测到的肤色， 调用 python 写好的肤色识别脚本
        const results = yield exec(`python2 ${scripts.extracSkinColor} -i ${avatar.path}`);
        const [, skinColor] = results.replace('\n', '').split(':');
        // 统计该肤色特别适宜以及不适宜的颜色
        const fitColors = [];
        const unfitColors = [];
        _.each((colorConfig), (color, hex) => {
            if (_.findIndex(color.fit, skinColor) > -1) {
                fitColors.push(hex);
            } else if (_.findIndex(color.unfit, skinColor) > -1) {
                unfitColors.push(hex);
            }
        });
        // 获得上装：刨除掉颜色不适宜的
        let styles = yield db.clothings.aggregate({
            $match: {
                category: clothing,
                color: { $nin: unfitColors }
            }
        }, {
            $group: {
                _id: '$style',
                clothings: {
                    $addToSet: {
                        color: '$color',
                        url: '$url',
                        image: '$image'
                    }
                }
            }
        });
        styles = _.sortBy(styles, ['_id']);
        // 每一个style挑选出最多5个适宜颜色的（假如有的话）
        const matchings = _.map(styles, (style) => {
            // 先乱序
            let clothings = _.shuffle(style.clothings);
            clothings = _.map(clothings, (clothing) => {
                clothing.color = _.findIndex(fitColors, clothing.color) > -1;
                return clothing;
            });
            let sorted = _.sortBy(clothings, ['color']);
            // 挑选出前五个
            return _.take(sorted, 5);
        });
        this.body = {
            skinColor,
            matchings
        };
        yield next;
    } catch (e) {
        console.error(e);
        this.throw(400, '获得搭配失败');
    }
});

// middlewares
app.use(bodyParser({
    multipart: true
}));
app.use(serve('../app/dist'));
app.use(api.routes());

// bootstrap
app.listen(port, () => {
    console.log(`Server listening on http://localhost:${port}`);
});
