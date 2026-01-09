/**
 * Deal Banner Carousel
 */

document.addEventListener('DOMContentLoaded', () => {
  const marquee = document.querySelector('.deal-banner-marquee');
  const track = document.querySelector('.deal-banner-marquee-track');

  if (!marquee || !track) return;

  const speedSteps = [10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40];
  const desktopSpeed = 110;
  const mobileSpeed = 140;

  const clearSpeedClasses = () => {
    speedSteps.forEach((s) => marquee.classList.remove(`deal-marquee-speed-${s}`));
  };

  const pickClosestStep = (seconds) => {
    let best = speedSteps[0];
    let bestDiff = Math.abs(seconds - best);

    speedSteps.forEach((s) => {
      const diff = Math.abs(seconds - s);
      if (diff < bestDiff) {
        best = s;
        bestDiff = diff;
      }
    });

    return best;
  };

  const getVisibleItems = () => {
    return Array.from(track.children).filter((item) => item.getAttribute('aria-hidden') !== 'true');
  };

  const fillTrack = () => {
    const viewportWidth = marquee.clientWidth;
    if (!viewportWidth) return;

    const items = getVisibleItems();
    if (!items.length) return;

    const targetWidth = viewportWidth * 2.2;
    let rounds = 0;

    while (track.scrollWidth < targetWidth && rounds < 8) {
      items.forEach((item) => {
        const clone = item.cloneNode(true);
        clone.setAttribute('aria-hidden', 'true');
        clone.setAttribute('tabindex', '-1');
        track.appendChild(clone);
      });
      rounds += 1;
    }
  };

  const updateSpeed = () => {
    clearSpeedClasses();

    const halfDistance = Math.max(1, Math.floor(track.scrollWidth / 2));
    const isMobile = window.matchMedia('(max-width: 768px)').matches;
    const pxPerSecond = isMobile ? mobileSpeed : desktopSpeed;

    let seconds = halfDistance / pxPerSecond;
    seconds = Math.max(10, Math.min(seconds, 40));

    const step = pickClosestStep(seconds);
    marquee.classList.add(`deal-marquee-speed-${step}`);
  };

  let resizeTimer = null;
  const onResize = () => {
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(() => {
      fillTrack();
      updateSpeed();
    }, 150);
  };

  fillTrack();
  updateSpeed();
  window.addEventListener('resize', onResize);
});
