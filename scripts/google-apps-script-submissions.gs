/**
 * Google Apps Script — research-blog submission receiver
 * ==================================================================
 * Receives file uploads from the "Publish with us" form on the website
 * and saves them into a Google Drive folder, where they join the
 * editorial review pipeline.
 *
 * SETUP (site owner, ~3 minutes, free, your own Google account):
 *
 *  1. Go to https://script.google.com → New project
 *  2. Paste this entire file into the editor
 *  3. (Optional, recommended) Set CONFIG.spamGuard answers below
 *  4. Deploy → New deployment → type: Web app
 *       - Execute as: Me
 *       - Who has access: Anyone
 *     Authorize when prompted (it only writes to YOUR Drive)
 *  5. Copy the Web App URL (ends in /exec)
 *  6. Paste it into src/data/contribute.ts → upload.endpoint
 *     and set upload.enabled = true
 *
 * Every submission lands in Drive → "Blog/Submissions" (created
 * automatically) with a metadata sidecar (.json). Review and publish
 * them with the normal editorial pipeline.
 */

var CONFIG = {
  folderName: 'Blog/Submissions',

  // Required folder path parts (root/parent/sub). The script creates any
  // missing level. Submissions are saved under the LAST name segment.
  // Example: 'Blog/Submissions'

  // Simple spam guard: the form sends `challenge` (a word the user types).
  // Leave an empty list to disable the check.
  spamGuardAnswers: ['indus', 'kohistan'],

  maxFileMb: 15,
  maxFiles: 3,
};

function doPost(e) {
  try {
    var params = e.parameter || {};
    var name = sanitize(params.name);
    var email = sanitize(params.email);
    var about = sanitize(params.about);
    var workType = sanitize(params.workType);
    var lang = sanitize(params.language);
    var challenge = (params.challenge || '').toLowerCase().trim();

    if (!name || !email) {
      return json({ ok: false, error: 'Name and email are required.' });
    }
    if (CONFIG.spamGuardAnswers.length > 0 && CONFIG.spamGuardAnswers.indexOf(challenge) === -1) {
      return json({ ok: false, error: 'Verification word is not correct.' });
    }

    var folder = getOrCreateFolder(CONFIG.folderName);
    var stamp = Utilities.formatDate(new Date(), 'UTC', 'yyyy-MM-dd-HH-mm-ss');
    var subId = 'submission-' + stamp;
    var filesSaved = [];

    var files = e.parameters && e.parameters.files ? e.parameters.files : [];
    if (files.length > CONFIG.maxFiles) {
      return json({ ok: false, error: 'Please attach at most ' + CONFIG.maxFiles + ' files.' });
    }
    for (var i = 0; i < files.length; i++) {
      var blob = files[i];
      if (blob.getBytes().length > CONFIG.maxFileMb * 1024 * 1024) {
        return json({ ok: false, error: 'File "' + blob.getName() + '" exceeds ' + CONFIG.maxFileMb + ' MB.' });
      }
      var safe = (blob.getName() || 'file').replace(/[\\/:*?"<>|]/g, '_');
      var saved = folder.createFile(blob.setName(subId + '-' + (i + 1) + '-' + safe));
      saved.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW); // owner-side access only
      filesSaved.push({ name: saved.getName(), url: saved.getUrl() });
    }

    var meta = {
      id: subId,
      receivedAt: new Date().toISOString(),
      name: name,
      email: email,
      workType: workType || '(not specified)',
      language: lang || '(not specified)',
      about: about || '',
      files: filesSaved,
    };
    folder.createFile(
      Utilities.newBlob(JSON.stringify(meta, null, 2), 'application/json', subId + '.json')
    );

    return json({ ok: true, id: subId, files: filesSaved.length });
  } catch (err) {
    return json({ ok: false, error: String(err && err.message || err) });
  }
}

function getOrCreateFolder(path) {
  var parts = path.split('/');
  var folder = DriveApp.getRootFolder();
  for (var i = 0; i < parts.length; i++) {
    var name = parts[i].trim();
    if (!name) continue;
    var it = folder.getFoldersByName(name);
    folder = it.hasNext() ? it.next() : folder.createFolders(name);
  }
  return folder;
}

function sanitize(s) {
  if (!s) return '';
  return String(s).replace(/[<>]/g, '').trim().slice(0, 300);
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(
    ContentService.MimeType.JSON
  );
}
