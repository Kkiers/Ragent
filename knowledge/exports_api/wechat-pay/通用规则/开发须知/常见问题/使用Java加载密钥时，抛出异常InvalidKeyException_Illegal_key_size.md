# 使用Java加载密钥时，抛出异常InvalidKeyException: Illegal key size

# 使用Java加载密钥时，抛出异常InvalidKeyException: Illegal key size

路径：通用规则/开发须知/常见问题/使用Java加载密钥时，抛出异常InvalidKeyException: Illegal key size

受到美国法律的约束，早期Java的运行时限制了JCE支持的密钥长度，即默认不支持256位的AES。解决的方法有三个：

- （推荐）升级Java 8u162+，[默认使用ulimited policy](https://bugs.openjdk.java.net/browse/JDK-8170157)
- Java 8u151和8u152，可以在你的程序中直接放开策略
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1Security.setProperty("crypto.policy", "unlimited");
```

- 其他版本，下载[无限强度权限策略文件补丁包](https://www.oracle.com/technetwork/java/javase/downloads/jce8-download-2133166.html)，并使用其中的文件覆盖$JAVA_HOME/lib/security目录下的对应的local_policy.jar 和US_export_policy.jar
- Java9及以上，均无限制。
