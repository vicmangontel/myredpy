def to_multiline_text(name: str, max_line_length=40, max_length=80, omitt_prefix='') -> str:
    """
    Breaks down the project name in a multiline text if the length 
    exceeds certain limit
    """
    # if omitt prefix is passed, remove it from the beggining
    if omitt_prefix.strip():
        if name.startswith(omitt_prefix):
            name = name[len(omitt_prefix):]
    # reduce text to max line allowed:
    name = (name[:max_length] + '..') if len(name) > max_length else name
    # accumulated line length
    ACC_length = 0
    words = name.split(' ')
    formatted_name = ''
    for word in words:
        # if ACC_length + len(word) and a space is <= max_line_length
        if ACC_length + (len(word) + 1) <= max_line_length:
            # append the word and a space
            formatted_name = formatted_name + word + " "
            # length = length + length of word + length of space
            ACC_length = ACC_length + len(word) + 1
        else:
            # append a line break, then the word and a space
            formatted_name = formatted_name + "\n" + word + " "
            # reset counter of length to the length of a word and a space
            ACC_length = len(word) + 1
    return formatted_name
