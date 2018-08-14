#-*-coding:utf-8-*-
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import re
import jieba     #分词包
import pandas as pd
import numpy
import matplotlib
import matplotlib.pyplot as plt
from wordcloud import WordCloud  #词云包
html=urlopen('https://movie.douban.com/cinema/nowplaying/hangzhou/')
html_obj=bs(html.read(),'html.parser')
#在div id='nowplaying'标签开始是我们想要的数据，里面有电影的名称
#评分，主演等信息
nowplaying_movie=html_obj.find_all('div',id='nowplaying')
#其中nowplaying_movie_list是一个列表，可以用print(nowplaying_movie_list[0]查看里面的内容)
nowplaying_movie_list=nowplaying_movie[0].find_all('li',class_='list-item')
#print(nowplaying_movie_list[0])
#data-subject属性中放了电影的id号码，而在img标签的alt属性里面放了电影的名字，因此我们就通过这两个属性来获取电影的名字和id
nowplaying_list=[]
for item in nowplaying_movie_list:
    nowplaying_dict={}
    nowplaying_dict['id']=item['data-subject']
    for tag_img_item in item.find_all('img'):
        nowplaying_dict['name']=tag_img_item['alt']
    nowplaying_list.append(nowplaying_dict)
#其中列表nowplaying_list中存放了最新电影的id和名称，可以使用print（nowplaying_list）进行查看
print(nowplaying_list)
#对网址进行解析，打开短评页面的html代码，关于评论的数据是在div标签的comment属性下面
#因此对此标签进行解析
requrl = ('https://movie.douban.com/subject/' + nowplaying_list[0]['id'] + '/comments' +'?' +'start=0' + '&limit=20')
resp=urlopen(requrl)
soup=bs(resp.read(),'html.parser')
comment_div_lits=soup.find_all('div',class_='comment')
#此时在comment_div_lits列表中存放的就是div标签和comment属性下面的html代码。
#对comment_div_lits代码中的html代码继续进行解析
eachCommentList=[]
for item in comment_div_lits:
        eachCommentList.append(item.find_all('p'))
#print(eachCommentList)


#数据清洗
comment=''
for k in range(len(eachCommentList)):
    comment=comment+(str(eachCommentList[k])).strip()
#print(comment)
#将标点符号清除，所用的方法是正则表达式
#python中的正则表达式是通过re模块来实现的
pattern =re.compile(r'[\u4e00-\u9fa5]+')
filterdata=re.findall(pattern,comment)
cleaned_comments=''.join(filterdata)
print(cleaned_comments)
#此时数据变得干净多了，要进行词频统计，先要进行中文分词操作。使用结巴分词
segment=jieba.lcut(cleaned_comments)
words_df = pd.DataFrame({'segment':segment})
print(words_df.ix[:10])
#以上词在很多时候都是高频词汇，并没有实际意义，所以对它们进行清除
stopwords=pd.read_csv('/home/jethro/文档/chineseStopWords.txt',index_col=False,quoting=3,sep='\t',names=['stopword'],encoding='ISO-8859-1')
#quoting=3 全不引用
words_df=words_df[~words_df.segment.isin(stopwords)]
print(words_df.head())
words_stat=words_df.groupby(by=['segment'])['segment'].agg({'计数':numpy.size})
words_stat=words_stat.reset_index().sort_values(by=['计数'],ascending=False)
print(words_stat.head())
matplotlib.rcParams['figure.figsize']=(10.0,5.0)
wordcloud=WordCloud(font_path='simhei.ttf',background_color='white',max_font_size=80)#指定字体类型，字体大小和字体颜色
word_frequence={x[0]:x[1] for x in words_stat.head(1000).values}
word_frequence_list=[]
for key in word_frequence:
    temp=(key,word_frequence[key])
    word_frequence_list.append(temp)
wordcloud=wordcloud.fit_words(word_frequence_list)
plt.show(wordcloud)
