# bridge.getLanguage

# bridge.getLanguage
获取当前文档语言。

## 输出
Promise 字符串，值为以下语言之一：
```js
export type Language =
  | 'zh'
  | 'zh-TW'
  | 'zh-HK'
  | 'en'
  | 'ja'
  | 'fr'
  | 'hi'
  | 'id'
  | 'it'
  | 'ko'
  | 'pt'
  | 'ru'
  | 'th'
  | 'vi'
  | 'de'
  | 'es';
```
## 示例代码
### 调用示例

```js
const res = await bitable.bridge.getLanguage();
```

### 返回示例
res:
```js
'zh'
```
