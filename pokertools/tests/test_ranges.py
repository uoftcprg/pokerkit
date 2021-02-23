from unittest import TestCase, main

from pokertools import parse_range


class CardTestCase(TestCase):
    def test_2_range(self) -> None:
        self.assertSetEqual(frozenset(map(lambda cards: frozenset(map(str, cards)), parse_range('QTs'))), {
            frozenset({'Qc', 'Tc'}), frozenset({'Qd', 'Td'}), frozenset({'Qh', 'Th'}), frozenset({'Qs', 'Ts'}),
        })
        self.assertSetEqual(frozenset(map(lambda cards: frozenset(map(str, cards)), parse_range('AKo'))), {
            frozenset({'Ac', 'Kd'}), frozenset({'Ac', 'Kh'}), frozenset({'Ac', 'Ks'}),
            frozenset({'Ad', 'Kc'}), frozenset({'Ad', 'Kh'}), frozenset({'Ad', 'Ks'}),
            frozenset({'Ah', 'Kc'}), frozenset({'Ah', 'Kd'}), frozenset({'Ah', 'Ks'}),
            frozenset({'As', 'Kc'}), frozenset({'As', 'Kd'}), frozenset({'As', 'Kh'}),
        })
        self.assertSetEqual(frozenset(map(lambda cards: frozenset(map(str, cards)), parse_range('AK'))), {
            frozenset({'Ac', 'Kd'}), frozenset({'Ac', 'Kh'}), frozenset({'Ac', 'Ks'}),
            frozenset({'Ad', 'Kc'}), frozenset({'Ad', 'Kh'}), frozenset({'Ad', 'Ks'}),
            frozenset({'Ah', 'Kc'}), frozenset({'Ah', 'Kd'}), frozenset({'Ah', 'Ks'}),
            frozenset({'As', 'Kc'}), frozenset({'As', 'Kd'}), frozenset({'As', 'Kh'}),
            frozenset({'Ac', 'Kc'}), frozenset({'Ad', 'Kd'}), frozenset({'Ah', 'Kh'}), frozenset({'As', 'Ks'}),
        })
        self.assertSetEqual(frozenset(map(lambda cards: frozenset(map(str, cards)), parse_range('JJ'))), {
            frozenset({'Jc', 'Jd'}), frozenset({'Jc', 'Jh'}), frozenset({'Jc', 'Js'}),
            frozenset({'Jd', 'Jh'}), frozenset({'Jd', 'Js'}), frozenset({'Jh', 'Js'}),
        })
        self.assertSetEqual(frozenset(map(lambda cards: frozenset(map(str, cards)), parse_range('AsKh'))), {
            frozenset({'As', 'Kh'})
        })
        self.assertSetEqual(frozenset(map(lambda cards: frozenset(map(str, cards)), parse_range('JJ+'))), {
            frozenset({'Jc', 'Jd'}), frozenset({'Jc', 'Jh'}), frozenset({'Jc', 'Js'}),
            frozenset({'Jd', 'Jh'}), frozenset({'Jd', 'Js'}), frozenset({'Jh', 'Js'}),
            frozenset({'Qc', 'Qd'}), frozenset({'Qc', 'Qh'}), frozenset({'Qc', 'Qs'}),
            frozenset({'Qd', 'Qh'}), frozenset({'Qd', 'Qs'}), frozenset({'Qh', 'Qs'}),
            frozenset({'Kc', 'Kd'}), frozenset({'Kc', 'Kh'}), frozenset({'Kc', 'Ks'}),
            frozenset({'Kd', 'Kh'}), frozenset({'Kd', 'Ks'}), frozenset({'Kh', 'Ks'}),
            frozenset({'Ac', 'Ad'}), frozenset({'Ac', 'Ah'}), frozenset({'Ac', 'As'}),
            frozenset({'Ad', 'Ah'}), frozenset({'Ad', 'As'}), frozenset({'Ah', 'As'}),
        })
        self.assertSetEqual(frozenset(map(lambda cards: frozenset(map(str, cards)), parse_range('JTo+'))), {
            frozenset({'Jc', 'Td'}), frozenset({'Jc', 'Th'}), frozenset({'Jc', 'Ts'}),
            frozenset({'Jd', 'Tc'}), frozenset({'Jd', 'Th'}), frozenset({'Jd', 'Ts'}),
            frozenset({'Jh', 'Tc'}), frozenset({'Jh', 'Td'}), frozenset({'Jh', 'Ts'}),
            frozenset({'Js', 'Tc'}), frozenset({'Js', 'Td'}), frozenset({'Js', 'Th'}),
        })
        self.assertSetEqual(frozenset(map(lambda cards: frozenset(map(str, cards)), parse_range('QT+'))), {
            frozenset({'Qc', 'Td'}), frozenset({'Qc', 'Th'}), frozenset({'Qc', 'Ts'}),
            frozenset({'Qd', 'Tc'}), frozenset({'Qd', 'Th'}), frozenset({'Qd', 'Ts'}),
            frozenset({'Qh', 'Tc'}), frozenset({'Qh', 'Td'}), frozenset({'Qh', 'Ts'}),
            frozenset({'Qs', 'Tc'}), frozenset({'Qs', 'Td'}), frozenset({'Qs', 'Th'}),
            frozenset({'Qc', 'Tc'}), frozenset({'Qd', 'Td'}), frozenset({'Qh', 'Th'}), frozenset({'Qs', 'Ts'}),
            frozenset({'Qc', 'Jd'}), frozenset({'Qc', 'Jh'}), frozenset({'Qc', 'Js'}),
            frozenset({'Qd', 'Jc'}), frozenset({'Qd', 'Jh'}), frozenset({'Qd', 'Js'}),
            frozenset({'Qh', 'Jc'}), frozenset({'Qh', 'Jd'}), frozenset({'Qh', 'Js'}),
            frozenset({'Qs', 'Jc'}), frozenset({'Qs', 'Jd'}), frozenset({'Qs', 'Jh'}),
            frozenset({'Qc', 'Jc'}), frozenset({'Qd', 'Jd'}), frozenset({'Qh', 'Jh'}), frozenset({'Qs', 'Js'}),
        })
        self.assertSetEqual(frozenset(map(lambda cards: frozenset(map(str, cards)), parse_range('9T+'))), set())


if __name__ == '__main__':
    main()
