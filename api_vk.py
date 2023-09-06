from pprint import pprint
import requests
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

class VK:

    def __init__(self, access_token, version='5.131'):
       self.token = access_token
       self.version = version
       self.params = {'access_token': self.token, 'v': self.version}

    def get_user_info(self, user_ids, fields='bdate,city,sex,photo_id'):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': user_ids, 'fields': fields, **self.params}
        response = requests.get(url, params=params)
        data = response.json()
        data["response"][0]['user_url'] = f'https://vk.com/id{user_ids}'
        data["response"][0]['photo_id'] = f'photo-{data["response"][0]["photo_id"]}'
        data["response"][0]['top_photo'] = vk.get_photos(data["response"][0]['id'])
        return data

    def search_candidates(self, sex, age_from, age_to, city, status, has_photo=1):
        url = 'https://api.vk.com/method/users.search'
        params = {"sex": sex,
                  "age_from": age_from,
                  "age_to": age_to,
                  'city': city,
                  "status":status,
                  "has_photo": has_photo,
                  'count':1000,
                  **self.params}
        candidates_list=[]
        while True:
            time.sleep(0.34)
            response = requests.get(url, params=params).json()

            for candidate in response['response']['items']:
                if candidate['is_closed'] == False:
                    candidates_list.append(candidate)

            if len(candidates_list) >= 1200:
                break

        return candidates_list

    def next(self, search_result_list):
        # search_result_list_cursor = -1

        # while search_result_list_cursor < len(search_result_list):
        #     search_result_list_cursor += 1
        #     if search_result_list_cursor >= len(search_result_list):
        #         break
        yield from search_result_list


    def get_photos(self, owner_id):
        url = 'https://api.vk.com/method/photos.getAll'
        params = {'owner_id': owner_id, "extended":1, 'album_id': 'profile', **self.params}
        res = requests.get(url, params=params).json()

        photos = []
        likes = []
        result=[]

        for photo in res['response']['items']:
            like = photo['likes']['count']
            photo_id = photo['id']
            likes.append(like)
            photos.append(photo_id)
        top_3 = sorted(zip(likes,photos), reverse=True)[:3]
        k=0
        for k in range(3):
            result.append(f"photo-{owner_id}_{top_3[k][1]}")
            k+=1
        return result

    def city_convert_id(self,q, need_all=0):
        url = 'https://api.vk.com/method/database.getCities'
        params = {'q':q, "need_all":need_all, **self.params}
        res = requests.get(url, params=params).json()
        return res

if __name__ == '__main__':
    access_token = os.getenv('vk_token')
    vk = VK(access_token, version='5.131')

    #user = vk.get_user_info(371521)
    candidates =vk.search_candidates(1,30,45,2,(1,6))
    #photos = vk.get_photos(371521)
    #city_id = vk.city_convert_id("Екатеринбург")
    next_candidate = vk.next(candidates)

    #pprint(user)
    # pprint(candidates)
    #pprint(photos)
    #print(city_id)

