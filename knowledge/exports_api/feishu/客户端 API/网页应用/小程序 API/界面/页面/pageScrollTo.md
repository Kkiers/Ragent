# pageScrollTo

# pageScrollTo(Object object)

滚动页面到目标位置

## 支持说明

应用能力 | Android | iOS | PC | Harmony | 预览效果
--- | --- | --- | --- | --- | ---
小程序 | **✓** | **✓** | **✓** | V7.35.0+ | [预览](https://applink.feishu.cn/client/mini_program/open?appId=cli_9dff7f6ae02ad104&path=page%2FAPI%2Fpages%2Fpage-scroll-to%2Fpage-scroll-to)
网页应用 | **X** | **X** | **X** | **X** | 预览

## 输入

属性描述：

名称 | 数据类型 | 属性 | 默认值 | 描述
--|--|--|--|--
`scrollTop` | `number` | required | N/A | 位置，单位 `px`
`duration` | `number` | optional | `200` | 执行时长，单位 `ms`

## 输出
无

## 示例代码

下载示例代码

<div style="display: flex">
          [预览小程序](https://applink.feishu.cn/client/mini_program/open?appId=cli_9dff7f6ae02ad104&path=page%2FAPI%2Fpages%2Fpage-scroll-to%2Fpage-scroll-to)
    预览网页应用

</div> 

```js
tt.pageScrollTo({
    scrollTop: 3008,
    duration: 1000,
    success () {
        console.log(`PageScrollTo invoked successfully`);
    },
    fail () {
        console.log(`Failed to invoke pageScrollTo`);
    }
});
```
