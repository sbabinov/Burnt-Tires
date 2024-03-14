DAYS_IN_MONTH = {
    "January": 31,
    "February": 28,
    "March": 31,
    "April": 30,
    "May": 31,
    "June": 30,
    "July": 31,
    "August": 31,
    "September": 30,
    "October": 31,
    "November": 30,
    "December": 31,
}

DAY_ENDINGS = {
    1: 'st',
    2: 'nd',
    3: 'rd'
}
for n in range(4, 32):
    DAY_ENDINGS[n] = 'th'
