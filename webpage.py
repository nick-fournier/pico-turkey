with open('template.html', 'r') as f:
    html_string = f.read()
    
def webpage(webhost):
    #Template HTML
    html = html_string.replace('{{webhost}}', webhost)
    
    return str(html)