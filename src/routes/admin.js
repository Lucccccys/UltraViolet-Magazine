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
const { getDefaultSiteSettings } = require('../config/siteDefaults');

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
    const [contentCount, issueCount, submissionCount, latestSubmissions, site] = await Promise.all([
      ContentItem.countDocuments(),
      Issue.countDocuments(),
      Submission.countDocuments(),
      Submission.find({}).sort({ createdAt: -1 }).limit(5).lean(),
      getSetting('site', {})
    ]);

    res.render('admin/dashboard', {
      title: 'Admin Dashboard',
      stats: { contentCount, issueCount, submissionCount },
      latestSubmissions,
      site: getDefaultSiteSettings(site)
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

router.get('/submissions/:id', requireAdmin, async (req, res, next) => {
  try {
    const submission = await Submission.findById(req.params.id).lean();
    if (!submission) {
      return res.status(404).render('pages/error', {
        title: 'Submission not found',
        statusCode: 404,
        message: 'That submission could not be found.'
      });
    }

    res.render('admin/submission-detail', {
      title: submission.title || 'Submission',
      submission
    });
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
    const [about, site, gallery] = await Promise.all([
      getSetting('about', {
        title: 'About Ultraviolet',
        body: ''
      }),
      getSetting('site', getDefaultSiteSettings()),
      getSetting('gallery', {})
    ]);

    res.render('admin/settings', {
      title: 'Settings',
      about,
      site: getDefaultSiteSettings(site),
      gallery
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

router.post('/settings/gallery', requireAdmin, async (req, res, next) => {
  try {
    await upsertSetting('gallery', {
      lookHoverImage: String(req.body.lookHoverImage || '').trim(),
      readHoverImage: String(req.body.readHoverImage || '').trim(),
      listenHoverImage: String(req.body.listenHoverImage || '').trim(),
      watchHoverImage: String(req.body.watchHoverImage || '').trim()
    });
    req.session.message = { type: 'success', text: 'Gallery hover images updated.' };
    res.redirect('/admin/settings');
  } catch (error) {
    next(error);
  }
});

router.post('/settings/site', requireAdmin, async (req, res, next) => {
  try {
    await upsertSetting('site', getDefaultSiteSettings({
      heroTitle: String(req.body.heroTitle || '').trim(),
      heroTagline: String(req.body.heroTagline || '').trim(),
      submissionMode: String(req.body.submissionMode || 'external').trim(),
      externalSubmissionUrl: String(req.body.externalSubmissionUrl || '').trim(),
      issuesArchiveUrl: String(req.body.issuesArchiveUrl || '').trim(),
      legacyAdminUrl: String(req.body.legacyAdminUrl || '').trim(),
      legacySiteUrl: String(req.body.legacySiteUrl || '').trim(),
      footerText: String(req.body.footerText || '').trim()
    }));
    req.session.message = { type: 'success', text: 'Site settings updated.' };
    res.redirect('/admin/settings');
  } catch (error) {
    next(error);
  }
});

module.exports = router;
