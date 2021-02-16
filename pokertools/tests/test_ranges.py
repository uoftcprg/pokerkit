from unittest import TestCase, main, skip

from pokertools import parse_range


@skip('Not yet implemented')
class CardTestCase(TestCase):
    def test_2_range(self) -> None:
        self.assertSetEqual(set(map(lambda cards: set(map(str, cards)), parse_range('AKo', 'JJ', 'QTs'))),
                            {{'Ac', 'Kd'}, {'Ac', 'Kh'}, {'Ac', 'Ks'},
                             {'Ad', 'Kc'}, {'Ad', 'Kh'}, {'Ad', 'Ks'},
                             {'Ah', 'Kc'}, {'Ah', 'Kd'}, {'Ah', 'Ks'},
                             {'As', 'Kc'}, {'As', 'Kd'}, {'As', 'Kh'},
                             {'Jc', 'Jd'}, {'Jc', 'Jh'}, {'Jc', 'Js'}, {'Jd', 'Jh'}, {'Jd', 'Js'}, {'Jh', 'Js'},
                             {'Qc', 'Tc'}, {'Qd', 'Td'}, {'Qh', 'Th'}, {'Qs', 'Ts'}})
        self.assertSetEqual(set(map(lambda cards: set(map(str, cards)), parse_range('AK', 'JJ'))),
                            {{'Ac', 'Kd'}, {'Ac', 'Kh'}, {'Ac', 'Ks'},
                             {'Ad', 'Kc'}, {'Ad', 'Kh'}, {'Ad', 'Ks'},
                             {'Ah', 'Kc'}, {'Ah', 'Kd'}, {'Ah', 'Ks'},
                             {'As', 'Kc'}, {'As', 'Kd'}, {'As', 'Kh'},
                             {'Ac', 'Kc'}, {'Ad', 'Kd'}, {'Ah', 'Kh'}, {'As', 'Ks'},
                             {'Jc', 'Jd'}, {'Jc', 'Jh'}, {'Jc', 'Js'}, {'Jd', 'Jh'}, {'Jd', 'Js'}, {'Jh', 'Js'}})
        self.assertSetEqual(set(map(lambda cards: set(map(str, cards)), parse_range('JJ+'))),
                            {{'Jc', 'Jd'}, {'Jc', 'Jh'}, {'Jc', 'Js'}, {'Jd', 'Jh'}, {'Jd', 'Js'}, {'Jh', 'Js'},
                             {'Qc', 'Qd'}, {'Qc', 'Qh'}, {'Qc', 'Qs'}, {'Qd', 'Qh'}, {'Qd', 'Qs'}, {'Qh', 'Qs'},
                             {'Kc', 'Kd'}, {'Kc', 'Kh'}, {'Kc', 'Ks'}, {'Kd', 'Kh'}, {'Kd', 'Ks'}, {'Kh', 'Ks'},
                             {'Ac', 'Ad'}, {'Ac', 'Ah'}, {'Ac', 'As'}, {'Ad', 'Ah'}, {'Ad', 'As'}, {'Ah', 'As'}})
        self.assertSetEqual(set(map(lambda cards: set(map(str, cards)), parse_range('JJ+', 'AA'))),
                            {{'Jc', 'Jd'}, {'Jc', 'Jh'}, {'Jc', 'Js'}, {'Jd', 'Jh'}, {'Jd', 'Js'}, {'Jh', 'Js'},
                             {'Qc', 'Qd'}, {'Qc', 'Qh'}, {'Qc', 'Qs'}, {'Qd', 'Qh'}, {'Qd', 'Qs'}, {'Qh', 'Qs'},
                             {'Kc', 'Kd'}, {'Kc', 'Kh'}, {'Kc', 'Ks'}, {'Kd', 'Kh'}, {'Kd', 'Ks'}, {'Kh', 'Ks'},
                             {'Ac', 'Ad'}, {'Ac', 'Ah'}, {'Ac', 'As'}, {'Ad', 'Ah'}, {'Ad', 'As'}, {'Ah', 'As'}})
        self.assertSetEqual(set(map(lambda cards: set(map(str, cards)), parse_range('JJ+', 'KK+'))),
                            {{'Jc', 'Jd'}, {'Jc', 'Jh'}, {'Jc', 'Js'}, {'Jd', 'Jh'}, {'Jd', 'Js'}, {'Jh', 'Js'},
                             {'Qc', 'Qd'}, {'Qc', 'Qh'}, {'Qc', 'Qs'}, {'Qd', 'Qh'}, {'Qd', 'Qs'}, {'Qh', 'Qs'},
                             {'Kc', 'Kd'}, {'Kc', 'Kh'}, {'Kc', 'Ks'}, {'Kd', 'Kh'}, {'Kd', 'Ks'}, {'Kh', 'Ks'},
                             {'Ac', 'Ad'}, {'Ac', 'Ah'}, {'Ac', 'As'}, {'Ad', 'Ah'}, {'Ad', 'As'}, {'Ah', 'As'}})
        self.assertSetEqual(set(map(lambda cards: set(map(str, cards)), parse_range('JJ-KK', 'JJ-QQ'))),
                            {{'Jc', 'Jd'}, {'Jc', 'Jh'}, {'Jc', 'Js'}, {'Jd', 'Jh'}, {'Jd', 'Js'}, {'Jh', 'Js'},
                             {'Qc', 'Qd'}, {'Qc', 'Qh'}, {'Qc', 'Qs'}, {'Qd', 'Qh'}, {'Qd', 'Qs'}, {'Qh', 'Qs'},
                             {'Kc', 'Kd'}, {'Kc', 'Kh'}, {'Kc', 'Ks'}, {'Kd', 'Kh'}, {'Kd', 'Ks'}, {'Kh', 'Ks'}})


if __name__ == '__main__':
    main()
