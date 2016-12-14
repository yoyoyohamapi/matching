const mockMatchings = [{
    clothing: {
        image: 'http://img12.static.yhbimg.com/goodsimg/2016/11/29/18/020d366cdb5b6ad58995c5cad92044a079.jpg?imageMogr2/thumbnail/235x314/extent/235x314/background/d2hpdGU=/position/center/quality/90',
        url: 'http://item.yohobuy.com/product/pro_644428_790660/Levi%E2%80%99s%20Truckeryurongniuzijichejiake%2028483-0002.html'
    },
    pants: {
        image: 'http://img12.static.yhbimg.com/goodsimg/2016/11/29/17/02820264f3af7f43d846ff7ee417ba9a94.jpg?imageMogr2/thumbnail/235x314/extent/235x314/background/d2hpdGU=/position/center/quality/90',
        url: 'http://item.yohobuy.com/product/pro_647534_794066/Dickies%20%20ketuoxieneidanjunzhuangwaitaoganlanlv%20163M10WD07OL.html'
    },
    score: 5
}, {
    clothing: {
        image: 'http://img12.static.yhbimg.com/goodsimg/2016/11/29/18/020d366cdb5b6ad58995c5cad92044a079.jpg?imageMogr2/thumbnail/235x314/extent/235x314/background/d2hpdGU=/position/center/quality/90',
        url: 'http://item.yohobuy.com/product/pro_644428_790660/Levi%E2%80%99s%20Truckeryurongniuzijichejiake%2028483-0002.html'
    },
    pants: {
        image: 'http://img12.static.yhbimg.com/goodsimg/2016/11/29/17/02820264f3af7f43d846ff7ee417ba9a94.jpg?imageMogr2/thumbnail/235x314/extent/235x314/background/d2hpdGU=/position/center/quality/90',
        url: 'http://item.yohobuy.com/product/pro_647534_794066/Dickies%20%20ketuoxieneidanjunzhuangwaitaoganlanlv%20163M10WD07OL.html'
    },
    score: 5
}, {
    clothing: {
        image: 'http://img12.static.yhbimg.com/goodsimg/2016/11/29/18/020d366cdb5b6ad58995c5cad92044a079.jpg?imageMogr2/thumbnail/235x314/extent/235x314/background/d2hpdGU=/position/center/quality/90',
        url: 'http://item.yohobuy.com/product/pro_644428_790660/Levi%E2%80%99s%20Truckeryurongniuzijichejiake%2028483-0002.html'
    },
    pants: {
        image: 'http://img12.static.yhbimg.com/goodsimg/2016/11/29/17/02820264f3af7f43d846ff7ee417ba9a94.jpg?imageMogr2/thumbnail/235x314/extent/235x314/background/d2hpdGU=/position/center/quality/90',
        url: 'http://item.yohobuy.com/product/pro_647534_794066/Dickies%20%20ketuoxieneidanjunzhuangwaitaoganlanlv%20163M10WD07OL.html'
    },
    score: 5
}, {
    clothing: {
        image: 'http://img12.static.yhbimg.com/goodsimg/2016/11/29/18/020d366cdb5b6ad58995c5cad92044a079.jpg?imageMogr2/thumbnail/235x314/extent/235x314/background/d2hpdGU=/position/center/quality/90',
        url: 'http://item.yohobuy.com/product/pro_644428_790660/Levi%E2%80%99s%20Truckeryurongniuzijichejiake%2028483-0002.html'
    },
    pants: {
        image: 'http://img12.static.yhbimg.com/goodsimg/2016/11/29/17/02820264f3af7f43d846ff7ee417ba9a94.jpg?imageMogr2/thumbnail/235x314/extent/235x314/background/d2hpdGU=/position/center/quality/90',
        url: 'http://item.yohobuy.com/product/pro_647534_794066/Dickies%20%20ketuoxieneidanjunzhuangwaitaoganlanlv%20163M10WD07OL.html'
    },
    score: 5
}, {
    clothing: {
        image: 'http://img12.static.yhbimg.com/goodsimg/2016/11/29/18/020d366cdb5b6ad58995c5cad92044a079.jpg?imageMogr2/thumbnail/235x314/extent/235x314/background/d2hpdGU=/position/center/quality/90',
        url: 'http://item.yohobuy.com/product/pro_644428_790660/Levi%E2%80%99s%20Truckeryurongniuzijichejiake%2028483-0002.html'
    },
    pants: {
        image: 'http://img12.static.yhbimg.com/goodsimg/2016/11/29/17/02820264f3af7f43d846ff7ee417ba9a94.jpg?imageMogr2/thumbnail/235x314/extent/235x314/background/d2hpdGU=/position/center/quality/90',
        url: 'http://item.yohobuy.com/product/pro_647534_794066/Dickies%20%20ketuoxieneidanjunzhuangwaitaoganlanlv%20163M10WD07OL.html'
    },
    score: 5
}];

module.exports = {
    getMatchings({ avatar, clothing }, success, error) {
        setTimeout(() => {
            success({ matchings: mockMatchings });
        }, 3000);
    }
};
