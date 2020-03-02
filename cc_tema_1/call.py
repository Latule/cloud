import requests
import threading
import time


def call(country: str):
    response = requests.get('http://localhost:5000/use/' + country)
    response.content


if __name__ == '__main__':

    for i in range(50):
        thread = threading.Thread(target=call, args=('roma',))
        thread.start()

        thread = threading.Thread(target=call, args=('spai',))
        thread.start()

        thread = threading.Thread(target=call, args=('ital',))
        thread.start()

        thread = threading.Thread(target=call, args=('ana',))
        thread.start()
