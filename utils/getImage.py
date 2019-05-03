#提取歌曲封面图片
import mutagen
import os

#保存信息
def getInformation(fileName):
    inf = mutagen.File(fileName)
    artwork = inf.tags['APIC:'].data  # 获取歌曲图片
    title = inf.tags["TIT2"].text[0]  # 获取歌曲名
    author = inf.tags["TPE1"].text[0]  # 获取歌曲作者
    album = inf.tags["TALB"].text[0]  # 专辑名称

    # 拼接字符串得到图片地址和资源地址
    src = 'http://127.0.0.1/file/music/' + author + ' - ' + title + '.mp3'
    picture = 'http://127.0.0.1/file/music/picture/' + title + '.jpg'
    #拼接为sql语句
    item = 'insert into music(name,author,picture,src)values(\"' + title + '\",\"' + author + '\",\"' + picture + '\",\"' + src + '\");\n'
    try:
        with open('./images/' + title + '.jpg', 'wb') as img:  # 将图片保存为和歌曲同名，jpg格式的图片
           img.write(artwork)
        with open('musicList.txt', 'a') as f:
            f.write(item)
    except Exception as e:
        print('wrong!!!!!' + title)

def getFile():
    g = os.listdir(r"D:\MyServere\apache\Apache24\www\file\music")
    for fileName in g:
        if fileName.find('.mp3') != -1:
            print(fileName)
            getInformation(fileName)




if __name__== '__main__':
    getFile()