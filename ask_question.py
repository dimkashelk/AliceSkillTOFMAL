from requests import post

headers_ask = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'ru,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Length': '213',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': '__cfduid=df1de15bf15d97ad848e6cdb012aa716f1618478253; check=1; spr_c=4ca5a1ffe083926d9df7909623cd4b5a8952c6a1966da4ee59afe7f4eef3caa0; HWETZ=E77IPUIO; _ym_uid=16184782551024505991; _ym_d=1618478255; _ym_isad=2; _ga=GA1.2.849612803.1618478255; _gid=GA1.2.238627137.1618478256; __gads=ID=4e6067ee2184484d-2284fa7e1ebb004b:T=1618478254:S=ALNI_MatwfFpQqk0Em-O-etu6RGLFirBxQ; _fbp=fb.1.1618478256178.177351733; __cf_bm=49f5d903e4dae3dc0b99a14d7626a978ed2f5599-1618498492-1800-ATlqvD5xx8VOyQpmDxvinXUwXq4eos6c9CE9I7fgS6gbKw0YomuZC8tI5cQclSz2Ahx1bGQcnhbJVcHVq+E555i2u9uaYmGTCecFn7GN+jtprmYj6V5nybRav/qMNLUwjQ==; _ym_visorc=w',
    'DNT': '1',
    'Host': 'sprashivai.ru',
    'Origin': 'http://sprashivai.ru',
    'Referer': 'http://sprashivai.ru/dimkashelk',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 YaBrowser/21.3.1.91 Yowser/2.5 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

data = {
    'username': 'lubichgr',
    'anonymously': 'yes',
    'question': '',
    'hash': 'd2cfe992bcc36307412216f97c2028de8fb8eb0b91869b787a3d818da17e0ef0',
    'sig': '5bdd31e17e9133d98beefa1ace51da3359b9c0e26e815adc8c85f5515df6480e'
}


def ask_question(text):
    text += '\n\n\nОтправлено из лицейского навыка Алисы'
    data['question'] = text
    dop = post('http://sprashivai.ru/question/ask', headers=headers_ask, data=data).json()
    return True if dop['status'] == 'ok' else False
