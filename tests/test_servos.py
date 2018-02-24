import json
import socket
import time
import unittest
from unittest import mock

from robot.robot import Robot
from robot.servo import ArduinoError, CommandError, InvalidResponse, ServoBoard
from tests.mock_robotd import MockRobotD, MockRobotDFactoryMixin

from robotd.devices import ServoAssembly


class ServoBoardTest(MockRobotDFactoryMixin, unittest.TestCase):
    def setUp(self):
        mock = self.create_mock_robotd()
        mock.new_powerboard()
        time.sleep(0.2)
        self.mock = mock
        self.robot = Robot(robotd_path=mock.root_dir)

    def test_insert_servoboards(self):
        self.mock.new_servoboard('ABC')
        self.mock.new_servoboard('DEF')
        # Give it a tiny bit to init the boards
        time.sleep(0.4)

        boards = self.robot.servo_boards

        # Check all the motor boards are initialised and can be indexed
        self.assertTrue(0 in boards)
        self.assertTrue(1 in boards)
        self.assertTrue('ABC' in boards)
        self.assertTrue('DEF' in boards)

    def test_remove_servoboard_recovery(self):
        mock_servo = self.mock.new_servoboard('ABC')
        # Give it a tiny bit to init the boards
        time.sleep(0.4)

        boards = self.robot.servo_boards

        # Get the board
        board = boards[0]
        self.mock.remove_board(mock_servo)
        with self.assertRaises(ConnectionError):
            board._servos[0].position = 1

        # Re-add it
        self.mock.new_servoboard('ABC')
        time.sleep(0.2)

        board.servos[0].position = 1

    def test_multiple_indexes(self):
        """ Checks you can index servo boards plenty of times"""
        self.mock.new_servoboard('ABC')
        # Give it a tiny bit to init the boards
        time.sleep(0.2)

        # Check all the motor boards are initialised and can be indexed
        for i in range(10):
            self.assertTrue(0 in self.robot.servo_boards)

    def test_set_edge_conditions(self):
        board = self.mock.new_servoboard()
        time.sleep(0.2)
        for servo in range(16):
            for pos in [1.0, 1, 0.002, -1]:
                self._try_position(servo, board, pos)
            # Invalid error
            with self.assertRaises(ValueError):
                self._try_position(servo, board, -1.01)

    def _try_position(self, motor, board, value):
        self._try_position_expect(motor, board, value, value)

    def _try_position_expect(self, servo, board, value, expect):
        self.robot.servo_boards[0].servos[servo].position = value
        got_value = board.message_queue.get()
        # Test the motor board got what it expected
        self.assertEqual(got_value, {'servos': {str(servo): expect}})
        # Test the value can be read
        self.assertEqual(self.robot.servo_boards[0].servos[servo].position, value)


class FakeSerialConnection:
    def __init__(self, responses):
        self.responses = responses
        self.received = ''

    @property
    def lines_received(self):
        return self.received.splitlines()

    def write(self, content):
        self.received += content.decode('utf-8')

    def flush(self):
        pass

    def reset_input_buffer(self):
        pass

    def readline(self):
        return self.responses.pop(0).encode('utf-8')


class Counter:
    def __init__(self):
        self.current = 0

    def __call__(self, *args):
        self.current += 1
        return self.current


class FakeSocket:
    def __init__(self, robotd_board):
        self.robotd_board = robotd_board

    def settimeout(self, timeout):
        pass

    def connect(self, location):
        pass


class ServoBoardGenericCommandTest(unittest.TestCase):
    longMessage = True

    def assertCommands(self, expected_commands):
        self.assertEqual(
            expected_commands,
            self.fake_connection.lines_received,
            "Wrong commands send over serial connection.",
        )

    @staticmethod
    def ok_response():
        return '+ ok'

    @staticmethod
    def error_response(error):
        return '- {}'.format(error)

    @staticmethod
    def message_response(message):
        return '> {}'.format(message)

    @staticmethod
    def comment_response(comment):
        return '# {}'.format(comment)

    @staticmethod
    def build_response_lines(command_number, messages):
        return ['@{:d} {}'.format(command_number, x) for x in messages]

    @staticmethod
    def connect_socket_to_robotd_board(socket, robotd_board):
        response_queue = [b'{"greetings": 1}']

        def enqueue_response(response):
            response_queue.append(json.dumps(response).encode('utf-8'))

        def send(raw_data):
            response = robotd_board.command(
                json.loads(raw_data.decode('utf-8')),
            )
            # do what the BoardRunner would do
            if response is not None:
                enqueue_response({'response': response})

            enqueue_response(robotd_board.status())

        def receive(size):
            return response_queue.pop(0) + b'\n'

        socket.sendall = send
        socket.recv = receive

        return response_queue

    def setUp(self):
        self.command_counter = Counter()
        self.mock_randint = mock.patch(
            'robotd.devices.random.randint',
            self.command_counter,
        )
        self.mock_randint.start()

        self.fake_connection = FakeSerialConnection(
            responses=self.build_response_lines(1, [
                self.message_response('fw-version'),
                self.ok_response(),
            ]),
        )
        self.mock_serial = mock.patch(
            'robotd.devices.serial.Serial',
            return_value=self.fake_connection,
        )
        self.mock_serial.start()

        self._servo_assembly = ServoAssembly({'DEVNAME': None})
        self._servo_assembly.make_safe = lambda: None
        self._servo_assembly.start()

        # remove the firmware version query that we don't care about
        self.fake_connection.received = ''

        self.spec_socket = socket.socket()
        socket_mock = mock.Mock(spec=self.spec_socket)
        self.mock_socket = mock.patch(
            'socket.socket',
            return_value=socket_mock,
            autospec=True,
        )
        self.mock_socket.start()

        self.response_queue = self.connect_socket_to_robotd_board(
            socket_mock,
            self._servo_assembly,
        )
        self.board = ServoBoard('')

    def tearDown(self):
        self.mock_socket.stop()
        self.mock_serial.stop()
        self.mock_randint.stop()

        self.spec_socket.close()
        self.board.close()

    def test_command_ok(self):
        RESPONSE = 'the-response'
        self.fake_connection.responses += self.build_response_lines(2, [
            self.message_response(RESPONSE),
            self.ok_response(),
        ])

        actual_response = self.board.direct_command('the-command')

        self.assertEqual(
            [RESPONSE],
            actual_response,
            "Wrong response to command",
        )

        self.assertCommands(['\0@2 the-command'])

        self.assertEqual(
            [],
            self.response_queue,
            "There should be no pending messages from the robotd board after "
            "the command completes",
        )

    def test_error_command_error(self):
        RESPONSE = 'the-response'
        self.fake_connection.responses += self.build_response_lines(2, [
            self.error_response(RESPONSE),
            self.ok_response(),
        ])

        with self.assertRaises(CommandError) as e_info:
            self.board.direct_command('the-command')

        self.assertIn(
            RESPONSE,
            str(e_info.exception),
            "Wrong error message",
        )

        self.assertEqual(
            [],
            self.response_queue,
            "There should be no pending messages from the robotd board after "
            "the command completes",
        )

    def test_error_invalid_response(self):
        RESPONSE = 'the-response'
        self.fake_connection.responses += self.build_response_lines(2, [
            RESPONSE,
        ])

        with self.assertRaises(InvalidResponse) as e_info:
            self.board.direct_command('the-command')

        self.assertIn(
            RESPONSE,
            str(e_info.exception),
            "Wrong error message",
        )

        self.assertEqual(
            [],
            self.response_queue,
            "There should be no pending messages from the robotd board after "
            "the command completes",
        )

    def test_unknown_error(self):
        ERROR_MESSAGE = "fancy error description"

        self._servo_assembly.command = mock.Mock(
            return_value={
                'status': 'error',
                'type': 'newly-added-type',
                'description': ERROR_MESSAGE,
            },
        )

        with self.assertRaises(ArduinoError) as e_info:
            self.board.direct_command('the-command')

        self.assertIn(
            ERROR_MESSAGE,
            str(e_info.exception),
            "Wrong error message",
        )
