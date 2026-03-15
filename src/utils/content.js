function normalizeImageUrls(rawValue) {
  if (!rawValue) {
    return [];
  }

  if (Array.isArray(rawValue)) {
    return rawValue.filter(Boolean);
  }

  return String(rawValue)
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean);
}

function categoryMeta(category) {
  const map = {
    look: {
      title: 'Look',
      subtitle: 'Artwork and Photography'
    },
    read: {
      title: 'Read',
      subtitle: 'Short Stories and Poems'
    },
    listen: {
      title: 'Listen',
      subtitle: 'Music and Spoken Word'
    },
    watch: {
      title: 'Watch',
      subtitle: 'Short Films and Videos'
    }
  };

  return map[category] || { title: 'Gallery', subtitle: 'Creative work' };
}

function isEmbeddableVideo(url) {
  return /youtube\.com|youtu\.be|vimeo\.com/i.test(String(url || ''));
}

function toEmbedUrl(url) {
  const value = String(url || '').trim();
  if (!value) return '';

  if (value.includes('youtube.com/watch?v=')) {
    const id = value.split('v=')[1]?.split('&')[0];
    return id ? `https://www.youtube.com/embed/${id}` : value;
  }

  if (value.includes('youtu.be/')) {
    const id = value.split('youtu.be/')[1]?.split('?')[0];
    return id ? `https://www.youtube.com/embed/${id}` : value;
  }

  if (value.includes('vimeo.com/')) {
    const id = value.split('vimeo.com/')[1]?.split('?')[0];
    return id ? `https://player.vimeo.com/video/${id}` : value;
  }

  return value;
}

module.exports = {
  normalizeImageUrls,
  categoryMeta,
  isEmbeddableVideo,
  toEmbedUrl
};
