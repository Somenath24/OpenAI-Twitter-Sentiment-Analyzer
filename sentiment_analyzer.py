# Import the required libraries
import PyPDF2
import requests
import PySimpleGUI as sg
import os
import openai
import tweepy as tw
import pandas as pd
os.chdir("path to keys")

# Define a class for the PDF Summarizer
class sentiment_analyzer:
    # Define the instance variables for the class
    def __init__(self):
        self.number_of_tweet1 = 0
        self.hashtag1 = ''

    # Open the PDF file
    def read_twitter(self, hashtag, number_of_tweet):
        no=number_of_tweet
        search_words=hashtag
        no=int(no)
        file1 = open("twitter_cred.txt","r+")

        with open("twitter_cred.txt") as file:
            lines = [line.rstrip() for line in file]
        # Read the API key
        consumer_key=lines[0]
        consumer_secret=lines[1]
        access_token=lines[2]
        access_token_secret=lines[3]
        auth = tw.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tw.API(auth, wait_on_rate_limit=True)
    
        tweets = tw.Cursor(api.search_tweets,result_type='recent',
                    q=search_words,
                    lang="en").items(no)
        

        users_locs = [[tweet.created_at, tweet.id, tweet.user.screen_name,tweet.text]
                for tweet in tweets]
        twitterDf = pd.DataFrame(data=users_locs,
                        columns=['location', "id","user","Content"])
        return(twitterDf)
        
    
    # Run the OpenAI summarization model
    def OpenAIrun(self, messages):
        # Change the current working directory
        # Open the API key file
        file1 = open("key.txt","r+")
        # Read the API key
        api_key=file1.read()
        # Set the OpenAI API key
        openai.organization="org id"
        openai.api_key = api_key
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Sentiment analysis of the following text, give only if it is positive, negative, or neutral and either happy, sad, anger, or surprise :  " + messages+"",
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        if 'choices' in response:
            if len(response['choices']) > 0:
                ret = response['choices'][0]['text']
            else:
                ret = 'No responses'
        else:
            ret = 'No responses'

        return ret
    
    def run_OpenAI(self, twitterDf):
        outlist=[]
        for index, row in twitterDf.iterrows():
            tweets=row['Content']
            sentiment=self.OpenAIrun(tweets)
            #sentiment="happy"
            outlist.append(sentiment)
        twitterDf['sentiment']=outlist
        return(twitterDf)
        
            


# Define the layout of the PySimpleGUI window

out_col1=[[sg.Text('Tweets')],[sg.Output(size=(80, 20),key='tweets')]]
out_col2=[[sg.Text('Sentiment')],[sg.Output(size=(80, 20),key='out_sentiment')]]
layout = [
    [sg.Text('Enter the hashtag you want to search for')],
    [sg.Input(key='hashtag')],
    [sg.Text('Enter number of data values needed')],
    [sg.Input(key='no_of_tweets')],
    [sg.Button('submit')],  
    [sg.Column(out_col1),
     sg.Column(out_col2)],
]

# Create the PySimpleGUI window
window = sg.Window('Sentiment Analyzer', layout)

# Create an instance of the PDFSummarizer class
sentiment_analyzer = sentiment_analyzer()

# Start the event loop for the window
while True:
    event, values = window.read()
    
    if event == sg.WIN_CLOSED:
        break

    if event == 'submit':
        #number_of_tweet=5
        hashtag=values['hashtag']
        number_of_tweet=values['no_of_tweets']
        twitterdf=sentiment_analyzer.read_twitter(hashtag, number_of_tweet)
        twitterdf=sentiment_analyzer.run_OpenAI(twitterdf)
        #print(pdf_summarizer.text)
        #print(summary)
        window['tweets'].update(twitterdf['Content'])
        window['out_sentiment'].update(twitterdf['sentiment'])

window.close()
