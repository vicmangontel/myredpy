def to_multiline_text(name:str, max_line_length=40, max_length=80, omitt_prefix='') -> str:
    """
    Breaks down the project name in a multiline text if the length exceeds certain limit
    """
    if omitt_prefix.strip():
        if name.startswith(omitt_prefix):
            name = name[len(omitt_prefix):]
    
    name = (name[:max_length] + '..') if len(name) > max_length else name

    acc_length = 0
    words = name.split(' ')
    formatted_name = ''
    for word in words:
        if acc_length + (len(word) + 1) <= max_line_length:
            formatted_name = formatted_name + word + " "
            acc_length = acc_length + len(word) + 1
        else:
            formatted_name = formatted_name + "\n" + word + " "
            acc_length = len(word) + 1
    return formatted_name 