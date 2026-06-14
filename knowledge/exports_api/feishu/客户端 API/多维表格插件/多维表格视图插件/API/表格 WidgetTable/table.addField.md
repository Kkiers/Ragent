# table.addField

# table.addField
新增一列字段。字段名字重复将抛出错误。

## 权限要求

查看、评论、编辑和管理多维表格(bitable:app)

## 输入
```
addField(fieldConfig)
```

名称 | 数据类型 | 是否必填 | 描述
--- | --- | --- | ---
fieldConfig | [IAddFieldConfig](https://open.feishu.cn/document/uAjLw4CM/uYjL24iN/base-extensions/base-view-extensions/data-type/iaddfieldconfig) | 是 | 需要新增的字段和它的配置

## 输出
Promise字符串：新增的字段的id。
## 示例代码
### 调用示例

```js
  const selection = await bitable.base.getSelection();
  const table = await bitable.base.getTableById(selection.tableId); // 获取当前数据表实例

const res = await table.addField({ // 新增一列多行文本类型的字段
    type: FieldType.Text,
    name: '多行文本2',
  })
```

### 返回示例
res:
```js
'fldILo3L59'
```
