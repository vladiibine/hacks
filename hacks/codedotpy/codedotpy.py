def main():
    name = raw_input('your name: ')

    gender = None
    genders = ['man', 'woman']

    while not gender in genders:
        gender = raw_input('your gender: ')
        
    if gender == 'man':
        print("hi {name}! i know that you're a man".format(name=name))
    else:
        print("hi {}! i know that you're a woman".format(name))
        answer = None
        while answer not in ['y','n']:
            answer = raw_input("would you like to sum up a few numbers? (y/n) ")
        if answer == 'y':
            sum_numbers()
    

def sum_numbers():
    print("type numbers; hit enter; hit twice when you're done")
    sum_ = 0
    number = None
    while number != '':
        number = raw_input('>>> ')
        sum_ += get_number(number)
    print("here's your sum: {}".format(sum_))

def get_number(number):
    if not number:
        return 0
    if number.isdigit():
        return int(number)
    import numbers
    try:
        return float(number)
    except ValueError:
        print("well, that's not a number")
        return 0
    
if __name__ == "__main__":
    main()
