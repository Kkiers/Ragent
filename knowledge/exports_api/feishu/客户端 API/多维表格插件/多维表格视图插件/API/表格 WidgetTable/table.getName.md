# table.getName

# table.getName
获取表名。

## 权限要求
**Notice**：开启以下任一权限
查看、评论、编辑和管理多维表格(bitable:app)
查看、评论和导出多维表格(bitable:app:readonly)

## 输出
promise字符串。
## 示例代码

```js
const table = await bitable.base.getTableByName('数据表')

const name = await table.getName()

console.log(name) // 数据表
```
