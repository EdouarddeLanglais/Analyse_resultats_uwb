def get_number_from_string(string, start, end, output):
    number_str = ""

    for i in range(start, end):
        number_str += chr(string[i])
    
    return output(number_str)