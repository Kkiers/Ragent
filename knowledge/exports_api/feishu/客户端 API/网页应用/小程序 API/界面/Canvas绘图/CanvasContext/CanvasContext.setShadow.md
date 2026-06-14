# CanvasContext.setShadow

# CanvasContext.setShadow(number x, number y, number blur, string color)

设置阴影

## 支持说明

应用能力 | Android | iOS | PC | Harmony | 预览效果
--- | --- | --- | --- | --- | ---
小程序 | **✓** | **✓** | **✓** | V7.35.0+ | 预览
网页应用 | **X** | **X** | **X** | **X** | /

## 输入

名称 | 数据类型 | 必填 | 默认值 | 描述
--- | --- | --- | --- | ---
x | number | 是 |  | x 轴偏移量
y | number | 是 |  | y 轴偏移量
blur | number | 是 |  | 模糊量
color | string | 是 |  | 颜色

## 输出

无

## 示例代码

下载示例代码

<div style="display: flex">
    预览小程序

</div> 

```javascript
ctx.setFillStyle("red");
ctx.setShadow(10, 50, 50, "blue");
ctx.fillRect(10, 10, 150, 75);

ctx.draw();
```
