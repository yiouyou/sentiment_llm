import requests
import json
import sys


HOST = '127.0.0.1:8000'


def api_comments(txt):
    _url = f'http://{HOST}/api/v1/comments/?txt={txt}'
    # print(_url)
    response = requests.request("POST", url=_url, headers={}, data={})
    print(response)
    # print(response.text)

    res = ''
    if response.status_code == 200:
        result = response.json()
        # print(result)
        res = json.dumps(result, indent=4)
        # print(res)
    return res


if __name__ == '__main__':

    txt = sys.argv[1]
    # print(f"txt: {txt}")

    res = api_comments(txt)
    print(f"\n\n[res]: {res}\n\n")
