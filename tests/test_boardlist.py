import unittest

from robot.board import Board, BoardList


class FakeBoard(Board):
    def _connect(selfself):
        pass

    def __repr__(self):
        return "FakeBoard({!r})".format(str(self.socket_path))


class BoardListTests(unittest.TestCase):
    longMessage = True

    def test_length_zero(self):
        board_list = BoardList()
        self.assertEqual(0, len(board_list))

    def test_length_one(self):
        board_list = BoardList({'a': FakeBoard('a')})
        self.assertEqual(1, len(board_list))

    def test_length_many(self):
        board_list = BoardList({x: FakeBoard(x) for x in "abcd"})
        self.assertEqual(4, len(board_list))

    def test_iterate_zero(self):
        # Mappings iterate over their keys
        board_list = BoardList()
        members = [x for x in board_list]
        self.assertEqual([], members)

    def test_iterate_one(self):
        # Mappings iterate over their keys
        board_list = BoardList({'a': FakeBoard('a')})
        members = [x for x in board_list]
        self.assertEqual(['x'], members)

    def test_iterate_many(self):
        # Mappings iterate over their keys
        board_list = BoardList({x: FakeBoard(x) for x in "abcd"})
        members = [x for x in board_list]
        self.assertEqual(list("abcd"), members)

    def test_contains_zero(self):
        # Mappings contain their keys
        board_list = BoardList()

        self.assertNotIn(0, board_list)
        self.assertNotIn(1, board_list)
        self.assertNotIn('a', board_list)
        self.assertNotIn('x', board_list)

    def test_contains_one(self):
        # Mappings contain their keys
        board_list = BoardList({'a': FakeBoard('a')})

        self.assertIn(0, board_list)
        self.assertIn('a', board_list)

        self.assertNotIn(1, board_list)
        self.assertNotIn('x', board_list)

    def test_contains_many(self):
        # Mappings contain their keys
        board_list = BoardList({x: FakeBoard(x) for x in "abcd"})

        self.assertIn(0, board_list)
        self.assertIn(1, board_list)
        self.assertIn(2, board_list)
        self.assertIn(3, board_list)

        self.assertNotIn(4, board_list)

        self.assertIn('a', board_list)
        self.assertIn('b', board_list)
        self.assertIn('c', board_list)
        self.assertIn('d', board_list)

        self.assertNotIn('x', board_list)

    def test_index_zero(self):
        # Mappings contain their keys
        board_list = BoardList()

        with self.assertRaises(IndexError):
            board_list[0]

        with self.assertRaises(KeyError):
            board_list['a']

    def test_index_one(self):
        # Mappings contain their keys
        fake_board = FakeBoard('a')
        board_list = BoardList({'a': fake_board})

        self.assertEqual(fake_board, board_list[0])
        self.assertEqual(fake_board, board_list['a'])

        with self.assertRaises(IndexError):
            board_list[1]

        with self.assertRaises(KeyError):
            board_list['x']

    def test_index_many(self):
        # Mappings contain their keys
        fake_board_a = FakeBoard('a')
        fake_board_b = FakeBoard('b')
        fake_board_c = FakeBoard('c')
        fake_board_d = FakeBoard('d')
        board_list = BoardList({
            'a': fake_board_a,
            'b': fake_board_b,
            'c': fake_board_c,
            'd': fake_board_d,
        })

        self.assertEqual(fake_board_a, board_list[0])
        self.assertEqual(fake_board_a, board_list['a'])

        self.assertEqual(fake_board_b, board_list[1])
        self.assertEqual(fake_board_b, board_list['b'])

        self.assertEqual(fake_board_c, board_list[2])
        self.assertEqual(fake_board_c, board_list['c'])

        self.assertEqual(fake_board_d, board_list[3])
        self.assertEqual(fake_board_d, board_list['d'])

        with self.assertRaises(IndexError):
            board_list[4]

        with self.assertRaises(KeyError):
            board_list['x']
