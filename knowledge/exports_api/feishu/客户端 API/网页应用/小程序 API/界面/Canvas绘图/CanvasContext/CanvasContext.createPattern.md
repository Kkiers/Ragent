# CanvasContext.createPattern

# CanvasContext.createPattern(string image, string repetition)

创建径向渐变管理对象

## 支持说明

应用能力 | Android | iOS | PC | Harmony | 预览效果
--- | --- | --- | --- | --- | ---
小程序 | V3.45.0+ | V3.45.0+ | V3.45.0+ | V7.35.0+ | 预览
网页应用 | **X** | **X** | **X** | **X** | /

## 输入

名称 | 数据类型 | 必填 | 默认值 | 描述
--- | --- | --- | --- | ---
image | string | 是 |  | 图片地址，支持本地地址和网络地址
repetition | string | 是 |  | 重复模式  
**可选值**：  
- `repeat` 默认值，横向和纵向重复  
- `repeat-x` 横向重复  
- `repeat-y` 纵向重复  
- `no-repeat` 不重复图片

## 输出

返回值：
`CanvasPattern`

## 示例代码

下载示例代码

<div style="display: flex">
    预览小程序

</div> 

```javascript
const pattern = ctx.createPattern("https://sf3-cn.feishucdn.com/obj/eden-cn/eseh7nupevhps/block/image.png", "repeat-x");
ctx.fillStyle = pattern;
ctx.fillRect(0, 0, 300, 150);
ctx.draw();
```
