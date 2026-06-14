# 获取用户ip指引

# 获取用户ip指引

路径：产品文档/支付产品/H5支付/附录/获取用户ip指引

## 背景介绍

H5支付要求商户在统一下单接口中上传用户真实ip地址“payer_client_ip”，为保证微信端获取的用户ip地址与商户端获取的一致，提供了以下获取用户ip的指引，希望对大家有所帮助。 

## 没有代理的情况

在商户的前端接入层没有做代理的情况下获取ip的方式比较简单，直接获取'REMOTE_ADDR '即可。

代码示例
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1function get_client_ip(){
2	$cip = "unknown";
3	if ($_SERVER['REMOTE_ADDR']){
4		$cip = $_SERVER['REMOTE_ADDR']
5	}elseif (getenv("REMOTE_ADDR")){
6		$cip = getenv("REMOTE_ADDR");
7	}
8	return $ip
9}           
```

## 有代理的情况

在有代理的情况下，因为要代替客户端去访问服务器，所以，当请求包经过反向代理后，在代理服务器这里这个IP数据包的IP包头做了修改，最终后端WEB服务器得到的数据包的头部源IP地址是代理服务器的IP地址。这样一来，后端服务器的程序就无法获取用户的真实ip。

nginx有代理的情况:

在nginx中配置中加入
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1proxy_set_header Host  $host;
2proxy_set_header X-Real-IP $remote_addr;
3proxy_set_header X-Real-Port $remote_port;
4proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
```

Apache有代理的情况：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1vi /usr/local/apache/conf/httpd.conf
2Include conf/extra/httpd-remoteip.conf
3vi /usr/local/apache/conf/extra/httpd-remoteip.conf
4LoadModule remoteip_module modules/mod_remoteip.so 
5RemoteIPHeader X-Forwarded-For 
6RemoteIPinternalProxy 127.0.0.1 
```

代码示例
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1string GetClientIp(CgiInput* poInput) { 
2	string client_ip = "";  
3	string strClientIPList;  
4	GetHttpHeader("X-Forwarded-For", strClientIPList);
5	
6  if (strClientIPList.empty()){
7	GetHttpHeader("X-Real-IP", strClientIPList);} 
8
9  if (!strClientIPList.empty()){
10	size_t iPos = strClientIPList.find( "," );
11	if( iPos != std::string::npos ){
12	client_ip = strClientIPList.substr( iPos );}
13  else{
14		client_ip = strClientIPList;
15		}
16	}
17	
18  if (client_ip.empty()){
19	GetHttpHeader("PROXY_FORWARDED_FOR", strClientIPList);
20	// 需进行兼容  
21	if(strClientIPList.empty()){
22		client_ip = getRemoteAddr();
23	}else{
24		size_t iPos = strClientIPList.find( "," );
25		if( iPos != std::string::npos ) { 
26			client_ip = strClientIPList.substr( iPos );
27		} 
28		else{
29				client_ip = strClientIPList;
30		}
31	}
32}
33
34	if(!MMPayCommFunc::IsIp(client_ip))
35	client_ip = getRemoteAddr();
36	return client_ip;
37} 
```
