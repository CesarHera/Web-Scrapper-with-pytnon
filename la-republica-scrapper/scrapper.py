import os, datetime, requests
import lxml.html as html


WEBSITE: str = 'https://www.larepublica.co/'

XPATH_LINK_TO_NEWS: str = '//text-fill/a/@href'


def remove_characters(str):
    characters = (
        '\"',
        '?',
        '|',
        '\\',
        '', #You need this line because the double backslash takes the next element. Try removing it
        '/',
        ':',
        '<',
        '>',
        '*'
    )

    for character in characters:
        str = str.replace(character, '')

    return str


def get_title(parsed, link):
    XPATH_NEWS_TITLE: str = '//div[@class="mb-auto"]/text-fill/span/text()'
    XPATH_NEWS_TITLE2: str = '//div[@class="wrap-caja-fuerte mb-5"]/h2/text()'
    XPATH_NEWS_TITLE3: str = '//div[@class="col order-2"]/h2/span/text()'
    XPATH_NEWS_TITLE4: str = '//h1[@class="articleTitle large"]/a/text()'
    XPATH_NEWS_TITLE5: str = '//header[@class="cell"]/h1/text()'

    title = parsed.xpath(XPATH_NEWS_TITLE)
    if not title:
        title = parsed.xpath(XPATH_NEWS_TITLE2)
    if not title:
        title = parsed.xpath(XPATH_NEWS_TITLE3)
    if not title:
        title = parsed.xpath(XPATH_NEWS_TITLE4)
    if not title:
        title = parsed.xpath(XPATH_NEWS_TITLE5)
    if not title:
        return f'Title NOT FOUNDED in: {link}'

    return title


def get_summary(parsed, link):
    XPATH_NEWS_SUMMARY: str = '//div[@class="lead"]/p/text()'
    XPATH_NEWS_SUMMARY2: str = '//p[@class="lead"]/text()'
    XPATH_NEWS_SUMMARY3: str = '//p[@class="intro hide-for-small show-for-large"]/text()'
    XPATH_NEWS_SUMMARY4: str = '//div[@class="wrap-caja-fuerte mb-5"]/p[1]/strong/text()' #caja-fuerte

    summary = parsed.xpath(XPATH_NEWS_SUMMARY)
    if not summary:
        summary = parsed.xpath(XPATH_NEWS_SUMMARY2)
    if not summary:
        summary = parsed.xpath(XPATH_NEWS_SUMMARY3)
    if not summary:
        summary = parsed.xpath(XPATH_NEWS_SUMMARY4)
    if not summary:
        return f'Summary NOT FOUNDED in: {link}'
    
    return summary


def get_body(parsed, link):
    XPATH_NEWS_BODY: str = '//div[@class="html-content"]/p[not(@class)]/text()' #common
    XPATH_NEWS_BODY2: str = '//div[@class="wrap-caja-fuerte mb-5"]/p[2]/text()' #caja-fuerte
    XPATH_NEWS_BODY3: str = '//div[@class="postContent"]/div[@class="cell"]/p[not(@class)]/text()' #agropecuario
    XPATH_NEWS_BODY4: str = '//div[@class="postContent cell"]/p[not(@class)]/text()' #actualidad
    
    body = parsed.xpath(XPATH_NEWS_BODY)
    if not body:
        body = parsed.xpath(XPATH_NEWS_BODY2)
    if not body:
        body = parsed.xpath(XPATH_NEWS_BODY3)
    if not body:
        body = parsed.xpath(XPATH_NEWS_BODY4)
    if not body:
        return f'Body NOT FOUNDED in :{link}'

    return body


def parse_news(link, today):
    if '/analisis/' in link: #We do not want these
        return
    elif '/podcast/' in link: #We do not want these
        return
    else:
        try:
            response = requests.get(link)
            if response.status_code == 200:
                news = response.content.decode('utf-8')
                parsed = html.fromstring(news)
            
                title = get_title(parsed, link)[0]
                file_title = remove_characters(title)
                summary = get_summary(parsed, link)[0]
                body = get_body(parsed, link)
                


                with open(f'news/{today}/{file_title}.txt', mode='w', encoding='UTF-8') as f:
                    f.write(link)
                    f.write('\n')
                    f.write(title.replace('\\', ''))
                    f.write('\n\n')
                    f.write(summary)
                    f.write('\n\n\n')
                    for paragraph in body:
                        f.write(paragraph)

            else:
                raise ValueError(f'Error: {response.status_code}')
        except ValueError as ve:
            print(ve)


def parse_home():
    try:
        response = requests.get(WEBSITE)
        if response.status_code == 200:
            home = response.content.decode('utf-8')
            parsed = html.fromstring(home)

            news_links = parsed.xpath(XPATH_LINK_TO_NEWS)

            today = datetime.date.today().strftime('%d-%m-%Y')

            if not os.path.isdir(f'news/{today}'):
                os.mkdir(f'news/{today}')

                for link in news_links:
                    parse_news(link, today)

        else:
            raise ValueError(f'Error: {response.status_code}')
    except ValueError as ve:
        print(ve)


def run():
    parse_home()
    

if __name__ == '__main__':
    run()