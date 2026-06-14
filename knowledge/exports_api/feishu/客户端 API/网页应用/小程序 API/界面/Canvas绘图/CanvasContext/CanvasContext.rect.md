# CanvasContext.rect

# CanvasContext.rect(number x, number y, number w, number h)

添加矩形到当前路径中

## 支持说明

应用能力 | Android | iOS | PC | Harmony | 预览效果
--- | --- | --- | --- | --- | ---
小程序 | **✓** | **✓** | **✓** | V7.35.0+ | 预览
网页应用 | **X** | **X** | **X** | **X** | /

## 输入

名称 | 数据类型 | 必填 | 默认值 | 描述
--- | --- | --- | --- | ---
x | number | 是 |  | 绘制开始点的 x 坐标
y | number | 是 |  | 绘制开始点的 y 坐标
w | number | 是 |  | 矩形宽度
h | number | 是 |  | 矩形高度

## 输出

无

## 示例代码

下载示例代码

<div style="display: flex">
    预览小程序

</div> 

```javascript
const ctx = tt.createCanvasContext(canvasId);

ctx.rect(10, 10, 100, 100);
ctx.fill();

ctx.draw();
```
