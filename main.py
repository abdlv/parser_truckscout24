import json
import os
import time
import requests
from bs4 import BeautifulSoup


def get_links():
    count = 0
    product_links = []
    main_url = 'https://www.truckscout24.de'
    while True:
        count += 1
        req = requests.get(f'https://www.truckscout24.de/transporter/gebraucht/kuehl-iso-frischdienst/renault'
                           f'?currentpage={count}')
        main_soup = BeautifulSoup(req.text, 'html.parser')

        if main_soup.find('p', class_='sc-font-bold sc-font-l') is not None:
            print('ВСЕ')
            break

        url = main_soup.find('div', class_='ls-elem ls-elem-gap').find('div', class_='ls-titles').find('a')['href']
        full_url = main_url + url
        product_links.append(full_url)

    return product_links


def get_data(product_links):
    data = {'ads': []}
    mileage = 0
    color = ''
    power = 0
    dir_path = os.path.dirname(os.path.realpath(__name__))

    for link in product_links:
        print(link)
        product_data = requests.get(link)
        product_soup = BeautifulSoup(product_data.text, 'html.parser')

        product_id = time.time()
        try:
            title = product_soup.find('h1', class_='sc-ellipsis sc-font-xl').text
            print(title)
        except:
            title = ''

        try:
            price = int(product_soup.find('h2', class_='sc-highlighter-4 sc-highlighter-xl sc-font-bold').
                        text.replace('€', '').replace('.', '').replace(',-', ''))
        except ValueError:
            price = 0
        print(price)

        chars = product_soup.find_all('div', class_='itemspace')
        for char in chars:
            char_name = char.find('div', class_='itemlbl')
            if char_name == 'Kilometer':
                try:
                    mileage = char.find('div', class_='itemval').text.replace('km', '')
                except:
                    pass
        print(mileage)

        tech_details = product_soup.find('ul', class_='columns').find_all('li')
        for tech_detail in tech_details:
            tech_detail_name = tech_detail.find('div', class_='sc-font-bold').text
            if tech_detail_name == 'Farbe':
                try:
                    color = tech_detail.find_all('div')[-1].text
                    print(color)
                except:
                    pass
            if tech_detail_name == 'Leistung':
                try:
                    power = tech_detail.find_all('div')[-1].text.split('kW')[0]
                    print(power)
                except:
                    pass
        try:
            description = product_soup.find('div', class_='sc-expandable-box__content').text
            print(description)
        except:
            description = ''

        image_counter = 0
        if os.path.exists(fr'{dir_path}/{int(product_id)}'):
            pass
        else:
            os.mkdir(fr'{dir_path}/{int(product_id)}')

        image_containers = product_soup.find('div', class_='as24-carousel__container').\
            find_all('div', class_='as24-carousel__item')

        for image_container in image_containers:
            image_counter += 1
            if image_counter > 3:
                break
            image_url = image_container.find('img')['data-src']
            print('-----------------------------------------',image_url)
            image = requests.get(image_url)
            with open(fr'{dir_path}\{int(product_id)}\{str(image_counter)}.jpg', 'wb') as f:
                f.write(image.content)

        data['ads'].append({'id': int(product_id),
                            'href': str(link),
                            'title': str(title),
                            'price': int(price),
                            'mileage': int(mileage),
                            'color': str(color),
                            'power': int(power),
                            'description': str(description)})

    return data


if __name__ == '__main__':
    links = get_links()
    data_json = get_data(links)
    with open('data.txt', 'w') as f:
        json.dump(data_json, f)

    print(data_json)
