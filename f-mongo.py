from crypt import methods
from flask import Flask, render_template, request
from flask_pymongo import PyMongo
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from textblob import TextBlob

app = Flask(__name__)

client = MongoClient()
client = MongoClient('localhost',27017)
db = client.flask

# app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/flask'
# mongo = PyMongo(app)

@app.route('/', methods=['GET','POST'])
def home():
    
    resp = flipkart('watches')
    soup = BeautifulSoup(resp,'html.parser')
    a_tags = soup.find_all('a',{'class':'_2UzuFa'})
    urls = list()
    for a in a_tags:
        urls.append('https://www.flipkart.com'+a['href'])
    products = list()
    for url in urls:
        product = dict()
        page_soup = BeautifulSoup(requests.get(url).text,'html.parser')

        name = page_soup.find('h1',{'class':'yhB1nd'})
        product['name'] = name.text
        
        price = page_soup.find('div',{'class':'_30jeq3 _16Jk6d'})
        product['price'] = price.text

        review_count = page_soup.find('span',{'class':'_2_R_DZ'})
        if review_count is None:
            product['review_count'] = '0 Review and 0 Ratings'
        else:
            product['review_count'] = review_count.text

        review = page_soup.find('div',{'class':'_2c2kV- _33R3aa'})
        if review is None:
            product['review'] = '0 Review'
        else:
            product['review'] = review.text

        review_sentiment = review.text.split(",")
        sentiment_analysed = list()
        for i in review_sentiment:
            ins = dict()
            s = TextBlob(i)
            op = s.sentiment.polarity
            if op<0:
                sentiment = "Negative"
            elif op == 0:
                sentiment = "Neutral"
            else:
                sentiment = "Positive"
            
            ins['Review'] = i
            ins['Sentiment'] = sentiment
            sentiment_analysed.append(ins)

        if sentiment_analysed is None:
            pass
        else:
            product['Sentiment'] = sentiment_analysed

        products.append(product)
        
        

    # return {'urls':urls}
    for prod in products:
        db.records.insert_one(prod)

    return {'products':products}





@app.route('/flipkart', methods=['GET'])
def flipkart(product):
    headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    params = (
        ('q', product),
        ('as', 'on'),
        ('as-show', 'on'),
        ('otracker', 'AS_Query_OrganicAutoSuggest_3_3_na_na_na'),
        ('otracker1', 'AS_Query_OrganicAutoSuggest_3_3_na_na_na'),
        ('as-pos', '3'),
        ('as-type', 'RECENT'),
        ('suggestionId', 'watches'),
        ('requestId', 'e42fd848-7596-4602-90d2-29406e3a85d4'),
        ('as-backfill', 'on'),
    )

    response = requests.get('https://www.flipkart.com/search', headers=headers, params=params, )
    return(response.text)




if __name__ == "__main__":
    app.run(debug=True)