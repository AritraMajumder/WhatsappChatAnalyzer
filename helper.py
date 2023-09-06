from urlextract import URLExtract
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import pandas as pd
import emoji

def fetch_stats(selected_user,df):

    if selected_user!='Overall':
        df = df[df['user'] == selected_user]

    #fetch no of messages
    num_msgs = df.shape[0]

    #fetch no of words
    words = []
    for i in df['message']:
        words.extend(i.split())
    num_words = len(words)
    
    #fetch no of media messages
    num_media = df[df['message'] == '<Media omitted>\n'].shape[0]

    #fetch no of links
    links = []
    extractor = URLExtract()
    for i in df['message']:
        links.extend(extractor.find_urls(i))
    num_links = len(links)

    return num_msgs,num_words,num_media,num_links

def busiest(df):
    x = df['user'].value_counts().head()
    new_df = round(df['user'].value_counts()/df.shape[0]*100,2).reset_index().rename(columns={'user':'name','count':'percentage'})
    return x,new_df

#helper func to remove stopwords
def remove_stops(message):
    f = open('stop_hinglish.txt','r')
    stop_words = f.read()
    l = []
    for word in message.lower().split():
        if word not in stop_words:
            l.append(word)
    return " ".join(l)

def create_wordcloud(selected_user,df):
    if selected_user !='Overall':
        df = df[df['user']==selected_user]

    temp = df[df['user']!='group_notif']
    temp = temp[temp['message']!='<Media omitted>\n']

    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    temp['message'] = temp['message'].apply(remove_stops)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user,df):
    if selected_user !='Overall':
        df = df[df['user']==selected_user]

    temp = df[df['user']!='group_notif']
    temp = temp[temp['message']!='<Media omitted>\n']
    temp = temp[temp['message']!='You deleted this message\n']

    f = open('stop_hinglish.txt','r')
    stop_words = f.read()

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common = pd.DataFrame(Counter(words).most_common(20))
    return most_common

def emojier(selected_user,df):
    if selected_user !='Overall':
        df = df[df['user']==selected_user]

    emojis = []
    for i in df['message']:
        emojis.extend([c for c in i if c in emoji.UNICODE_EMOJI['en']])
    
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    emoji_df['Percentage'] = round(emoji_df[1]/len(emojis)*100,2)
    return emoji_df

def monthly(selected_user,df):
    if selected_user !='Overall':
        df = df[df['user']==selected_user]

    timeline = df.groupby(['year','month_num','month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i]+"-"+str(timeline['year'][i]))
    timeline['time'] = time

    return timeline

def daily(selected_user,df):
    if selected_user !='Overall':
        df = df[df['user']==selected_user]
    
    daily = df.groupby('only_date').count()['message'].reset_index()
    return daily

def week_activity_map(selected_user,df):
    if selected_user !='Overall':
        df = df[df['user']==selected_user]

    return df['day_name'].value_counts()

def month_map(selected_user,df):
    if selected_user !='Overall':
        df = df[df['user']==selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):
    if selected_user !='Overall':
        df = df[df['user']==selected_user]

    act_heat = df.pivot_table(index = 'day_name',columns = 'period',values = 'message',
    aggfunc = 'count').fillna(0)

    return act_heat

def cleaner(df):
    df = df[df['message']!='<Media omitted>\n']
    df = df[df['message']!='You deleted this message\n']
    text = ""
    for i in df['message']:
        text+=i
    text = " ".join(text.split("\n"))


    extractor = URLExtract()
    urls = extractor.find_urls(text)

    for url in urls:
        text = text.replace(url,"")
    clean_text = ""
    for i in text:
        if i.isalpha() or i.isspace():
            clean_text+=i.lower()
    return remove_stops(clean_text)

def sentiment_analyser(df):
    text = cleaner(df).split()
    em_list = []
    with open('emotions.txt','r') as file:
        for emotion in file:
            emotion = emotion.replace("\n","").replace(",","").replace("'","").strip()
            word,emotion = emotion.split(": ")
            
            for i in text:
                if i==word:
                    em_list.append(emotion) 
    counter = Counter(em_list)
    return list(counter.keys())[:5],list(counter.values())[:5] #top 5 most prevalent emotions