"""
Gets sensor data from Delta Solar Cloud.
Author: dylanmazurek
https://github.com/DylanMazurek/hass-delta-solar-cloud
"""
import requests
import datetime
import logging
from collections import defaultdict

# from .const import (
#     _LOGGER
# )

class DeltaSolarCloud(object):
    """ Wrapper class for DeltaSolarCloud"""

    def __init__(self, username, password, plantid, serial):
        self.username = username
        self.password = password
        self.serial = serial
        self.plantid = plantid

    def get_cookie(self):
      """Use api to get data"""
      url = "https://mydeltasolar.deltaww.com/includes/process_login.php"

      headers = {
        'Host': 'mydeltasolar.deltaww.com',
        'Connection': 'keep-alive',
        'Content-Length': '50',
        'Pragma': 'no-cache',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://mydeltasolar.deltaww.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://mydeltasolar.deltaww.com/index.php?lang=en-us',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-AU,en-GB;q=0.9,en-US;q=0.8,en;q=0.7'
      }

      payload = {
        'email': self.username,
        'password': self.password
      }
      response = requests.request("POST", url, headers = headers, data = payload)

      cookie = response.cookies.get('sec_session_id')

      return cookie

    def fetch_data(self):
      """Use api to get live data"""
      url = "https://mydeltasolar.deltaww.com/AjaxPlantUpdatePlant.php"

      cookie = self.get_cookie()

      logger = logging.getLogger("blah")
      logger.setLevel(logging.INFO)

      logger.error('cookie ' + cookie)

      headers = {
        'Host': 'mydeltasolar.deltaww.com',
        'Connection': 'keep-alive',
        'Content-Length': '50',
        'Pragma': 'no-cache',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://mydeltasolar.deltaww.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://mydeltasolar.deltaww.com/index.php?lang=en-us',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-AU,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cookie': 'sec_session_id=' + cookie
      }
      
      now = datetime.datetime.now()

      payload = {
        'item': 'energy',
        'unit': 'day',
        'sn': self.serial,
        'inv_num': '1',
        'is_inv': '1',
        'year': now.strftime('%Y'),
        'month': now.strftime('%m').lstrip("0"),
        'day': now.strftime('%d').lstrip("0"),
        'plant_id': self.plantid,
        'start_date': '2020-11-13',
        'plt_type': '2',
        'mtnm': '1',
        'timezone': '10'
      }

      response = requests.request("POST", url, headers = headers, data = payload).json()

      arrayLength = (len(response['sell']) - 1)

      import json
      logger.error('payload ' + json.dumps(payload))
      logger.error('array length ' + str(arrayLength))
      logger.error('buy ' + str(response['buy'][arrayLength]))

      data = {}

      data['sell'] = (response['sell'][arrayLength], 'mdi:transmission-tower-export', 'W')
      data['buy'] = (response['buy'][arrayLength], 'mdi:transmission-tower-import', 'W')
      data['con'] = (response['con'][arrayLength], 'mdi:home', 'W')
      data['energy'] = (response['tip'][arrayLength], 'mdi:brightness-7', 'W')

      return data