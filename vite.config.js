import { defineConfig } from 'vite';
import { resolve } from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const htmlFiles = fs.readdirSync(__dirname).filter(file => file.endsWith('.html'));
const input = {};
htmlFiles.forEach(file => {
    const name = file.replace('.html', '');
    input[name] = resolve(__dirname, file);
});

export default defineConfig({
    build: {
        rollupOptions: {
            input
        }
    }
});
