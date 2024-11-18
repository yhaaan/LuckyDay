from flask import Flask, render_template, request
from lunarcalendar import Converter, Solar
from bs4 import BeautifulSoup as bs
import urllib.request as ur
from datetime import datetime
import re

app = Flask(__name__)

# 별자리 리스트
star = ["물병자리", "물고기자리", "양자리", "황소자리", "쌍둥이자리", 
        "게자리", "사자자리", "처녀자리", "천칭자리", "전갈자리", 
        "사수자리", "염소자리"]

# 띠 리스트
animal = ["쥐띠", "소띠", "호랑이띠", "토끼띠", "용띠", "뱀띠", 
          "말띠", "양띠", "원숭이띠", "닭띠", "개띠", "돼지띠"]

# 이모지 리스트
emoji = ['♒', '♓', '♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑',
         '🐭', '🐮', '🐯', '🐇', '🐉', '🐍', '🦄', '🐑', '🐵', '🐔', '🐶', '🐷']

# 별자리 계산 함수
def get_zodiac_sign(month, day):
    if (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "물병자리"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "물고기자리"
    elif (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "양자리"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "황소자리"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "쌍둥이자리"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "게자리"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "사자자리"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "처녀자리"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "천칭자리"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "전갈자리"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "사수자리"
    else:
        return "염소자리"
    
def get_animal_sign(year, month, day):
    # 양력 생일을 음력으로 변환
    solar_date = Solar(year, month, day)
    lunar_date = Converter.Solar2Lunar(solar_date)

    # 음력 연도를 사용해 띠를 계산 (쥐띠 기준으로 -4 보정)
    lunar_year = lunar_date.year
    return animal[(lunar_year - 4) % 12]

# 별자리 운세 반환 함수
def starin(s_name):
    soup = bs(ur.urlopen("https://search.naver.com/search.naver?where=nexearch&sm=tab_etc&qvt=0&query=%EB%B3%84%EC%9E%90%EB%A6%AC%20%EC%9A%B4%EC%84%B8").read(), 'html.parser')

    star_url = soup.find_all('ul', {"class": "sign_lst"})[0].find_all('li')[star.index(s_name)].find_all('a')[0].get('href')
    soup = bs(ur.urlopen("https://search.naver.com/search.naver?where" + star_url).read(), 'html.parser')

    text = soup.find_all('p', {"class": "text _cs_fortune_text"})[0].text
    match = re.match(r"(\d{1,2}월 \d{1,2}일 ~ \d{1,2}월 \d{1,2}일)(.*)", text)
    if match:
        date_info = match.group(1)
        main_text = match.group(2).strip().replace(". ", ".\n")
    else:
        date_info = ""
        main_text = text.replace(". ", ".\n")

    return date_info, main_text

# 띠 운세 반환 함수
def aniin(a_name):
    soup = bs(ur.urlopen("https://search.naver.com/search.naver?where=nexearch&sm=tab_etc&qvt=0&query=%EB%9D%A0%EB%B3%84%20%EC%9A%B4%EC%84%B8").read(), 'html.parser')

    animal_url = soup.find_all('ul', {"class": "sign_lst"})[0].find_all('li')[animal.index(a_name)].find_all('a')[0].get('href')
    soup = bs(ur.urlopen("https://search.naver.com/search.naver?where" + animal_url).read(), 'html.parser')

    text = soup.find_all('p', {"class": "text _cs_fortune_text"})[0].text
    match = re.match(r"(\d{1,2}월 \d{1,2}일 ~ \d{1,2}월 \d{1,2}일)(.*)", text)
    if match:
        date_info = match.group(1)
        main_text = match.group(2).strip().replace(". ", ".\n")
    else:
        date_info = ""
        main_text = text.replace(". ", ".\n")

    return date_info, main_text

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    date_info = None
    zodiac_sign = None
    animal_sign = None
    error = None
    birthdate = ""
    zodiac_emoji = ""
    animal_emoji = ""
    if request.method == 'POST':
        birthdate = request.form.get('birthdate')
        if len(birthdate) != 8 or not birthdate.isdigit():
            error = "생일은 8자리 숫자 형식(예: 19900101)으로 입력해야 합니다."
        else:
            try:
                year = int(birthdate[:4])
                month = int(birthdate[4:6])
                day = int(birthdate[6:])
                datetime(year=year, month=month, day=day)  # 예외 처리: 존재하지 않는 월일 검사

                # 버튼에 따라 별자리 운세 또는 띠 운세 가져오기
                if request.form.get('type') == 'zodiac':
                    zodiac_sign = get_zodiac_sign(month, day)
                    zodiac_emoji = emoji[star.index(zodiac_sign)]
                    date_info, result = starin(zodiac_sign)
                elif request.form.get('type') == 'animal':
                    animal_sign = get_animal_sign(year, month, day)
                    animal_emoji = emoji[12 + animal.index(animal_sign)]
                    date_info, result = aniin(animal_sign)
            except ValueError:
                error = "존재하지 않는 월일입니다. 올바른 날짜를 입력하세요."
    return render_template('index.html', birthdate=birthdate, zodiac_sign=zodiac_sign, zodiac_emoji=zodiac_emoji, animal_sign=animal_sign,animal_emoji=animal_emoji, date_info=date_info, result=result, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

