"""
Kochka core related lib

Copyright 2017 Pavel Folov
"""

import re
from enum import Enum
from textwrap import shorten

from patterns import Event
from oslib import filebackup


class Set:
    """Подходы: вес, повторения, подходы"""

    __slots__ = ['weight', 'count', 'set_count']

    # to access by index
    # getattr(set_, Set.ATTRS[col])
    ATTRS = __slots__

    def __init__(self, weight, count, set_count=1):
        self.weight = int(weight)
        self.count = int(count)
        self.set_count = int(set_count)

    @property
    def total_weight(self) -> int:
        return self.weight * self.count * self.set_count

    def __str__(self):
        if self.set_count > 1:
            return '{} {} x{}'.format(self. weight, self.count, self.set_count)
        else:
            return '{} {}'.format(self.weight, self.count)


class Exercise:
    """Упражнение из подходов"""

    __slots__ = ['date', 'name', 'sets', 'note']

    # to access by index
    # getattr(exercise, Exercise.ATTRS[col])
    ATTRS = __slots__

    def __init__(self, date=None, name=None, sets=None, note=None):
        self.date = date
        self.name = name
        self.sets = sets or []
        self.note = note

    def add_set(self, set_: Set):
        self.sets.append(set_)

    @property
    def total_weight(self) -> int:
        return sum(s.total_weight for s in self.sets)

    @property
    def sets_str(self) -> str:
        return ' '.join('[{}]'.format(str(s)) for s in self.sets)

    def str_to_save(self) -> str:
        record_list = [self.date, self.name]
        if self.note:
            record_list.append(self.note_to_save)
        record_list.append('\n'.join('{}'.format(str(s)) for s in self.sets))
        return '\n'.join(record_list)

    @property
    def note_to_save(self):
        return '# {}'.format(self.note)

    @property
    def name_with_note(self):
        if self.note is None:
            return self.name
        else:
            return '{} ({})'.format(
                self.name,
                shorten(self.note, width=20, placeholder='...')
            )

    def __str__(self):
        return 'date({0.date}), name({0.name}), sets({0.sets_str})'.format(
            self)


class ParserState(Enum):
    START = 0
    DATE_GOT = 1
    NAME_GOT = 2
    NOTE_GOT = 3
    SETS_GETTING = 4
    DONE = 5


class ExerciseTxtParser:
    """
    Training text file parser

    2017.01.13
    жим
    #травма, поясница
    35 5
    45 10 х5
    50 6 х2

    >>> parser = ExerciseTxtParser('data.txt')
    >>> for e in parser: print(e)
    >>> # date(2017.01.13), name(жим), sets([35 5] [45 10 x5] [50 6 x2])
    """

    date_pattern = re.compile(r'(?P<Y>\d{4})\.(?P<M>\d{2})\.(?P<D>\d{2})$')
    name_pattern = re.compile(r'(?P<NAME>\w+)$')
    set_pattern = re.compile(r'(?P<WEIGHT>\d{2,3}) (?P<COUNT>\d{1,2})'
                             r'(?:\s?[\*xXхХ]\s?(?P<SET_COUNT>\d{1,2}))?$')

    def __init__(self, filename: str):
        self.filename = filename
        self.state = ParserState.START
        self.currentExercise = None
        self.on_error = Event()

    def __iter__(self):
        # из cookbook, может лучше просто итератор реализовать
        with open(self.filename) as f:
            for lineno, line in enumerate(f, start=1):
                self.dispatch_line(line.rstrip(), lineno)
                if self.is_done:
                    self.state = ParserState.START
                    yield self.currentExercise
                    self.currentExercise = None

    @property
    def is_start(self):
        return self.state is ParserState.START

    @property
    def is_date_got(self):
        return self.state is ParserState.DATE_GOT

    @property
    def is_name_got(self):
        return self.state is ParserState.NAME_GOT

    @property
    def is_note_got(self):
        return self.state is ParserState.NOTE_GOT

    @property
    def is_sets_getting(self):
        return self.state is ParserState.SETS_GETTING

    @property
    def is_done(self):
        return self.state is ParserState.DONE

    # todo: избавиться от условий (конечный автомат, или еще чего)
    def dispatch_line(self, line: str, lineno: int):
        done_cond = (not line) and self.is_sets_getting
        if done_cond:
            self.state = ParserState.DONE
            return
        elif not line:
            self.on_error('Unexpected new line: lineno({}), detail{}'.format(
                lineno, str(self)))
            return
        elif self.is_start and self.date_pattern.match(line):
            self.currentExercise = Exercise(date=line)
            self.state = ParserState.DATE_GOT
            return
        elif self.is_date_got and self.name_pattern.match(line):
            self.currentExercise.name = line
            self.state = ParserState.NAME_GOT
            return
        elif self.is_name_got and line.startswith('#'):
            self.currentExercise.note = line.lstrip('# ')
            self.state = ParserState.NOTE_GOT
            return
        elif self.is_name_got or self.is_note_got or self.is_sets_getting:
            match = self.set_pattern.match(line)
            if match:
                self.currentExercise.sets.append(
                    self._create_set_by_match(match))
                self.state = ParserState.SETS_GETTING
                return
        err_msg = 'Parser sequence error: lineno({}), line({}), detail({})'
        self.on_error(err_msg.format(lineno, line, str(self)))

    def _create_set_by_match(self, match):
        set_dict = match.groupdict()
        if set_dict['SET_COUNT']:
            return Set(set_dict['WEIGHT'], set_dict['COUNT'],
                       set_dict['SET_COUNT'])
        else:
            return Set(set_dict['WEIGHT'], set_dict['COUNT'])

    def __str__(self):
        return 'Parser: {0.state}, exercise({0.currentExercise})'.format(self)


def save_exercises_to_file(filename, exercises):
    """Writes exercises to file"""
    if not exercises:
        raise ValueError('Exercises cannot be empty')

    with filebackup(filename), open(filename, 'w') as f:
        for exercise in exercises:
            f.write(''.join([
                exercise.str_to_save(),
                '\n\n'
            ]))
