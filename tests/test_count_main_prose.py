from scripts.count_main_prose import count_words


def test_count_words_ignores_commands_comments_and_math():
    text = r"""
    % ignored comment
    \section{Visible Heading}
    Visible prose has four words.
    \[
      x = y + z
    \]
    \caption{Visible caption words}
    """
    assert count_words(text) == 10
