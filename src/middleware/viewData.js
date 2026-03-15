const PageSetting = require('../models/PageSetting');
const SocialLink = require('../models/SocialLink');
const { getDefaultSiteSettings } = require('../config/siteDefaults');

function getAdminBackHref(currentPath) {
  if (!currentPath || !currentPath.startsWith('/admin')) {
    return '/';
  }

  if (currentPath === '/admin/login') {
    return '/';
  }

  if (currentPath === '/admin') {
    return '/';
  }

  if (currentPath === '/admin/content' || currentPath.startsWith('/admin/content/')) {
    return currentPath === '/admin/content' ? '/admin' : '/admin/content';
  }

  if (currentPath === '/admin/issues' || currentPath.startsWith('/admin/issues/')) {
    return currentPath === '/admin/issues' ? '/admin' : '/admin/issues';
  }

  if (currentPath === '/admin/submissions' || currentPath.startsWith('/admin/submissions/')) {
    return currentPath === '/admin/submissions' ? '/admin' : '/admin/submissions';
  }

  if (currentPath === '/admin/social-links' || currentPath === '/admin/settings') {
    return '/admin';
  }

  const segments = currentPath.split('/').filter(Boolean);
  if (segments.length <= 1) {
    return '/';
  }

  return `/${segments.slice(0, -1).join('/')}`;
}

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

    const siteSettings = getDefaultSiteSettings(settings ? settings.value : {});

    res.locals.currentPath = req.path;
    res.locals.socialLinks = socialLinks;
    res.locals.siteSettings = siteSettings;
    res.locals.submitUrl = siteSettings.submissionMode === 'internal' ? '/submit/local' : (siteSettings.externalSubmissionUrl || '/submit/local');
    res.locals.issuesArchiveUrl = siteSettings.issuesArchiveUrl || '/issues';
    res.locals.legacyAdminUrl = siteSettings.legacyAdminUrl || '';
    res.locals.legacySiteUrl = siteSettings.legacySiteUrl || '';
    res.locals.isAdminAuthenticated = Boolean(req.session.userId);
    res.locals.adminBackHref = getAdminBackHref(req.path);
    next();
  } catch (error) {
    next(error);
  }
}

module.exports = {
  attachGlobals,
  attachFlashLikeMessage
};
