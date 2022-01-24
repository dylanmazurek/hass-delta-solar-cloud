"""
Gets sensor data from Delta Solar Cloud.
Author: dylanmazurek
https://github.com/DylanMazurek/hass-delta-solar-cloud
"""
import requests
import logging
from datetime import datetime, timedelta
from collections import defaultdict

# from .const import (
#     _LOGGER
# )

class DeltaSolarCloud(object):
    """ Wrapper class for DeltaSolarCloud"""

    def __init__(self, username, password, plantid, serial, timezone):
        self.username = username
        self.password = password
        self.serial = serial
        self.plantid = plantid
        self.timezone = timezone

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

    def fetch_api_data(self, cookie, datetime, plantid, serial, type):
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
      
      payload = {
        'item': 'energy',
        'unit': type,
        'sn': serial,
        'inv_num': '1',
        'is_inv': '1',
        'year': datetime.strftime('%Y'),
        'month': datetime.strftime('%m').lstrip("0"),
        'day': datetime.strftime('%d').lstrip("0"),
        'plant_id': plantid,
        'start_date': '2020-11-13',
        'plt_type': '2',
        'mtnm': '1',
        'timezone': '10'
      }

      url = "https://mydeltasolar.deltaww.com/AjaxPlantUpdatePlant.php"

      return requests.request("POST", url, headers = headers, data = payload).json()

    def fetch_data(self):
      """Use api to get live data"""

      cookie = self.get_cookie()

      now = datetime.utcnow() + timedelta(hours=self.timezone)
      
      dataDay = self.fetch_api_data(cookie, now, self.plantid, self.serial, 'day')

      arrayLengthDay = (len(dataDay['sell']) - 1)

      data = {}
      if arrayLengthDay > 0:
        data['sell'] = (dataDay['sell'][arrayLengthDay], 'mdi:transmission-tower-export', 'W')
        data['buy'] = (abs(dataDay['buy'][arrayLengthDay]), 'mdi:transmission-tower-import', 'W')
        data['con'] = (abs(dataDay['con'][arrayLengthDay]), 'mdi:home', 'W')
        data['energy'] = (dataDay['tip'][arrayLengthDay], 'mdi:brightness-7', 'W')
      else:
        data['sell'] = (0, 'mdi:transmission-tower-export', 'W')
        data['buy'] = (0, 'mdi:transmission-tower-import', 'W')
        data['con'] = (0, 'mdi:home', 'W')
        data['energy'] = (0, 'mdi:brightness-7', 'W')

      now = datetime.now()
      dataMonth = self.fetch_api_data(cookie, now, self.plantid, self.serial, 'month')
      date = '{}-{}-{}'.format(now.strftime('%Y'), now.strftime('%m'), now.strftime('%d'))
      indexOfMonth = dataMonth['ts'].index(date)

      dataTest = dataMonth['sell'][indexOfMonth]

      spikeBlock = (int(now.strftime('%H')) < 4 and abs(dataMonth['energy'][indexOfMonth]) > 2000)

      if(dataTest is not None and not spikeBlock):
        data['daysell'] = (dataMonth['sell'][indexOfMonth], 'mdi:transmission-tower-export', 'Wh')
        data['daybuy'] = (abs(dataMonth['buy'][indexOfMonth]), 'mdi:transmission-tower-import', 'Wh')
        data['daycon'] = (abs(dataMonth['con'][indexOfMonth]), 'mdi:home', 'Wh')
        data['dayenergy'] = (dataMonth['energy'][indexOfMonth], 'mdi:brightness-7', 'Wh')
      else:
        data['daysell'] = (0, 'mdi:transmission-tower-export', 'Wh')
        data['daybuy'] = (0, 'mdi:transmission-tower-import', 'Wh')
        data['daycon'] = (0, 'mdi:home', 'Wh')
        data['dayenergy'] = (0, 'mdi:brightness-7', 'Wh')
      
      return data
      