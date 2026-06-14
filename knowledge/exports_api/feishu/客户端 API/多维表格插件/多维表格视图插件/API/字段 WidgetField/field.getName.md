# field.getName

# field.getName
获取字段名。

## 权限要求
**Notice**：开启以下任一权限
查看、评论、编辑和管理多维表格(bitable:app)
查看、评论和导出多维表格(bitable:app:readonly)

## 输出
Promise字符串：该字段的字段名。
## 示例代码
### 调用示例

```js
    const selection = await bitable.base.getSelection();
    const table = await bitable.base.getTableById(selection.tableId);
    const filed = await table.getFieldByName('查找引用');

const res = await filed.getName()
```

### 返回示例
res:
```js
'查找引用'
```
