# 如何使用API证书解密敏感字段

# 如何使用API证书解密敏感字段

路径：通用规则/开发须知/如何加解密敏感字段/如何使用API证书解密敏感字段

微信支付使用商户API证书中的公钥对下行的敏感信息进行加密。开发者应使用商户私钥对下行的敏感信息的密文进行解密。

同样的，大部分编程语言支持RSA私钥解密。你可以参考示例，了解如何使用您的编程语言实现敏感信息解密。

JAVA：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1public static String rsaDecryptOAEP(String ciphertext, PrivateKey privateKey)
2throws BadPaddingException, IOException {
3  try {
4    Cipher cipher = Cipher.getInstance("RSA/ECB/OAEPWithSHA-1AndMGF1Padding");
5    cipher.init(Cipher.DECRYPT_MODE, privateKey);
6    byte[] data = Base64.getDecoder().decode(ciphertext);
7    return new String(cipher.doFinal(data), "utf-8");
8  } catch (NoSuchPaddingException | NoSuchAlgorithmException e) {
9    throw new RuntimeException("当前Java环境不支持RSA v1.5/OAEP", e);
10  } catch (InvalidKeyException e) {
11    throw new IllegalArgumentException("无效的私钥", e);
12  } catch (BadPaddingException | IllegalBlockSizeException e) {
13    throw new BadPaddingException("解密失败");
14  }
15}
```

GO：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1cipherdata, _ := base64.StdEncoding.DecodeString(ciphertext)
2rng := rand.Reader
3plaintext, err := DecryptOAEP(sha1.New(), rng, rsaPrivateKey, cipherdata, nil)
4if err != nil {
5  fmt.Fprintf(os.Stderr, "Error from decryption: %s\n", err)
6  return
7}
8fmt.Printf("Plaintext: %s\n", string(plaintext))
```
