import openai
import requests
from datetime import date
from bs4 import BeautifulSoup
import time

def get_mood(text):
    openai.api_key = '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'

    response = openai.ChatCompletion.create(
        #model="gpt-3.5-turbo",
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": "Respond with very good, good, bad, very bad, or neutral." + text
            },
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0]['message']['content']

def summarize_text(text, title):
    openai.api_key = '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'

    response = openai.ChatCompletion.create(
        #model="gpt-3.5-turbo",
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": "summarize this text into three sentences." + text + ". If it is not about a satellite company sumarize this instead" + title
            },
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0]['message']['content']

def get_articles(date, company, limit=100):
    class Article:
        def __init__(self, title, date, content, url):
            self.title = title
            self.date = date
            self.content = content
            self.url = url
    url = ('https://newsapi.org/v2/everything?'
            'q=' + company + '&'
            'from=' + date + 'T00:00:00'+'&'
           # 'to=2023-10-26&'
            'sortBy=relevancy&'
            'language=en&'
            'searchin=title&'
            'apiKey=f7427272534142928078f0552dfcf127&'
            'pageSize=' + str(limit))

    response = requests.get(url).json()
    num_results = response['totalResults']
    if num_results > 100:
        num_results = 100
    if limit < num_results:
        num_results = limit
    articles_list = []
    if num_results != 0:
        for i in range(num_results):
            print(response['articles'][i])
            articles_list.append(Article(response['articles'][i]['title'],
                                         response['articles'][i]['publishedAt'],
                                         response['articles'][i]['content'],
                                         response['articles'][i]['url']))
    else:
        articles_list = 0

    return articles_list

def getTextFromUrl(url):
    response = requests.get(url)

    # Step 2: Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Step 3: Parse the web page content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Step 4: Find and extract the data you need
        news = []
        for article in soup.find_all('p'):
            news.append(article.text)
        for article in soup.find_all('h2'):
            news.append(article.text)
        for article in soup.find_all('article'):
            news.append(article.text)
        # Step 5: Print or process the extracted data
        news = news[0].replace('\n', '').replace('\r', '')
        return(news)

    else:
        return 'failed'

def saveNewsSummary(summary):
    url = 'https://aero-intel-server.onrender.com/save-news'
    result = requests.post(url, json=summary)
    return result

def updateCompanyStats(stats):
    url = 'https://aero-intel-server.onrender.com/update-stats'
    result = requests.post(url, json=stats)
    return result

def get_summary(date, company_list):
    for company in company_list:
        summary = []
        print(company, '-------------------------------------------------------------')
        article_dump = get_articles(date, company, 5)
        if article_dump == 0:
            continue

        for i in range(len(article_dump)):
            url = article_dump[i].url
            text = getTextFromUrl(url)
            print(text)
            summarized = summarize_text(text, article_dump[i].title)
            print(company + ' text is being sumarized')
            if text == 'failed':
                continue
            summary.append({
                "company": company,
                "headline": article_dump[i].title,
                "link": url,
                "summary": summarized
            })
        result = saveNewsSummary(summary)
        print(result)

today = date.today()
date_today = today.strftime("%Y-%m-%d")
company_list = ['Intelsat', 'SpaceX', 'Eutelsat', 'Viasat']

Intelsat_mood_count = {'very bad' : 0, 'bad' : 0, 'neutral' : 0, 'good' : 0, 'very good': 0}
SpaceX_mood_count = {'very bad' : 0, 'bad' : 0, 'neutral' : 0, 'good' : 0, 'very good': 0}
Eutelsat_mood_count = {'very bad' : 0, 'bad' : 0, 'neutral' : 0, 'good' : 0, 'very good': 0}
Viasat_mood_count = {'very bad' : 0, 'bad' : 0, 'neutral' : 0, 'good' : 0, 'very good': 0}
mood_count_dict = {'Intelsat' : Intelsat_mood_count, 'SpaceX' : SpaceX_mood_count, 'Eutelsat' : Eutelsat_mood_count, 'Viasat' : Viasat_mood_count}

for company in company_list:
    print(company, '-------------------------------------------------------------')
    article_dump = get_articles('2023-10-26', company)
    summary = []
    if article_dump == 0:
        continue

    for i in range(len(article_dump)):
        print(article_dump[i].title)
        print(article_dump[i].content)
        print(article_dump[i].date)
        print(article_dump[i].url)
        mood = get_mood(article_dump[i].content).lower()
        print(mood)
        mood_count_dict[company][mood] += 1
        print(mood_count_dict[company])
        print('\n')
        time.sleep(5)

        url = article_dump[i].url
        text = getTextFromUrl(url)
        print(text)
        summarized = summarize_text(text, article_dump[i].title)
        print(company + ' text is being sumarized')
        if text == 'failed':
            continue
        summary.append({
            "company": company,
            "headline": article_dump[i].title,
            "link": url,
            "summary": summarized
        })
    result = saveNewsSummary(summary)

    data = {
        "company": company,
        "veryBad": mood_count_dict[company]['very bad'],
        "bad": mood_count_dict[company]['bad'],
        "neutral": mood_count_dict[company]['neutral'],
        "good": mood_count_dict[company]['good'],
        "veryGood": mood_count_dict[company]['very good'],
    }
    x = updateCompanyStats(data)