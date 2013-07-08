import os.path
import datetime
import time
import queue
import threading
import requests
import logging
from tornado.options import define, options, parse_config_file, parse_command_line
from pymongo import MongoClient
from bs4 import BeautifulSoup
from libs import config

# Parse the config file
parse_config_file('./settings.conf')

# Requests queue
requestsQueue = queue.Queue()

# Beautiful queue
bsQueue = queue.Queue()

# Store queue
sotreQueue = queue.Queue()

# Database
client = MongoClient(options.db_host, options.db_port)
db = client[options.db_name]

def isInstall():
  '''Check if installed the application
  '''
  lockPath = os.path.join(os.path.dirname(__file__), 'install.lock')
  created = os.path.isfile(lockPath) and True or False
  return created

def createInstallLock():
  '''Create install lock
  '''
  lockPath = os.path.join(os.path.dirname(__file__), 'install.lock')
  f = open(lockPath, 'w')
  f.close()

class RequestsThread(threading.Thread):
  '''Requests the target url and put its result into beaufitulSoupQueue

  Args:
    q: requests queue
    bsq: beautiful soup queue
  '''
  def __init__(self, q, bsq):
    threading.Thread.__init__(self)
    self.q = q
    self.bsq = bsq

  def run(self):
    while True:
      baseUrl = 'http://lcs.yicai.com/index.php?unit=%s'

      # Grabs unit from queue
      unit = self.q.get()

      # Grabs chunk of webpage
      s = requests.Session()
      a = requests.adapters.HTTPAdapter(max_retries = 10)
      s.mount('http://', a)
      try:
        chunk = s.get(baseUrl % unit, timeout = 5).text
      except requests.exceptions.Timeout: # if grabs faild
        logging.error('Grabs %s faild' % (baseUrl % unit))
        chunk = ''

      # Place chunk into beautiful soup queue
      self.bsq.put({ 'unit': unit, 'html': chunk })

      # Signals to queue job is done
      self.q.task_done()

class BsThread(threading.Thread):
  '''Filter the HTML using BeautifulSoup that we need and put
    its result with a Dict class into sotreQueue

  Args:
    q: beautiful soup queue
    storeq: store queue
  '''
  def __init__(self, q, storeq):
    threading.Thread.__init__(self)
    self.q = q
    self.storeq = storeq

  def run(self):
    while True:
      '''Grabs chunk from queue

      Example: { 'unit': '工商银行', 'html', chunk }
      '''
      chunk = self.q.get()

      unit = chunk['unit']
      html = chunk['html']

      # Beautiful soup
      soup = BeautifulSoup(html)

      contestants = {}

      # Current contestant id
      cid = None

      for tags in soup.find_all('div', class_ = 'right2'):
        '''Current contestant id

        Example:
          uid_346181
        '''
        cid = tags.get('id')[4:]

        contestants[cid] = {}

        '''HTML structure demo

        <div class="right2" style="padding-bottom:12px" id="uid_328128"> <img src="http://myfilesdata.yicai.com/attachment/201211/30/0_1354284359LEi8.jpg">
          <p style="color:#000;font-size:14px">陈雪熙</p>
          <p><a href="http://t.yicai.com/b/550961/" title="中行陈雪熙：平衡型客户理财案例" target="_blank">中行陈雪熙：平衡型客户理财案例</a></p>
          <div class="clear"></div>
          <div class="toupiao2"><img style="width:14px;height:26px" src="images/xin.jpg" alt="#"><span id="vote_user_328128">4482</span></div>
          <div class="toupiao" onclick="vote(328128, 'user')" style="cursor:pointer">点击投票</div>
        </div>
        '''
        if not isInstall(): # Grabs all infomation at the first time
          # Name, unit
          for subs in tags.find_all('p', limit = 1):
            contestants[cid]['name'] = subs.text
            contestants[cid]['unit'] = unit

          # Avatar
          for subs in tags.find_all('img', limit = 1):
            contestants[cid]['avatar'] = subs.attrs.get('src', '')

          # Case
          for subs in tags.find_all('a', limit = 1):
            contestants[cid]['case'] = {
              'label': subs.text,
              'url': subs.attrs.get('href', '')
            }

        # Tickets
        for subs in tags.find_all('span'):
          contestants[cid]['tickets'] = int(subs.text)

      # Place contestants' infomation into storage queue
      self.storeq.put(contestants)

      # Signals to queue job is done
      self.q.task_done()

class StoreThread(threading.Thread):
  '''Store the contestants' infomation into database

  Args:
    q: storage queue
  '''
  def __init__(self, q):
    threading.Thread.__init__(self)
    self.q = q

  def run(self):
    while True:
      # Grabs contestants' infomation from queue
      contestants = self.q.get()

      if not isInstall(): # then insert all infomation
        for cid, contestant in contestants.items():
          contestant['cid'] = cid
          db.contestants.insert(contestant)
      else: # then just update the tickets    
        for cid, contestant in contestants.items():
          db.contestants.update({ 'cid': cid }, { "$set": {
            'tickets': contestant['tickets']
          }})

      # Signals to queue job is done
      self.q.task_done()

def main():
  '''Get the contestants' infomation of the first Yicai financial match
    and then put them into database.

  Author: Li Zhineng <lizhineng@gmail.com>
  URL: http://zhineng.li
  '''
  # Spawn a pool of threads, and pass them queue instance
  for i in range(10):
    rt = RequestsThread(requestsQueue, bsQueue)
    rt.setDaemon(True)
    rt.start()

  for i in range(8):
    bt = BsThread(bsQueue, sotreQueue)
    bt.setDaemon(True)
    bt.start()

  for i in range(5):
    st = StoreThread(sotreQueue)
    st.setDaemon(True)
    st.start()

  # Wait on the queues until everything has been processed
  requestsQueue.join()
  bsQueue.join()
  sotreQueue.join()

if __name__ == '__main__':
  '''Parse command line

  Examples:
    $ python3 backend.py --interval=5
  '''
  parse_command_line()

  main()

  # Banks
  units = ['中国银行', '招商银行', '交通银行', '平安银行', '兴业银行', '光大银行', '汇丰银行',
              '东亚银行', '星展银行', '大华银行', '建设银行', '泽世投资', '景淳投资', '海银金融',
              '平安信托', '百基资产', '国泰君安', '嘉华财富', '华泰证券', '华泰人寿', '中国平安']

  # Pass the units into requestsQueue every `options.interval` seconds
  while True:
    for unit in units:
      requestsQueue.put(unit)

    # Update last update
    db.info.update({ 'name': 'lastUpdate' }, { '$set': {
      'value': datetime.datetime.now()
    }}, upsert = True)

    # Create install lock if the app hasn't been installed
    if not isInstall():
      # Sleep 10 seconds to wait the queues to finish all tasks
      time.sleep(10)
      createInstallLock()

    time.sleep(options.interval)