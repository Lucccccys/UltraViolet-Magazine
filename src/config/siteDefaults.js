const OFFICIAL_URLS = {
  externalSubmissionUrl: 'https://docs.google.com/forms/d/e/1FAIpQLSfY1mKenxXltfFdG36W9Bb_Y3LJz9I9j_zj71UfWm_z2YLKTQ/viewform',
  issuesArchiveUrl: 'https://issuu.com/ultravioletmagazine',
  legacyAdminUrl: 'https://users.wix.com/signin?originUrl=https%3A%2F%2Fmanage.wix.com%2Fmy-account%2Fsites&postLogin=https%3A%2F%2Fmanage.wix.com%2Fmy-account%2Fsites&overrideLocale=zh&forceRender=true',
  legacySiteUrl: 'https://uvmagqueens.wixsite.com/uvmagazine'
};

function getDefaultSiteSettings(overrides = {}) {
  return {
    heroTitle: 'Ultraviolet Magazine',
    heroTagline: 'Get creative. Explore boundaries.',
    submissionMode: 'external',
    externalSubmissionUrl: OFFICIAL_URLS.externalSubmissionUrl,
    issuesArchiveUrl: OFFICIAL_URLS.issuesArchiveUrl,
    legacyAdminUrl: OFFICIAL_URLS.legacyAdminUrl,
    legacySiteUrl: OFFICIAL_URLS.legacySiteUrl,
    footerText: 'Ultraviolet Magazine — Queen’s University, Kingston ON',
    ...overrides
  };
}

module.exports = {
  OFFICIAL_URLS,
  getDefaultSiteSettings
};
