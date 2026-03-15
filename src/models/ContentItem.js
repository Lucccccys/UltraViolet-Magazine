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
