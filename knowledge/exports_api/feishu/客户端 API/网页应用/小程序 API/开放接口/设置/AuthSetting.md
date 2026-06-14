# AuthSetting

# AuthSetting

名称 | 类型 | 描述
--|--|--
 scope.userInfo | boolean | 是否授权用户信息，对应接口 tt.getUserInfo |
 scope.userLocation | boolean | 是否授权地理位置，对应接口 tt.getLocation, tt.chooseLocation | 
 scope.camera | boolean | 是否授权摄像头功能，对应<camera>组件 | 
 scope.record | boolean | 是否授权麦克风功能，对应接口 tt.getRecorderManager.start | 
 scope.writePhotosAlbum | boolean | 是否授权保存到相册,  对应接口 tt.saveImageToPhotosAlbum, tt.saveVideoToPhotosAlbum **(PC端无此权限)**| 
 scope.clipboard | boolean | 是否授权剪贴板权限，对应接口 tt.setClipboardData,tt.getClipboardData |
  scope.bluetooth | boolean | 是否授权蓝牙权限，对应接口 tt.openBluetoothAdapter |
