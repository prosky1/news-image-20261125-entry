// news-image-20261125 entry (Node 22, standard library only).
// Copies the bundled entry.png to /output/entry.png.
// Outside the grader container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const src = new URL('./entry.png', import.meta.url);
if (!existsSync(src)) {
  throw new Error('entry.png missing beside main.ts');
}
const size = statSync(src).size;
if (size <= 0 || size > 1048576) {
  throw new Error(`entry.png size out of gate range: ${size}`);
}
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
copyFileSync(src, join(outDir, 'entry.png'));
