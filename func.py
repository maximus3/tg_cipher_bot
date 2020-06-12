def get_commands(commands):
    text = ''
    for command in commands:
        text += command['command'] + ' - ' + command['description'] + '\n'
    return text