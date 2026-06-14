# CanvasContext.scale

# CanvasContext.scale(number x, number y)

缩放坐标点

## 支持说明

应用能力 | Android | iOS | PC | Harmony | 预览效果
--- | --- | --- | --- | --- | ---
小程序 | **✓** | **✓** | **✓** | V7.35.0+ | 预览
网页应用 | **X** | **X** | **X** | **X** | /

## 输入

名称 | 数据类型 | 必填 | 默认值 | 描述
--- | --- | --- | --- | ---
x | number | 是 |  | x 轴方向缩放值
y | number | 是 |  | y 轴方向缩放值

## 输出

无

## 示例代码

下载示例代码

<div style="display: flex">
    预览小程序

</div> 

```javascript
ctx.strokeRect(10, 10, 25, 15);
ctx.scale(2, 2);
ctx.strokeRect(10, 10, 25, 15);
ctx.scale(2, 2);
ctx.strokeRect(10, 10, 25, 15);

ctx.draw();
```
