from pathlib import Path
root = Path('/mnt/data/uv-magazine-app')
files = {}
files['package.json'] = r'''
{
  "name": "uv-magazine-fullstack",
  "version": "1.0.0",
  "private": true,
  "description": "Full-stack English website for Ultraviolet Magazine using Express, EJS, MongoDB, and Mongoose.",
  "main": "src/server.js",
  "scripts": {
    "dev": "node src/server.js",
    "start": "NODE_ENV=production node src/server.js",
    "seed": "node src/seed.js",
    "check": "node --check src/server.js && node --check src/seed.js && node --check src/routes/public.js && node --check src/routes/admin.js && node --check src/routes/api.js"
  },
  "dependencies": {
    "bcryptjs": "^2.4.3",
    "connect-mongo": "^5.1.0",
    "dotenv": "^16.4.5",
    "ejs": "^3.1.10",
    "express": "^4.21.2",
    "express-session": "^1.18.1",
    "method-override": "^3.0.0",
    "mongoose": "^8.9.2",
    "morgan": "^1.10.0"
  }
}
'''
files['.env.example'] = r'''
PORT=3000
MONGODB_URI=mongodb://127.0.0.1:27017/uv-magazine
SESSION_SECRET=change-this-session-secret
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change-this-admin-password
SITE_URL=http://localhost:3000
'''
files['README.md'] = r'''
# UV Magazine Full-Stack Website

A full-stack English website for a literary and multimedia magazine. It covers the functional requirements from the provided PDF:

- Home page with About / Gallery / Submit navigation
- Featured Issues section
- Footer social links
- About page
- Gallery page with LOOK / READ / LISTEN / WATCH category entry cards
- LOOK page for artwork and photography in a grid
- READ page for short stories and poems as cards, plus detail pages
- LISTEN page with audio players
- WATCH page with video embeds
- Logo/home navigation and submit CTA
- Submission form backed by MongoDB
- Admin area for managing content, issues, about text, links, and submissions

The original PDF specifies these core functions and page groupings. fileciteturn3file0 fileciteturn3file1turn3file2

## Stack

- Node.js
- Express
- EJS
- MongoDB + Mongoose
- express-session
- Basic CSS and vanilla JavaScript

## Quick start

1. Copy `.env.example` to `.env`
2. Set `MONGODB_URI`, `SESSION_SECRET`, `ADMIN_EMAIL`, and `ADMIN_PASSWORD`
3. Install dependencies
   ```bash
   npm install
   ```
4. Seed the database
   ```bash
   npm run seed
   ```
5. Start the server
   ```bash
   npm run dev
   ```
6. Open `http://localhost:3000`

## Admin login

Go to `/admin/login`

The first run creates an admin user using:

- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`

## Content model summary

- `ContentItem`
  - categories: `look`, `read`, `listen`, `watch`
  - subtypes for finer classification such as artwork, photography, poem, short-story, music, spoken-word, short-film, video
- `Issue`
- `SocialLink`
- `Submission`
- `PageSetting`
- `User`

## Submission behavior

The PDF references a submit button that can jump to a Google Form. This implementation supports both:

- internal site submission page at `/submit`
- optional external submission URL in admin settings

If `submissionMode` is set to `external`, the submit button redirects to the external form URL.

## Media notes

To keep the app stable and simple:

- images are stored as URLs
- audio is stored as hosted file URLs
- video is stored as embed URLs (YouTube/Vimeo) or direct video URLs

## Suggested production hardening

Before production, add:

- CSRF protection
- rate limiting
- stricter content sanitization
- secure cookies and HTTPS
- file upload service if needed
- richer admin roles if a team will manage the site
'''
files['src/server.js'] = r'''
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
'''
files['src/config/db.js'] = r'''
const mongoose = require('mongoose');

async function connectToDatabase() {
  const mongoUri = process.env.MONGODB_URI;

  if (!mongoUri) {
    throw new Error('MONGODB_URI is not set.');
  }

  mongoose.set('strictQuery', true);

  await mongoose.connect(mongoUri, {
    autoIndex: true
  });

  console.log('Connected to MongoDB');
}

module.exports = { connectToDatabase };
'''
files['src/middleware/viewData.js'] = r'''
const PageSetting = require('../models/PageSetting');
const SocialLink = require('../models/SocialLink');

function attachFlashLikeMessage(req, res, next) {
  res.locals.message = req.session.message || null;
  delete req.session.message;
  next();
}

async function attachGlobals(req, res, next) {
  try {
    const [settings, socialLinks] = await Promise.all([
      PageSetting.findOne({ key: 'site' }).lean(),
      SocialLink.find({ isActive: true }).sort({ order: 1 }).lean()
    ]);

    res.locals.currentPath = req.path;
    res.locals.socialLinks = socialLinks;
    res.locals.siteSettings = settings ? settings.value : {};
    res.locals.isAdminAuthenticated = Boolean(req.session.userId);
    next();
  } catch (error) {
    next(error);
  }
}

module.exports = {
  attachGlobals,
  attachFlashLikeMessage
};
'''
files['src/middleware/auth.js'] = r'''
function requireAdmin(req, res, next) {
  if (!req.session.userId) {
    req.session.message = { type: 'error', text: 'Please sign in to access the admin area.' };
    return res.redirect('/admin/login');
  }

  return next();
}

module.exports = { requireAdmin };
'''
files['src/models/User.js'] = r'''
const mongoose = require('mongoose');

const userSchema = new mongoose.Schema(
  {
    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true
    },
    passwordHash: {
      type: String,
      required: true
    },
    role: {
      type: String,
      enum: ['admin'],
      default: 'admin'
    }
  },
  { timestamps: true }
);

module.exports = mongoose.model('User', userSchema);
'''
files['src/models/ContentItem.js'] = r'''
const mongoose = require('mongoose');

const contentItemSchema = new mongoose.Schema(
  {
    title: { type: String, required: true, trim: true },
    slug: { type: String, required: true, unique: true, trim: true },
    category: {
      type: String,
      required: true,
      enum: ['look', 'read', 'listen', 'watch']
    },
    subtype: { type: String, default: '', trim: true },
    creatorName: { type: String, required: true, trim: true },
    summary: { type: String, default: '', trim: true },
    body: { type: String, default: '' },
    issueYear: { type: Number },
    coverImageUrl: { type: String, default: '' },
    imageUrls: [{ type: String }],
    audioUrl: { type: String, default: '' },
    videoUrl: { type: String, default: '' },
    externalUrl: { type: String, default: '' },
    durationLabel: { type: String, default: '' },
    isPublished: { type: Boolean, default: true },
    isFeatured: { type: Boolean, default: false },
    sortOrder: { type: Number, default: 0 }
  },
  { timestamps: true }
);

contentItemSchema.index({ category: 1, isPublished: 1, sortOrder: 1, createdAt: -1 });

module.exports = mongoose.model('ContentItem', contentItemSchema);
'''
files['src/models/Issue.js'] = r'''
const mongoose = require('mongoose');

const issueSchema = new mongoose.Schema(
  {
    year: { type: Number, required: true, unique: true },
    title: { type: String, required: true, trim: true },
    summary: { type: String, default: '', trim: true },
    coverImageUrl: { type: String, default: '' },
    externalUrl: { type: String, default: '' },
    isFeatured: { type: Boolean, default: true },
    order: { type: Number, default: 0 }
  },
  { timestamps: true }
);

module.exports = mongoose.model('Issue', issueSchema);
'''
files['src/models/SocialLink.js'] = r'''
const mongoose = require('mongoose');

const socialLinkSchema = new mongoose.Schema(
  {
    label: { type: String, required: true, trim: true },
    icon: { type: String, required: true, trim: true },
    url: { type: String, required: true, trim: true },
    order: { type: Number, default: 0 },
    isActive: { type: Boolean, default: true }
  },
  { timestamps: true }
);

module.exports = mongoose.model('SocialLink', socialLinkSchema);
'''
files['src/models/Submission.js'] = r'''
const mongoose = require('mongoose');

const submissionSchema = new mongoose.Schema(
  {
    name: { type: String, required: true, trim: true },
    email: { type: String, required: true, trim: true, lowercase: true },
    category: {
      type: String,
      required: true,
      enum: ['look', 'read', 'listen', 'watch']
    },
    title: { type: String, required: true, trim: true },
    creatorName: { type: String, default: '', trim: true },
    summary: { type: String, default: '', trim: true },
    assetUrl: { type: String, default: '', trim: true },
    notes: { type: String, default: '' },
    status: {
      type: String,
      enum: ['new', 'reviewed', 'accepted', 'rejected'],
      default: 'new'
    }
  },
  { timestamps: true }
);

module.exports = mongoose.model('Submission', submissionSchema);
'''
files['src/models/PageSetting.js'] = r'''
const mongoose = require('mongoose');

const pageSettingSchema = new mongoose.Schema(
  {
    key: { type: String, required: true, unique: true, trim: true },
    value: { type: mongoose.Schema.Types.Mixed, default: {} }
  },
  { timestamps: true }
);

module.exports = mongoose.model('PageSetting', pageSettingSchema);
'''
files['src/services/bootstrap.js'] = r'''
const bcrypt = require('bcryptjs');
const User = require('../models/User');

async function ensureAdminUser() {
  const email = (process.env.ADMIN_EMAIL || '').trim().toLowerCase();
  const password = process.env.ADMIN_PASSWORD || '';

  if (!email || !password) {
    console.warn('Admin bootstrap skipped because ADMIN_EMAIL or ADMIN_PASSWORD is missing.');
    return;
  }

  const existingUser = await User.findOne({ email });
  if (existingUser) {
    return;
  }

  const passwordHash = await bcrypt.hash(password, 10);
  await User.create({ email, passwordHash, role: 'admin' });
  console.log(`Created admin user: ${email}`);
}

module.exports = { ensureAdminUser };
'''
files['src/services/settings.js'] = r'''
const PageSetting = require('../models/PageSetting');

async function getSetting(key, fallback = {}) {
  const record = await PageSetting.findOne({ key }).lean();
  return record ? record.value : fallback;
}

async function upsertSetting(key, value) {
  await PageSetting.findOneAndUpdate(
    { key },
    { value },
    { upsert: true, new: true, setDefaultsOnInsert: true }
  );
}

module.exports = {
  getSetting,
  upsertSetting
};
'''
files['src/utils/slugify.js'] = r'''
function slugify(input) {
  return String(input)
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .replace(/-{2,}/g, '-');
}

module.exports = { slugify };
'''
files['src/utils/content.js'] = r'''
function normalizeImageUrls(rawValue) {
  if (!rawValue) {
    return [];
  }

  if (Array.isArray(rawValue)) {
    return rawValue.filter(Boolean);
  }

  return String(rawValue)
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean);
}

function categoryMeta(category) {
  const map = {
    look: {
      title: 'Look',
      subtitle: 'Artwork and Photography'
    },
    read: {
      title: 'Read',
      subtitle: 'Short Stories and Poems'
    },
    listen: {
      title: 'Listen',
      subtitle: 'Music and Spoken Word'
    },
    watch: {
      title: 'Watch',
      subtitle: 'Short Films and Videos'
    }
  };

  return map[category] || { title: 'Gallery', subtitle: 'Creative work' };
}

function isEmbeddableVideo(url) {
  return /youtube\.com|youtu\.be|vimeo\.com/i.test(String(url || ''));
}

function toEmbedUrl(url) {
  const value = String(url || '').trim();
  if (!value) return '';

  if (value.includes('youtube.com/watch?v=')) {
    const id = value.split('v=')[1]?.split('&')[0];
    return id ? `https://www.youtube.com/embed/${id}` : value;
  }

  if (value.includes('youtu.be/')) {
    const id = value.split('youtu.be/')[1]?.split('?')[0];
    return id ? `https://www.youtube.com/embed/${id}` : value;
  }

  if (value.includes('vimeo.com/')) {
    const id = value.split('vimeo.com/')[1]?.split('?')[0];
    return id ? `https://player.vimeo.com/video/${id}` : value;
  }

  return value;
}

module.exports = {
  normalizeImageUrls,
  categoryMeta,
  isEmbeddableVideo,
  toEmbedUrl
};
'''
files['src/routes/public.js'] = r'''
const express = require('express');
const ContentItem = require('../models/ContentItem');
const Issue = require('../models/Issue');
const Submission = require('../models/Submission');
const { getSetting } = require('../services/settings');
const { categoryMeta, isEmbeddableVideo, toEmbedUrl } = require('../utils/content');

const router = express.Router();

router.get('/', async (req, res, next) => {
  try {
    const [featuredIssues, featuredContent, aboutSnippet] = await Promise.all([
      Issue.find({ isFeatured: true }).sort({ order: 1, year: -1 }).lean(),
      ContentItem.find({ isPublished: true, isFeatured: true })
        .sort({ sortOrder: 1, createdAt: -1 })
        .limit(8)
        .lean(),
      getSetting('about', {
        title: 'About Ultraviolet',
        body: 'Ultraviolet is a student-run creative magazine celebrating prose, poetry, art, photography, music, and film.'
      })
    ]);

    res.render('pages/home', {
      title: 'Home',
      featuredIssues,
      featuredContent,
      aboutSnippet
    });
  } catch (error) {
    next(error);
  }
});

router.get('/about', async (req, res, next) => {
  try {
    const about = await getSetting('about', {
      title: 'About Ultraviolet',
      body: 'Ultraviolet is a creative magazine devoted to prose, poetry, art, photography, graphics, music, spoken word, and video.'
    });

    res.render('pages/about', {
      title: 'About',
      about
    });
  } catch (error) {
    next(error);
  }
});

router.get('/gallery', async (req, res) => {
  const cards = [
    {
      category: 'look',
      title: 'Look',
      subtitle: 'Artwork / Photography',
      description: 'Browse visual work in a responsive gallery grid.'
    },
    {
      category: 'read',
      title: 'Read',
      subtitle: 'Short Stories / Poems',
      description: 'Explore literary pieces with previews and full entries.'
    },
    {
      category: 'listen',
      title: 'Listen',
      subtitle: 'Music / Spoken Word',
      description: 'Play audio pieces directly in the browser.'
    },
    {
      category: 'watch',
      title: 'Watch',
      subtitle: 'Short Films / Videos',
      description: 'View films and video work with embedded playback.'
    }
  ];

  res.render('pages/gallery', {
    title: 'Gallery',
    cards
  });
});

router.get('/gallery/:category', async (req, res, next) => {
  try {
    const { category } = req.params;
    if (!['look', 'read', 'listen', 'watch'].includes(category)) {
      return res.status(404).render('pages/error', {
        title: 'Category Not Found',
        statusCode: 404,
        message: 'That gallery category does not exist.'
      });
    }

    const items = await ContentItem.find({ category, isPublished: true })
      .sort({ sortOrder: 1, createdAt: -1 })
      .lean();

    res.render('pages/category', {
      title: categoryMeta(category).title,
      category,
      meta: categoryMeta(category),
      items,
      isEmbeddableVideo,
      toEmbedUrl
    });
  } catch (error) {
    next(error);
  }
});

router.get('/content/:slug', async (req, res, next) => {
  try {
    const item = await ContentItem.findOne({ slug: req.params.slug, isPublished: true }).lean();

    if (!item) {
      return res.status(404).render('pages/error', {
        title: 'Content Not Found',
        statusCode: 404,
        message: 'The requested content item could not be found.'
      });
    }

    res.render('pages/content-detail', {
      title: item.title,
      item,
      meta: categoryMeta(item.category),
      isEmbeddableVideo,
      toEmbedUrl
    });
  } catch (error) {
    next(error);
  }
});

router.get('/issues', async (req, res, next) => {
  try {
    const issues = await Issue.find({}).sort({ year: -1 }).lean();
    res.render('pages/issues', { title: 'Issues', issues });
  } catch (error) {
    next(error);
  }
});

router.get('/submit', async (req, res, next) => {
  try {
    const site = await getSetting('site', {});
    if (site.submissionMode === 'external' && site.externalSubmissionUrl) {
      return res.redirect(site.externalSubmissionUrl);
    }

    res.render('pages/submit', { title: 'Submit' });
  } catch (error) {
    next(error);
  }
});

router.post('/submit', async (req, res, next) => {
  try {
    const payload = {
      name: String(req.body.name || '').trim(),
      email: String(req.body.email || '').trim().toLowerCase(),
      category: String(req.body.category || '').trim(),
      title: String(req.body.title || '').trim(),
      creatorName: String(req.body.creatorName || '').trim(),
      summary: String(req.body.summary || '').trim(),
      assetUrl: String(req.body.assetUrl || '').trim(),
      notes: String(req.body.notes || '').trim()
    };

    const missingRequired = !payload.name || !payload.email || !payload.category || !payload.title;
    if (missingRequired) {
      req.session.message = { type: 'error', text: 'Please complete all required submission fields.' };
      return res.redirect('/submit');
    }

    await Submission.create(payload);
    req.session.message = { type: 'success', text: 'Submission received. Thank you for sharing your work.' };
    return res.redirect('/submit');
  } catch (error) {
    next(error);
  }
});

module.exports = router;
'''
files['src/routes/admin.js'] = r'''
const express = require('express');
const bcrypt = require('bcryptjs');
const User = require('../models/User');
const ContentItem = require('../models/ContentItem');
const Issue = require('../models/Issue');
const SocialLink = require('../models/SocialLink');
const Submission = require('../models/Submission');
const { requireAdmin } = require('../middleware/auth');
const { getSetting, upsertSetting } = require('../services/settings');
const { slugify } = require('../utils/slugify');
const { normalizeImageUrls } = require('../utils/content');

const router = express.Router();

router.get('/login', (req, res) => {
  res.render('admin/login', { title: 'Admin Login' });
});

router.post('/login', async (req, res, next) => {
  try {
    const email = String(req.body.email || '').trim().toLowerCase();
    const password = String(req.body.password || '');

    const user = await User.findOne({ email });
    if (!user) {
      req.session.message = { type: 'error', text: 'Invalid email or password.' };
      return res.redirect('/admin/login');
    }

    const isValid = await bcrypt.compare(password, user.passwordHash);
    if (!isValid) {
      req.session.message = { type: 'error', text: 'Invalid email or password.' };
      return res.redirect('/admin/login');
    }

    req.session.userId = String(user._id);
    req.session.message = { type: 'success', text: 'You are now signed in.' };
    return res.redirect('/admin');
  } catch (error) {
    next(error);
  }
});

router.post('/logout', requireAdmin, (req, res) => {
  req.session.destroy(() => {
    res.redirect('/admin/login');
  });
});

router.get('/', requireAdmin, async (req, res, next) => {
  try {
    const [contentCount, issueCount, submissionCount, latestSubmissions] = await Promise.all([
      ContentItem.countDocuments(),
      Issue.countDocuments(),
      Submission.countDocuments(),
      Submission.find({}).sort({ createdAt: -1 }).limit(5).lean()
    ]);

    res.render('admin/dashboard', {
      title: 'Admin Dashboard',
      stats: { contentCount, issueCount, submissionCount },
      latestSubmissions
    });
  } catch (error) {
    next(error);
  }
});

router.get('/content', requireAdmin, async (req, res, next) => {
  try {
    const items = await ContentItem.find({}).sort({ category: 1, sortOrder: 1, createdAt: -1 }).lean();
    res.render('admin/content-list', { title: 'Manage Content', items });
  } catch (error) {
    next(error);
  }
});

router.get('/content/new', requireAdmin, (req, res) => {
  res.render('admin/content-form', {
    title: 'New Content',
    item: null,
    formAction: '/admin/content',
    methodOverride: null
  });
});

router.post('/content', requireAdmin, async (req, res, next) => {
  try {
    const title = String(req.body.title || '').trim();
    const slug = String(req.body.slug || '').trim() || slugify(title);

    await ContentItem.create({
      title,
      slug,
      category: req.body.category,
      subtype: String(req.body.subtype || '').trim(),
      creatorName: String(req.body.creatorName || '').trim(),
      summary: String(req.body.summary || '').trim(),
      body: String(req.body.body || '').trim(),
      issueYear: req.body.issueYear ? Number(req.body.issueYear) : undefined,
      coverImageUrl: String(req.body.coverImageUrl || '').trim(),
      imageUrls: normalizeImageUrls(req.body.imageUrls),
      audioUrl: String(req.body.audioUrl || '').trim(),
      videoUrl: String(req.body.videoUrl || '').trim(),
      externalUrl: String(req.body.externalUrl || '').trim(),
      durationLabel: String(req.body.durationLabel || '').trim(),
      isPublished: req.body.isPublished === 'on',
      isFeatured: req.body.isFeatured === 'on',
      sortOrder: Number(req.body.sortOrder || 0)
    });

    req.session.message = { type: 'success', text: 'Content item created.' };
    res.redirect('/admin/content');
  } catch (error) {
    next(error);
  }
});

router.get('/content/:id/edit', requireAdmin, async (req, res, next) => {
  try {
    const item = await ContentItem.findById(req.params.id).lean();
    if (!item) {
      req.session.message = { type: 'error', text: 'Content item not found.' };
      return res.redirect('/admin/content');
    }

    res.render('admin/content-form', {
      title: 'Edit Content',
      item,
      formAction: `/admin/content/${item._id}?_method=PUT`,
      methodOverride: 'PUT'
    });
  } catch (error) {
    next(error);
  }
});

router.put('/content/:id', requireAdmin, async (req, res, next) => {
  try {
    const title = String(req.body.title || '').trim();
    const slug = String(req.body.slug || '').trim() || slugify(title);

    await ContentItem.findByIdAndUpdate(req.params.id, {
      title,
      slug,
      category: req.body.category,
      subtype: String(req.body.subtype || '').trim(),
      creatorName: String(req.body.creatorName || '').trim(),
      summary: String(req.body.summary || '').trim(),
      body: String(req.body.body || '').trim(),
      issueYear: req.body.issueYear ? Number(req.body.issueYear) : undefined,
      coverImageUrl: String(req.body.coverImageUrl || '').trim(),
      imageUrls: normalizeImageUrls(req.body.imageUrls),
      audioUrl: String(req.body.audioUrl || '').trim(),
      videoUrl: String(req.body.videoUrl || '').trim(),
      externalUrl: String(req.body.externalUrl || '').trim(),
      durationLabel: String(req.body.durationLabel || '').trim(),
      isPublished: req.body.isPublished === 'on',
      isFeatured: req.body.isFeatured === 'on',
      sortOrder: Number(req.body.sortOrder || 0)
    });

    req.session.message = { type: 'success', text: 'Content item updated.' };
    res.redirect('/admin/content');
  } catch (error) {
    next(error);
  }
});

router.post('/content/:id/delete', requireAdmin, async (req, res, next) => {
  try {
    await ContentItem.findByIdAndDelete(req.params.id);
    req.session.message = { type: 'success', text: 'Content item deleted.' };
    res.redirect('/admin/content');
  } catch (error) {
    next(error);
  }
});

router.get('/issues', requireAdmin, async (req, res, next) => {
  try {
    const issues = await Issue.find({}).sort({ year: -1 }).lean();
    res.render('admin/issues-list', { title: 'Manage Issues', issues });
  } catch (error) {
    next(error);
  }
});

router.get('/issues/new', requireAdmin, (req, res) => {
  res.render('admin/issue-form', {
    title: 'New Issue',
    issue: null,
    formAction: '/admin/issues'
  });
});

router.post('/issues', requireAdmin, async (req, res, next) => {
  try {
    await Issue.create({
      year: Number(req.body.year),
      title: String(req.body.title || '').trim(),
      summary: String(req.body.summary || '').trim(),
      coverImageUrl: String(req.body.coverImageUrl || '').trim(),
      externalUrl: String(req.body.externalUrl || '').trim(),
      isFeatured: req.body.isFeatured === 'on',
      order: Number(req.body.order || 0)
    });
    req.session.message = { type: 'success', text: 'Issue created.' };
    res.redirect('/admin/issues');
  } catch (error) {
    next(error);
  }
});

router.get('/issues/:id/edit', requireAdmin, async (req, res, next) => {
  try {
    const issue = await Issue.findById(req.params.id).lean();
    if (!issue) {
      req.session.message = { type: 'error', text: 'Issue not found.' };
      return res.redirect('/admin/issues');
    }
    res.render('admin/issue-form', {
      title: 'Edit Issue',
      issue,
      formAction: `/admin/issues/${issue._id}?_method=PUT`
    });
  } catch (error) {
    next(error);
  }
});

router.put('/issues/:id', requireAdmin, async (req, res, next) => {
  try {
    await Issue.findByIdAndUpdate(req.params.id, {
      year: Number(req.body.year),
      title: String(req.body.title || '').trim(),
      summary: String(req.body.summary || '').trim(),
      coverImageUrl: String(req.body.coverImageUrl || '').trim(),
      externalUrl: String(req.body.externalUrl || '').trim(),
      isFeatured: req.body.isFeatured === 'on',
      order: Number(req.body.order || 0)
    });
    req.session.message = { type: 'success', text: 'Issue updated.' };
    res.redirect('/admin/issues');
  } catch (error) {
    next(error);
  }
});

router.post('/issues/:id/delete', requireAdmin, async (req, res, next) => {
  try {
    await Issue.findByIdAndDelete(req.params.id);
    req.session.message = { type: 'success', text: 'Issue deleted.' };
    res.redirect('/admin/issues');
  } catch (error) {
    next(error);
  }
});

router.get('/social-links', requireAdmin, async (req, res, next) => {
  try {
    const links = await SocialLink.find({}).sort({ order: 1 }).lean();
    res.render('admin/social-links', { title: 'Manage Social Links', links });
  } catch (error) {
    next(error);
  }
});

router.post('/social-links', requireAdmin, async (req, res, next) => {
  try {
    await SocialLink.create({
      label: String(req.body.label || '').trim(),
      icon: String(req.body.icon || '').trim() || 'link',
      url: String(req.body.url || '').trim(),
      order: Number(req.body.order || 0),
      isActive: req.body.isActive === 'on'
    });
    req.session.message = { type: 'success', text: 'Social link created.' };
    res.redirect('/admin/social-links');
  } catch (error) {
    next(error);
  }
});

router.post('/social-links/:id/delete', requireAdmin, async (req, res, next) => {
  try {
    await SocialLink.findByIdAndDelete(req.params.id);
    req.session.message = { type: 'success', text: 'Social link deleted.' };
    res.redirect('/admin/social-links');
  } catch (error) {
    next(error);
  }
});

router.get('/submissions', requireAdmin, async (req, res, next) => {
  try {
    const submissions = await Submission.find({}).sort({ createdAt: -1 }).lean();
    res.render('admin/submissions', { title: 'Submissions', submissions });
  } catch (error) {
    next(error);
  }
});

router.post('/submissions/:id/status', requireAdmin, async (req, res, next) => {
  try {
    await Submission.findByIdAndUpdate(req.params.id, {
      status: String(req.body.status || 'new')
    });
    req.session.message = { type: 'success', text: 'Submission status updated.' };
    res.redirect('/admin/submissions');
  } catch (error) {
    next(error);
  }
});

router.get('/settings', requireAdmin, async (req, res, next) => {
  try {
    const [about, site] = await Promise.all([
      getSetting('about', {
        title: 'About Ultraviolet',
        body: ''
      }),
      getSetting('site', {
        heroTitle: 'Ultraviolet Magazine',
        heroTagline: 'Get creative. Explore boundaries.',
        submissionMode: 'internal',
        externalSubmissionUrl: '',
        footerText: 'Ultraviolet Magazine — Queen’s University, Kingston ON'
      })
    ]);

    res.render('admin/settings', {
      title: 'Settings',
      about,
      site
    });
  } catch (error) {
    next(error);
  }
});

router.post('/settings/about', requireAdmin, async (req, res, next) => {
  try {
    await upsertSetting('about', {
      title: String(req.body.title || '').trim(),
      body: String(req.body.body || '').trim(),
      imageUrl: String(req.body.imageUrl || '').trim()
    });
    req.session.message = { type: 'success', text: 'About page updated.' };
    res.redirect('/admin/settings');
  } catch (error) {
    next(error);
  }
});

router.post('/settings/site', requireAdmin, async (req, res, next) => {
  try {
    await upsertSetting('site', {
      heroTitle: String(req.body.heroTitle || '').trim(),
      heroTagline: String(req.body.heroTagline || '').trim(),
      submissionMode: String(req.body.submissionMode || 'internal').trim(),
      externalSubmissionUrl: String(req.body.externalSubmissionUrl || '').trim(),
      footerText: String(req.body.footerText || '').trim()
    });
    req.session.message = { type: 'success', text: 'Site settings updated.' };
    res.redirect('/admin/settings');
  } catch (error) {
    next(error);
  }
});

module.exports = router;
'''
files['src/routes/api.js'] = r'''
const express = require('express');
const ContentItem = require('../models/ContentItem');
const Issue = require('../models/Issue');
const SocialLink = require('../models/SocialLink');

const router = express.Router();

router.get('/health', (req, res) => {
  res.json({ ok: true });
});

router.get('/content', async (req, res, next) => {
  try {
    const filter = { isPublished: true };
    if (req.query.category) {
      filter.category = String(req.query.category);
    }

    const items = await ContentItem.find(filter)
      .sort({ sortOrder: 1, createdAt: -1 })
      .lean();

    res.json(items);
  } catch (error) {
    next(error);
  }
});

router.get('/issues', async (req, res, next) => {
  try {
    const issues = await Issue.find({}).sort({ year: -1 }).lean();
    res.json(issues);
  } catch (error) {
    next(error);
  }
});

router.get('/social-links', async (req, res, next) => {
  try {
    const links = await SocialLink.find({ isActive: true }).sort({ order: 1 }).lean();
    res.json(links);
  } catch (error) {
    next(error);
  }
});

module.exports = router;
'''
files['src/seed.js'] = r'''
require('dotenv').config();
const bcrypt = require('bcryptjs');
const { connectToDatabase } = require('./config/db');
const User = require('./models/User');
const Issue = require('./models/Issue');
const SocialLink = require('./models/SocialLink');
const ContentItem = require('./models/ContentItem');
const Submission = require('./models/Submission');
const PageSetting = require('./models/PageSetting');

async function seed() {
  await connectToDatabase();

  await Promise.all([
    User.deleteMany({}),
    Issue.deleteMany({}),
    SocialLink.deleteMany({}),
    ContentItem.deleteMany({}),
    Submission.deleteMany({}),
    PageSetting.deleteMany({})
  ]);

  const email = (process.env.ADMIN_EMAIL || 'admin@example.com').trim().toLowerCase();
  const password = process.env.ADMIN_PASSWORD || 'change-this-admin-password';
  const passwordHash = await bcrypt.hash(password, 10);

  await User.create({ email, passwordHash, role: 'admin' });

  await PageSetting.insertMany([
    {
      key: 'site',
      value: {
        heroTitle: 'Ultraviolet Magazine',
        heroTagline: 'Get creative. Explore boundaries.',
        submissionMode: 'internal',
        externalSubmissionUrl: '',
        footerText: 'Ultraviolet Magazine — Queen’s University, Kingston ON'
      }
    },
    {
      key: 'about',
      value: {
        title: 'About Ultraviolet',
        body: 'Ultraviolet is a student-run creative magazine devoted to prose, poetry, art, photography, graphics, music, spoken word, and moving image. We promote creative work on and off campus and make room for experimentation across media.',
        imageUrl: 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=900&q=80'
      }
    }
  ]);

  await SocialLink.insertMany([
    { label: 'Instagram', icon: 'instagram', url: 'https://instagram.com', order: 1, isActive: true },
    { label: 'Facebook', icon: 'facebook', url: 'https://facebook.com', order: 2, isActive: true },
    { label: 'Email', icon: 'mail', url: 'mailto:hello@example.com', order: 3, isActive: true }
  ]);

  await Issue.insertMany([
    {
      year: 2025,
      title: 'Ultraviolet 2025',
      summary: 'A new issue featuring visual art, poetry, sound, and moving image.',
      coverImageUrl: 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80',
      externalUrl: 'https://issuu.com',
      isFeatured: true,
      order: 1
    },
    {
      year: 2024,
      title: 'Ultraviolet 2024',
      summary: 'A previous issue archive entry.',
      coverImageUrl: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=800&q=80',
      externalUrl: 'https://issuu.com',
      isFeatured: true,
      order: 2
    },
    {
      year: 2023,
      title: 'Ultraviolet 2023',
      summary: 'Archive issue with student work across media.',
      coverImageUrl: 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80',
      externalUrl: 'https://issuu.com',
      isFeatured: true,
      order: 3
    }
  ]);

  await ContentItem.insertMany([
    {
      title: 'Lavender Windows',
      slug: 'lavender-windows',
      category: 'look',
      subtype: 'photography',
      creatorName: 'Maya Chen',
      summary: 'A photographic series on reflection, shadow, and evening color.',
      coverImageUrl: 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80',
      imageUrls: [
        'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80',
        'https://images.unsplash.com/photo-1493246318656-5bfd4cfb29b8?auto=format&fit=crop&w=1200&q=80'
      ],
      issueYear: 2025,
      isPublished: true,
      isFeatured: true,
      sortOrder: 1
    },
    {
      title: 'After the Rain',
      slug: 'after-the-rain',
      category: 'read',
      subtype: 'poem',
      creatorName: 'Leah Morgan',
      summary: 'A poem about wet streets, memory, and return.',
      body: 'The rain has ended but the city still remembers. Pavement holds the sky in fragments, and every step feels like walking through a delayed reflection. This sample text stands in for a full poem or short prose piece.',
      coverImageUrl: 'https://images.unsplash.com/photo-1511497584788-876760111969?auto=format&fit=crop&w=1000&q=80',
      issueYear: 2025,
      isPublished: true,
      isFeatured: true,
      sortOrder: 2
    },
    {
      title: 'Station Voice',
      slug: 'station-voice',
      category: 'listen',
      subtype: 'spoken-word',
      creatorName: 'Jordan Patel',
      summary: 'A spoken word piece on transit, waiting, and city rhythm.',
      audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
      durationLabel: '3:42',
      coverImageUrl: 'https://images.unsplash.com/photo-1487180144351-b8472da7d491?auto=format&fit=crop&w=1000&q=80',
      issueYear: 2025,
      isPublished: true,
      isFeatured: true,
      sortOrder: 3
    },
    {
      title: 'Quiet Neon',
      slug: 'quiet-neon',
      category: 'watch',
      subtype: 'short-film',
      creatorName: 'Aria Williams',
      summary: 'A short film about color, motion, and nighttime solitude.',
      videoUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      coverImageUrl: 'https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?auto=format&fit=crop&w=1000&q=80',
      issueYear: 2025,
      isPublished: true,
      isFeatured: true,
      sortOrder: 4
    },
    {
      title: 'Glass Study No. 2',
      slug: 'glass-study-no-2',
      category: 'look',
      subtype: 'artwork',
      creatorName: 'Nina Alvarez',
      summary: 'Mixed-media digital artwork with translucent layers and soft geometry.',
      coverImageUrl: 'https://images.unsplash.com/photo-1515405295579-ba7b45403062?auto=format&fit=crop&w=1000&q=80',
      imageUrls: ['https://images.unsplash.com/photo-1515405295579-ba7b45403062?auto=format&fit=crop&w=1000&q=80'],
      issueYear: 2024,
      isPublished: true,
      sortOrder: 5
    },
    {
      title: 'North Hall, 2 A.M.',
      slug: 'north-hall-2-am',
      category: 'read',
      subtype: 'short-story',
      creatorName: 'Evan Brooks',
      summary: 'A short story about campus quiet, fluorescent light, and unplanned conversation.',
      body: 'At two in the morning, the residence hallway stopped pretending to be temporary. Doors looked permanent. The vending machine sounded like weather. Then someone at the far end laughed, and the place became human again.',
      coverImageUrl: 'https://images.unsplash.com/photo-1519074069444-1ba4fff66d16?auto=format&fit=crop&w=1000&q=80',
      issueYear: 2024,
      isPublished: true,
      sortOrder: 6
    }
  ]);

  await Submission.insertMany([
    {
      name: 'Sample Submitter',
      email: 'submitter@example.com',
      category: 'read',
      title: 'Draft Piece',
      creatorName: 'Sample Submitter',
      summary: 'Example submission waiting for review.',
      assetUrl: 'https://example.com/draft-piece',
      notes: 'Please consider this for the next issue.',
      status: 'new'
    }
  ]);

  console.log('Database seeded successfully');
  process.exit(0);
}

seed().catch((error) => {
  console.error(error);
  process.exit(1);
});
'''
files['src/views/partials/head.ejs'] = r'''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title><%= title %> | <%= siteSettings.heroTitle || 'Ultraviolet Magazine' %></title>
    <link rel="stylesheet" href="/styles.css" />
    <script defer src="/app.js"></script>
  </head>
  <body>
'''
files['src/views/partials/header.ejs'] = r'''
<header class="site-header">
  <div class="container nav-wrap">
    <a href="/" class="logo-link">UV Magazine</a>
    <nav class="main-nav" aria-label="Primary navigation">
      <a class="<%= currentPath === '/about' ? 'active' : '' %>" href="/about">About</a>
      <a class="<%= currentPath.startsWith('/gallery') ? 'active' : '' %>" href="/gallery">Gallery</a>
      <a class="<%= currentPath.startsWith('/issues') ? 'active' : '' %>" href="/issues">Issues</a>
      <a class="<%= currentPath === '/submit' ? 'active' : '' %>" href="/submit">Submit</a>
      <% if (isAdminAuthenticated) { %>
        <a class="<%= currentPath.startsWith('/admin') ? 'active' : '' %>" href="/admin">Admin</a>
      <% } else { %>
        <a href="/admin/login">Admin</a>
      <% } %>
    </nav>
  </div>
</header>
<% if (message) { %>
  <div class="container flash-row">
    <div class="flash flash-<%= message.type %>"><%= message.text %></div>
  </div>
<% } %>
'''
files['src/views/partials/footer.ejs'] = r'''
<footer class="site-footer">
  <div class="container footer-content">
    <div>
      <strong><%= siteSettings.heroTitle || 'Ultraviolet Magazine' %></strong>
      <p><%= siteSettings.footerText || 'Ultraviolet Magazine — Queen’s University, Kingston ON' %></p>
    </div>
    <div class="social-links" aria-label="Social links">
      <% socialLinks.forEach((link) => { %>
        <a href="<%= link.url %>" target="_blank" rel="noreferrer"><%= link.label %></a>
      <% }) %>
    </div>
  </div>
</footer>
</body>
</html>
'''
files['src/views/pages/home.ejs'] = r'''
<%- include('../partials/head') %>
<%- include('../partials/header') %>
<main>
  <section class="hero-section">
    <div class="container hero-grid">
      <div>
        <p class="eyebrow">Student magazine</p>
        <h1><%= siteSettings.heroTitle || 'Ultraviolet Magazine' %></h1>
        <p class="lead"><%= siteSettings.heroTagline || 'Get creative. Explore boundaries.' %></p>
        <div class="button-row">
          <a class="button" href="/gallery">Enter the gallery</a>
          <a class="button button-secondary" href="/submit">Submit your work</a>
        </div>
      </div>
      <div class="hero-card">
        <h2><%= aboutSnippet.title %></h2>
        <p><%= aboutSnippet.body %></p>
        <a href="/about" class="text-link">Read more</a>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="section-heading">
        <h2>Featured issues</h2>
        <a href="/issues" class="text-link">View all issues</a>
      </div>
      <div class="card-grid issues-grid">
        <% featuredIssues.forEach((issue) => { %>
          <article class="card issue-card">
            <img src="<%= issue.coverImageUrl || 'https://placehold.co/600x800?text=Issue' %>" alt="<%= issue.title %> cover" />
            <div class="card-body">
              <p class="issue-year"><%= issue.year %></p>
              <h3><%= issue.title %></h3>
              <p><%= issue.summary %></p>
              <% if (issue.externalUrl) { %>
                <a class="text-link" href="<%= issue.externalUrl %>" target="_blank" rel="noreferrer">Open issue</a>
              <% } %>
            </div>
          </article>
        <% }) %>
      </div>
    </div>
  </section>

  <section class="section section-muted">
    <div class="container">
      <div class="section-heading">
        <h2>Featured work</h2>
        <a href="/gallery" class="text-link">Browse gallery</a>
      </div>
      <div class="card-grid featured-grid">
        <% featuredContent.forEach((item) => { %>
          <article class="card content-card">
            <img src="<%= item.coverImageUrl || 'https://placehold.co/600x400?text=Featured+Work' %>" alt="<%= item.title %>" />
            <div class="card-body">
              <span class="pill"><%= item.category %></span>
              <h3><%= item.title %></h3>
              <p>By <%= item.creatorName %></p>
              <p><%= item.summary %></p>
              <a class="text-link" href="/content/<%= item.slug %>">View piece</a>
            </div>
          </article>
        <% }) %>
      </div>
    </div>
  </section>
</main>
<%- include('../partials/footer') %>
'''
files['src/views/pages/about.ejs'] = r'''
<%- include('../partials/head') %>
<%- include('../partials/header') %>
<main class="section">
  <div class="container split-layout">
    <div>
      <p class="eyebrow">About</p>
      <h1><%= about.title %></h1>
      <div class="prose">
        <% about.body.split('\n').forEach((paragraph) => { %>
          <% if (paragraph.trim()) { %>
            <p><%= paragraph %></p>
          <% } %>
        <% }) %>
      </div>
    </div>
    <div>
      <img class="feature-image" src="<%= about.imageUrl || 'https://placehold.co/700x900?text=About+UV' %>" alt="About Ultraviolet" />
    </div>
  </div>
</main>
<%- include('../partials/footer') %>
'''
files['src/views/pages/gallery.ejs'] = r'''
<%- include('../partials/head') %>
<%- include('../partials/header') %>
<main class="section">
  <div class="container">
    <p class="eyebrow">Gallery</p>
    <h1>Choose a category</h1>
    <p class="lead">Explore the four creative sections requested in the project brief: LOOK, READ, LISTEN, and WATCH.</p>
    <div class="gallery-grid">
      <% cards.forEach((card) => { %>
        <a class="gallery-entry entry-<%= card.category %>" href="/gallery/<%= card.category %>">
          <div>
            <p class="entry-index"><%= card.title[0] %></p>
            <h2><%= card.title %></h2>
            <p class="entry-subtitle"><%= card.subtitle %></p>
            <p><%= card.description %></p>
          </div>
          <span class="text-link">Open</span>
        </a>
      <% }) %>
    </div>
  </div>
</main>
<%- include('../partials/footer') %>
'''
files['src/views/pages/category.ejs'] = r'''
<%- include('../partials/head') %>
<%- include('../partials/header') %>
<main class="section">
  <div class="container">
    <p class="eyebrow"><%= meta.title %></p>
    <h1><%= meta.subtitle %></h1>

    <% if (category === 'look') { %>
      <div class="masonry-grid">
        <% items.forEach((item) => { %>
          <a class="masonry-item" href="/content/<%= item.slug %>">
            <img src="<%= item.coverImageUrl || 'https://placehold.co/700x700?text=Artwork' %>" alt="<%= item.title %>" />
            <div class="overlay">
              <h3><%= item.title %></h3>
              <p><%= item.creatorName %></p>
            </div>
          </a>
        <% }) %>
      </div>
    <% } %>

    <% if (category === 'read') { %>
      <div class="card-grid">
        <% items.forEach((item) => { %>
          <article class="card read-card">
            <div class="card-body">
              <span class="pill"><%= item.subtype || 'piece' %></span>
              <h3><%= item.title %></h3>
              <p>By <%= item.creatorName %></p>
              <p><%= item.summary %></p>
              <a class="text-link" href="/content/<%= item.slug %>">Read more</a>
            </div>
          </article>
        <% }) %>
      </div>
    <% } %>

    <% if (category === 'listen') { %>
      <div class="stack-list">
        <% items.forEach((item) => { %>
          <article class="audio-card">
            <div>
              <h3><%= item.title %></h3>
              <p>By <%= item.creatorName %></p>
              <p><%= item.summary %></p>
            </div>
            <audio controls preload="none" src="<%= item.audioUrl %>"></audio>
            <% if (item.durationLabel) { %>
              <p class="muted">Runtime: <%= item.durationLabel %></p>
            <% } %>
            <a class="text-link" href="/content/<%= item.slug %>">Details</a>
          </article>
        <% }) %>
      </div>
    <% } %>

    <% if (category === 'watch') { %>
      <div class="stack-list video-list">
        <% items.forEach((item) => { %>
          <article class="video-card">
            <div>
              <h3><%= item.title %></h3>
              <p>By <%= item.creatorName %></p>
              <p><%= item.summary %></p>
            </div>
            <% if (isEmbeddableVideo(item.videoUrl)) { %>
              <iframe src="<%= toEmbedUrl(item.videoUrl) %>" title="<%= item.title %> video" allowfullscreen loading="lazy"></iframe>
            <% } else if (item.videoUrl) { %>
              <video controls preload="metadata" src="<%= item.videoUrl %>"></video>
            <% } %>
            <a class="text-link" href="/content/<%= item.slug %>">Details</a>
          </article>
        <% }) %>
      </div>
    <% } %>

    <% if (!items.length) { %>
      <div class="empty-state">
        <p>No published items are available yet for this category.</p>
      </div>
    <% } %>
  </div>
</main>
<%- include('../partials/footer') %>
'''
files['src/views/pages/content-detail.ejs'] = r'''
<%- include('../partials/head') %>
<%- include('../partials/header') %>
<main class="section">
  <div class="container detail-layout">
    <div>
      <p class="eyebrow"><%= meta.title %></p>
      <h1><%= item.title %></h1>
      <p class="lead">By <%= item.creatorName %></p>
      <% if (item.summary) { %>
        <p><%= item.summary %></p>
      <% } %>
      <% if (item.issueYear) { %>
        <p class="muted">Issue year: <%= item.issueYear %></p>
      <% } %>
      <% if (item.category === 'read' && item.body) { %>
        <div class="prose">
          <% item.body.split('\n').forEach((paragraph) => { %>
            <% if (paragraph.trim()) { %>
              <p><%= paragraph %></p>
            <% } %>
          <% }) %>
        </div>
      <% } %>
      <% if (item.category === 'listen' && item.audioUrl) { %>
        <audio controls preload="metadata" src="<%= item.audioUrl %>"></audio>
      <% } %>
      <% if (item.category === 'watch' && item.videoUrl) { %>
        <% if (isEmbeddableVideo(item.videoUrl)) { %>
          <iframe class="detail-video" src="<%= toEmbedUrl(item.videoUrl) %>" title="<%= item.title %> video" allowfullscreen loading="lazy"></iframe>
        <% } else { %>
          <video class="detail-video" controls preload="metadata" src="<%= item.videoUrl %>"></video>
        <% } %>
      <% } %>
      <% if (item.externalUrl) { %>
        <p><a class="text-link" href="<%= item.externalUrl %>" target="_blank" rel="noreferrer">Open external link</a></p>
      <% } %>
    </div>

    <div>
      <% if (item.category === 'look' && item.imageUrls && item.imageUrls.length) { %>
        <div class="image-stack">
          <% item.imageUrls.forEach((url) => { %>
            <img class="feature-image" src="<%= url %>" alt="<%= item.title %>" />
          <% }) %>
        </div>
      <% } else { %>
        <img class="feature-image" src="<%= item.coverImageUrl || 'https://placehold.co/800x1000?text=UV+Magazine' %>" alt="<%= item.title %>" />
      <% } %>
    </div>
  </div>
</main>
<%- include('../partials/footer') %>
'''
files['src/views/pages/issues.ejs'] = r'''
<%- include('../partials/head') %>
<%- include('../partials/header') %>
<main class="section">
  <div class="container">
    <p class="eyebrow">Issues</p>
    <h1>Magazine archive</h1>
    <div class="card-grid issues-grid">
      <% issues.forEach((issue) => { %>
        <article class="card issue-card">
          <img src="<%= issue.coverImageUrl || 'https://placehold.co/600x800?text=Issue' %>" alt="<%= issue.title %>" />
          <div class="card-body">
            <p class="issue-year"><%= issue.year %></p>
            <h2><%= issue.title %></h2>
            <p><%= issue.summary %></p>
            <% if (issue.externalUrl) { %>
              <a class="text-link" href="<%= issue.externalUrl %>" target="_blank" rel="noreferrer">Open issue</a>
            <% } %>
          </div>
        </article>
      <% }) %>
    </div>
  </div>
</main>
<%- include('../partials/footer') %>
'''
files['src/views/pages/submit.ejs'] = r'''
<%- include('../partials/head') %>
<%- include('../partials/header') %>
<main class="section">
  <div class="container form-container">
    <div>
      <p class="eyebrow">Submit</p>
      <h1>Share your work</h1>
      <p>Use this internal submission form to send artwork, writing, audio, or video for review.</p>
    </div>
    <form class="site-form" action="/submit" method="POST">
      <label>
        Your name *
        <input type="text" name="name" required />
      </label>
      <label>
        Email *
        <input type="email" name="email" required />
      </label>
      <label>
        Category *
        <select name="category" required>
          <option value="">Select a category</option>
          <option value="look">Look</option>
          <option value="read">Read</option>
          <option value="listen">Listen</option>
          <option value="watch">Watch</option>
        </select>
      </label>
      <label>
        Title *
        <input type="text" name="title" required />
      </label>
      <label>
        Creator name
        <input type="text" name="creatorName" />
      </label>
      <label>
        Short summary
        <textarea name="summary" rows="4"></textarea>
      </label>
      <label>
        Asset URL
        <input type="url" name="assetUrl" placeholder="https://..." />
      </label>
      <label>
        Notes
        <textarea name="notes" rows="5"></textarea>
      </label>
      <button class="button" type="submit">Submit</button>
    </form>
  </div>
</main>
<%- include('../partials/footer') %>
'''
files['src/views/pages/error.ejs'] = r'''
<%- include('../partials/head') %>
<%- include('../partials/header') %>
<main class="section">
  <div class="container narrow">
    <p class="eyebrow">Error</p>
    <h1><%= statusCode %></h1>
    <p><%= message %></p>
    <a class="button" href="/">Go home</a>
  </div>
</main>
<%- include('../partials/footer') %>
'''
files['src/views/admin/login.ejs'] = r'''
<%- include('../partials/head') %>
<%- include('../partials/header') %>
<main class="section">
  <div class="container narrow">
    <p class="eyebrow">Admin</p>
    <h1>Sign in</h1>
    <form class="site-form" action="/admin/login" method="POST">
      <label>
        Email
        <input type="email" name="email" required />
      </label>
      <label>
        Password
        <input type="password" name="password" required />
      </label>
      <button class="button" type="submit">Sign in</button>
    </form>
  </div>
</main>
<%- include('../partials/footer') %>
'''
files['src/views/admin/dashboard.ejs'] = r'''
<%- include('../partials/head') %>
<%- include('../partials/header') %>
<main class="section">
  <div class="container">
    <div class="admin-toolbar">
      <div>
        <p class="eyebrow">Admin</p>
        <h1>Dashboard</h1>
      </div>
      <form action="/admin/logout" method="POST">
        <button class="button button-secondary" type="submit">Log out</button>
      </form>
    </div>

    <div class="stats-grid">
      <article class="stat-card">
        <h2><%= stats.contentCount %></h2>
        <p>Content items</p>
      </article>
      <article class="stat-card">
        <h2><%= stats.issueCount %></h2>
        <p>Issues</p>
      </article>
      <article class="stat-card">
        <h2><%= stats.submissionCount %></h2>
        <p>Submissions</p>
      </article>
    </div>

    <div class="admin-nav-links">
      <a href="/admin/content">Manage content</a>
      <a href="/admin/issues">Manage issues</a>
      <a href="/admin/social-links">Manage social links</a>
      <a href="/admin/submissions">Review submissions</a>
      <a href="/admin/settings">Settings</a>
    </div>

    <section class="section-inner">
      <h2>Latest submissions</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Category</th>
              <th>Sender</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <% latestSubmissions.forEach((submission) => { %>
              <tr>
                <td><%= submission.title %></td>
                <td><%= submission.category %></td>
                <td><%= submission.name %></td>
                <td><%= submission.status %></td>
              </tr>
            <% }) %>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</main>
<%- include('../partials/footer') %>
'''
files['src/views/admin/content-list.ejs'] = r'''
<%- include('../partials/head') %>
<%- include('../partials/header') %>
<main class="section">
  <div class="container">
    <div class="admin-toolbar">
      <div>
        <p class="eyebrow">Admin</p>
        <h1>Content</h1>
      </div>
      <a class="button" href="/admin/content/new">New content</a>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>Category</th>
            <th>Creator</th>
            <th>Published</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <% items.forEach((item) => { %>
            <tr>
              <td><%= item.title %></td>
              <td><%= item.category %></td>
              <td><%= item.creatorName %></td>
              <td><%= item.isPublished ? 'Yes' : 'No' %></td>
              <td>
                <div class="row-actions">
                  <a href="/admin/content/<%= item._id %>/edit">Edit</a>
                  <form action="/admin/content/<%= item._id %>/delete" method="POST" onsubmit="return confirm('Delete this content item?');">
                    <button type="submit">Delete</button>
                  </form>
                </div>
              </td>
            </tr>
          <% }) %>
        </tbody>
      </table>
    </div>
  </div>
</main>
<%- include('../partials/footer') %>
'''
files['src/views/admin/content-form.ejs'] = r'''
<%- include('../partials/head') %>
<%- include('../partials/header') %>
<main class="section">
  <div class="container form-container">
    <div>
      <p class="eyebrow">Admin</p>
      <h1><%= item ? 'Edit content' : 'Create content' %></h1>
    </div>
    <form class="site-form" action="<%= formAction %>" method="POST">
      <label>Title <input type="text" name="title" value="<%= item?.title || '' %>" required /></label>
      <label>Slug <input type="text" name="slug" value="<%= item?.slug || '' %>" /></label>
      <label>
        Category
        <select name="category" required>
          <% ['look','read','listen','watch'].forEach((option) => { %>
            <option value="<%= option %>" <%= item?.category === option ? 'selected' : '' %>><%= option %></option>
          <% }) %>
        </select>
      </label>
      <label>Subtype <input type="text" name="subtype" value="<%= item?.subtype || '' %>" /></label>
      <label>Creator name <input type="text" name="creatorName" value="<%= item?.creatorName || '' %>" required /></label>
      <label>Summary <textarea name="summary" rows="4"><%= item?.summary || '' %></textarea></label>
      <label>Body <textarea name="body" rows="8"><%= item?.body || '' %></textarea></label>
      <label>Issue year <input type="number" name="issueYear" value="<%= item?.issueYear || '' %>" /></label>
      <label>Cover image URL <input type="url" name="coverImageUrl" value="<%= item?.coverImageUrl || '' %>" /></label>
      <label>Image URLs, one per line <textarea name="imageUrls" rows="5"><%= item?.imageUrls?.join('\n') || '' %></textarea></label>
      <label>Audio URL <input type="url" name="audioUrl" value="<%= item?.audioUrl || '' %>" /></label>
      <label>Video URL <input type="url" name="videoUrl" value="<%= item?.videoUrl || '' %>" /></label>
      <label>External URL <input type="url" name="externalUrl" value="<%= item?.externalUrl || '' %>" /></label>
      <label>Duration label <input type="text" name="durationLabel" value="<%= item?.durationLabel || '' %>" /></label>
      <label>Sort order <input type="number" name="sortOrder" value="<%= item?.sortOrder || 0 %>" /></label>
      <label class="checkbox-row"><input type="checkbox" name="isPublished" <%= item?.isPublished !== false ? 'checked' : '' %> /> Published</label>
      <label class="checkbox-row"><input type="checkbox" name="isFeatured" <%= item?.isFeatured ? 'checked' : '' %> /> Featured</label>
      <div class="button-row">
        <button class="button" type="submit">Save</button>
        <a class="button button-secondary" href="/admin/content">Cancel</a>
      </div>
    </form>
  </div>
</main>
<%- include('../partials/footer') %>
'''
files['src/views/admin/issues-list.ejs'] = r'''
<%- include('../partials/head') %>
<%- include('../partials/header') %>
<main class="section">
  <div class="container">
    <div class="admin-toolbar">
      <div>
        <p class="eyebrow">Admin</p>
        <h1>Issues</h1>
      </div>
      <a class="button" href="/admin/issues/new">New issue</a>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Year</th>
            <th>Title</th>
            <th>Featured</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <% issues.forEach((issue) => { %>
            <tr>
              <td><%= issue.year %></td>
              <td><%= issue.title %></td>
              <td><%= issue.isFeatured ? 'Yes' : 'No' %></td>
              <td>
                <div class="row-actions">
                  <a href="/admin/issues/<%= issue._id %>/edit">Edit</a>
                  <form action="/admin/issues/<%= issue._id %>/delete" method="POST" onsubmit="return confirm('Delete this issue?');">
                    <button type="submit">Delete</button>
                  </form>
                </div>
              </td>
            </tr>
          <% }) %>
        </tbody>
      </table>
    </div>
  </div>
</main>
<%- include('../partials/footer') %>
'''
files['src/views/admin/issue-form.ejs'] = r'''
<%- include('../partials/head') %>
<%- include('../partials/header') %>
<main class="section">
  <div class="container form-container">
    <div>
      <p class="eyebrow">Admin</p>
      <h1><%= issue ? 'Edit issue' : 'Create issue' %></h1>
    </div>
    <form class="site-form" action="<%= formAction %>" method="POST">
      <label>Year <input type="number" name="year" value="<%= issue?.year || '' %>" required /></label>
      <label>Title <input type="text" name="title" value="<%= issue?.title || '' %>" required /></label>
      <label>Summary <textarea name="summary" rows="4"><%= issue?.summary || '' %></textarea></label>
      <label>Cover image URL <input type="url" name="coverImageUrl" value="<%= issue?.coverImageUrl || '' %>" /></label>
      <label>External issue URL <input type="url" name="externalUrl" value="<%= issue?.externalUrl || '' %>" /></label>
      <label>Order <input type="number" name="order" value="<%= issue?.order || 0 %>" /></label>
      <label class="checkbox-row"><input type="checkbox" name="isFeatured" <%= issue?.isFeatured !== false ? 'checked' : '' %> /> Featured</label>
      <div class="button-row">
        <button class="button" type="submit">Save</button>
        <a class="button button-secondary" href="/admin/issues">Cancel</a>
      </div>
    </form>
  </div>
</main>
<%- include('../partials/footer') %>
'''
files['src/views/admin/social-links.ejs'] = r'''
<%- include('../partials/head') %>
<%- include('../partials/header') %>
<main class="section">
  <div class="container form-container">
    <div>
      <p class="eyebrow">Admin</p>
      <h1>Social links</h1>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Label</th>
              <th>URL</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <% links.forEach((link) => { %>
              <tr>
                <td><%= link.label %></td>
                <td><%= link.url %></td>
                <td>
                  <form action="/admin/social-links/<%= link._id %>/delete" method="POST" onsubmit="return confirm('Delete this social link?');">
                    <button type="submit">Delete</button>
                  </form>
                </td>
              </tr>
            <% }) %>
          </tbody>
        </table>
      </div>
    </div>
    <form class="site-form" action="/admin/social-links" method="POST">
      <label>Label <input type="text" name="label" required /></label>
      <label>Icon name <input type="text" name="icon" placeholder="instagram" /></label>
      <label>URL <input type="url" name="url" required /></label>
      <label>Order <input type="number" name="order" value="0" /></label>
      <label class="checkbox-row"><input type="checkbox" name="isActive" checked /> Active</label>
      <button class="button" type="submit">Add link</button>
    </form>
  </div>
</main>
<%- include('../partials/footer') %>
'''
files['src/views/admin/submissions.ejs'] = r'''
<%- include('../partials/head') %>
<%- include('../partials/header') %>
<main class="section">
  <div class="container">
    <p class="eyebrow">Admin</p>
    <h1>Submissions</h1>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Title</th>
            <th>Sender</th>
            <th>Category</th>
            <th>Asset</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <% submissions.forEach((submission) => { %>
            <tr>
              <td><%= new Date(submission.createdAt).toLocaleDateString() %></td>
              <td><%= submission.title %></td>
              <td>
                <strong><%= submission.name %></strong><br />
                <span><%= submission.email %></span>
              </td>
              <td><%= submission.category %></td>
              <td>
                <% if (submission.assetUrl) { %>
                  <a href="<%= submission.assetUrl %>" target="_blank" rel="noreferrer">Open</a>
                <% } %>
              </td>
              <td>
                <form action="/admin/submissions/<%= submission._id %>/status" method="POST">
                  <select name="status" onchange="this.form.submit()">
                    <% ['new','reviewed','accepted','rejected'].forEach((option) => { %>
                      <option value="<%= option %>" <%= submission.status === option ? 'selected' : '' %>><%= option %></option>
                    <% }) %>
                  </select>
                </form>
              </td>
            </tr>
          <% }) %>
        </tbody>
      </table>
    </div>
  </div>
</main>
<%- include('../partials/footer') %>
'''
files['src/views/admin/settings.ejs'] = r'''
<%- include('../partials/head') %>
<%- include('../partials/header') %>
<main class="section">
  <div class="container settings-grid">
    <form class="site-form" action="/admin/settings/site" method="POST">
      <p class="eyebrow">Admin</p>
      <h1>Site settings</h1>
      <label>Hero title <input type="text" name="heroTitle" value="<%= site.heroTitle || '' %>" required /></label>
      <label>Hero tagline <input type="text" name="heroTagline" value="<%= site.heroTagline || '' %>" required /></label>
      <label>
        Submission mode
        <select name="submissionMode">
          <option value="internal" <%= site.submissionMode === 'internal' ? 'selected' : '' %>>Internal form</option>
          <option value="external" <%= site.submissionMode === 'external' ? 'selected' : '' %>>External URL</option>
        </select>
      </label>
      <label>External submission URL <input type="url" name="externalSubmissionUrl" value="<%= site.externalSubmissionUrl || '' %>" /></label>
      <label>Footer text <input type="text" name="footerText" value="<%= site.footerText || '' %>" /></label>
      <button class="button" type="submit">Save site settings</button>
    </form>

    <form class="site-form" action="/admin/settings/about" method="POST">
      <p class="eyebrow">Admin</p>
      <h1>About page</h1>
      <label>Title <input type="text" name="title" value="<%= about.title || '' %>" required /></label>
      <label>Body <textarea name="body" rows="12"><%= about.body || '' %></textarea></label>
      <label>Image URL <input type="url" name="imageUrl" value="<%= about.imageUrl || '' %>" /></label>
      <button class="button" type="submit">Save about page</button>
    </form>
  </div>
</main>
<%- include('../partials/footer') %>
'''
files['public/styles.css'] = r'''
:root {
  --bg: #faf7ff;
  --surface: #ffffff;
  --surface-2: #f2eaff;
  --text: #2b1638;
  --muted: #6e5c78;
  --border: #e2d7f2;
  --primary: #7d4ee7;
  --primary-dark: #5d2ed0;
  --success: #def5e5;
  --error: #fbe4e7;
  --shadow: 0 18px 45px rgba(84, 46, 142, 0.08);
  --radius: 20px;
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  font-family: Inter, Arial, Helvetica, sans-serif;
  color: var(--text);
  background: linear-gradient(180deg, #fcfaff 0%, #f6f0ff 100%);
}

a {
  color: inherit;
  text-decoration: none;
}

img,
video,
iframe {
  max-width: 100%;
  display: block;
  border: 0;
}

iframe {
  width: 100%;
  min-height: 360px;
  border-radius: 18px;
}

audio,
video {
  width: 100%;
}

.container {
  width: min(1120px, calc(100% - 2rem));
  margin: 0 auto;
}

.narrow {
  max-width: 720px;
}

.section {
  padding: 4rem 0;
}

.section-muted {
  background: rgba(255, 255, 255, 0.55);
}

.section-inner {
  margin-top: 2rem;
}

.site-header {
  position: sticky;
  top: 0;
  z-index: 20;
  background: rgba(250, 247, 255, 0.88);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(125, 78, 231, 0.1);
}

.nav-wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 0;
}

.logo-link {
  font-size: 1.2rem;
  font-weight: 800;
  letter-spacing: 0.04em;
}

.main-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.main-nav a {
  padding: 0.7rem 1rem;
  border-radius: 999px;
  color: var(--muted);
  font-weight: 600;
}

.main-nav a:hover,
.main-nav a.active {
  background: var(--surface);
  color: var(--primary-dark);
  box-shadow: var(--shadow);
}

.hero-section {
  padding: 5rem 0 3rem;
}

.hero-grid,
.split-layout,
.detail-layout,
.form-container,
.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 2rem;
  align-items: start;
}

.hero-card,
.card,
.audio-card,
.video-card,
.stat-card,
.site-form,
.empty-state,
.table-wrap,
.flash {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

.hero-card,
.audio-card,
.video-card,
.stat-card,
.empty-state,
.site-form {
  padding: 1.5rem;
}

.eyebrow {
  margin: 0 0 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.78rem;
  color: var(--primary-dark);
  font-weight: 700;
}

h1,
h2,
h3,
p {
  margin-top: 0;
}

h1 {
  font-size: clamp(2.4rem, 5vw, 4.4rem);
  line-height: 1.05;
  margin-bottom: 1rem;
}

h2 {
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  line-height: 1.15;
}

.lead {
  color: var(--muted);
  font-size: 1.1rem;
  line-height: 1.7;
  max-width: 60ch;
}

.button-row,
.admin-toolbar,
.section-heading,
.footer-content,
.row-actions,
.flash-row,
.admin-nav-links,
.social-links {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.button-row,
.admin-nav-links,
.social-links {
  flex-wrap: wrap;
}

.button,
button,
select,
input,
textarea {
  font: inherit;
}

.button,
button {
  border: 0;
  cursor: pointer;
}

.button,
button[type='submit'] {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  padding: 0.9rem 1.2rem;
  border-radius: 999px;
  background: var(--primary);
  color: white;
  font-weight: 700;
}

.button:hover,
button[type='submit']:hover {
  background: var(--primary-dark);
}

.button-secondary {
  background: transparent;
  color: var(--primary-dark);
  border: 1px solid var(--border);
}

.text-link {
  color: var(--primary-dark);
  font-weight: 700;
}

.pill {
  display: inline-flex;
  padding: 0.3rem 0.7rem;
  background: var(--surface-2);
  border-radius: 999px;
  color: var(--primary-dark);
  font-weight: 700;
  font-size: 0.85rem;
  text-transform: capitalize;
}

.card-grid,
.issues-grid,
.featured-grid,
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.25rem;
}

.card img,
.feature-image,
.masonry-item img {
  width: 100%;
  border-radius: calc(var(--radius) - 4px);
  object-fit: cover;
}

.card img {
  aspect-ratio: 4 / 3;
}

.issue-card img {
  aspect-ratio: 3 / 4;
}

.card-body {
  padding: 1rem 1rem 1.25rem;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
  margin-top: 2rem;
}

.gallery-entry {
  min-height: 360px;
  background: linear-gradient(180deg, rgba(255,255,255,0.82), rgba(255,255,255,0.96));
  border: 1px solid var(--border);
  border-radius: 30px;
  padding: 1.4rem;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
  position: relative;
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.gallery-entry::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 180ms ease;
}

.entry-look::before { background: radial-gradient(circle at top left, rgba(125,78,231,0.25), transparent 50%), linear-gradient(140deg, #fcfbff, #efe5ff); }
.entry-read::before { background: radial-gradient(circle at bottom right, rgba(186,133,255,0.25), transparent 45%), linear-gradient(140deg, #fffafd, #f6ebff); }
.entry-listen::before { background: radial-gradient(circle at top right, rgba(124,78,231,0.22), transparent 50%), linear-gradient(140deg, #fff, #ece8ff); }
.entry-watch::before { background: radial-gradient(circle at center, rgba(154,108,255,0.20), transparent 45%), linear-gradient(140deg, #fdfbff, #f2ebff); }

.gallery-entry:hover {
  transform: translateY(-4px);
  border-color: rgba(125, 78, 231, 0.35);
}

.gallery-entry:hover::before {
  opacity: 1;
}

.gallery-entry > * {
  position: relative;
  z-index: 1;
}

.entry-index {
  font-size: 4rem;
  line-height: 1;
  opacity: 0.35;
  font-weight: 800;
}

.entry-subtitle,
.muted,
.issue-year {
  color: var(--muted);
}

.masonry-grid {
  margin-top: 2rem;
  columns: 3 260px;
  column-gap: 1rem;
}

.masonry-item {
  position: relative;
  display: block;
  margin-bottom: 1rem;
}

.masonry-item img {
  border-radius: 24px;
}

.overlay {
  position: absolute;
  inset: auto 1rem 1rem 1rem;
  padding: 1rem;
  color: white;
  background: linear-gradient(180deg, transparent, rgba(25, 15, 33, 0.75));
  border-radius: 18px;
}

.stack-list {
  display: grid;
  gap: 1rem;
  margin-top: 2rem;
}

.video-list iframe,
.detail-video {
  aspect-ratio: 16 / 9;
}

.image-stack {
  display: grid;
  gap: 1rem;
}

.feature-image {
  min-height: 280px;
}

.site-form {
  display: grid;
  gap: 1rem;
}

.site-form label {
  display: grid;
  gap: 0.45rem;
  font-weight: 600;
}

input,
textarea,
select {
  width: 100%;
  padding: 0.9rem 1rem;
  border-radius: 16px;
  border: 1px solid var(--border);
  background: #fff;
  color: var(--text);
}

textarea {
  resize: vertical;
}

.checkbox-row {
  display: flex !important;
  align-items: center;
  gap: 0.75rem;
}

.checkbox-row input {
  width: auto;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 720px;
}

th,
td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}

th {
  color: var(--muted);
  font-size: 0.9rem;
}

.site-footer {
  padding: 2rem 0 3rem;
  border-top: 1px solid rgba(125, 78, 231, 0.12);
}

.footer-content {
  justify-content: space-between;
}

.social-links a,
.admin-nav-links a,
.row-actions a,
.row-actions button {
  padding: 0.55rem 0.8rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 999px;
  color: var(--primary-dark);
  font-weight: 700;
}

.row-actions form {
  margin: 0;
}

.flash-row {
  padding-top: 1rem;
}

.flash {
  width: 100%;
  padding: 1rem 1.2rem;
}

.flash-success {
  background: var(--success);
}

.flash-error {
  background: var(--error);
}

.prose {
  line-height: 1.8;
}

@media (max-width: 960px) {
  .hero-grid,
  .split-layout,
  .detail-layout,
  .form-container,
  .settings-grid,
  .gallery-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 720px) {
  .nav-wrap,
  .footer-content,
  .admin-toolbar,
  .section-heading {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-grid,
  .split-layout,
  .detail-layout,
  .form-container,
  .settings-grid,
  .gallery-grid {
    grid-template-columns: 1fr;
  }

  .masonry-grid {
    columns: 1;
  }

  h1 {
    font-size: 2.5rem;
  }
}
'''
files['public/app.js'] = r'''
document.addEventListener('DOMContentLoaded', () => {
  const currentYearNodes = document.querySelectorAll('[data-current-year]');
  const year = new Date().getFullYear();
  currentYearNodes.forEach((node) => {
    node.textContent = year;
  });
});
'''

for rel, content in files.items():
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.lstrip('\n'), encoding='utf-8')

print(f'Wrote {len(files)} files')
