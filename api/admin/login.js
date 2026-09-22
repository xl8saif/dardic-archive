import crypto from 'node:crypto';

function signature(value) {
  return crypto.createHmac('sha256', process.env.ADMIN_SESSION_SECRET || process.env.ADMIN_PASSWORD || '').update(value).digest('base64url');
}
export default function handler(req, res) {
  if (req.method === 'DELETE') {
    res.setHeader('Set-Cookie','dardic_admin=; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=0');
    return res.status(204).end();
  }
  if (req.method !== 'POST') return res.status(405).json({ok:false,error:'Method not allowed.'});
  if (!process.env.ADMIN_PASSWORD || String(req.body?.password || '') !== process.env.ADMIN_PASSWORD) return res.status(401).json({ok:false,error:'Invalid admin credentials.'});
  const value='admin.'+Date.now();
  const token=value+'.'+signature(value);
  res.setHeader('Set-Cookie',`dardic_admin=${token}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=28800`);
  return res.status(200).json({ok:true});
}