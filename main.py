from pycorenlp import StanfordCoreNLP
from bs4 import BeautifulSoup
import requests 
import time
import re
import os 


send_meth = 'sendMessage'
token = '772758152:AAEPfekp2KJy01ad2BbDbd3zjdQEw-3qmN8'
base_url = 'https://api.telegram.org/bot{}'.format(token)
user = '70319882'

def send_request(offset=''):
    respons = requests.get(
        base_url + '/getUpdates?offset={}'.format(offset)).json()
    if not respons['ok']:
        return []
    return respons['result']


def get_updates():
    last_update = ''
    while True:
        time.sleep(1)
        resp = send_request(offset=last_update)
        if not resp:
            continue
        last_update = resp[-1]['update_id'] + 1
        for item in resp:
            yield {
                'text': item['message']['text'],
                'user': item['message']['from']
            }

def send_post(token, send_meth):
    response = requests.post(
    url='https://api.telegram.org/bot{0}/{1}'.format(token, send_meth),
    data={'chat_id': user, 'text': final_sentiment }
    ).json()



def tweeter_scrapper(tweeter_id):

    list_of_dirty_tweets = []
    clear_list_of_tweets = []
    tweeter_url = 'https://twitter.com/{}'.format(tweeter_id)


    response = requests.get(tweeter_url)
    soup = BeautifulSoup(response.content , 'lxml')
    all_tweets = soup.find_all('div',{'class':'tweet'})

    for tweet in all_tweets:
        content = tweet.find('div',{'class':'content'})
        message = content.find('div',{'class':'js-tweet-text-container'}).text.replace("\n"," ").strip()
        list_of_dirty_tweets.append(message)
    for dirty_tweet in list_of_dirty_tweets:
        dirty_tweet = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', dirty_tweet, flags=re.MULTILINE)
        dirty_tweet = re.sub(r'(#)\w*', '', dirty_tweet, flags=re.MULTILINE)
        dirty_tweet = re.sub(r'(.twitter.com/)\w*', '', dirty_tweet, flags=re.MULTILINE)
        dirty_tweet = re.sub(r'\.', '', dirty_tweet, flags=re.MULTILINE)
        dirty_tweet = re.sub(r'(@)\w*', '', dirty_tweet, flags=re.MULTILINE)
        dirty_tweet = re.sub(r'\?', '', dirty_tweet, flags=re.MULTILINE)
        dirty_tweet = re.sub(r'\.', '', dirty_tweet, flags=re.MULTILINE)
        dirty_tweet = re.sub(r'\-', '', dirty_tweet, flags=re.MULTILINE)
        dirty_tweet = re.sub(r'\!', '', dirty_tweet, flags=re.MULTILINE)
        dirty_tweet = re.sub(r'\&', '', dirty_tweet, flags=re.MULTILINE)
        dirty_tweet = re.sub(r'\:', '', dirty_tweet, flags=re.MULTILINE)

        dirty_tweet = dirty_tweet.replace(u'\xa0…', u'')
        dirty_tweet = dirty_tweet.replace(u'\xa0', u'')
        clear_list_of_tweets.append(dirty_tweet)
    print(clear_list_of_tweets)
    return clear_list_of_tweets


if __name__ == "__main__":
    for message in get_updates():
        list_sentiment_result = []
        tweeter_username = message['text']
        tweeter_scrapper(tweeter_username)
        for any_tweet in tweeter_scrapper(tweeter_username):
            nlp = StanfordCoreNLP('http://localhost:9000')
            res = nlp.annotate(any_tweet ,
                    properties={
                    'annotators': 'sentiment',
                    'outputFormat': 'json',
                    'timeout': 1000,
                })
                
            for s in res['sentences']:
                result_str = str(s["sentiment"])
                list_sentiment_result.append(result_str)
                print(list_sentiment_result)
            positive_count = list_sentiment_result.count('Positive')
            negative_count = list_sentiment_result.count('Negative')
            very_negative_count = list_sentiment_result.count('Verynegative')
            very_positive_count = list_sentiment_result.count('Verypositive')
            print( 'counts of positive tweet: ' + str(positive_count))
            print( 'counts of very positive tweet: ' + str(very_positive_count))
            print( 'counts of negative tweet: ' +  str(negative_count))
            print( 'counts of very negative tweet: ' + str(very_negative_count))
        if negative_count + very_negative_count > positive_count + very_positive_count:
            final_sentiment = 'This person posts NEGATIVE tweet in his/her/other 20 last tweets'
            send_post(token, send_meth)
        elif negative_count + very_negative_count < positive_count + very_positive_count:
            final_sentiment = 'This person posts POSITIVE tweet in his/her/other 20 last tweets'
            send_post(token, send_meth)

