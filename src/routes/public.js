const express = require('express');
const ContentItem = require('../models/ContentItem');
const Issue = require('../models/Issue');
const Submission = require('../models/Submission');
const { getSetting } = require('../services/settings');
const { categoryMeta, isEmbeddableVideo, toEmbedUrl } = require('../utils/content');
const { getDefaultSiteSettings } = require('../config/siteDefaults');

const router = express.Router();

router.get('/', async (req, res, next) => {
  try {
    const allIssues = await Issue.find({}).sort({ year: -1 }).lean();

    res.render('pages/home', {
      title: 'Home',
      allIssues
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

router.get('/gallery', async (req, res, next) => {
  try {
    const gallery = await getSetting('gallery', {});

    const defaultImages = {
      look: '/images/background-2.webp',
      read: '/images/background-2.webp',
      listen: '/images/background-2.webp',
      watch: '/images/background-2.webp'
    };

    const cards = [
      {
        category: 'look',
        title: 'Look',
        subtitle: 'Artwork\nPhotograph',
        description: 'Browse artwork and photography in a visual grid.',
        hoverImageUrl: gallery.lookHoverImage || defaultImages.look
      },
      {
        category: 'read',
        title: 'Read',
        subtitle: 'Short Stories\nPoems',
        description: 'Explore short stories and poems with preview cards.',
        hoverImageUrl: gallery.readHoverImage || defaultImages.read
      },
      {
        category: 'listen',
        title: 'Listen',
        subtitle: 'Music\nSpoken Work',
        description: 'Play music and spoken word directly in the browser.',
        hoverImageUrl: gallery.listenHoverImage || defaultImages.listen
      },
      {
        category: 'watch',
        title: 'Watch',
        subtitle: 'Short Films\nVideos',
        description: 'View short films and videos with embedded playback.',
        hoverImageUrl: gallery.watchHoverImage || defaultImages.watch
      }
    ];

    res.render('pages/gallery', {
      title: 'Gallery',
      cards
    });
  } catch (error) {
    next(error);
  }
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
    const site = getDefaultSiteSettings(await getSetting('site', {}));
    if (site.submissionMode === 'internal') {
      return res.redirect('/submit/local');
    }

    if (site.externalSubmissionUrl) {
      return res.redirect(site.externalSubmissionUrl);
    }

    return res.redirect('/submit/local');
  } catch (error) {
    next(error);
  }
});

router.get('/submit/local', async (req, res, next) => {
  try {
    res.render('pages/submit', { title: 'Local Submission Test Form' });
  } catch (error) {
    next(error);
  }
});

router.post('/submit/local', async (req, res, next) => {
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
      return res.redirect('/submit/local');
    }

    await Submission.create(payload);
    req.session.message = { type: 'success', text: 'Submission received. Thank you for sharing your work.' };
    return res.redirect('/submit/local');
  } catch (error) {
    next(error);
  }
});

module.exports = router;
