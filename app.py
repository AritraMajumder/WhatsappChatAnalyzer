import streamlit as st
import preprocessor,helper
import matplotlib.pyplot as plt
import seaborn as sb

st.sidebar.title("Whatsapp Chat Analyzer")


uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    #st.text(data)
    df = preprocessor.preprocess(data)

    #st.dataframe(df)

    #fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notif')
    user_list.sort()
    user_list.insert(0,"Overall")
    selected_user = st.sidebar.selectbox("Select user to analyse",user_list)

    if st.sidebar.button("Show Analysis"):
        #general stats
        num_msgs,num_words,num_media,num_links = helper.fetch_stats(selected_user,df)
        st.title("Top Statistics")
        col1,col2,col3,col4 = st.columns(4)
        with col1:
            st.header("Total Messages")
            st.title(num_msgs)
        with col2:
            st.header("Total Words")
            st.title(num_words)
        with col3:
            st.header("Media Shared")
            st.title(num_media)
        with col4:
            st.header("Links Shared")
            st.title(num_links)
        #monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly(selected_user,df)
        fig,ax = plt.subplots()
        ax.plot(timeline['time'],timeline['message'],color='green')
        plt.xticks(rotation = 'vertical')
        st.pyplot(fig)

        #daily timeline
        st.title("Daily Timeline")
        timeline = helper.daily(selected_user,df)
        fig,ax = plt.subplots()
        ax.plot(timeline['only_date'],timeline['message'],color='green')
        plt.xticks(rotation = 'vertical')
        st.pyplot(fig)

        #activity map
        st.title("Activity Map")
        col1,col2 = st.columns(2)

        with col1:
            st.header("Busiest Day")
            busy = helper.week_activity_map(selected_user,df)
            fig,ax = plt.subplots()
            ax.bar(busy.index,busy.values)
            plt.xticks(rotation = 'vertical')
            st.pyplot(fig)
        
        with col2:
            st.header("Busiest Month")
            busy = helper.month_map(selected_user,df)
            fig,ax = plt.subplots()
            ax.bar(busy.index,busy.values,color = 'orange')
            plt.xticks(rotation = 'vertical')
            st.pyplot(fig)


        #busiest users
        if selected_user =='Overall':
            st.title("Busiest Users")
            x,new_df = helper.busiest(df)
            fig,ax = plt.subplots()

            col1,col2 = st.columns(2)

            with col1:
                ax.bar(x.index,x.values,color = 'red')
                plt.xticks(rotation = 'vertical')
                st.pyplot(fig)
            
            with col2:
                st.dataframe(new_df)
        
        #wordcloud
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user,df)
        fig,ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        #most common words
        mcw_df = helper.most_common_words(selected_user,df)

        fig,ax = plt.subplots()

        ax.barh(mcw_df[0],mcw_df[1],color = 'red')
        plt.xticks(rotation = 'vertical')

        st.title("Most Common Words")
        st.pyplot(fig)

        #emoji analysis
        emoji_df = helper.emojier(selected_user,df).rename(columns={0:'Emoji',1:'Count'})
        st.title("Emoji Analysis")

        col1,col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig,ax = plt.subplots()

            ax.bar(emoji_df['Emoji'],emoji_df['Count'],color = 'green')
            plt.xticks(rotation = 'vertical')
            st.pyplot(fig)
        

        st.title("Weekly Activity")
        act_heat = helper.activity_heatmap(selected_user,df)
        fig,ax = plt.subplots()
        ax = sb.heatmap(act_heat)
        st.pyplot(fig)

        #sentiment analysis
        if selected_user!='Overall':
            st.title("Sentiment Analysis")
            df = df[df['user']==selected_user]

            labels,sizes = helper.sentiment_analyser(df)

            # fig,ax = plt.subplots()
            # ax.barh(labels,sizes,color = 'red')
            # plt.xticks(rotation = 'vertical')
            # st.pyplot(fig)
            fig,ax = plt.subplots()
            ax.pie(sizes,labels = labels,autopct = '%1.1f%%')
            ax.axis('equal')
            st.pyplot(fig)
