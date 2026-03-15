function requireAdmin(req, res, next) {
  if (!req.session.userId) {
    req.session.message = { type: 'error', text: 'Please sign in to access the admin area.' };
    return res.redirect('/admin/login');
  }

  return next();
}

module.exports = { requireAdmin };
