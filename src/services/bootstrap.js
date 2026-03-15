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
