from pprint import pprint
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()


class VK:
    def __init__(self, version='5.131'):
       self.token = os.getenv('VK_TOKEN')
       self.version = version
       self.params = {'access_token': self.token, 'v': self.version}

    def get_user_info(self, user_ids, fields='bdate,city,sex,photo_id'):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': user_ids, 'fields': fields, **self.params}
        response = requests.get(url, params=params)
        try:
            data = response.json()["response"][0]
            data['user_url'] = f'https://vk.com/id{user_ids}'
            data['photo_id'] = f'photo{data["photo_id"]}'
            return data
        except KeyError:
            return {}

    def search_candidates(self, sex, age_from, age_to, city, status=(1, 6), has_photo=1):
        url = 'https://api.vk.com/method/users.search'
        params = {"sex": sex,
                  "age_from": age_from,
                  "age_to": age_to,
                  'city': city,
                  "status": status,
                  "has_photo": has_photo,
                  'count': 1000,
                  'fields': 'bdate,city,photo_id',
                  **self.params}
        candidates_list = []
        # while True:
        #     time.sleep(0.34)
        response = requests.get(url, params=params).json()

        for candidate in response['response']['items']:
            candidate_id = candidate.get('id')
            if not candidate['is_closed'] and candidate_id:
                # здесь добавить проверку на то, есть ли в БД candidate_id найденного кандидата (был ли он ранее показан пользователю бота)
                candidates_list.append(
                    {'id': candidate_id,
                     'first_name': candidate.get('first_name', ''),
                     'last_name': candidate.get('last_name', ''),
                     'sex': candidate.get('sex', 0),
                     'city': candidate.get('city', ''),
                     # 'city_id': candidate.get('city', {}).get('id', ''),
                     # 'city_title': candidate.get('city', {}).get('title', ''),
                     'bdate': candidate.get('bdate', ''),
                     'photo_id': candidate.get('photo_id', ''),
                     # 'top_photo': self.get_photos(candidate_id),
                     'user_url': f"https://vk.com/id{candidate_id}"}
                )
            # if len(candidates_list) >= 1200:
            #     break

        return candidates_list

    def get_photos(self, owner_id):
        url = 'https://api.vk.com/method/photos.getAll'
        params = {'owner_id': owner_id, "extended": 1, 'album_id': 'profile', **self.params}
        res = requests.get(url, params=params).json()

        photos = []
        likes = []

        for photo in res['response']['items']:
            like = photo['likes']['count']
            photo_id = photo['id']
            likes.append(like)
            photos.append(photo_id)

        top_3 = sorted(zip(likes, photos), reverse=True)[:3]
        result = [f"photo{owner_id}_{photo[1]}" for photo in top_3]
        return result

    def city_convert_id(self, user_id, q, need_all=0):
        try:
            url = 'https://api.vk.com/method/database.getCities'
            params = {'q': q, "need_all": need_all, **self.params}
            res = requests.get(url, params=params).json()
            return res['response']['items'][0]['id']
        except Exception as error:
            city = self.get_user_info(user_id).get('city', {}).get('id', '')
            return city if city else 1


if __name__ == '__main__':
    # access_token = os.getenv('vk_token')
    vk = VK()

    user = vk.get_user_info(55242725)
    print(user)
    # candidates =vk.search_candidates(1,30,45,2)
    #photos = vk.get_photos(371521)
    # city_id = vk.city_convert_id("москва")
    # print(city_id)
    # print(type(city_id))
    # next_candidate = vk.next(candidates)

    #pprint(user)
    # pprint(candidates)
    #pprint(photos)
    #print(city_id)

