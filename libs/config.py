from tornado.options import define

# Web
define('port', default = 8080, help = 'Run on the given port', type = int)
define('debug', default = False, help = 'Run in debug mode', type = bool)
define('gzip', default = True, help = 'Enable gzip compression', type = bool)

# Mongodb
define('db_host', default = 'localhost', help = 'MongoDB host', type = str)
define('db_port', default = 27017, help = 'MongoDB running port', type = int)
define('db_name', default = 'yicai', help = 'The name of the database', type = str)

# Back end
define('interval', default = 10, help = 'How long will the back end grabs the data (second)?', type = int)