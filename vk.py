from urllib.parse import urlencode, urlparse
import requests
import time

AUTH_URL = 'https://oauth.vk.com/authorize'
VERSION = '5.60'
APP_ID = 5796249
N = 10   #количество выводимых друзей с наибольшим совпадением


# возвращает словарь друзей пользователя по параметрам или 0, если пользователь удален
def get_friends(params):
    response = requests.get('https://api.vk.com/method/friends.get', params)
    if response.json().get('error') != None:
        return 0
    friends = {}
    for item in response.json()['response']['items']:
        friends[item['id']] = [item['first_name'], item['last_name']]
    return friends


# возвращает количество совпадений
def compare_dicts(dict1, dict2):
    set1 = set(dict1)
    set2 = set(dict2)
    return len(set1.intersection(set2))


# устанавливает одному другу количество совпадений
def add_matches(friends, friend, friends_of_friend):
    if friends_of_friend == 0:
        friends[friend].append(0)
    else:
        matches = compare_dicts(friends, friends_of_friend)
        friends[friend].append(matches)


# устанавливает каждому другу из словаря количество совпадений
def get_matches(friends, params):
    for i, friend in enumerate(friends):
        params['user_id'] = friend
        if (i + 1) % 3 == 0: # для удовлетворения ограничениям API по количеству запросов в секунду
            time.sleep(1)
        friends_of_friend = get_friends(params)
        add_matches(friends, friend, friends_of_friend)
        print('processing {}/{}'.format(i +1, len(friends)))


# выводит n друзей с наимбольшими совпадениями
def print_top_n(friends, n):
    l = lambda x: x[1][2]
    for i, friend in enumerate(sorted(friends.items(), key=l, reverse=True)):
        if i + 1 > n:
            break
        print(i + 1, friend)


auth_data = {
    'client_id': APP_ID,
    'display': 'mobile',
    'response_type': 'token',
    'scope': 'friends,status',
    'v': VERSION
}
print('?'.join((AUTH_URL, urlencode(auth_data))))

token_url = 'https://oauth.vk.com/blank.html#access_token=62fe326b029a7b00051906d439c454d28c1f46ec2617d376352bfe1936ac81146d806e791917b35690142&expires_in=86400&user_id=289384'


o = urlparse(token_url)
fragments = dict((i.split('=') for i in o.fragment.split('&')))
access_token = fragments['access_token']

params = dict(access_token=access_token, v=VERSION, fields='name')

friends = get_friends(params)
get_matches(friends, params)
print_top_n(friends, N)

