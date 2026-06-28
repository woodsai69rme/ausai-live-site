const fs = require('fs');
const https = require('https');
const { execSync } = require('child_process');
const path = require('path');

const url = 'https://github.com/lsdefine/GenericAgent/archive/refs/heads/main.zip';
const zipDest = 'C:\\Users\\karma\\ACTIVE_PROJECTS\\GenericAgent.zip';
const extractDir = 'C:\\Users\\karma\\ACTIVE_PROJECTS';
const finalDir = 'C:\\Users\\karma\\ACTIVE_PROJECTS\\GenericAgent';

console.log('Downloading GenericAgent...');

// Follow redirects for github
function download(url, dest) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        return download(res.headers.location, dest).then(resolve, reject);
      }
      const file = fs.createWriteStream(dest);
      res.pipe(file);
      file.on('finish', () => {
        file.close(resolve);
      });
    }).on('error', (err) => {
      fs.unlink(dest, () => reject(err));
    });
  });
}

download(url, zipDest).then(() => {
  console.log('Download complete. Extracting via PowerShell...');
  try {
    execSync(`powershell -Command "Expand-Archive -Path '${zipDest}' -DestinationPath '${extractDir}' -Force"`);
    console.log('Extracted.');
    fs.unlinkSync(zipDest);
    
    const extractedFolder = path.join(extractDir, 'GenericAgent-main');
    if (fs.existsSync(extractedFolder)) {
      if (fs.existsSync(finalDir)) {
        fs.rmSync(finalDir, { recursive: true, force: true });
      }
      fs.renameSync(extractedFolder, finalDir);
      console.log('Successfully renamed and ready:', finalDir);
    }
  } catch(e) {
    console.error('Extraction error:', e.message);
  }
}).catch(console.error);
