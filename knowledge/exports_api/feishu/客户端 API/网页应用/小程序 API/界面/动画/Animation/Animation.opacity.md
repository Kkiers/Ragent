# Animation.opacity

# Animation.opacity(number value)

设置透明度

## 支持说明

应用能力 | Android | iOS | PC | Harmony | 预览效果
--- | --- | --- | --- | --- | ---
小程序 | **✓** | **✓** | **✓** | V7.35.0+ | [预览](https://applink.feishu.cn/client/mini_program/open?appId=cli_9dff7f6ae02ad104&path=%2Fpage%2FAPI%2Fpages%2Fanimation%2Fanimation)
网页应用 | **X** | **X** | **X** | **X** | /

## 输入

名称 | 数据类型 | 必填 | 默认值 | 描述
--- | --- | --- | --- | ---
value | number | 是 | / | 透明度，范围 0-1

## 输出

返回值：  

`Animation` 实例

## 示例代码

下载示例代码

<div style="display: flex">
          [预览小程序](https://applink.feishu.cn/client/mini_program/open?appId=cli_9dff7f6ae02ad104&path=%2Fpage%2FAPI%2Fpages%2Fanimation%2Fanimation)

</div> 

```js
const animation = tt.createAnimation();

animation.opacity(0.5).step();
```
