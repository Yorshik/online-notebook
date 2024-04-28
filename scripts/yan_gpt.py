from yandexgptlite import YandexGPTLite


def gpt_answer(text):
    account = YandexGPTLite('b1gqdn454mip7ombgb54', 'y0_AgAAAAAy_SMVAATuwQAAAAEB6K5tAAAPCIKUDadLH5774KDpceA82ll8Tw')
    answer = account.create_completion(
        text, '0.5',
        system_prompt='''ты находишься на сайте Онлайн блокнот. Помогай людям придумывать идеи для заметок.'''
    )
    return answer
