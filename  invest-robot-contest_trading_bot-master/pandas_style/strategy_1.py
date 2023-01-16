def color_macd(col):
    if col.name == "macd":
        return ['background-color: red'
                if x < 0
                else 'background-color: green'
                for i, x in col.iteritems()]

    if col.name == "adx":
        return ['background-color: red'
                if x < 20
                else 'background-color: green'
                for i, x in col.iteritems()]

    else:
        return ['background-color: white'
                for i, x in col.iteritems()]


def color_adx(val):
    if val < 20:
        color = 'red'
    elif val < 40:
        color = '#90EE90'
    elif val < 60:
        color = '#006400'
    elif val < 80:
        color = '#90EE90'
    elif val < 100:
        color = '#8B0000'
    else:
        color = 'white'
    return 'color: %s' % color
