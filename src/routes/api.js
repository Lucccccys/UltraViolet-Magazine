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
