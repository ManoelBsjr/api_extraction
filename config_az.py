from configparser import ConfigParser

def load_config(filename='conns.ini', section='azurestorage'):
    parser = ConfigParser()
    parser.read(filename)

    # get section
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')

    return config