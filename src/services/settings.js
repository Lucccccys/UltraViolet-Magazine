const PageSetting = require('../models/PageSetting');

async function getSetting(key, fallback = {}) {
  const record = await PageSetting.findOne({ key }).lean();
  return record ? record.value : fallback;
}

async function upsertSetting(key, value) {
  await PageSetting.findOneAndUpdate(
    { key },
    { value },
    { upsert: true, new: true, setDefaultsOnInsert: true }
  );
}

module.exports = {
  getSetting,
  upsertSetting
};
