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
