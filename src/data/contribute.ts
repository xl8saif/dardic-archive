/**
 * Contribute — the site as a publishing platform for endangered-language work.
 *
 * Editorial gate: EVERY submission is revised and approved by Saif Ullah
 * before publication. Nothing here invents a contact channel — the email/
 * address is pending and must be provided by the site owner.
 */

export const CONTRIBUTE = {
  title: 'Publish on this platform',
  mission:
    'This site is a publishing platform in the service of endangered languages — above all Indus-Kohistani and Shina. If you have research, documentation, stories or educational material in or about these languages, you can publish here after editorial review.',
  focus: ['Indus-Kohistani', 'Shina'],
  alsoAccepted: ['Urdu', 'Arabic', 'English'],
  submissionTypes: [
    { title: 'Research articles', note: 'linguistic or cultural research on Indus-Kohistani, Shina and related Dardic languages' },
    { title: 'Documentation material', note: 'field notes, word lists, texts, transcriptions' },
    { title: 'Folklore & oral traditions', note: 'tales, songs, laments — original language with translation where possible' },
    { title: 'Educational resources', note: 'teaching material, children’s literature, literacy resources' },
    { title: 'Terminology & orthography proposals', note: 'terminology sets, spelling-convention discussions' },
    { title: 'Translations', note: 'works translated into or from Indus-Kohistani and Shina, with source identified' },
    { title: 'Project & archive reports', note: 'documentation projects, recordings, digitisation work' },
  ],
  process: [
    { step: '1 · Submit', detail: 'Send your draft in any format, in any of the accepted languages, through the submission channel.' },
    { step: '2 · Editorial review', detail: 'The editor (Saif Ullah) reviews the content for accuracy, language and fit with the site’s research standards.' },
    { step: '3 · Revision', detail: 'You receive feedback and revise together with the editor. Linguistic review may include orthography and terminology checks against the established conventions.' },
    { step: '4 · Your permission', detail: 'Nothing is published without your explicit approval of the final revised text.' },
    { step: '5 · Publication & attribution', detail: 'The work is published under your name, with your chosen language version(s), and indexed in the archive and relevant language pages.' },
  ],
  standards: [
    'Original work only — or work you have the right to publish, with the source identified',
    'Evidence-based: distinguish documented facts from personal observation',
    'Name the language/variety precisely (e.g. which Indus-Kohistani dialect, where relevant)',
    'Established orthography is preserved; original-language text is kept with translations separate',
    'No fabricated claims, statistics or attributions — the same rules the site holds itself to',
  ],
  rights: [
    'Authorship stays with you, always displayed accurately (author, translator, collector…)',
    'You keep the right to republish your work elsewhere',
    'You may request correction or withdrawal at any time',
    'Collaborative works list every contributor’s role',
  ],
  contact: {
    /** PENDING — must be provided by the site owner; nothing is invented here */
    status: 'pending' as const,
    note: 'The submission channel (email address) is being set up and will be announced here.',
  },

  /**
   * File-upload submission channel.
   *
   * The site is static (GitHub Pages), so uploads are received by a free
   * Google Apps Script Web App deployed by the site owner — submissions
   * land in the Drive folder `Blog/Submissions` and join the same
   * editorial review pipeline as everything else on this site.
   *
   * SETUP (owner, ~3 min — full steps in README.md):
   *   1. Create the Apps Script from scripts/google-apps-script-submissions.gs
   *   2. Deploy as Web App (execute as: Me; access: Anyone)
   *   3. Paste the web-app URL below and set enabled: true
   */
  upload: {
    // Turned on for preview. Until the Apps Script URL below is replaced with
    // a real deployed Web App URL, a test submission will show the error path
    // ("Sending failed…") — expected behavior, nothing is lost.
    enabled: true,
    endpoint: '',
    maxFileMb: 15,
    maxFiles: 3,
    driveFolder: 'Blog/Submissions',
  },
} as const;
