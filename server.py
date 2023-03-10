from flask import Flask
from flask import render_template
from datetime import datetime
import json
import configparser  
import logging
from task import get_pic

config=configparser.ConfigParser()


app = Flask(__name__)

@app.route('/teen')
def teen():
    if datetime.now().weekday() == 0:
        get_pic()
    config.read('./config',encoding='utf-8')
    course_name = config.get('COURSEINFO','course_name')
    context = {"flag":course_name}
    return render_template('teen.html',**context)
    
    

if __name__ == '__main__':
    logging.basicConfig(handlers=[logging.FileHandler(filename='./teen.log',
                                                      encoding='utf-8', mode='a+')],
                        format='%(asctime)s %(message)s',
                        level=getattr(logging, 'INFO'))
    app.run(host="0.0.0.0", port=5000)