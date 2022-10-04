import requests


def send_telegram(text: str):
    token = '5640422707:AAHJx2qPDIiaLoo8y3QrFue8S9dz08N7eJY'
    url = "https://api.telegram.org/bot"
    channel_id = '878902067'
    url += token
    method = url + "/sendMessage"

    r = requests.post(method, data={
        "chat_id": channel_id,
        "text": text,
        "parse_mode": "HTML"
    })

    if r.status_code != 200:
        raise Exception("post_text error")


def main():
    send_telegram('Привет, чувак!')


if __name__ == '__main__':
    main()