#!/usr/bin/env node

import { readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

function bumpVersion(currentVersion, type) {
  const [major, minor, patch] = currentVersion.split('.').map(Number);
  
  switch (type) {
    case 'major':
      return `${major + 1}.0.0`;
    case 'minor':
      return `${major}.${minor + 1}.0`;
    case 'patch':
      return `${major}.${minor}.${patch + 1}`;
    default:
      throw new Error('Invalid version type. Use: major, minor, or patch');
  }
}

function updateVersionFile(newVersion) {
  const versionFilePath = join(__dirname, '../src/version.ts');
  const buildDate = new Date().toISOString();
  
  const content = `// Auto-generated version file
// Update this manually before each deployment
export const VERSION = "${newVersion}";
export const BUILD_DATE = "${buildDate}";`;

  writeFileSync(versionFilePath, content);
  console.log(`✅ Updated version.ts to ${newVersion}`);
}

function updatePackageJson(newVersion) {
  const packageJsonPath = join(__dirname, '../package.json');
  const packageJson = JSON.parse(readFileSync(packageJsonPath, 'utf8'));
  
  packageJson.version = newVersion;
  
  writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2) + '\n');
  console.log(`✅ Updated package.json to ${newVersion}`);
}

function main() {
  const versionType = process.argv[2];
  
  if (!versionType || !['major', 'minor', 'patch'].includes(versionType)) {
    console.error('❌ Usage: node bump-version.js [major|minor|patch]');
    process.exit(1);
  }

  try {
    // Read current version from version.ts
    const versionFilePath = join(__dirname, '../src/version.ts');
    const versionContent = readFileSync(versionFilePath, 'utf8');
    const versionMatch = versionContent.match(/export const VERSION = "([^"]+)"/);
    
    if (!versionMatch) {
      throw new Error('Could not find version in version.ts');
    }
    
    const currentVersion = versionMatch[1];
    const newVersion = bumpVersion(currentVersion, versionType);
    
    console.log(`🚀 Bumping version from ${currentVersion} to ${newVersion}`);
    
    updateVersionFile(newVersion);
    updatePackageJson(newVersion);
    
    console.log(`\n✨ Version bump complete!`);
    console.log(`📦 Ready to commit and deploy version ${newVersion}`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

main();