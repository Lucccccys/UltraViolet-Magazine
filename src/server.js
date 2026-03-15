require('dotenv').config();
const path = require('path');
const express = require('express');
const session = require('express-session');
const MongoStore = require('connect-mongo');
const methodOverride = require('method-override');
const morgan = require('morgan');
const { connectToDatabase } = require('./config/db');
const { attachGlobals, attachFlashLikeMessage } = require('./middleware/viewData');
const publicRoutes = require('./routes/public');
const adminRoutes = require('./routes/admin');
const apiRoutes = require('./routes/api');
const { ensureAdminUser } = require('./services/bootstrap');

const app = express();
const port = Number(process.env.PORT || 3000);

async function start() {
  await connectToDatabase();
  await ensureAdminUser();

  app.set('view engine', 'ejs');
  app.set('views', path.join(__dirname, 'views'));

  app.use(morgan('dev'));
  app.use(express.urlencoded({ extended: true }));
  app.use(express.json({ limit: '1mb' }));
  app.use(methodOverride('_method'));
  app.use(express.static(path.join(__dirname, '..', 'public')));
  app.get('/home-assets/:file', (req, res) => {
    const allowedFiles = new Set(['background.webp', 'background-2.webp', 'logo.webp']);
    const { file } = req.params;
    if (!allowedFiles.has(file)) {
      return res.status(404).end();
    }

    return res.sendFile(path.join(__dirname, '..', file));
  });

  app.use(
    session({
      secret: process.env.SESSION_SECRET || 'development-secret',
      resave: false,
      saveUninitialized: false,
      store: MongoStore.create({
        mongoUrl: process.env.MONGODB_URI,
        ttl: 60 * 60 * 24 * 7
      }),
      cookie: {
        httpOnly: true,
        sameSite: 'lax',
        secure: false,
        maxAge: 1000 * 60 * 60 * 24 * 7
      }
    })
  );

  app.use(attachFlashLikeMessage);
  app.use(attachGlobals);

  app.use('/', publicRoutes);
  app.use('/admin', adminRoutes);
  app.use('/api', apiRoutes);

  app.use((req, res) => {
    res.status(404).render('pages/error', {
      title: 'Page Not Found',
      statusCode: 404,
      message: 'The page you are looking for does not exist.'
    });
  });

  app.use((error, req, res, next) => {
    console.error(error);
    res.status(500).render('pages/error', {
      title: 'Server Error',
      statusCode: 500,
      message: 'Something went wrong on the server.'
    });
  });

  app.listen(port, () => {
    console.log(`UV Magazine app running at http://localhost:${port}`);
  });
}

start().catch((error) => {
  console.error('Failed to start application:', error);
  process.exit(1);
});
