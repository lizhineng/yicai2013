import requests
import socket
import struct
import random
import queue
import threading

def vote(cid):
  '''Vote for someone whose id is cid

  Args:
  cid: the contestant id

  Return the HTTP request

  Author: Li Zhineng <lizhineng@gmail.com>
  Url: http://zhineng.li
  '''
  # IP Address from 0 ~ 4294967295
  randInt = int(random.random() * (4294967295 + 1))
  ip = socket.inet_ntoa(struct.pack('I',socket.htonl(randInt)))

  # Number => String
  cid = str(cid)

  # Custom headers
  headers = {
    'X-Forwarded-For': ip,
    'Referer': 'http://lcs.yicai.com'
  }

  obj = requests.get('http://lcs.yicai.com/do.php?ac=vote&inajax=1&op=vote&type=user&id=' + cid, headers = headers)
  return obj.text

class _voteThread(threading.Thread):
  '''Vote for someone (Just a Thread class)

  Arg:
    q: vote queue
  '''
  def __init__(self, q):
    self.q = q
    threading.Thread.__init__(self)

  def run(self):
    while True:
      cid = self.q.get()

      # Vote for someone
      vote(cid)

      # Signals to queue job is done
      self.q.task_done()

def voteHelper(cid, tickets):
  '''Vote helper (multithreading)
  '''
  # Create a new queue
  voteQueue = queue.Queue()

  # Tickets that you want to vote
  [voteQueue.put(cid) for i in range(int(tickets))]

  # Spawn a pool of threads
  for i in range(20):
    st = _voteThread(voteQueue)
    st.setDaemon(True)
    st.start()

  # Wait on the queues until everything has been processed
  voteQueue.join()

if __name__ == '__main__':
  pass