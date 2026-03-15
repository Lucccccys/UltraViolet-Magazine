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
