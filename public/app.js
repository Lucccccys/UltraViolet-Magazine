document.addEventListener('DOMContentLoaded', () => {
  const currentYearNodes = document.querySelectorAll('[data-current-year]');
  const year = new Date().getFullYear();
  currentYearNodes.forEach((node) => {
    node.textContent = year;
  });

  const formatDuration = (seconds) => {
    if (!Number.isFinite(seconds) || seconds < 0) {
      return '0 : 00';
    }

    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60)
      .toString()
      .padStart(2, '0');

    return `${minutes} : ${remainingSeconds}`;
  };

  document.querySelectorAll('[data-audio-card]').forEach((card) => {
    const audio = card.querySelector('.gallery-listen-audio');
    const button = card.querySelector('.gallery-listen-play');
    const progressFill = card.querySelector('[data-audio-progress]');
    const timeNode = card.querySelector('[data-audio-time]');

    if (!audio || !button || !progressFill || !timeNode) {
      return;
    }

    const syncVisuals = () => {
      const duration = Number.isFinite(audio.duration) && audio.duration > 0 ? audio.duration : 0;
      const current = Number.isFinite(audio.currentTime) && audio.currentTime > 0 ? audio.currentTime : 0;
      const ratio = duration > 0 ? Math.min(1, current / duration) : 0;
      progressFill.style.transform = `scaleX(${ratio || 0.985})`;
      timeNode.textContent = formatDuration(duration > 0 ? Math.max(duration - current, 0) : 0);
      card.classList.toggle('is-playing', !audio.paused && !audio.ended);
    };

    button.addEventListener('click', async () => {
      const otherPlayingAudios = document.querySelectorAll('.gallery-listen-card.is-playing .gallery-listen-audio');
      otherPlayingAudios.forEach((otherAudio) => {
        if (otherAudio !== audio) {
          otherAudio.pause();
        }
      });

      if (audio.paused) {
        try {
          await audio.play();
        } catch (error) {
          console.error(error);
        }
      } else {
        audio.pause();
      }

      syncVisuals();
    });

    audio.addEventListener('timeupdate', syncVisuals);
    audio.addEventListener('loadedmetadata', syncVisuals);
    audio.addEventListener('durationchange', syncVisuals);
    audio.addEventListener('pause', syncVisuals);
    audio.addEventListener('play', syncVisuals);
    audio.addEventListener('ended', () => {
      audio.currentTime = 0;
      syncVisuals();
    });

    syncVisuals();
  });
});
