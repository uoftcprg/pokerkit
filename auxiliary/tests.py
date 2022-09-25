"""This module implements unittests for all classes and functions in
Auxiliary.
"""

from itertools import chain, repeat
from unittest import TestCase, main

from auxiliary import (
    IndexedEnum, MappingView, SequenceView, SetView, SupportsLessThan, chunked,
    clip,
    const, distinct, maxima, minima, next_or_none, prod, reverse_args, rotated,
    windowed,
)


class _Number(IndexedEnum):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3


class _WeirdClass(SupportsLessThan):
    def __lt__(self, other):
        return id(self) < id(other)


class AuxiliaryTestCase(TestCase):
    def test_indexed_enum(self):
        self.assertSequenceEqual(
            tuple(map(IndexedEnum.index.fget, _Number)), range(4),
        )

        self.assertLess(_Number.ZERO, _Number.ONE)
        self.assertLess(_Number.ZERO, _Number.TWO)
        self.assertLess(_Number.ZERO, _Number.THREE)
        self.assertLess(_Number.ONE, _Number.TWO)
        self.assertLess(_Number.ONE, _Number.THREE)
        self.assertLess(_Number.TWO, _Number.THREE)

        self.assertGreater(_Number.THREE, _Number.TWO)
        self.assertGreater(_Number.THREE, _Number.ONE)
        self.assertGreater(_Number.THREE, _Number.ZERO)
        self.assertGreater(_Number.TWO, _Number.ONE)
        self.assertGreater(_Number.TWO, _Number.ZERO)
        self.assertGreater(_Number.ONE, _Number.ZERO)

        self.assertEqual(_Number.ZERO, _Number.ZERO)
        self.assertEqual(_Number.ONE, _Number.ONE)
        self.assertEqual(_Number.TWO, _Number.TWO)
        self.assertEqual(_Number.THREE, _Number.THREE)

    def test_supports_less_than(self):
        self.assertIsInstance(_Number.ZERO, SupportsLessThan)
        self.assertIsInstance(3, SupportsLessThan)
        self.assertIsInstance(3.0, SupportsLessThan)
        self.assertIsInstance('', SupportsLessThan)
        self.assertIsInstance([], SupportsLessThan)
        self.assertIsInstance((), SupportsLessThan)
        self.assertIsInstance(set(), SupportsLessThan)
        self.assertNotIsInstance(object(), SupportsLessThan)
        self.assertNotIsInstance(type, SupportsLessThan)
        self.assertNotIsInstance(..., SupportsLessThan)
        self.assertNotIsInstance(None, SupportsLessThan)

        self.assertTrue(issubclass(_Number, SupportsLessThan))
        self.assertTrue(issubclass(int, SupportsLessThan))
        self.assertTrue(issubclass(float, SupportsLessThan))
        self.assertTrue(issubclass(str, SupportsLessThan))
        self.assertTrue(issubclass(list, SupportsLessThan))
        self.assertTrue(issubclass(tuple, SupportsLessThan))
        self.assertTrue(issubclass(set, SupportsLessThan))
        self.assertFalse(issubclass(object, SupportsLessThan))
        self.assertFalse(issubclass(type, SupportsLessThan))
        self.assertFalse(issubclass(type(...), SupportsLessThan))
        self.assertFalse(issubclass(type(None), SupportsLessThan))

        self.assertFalse(isinstance(3, _WeirdClass))
        self.assertFalse(issubclass(float, _WeirdClass))

    def test_mapping_view(self):
        dict_ = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
        view = MappingView(dict_)
        for value, key in enumerate(('a', 'b', 'c', 'd')):
            self.assertEqual(view[key], value)
        self.assertEqual(len(view), 4)
        dict_['e'] = 4
        for value, key in enumerate(('a', 'b', 'c', 'd', 'e')):
            self.assertEqual(view[key], value)
        self.assertEqual(len(view), 5)

    def test_sequence_view(self):
        list_ = list(range(5))
        view = SequenceView(list_)
        for i in range(5):
            self.assertEqual(view[i], i)
        self.assertEqual(len(view), 5)

        list_.append(5)
        for i in range(6):
            self.assertEqual(view[i], i)
        self.assertEqual(len(view), 6)

        list_ = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        view = SequenceView(list_)
        for i in range(3):
            for j in range(3):
                self.assertEqual(view[i][j], i * 3 + j)

    def test_set_view(self):
        list_ = set(range(5))
        view = SetView(list_)
        for i in range(5):
            self.assertIn(i, view)
        self.assertNotIn(6, view)
        self.assertEqual(len(view), 5)

        list_.add(5)
        for i in range(6):
            self.assertIn(i, view)
        self.assertEqual(len(view), 6)

    def test_distinct(self):
        self.assertFalse(distinct(iter((1, 1, 1))))
        self.assertTrue(distinct(()))
        self.assertFalse(distinct(((1, 1), (1, 1), (1, 2))))
        self.assertFalse(distinct(([2, 1], [1, 1], [2, 1])))
        self.assertTrue(distinct(([2, 1], [1, 1], [1, 2])))
        self.assertTrue(distinct(range(10)))
        self.assertTrue(distinct(iter(range(10))))
        self.assertFalse(distinct((object(), 2, object(), 2, [])))
        self.assertTrue(distinct((object(), 2, object(), 3, [])))

    def test_const(self):
        self.assertTrue(const(iter((1, 1, 1))))
        self.assertTrue(const(()))
        self.assertTrue(const(((1, 1), (1, 1))))
        self.assertFalse(const(range(10)))
        self.assertFalse(const(iter(range(10))))

    def test_chunked(self):
        self.assertSequenceEqual(tuple(chunked(iter(range(7)), 3)), tuple(map(
            tuple, (range(3), range(3, 6), range(6, 7)),
        )))
        self.assertSequenceEqual(tuple(chunked(range(5), 2)), (
            range(2), range(2, 4), range(4, 5),
        ))
        self.assertSequenceEqual(tuple(chunked(range(5), 1)), (
            range(1), range(1, 2), range(2, 3), range(3, 4), range(4, 5),
        ))
        self.assertSequenceEqual(
            tuple(chunked(list(range(5)), 1)), tuple(map(list, (
                range(1), range(1, 2), range(2, 3), range(3, 4), range(4, 5),
            ))),
        )

    def test_windowed(self):
        self.assertSequenceEqual(tuple(windowed(range(6), 3)), (
            range(3), range(1, 4), range(2, 5), range(3, 6),
        ))
        self.assertSequenceEqual(tuple(windowed(range(6), 6)), (range(6),))
        self.assertSequenceEqual(tuple(windowed(range(6), 7)), ())
        self.assertSequenceEqual(tuple(windowed(iter(range(6)), 0)), (
            (), (), (), (), (), (), (),
        ))
        self.assertSequenceEqual(tuple(windowed(range(6), 3, partial_=True)), (
            range(3), range(1, 4), range(2, 5),
            range(3, 6), range(4, 6), range(5, 6),
        ))

    def test_rotated(self):
        self.assertSequenceEqual(rotated(iter(range(6)), -1), tuple(chain(
            (5,), range(5),
        )))
        self.assertSequenceEqual(rotated(range(6), 0), range(6))
        self.assertSequenceEqual(rotated(range(6), 2), tuple(chain(
            range(2, 6), range(2),
        )))

    def test_prod(self):
        self.assertEqual(prod(iter(range(1, 10))), 362880)
        self.assertEqual(prod(range(1, 10), 0), 0)
        self.assertEqual(prod(repeat(1, 5)), 1)
        self.assertEqual(prod(()), 1)
        self.assertEqual(prod((), 5), 5)

    def test_clip(self):
        self.assertEqual(clip(1, 0, 2), 1)
        self.assertEqual(clip(-100, 0, 2), 0)
        self.assertEqual(clip(100, 0, 2), 2)
        self.assertRaises(ValueError, clip, 100, 2, 0)

    def test_next_or_none(self):
        self.assertEqual(next_or_none(iter(range(3))), 0)
        self.assertIsNone(next_or_none(iter(())))

    def test_reverse_args(self):
        self.assertEqual(reverse_args(range)(5, 1), range(1, 5))
        self.assertEqual(reverse_args(dict)(foo='foo', bar='bar'), {
            'foo': 'foo', 'bar': 'bar',
        })
        x, y = [], []
        self.assertIs(max(x, y), x)
        self.assertIs(reverse_args(max)(x, y), y)

    def test_maxima(self):
        self.assertEqual(tuple(maxima(())), ())
        self.assertEqual(tuple(maxima(range(10))), (9,))
        self.assertEqual(tuple(maxima(tuple(range(10)) + tuple(range(10)))), (
            9, 9,
        ))
        self.assertEqual(tuple(maxima(tuple(range(10)) + tuple(range(5)))), (
            9,
        ))
        self.assertEqual(tuple(maxima(tuple(range(10)) + tuple(range(15)))), (
            14,
        ))
        self.assertEqual(tuple(maxima(iter(range(10)))), (9,))
        self.assertEqual(
            tuple(maxima(('1', '2', '3', '4', '3', ' 4', '3', '1 '), key=int)),
            ('4', ' 4'),
        )

    def test_minima(self):
        self.assertEqual(tuple(minima(())), ())
        self.assertEqual(tuple(minima(range(10))), (0,))
        self.assertEqual(tuple(minima(tuple(range(10)) + tuple(range(10)))), (
            0, 0,
        ))
        self.assertEqual(
            tuple(minima(tuple(range(10)) + tuple(range(5, 10)))), (0,),
        )
        self.assertEqual(
            tuple(minima(tuple(range(10)) + tuple(range(-5, 10)))), (-5,),
        )
        self.assertEqual(tuple(minima(iter(range(10)))), (0,))
        self.assertEqual(
            tuple(minima(('1', '2', '3', '4', '3', ' 4', '3', '1 '), key=int)),
            ('1', '1 '),
        )


if __name__ == '__main__':
    main()
