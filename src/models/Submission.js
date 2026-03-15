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
