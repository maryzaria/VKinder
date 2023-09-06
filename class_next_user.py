from api_vk import VK


class NextUser:
    candidates = {}

    def __init__(self, user_id):
        self.candidates_list = self.candidates_for_user(user_id)
        self.next_candidate = self.next_user(self.candidates_list)

    def __iter__(self):
        return self

    @staticmethod
    def next_user(data):
        yield from data

    def candidates_for_user(self, user_id):
        users = self.candidates.get(user_id)
        # print(users)
        if users is None:
            vk_search = VK()
            # sex, age_from, age_to, city = ... - Критерии поиска достаем из БД
            sex, age_from, age_to, city = 1, 30, 45, 2
            city = vk_search.city_convert_id(user_id=user_id, q=city)
            candidates_for_user = vk_search.search_candidates(sex=sex, age_from=age_from,
                                                              age_to=age_to, city=city)
            # sex=self.sex, age_from=self.age_from, age_to=self.age_to, city=self.city
            self.candidates[user_id] = candidates_for_user
        return self.candidates[user_id]

    def __next__(self):
        return next(self.next_candidate)


if __name__ == '__main__':
    n = NextUser('55242725')
    print(next(n))
    print(next(n))