from unittest import TestCase, main

from pokerface import Range, parse_card, parse_cards


class RangeTestCase(TestCase):
    def test_parse(self):
        self.assertSetEqual(Range('QJs'), set(map(frozenset, (
            parse_cards('QcJc'), parse_cards('QdJd'), parse_cards('QhJh'),
            parse_cards('QsJs'),
        ))))
        self.assertSetEqual(Range('2s3s'), set(map(frozenset, (
            parse_cards('2s3s'),
        ))))
        self.assertSetEqual(Range('4s5h', '2s3s'), set(map(frozenset, (
            parse_cards('4s5h'), parse_cards('2s3s'),
        ))))
        self.assertSetEqual(
            Range(parse_cards('7s8s'), '27', 'AK', 'ATs+'),
            set(map(frozenset, (
                parse_cards('7s8s'), parse_cards('2c7d'), parse_cards('2c7h'),
                parse_cards('2c7s'), parse_cards('2d7c'), parse_cards('2d7h'),
                parse_cards('2d7s'), parse_cards('2h7c'), parse_cards('2h7d'),
                parse_cards('2h7s'), parse_cards('2s7c'), parse_cards('2s7d'),
                parse_cards('2s7h'), parse_cards('2c7c'), parse_cards('2d7d'),
                parse_cards('2h7h'), parse_cards('2s7s'), parse_cards('AcKd'),
                parse_cards('AcKh'), parse_cards('AcKs'), parse_cards('AdKc'),
                parse_cards('AdKh'), parse_cards('AdKs'), parse_cards('AhKc'),
                parse_cards('AhKd'), parse_cards('AhKs'), parse_cards('AsKc'),
                parse_cards('AsKd'), parse_cards('AsKh'), parse_cards('AcKc'),
                parse_cards('AdKd'), parse_cards('AhKh'), parse_cards('AsKs'),
                parse_cards('AcQc'), parse_cards('AdQd'), parse_cards('AhQh'),
                parse_cards('AsQs'), parse_cards('AcJc'), parse_cards('AdJd'),
                parse_cards('AhJh'), parse_cards('AsJs'), parse_cards('AcTc'),
                parse_cards('AdTd'), parse_cards('AhTh'), parse_cards('AsTs'),
            ))),
        )
        self.assertSetEqual(
            Range('99+', (parse_card('2h'), parse_card('7s'))),
            set(map(frozenset, (
                parse_cards('9c9d'), parse_cards('9c9h'), parse_cards('9c9s'),
                parse_cards('9d9h'), parse_cards('9d9s'), parse_cards('9h9s'),
                parse_cards('TcTd'), parse_cards('TcTh'), parse_cards('TcTs'),
                parse_cards('TdTh'), parse_cards('TdTs'), parse_cards('ThTs'),
                parse_cards('JcJd'), parse_cards('JcJh'), parse_cards('JcJs'),
                parse_cards('JdJh'), parse_cards('JdJs'), parse_cards('JhJs'),
                parse_cards('QcQd'), parse_cards('QcQh'), parse_cards('QcQs'),
                parse_cards('QdQh'), parse_cards('QdQs'), parse_cards('QhQs'),
                parse_cards('KcKd'), parse_cards('KcKh'), parse_cards('KcKs'),
                parse_cards('KdKh'), parse_cards('KdKs'), parse_cards('KhKs'),
                parse_cards('AcAd'), parse_cards('AcAh'), parse_cards('AcAs'),
                parse_cards('AdAh'), parse_cards('AdAs'), parse_cards('AhAs'),
                parse_cards('2h7s'),
            ))),
        )
        self.assertSetEqual(Range('QTs'), set(map(frozenset, (
            parse_cards('QcTc'), parse_cards('QdTd'), parse_cards('QhTh'),
            parse_cards('QsTs'),
        ))))
        self.assertSetEqual(Range('AKo'), set(map(frozenset, (
            parse_cards('AcKd'), parse_cards('AcKh'), parse_cards('AcKs'),
            parse_cards('AdKc'), parse_cards('AdKh'), parse_cards('AdKs'),
            parse_cards('AhKc'), parse_cards('AhKd'), parse_cards('AhKs'),
            parse_cards('AsKc'), parse_cards('AsKd'), parse_cards('AsKh'),
        ))))
        self.assertSetEqual(Range('AK'), set(map(frozenset, (
            parse_cards('AcKd'), parse_cards('AcKh'), parse_cards('AcKs'),
            parse_cards('AdKc'), parse_cards('AdKh'), parse_cards('AdKs'),
            parse_cards('AhKc'), parse_cards('AhKd'), parse_cards('AhKs'),
            parse_cards('AsKc'), parse_cards('AsKd'), parse_cards('AsKh'),
            parse_cards('AcKc'), parse_cards('AdKd'), parse_cards('AhKh'),
            parse_cards('AsKs'),
        ))))
        self.assertSetEqual(Range('JJ'), set(map(frozenset, (
            parse_cards('JcJd'), parse_cards('JcJh'), parse_cards('JcJs'),
            parse_cards('JdJh'), parse_cards('JdJs'), parse_cards('JhJs'),
        ))))
        self.assertSetEqual(Range('AsKh'), {frozenset(parse_cards('AsKh'))})
        self.assertSetEqual(Range('JJ+'), set(map(frozenset, (
            parse_cards('JcJd'), parse_cards('JcJh'), parse_cards('JcJs'),
            parse_cards('JdJh'), parse_cards('JdJs'), parse_cards('JhJs'),
            parse_cards('QcQd'), parse_cards('QcQh'), parse_cards('QcQs'),
            parse_cards('QdQh'), parse_cards('QdQs'), parse_cards('QhQs'),
            parse_cards('KcKd'), parse_cards('KcKh'), parse_cards('KcKs'),
            parse_cards('KdKh'), parse_cards('KdKs'), parse_cards('KhKs'),
            parse_cards('AcAd'), parse_cards('AcAh'), parse_cards('AcAs'),
            parse_cards('AdAh'), parse_cards('AdAs'), parse_cards('AhAs'),
        ))))
        self.assertSetEqual(Range('JTo+'), set(map(frozenset, (
            parse_cards('JcTd'), parse_cards('JcTh'), parse_cards('JcTs'),
            parse_cards('JdTc'), parse_cards('JdTh'), parse_cards('JdTs'),
            parse_cards('JhTc'), parse_cards('JhTd'), parse_cards('JhTs'),
            parse_cards('JsTc'), parse_cards('JsTd'), parse_cards('JsTh'),
        ))))
        self.assertSetEqual(Range('QT+'), set(map(frozenset, (
            parse_cards('QcTd'), parse_cards('QcTh'), parse_cards('QcTs'),
            parse_cards('QdTc'), parse_cards('QdTh'), parse_cards('QdTs'),
            parse_cards('QhTc'), parse_cards('QhTd'), parse_cards('QhTs'),
            parse_cards('QsTc'), parse_cards('QsTd'), parse_cards('QsTh'),
            parse_cards('QcTc'), parse_cards('QdTd'), parse_cards('QhTh'),
            parse_cards('QsTs'), parse_cards('QcJd'), parse_cards('QcJh'),
            parse_cards('QcJs'), parse_cards('QdJc'), parse_cards('QdJh'),
            parse_cards('QdJs'), parse_cards('QhJc'), parse_cards('QhJd'),
            parse_cards('QhJs'), parse_cards('QsJc'), parse_cards('QsJd'),
            parse_cards('QsJh'), parse_cards('QcJc'), parse_cards('QdJd'),
            parse_cards('QhJh'), parse_cards('QsJs'),
        ))))
        self.assertSetEqual(Range('9T+'), set())
        self.assertSetEqual(Range('AsKsQsJsT?'), set(map(frozenset, (
            parse_cards('AsKsQsJsTc'), parse_cards('AsKsQsJsTd'),
            parse_cards('AsKsQsJsTh'), parse_cards('AsKsQsJsTs'),
        ))))
        self.assertSetEqual(Range('9?T?'), Range('9T'))
        self.assertSetEqual(Range('A???'), Range('A2+') | Range('AA'))


if __name__ == '__main__':
    main()
