import datetime
import pytz
import telebot
from telebot.types import InputMediaPhoto
from bs4 import BeautifulSoup
import requests as re
from os import environ
from dotenv import load_dotenv
import json

load_dotenv()
API_TOKEN = environ['API_TOKEN']

bot = telebot.TeleBot(API_TOKEN)


# FUNÇÕES DE APOIO
def return_soup() -> BeautifulSoup:
    """
    Função para retornar um objeto BeautifulSoup gerado a partir do site da canção nova
    :return: BeautifulSoup da Canção Nova
    """
    url = "https://santo.cancaonova.com/"
    html_content = re.get(url).content
    return BeautifulSoup(html_content, 'html.parser')


def get_prayer_source(soup: BeautifulSoup) -> str:
    """
    Retorna oração do santo e fonte
    :param soup: soup gerada
    :return: oração do santo e fonte
    """
    pos = 0
    paragraph_list = soup.find('div', attrs={'class': 'content-santo'}).findChildren('p')
    for i in range(len(paragraph_list)):
        if paragraph_list[i].text.strip().lower() == 'a minha oração':
            pos = i + 1
    prayer = paragraph_list[pos].text.strip()
    return "Oração:\n<i>" + prayer + "</i>\n\nFonte: Canção Nova"


def get_saint_name(soup: BeautifulSoup) -> str:
    """
    Retorna o nome do santo
    :param soup: soup da página
    :return: nome do santo com html
    """
    return "<b>" + soup.find('h1', attrs={'class': 'entry-title'}).text.strip() + "</b>\n\n"


def get_rosary(day: int) -> dict:
    """
    Função para retornar os mistérios do dia e informações úteis
    :param day: dia da semana (0 é segunda-feira)
    :return: dicionário do mistério
    """
    with open("rosario.json", encoding='UTF-8') as ros:
        rosary = json.load(ros)
    return rosary[str(day)]


# FUNÇÕES DE INTERAÇÃO

# Define a command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_photo(message.chat.id,
                   "https://th.bing.com/th/id/OIG4..hzEazUio1m9jxK_R.pz?pid=ImgGn",
                   "*Seja muito bem-vindo ao bot católico!*\n\n"
                   "Aqui você pode encontrar folheto da missa dominical, encontrar a oração do santo dia e"
                   "buscar versículos da Bíblia\n\n"
                   "Descubra nossos comandos com /info. Em desenvolvimento", parse_mode='Markdown')


@bot.message_handler(commands=['info'])
def send_info(message):
    bot.reply_to(message,
                 "<b>Lista de comandos:</b>\n"
                 "/santo_do_dia: retorna imagem e oração do santo do dia\n"
                 "/folheto: folheto da missa dominical\n"
                 "/terco: mistérios do terço deste dia\n"
                 "/biblia: escreva \"/biblia sigla:versiculo\" para um versículo "
                 "ou \"biblia sigla:versiculo1-versiculo2\".\n"
                 "Por exemplo: \"Mt 16:18\" ou \"Jo 15:1-9\"\n"
                 "Caso não conheça as siglas de cor, digite /siglas", parse_mode="HTML")


# funcao para santo do dia
@bot.message_handler(commands=['santo_do_dia'])
def send_saint(message):
    try:
        soup = return_soup()
        string = get_saint_name(soup) + get_prayer_source(soup)
        src = soup.find_all('img')[1]['src']
        bot.send_photo(message.chat.id,
                       photo=src,
                       caption=string, parse_mode='html')
    except Exception as e:
        print(e)
        bot.reply_to(message, "Infelizmente, não foi possível executar este comando.")


# função para o rosário
@bot.message_handler(commands=['terco', 'rosario', 'terço', 'rosário'])
def send_rosary(message):
    timezone = pytz.timezone('America/Sao_Paulo')
    day = datetime.datetime.now(timezone).weekday()
    rosary = get_rosary(day)
    imgs = rosary['imgs']
    imgs_to_be_sent = []
    caption = "*" + rosary['title'] + "*" + "\n\n" + rosary['text'] + "\n\n" + (f"Caso queira ser acompanhado(a) "
                                                                                f"em suas orações, "
                                                                                f"[recomendamos "
                                                                                f"este video.]({rosary['video']})")
    for i in range(len(imgs)):
        if i != 0:
            imgs_to_be_sent.append(InputMediaPhoto(imgs[i], parse_mode="Markdown"))
        else:
            imgs_to_be_sent.append(InputMediaPhoto(imgs[i], caption=caption, parse_mode="Markdown"))
    bot.send_media_group(message.chat.id, imgs_to_be_sent)


@bot.message_handler(commands=['folheto'])
def send_folheto(message):
    url = ""
    tz = pytz.timezone('America/Sao_Paulo')
    diff = 6 - datetime.datetime.now(tz).weekday()  # dias até domingo
    next_sunday = datetime.datetime.now(tz).date() + datetime.timedelta(diff)  # próximo domingo
    next_sunday = next_sunday.strftime("%d/%m/%Y")
    try:
        fol = re.get("https://arqrio.org.br/folhetos")
        soup = BeautifulSoup(fol.content, 'html.parser')
        cards = soup.find_all('div', attrs={'class': 'card'})
        for card in cards:
            if card.find('h3').text == next_sunday:
                url = card.find_all('a')[1]['href']
                break
    except Exception as e:
        bot.reply_to(message, "Algo deu errado. Entre em contato com o desenvolvedor")
    bot.send_document(message.chat.id,
                      document=url,
                      caption="**Folheto para a santa missa dominical.**\n\n"
                              "__Obs: Canções podem variar entre paróquias__",
                      parse_mode='markdown',
                      visible_file_name="a_missa.pdf")


@bot.message_handler(commands=['biblia', 'bíblia'])
def send_bible_verses(message):
    mess = message.text.lower()
    if 'bíblia' in mess:
        mess.replace("bíblia", "biblia")
    try:
        if '/' in ''.join(mess.split(' ')[1:]) or mess[mess.find(' ') + 1:].strip().count(' ') > 1:
            raise ValueError
        elif '-' in mess:
            mess = '/'.join(mess.split(' ')[1:]).replace(':', '/')
        else:
            mess = '/'.join(mess.split(' ')[1:]).replace(':', '/')
        resp = re.get("https://biblia-api-flask.onrender.com/" + mess)
        if resp.status_code == 404:
            raise ValueError
        bot.reply_to(message, resp.json()['data'])
    except ValueError:
        bot.reply_to(message, "Por favor, digite no padrão `sigla_livro capitulo:versiculo1-versiculo2` ou "
                              "`sigla_livro capitulo:versiculo`\n\n Caso tenha dificuldade, digite /siglas",
                     parse_mode="Markdown")


@bot.message_handler(commands=['siglas'])
def send_bible_short(message):
    string = ""
    for key in bible_short.keys():
        string += str(key) + ": " + bible_short[key] + "\n"
    bot.reply_to(message, string)


# será removido
bible_short = {
    "Gênesis": "Gn",
    "Êxodo": "Ex",
    "Levítico": "Lv",
    "Números": "Nm",
    "Deuteronômio": "Dt",
    "Josué": "Js",
    "Juízes": "Jz",
    "Rute": "Rt",
    "1 Samuel": "1Sm",
    "2 Samuel": "2Sm",
    "1 Reis": "1Rs",
    "2 Reis": "2Rs",
    "1 Crônicas": "1Cr",
    "2 Crônicas": "2Cr",
    "Esdras": "Ed",
    "Neemias": "Ne",
    "Tobias": "Tb",
    "Judite": "Jt",
    "Ester": "Et",
    "1 Macabeus": "1Mc",
    "2 Macabeus": "2Mc",
    "Jó": "Jó",
    "Salmos": "Sl",
    "Provérbios": "Pr",
    "Eclesiastes": "Ec",
    "Cântico dos Cânticos": "Ct",
    "Sabedoria": "Sb",
    "Eclesiástico": "Eclo",
    "Isaías": "Is",
    "Jeremias": "Jr",
    "Lamentações": "Lm",
    "Baruc": "Br",
    "Ezequiel": "Ez",
    "Daniel": "Dn",
    "Oséias": "Os",
    "Joel": "Jl",
    "Amós": "Am",
    "Abdias": "Abd",
    "Jonas": "Jn",
    "Miquéias": "Mq",
    "Naum": "Na",
    "Habacuque": "Hc",
    "Sofonias": "Sf",
    "Ageu": "Ag",
    "Zacarias": "Zc",
    "Malaquias": "Ml",
    "Mateus": "Mt",
    "Marcos": "Mc",
    "Lucas": "Lc",
    "João": "Jo",
    "Atos dos Apóstolos": "At",
    "Romanos": "Rm",
    "1 Coríntios": "1Cor",
    "2 Coríntios": "2Cor",
    "Gálatas": "Gl",
    "Efésios": "Ef",
    "Filipenses": "Fl",
    "Colossenses": "Cl",
    "1 Tessalonicenses": "1Ts",
    "2 Tessalonicenses": "2Ts",
    "1 Timóteo": "1Tm",
    "2 Timóteo": "2Tm",
    "Tito": "Tt",
    "Filemon": "Flm",
    "Hebreus": "Hb",
    "Tiago": "Tg",
    "1 Pedro": "1Pd",
    "2 Pedro": "2Pd",
    "1 João": "1Jo",
    "2 João": "2Jo",
    "3 João": "3Jo",
    "Judas": "Jd",
    "Apocalipse": "Ap"
}
bot.polling()
