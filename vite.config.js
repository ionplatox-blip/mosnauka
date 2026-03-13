import { defineConfig } from 'vite';
import { resolve } from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Collect ALL .html files: root + subdirectories
const input = {};

// Root HTML files
fs.readdirSync(__dirname)
  .filter(file => file.endsWith('.html'))
  .forEach(file => {
    const name = file.replace('.html', '');
    input[name] = resolve(__dirname, file);
  });

// Subdirectory HTML files (org pages: mgu/, mfti/, misis/, etc.)
fs.readdirSync(__dirname, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && !['node_modules', 'dist'].includes(d.name))
  .forEach(dir => {
    const dirPath = join(__dirname, dir.name);
    fs.readdirSync(dirPath)
      .filter(file => file.endsWith('.html'))
      .forEach(file => {
        const key = `${dir.name}/${file.replace('.html', '')}`;
        input[key] = resolve(dirPath, file);
      });
  });

export default defineConfig({
    build: {
        rollupOptions: {
            input
        }
    }
});
