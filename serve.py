import logging
import os.path
import tornado.ioloop
import tornado.web
from tornado.options import options, parse_config_file
from pymongo import MongoClient
from libs import vote, config

# Parse the config file
parse_config_file('settings.conf')

# Database
client = MongoClient(options.db_host, options.db_port)
db = client[options.db_name]

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    contestants = db.contestants.find().sort('tickets', -1)
    counter = contestants.count()
    lastUpdate = db.info.find_one({ 'name': 'lastUpdate' })['value']
    self.render('home.html', contestants = contestants, counter = counter, lastUpdate = lastUpdate)

class VoteHandler(tornado.web.RequestHandler):
  def get(self):
    try:
      cid = self.get_argument('cid', True)
      tickets = int(self.get_argument('tickets', True))
    except:
      return

    # Between 1 ~ ???
    if tickets > 0:
      if tickets == 1:
        result = vote.vote(cid)
        self.write(result)
      else: # Maybe a big number
        vote.voteHelper(cid, tickets)
    else:
      return

config = dict(
  debug = options.debug,
  template_path = os.path.join(os.path.dirname(__file__), 'templates'),
  static_path = os.path.join(os.path.dirname(__file__), 'static'),
  gzip = options.gzip
)

application = tornado.web.Application([
  (r'/', MainHandler),
  (r'/vote', VoteHandler)
], **config)

if __name__ == '__main__':
  application.listen(options.port)
  logging.info('Starting tornado server on port %i' % options.port)
  tornado.ioloop.IOLoop.instance().start()