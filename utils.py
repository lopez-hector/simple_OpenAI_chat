from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
from pygments.styles import get_style_by_name
from pygments.lexers import get_lexer_by_name


def get_code_formatted(code, language):
    try:
        lexer = get_lexer_by_name(language)
    except:
        lexer = PythonLexer()

    formatter = TerminalFormatter(style=get_style_by_name('xcode'))
    return highlight(code, lexer, formatter)


def get_formatted_text(input):
    """
    Converts input to formatted code and text.
    :param input:
    :return:
    """

    code_marker = '```'
    split_text = input.split(code_marker)

    # Every even entry would be a code entry
    # assuming that code is always enclosed by ```
    for i in range(len(split_text)):
        if i > 0 and i % 2 == 1:
            language = split_text[i][:split_text[i].find('\n')]
            split_text[i] = get_code_formatted(code=split_text[i], language=language)

    return ''.join(split_text)
