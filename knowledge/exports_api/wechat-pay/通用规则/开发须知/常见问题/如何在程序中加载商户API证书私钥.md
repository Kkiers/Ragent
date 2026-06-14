# 如何在程序中加载商户API证书私钥

# 如何在程序中加载商户API证书私钥

路径：通用规则/开发须知/常见问题/如何在程序中加载商户API证书私钥

推荐使用微信支付提供的SDK。你也可以查看下列编程语言的示例代码。

## JAVA：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1/**
2  * 获取私钥。
3  *
4  * @param filename 私钥文件路径  (required)
5  * @return 私钥对象
6  */
7public static PrivateKey getPrivateKey(String filename) throws IOException {
8  String content = new String(Files.readAllBytes(Paths.get(filename)), "utf-8");
9  try {
10    String privateKey = content.replace("-----BEGIN PRIVATE KEY-----", "")
11        .replace("-----END PRIVATE KEY-----", "")
12        .replaceAll("\\s+", "");
13    KeyFactory kf = KeyFactory.getInstance("RSA");
14    return kf.generatePrivate(
15        new PKCS8EncodedKeySpec(Base64.getDecoder().decode(privateKey)));
16  } catch (NoSuchAlgorithmException e) {
17    throw new RuntimeException("当前Java环境不支持RSA", e);
18  } catch (InvalidKeySpecException e) {
19    throw new RuntimeException("无效的密钥格式");
20  }
21}
```

## PHP：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1/**
2* Read private key from file
3*
4* @param string    $filepath     PEM encoded private key file path
5* 
6* @return resource|bool     Private key resource identifier on success, or FALSE on error
7*/
8public static function getPrivateKey($filepath) {
9    return openssl_get_privatekey(file_get_contents($filepath));
10}
```

## csharp：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1protected string sign(string message)
2{
3    // 需去除私钥文件中的-----BEGIN/END PRIVATE KEY-----
4    string privateKey = "MIIEvgIBADANBgkqhkiG...30HBe+GD1tntZgf6I1Y0ZpHZ";
5    byte[] keyData = Convert.FromBase64String(privateKey);
6    using (CngKey cngKey = CngKey.Import(keyData, CngKeyBlobFormat.Pkcs8PrivateBlob))
7    using (RSACng rsa = new RSACng(cngKey))
8    {
9        byte[] data = System.Text.Encoding.UTF8.GetBytes(message);
10        return Convert.ToBase64String(rsa.SignData(data, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1));
11    }
12}
```

## GO：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1package main
2import (
3  "crypto/x509"
4  "encoding/pem"
5  "fmt"
6  "log"
7)
8func main() {
9  var pemData = []byte(`
10-----BEGIN PRIVATE KEY-----
11MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC1yhh6LNB8nXmO
12SxdGKWmDh0OxAM/wnGyHKSD9tcEhMQTe+wabce0POXzejCmwFBzZa7ZmxH5LoAey
13T7Fpwb7pptbbDx58CxCYhNEdQ2XrFILUCq3daMj++KQlyDp8U0NspFKsO57gSlih
14AJ49DzcXQb7Vs5daIvtLapIouPyixAE5uDL+afmJ+bXC11xP5sPWw1RfXynW3vbE
15yfRol9hQyQWfmO15GSZi6TTAhTKaW31yKaQNChy06K+LsE9JAU+ESxihthtGiMbY
163fFRyhF9Ka2e0wIOz6UdcfwMjxXWRV4OLD1uFG9IYbUiugmYtDyIYZaFDPYdi/+R
17jm10Ps5lAgMBAAECggEAb19kRZ2lEWOM8D9S//opGZrKPuvneVrsJpZtDuLGcqZM
18fKvALYXLnZMzzEiE1cpMrmuOMUHaukxNytGGOOupIg7D/SszGv3QahCc6Ne83hwP
191wa/5DDpS0RblIYqRrbgTPQTbk+Mk48Y43K0f2YN82KlHtnLNT7PRDIDX42Nwc1X
208f4JcfyKUE/pOSn+YUlu5Edu6QYbWJWS7mlojEZ/wuWbSymbs6mVVkKeSWGTIh1v
214n2F3Gj6ckUDlt4aZWTVcBa2+ZvSE2h5frSH0snpdGV1bW44IqE3NkwfTQ7JI34C
22VJdhb3goIyoTmiz6NGEZuiyr8gP9IOjqPfeP7GO5YQKBgQDuB1CT8ksO4SqR3skR
23kdCQW7kOogZgDThei+3HUMOsHr8L42oYkJDmk2res1ow/mz6SoIV4w6mvvUSnACx
24dtYA1AzUEs3jvltv8cQ1HAuDhLRslWrhSoxrQQh20yrVxxGN0J4DdCAGURSUwypz
25UHR+mlfcjacPyxKUsT41+8zG+QKBgQDDg8ZGivuV794RuA3cfpitUFG+0nA0ZS3q
26AZqlA3ufnCudHQixFIsf83Q7sX7pBob5PNONqsbv0OKpC3/xJRSPIwjWTBUPlDLX
27rsGajKMhUPtkWo4zkfrSa8XaUpUVDU0qTzS71f9Aab3SkPH1d1o4cQxO08axGLbm
28TV/46QCBzQKBgDd7ZQDXPT+epHmT4HJD9sVvW9dZVPsWmckP/MC0xqdcE1QGEjjf
29mablPcfjLma1J1m//Ep1vniHkkBgNJkpBgDzbHoSWAN5335ccEug2d4yFIwq19rj
30sY9efUaVOirSV/kiY3KSotRWGeIDC+YNHtpTx58VNZes0gvutH2Iz9ahAoGAUcoW
31b/xEMv0dURxF8C+lfxtSlxlBhymsg3AYWV+Tn7mdJSS4Nhv592vI/A/Mn37zh+BC
32P8lpX3lq2HzPEPoKF7b4Q22ggdvlSQT6SMT8mTtfbyPSyRAQdWZQZnyVkTD3TvPD
33g7CKD1As8KFiFuXPAD2KgI9nVz6XhNBpjZ8rbyECgYEAsOrm1hbNZbvlNhnuUjw5
34DTgTuJ3B0j1aK/7C2EQWR+mIG2q5TKDC6xNdszV0gK1/TbJk4RNgQo0JLkuZ2Xk2
35Q8KhaNe+X8SYP9CFKIsXuhGrYI5ICjipov5oJqjESV4wle575eWwdPgF1ICabpIq
36dnX2MxS9tkk830uXxPrXpRA=
37-----END PRIVATE KEY-----`)
38  block, rest := pem.Decode(pemData)
39  if block == nil || block.Type != "PRIVATE KEY" {
40    log.Fatal("failed to decode PEM block containing public key")
41  }
42  pri, err := x509.ParsePKCS8PrivateKey(block.Bytes)
43  if err != nil {
44    log.Fatal(err)
45  }
46  fmt.Printf("Got a %T, with remaining data: %q", pri, rest)
47}
```
