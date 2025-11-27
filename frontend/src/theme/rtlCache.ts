import createCache from '@emotion/cache';
import rtlPlugin from 'stylis-plugin-rtl';

export default function createRtlCache() {
  return createCache({ key: 'muirtl', stylisPlugins: [rtlPlugin] });
}
