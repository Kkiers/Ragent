# Animation.rotate3d

# Animation.rotate3d(number x, number y, number z, number angle)

从 固定 轴顺时针旋转一个角度

## 支持说明

应用能力 | Android | iOS | PC | Harmony | 预览效果
--- | --- | --- | --- | --- | ---
小程序 | **✓** | **✓** | **✓** | V7.35.0+ | [预览](https://applink.feishu.cn/client/mini_program/open?appId=cli_9dff7f6ae02ad104&path=%2Fpage%2FAPI%2Fpages%2Fanimation%2Fanimation)
网页应用 | **X** | **X** | **X** | **X** | /

## 输入

名称 | 数据类型 | 必填 | 默认值 | 描述
--- | --- | --- | --- | ---
x | number | 是 | / | 旋转轴的 x 坐标
y | number | 是 | / | 旋转轴的 y 坐标
z | number | 是 | / | 旋转轴的 z 坐标
angle | number | 是 | / | 旋转的角度。范围 [-180, 180]

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

animation.rotate(20, 20, 20, 90).step();
```
