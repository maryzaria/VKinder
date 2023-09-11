from api_vk import VK
from methods import data_base


class NextUser:
    candidates = {}

    def __init__(self, user_id, cursess, db):
        self.user_id = user_id
        self.candidates_list = self.candidates_for_user(user_id, cursess, db)
        self.next_candidate = self.next_user(self.candidates_list)

    def __iter__(self):
        return self

    @staticmethod
    def next_user(data):
        yield from data

    def candidates_for_user(self, user_id, cursess, db):
        users = self.candidates.get(user_id)
        if users is None:
            vk_search = VK()
            result = db.get_pref(vk_id=user_id, cursess=cursess)
            vk_id, sex, age_from, age_to, city = result.values()
            city = vk_search.city_convert_id(user_id=user_id, q=city)
            candidates_for_user = vk_search.search_candidates(sex=sex, age_from=age_from, age_to=age_to, city=city,
                                                              user_ids=user_id, db=db, cursess=cursess)
            self.candidates[user_id] = candidates_for_user
        return self.candidates[user_id]

    def __next__(self):
        try:
            return next(self.next_candidate)
        except StopIteration:
            self.candidates_list = self.candidates_for_user(self.user_id)
            self.next_candidate = self.next_user(self.candidates_list)
            return next(self.next_candidate)


if __name__ == '__main__':
    n = NextUser('55242725')
    print(next(n))
    print(next(n))