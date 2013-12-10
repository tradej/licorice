
import pytest

from licorice import helper

class TestHelper():

    @pytest.mark.parametrize(('line', 'result'), [
        ('a b c', ['a', 'b', 'c']),
        ('a . c', ['a', 'c']),
        ('a, c', ['a', 'c']),
        (',a c', ['a', 'c']),
        ('a ,, c', ['a', 'c']),
        ('', [])
        ])
    def test_tokenize(self, line, result):
        assert helper.tokenize(line) == result

    def test_tokenize_newline(self):
        assert helper.tokenize('', with_newline=True)[-1] == '\n'

