"""
Gets sensor data from Delta Solar Cloud.
Author: dylanmazurek
https://github.com/DylanMazurek/hass-delta-solar-cloud
"""
import requests
import datetime
import logging
from collections import defaultdict

# from const import (
#     _LOGGER
# )

class DeltaSolarCloud(object):
    """ Wrapper class for DeltaSolarCloud"""

    def __init__(self, username, password):
        #self.cookie = None
        self.username = username
        self.password = password

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
        'unit': 'day',
        'sn': 'O9Y20300564WB',
        'inv_num': '1',
        'is_inv': '1',
        'year': '2022',
        'month': '1',
        'day': '12',
        'plant_id': '23400',
        'start_date': '2020-11-13',
        'plt_type': '2',
        'mtnm': '1',
        'timezone': '10'
      }

      response = requests.request("POST", url, headers = headers, data = payload).json()

      arrayLength = (len(response['sell']) - 1)
      logging.debug(arrayLength)
      

      # return {
      #   'sell': response['sell'][arrayLength],
      #   'buy': response['buy'][arrayLength],
      #   'con': response['con'][arrayLength],
      #   'energy': response['tip'][arrayLength]
      # }

      data = {}

      data['sell'] = (response['sell'][arrayLength], 'mdi:transmission-tower-export', 'kW')
      data['buy'] = (response['buy'][arrayLength], 'mdi:transmission-tower-import', 'kW')
      data['con'] = (response['con'][arrayLength], 'mdi:home', 'kW')
      data['energy'] = (response['tip'][arrayLength], 'mdi:brightness-7', 'kW')

      return data