from qiniu import Auth, put_file, etag,put_data
import qiniu.config
#需要填写你的 Access Key 和 Secret Key
access_key = 'QgZkBoYcD5k55wN3Xdl7FBTHCRICyR-9uQNylgAU'
secret_key = 'aBhID5rZmjtT4fU8RLYHz2sge06eACrZTQgP_eyD'

def image_storage(image_data):
    #构建鉴权对象
    q = Auth(access_key, secret_key)

    #要上传的空间
    bucket_name = 'info15'

    #上传到七牛后保存的文件名
    #如果不指定,名称由七牛云维护
    # key = 'my-python-logo.png'
    key = None

    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)

    #要上传文件的本地路径
    # localfile = './11.jpg'
    # ret, info = put_file(token, key, localfile)
    ret, info = put_data(token, key, image_data)

    # print(info)
    # print(ret)

    #判断是否上传成功
    if info.status_code == 200:
        return ret.get("key")
    else:
        return ""

#测试而已
if __name__ == '__main__':

    #读取用户的图片,做为二进制流上传
    # f = open("./11.jpg",'rb')
    # image_storage(f.read())
    # f.close()

    with open("./person02.png","rb") as f:
        image_name = image_storage(f.read())
        print(image_name)
